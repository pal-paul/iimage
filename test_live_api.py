#!/usr/bin/env python3
"""
Quick test script for the running Image Detection API
"""

import sys

import requests


def test_api():
    """Test the running API"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Image Object Detection API\n")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n1️⃣  Health Check")
    print("-" * 60)
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Get API info
    print("\n2️⃣  API Information")
    print("-" * 60)
    try:
        response = requests.get(base_url)
        data = response.json()
        print(f"Name: {data['name']}")
        print(f"Version: {data['version']}")
        print(f"Environment: {data['environment']}")
        print(f"Available endpoints: {len(data['endpoints'])}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 3: Get available classes
    print("\n3️⃣  Available Object Classes")
    print("-" * 60)
    try:
        response = requests.get(f"{base_url}/api/v1/classes")
        data = response.json()
        print(f"Total classes: {data['total_classes']}")
        print(f"Sample classes: {list(data['classes'].values())[:10]}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 4: Metrics endpoint
    print("\n4️⃣  Prometheus Metrics")
    print("-" * 60)
    try:
        response = requests.get(f"{base_url}/metrics")
        lines = response.text.split('\n')
        metric_lines = [l for l in lines if l and not l.startswith('#')][:5]
        print(f"Available metrics (sample):")
        for line in metric_lines:
            print(f"  {line}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)
    print(f"\n📚 Interactive API Documentation:")
    print(f"   Swagger UI: {base_url}/docs")
    print(f"   ReDoc:      {base_url}/redoc")
    print(f"\n🔍 To test object detection, upload an image:")
    print(f'   curl -X POST "{base_url}/api/v1/detect" \\')
    print(f'        -F "file=@your-image.jpg"')
    print(f"\n🎨 To get annotated image:")
    print(f'   curl -X POST "{base_url}/api/v1/detect/annotated" \\')
    print(f'        -F "file=@your-image.jpg" \\')
    print(f'        -o annotated_output.jpg')
    print()
    
    return True

if __name__ == "__main__":
    success = test_api()
    sys.exit(0 if success else 1)
