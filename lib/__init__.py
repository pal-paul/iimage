"""
Image Object Detection Library

This library provides a simple interface for detecting objects in images
using YOLOv8 (You Only Look Once) pre-trained models.
"""

__version__ = "1.0.0"
__author__ = "Your Name"

from .detector import ObjectDetector
from .moderator import ContentModerator

__all__ = ["ObjectDetector", "ContentModerator"]
