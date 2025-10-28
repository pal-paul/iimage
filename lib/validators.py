"""
Validators for input validation.
"""

import io
from pathlib import Path
from typing import Optional, Set

from PIL import Image

from .exceptions import (FileSizeExceededError, InvalidImageError,
                         UnsupportedFileTypeError)


class ImageValidator:
    """Validator for image files."""
    
    # MIME types for allowed image formats
    ALLOWED_MIME_TYPES = {
        "image/jpeg",
        "image/png",
        "image/bmp",
        "image/webp",
        "image/tiff"
    }
    
    # Magic number signatures for image formats
    IMAGE_SIGNATURES = {
        b"\xff\xd8\xff": "jpeg",
        b"\x89\x50\x4e\x47": "png",
        b"\x42\x4d": "bmp",
        b"\x52\x49\x46\x46": "webp",
        b"\x49\x49\x2a\x00": "tiff",
        b"\x4d\x4d\x00\x2a": "tiff",
    }
    
    def __init__(self, max_file_size: int, allowed_extensions: Set[str]):
        """
        Initialize the image validator.
        
        Args:
            max_file_size: Maximum allowed file size in bytes
            allowed_extensions: Set of allowed file extensions
        """
        self.max_file_size = max_file_size
        self.allowed_extensions = allowed_extensions
    
    def validate_extension(self, filename: str) -> None:
        """
        Validate file extension.
        
        Args:
            filename: Name of the file
            
        Raises:
            UnsupportedFileTypeError: If extension is not allowed
        """
        if not filename or "." not in filename:
            raise UnsupportedFileTypeError(
                "File must have an extension",
                details={"filename": filename}
            )
        
        extension = filename.rsplit(".", 1)[1].lower()
        if extension not in self.allowed_extensions:
            raise UnsupportedFileTypeError(
                f"File extension '.{extension}' is not allowed",
                details={
                    "extension": extension,
                    "allowed_extensions": list(self.allowed_extensions)
                }
            )
    
    def validate_size(self, file_content: bytes, filename: str = "") -> None:
        """
        Validate file size.
        
        Args:
            file_content: File content as bytes
            filename: Optional filename for error details
            
        Raises:
            FileSizeExceededError: If file size exceeds limit
        """
        file_size = len(file_content)
        if file_size > self.max_file_size:
            raise FileSizeExceededError(
                f"File size {file_size} bytes exceeds maximum {self.max_file_size} bytes",
                details={
                    "file_size": file_size,
                    "max_size": self.max_file_size,
                    "filename": filename
                }
            )
    
    def validate_magic_number(self, file_content: bytes) -> None:
        """
        Validate file magic number (file signature).
        
        Args:
            file_content: File content as bytes
            
        Raises:
            InvalidImageError: If magic number doesn't match known image formats
        """
        if len(file_content) < 12:
            raise InvalidImageError("File is too small to be a valid image")
        
        # Check magic numbers
        is_valid = False
        for signature in self.IMAGE_SIGNATURES.keys():
            if file_content.startswith(signature):
                is_valid = True
                break
        
        if not is_valid:
            raise InvalidImageError(
                "File does not appear to be a valid image (invalid magic number)"
            )
    
    def validate_image_content(self, file_content: bytes, filename: str = "") -> Image.Image:
        """
        Validate that content is actually a valid image.
        
        Args:
            file_content: File content as bytes
            filename: Optional filename for error details
            
        Returns:
            PIL Image object if valid
            
        Raises:
            InvalidImageError: If content is not a valid image
        """
        try:
            image = Image.open(io.BytesIO(file_content))
            # Verify will check if image is corrupted
            image.verify()
            
            # Reopen for actual use (verify closes the file)
            image = Image.open(io.BytesIO(file_content))
            
            # Additional checks
            if image.size[0] == 0 or image.size[1] == 0:
                raise InvalidImageError("Image has invalid dimensions")
            
            # Check if image is too large (dimensions)
            max_dimension = 10000  # 10k pixels
            if image.size[0] > max_dimension or image.size[1] > max_dimension:
                raise InvalidImageError(
                    f"Image dimensions exceed maximum {max_dimension}x{max_dimension}",
                    details={
                        "width": image.size[0],
                        "height": image.size[1],
                        "filename": filename
                    }
                )
            
            return image
            
        except InvalidImageError:
            raise
        except Exception as e:
            raise InvalidImageError(
                f"Invalid image content: {str(e)}",
                details={"filename": filename, "error": str(e)}
            )
    
    def validate_all(self, filename: str, file_content: bytes) -> Image.Image:
        """
        Run all validation checks.
        
        Args:
            filename: Name of the file
            file_content: File content as bytes
            
        Returns:
            PIL Image object if all validations pass
            
        Raises:
            Various exceptions if validation fails
        """
        self.validate_extension(filename)
        self.validate_size(file_content, filename)
        self.validate_magic_number(file_content)
        return self.validate_image_content(file_content, filename)
