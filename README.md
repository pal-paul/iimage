# Image Object Detection API

A complete Python library and REST API for detecting objects in images using YOLOv8 (You Only Look Once) deep learning model.

## Features

- 🚀 **Fast & Accurate**: Uses YOLOv8 for state-of-the-art object detection
- 🎯 **80+ Object Classes**: Can detect people, vehicles, animals, and more
- 🔧 **Easy to Use**: Simple Python library and REST API
- ⚙️ **Configurable**: Adjustable confidence and IoU thresholds
- 📦 **Production Ready**: Built with FastAPI for high performance
- 🖼️ **Multiple Formats**: Supports JPG, PNG, BMP, WebP, and more

## Quick Start

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd iimage
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create configuration file:
```bash
cp .env.example .env
```

### Running the API

Start the API server:
```bash
python api/main.py
```

The API will be available at `http://localhost:8000`

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
