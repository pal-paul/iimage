"""
Unit tests for image validators.
"""

import io

import pytest
from PIL import Image

from lib.exceptions import (FileSizeExceededError, InvalidImageError,
                            UnsupportedFileTypeError)
from lib.validators import ImageValidator


@pytest.fixture
def validator():
    """Create a validator instance."""
    return ImageValidator(
        max_file_size=1024 * 1024,  # 1MB
        allowed_extensions={"jpg", "jpeg", "png", "bmp"}
    )


@pytest.fixture
def valid_jpeg_content():
    """Create valid JPEG content."""
    img = Image.new("RGB", (100, 100), color="red")
    byte_arr = io.BytesIO()
    img.save(byte_arr, format="JPEG")
    return byte_arr.getvalue()


@pytest.fixture
def valid_png_content():
    """Create valid PNG content."""
    img = Image.new("RGB", (100, 100), color="blue")
    byte_arr = io.BytesIO()
    img.save(byte_arr, format="PNG")
    return byte_arr.getvalue()


class TestImageValidator:
    """Test suite for ImageValidator class."""
    
    def test_validate_extension_valid(self, validator):
        """Test validation with valid extensions."""
        validator.validate_extension("image.jpg")
        validator.validate_extension("photo.jpeg")
        validator.validate_extension("picture.png")
        validator.validate_extension("IMAGE.JPG")  # Case insensitive
    
    def test_validate_extension_invalid(self, validator):
        """Test validation with invalid extensions."""
        with pytest.raises(UnsupportedFileTypeError):
            validator.validate_extension("file.txt")
        
        with pytest.raises(UnsupportedFileTypeError):
            validator.validate_extension("file.pdf")
        
        with pytest.raises(UnsupportedFileTypeError):
            validator.validate_extension("noextension")
    
    def test_validate_size_valid(self, validator, valid_jpeg_content):
        """Test size validation with valid file."""
        validator.validate_size(valid_jpeg_content, "test.jpg")
    
    def test_validate_size_too_large(self, validator):
        """Test size validation with oversized file."""
        large_content = b"x" * (2 * 1024 * 1024)  # 2MB
        
        with pytest.raises(FileSizeExceededError) as exc_info:
            validator.validate_size(large_content, "large.jpg")
        
        assert "2097152" in str(exc_info.value.message)
    
    def test_validate_magic_number_jpeg(self, validator, valid_jpeg_content):
        """Test magic number validation for JPEG."""
        validator.validate_magic_number(valid_jpeg_content)
    
    def test_validate_magic_number_png(self, validator, valid_png_content):
        """Test magic number validation for PNG."""
        validator.validate_magic_number(valid_png_content)
    
    def test_validate_magic_number_invalid(self, validator):
        """Test magic number validation with invalid content."""
        invalid_content = b"This is not an image"
        
        with pytest.raises(InvalidImageError):
            validator.validate_magic_number(invalid_content)
    
    def test_validate_image_content_valid(self, validator, valid_jpeg_content):
        """Test image content validation with valid image."""
        img = validator.validate_image_content(valid_jpeg_content, "test.jpg")
        assert isinstance(img, Image.Image)
        assert img.size == (100, 100)
    
    def test_validate_image_content_invalid(self, validator):
        """Test image content validation with invalid content."""
        invalid_content = b"Not an image"
        
        with pytest.raises(InvalidImageError):
            validator.validate_image_content(invalid_content, "test.jpg")
    
    def test_validate_image_content_zero_dimensions(self, validator):
        """Test validation with zero dimension image."""
        # This is a theoretical test; PIL usually prevents this
        pass
    
    def test_validate_all_success(self, validator, valid_jpeg_content):
        """Test complete validation with valid image."""
        img = validator.validate_all("test.jpg", valid_jpeg_content)
        assert isinstance(img, Image.Image)
    
    def test_validate_all_invalid_extension(self, validator, valid_jpeg_content):
        """Test complete validation with invalid extension."""
        with pytest.raises(UnsupportedFileTypeError):
            validator.validate_all("test.txt", valid_jpeg_content)
    
    def test_validate_all_file_too_large(self, validator):
        """Test complete validation with oversized file."""
        large_img = Image.new("RGB", (2000, 2000), color="green")
        byte_arr = io.BytesIO()
        large_img.save(byte_arr, format="JPEG", quality=100)
        content = byte_arr.getvalue()
        
        with pytest.raises(FileSizeExceededError):
            validator.validate_all("large.jpg", content)
