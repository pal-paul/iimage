"""
Example showing how to use the API client.
"""

import json
from pathlib import Path

import requests

# API base URL
BASE_URL = "http://localhost:8000"


def check_health():
    """Check API health."""
    print("=== Checking API Health ===")
    response = requests.get(f"{BASE_URL}/health")
    print(json.dumps(response.json(), indent=2))
    print()


def get_available_classes():
    """Get all available detection classes."""
    print("=== Available Classes ===")
    response = requests.get(f"{BASE_URL}/classes")
    data = response.json()
    print(f"Total classes: {data['total_classes']}")
    print("\nSample classes:")
    for class_id, class_name in list(data['classes'].items())[:10]:
        print(f"  {class_id}: {class_name}")
    print("  ...\n")


def detect_objects(image_path: str, confidence: float = None, iou: float = None):
    """
    Detect objects in an image.
    
    Args:
        image_path: Path to the image file
        confidence: Optional confidence threshold
        iou: Optional IoU threshold
    """
    print(f"=== Detecting Objects in {Path(image_path).name} ===")
    
    # Prepare the file
    with open(image_path, 'rb') as f:
        files = {'file': (Path(image_path).name, f, 'image/jpeg')}
        
        # Optional parameters
        params = {}
        if confidence is not None:
            params['confidence'] = confidence
        if iou is not None:
            params['iou'] = iou
        
        # Make request
        response = requests.post(
            f"{BASE_URL}/detect",
            files=files,
            params=params
        )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Total objects detected: {result['total_objects']}")
        print(f"\nDetections:")
        for detection in result['detections']:
            print(f"  - {detection['class']}: {detection['confidence']:.2%}")
            print(f"    BBox: {detection['bbox']}")
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
    print()


def detect_and_save_annotated(image_path: str, output_path: str = None):
    """
    Detect objects and save annotated image.
    
    Args:
        image_path: Path to the input image
        output_path: Path to save the annotated image
    """
    print(f"=== Detecting and Annotating {Path(image_path).name} ===")
    
    if output_path is None:
        output_path = f"annotated_{Path(image_path).name}"
    
    # Prepare the file
    with open(image_path, 'rb') as f:
        files = {'file': (Path(image_path).name, f, 'image/jpeg')}
        
        # Make request
        response = requests.post(
            f"{BASE_URL}/detect/annotated",
            files=files
        )
    
    if response.status_code == 200:
        # Save the annotated image
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f"Annotated image saved to: {output_path}")
    else:
        print(f"Error: {response.status_code}")
    print()


def main():
    """Run API examples."""
    print("Object Detection API Examples\n")
    print("=" * 50)
    print("\nMake sure the API is running: python api/main.py\n")
    print("=" * 50)
    print()
    
    try:
        # Check health
        check_health()
        
        # Get available classes
        get_available_classes()
        
        # Example detection (update with your image path)
        image_path = "path/to/your/image.jpg"
        
        if Path(image_path).exists():
            # Basic detection
            detect_objects(image_path)
            
            # Detection with custom confidence
            detect_objects(image_path, confidence=0.5)
            
            # Get annotated image
            detect_and_save_annotated(image_path, "output_annotated.jpg")
        else:
            print(f"Image not found: {image_path}")
            print("Please provide a valid image path to test detection.")
    
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API.")
        print("Make sure the API is running on http://localhost:8000")
        print("\nStart the API with:")
        print("  python api/main.py")


if __name__ == "__main__":
    main()
