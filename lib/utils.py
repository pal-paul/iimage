"""
Utility functions for image processing and validation.
"""

import io
import os
from pathlib import Path
from typing import List, Optional

from PIL import Image

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'webp', 'tiff'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def is_valid_image_extension(filename: str, allowed_extensions: Optional[List[str]] = None) -> bool:
    """
    Check if the file has a valid image extension.
    
    Args:
        filename: Name of the file
        allowed_extensions: List of allowed extensions (default: common image formats)
    
    Returns:
        True if extension is valid, False otherwise
    """
    if allowed_extensions is None:
        allowed_extensions = ALLOWED_EXTENSIONS
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def validate_image_file(file_path: str, max_size: int = MAX_FILE_SIZE) -> bool:
    """
    Validate an image file exists and is within size limits.
    
    Args:
        file_path: Path to the image file
        max_size: Maximum allowed file size in bytes
    
    Returns:
        True if valid, raises exception otherwise
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Image file not found: {file_path}")
    
    file_size = os.path.getsize(file_path)
    if file_size > max_size:
        raise ValueError(f"File size ({file_size} bytes) exceeds maximum ({max_size} bytes)")
    
    return True


def validate_image_content(file_content: bytes) -> bool:
    """
    Validate that the file content is actually an image.
    
    Args:
        file_content: Raw file content as bytes
    
    Returns:
        True if valid image, raises exception otherwise
    """
    try:
        image = Image.open(io.BytesIO(file_content))
        image.verify()
        return True
    except Exception as e:
        raise ValueError(f"Invalid image content: {str(e)}")


def create_directory_if_not_exists(directory: str) -> None:
    """
    Create a directory if it doesn't exist.
    
    Args:
        directory: Path to the directory
    """
    Path(directory).mkdir(parents=True, exist_ok=True)
