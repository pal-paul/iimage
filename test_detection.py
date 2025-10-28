#!/usr/bin/env python3
"""
Test the Image Detection API with sample images or create a test image.
"""

import io
import sys

import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFont


def create_test_image():
    """Create a simple test image with common objects"""
    # Create a white canvas
    width, height = 800, 600
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw some simple shapes that might look like objects
    # Draw a "car" (rectangle with wheels)
    draw.rectangle([100, 300, 300, 400], fill='blue', outline='black', width=3)
    draw.ellipse([110, 390, 160, 440], fill='black')  # Wheel
    draw.ellipse([240, 390, 290, 440], fill='black')  # Wheel
    draw.rectangle([150, 280, 200, 300], fill='lightblue', outline='black')  # Window
    
    # Draw a "person" (stick figure)
    draw.ellipse([450, 200, 500, 250], fill='peachpuff', outline='black', width=2)  # Head
    draw.line([475, 250, 475, 350], fill='black', width=3)  # Body
    draw.line([475, 280, 430, 320], fill='black', width=3)  # Arm
    draw.line([475, 280, 520, 320], fill='black', width=3)  # Arm
    draw.line([475, 350, 440, 420], fill='black', width=3)  # Leg
    draw.line([475, 350, 510, 420], fill='black', width=3)  # Leg
    
    # Draw a "bottle"
    draw.rectangle([600, 300, 650, 450], fill='green', outline='darkgreen', width=2)
    draw.rectangle([590, 280, 660, 310], fill='darkgreen', outline='black', width=2)
    
    # Add text
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 30)
    except:
        font = ImageFont.load_default()
    
    draw.text((250, 50), "Test Image", fill='black', font=font)
    
    return img


def test_detection_with_url(image_url: str):
    """Test detection with an image URL"""
    print(f"\n🔍 Testing detection with URL: {image_url}\n")
    print("=" * 70)
    
    # Download image
    print("📥 Downloading image...")
    response = requests.get(image_url)
    if response.status_code != 200:
        print(f"❌ Failed to download image: {response.status_code}")
        return False
    
    # Save to temp file
    img_bytes = io.BytesIO(response.content)
    
    # Test detection
    print("🔍 Running object detection...")
    api_response = requests.post(
        "http://localhost:8000/api/v1/detect",
        files={"file": ("test_image.jpg", img_bytes, "image/jpeg")}
    )
    
    if api_response.status_code != 200:
        print(f"❌ Detection failed: {api_response.status_code}")
        print(api_response.text)
        return False
    
    result = api_response.json()
    print(f"\n✅ Detection completed!")
    print(f"📊 Total objects found: {result['total_objects']}")
    
    if result['total_objects'] > 0:
        print(f"\n🎯 Detected objects:")
        for i, det in enumerate(result['detections'], 1):
            print(f"  {i}. {det['class']:<15} (confidence: {det['confidence']:.2%})")
        
        # Get annotated image
        print(f"\n🎨 Getting annotated image...")
        img_bytes.seek(0)
        annotated_response = requests.post(
            "http://localhost:8000/api/v1/detect/annotated",
            files={"file": ("test_image.jpg", img_bytes, "image/jpeg")}
        )
        
        if annotated_response.status_code == 200:
            with open("annotated_test_output.jpg", "wb") as f:
                f.write(annotated_response.content)
            print("✅ Annotated image saved to: annotated_test_output.jpg")
        else:
            print(f"❌ Failed to get annotated image: {annotated_response.status_code}")
    else:
        print("\n⚠️  No objects detected in this image.")
        print("   The model can detect these types of objects:")
        print("   - People, animals (cat, dog, bird, etc.)")
        print("   - Vehicles (car, bicycle, bus, truck, etc.)")
        print("   - Common items (chair, laptop, phone, bottle, etc.)")
    
    return True


def test_with_generated_image():
    """Test with a generated test image"""
    print("\n🎨 Creating test image...\n")
    print("=" * 70)
    
    img = create_test_image()
    img.save("generated_test_image.jpg")
    print("✅ Test image created: generated_test_image.jpg")
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)
    
    # Test detection
    print("\n🔍 Running object detection...")
    response = requests.post(
        "http://localhost:8000/api/v1/detect",
        files={"file": ("test.jpg", img_bytes, "image/jpeg")}
    )
    
    if response.status_code != 200:
        print(f"❌ Detection failed: {response.status_code}")
        print(response.text)
        return False
    
    result = response.json()
    print(f"\n✅ Detection completed!")
    print(f"📊 Total objects found: {result['total_objects']}")
    
    if result['total_objects'] > 0:
        print(f"\n🎯 Detected objects:")
        for i, det in enumerate(result['detections'], 1):
            print(f"  {i}. {det['class']:<15} (confidence: {det['confidence']:.2%})")
    else:
        print("\n⚠️  No objects detected.")
        print("   Note: Simple drawings may not be recognized.")
        print("   Try with a real photo containing people, animals, or vehicles.")
    
    return True


def main():
    """Main test function"""
    print("\n" + "=" * 70)
    print("🧪 IMAGE DETECTION API TEST")
    print("=" * 70)
    
    # Check if API is running
    try:
        health = requests.get("http://localhost:8000/health", timeout=2)
        if health.status_code != 200:
            print("\n❌ API is not responding correctly")
            return 1
    except requests.exceptions.RequestException:
        print("\n❌ API is not running!")
        print("   Please start the API first:")
        print("   ./start.sh")
        return 1
    
    print("\n✅ API is running\n")
    
    # Test with a real image from the internet
    print("=" * 70)
    print("Testing with a real photo...")
    print("=" * 70)
    
    # Using a sample image that should have detectable objects
    # This is a public domain image from Unsplash
    test_url = "https://images.unsplash.com/photo-1544568100-847a948585b9?w=800"
    
    print("\n📝 Options:")
    print("  1. Test with online image (people in office)")
    print("  2. Test with generated simple image")
    print("  3. Test with your own image file")
    
    choice = input("\nSelect option (1-3) or press Enter for option 1: ").strip()
    
    if choice == "2":
        success = test_with_generated_image()
    elif choice == "3":
        image_path = input("Enter image path: ").strip()
        with open(image_path, "rb") as f:
            print(f"\n🔍 Testing with: {image_path}\n")
            response = requests.post(
                "http://localhost:8000/api/v1/detect",
                files={"file": f}
            )
            result = response.json()
            print(f"📊 Total objects found: {result['total_objects']}")
            if result['total_objects'] > 0:
                print(f"\n🎯 Detected objects:")
                for i, det in enumerate(result['detections'], 1):
                    print(f"  {i}. {det['class']:<15} (confidence: {det['confidence']:.2%})")
        success = True
    else:
        success = test_detection_with_url(test_url)
    
    print("\n" + "=" * 70)
    if success:
        print("✅ Test completed successfully!")
    else:
        print("❌ Test failed")
    print("=" * 70 + "\n")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
