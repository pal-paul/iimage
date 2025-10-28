#!/bin/bash

# Deployment script for production environments

set -e

echo "========================================="
echo "Image Detection API - Production Deploy"
echo "========================================="

# Configuration
ENV=${1:-production}
VERSION=$(git describe --tags --always --dirty)
IMAGE_NAME="image-detection-api"
REGISTRY=${REGISTRY:-""}

echo ""
echo "Environment: $ENV"
echo "Version: $VERSION"
echo ""

# Build production image
echo "Building production Docker image..."
docker build -f Dockerfile.prod -t ${IMAGE_NAME}:${VERSION} .
docker tag ${IMAGE_NAME}:${VERSION} ${IMAGE_NAME}:latest

# Optional: Push to registry
if [ -n "$REGISTRY" ]; then
    echo "Pushing to registry: $REGISTRY"
    docker tag ${IMAGE_NAME}:${VERSION} ${REGISTRY}/${IMAGE_NAME}:${VERSION}
    docker tag ${IMAGE_NAME}:${VERSION} ${REGISTRY}/${IMAGE_NAME}:latest
    docker push ${REGISTRY}/${IMAGE_NAME}:${VERSION}
    docker push ${REGISTRY}/${IMAGE_NAME}:latest
fi

# Deploy with docker-compose
echo "Deploying with docker-compose..."
docker-compose -f docker-compose.yml down
docker-compose -f docker-compose.yml up -d

# Wait for health check
echo "Waiting for service to be healthy..."
for i in {1..30}; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✓ Service is healthy!"
        break
    fi
    echo "Waiting... ($i/30)"
    sleep 2
done

echo ""
echo "========================================="
echo "Deployment complete!"
echo "========================================="
echo "API: http://localhost:8000"
echo "Docs: http://localhost:8000/docs"
echo "Health: http://localhost:8000/health"
echo "Metrics: http://localhost:8000/metrics"
echo ""
