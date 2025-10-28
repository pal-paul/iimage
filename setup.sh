#!/bin/bash

# Setup script for Image Object Detection API

echo "==================================================="
echo "Image Object Detection API - Setup"
echo "==================================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ".env file created. You can customize it if needed."
fi

# Create directories
echo ""
echo "Creating necessary directories..."
mkdir -p uploads
mkdir -p temp
mkdir -p models

echo ""
echo "==================================================="
echo "Setup complete!"
echo "==================================================="
echo ""
echo "To start using the API:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate  (macOS/Linux)"
echo "     venv\\Scripts\\activate  (Windows)"
echo ""
echo "  2. Start the API server:"
echo "     python api/main.py"
echo ""
echo "  3. Visit http://localhost:8000/docs for API documentation"
echo ""
echo "  4. Try the examples:"
echo "     python examples/basic_usage.py"
echo "     python examples/api_client.py"
echo ""
