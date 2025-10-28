"""
Example script demonstrating how to use the object detection library.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json

from PIL import Image

from lib.detector import ObjectDetector


def example_basic_detection():
    """Basic example of detecting objects in an image."""
    print("=== Basic Object Detection Example ===\n")
    
    # Initialize detector
    detector = ObjectDetector(
        model_name="yolov8n.pt",  # nano model (fastest)
        confidence_threshold=0.25,
        iou_threshold=0.45
    )
    
    # Detect from file path (provide your own image path)
    image_path = "path/to/your/image.jpg"
    
    if os.path.exists(image_path):
        result = detector.detect_from_path(image_path)
        
        print(f"Total objects detected: {result['total_objects']}")
        print(f"\nDetections:")
        for detection in result['detections']:
            print(f"  - {detection['class']}: {detection['confidence']:.2%} confidence")
            print(f"    Location: {detection['bbox']}")
    else:
        print(f"Image not found: {image_path}")
        print("Please provide a valid image path to test detection.")


def example_pil_detection():
    """Example using PIL Image."""
    print("\n=== PIL Image Detection Example ===\n")
    
    detector = ObjectDetector()
    
    # Load image with PIL
    image_path = "path/to/your/image.jpg"
    
    if os.path.exists(image_path):
        pil_image = Image.open(image_path)
        
        # Detect objects
        result = detector.detect_from_pil(pil_image)
        
        print(json.dumps(result, indent=2))
    else:
        print(f"Image not found: {image_path}")


def example_custom_thresholds():
    """Example with custom detection thresholds."""
    print("\n=== Custom Thresholds Example ===\n")
    
    # Initialize with custom thresholds
    detector = ObjectDetector(
        confidence_threshold=0.5,  # Higher confidence
        iou_threshold=0.3
    )
    
    print(f"Initial thresholds:")
    print(f"  Confidence: {detector.confidence_threshold}")
    print(f"  IoU: {detector.iou_threshold}")
    
    # Update thresholds dynamically
    detector.update_thresholds(confidence_threshold=0.3)
    
    print(f"\nUpdated thresholds:")
    print(f"  Confidence: {detector.confidence_threshold}")
    print(f"  IoU: {detector.iou_threshold}")


def example_available_classes():
    """Example showing available detection classes."""
    print("\n=== Available Classes Example ===\n")
    
    detector = ObjectDetector()
    classes = detector.get_available_classes()
    
    print(f"Total classes: {len(classes)}")
    print("\nSample classes:")
    for class_id, class_name in list(classes.items())[:10]:
        print(f"  {class_id}: {class_name}")
    print("  ...")


if __name__ == "__main__":
    print("Object Detection Library Examples\n")
    print("=" * 50)
    
    # Run examples
    example_basic_detection()
    example_custom_thresholds()
    example_available_classes()
    # example_pil_detection()  # Uncomment to run
    
    print("\n" + "=" * 50)
    print("\nNote: Update image_path variables to test with actual images.")
