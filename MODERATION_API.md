# 🛡️ Image Content Moderation API

## Overview

The Image Moderation API endpoint provides automated content moderation to detect inappropriate images including NSFW content, violence, gore, and other harmful material.

## Endpoint

```
POST /api/v1/moderate
```

## Features

✅ **AI-Powered Detection** - Uses state-of-the-art models from Hugging Face  
✅ **Configurable Threshold** - Adjust sensitivity to your needs  
✅ **Detailed Scores** - Get confidence scores for each category  
✅ **Multiple Categories** - Detects various types of inappropriate content  
✅ **Fast Processing** - Real-time moderation with quick response times  
✅ **Rate Limited** - Protected against abuse  

## How It Works

1. Upload an image file
2. AI model analyzes the content
3. Returns safety assessment with confidence scores
4. Flags content that exceeds the threshold

## Request

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file` | File | Yes | - | Image file (JPEG, PNG, etc.) |
| `threshold` | float | No | 0.7 | Confidence threshold (0-1) for flagging |

### Example Request

```bash
# Basic moderation with default threshold (0.7)
curl -X POST "http://localhost:8000/api/v1/moderate" \
     -F "file=@image.jpg"

# With custom threshold (stricter at 0.5)
curl -X POST "http://localhost:8000/api/v1/moderate?threshold=0.5" \
     -F "file=@image.jpg"

# More lenient (0.9)
curl -X POST "http://localhost:8000/api/v1/moderate?threshold=0.9" \
     -F "file=@image.jpg"
