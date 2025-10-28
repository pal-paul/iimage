#!/usr/bin/env python3
"""
Quick start script to run the API server.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn

from api.main import app
from lib.config import config

if __name__ == "__main__":
    print("=" * 60)
    print("Image Object Detection API")
    print("=" * 60)
    print(f"\nStarting server on http://{config.HOST}:{config.PORT}")
    print(f"Model: {config.MODEL_NAME}")
    print(f"Confidence threshold: {config.CONFIDENCE_THRESHOLD}")
    print(f"IoU threshold: {config.IOU_THRESHOLD}")
    print("\nAPI Documentation: http://localhost:8000/docs")
    print("=" * 60)
    print("\nPress CTRL+C to stop the server\n")
    
    uvicorn.run(
        app,
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG
    )
