"""
Object Detection Module

Provides the ObjectDetector class for detecting objects in images.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import cv2
import numpy as np
import torch
from PIL import Image
from ultralytics import YOLO

from .exceptions import DetectionError, ModelLoadError
from .logging_config import get_logger

logger = get_logger(__name__)


class ObjectDetector:
    """
    A class for detecting objects in images using YOLOv8.
    
    Attributes:
        model_name (str): Name of the YOLO model to use
        confidence_threshold (float): Minimum confidence score for detections
        iou_threshold (float): IoU threshold for NMS (Non-Maximum Suppression)
    """
    
    def __init__(
        self,
        model_name: str = "yolov8n.pt",
        confidence_threshold: float = 0.25,
        iou_threshold: float = 0.45
    ):
        """
        Initialize the ObjectDetector.
        
        Args:
            model_name: Name of the YOLO model (yolov8n, yolov8s, yolov8m, yolov8l, yolov8x)
            confidence_threshold: Minimum confidence score (0-1)
            iou_threshold: IoU threshold for NMS (0-1)
        """
        self.model_name = model_name
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.model = None
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the YOLO model. Downloads if not available."""
        try:
            logger.info("loading_model", model_name=self.model_name)
            
            # For PyTorch 2.6+, we need to set weights_only=False for YOLO models
            # This is safe for official Ultralytics models from trusted sources
            torch_load_func = torch.load
            original_weights_only = None
            
            # Temporarily set weights_only to False for loading YOLO models
            def patched_load(*args, **kwargs):
                if 'weights_only' not in kwargs:
                    kwargs['weights_only'] = False
                return torch_load_func(*args, **kwargs)
            
            torch.load = patched_load
            
            try:
                self.model = YOLO(self.model_name)
            finally:
                # Restore original torch.load
                torch.load = torch_load_func
                
            logger.info("model_loaded_successfully", model_name=self.model_name)
        except Exception as e:
            logger.error("model_load_failed", model_name=self.model_name, error=str(e))
            raise ModelLoadError(
                f"Failed to load model: {str(e)}",
                details={"model_name": self.model_name, "error": str(e)}
            )
    
    def detect_from_path(
        self,
        image_path: Union[str, Path],
        return_image: bool = False
    ) -> Dict[str, Any]:
        """
        Detect objects in an image from a file path.
        
        Args:
            image_path: Path to the image file
            return_image: Whether to return the annotated image
        
        Returns:
            Dictionary containing detection results
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Read image
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError(f"Failed to read image: {image_path}")
        
        return self._detect(image, return_image)
    
    def detect_from_array(
        self,
        image_array: np.ndarray,
        return_image: bool = False
    ) -> Dict[str, Any]:
        """
        Detect objects in an image from a numpy array.
        
        Args:
            image_array: Image as numpy array (BGR format)
            return_image: Whether to return the annotated image
        
        Returns:
            Dictionary containing detection results
        """
        if not isinstance(image_array, np.ndarray):
            raise TypeError("Image must be a numpy array")
        
        return self._detect(image_array, return_image)
    
    def detect_from_pil(
        self,
        pil_image: Image.Image,
        return_image: bool = False
    ) -> Dict[str, Any]:
        """
        Detect objects in a PIL Image.
        
        Args:
            pil_image: PIL Image object
            return_image: Whether to return the annotated image
        
        Returns:
            Dictionary containing detection results
        """
        # Convert PIL to numpy array (RGB to BGR)
        image_array = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        return self._detect(image_array, return_image)
    
    def _detect(
        self,
        image: np.ndarray,
        return_image: bool = False
    ) -> Dict[str, Any]:
        """
        Internal method to perform object detection.
        
        Args:
            image: Image as numpy array
            return_image: Whether to return the annotated image
        
        Returns:
            Dictionary with detection results
        """
        try:
            logger.debug("starting_detection", image_shape=image.shape)
            
            # Run inference
            results = self.model.predict(
                image,
                conf=self.confidence_threshold,
                iou=self.iou_threshold,
                verbose=False
            )
            
            # Parse results
            detections = self._parse_results(results[0])
            
            logger.info(
                "detection_completed",
                total_objects=len(detections),
                image_shape=image.shape
            )
            
            response = {
                "total_objects": len(detections),
                "detections": detections,
                "image_shape": {
                    "height": image.shape[0],
                    "width": image.shape[1],
                    "channels": image.shape[2] if len(image.shape) > 2 else 1
                }
            }
            
            # Optionally add annotated image
            if return_image:
                annotated_image = results[0].plot()
                response["annotated_image"] = annotated_image
            
            return response
            
        except Exception as e:
            logger.error("detection_failed", error=str(e), error_type=type(e).__name__)
            raise DetectionError(
                f"Object detection failed: {str(e)}",
                details={"error": str(e), "image_shape": image.shape}
            )
    
    def _parse_results(self, result) -> List[Dict[str, Any]]:
        """
        Parse YOLO results into a structured format.
        
        Args:
            result: YOLO result object
        
        Returns:
            List of detection dictionaries
        """
        detections = []
        
        if result.boxes is not None:
            boxes = result.boxes
            
            for i in range(len(boxes)):
                # Get box coordinates
                box = boxes.xyxy[i].cpu().numpy()
                
                # Get class and confidence
                class_id = int(boxes.cls[i].cpu().numpy())
                confidence = float(boxes.conf[i].cpu().numpy())
                class_name = result.names[class_id]
                
                detection = {
                    "class": class_name,
                    "class_id": class_id,
                    "confidence": round(confidence, 4),
                    "bbox": {
                        "x1": round(float(box[0]), 2),
                        "y1": round(float(box[1]), 2),
                        "x2": round(float(box[2]), 2),
                        "y2": round(float(box[3]), 2)
                    }
                }
                
                detections.append(detection)
        
        return detections
    
    def get_available_classes(self) -> Dict[int, str]:
        """
        Get all available object classes that the model can detect.
        
        Returns:
            Dictionary mapping class IDs to class names
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        return self.model.names
    
    def update_thresholds(
        self,
        confidence_threshold: Optional[float] = None,
        iou_threshold: Optional[float] = None
    ) -> None:
        """
        Update detection thresholds.
        
        Args:
            confidence_threshold: New confidence threshold
            iou_threshold: New IoU threshold
        """
        if confidence_threshold is not None:
            if not 0 <= confidence_threshold <= 1:
                raise ValueError("Confidence threshold must be between 0 and 1")
            self.confidence_threshold = confidence_threshold
        
        if iou_threshold is not None:
            if not 0 <= iou_threshold <= 1:
                raise ValueError("IoU threshold must be between 0 and 1")
            self.iou_threshold = iou_threshold
