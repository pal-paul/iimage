"""
Unit tests for the ObjectDetector class.
"""

import io
import tempfile
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from lib.detector import ObjectDetector
from lib.exceptions import DetectionError, ModelLoadError


@pytest.fixture
def detector():
    """Create a detector instance for testing."""
    return ObjectDetector(model_name="yolov8n.pt")


@pytest.fixture
def sample_image():
    """Create a sample image for testing."""
    # Create a simple RGB image
    img_array = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    return Image.fromarray(img_array)


@pytest.fixture
def sample_image_path(sample_image, tmp_path):
    """Save sample image to a temporary file."""
    image_path = tmp_path / "test_image.jpg"
    sample_image.save(image_path)
    return str(image_path)


class TestObjectDetector:
    """Test suite for ObjectDetector class."""
    
    def test_initialization(self, detector):
        """Test detector initialization."""
        assert detector is not None
        assert detector.model is not None
        assert detector.confidence_threshold == 0.25
        assert detector.iou_threshold == 0.45
    
    def test_initialization_with_custom_params(self):
        """Test detector initialization with custom parameters."""
        detector = ObjectDetector(
            model_name="yolov8n.pt",
            confidence_threshold=0.5,
            iou_threshold=0.3
        )
        assert detector.confidence_threshold == 0.5
        assert detector.iou_threshold == 0.3
    
    def test_detect_from_pil(self, detector, sample_image):
        """Test detection from PIL Image."""
        result = detector.detect_from_pil(sample_image)
        
        assert "total_objects" in result
        assert "detections" in result
        assert "image_shape" in result
        assert isinstance(result["total_objects"], int)
        assert isinstance(result["detections"], list)
        assert result["image_shape"]["height"] == 480
        assert result["image_shape"]["width"] == 640
    
    def test_detect_from_path(self, detector, sample_image_path):
        """Test detection from file path."""
        result = detector.detect_from_path(sample_image_path)
        
        assert "total_objects" in result
        assert "detections" in result
        assert "image_shape" in result
    
    def test_detect_from_path_nonexistent(self, detector):
        """Test detection with nonexistent file."""
        with pytest.raises(FileNotFoundError):
            detector.detect_from_path("/nonexistent/image.jpg")
    
    def test_detect_with_annotated_image(self, detector, sample_image):
        """Test detection with annotated image return."""
        result = detector.detect_from_pil(sample_image, return_image=True)
        
        assert "annotated_image" in result
        assert isinstance(result["annotated_image"], np.ndarray)
    
    def test_get_available_classes(self, detector):
        """Test getting available classes."""
        classes = detector.get_available_classes()
        
        assert isinstance(classes, dict)
        assert len(classes) == 80  # COCO dataset has 80 classes
        assert 0 in classes  # person class
    
    def test_update_thresholds(self, detector):
        """Test updating detection thresholds."""
        detector.update_thresholds(confidence_threshold=0.6, iou_threshold=0.4)
        
        assert detector.confidence_threshold == 0.6
        assert detector.iou_threshold == 0.4
    
    def test_update_thresholds_invalid_confidence(self, detector):
        """Test updating with invalid confidence threshold."""
        with pytest.raises(ValueError):
            detector.update_thresholds(confidence_threshold=1.5)
    
    def test_update_thresholds_invalid_iou(self, detector):
        """Test updating with invalid IoU threshold."""
        with pytest.raises(ValueError):
            detector.update_thresholds(iou_threshold=-0.1)
    
    def test_detection_result_structure(self, detector, sample_image):
        """Test structure of detection results."""
        result = detector.detect_from_pil(sample_image)
        
        if result["total_objects"] > 0:
            detection = result["detections"][0]
            assert "class" in detection
            assert "class_id" in detection
            assert "confidence" in detection
            assert "bbox" in detection
            
            bbox = detection["bbox"]
            assert "x1" in bbox
            assert "y1" in bbox
            assert "x2" in bbox
            assert "y2" in bbox
