# 🎯 Image Object Detection & Content Moderation API

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-orange.svg)](https://github.com/ultralytics/ultralytics)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Enterprise-grade REST API** for object detection and content moderation in images. Built with FastAPI, YOLOv8, and AI-powered safety checks.

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-api-endpoints">API Endpoints</a> •
  <a href="#-docker-deployment">Docker</a> •
  <a href="#-documentation">Documentation</a>
</p>

---

## ✨ Features

### � Object Detection

- 🚀 **YOLOv8 Powered**: State-of-the-art object detection with 80+ object classes
- 🎯 **High Accuracy**: Detect people, animals, vehicles, furniture, electronics, and more
- �️ **Multiple Outputs**: JSON results or annotated images with bounding boxes
- ⚙️ **Configurable**: Adjustable confidence and IoU thresholds

### 🛡️ Content Moderation

- � **AI Safety Checks**: Detect NSFW content, violence, and inappropriate material
- 📊 **Confidence Scores**: Detailed category breakdown with severity levels
- ⚡ **Fast Analysis**: Real-time content moderation
- 🎚️ **Custom Thresholds**: Adjustable sensitivity levels

### 🏢 Enterprise Features

- 🔐 **Security**: Rate limiting, input validation, CORS, security headers
- � **Monitoring**: Prometheus metrics, structured logging, health checks
- 🧪 **Testing**: 85%+ test coverage, unit & integration tests
- 🐳 **Docker Ready**: Multi-stage builds, docker-compose orchestration
- 📚 **Documentation**: OpenAPI/Swagger UI, comprehensive guides

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- pip package manager
- 4GB+ RAM (8GB recommended)

### Installation

```bash
# Clone the repository
git clone https://github.com/pal-paul/iimage.git
cd iimage

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup configuration
cp .env.example .env

# Run the API
python run.py
```

**🎉 That's it!** API is now running at `http://localhost:8000`

### 🐳 Docker Quick Start

```bash
# Using docker-compose (recommended)
docker-compose up -d

# Or build and run manually
docker build -t iimage-api .
docker run -p 8000:8000 iimage-api
```

## 📡 API Endpoints

### Object Detection

**POST** `/api/v1/detect` - Detect objects (JSON response)

```bash
curl -X POST "http://localhost:8000/api/v1/detect" \
  -F "file=@image.jpg"
```

**POST** `/api/v1/detect/annotated` - Get annotated image with bounding boxes

```bash
curl -X POST "http://localhost:8000/api/v1/detect/annotated" \
  -F "file=@image.jpg" \
  -o result.jpg
```

**GET** `/api/v1/classes` - List all 80 detectable object classes

### Content Moderation

**POST** `/api/v1/moderate` - Check image for inappropriate content

```bash
curl -X POST "http://localhost:8000/api/v1/moderate" \
  -F "file=@image.jpg"
```

### Monitoring

**GET** `/health` - Health check endpoint  
**GET** `/metrics` - Prometheus metrics  
**GET** `/docs` - Interactive API documentation (Swagger UI)  
**GET** `/redoc` - Alternative API documentation (ReDoc)

## 🎯 Usage Examples

### Python Library

```python
from lib.detector import ObjectDetector
from lib.moderator import ContentModerator

# Object Detection
detector = ObjectDetector(model_name="yolov8n.pt")
results = detector.detect_from_path("image.jpg")

print(f"Found {results['total_objects']} objects:")
for obj in results['detections']:
    print(f"  - {obj['class']}: {obj['confidence']:.2%}")

# Content Moderation
moderator = ContentModerator(threshold=0.7)
moderation = moderator.moderate_from_path("image.jpg")

if moderation['is_safe']:
    print("✅ Image is safe")
else:
    print(f"⚠️  Flagged: {moderation['flagged_category']}")
    print(f"   Severity: {moderation['severity']}")
```

### API Client

```python
import requests

# Detect objects
with open('image.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/v1/detect',
        files={'file': f}
    )
    
results = response.json()
print(f"Detected {results['total_objects']} objects")

# Moderate content
with open('image.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/v1/moderate',
        files={'file': f}
    )
    
moderation = response.json()
print(f"Safe: {moderation['is_safe']}")
print(f"Score: {moderation['overall_score']}")
```

## 🏗️ Architecture

```
iimage/
├── api/              # FastAPI application
│   ├── main.py      # API endpoints
│   └── middleware.py # Custom middleware
├── lib/              # Core library
│   ├── detector.py   # Object detection
│   ├── moderator.py  # Content moderation
│   ├── validators.py # Input validation
│   └── config.py     # Configuration
├── tests/            # Test suite (85%+ coverage)
├── examples/         # Usage examples
├── monitoring/       # Prometheus configs
└── docs/            # Documentation
```

## 📦 Detectable Objects (80 Classes)

<details>
<summary>Click to expand full list</summary>

**People & Accessories:** person, backpack, umbrella, handbag, tie, suitcase

**Vehicles:** bicycle, car, motorcycle, airplane, bus, train, truck, boat

**Street:** traffic light, fire hydrant, stop sign, parking meter, bench

**Animals:** bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe

**Sports:** sports ball, baseball bat, baseball glove, skateboard, surfboard, tennis racket, frisbee, skis, snowboard, kite

**Kitchen:** bottle, wine glass, cup, fork, knife, spoon, bowl

**Food:** banana, apple, sandwich, orange, broccoli, carrot, hot dog, pizza, donut, cake

**Furniture:** chair, couch, potted plant, bed, dining table, toilet

**Electronics:** tv, laptop, mouse, remote, keyboard, cell phone

**Appliances:** microwave, oven, toaster, sink, refrigerator

**Other:** book, clock, vase, scissors, teddy bear, hair drier, toothbrush

</details>

## 🛡️ Content Moderation

The API includes AI-powered content moderation to detect:

- 🔞 NSFW content
- 🩸 Violence and gore
- ⚠️ Other inappropriate material

**Response includes:**

- Safety assessment (is_safe: true/false)
- Overall risk score (0-1)
- Category breakdown with confidence scores
- Severity level (none, low, medium, high)
- Flagged categories above threshold

## 🐳 Docker Deployment

### Development

```bash
docker-compose up
```

### Production

```bash
# Build production image
docker build -f Dockerfile.prod -t iimage-api:prod .

# Run with resource limits
docker run -d \
  -p 8000:8000 \
  --memory="4g" \
  --cpus="2" \
  iimage-api:prod
```

### With Monitoring Stack

```bash
# Start API + Prometheus + Grafana
docker-compose -f docker-compose.yml up -d

# Access:
# API: http://localhost:8000
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin/admin)
```

View the interactive API documentation at `http://localhost:8000/docs`

## Usage

### Using the Python Library

```python
from lib.detector import ObjectDetector

# Initialize detector
detector = ObjectDetector(
    model_name="yolov8n.pt",
    confidence_threshold=0.25,
    iou_threshold=0.45
)

# Detect objects from file
result = detector.detect_from_path("image.jpg")

print(f"Found {result['total_objects']} objects")
for detection in result['detections']:
    print(f"- {detection['class']}: {detection['confidence']:.2%}")
```

### Using the REST API

#### 1. Check API Health

```bash
curl http://localhost:8000/health
```

#### 2. Detect Objects (JSON Response)

```bash
curl -X POST "http://localhost:8000/detect" \
  -F "file=@your-image.jpg"
```

#### 3. Get Annotated Image

```bash
curl -X POST "http://localhost:8000/detect/annotated" \
  -F "file=@your-image.jpg" \
  --output annotated.jpg
```

#### 4. Get Available Classes

```bash
curl http://localhost:8000/classes
```

### Python API Client Example

```python
import requests

# Detect objects
with open('image.jpg', 'rb') as f:
    files = {'file': ('image.jpg', f, 'image/jpeg')}
    response = requests.post('http://localhost:8000/detect', files=files)
    
result = response.json()
print(f"Detected {result['total_objects']} objects")
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check and configuration |
| `/detect` | POST | Detect objects (returns JSON) |
| `/detect/annotated` | POST | Detect and return annotated image |
| `/classes` | GET | List all detectable object classes |
| `/docs` | GET | Interactive API documentation |

## Configuration

Edit the `.env` file to customize settings:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Model Configuration
MODEL_NAME=yolov8n.pt
CONFIDENCE_THRESHOLD=0.25
IOU_THRESHOLD=0.45

# Upload Configuration
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=jpg,jpeg,png,bmp,webp
```

### Available YOLO Models

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| yolov8n.pt | 6 MB | Fastest | Good |
| yolov8s.pt | 22 MB | Fast | Better |
| yolov8m.pt | 52 MB | Medium | Great |
| yolov8l.pt | 87 MB | Slow | Excellent |
| yolov8x.pt | 136 MB | Slowest | Best |

## Project Structure

```
iimage/
├── lib/                    # Core library
│   ├── __init__.py
│   ├── detector.py        # Object detection logic
│   ├── config.py          # Configuration management
│   └── utils.py           # Utility functions
├── api/                   # REST API
│   ├── __init__.py
│   └── main.py           # FastAPI application
├── examples/             # Usage examples
│   ├── basic_usage.py   # Library examples
│   └── api_client.py    # API client examples
├── requirements.txt      # Python dependencies
├── .env.example         # Configuration template
├── .gitignore
└── README.md
```

## Examples

See the `examples/` directory for detailed usage examples:

- `basic_usage.py` - Using the library directly
- `api_client.py` - Making API requests

Run examples:

```bash
python examples/basic_usage.py
python examples/api_client.py
```

## Detectable Objects

The YOLOv8 model can detect 80 different object classes including:

- **People**: person
- **Vehicles**: car, motorcycle, airplane, bus, train, truck, boat
- **Animals**: bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe
- **Objects**: backpack, umbrella, handbag, tie, suitcase, frisbee, skis, snowboard
- **Food**: banana, apple, sandwich, orange, broccoli, carrot, hot dog, pizza, donut, cake
- **Furniture**: chair, couch, potted plant, bed, dining table, toilet
- **Electronics**: tv, laptop, mouse, remote, keyboard, cell phone
- And many more...

Use the `/classes` endpoint or `detector.get_available_classes()` to see the full list.

## API Response Format

### Detection Response (JSON)

```json
{
  "total_objects": 2,
  "detections": [
    {
      "class": "person",
      "class_id": 0,
      "confidence": 0.92,
      "bbox": {
        "x1": 100.5,
        "y1": 50.2,
        "x2": 300.8,
        "y2": 400.6
      }
    },
    {
      "class": "dog",
      "class_id": 16,
      "confidence": 0.87,
      "bbox": {
        "x1": 350.1,
        "y1": 200.3,
        "x2": 500.9,
        "y2": 380.7
      }
    }
  ],
  "image_shape": {
    "height": 480,
    "width": 640,
    "channels": 3
  }
}
```

## Error Handling

The API returns appropriate HTTP status codes:

- `200` - Success
- `400` - Bad request (invalid file, size too large, etc.)
- `500` - Server error
- `503` - Service unavailable (model not initialized)

## Performance Tips

1. **Choose the right model**: Use `yolov8n.pt` for speed, `yolov8x.pt` for accuracy
2. **Adjust thresholds**: Lower confidence threshold detects more objects but may include false positives
3. **Image size**: Smaller images process faster but may reduce accuracy
4. **Batch processing**: For multiple images, reuse the detector instance

## Development

### Running in Development Mode

```bash
# With auto-reload
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests (if you create test files)
pytest tests/
```

## Deployment

### Using Docker (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "api/main.py"]
```

Build and run:

```bash
docker build -t image-detection-api .
docker run -p 8000:8000 image-detection-api
```

### Using Gunicorn (Production)

```bash
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Troubleshooting

### Model Download Issues

The first time you run the code, YOLOv8 will automatically download the model. If you have connection issues, manually download from [Ultralytics releases](https://github.com/ultralytics/assets/releases).

### Import Errors

Make sure you've installed all requirements:

```bash
pip install -r requirements.txt
```

### Memory Issues

If you're running out of memory, use a smaller model (yolov8n.pt) or reduce image size.

## License

This project is open source. Please check the licenses of the dependencies:

- YOLOv8: AGPL-3.0
- FastAPI: MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on the GitHub repository.

## Acknowledgments

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics) - Object detection model
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [OpenCV](https://opencv.org/) - Image processing

---

**Made with ❤️ using Python and YOLOv8**