```

## Response

### Response Model

```json
{
  "is_safe": true,
  "overall_score": 0.0001,
  "flagged_category": null,
  "severity": "none",
  "categories": {
    "normal": 0.9999,
    "nsfw": 0.0001
  },
  "flags": [],
  "threshold": 0.7,
  "request_id": "abc123...",
  "message": "Image passed content moderation checks."
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `is_safe` | boolean | Whether the image passed moderation |
| `overall_score` | float | Highest unsafe category score (0-1) |
| `flagged_category` | string\|null | Primary category if flagged |
| `severity` | string | Risk level: "none", "low", "medium", "high" |
| `categories` | object | Scores for all detected categories |
| `flags` | array | List of flagged categories with scores |
| `threshold` | float | Threshold used for this request |
| `request_id` | string | Unique request identifier |
| `message` | string | Human-readable result message |

### Severity Levels

| Severity | Score Range | Description |
|----------|-------------|-------------|
| `none` | 0.0 - 0.5 | Safe content |
| `low` | 0.5 - 0.7 | Slightly concerning |
| `medium` | 0.7 - 0.9 | Potentially inappropriate |
| `high` | 0.9 - 1.0 | Highly inappropriate |

## Examples

### Safe Image Response

```json
{
  "is_safe": true,
  "overall_score": 0.0001,
  "flagged_category": null,
  "severity": "none",
  "categories": {
    "normal": 0.9999,
    "nsfw": 0.0001
  },
  "flags": [],
  "threshold": 0.7,
  "message": "Image passed content moderation checks."
}
```

### Flagged Image Response

```json
{
  "is_safe": false,
  "overall_score": 0.9234,
  "flagged_category": "nsfw",
  "severity": "high",
  "categories": {
    "normal": 0.0766,
    "nsfw": 0.9234
  },
  "flags": [
    {
      "category": "nsfw",
      "confidence": 0.9234
    }
  ],
  "threshold": 0.7,
  "message": "Image flagged as potentially inappropriate. Primary concern: nsfw (confidence: 92.34%)"
}
```

## Python Integration

### Basic Usage

```python
import requests

def moderate_image(image_path, threshold=0.7):
    """Moderate an image file"""
    with open(image_path, "rb") as f:
        response = requests.post(
            "http://localhost:8000/api/v1/moderate",
            files={"file": f},
            params={"threshold": threshold}
        )
    
    return response.json()

# Test an image
result = moderate_image("photo.jpg")

if result["is_safe"]:
    print("✅ Image is safe!")
else:
    print(f"⚠️  Image flagged!")
    print(f"Category: {result['flagged_category']}")
    print(f"Confidence: {result['overall_score']:.2%}")
    print(f"Severity: {result['severity']}")
```

### Advanced Usage with Error Handling

```python
import requests
from typing import Dict, Optional

class ImageModerator:
    """Client for image moderation API"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.endpoint = f"{api_url}/api/v1/moderate"
    
    def moderate(
        self,
        image_path: str,
        threshold: float = 0.7,
        timeout: int = 30
    ) -> Dict:
        """
        Moderate an image.
        
        Args:
            image_path: Path to image file
            threshold: Confidence threshold (0-1)
            timeout: Request timeout in seconds
        
        Returns:
            Moderation result dictionary
        
        Raises:
            requests.RequestException: On network errors
        """
        try:
            with open(image_path, "rb") as f:
                response = requests.post(
                    self.endpoint,
                    files={"file": f},
                    params={"threshold": threshold},
                    timeout=timeout
                )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error moderating image: {e}")
            raise
    
    def is_safe(self, image_path: str, threshold: float = 0.7) -> bool:
        """Quick check if image is safe"""
        result = self.moderate(image_path, threshold)
        return result["is_safe"]
    
    def get_risk_score(self, image_path: str) -> float:
        """Get overall risk score"""
        result = self.moderate(image_path)
        return result["overall_score"]

# Usage
moderator = ImageModerator()

# Quick safety check
if moderator.is_safe("image.jpg"):
    print("✅ Safe to display")
else:
    print("⚠️  Potentially inappropriate")

# Get detailed results
result = moderator.moderate("image.jpg", threshold=0.8)
print(f"Risk Score: {result['overall_score']:.2%}")
print(f"Severity: {result['severity']}")
```

## Threshold Configuration

### Recommended Thresholds

| Use Case | Threshold | Description |
|----------|-----------|-------------|
| **Social Media** | 0.7 | Balanced approach |
| **Children's App** | 0.5 | Strict filtering |
| **Adult Platform** | 0.9 | Lenient filtering |
| **News/Media** | 0.6 | Moderate filtering |

### Choosing a Threshold

- **Lower threshold (0.5)**: More strict, catches more content but may have false positives
- **Medium threshold (0.7)**: Balanced, good for most applications
- **Higher threshold (0.9)**: More lenient, only flags very obvious content

## Error Responses

### 400 - Invalid Input

```json
{
  "error": "InvalidImageError",
  "message": "Invalid image format",
  "details": {...}
}
```

### 413 - File Too Large

```json
{
  "error": "FileSizeExceededError",
  "message": "File size exceeds maximum allowed (10MB)",
  "details": {...}
}
```

### 415 - Unsupported File Type

```json
{
  "error": "UnsupportedFileTypeError",
  "message": "File type not supported",
  "details": {...}
}
```

### 429 - Rate Limit Exceeded

```
Too Many Requests
```

### 503 - Service Not Ready

```json
{
  "detail": "Service not ready"
}
```

## Performance

- **Average Processing Time**: 1-3 seconds
- **Max File Size**: 10MB (configurable)
- **Supported Formats**: JPEG, PNG, GIF, BMP, WebP
- **Rate Limit**: 100 requests/minute (configurable)

## Categories Detected

The model detects the following categories:

- **normal** - Safe, appropriate content
- **nsfw** - Not Safe For Work content
- Additional categories depend on the model used

## Best Practices

### 1. Set Appropriate Thresholds

```python
# For a children's app
result = moderate_image("image.jpg", threshold=0.5)

# For adult social media
result = moderate_image("image.jpg", threshold=0.8)
```

### 2. Handle Errors Gracefully

```python
try:
    result = moderate_image("image.jpg")
    if not result["is_safe"]:
        # Block or blur the image
        handle_inappropriate_content(result)
except Exception as e:
    # Log error and fail safe
    log_error(e)
    # Default to blocking if moderation fails
    block_image()
```

### 3. Log Moderation Results

```python
result = moderate_image("image.jpg")
log_moderation(
    request_id=result["request_id"],
    is_safe=result["is_safe"],
    score=result["overall_score"],
    category=result["flagged_category"]
)
```

### 4. Cache Results

```python
# Cache moderation results to avoid re-processing
cache_key = hash_image(image_path)
if cache_key in moderation_cache:
    return moderation_cache[cache_key]

result = moderate_image(image_path)
moderation_cache[cache_key] = result
return result
```

## Testing

Run the test script:

```bash
./venv/bin/python test_moderation.py
```

Or test manually:

```bash
# Test with a known safe image
curl -X POST "http://localhost:8000/api/v1/moderate" \
     -F "file=@safe_image.jpg" | python3 -m json.tool

# Test with different thresholds
curl -X POST "http://localhost:8000/api/v1/moderate?threshold=0.5" \
     -F "file=@image.jpg" | python3 -m json.tool
```

## Monitoring

Check moderation metrics:

```bash
curl http://localhost:8000/metrics | grep moderation
```

View logs:

```bash
tail -f /tmp/iimage_api.log | grep moderation
```

## Limitations

1. **Model Accuracy**: Not 100% accurate, may have false positives/negatives
2. **Context-Unaware**: Cannot understand context or artistic intent
3. **Language-Specific**: Primarily trained on Western content
4. **Processing Time**: Takes 1-3 seconds per image
5. **File Size**: Limited to 10MB per file

## Support

- **API Documentation**: <http://localhost:8000/docs>
- **Interactive Testing**: <http://localhost:8000/docs#/Moderation/moderate_image_api_v1_moderate_post>
- **Test Script**: `./venv/bin/python test_moderation.py`

## Model Information

- **Model**: Falconsai/nsfw_image_detection
- **Source**: Hugging Face Transformers
- **Type**: Image Classification
- **Categories**: Normal, NSFW

---

**Last Updated**: October 28, 2025  
**API Version**: 1.0.0
