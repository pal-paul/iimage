"""
Custom exceptions for the image detection API.
"""

from typing import Any, Dict, Optional


class ImageDetectionException(Exception):
    """Base exception for all image detection errors."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ModelLoadError(ImageDetectionException):
    """Raised when the model fails to load."""
    
    def __init__(self, message: str = "Failed to load detection model", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=503, details=details)


class InvalidImageError(ImageDetectionException):
    """Raised when the uploaded file is not a valid image."""
    
    def __init__(self, message: str = "Invalid image file", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, details=details)


class FileSizeExceededError(ImageDetectionException):
    """Raised when the uploaded file exceeds the size limit."""
    
    def __init__(self, message: str = "File size exceeds maximum allowed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=413, details=details)


class UnsupportedFileTypeError(ImageDetectionException):
    """Raised when the file type is not supported."""
    
    def __init__(self, message: str = "Unsupported file type", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=415, details=details)


class DetectionError(ImageDetectionException):
    """Raised when object detection fails."""
    
    def __init__(self, message: str = "Object detection failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)


class ConfigurationError(ImageDetectionException):
    """Raised when there's a configuration error."""
    
    def __init__(self, message: str = "Configuration error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)
