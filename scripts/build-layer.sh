#!/bin/bash

# Build Lambda layer for stitch embroidery conversion
# This script packages the required Python libraries for AWS Lambda

set -e

echo "Building Lambda layer for stitch..."

# Create layer directory structure
mkdir -p layer/python

# Install dependencies to layer directory
echo "Installing Python dependencies..."
pip install -r ../lambda/requirements.txt -t layer/python/

# Remove unnecessary files to reduce layer size
echo "Cleaning up layer..."
find layer/python -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find layer/python -name "*.pyc" -delete 2>/dev/null || true
find layer/python -name "*.pyo" -delete 2>/dev/null || true
find layer/python -name "*.pyd" -delete 2>/dev/null || true
find layer/python -name "*.so" -exec strip {} + 2>/dev/null || true

# Create layer zip file
echo "Creating layer zip file..."
cd layer
zip -r ../layer.zip .
cd ..

echo "Layer built successfully: layer.zip"
echo "Layer size: $(du -h layer.zip | cut -f1)"
