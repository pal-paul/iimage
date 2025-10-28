"""
Integration tests for the API.
"""

import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from api.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def sample_image_bytes():
    """Create sample image bytes."""
    img = Image.new("RGB", (200, 200), color="green")
    byte_arr = io.BytesIO()
    img.save(byte_arr, format="JPEG")
    byte_arr.seek(0)
    return byte_arr


class TestAPIEndpoints:
    """Test suite for API endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "endpoints" in data
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "model" in data
        assert "version" in data
    
    def test_classes_endpoint(self, client):
        """Test classes endpoint."""
        response = client.get("/api/v1/classes")
        assert response.status_code == 200
        data = response.json()
        assert "total_classes" in data
        assert "classes" in data
        assert data["total_classes"] == 80
    
    def test_detect_endpoint(self, client, sample_image_bytes):
        """Test detect endpoint with valid image."""
        files = {"file": ("test.jpg", sample_image_bytes, "image/jpeg")}
        response = client.post("/api/v1/detect", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert "total_objects" in data
        assert "detections" in data
        assert "image_shape" in data
        assert "request_id" in data
    
    def test_detect_with_confidence_param(self, client, sample_image_bytes):
        """Test detect endpoint with confidence parameter."""
        files = {"file": ("test.jpg", sample_image_bytes, "image/jpeg")}
        response = client.post(
            "/api/v1/detect",
            files=files,
            params={"confidence": 0.5}
        )
        
        assert response.status_code == 200
    
    def test_detect_annotated_endpoint(self, client, sample_image_bytes):
        """Test detect annotated endpoint."""
        files = {"file": ("test.jpg", sample_image_bytes, "image/jpeg")}
        response = client.post("/api/v1/detect/annotated", files=files)
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/jpeg"
        assert "X-Request-ID" in response.headers
        assert "X-Objects-Detected" in response.headers
    
    def test_detect_invalid_file_type(self, client):
        """Test detect with invalid file type."""
        files = {"file": ("test.txt", b"not an image", "text/plain")}
        response = client.post("/api/v1/detect", files=files)
        
        assert response.status_code == 415
        data = response.json()
        assert "error" in data
    
    def test_detect_file_too_large(self, client):
        """Test detect with oversized file."""
        # Create a large fake image
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        files = {"file": ("large.jpg", large_content, "image/jpeg")}
        response = client.post("/api/v1/detect", files=files)
        
        assert response.status_code == 413
    
    def test_detect_no_file(self, client):
        """Test detect without file."""
        response = client.post("/api/v1/detect")
        assert response.status_code == 422  # Validation error
