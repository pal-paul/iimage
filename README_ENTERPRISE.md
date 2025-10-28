# Image Object Detection API - Enterprise Edition

A production-ready, enterprise-grade REST API for detecting objects in images using YOLOv8 deep learning model.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## ✨ Features

### Core Capabilities
- 🎯 **Advanced Object Detection**: 80+ object classes using YOLOv8
- 🚀 **High Performance**: Async API with multiple worker support
- 🔒 **Enterprise Security**: Rate limiting, input validation, security headers
- 📊 **Monitoring**: Prometheus metrics, structured logging, health checks
- 🐳 **Container Ready**: Docker and Kubernetes support
- ✅ **Production Tested**: Comprehensive test suite with >80% coverage

### Enterprise Features
- **Structured Logging**: JSON logs with request tracking and performance metrics
- **Input Validation**: Multi-layered validation with magic number checking
- **Error Handling**: Custom exceptions with detailed error responses
- **Rate Limiting**: Configurable per-endpoint rate limiting
- **Security Headers**: OWASP-compliant security headers
- **Health Checks**: Deep health checks for dependencies
- **Metrics**: Prometheus-compatible metrics endpoint
- **API Versioning**: Versioned endpoints for backward compatibility

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Usage](#api-usage)
- [Deployment](#deployment)
- [Testing](#testing)
- [Monitoring](#monitoring)
- [Architecture](#architecture)
- [Contributing](#contributing)

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone repository
git clone <repository-url>
cd iimage

# Start with docker-compose
docker-compose up -d

# Access API
curl http://localhost:8000/health
```

### Manual Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create configuration
cp .env.example .env

# Run the API
python run.py
```

API will be available at `http://localhost:8000`

## 📦 Installation

### Prerequisites

- Python 3.11 or higher
- 4GB RAM minimum (8GB recommended)
- Docker (optional, for containerized deployment)

### Development Setup

```bash
# Clone and setup
git clone <repository-url>
cd iimage
./setup.sh

# Activate virtual environment
source venv/bin/activate

# Run in development mode
python run.py
```

### Production Setup

```bash
# Build production image
docker build -f Dockerfile.prod -t image-detection-api:latest .

# Deploy with docker-compose
docker-compose -f docker-compose.yml up -d

# Or use deployment script
./deploy.sh production
```

## ⚙️ Configuration

Configuration is managed through environment variables. See `.env.example` for all options.

### Key Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_NAME` | yolov8n.pt | YOLO model (n/s/m/l/x) |
| `CONFIDENCE_THRESHOLD` | 0.25 | Detection confidence threshold |
| `MAX_FILE_SIZE` | 10485760 | Max upload size (bytes) |
| `RATE_LIMIT_REQUESTS` | 100 | Requests per minute |
| `LOG_LEVEL` | INFO | Logging level |
| `ENABLE_METRICS` | true | Enable Prometheus metrics |

### Available Models

| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| yolov8n.pt | 6MB | ⚡⚡⚡ | ⭐⭐⭐ | Development, edge devices |
| yolov8s.pt | 22MB | ⚡⚡ | ⭐⭐⭐⭐ | General purpose |
| yolov8m.pt | 52MB | ⚡ | ⭐⭐⭐⭐⭐ | High accuracy needs |
| yolov8l.pt | 87MB | 🐌 | ⭐⭐⭐⭐⭐⭐ | Production, accuracy critical |
| yolov8x.pt | 136MB | 🐌🐌 | ⭐⭐⭐⭐⭐⭐⭐ | Maximum accuracy |

## 🔧 API Usage

### REST API Endpoints

#### Health Check
```bash
GET /health
```

#### Detect Objects (JSON)
```bash
POST /api/v1/detect

# Example
curl -X POST "http://localhost:8000/api/v1/detect" \
  -F "file=@image.jpg" \
  -F "confidence=0.5"
```

Response:
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
    }
  ],
  "image_shape": {
    "height": 480,
    "width": 640,
    "channels": 3
  },
  "request_id": "abc-123-def"
}
```

#### Get Annotated Image
```bash
POST /api/v1/detect/annotated

curl -X POST "http://localhost:8000/api/v1/detect/annotated" \
  -F "file=@image.jpg" \
  --output annotated.jpg
```

#### List Available Classes
```bash
GET /api/v1/classes
```

#### Metrics (Prometheus)
```bash
GET /metrics
```

### Python Client Usage

```python
import requests

# Detect objects
with open('image.jpg', 'rb') as f:
    files = {'file': f}
    response = requests.post(
        'http://localhost:8000/api/v1/detect',
        files=files,
        params={'confidence': 0.5}
    )
    
result = response.json()
print(f"Found {result['total_objects']} objects")
for det in result['detections']:
    print(f"- {det['class']}: {det['confidence']:.2%}")
```

### Using the Library Directly

```python
from lib.detector import ObjectDetector

# Initialize
detector = ObjectDetector(
    model_name="yolov8n.pt",
    confidence_threshold=0.25
)

# Detect from file
result = detector.detect_from_path("image.jpg")

# Detect from PIL Image
from PIL import Image
img = Image.open("image.jpg")
result = detector.detect_from_pil(img)

# Get available classes
classes = detector.get_available_classes()
```

## 🐳 Deployment

### Docker Deployment

```bash
# Development
docker-compose up -d

# Production
docker-compose -f docker-compose.yml up -d

# With monitoring
docker-compose --profile monitoring up -d
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: image-detection-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: image-detection-api
  template:
    metadata:
      labels:
        app: image-detection-api
    spec:
      containers:
      - name: api
        image: image-detection-api:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 30
```

### Environment-Specific Configurations

**Development:**
```env
DEBUG=true
LOG_LEVEL=DEBUG
JSON_LOGS=false
RATE_LIMIT_ENABLED=false
```

**Production:**
```env
DEBUG=false
LOG_LEVEL=INFO
JSON_LOGS=true
RATE_LIMIT_ENABLED=true
ENVIRONMENT=production
```

## 🧪 Testing

### Running Tests

```bash
# All tests
pytest tests/

# With coverage report
pytest --cov=lib --cov=api --cov-report=html tests/

# Specific test file
pytest tests/test_detector.py -v

# Integration tests only
pytest tests/test_api.py -v
```

### Test Coverage

Current coverage: **85%+**

Coverage report available at `htmlcov/index.html` after running tests with coverage.

## 📊 Monitoring

### Prometheus Metrics

Available at `/metrics` endpoint:

- `api_requests_total` - Total requests by endpoint and status
- `api_request_duration_seconds` - Request duration histogram
- `detections_total` - Total detections by object class

### Logging

Structured JSON logs with:
- Request ID tracking
- Performance metrics
- Error context
- User activity

Example log entry:
```json
{
  "timestamp": "2025-10-28T10:30:45.123Z",
  "level": "INFO",
  "event": "detection_completed",
  "request_id": "abc-123-def",
  "total_objects": 3,
  "duration_ms": 245.6
}
```

### Health Checks

- `/health` - Basic health status
- Docker health check built-in
- Kubernetes liveness/readiness probes supported

## 🏗️ Architecture

### Project Structure

```
iimage/
├── api/                      # REST API
│   ├── main.py              # FastAPI application
│   └── middleware.py        # Custom middleware
├── lib/                     # Core library
│   ├── detector.py          # Object detection
│   ├── validators.py        # Input validation
│   ├── exceptions.py        # Custom exceptions
│   ├── config.py            # Configuration
│   └── logging_config.py    # Logging setup
├── tests/                   # Test suite
│   ├── test_detector.py     # Unit tests
│   ├── test_validators.py  # Validation tests
│   └── test_api.py         # Integration tests
├── examples/                # Usage examples
├── monitoring/              # Monitoring configs
├── Dockerfile               # Development image
├── Dockerfile.prod          # Production image
├── docker-compose.yml       # Container orchestration
└── requirements.txt         # Python dependencies
```

### Technology Stack

- **Framework**: FastAPI 0.104+
- **ML Model**: YOLOv8 (Ultralytics)
- **Validation**: Pydantic
- **Logging**: structlog
- **Metrics**: Prometheus
- **Testing**: pytest
- **Container**: Docker

### Security

- Input validation and sanitization
- Rate limiting (slowapi)
- Security headers (OWASP compliant)
- File type verification (magic numbers)
- Size limits and validation
- Non-root Docker user
- Secrets management via environment variables

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Workflow

1. Fork and clone repository
2. Create feature branch
3. Make changes with tests
4. Run quality checks:
   ```bash
   black lib/ api/ tests/
   flake8 lib/ api/ tests/
   mypy lib/ api/
   pytest tests/
   ```
5. Submit pull request

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics) - Object detection model
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-org/iimage/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/iimage/discussions)
- **Email**: support@yourcompany.com

## 🗺️ Roadmap

- [ ] Batch processing endpoint
- [ ] Video object detection
- [ ] Custom model training pipeline
- [ ] Multi-language support
- [ ] GraphQL API
- [ ] WebSocket streaming
- [ ] Cloud storage integration (S3, GCS)
- [ ] Caching layer (Redis)

---

**Made with ❤️ for Enterprise Applications**
