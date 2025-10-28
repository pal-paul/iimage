"""
Content Moderation Module

Provides the ContentModerator class for detecting inappropriate content in images.
"""

import io
from pathlib import Path
from typing import Any, Dict, Optional, Union

import numpy as np
import torch
from PIL import Image
from transformers import pipeline

from .exceptions import DetectionError, ModelLoadError
from .logging_config import get_logger

logger = get_logger(__name__)


class ContentModerator:
    """
    A class for detecting inappropriate content in images.
    
    Uses AI models to detect NSFW content, violence, gore, and other
    inappropriate material.
    
    Attributes:
        model_name (str): Name of the moderation model to use
        threshold (float): Minimum confidence score for flagging content
    """
    
    def __init__(
        self,
        model_name: str = "Falconsai/nsfw_image_detection",
        threshold: float = 0.7
    ):
        """
        Initialize the ContentModerator.
        
        Args:
            model_name: Name of the Hugging Face model for content moderation
            threshold: Confidence threshold for flagging (0-1)
        """
        self.model_name = model_name
        self.threshold = threshold
        self.pipeline = None
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the content moderation model."""
        try:
            logger.info("loading_moderation_model", model_name=self.model_name)
            
            # For PyTorch 2.6+, we need to set weights_only=False
            torch_load_func = torch.load
            
            def patched_load(*args, **kwargs):
                if 'weights_only' not in kwargs:
                    kwargs['weights_only'] = False
                return torch_load_func(*args, **kwargs)
            
            torch.load = patched_load
            
            try:
                self.pipeline = pipeline(
                    "image-classification",
                    model=self.model_name,
                    device=0 if torch.cuda.is_available() else -1
                )
            finally:
                torch.load = torch_load_func
            
            logger.info("moderation_model_loaded", model_name=self.model_name)
            
        except Exception as e:
            logger.error("moderation_model_load_failed", model_name=self.model_name, error=str(e))
            raise ModelLoadError(
                f"Failed to load moderation model: {str(e)}",
                details={"model_name": self.model_name, "error": str(e)}
            )
    
    def moderate_from_path(
        self,
        image_path: Union[str, Path]
    ) -> Dict[str, Any]:
        """
        Moderate image from file path.
        
        Args:
            image_path: Path to the image file
        
        Returns:
            Dictionary containing moderation results
        """
        try:
            pil_image = Image.open(image_path).convert("RGB")
            return self.moderate_from_pil(pil_image)
        except Exception as e:
            logger.error("moderation_failed", error=str(e))
            raise DetectionError(
                f"Image moderation failed: {str(e)}",
                details={"image_path": str(image_path), "error": str(e)}
            )
    
    def moderate_from_bytes(
        self,
        image_bytes: bytes
    ) -> Dict[str, Any]:
        """
        Moderate image from bytes.
        
        Args:
            image_bytes: Image data as bytes
        
        Returns:
            Dictionary containing moderation results
        """
        try:
            pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            return self.moderate_from_pil(pil_image)
        except Exception as e:
            logger.error("moderation_failed", error=str(e))
            raise DetectionError(
                f"Image moderation failed: {str(e)}",
                details={"error": str(e)}
            )
    
    def moderate_from_pil(
        self,
        pil_image: Image.Image
    ) -> Dict[str, Any]:
        """
        Moderate PIL Image object.
        
        Args:
            pil_image: PIL Image object
        
        Returns:
            Dictionary containing moderation results
        """
        try:
            logger.debug("starting_moderation", image_size=pil_image.size)
            
            # Run moderation
            results = self.pipeline(pil_image)
            
            # Parse results
            moderation_data = self._parse_results(results)
            
            logger.info(
                "moderation_completed",
                is_safe=moderation_data["is_safe"],
                flags=moderation_data["flags"]
            )
            
            return moderation_data
            
        except Exception as e:
            logger.error("moderation_failed", error=str(e), error_type=type(e).__name__)
            raise DetectionError(
                f"Image moderation failed: {str(e)}",
                details={"error": str(e)}
            )
    
    def _parse_results(self, results: list) -> Dict[str, Any]:
        """
        Parse moderation results into a structured format.
        
        Args:
            results: Model output
        
        Returns:
            Dictionary with moderation results
        """
        # Extract scores for each category
        categories = {}
        flagged_categories = []
        unsafe_score = 0.0
        unsafe_category = None
        
        # Define unsafe categories (not "normal" or "safe")
        unsafe_labels = ["nsfw", "inappropriate", "violence", "gore", "explicit"]
        
        for result in results:
            label = result["label"]
            score = result["score"]
            categories[label] = score
            
            # Track highest unsafe score
            if label.lower() in unsafe_labels or label.lower() != "normal":
                if label.lower() in unsafe_labels and score > unsafe_score:
                    unsafe_score = score
                    unsafe_category = label
            
            # Check if unsafe category exceeds threshold
            if label.lower() in unsafe_labels and score > self.threshold:
                flagged_categories.append({
                    "category": label,
                    "confidence": round(score, 4)
                })
        
        # Determine if image is safe (unsafe score must be below threshold)
        is_safe = unsafe_score <= self.threshold
        
        # Determine severity based on unsafe score
        if unsafe_score > 0.9:
            severity = "high"
        elif unsafe_score > 0.7:
            severity = "medium"
        elif unsafe_score > 0.5:
            severity = "low"
        else:
            severity = "none"
        
        return {
            "is_safe": is_safe,
            "overall_score": round(unsafe_score, 4),
            "flagged_category": unsafe_category if not is_safe else None,
            "severity": severity,
            "categories": {k: round(v, 4) for k, v in categories.items()},
            "flags": flagged_categories,
            "threshold": self.threshold
        }
    
    def update_threshold(self, threshold: float) -> None:
        """
        Update the moderation threshold.
        
        Args:
            threshold: New threshold value (0-1)
        """
        if not 0 <= threshold <= 1:
            raise ValueError("Threshold must be between 0 and 1")
        
        old_threshold = self.threshold
        self.threshold = threshold
        logger.info(
            "moderation_threshold_updated",
            old_threshold=old_threshold,
            new_threshold=threshold
        )
