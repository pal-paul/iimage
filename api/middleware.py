"""
Middleware for the FastAPI application.
"""

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from lib.exceptions import ImageDetectionException
from lib.logging_config import get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests and responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details."""
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Start timer
        start_time = time.time()
        
        # Log incoming request
        logger.info(
            "request_started",
            request_id=request_id,
            method=request.method,
            url=str(request.url),
            client_host=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent", "unknown")
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            logger.info(
                "request_completed",
                request_id=request_id,
                method=request.method,
                url=str(request.url),
                status_code=response.status_code,
                duration_ms=round(duration * 1000, 2)
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "request_failed",
                request_id=request_id,
                method=request.method,
                url=str(request.url),
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=round(duration * 1000, 2)
            )
            raise


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware to handle exceptions uniformly."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and handle exceptions."""
        try:
            return await call_next(request)
        except ImageDetectionException as e:
            # Handle custom exceptions
            request_id = getattr(request.state, "request_id", "unknown")
            logger.warning(
                "custom_exception_caught",
                request_id=request_id,
                exception_type=type(e).__name__,
                message=e.message,
                status_code=e.status_code,
                details=e.details
            )
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "error": e.message,
                    "details": e.details,
                    "request_id": request_id
                }
            )
        except Exception as e:
            # Handle unexpected exceptions
            request_id = getattr(request.state, "request_id", "unknown")
            logger.error(
                "unexpected_exception",
                request_id=request_id,
                exception_type=type(e).__name__,
                error=str(e)
            )
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": str(e),
                    "request_id": request_id
                }
            )


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response."""
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response
