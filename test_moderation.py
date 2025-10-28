#!/usr/bin/env python3
"""
Test script for the Image Moderation API endpoint
"""

import sys
from pathlib import Path

import requests


def test_moderation():
    """Test the image moderation endpoint"""
    base_url = "http://localhost:8000"
    
    print("=" * 70)
    print("🛡️  IMAGE CONTENT MODERATION API TEST")
    print("=" * 70)
    
    # Check if API is running
    try:
        health = requests.get(f"{base_url}/health", timeout=2)
        if health.status_code != 200:
            print("\n❌ API is not responding correctly")
            return False
    except requests.exceptions.RequestException:
        print("\n❌ API is not running!")
        print("   Please start the API first: ./start.sh")
        return False
    
    print("\n✅ API is running\n")
    
    # Test 1: Moderate the safe test image
    print("=" * 70)
    print("TEST 1: Moderating Safe Image")
    print("=" * 70)
    
    test_image = "test_with_people.jpg"
    if not Path(test_image).exists():
        print(f"⚠️  Test image '{test_image}' not found. Using any available image...")
        test_image = "annotated_example.jpg"
    
    if Path(test_image).exists():
        print(f"\n📁 Testing with: {test_image}")
        
        with open(test_image, "rb") as f:
            response = requests.post(
                f"{base_url}/api/v1/moderate",
                files={"file": f}
            )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n{'✅ SAFE' if result['is_safe'] else '⚠️  FLAGGED'}")
            print(f"{'─' * 70}")
            print(f"Overall Score:     {result['overall_score']:.4f}")
            print(f"Severity:          {result['severity']}")
            print(f"Threshold Used:    {result['threshold']}")
            print(f"Message:           {result['message']}")
            
            print(f"\n📊 Category Scores:")
            for category, score in result['categories'].items():
                emoji = "✅" if score < 0.5 else "⚠️"
                print(f"  {emoji} {category:<15} {score:.4f} ({score*100:.2f}%)")
            
            if result['flags']:
                print(f"\n🚩 Flagged Categories:")
                for flag in result['flags']:
                    print(f"  ⚠️  {flag['category']}: {flag['confidence']:.4f}")
            else:
                print(f"\n✅ No flags - Image is safe!")
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(response.text)
            return False
    
    # Test 2: Custom threshold
    print(f"\n{'=' * 70}")
    print("TEST 2: Testing with Custom Threshold (0.5)")
    print("=" * 70)
    
    if Path(test_image).exists():
        with open(test_image, "rb") as f:
            response = requests.post(
                f"{base_url}/api/v1/moderate",
                files={"file": f},
                params={"threshold": 0.5}
            )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n{'✅ SAFE' if result['is_safe'] else '⚠️  FLAGGED'} (threshold: {result['threshold']})")
            print(f"Overall Score: {result['overall_score']:.4f}")
            print(f"Message: {result['message']}")
        else:
            print(f"❌ Request failed: {response.status_code}")
    
    # Usage examples
    print(f"\n{'=' * 70}")
    print("📚 USAGE EXAMPLES")
    print("=" * 70)
    
    print("""
1️⃣  Basic moderation (default threshold 0.7):
   curl -X POST "http://localhost:8000/api/v1/moderate" \\
        -F "file=@your_image.jpg"

2️⃣  With custom threshold (stricter at 0.5):
   curl -X POST "http://localhost:8000/api/v1/moderate?threshold=0.5" \\
        -F "file=@your_image.jpg"

3️⃣  Python example:
   import requests
   
   with open("image.jpg", "rb") as f:
       response = requests.post(
           "http://localhost:8000/api/v1/moderate",
           files={"file": f},
           params={"threshold": 0.7}
       )
   
   result = response.json()
   if result["is_safe"]:
       print("✅ Image is safe!")
   else:
       print(f"⚠️  Flagged: {result['flagged_category']}")
       print(f"   Confidence: {result['overall_score']:.2%}")
""")
    
    print("=" * 70)
    print("✅ MODERATION API TEST COMPLETE")
    print("=" * 70)
    print(f"\n📖 Interactive API docs: {base_url}/docs")
    print(f"   See the /api/v1/moderate endpoint for details\n")
    
    return True


def main():
    """Main function"""
    try:
        success = test_moderation()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
