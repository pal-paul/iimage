"""
FastAPI application for object detection in images with enterprise features.

This API provides endpoints for uploading images and detecting objects with
comprehensive logging, monitoring, security, and error handling.
"""

import sys
import os
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any

from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Request, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import io

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.detector import ObjectDetector
from lib.moderator import ContentModerator
from lib.config import settings
from lib.validators import ImageValidator
from lib.logging_config import setup_logging, get_logger
from lib.exceptions import ImageDetectionException
from api.middleware import (
    RequestLoggingMiddleware,
    ExceptionHandlerMiddleware,
    SecurityHeadersMiddleware
)
import numpy as np
from PIL import Image
import cv2

# Setup logging
setup_logging(log_level=settings.log_level, json_logs=settings.json_logs)
logger = get_logger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    "api_requests_total",
    "Total number of API requests",
    ["method", "endpoint", "status"]
)
REQUEST_DURATION = Histogram(
    "api_request_duration_seconds",
    "Request duration in seconds",
    ["method", "endpoint"]
)
DETECTION_COUNT = Counter(
    "detections_total",
    "Total number of objects detected",
    ["class_name"]
)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Global detector instance
detector: Optional[ObjectDetector] = None
moderator: Optional[ContentModerator] = None
image_validator: Optional[ImageValidator] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management for the application."""
    global detector, moderator, image_validator
    
    logger.info(
        "application_starting",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment
    )
    
    try:
        # Initialize detector
        detector = ObjectDetector(
            model_name=settings.model_name,
            confidence_threshold=settings.confidence_threshold,
            iou_threshold=settings.iou_threshold
        )
        
        # Initialize content moderator
        moderator = ContentModerator(
            threshold=0.7  # 70% confidence threshold for flagging
        )
        
        # Initialize validator
        image_validator = ImageValidator(
            max_file_size=settings.max_file_size,
            allowed_extensions=settings.get_allowed_extensions_set()
        )
        
        logger.info("application_started_successfully")
        
    except Exception as e:
        logger.error("application_startup_failed", error=str(e))
        raise
    
    yield
    
    logger.info("application_shutting_down")


# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Enterprise-grade API for detecting objects in images using YOLOv8",
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(ExceptionHandlerMiddleware)
app.add_middleware(RequestLoggingMiddleware)


# Response models
class BoundingBox(BaseModel):
    """Bounding box coordinates."""
    x1: float = Field(..., description="Top-left x coordinate")
    y1: float = Field(..., description="Top-left y coordinate")
    x2: float = Field(..., description="Bottom-right x coordinate")
    y2: float = Field(..., description="Bottom-right y coordinate")


class Detection(BaseModel):
    """Detection result."""
    class_name: str = Field(..., alias="class", description="Detected object class")
    class_id: int = Field(..., description="Class ID")
    confidence: float = Field(..., description="Confidence score")
    bbox: BoundingBox = Field(..., description="Bounding box coordinates")
    
    class Config:
        populate_by_name = True


class DetectionResponse(BaseModel):
    """Response for object detection."""
    total_objects: int = Field(..., description="Total number of objects detected")
    detections: list[Detection] = Field(..., description="List of detected objects")
    image_shape: Dict[str, int] = Field(..., description="Image dimensions")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    model: str = Field(..., description="Model name")
    environment: str = Field(..., description="Environment")
    version: str = Field(..., description="API version")


class MetricsResponse(BaseModel):
    """Metrics response."""
    total_classes: int
    classes: Dict[int, str]


class ErrorResponse(BaseModel):
    """Error response."""
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    request_id: Optional[str] = Field(None, description="Request ID")


class ModerationFlag(BaseModel):
    """Flagged content category."""
    category: str = Field(..., description="Category name")
    confidence: float = Field(..., description="Confidence score")


class ModerationResponse(BaseModel):
    """Response for content moderation."""
    is_safe: bool = Field(..., description="Whether the image is safe")
    overall_score: float = Field(..., description="Overall risk score")
    flagged_category: Optional[str] = Field(None, description="Primary flagged category")
    severity: str = Field(..., description="Severity level: none, low, medium, high")
    categories: Dict[str, float] = Field(..., description="Scores for all categories")
    flags: list[ModerationFlag] = Field(..., description="List of flagged categories")
    threshold: float = Field(..., description="Threshold used for flagging")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")
    message: Optional[str] = Field(None, description="Additional message")


# Dependency to get request ID
def get_request_id(request: Request) -> str:
    """Get request ID from request state."""
    return getattr(request.state, "request_id", "unknown")


@app.get("/", tags=["General"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics",
            "detect": "/api/v1/detect",
            "detect_annotated": "/api/v1/detect/annotated",
            "moderate": "/api/v1/moderate",
            "classes": "/api/v1/classes",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Monitoring"])
async def health_check():
    """
    Health check endpoint.
    
    Returns the service status and configuration.
    """
    if detector is None:
        raise HTTPException(status_code=503, detail="Detector not initialized")
    
    return {
        "status": "healthy",
        "model": settings.model_name,
        "environment": settings.environment,
        "version": settings.app_version
    }


@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """
    Prometheus metrics endpoint.
    
    Returns metrics in Prometheus format.
    """
    if not settings.enable_metrics:
        raise HTTPException(status_code=404, detail="Metrics disabled")
    
    return StreamingResponse(
        iter([generate_latest()]),
        media_type=CONTENT_TYPE_LATEST
    )


@app.post(
    "/api/v1/detect",
    response_model=DetectionResponse,
    tags=["Detection"],
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        413: {"model": ErrorResponse, "description": "File too large"},
        415: {"model": ErrorResponse, "description": "Unsupported file type"},
        429: {"description": "Too many requests"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
@limiter.limit(f"{settings.rate_limit_requests}/minute")
async def detect_objects(
    request: Request,
    file: UploadFile = File(..., description="Image file to process"),
    confidence: Optional[float] = Query(
        None, ge=0.0, le=1.0, description="Confidence threshold override"
    ),
    iou: Optional[float] = Query(
        None, ge=0.0, le=1.0, description="IoU threshold override"
    ),
    request_id: str = Depends(get_request_id)
):
    """
    Detect objects in an uploaded image.
    
    - **file**: Image file (jpg, jpeg, png, bmp, webp)
    - **confidence**: Optional confidence threshold (0.0-1.0)
    - **iou**: Optional IoU threshold (0.0-1.0)
    
    Returns JSON with detected objects and their bounding boxes.
    """
    if detector is None or image_validator is None:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    logger.info("detection_request_received", request_id=request_id, filename=file.filename)
    
    # Read file content
    contents = await file.read()
    
    # Validate image
    pil_image = image_validator.validate_all(file.filename, contents)
    
    # Update thresholds if provided
    original_conf = detector.confidence_threshold
    original_iou = detector.iou_threshold
    
    try:
        if confidence is not None or iou is not None:
            detector.update_thresholds(
                confidence_threshold=confidence,
                iou_threshold=iou
            )
        
        # Perform detection
        result = detector.detect_from_pil(pil_image, return_image=False)
        
        # Update metrics
        for detection in result["detections"]:
            DETECTION_COUNT.labels(class_name=detection["class"]).inc()
        
        # Add request ID to response
        result["request_id"] = request_id
        
        logger.info(
            "detection_successful",
            request_id=request_id,
            total_objects=result["total_objects"]
        )
        
        return result
    
    finally:
        # Reset thresholds
        if confidence is not None or iou is not None:
            detector.update_thresholds(
                confidence_threshold=original_conf,
                iou_threshold=original_iou
            )


@app.post(
    "/api/v1/detect/annotated",
    tags=["Detection"],
    responses={
        200: {"content": {"image/jpeg": {}}, "description": "Annotated image"},
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        415: {"model": ErrorResponse},
        429: {"description": "Too many requests"},
        500: {"model": ErrorResponse}
    }
)
@limiter.limit(f"{settings.rate_limit_requests}/minute")
async def detect_objects_annotated(
    request: Request,
    file: UploadFile = File(..., description="Image file to process"),
    confidence: Optional[float] = Query(None, ge=0.0, le=1.0),
    iou: Optional[float] = Query(None, ge=0.0, le=1.0),
    request_id: str = Depends(get_request_id)
):
    """
    Detect objects and return an annotated image.
    
    Returns the image with bounding boxes drawn around detected objects.
    """
    if detector is None or image_validator is None:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    logger.info("annotated_detection_request", request_id=request_id, filename=file.filename)
    
    # Read and validate
    contents = await file.read()
    pil_image = image_validator.validate_all(file.filename, contents)
    
    # Update thresholds if provided
    original_conf = detector.confidence_threshold
    original_iou = detector.iou_threshold
    
    try:
        if confidence is not None or iou is not None:
            detector.update_thresholds(
                confidence_threshold=confidence,
                iou_threshold=iou
            )
        
        # Perform detection
        result = detector.detect_from_pil(pil_image, return_image=True)
        
        # Update metrics
        for detection in result["detections"]:
            DETECTION_COUNT.labels(class_name=detection["class"]).inc()
        
        # Convert to image bytes
        annotated_image = result["annotated_image"]
        annotated_image_rgb = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)
        pil_annotated = Image.fromarray(annotated_image_rgb)
        
        img_byte_arr = io.BytesIO()
        pil_annotated.save(img_byte_arr, format="JPEG", quality=95)
        img_byte_arr.seek(0)
        
        logger.info(
            "annotated_detection_successful",
            request_id=request_id,
            total_objects=result["total_objects"]
        )
        
        return StreamingResponse(
            img_byte_arr,
            media_type="image/jpeg",
            headers={
                "Content-Disposition": f'inline; filename="annotated_{file.filename}"',
                "X-Request-ID": request_id,
                "X-Objects-Detected": str(result["total_objects"])
            }
        )
    
    finally:
        if confidence is not None or iou is not None:
            detector.update_thresholds(
                confidence_threshold=original_conf,
                iou_threshold=original_iou
            )


@app.post(
    "/api/v1/moderate",
    response_model=ModerationResponse,
    tags=["Moderation"],
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        413: {"model": ErrorResponse, "description": "File too large"},
        415: {"model": ErrorResponse, "description": "Unsupported file type"},
        429: {"description": "Too many requests"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
@limiter.limit(f"{settings.rate_limit_requests}/minute")
async def moderate_image(
    request: Request,
    file: UploadFile = File(..., description="Image file to moderate"),
    threshold: Optional[float] = Query(
        None,
        ge=0.0,
        le=1.0,
        description="Custom threshold for flagging content (0-1)"
    ),
    request_id: str = Depends(get_request_id)
):
    """
    Moderate image content for inappropriate material.
    
    Analyzes the uploaded image for NSFW content, violence, gore, and other
    inappropriate material. Returns safety assessment with confidence scores.
    
    - **file**: Image file to moderate (JPEG, PNG, etc.)
    - **threshold**: Optional custom threshold (default: 0.7)
    
    Returns:
    - **is_safe**: Boolean indicating if the image is safe
    - **overall_score**: Overall risk score (0-1)
    - **flagged_category**: Primary category if flagged
    - **severity**: Risk severity (none, low, medium, high)
    - **categories**: Detailed scores for all categories
    - **flags**: List of flagged categories with scores
    """
    if moderator is None or image_validator is None:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    logger.info("moderation_request", request_id=request_id, filename=file.filename)
    
    # Read and validate
    contents = await file.read()
    pil_image = image_validator.validate_all(file.filename, contents)
    
    # Update threshold if provided
    original_threshold = moderator.threshold
    
    try:
        if threshold is not None:
            moderator.update_threshold(threshold)
        
        # Perform moderation
        result = moderator.moderate_from_pil(pil_image)
        
        # Add additional context
        result["request_id"] = request_id
        
        if not result["is_safe"]:
            result["message"] = (
                f"Image flagged as potentially inappropriate. "
                f"Primary concern: {result['flagged_category']} "
                f"(confidence: {result['overall_score']:.2%})"
            )
        else:
            result["message"] = "Image passed content moderation checks."
        
        logger.info(
            "moderation_successful",
            request_id=request_id,
            is_safe=result["is_safe"],
            severity=result["severity"]
        )
        
        return result
    
    finally:
        if threshold is not None:
            moderator.update_threshold(original_threshold)


@app.get("/api/v1/classes", response_model=MetricsResponse, tags=["Information"])
async def get_classes():
    """
    Get all available object classes.
    
    Returns a dictionary of class IDs and their corresponding names.
    """
    if detector is None:
        raise HTTPException(status_code=503, detail="Detector not initialized")
    
    classes = detector.get_available_classes()
    return {
        "total_classes": len(classes),
        "classes": classes
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info(
        "starting_server",
        host=settings.host,
        port=settings.port,
        environment=settings.environment
    )
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_config=None  # Use our custom logging
    )
