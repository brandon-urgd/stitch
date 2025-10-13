#!/bin/bash
# ULTIMATE BADASS LAMBDA LAYER BUILD SCRIPT
# Building the most powerful Lambda layer ever created

set -e

echo "🚀 BUILDING THE ULTIMATE BADASS LAMBDA LAYER..."
echo "⚡ This is going to be EPIC!"

# Create build directory
BUILD_DIR="/tmp/ultimate-layer-build"
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

echo "📦 Installing system dependencies (the nuclear option)..."

# Install EVERY system dependency known to man
sudo apt-get update
sudo apt-get install -y \
  # Image processing powerhouses
  libjpeg-dev libpng-dev libtiff-dev libwebp-dev \
  libopenjp2-7-dev libopenjp2-7 \
  libjpeg-turbo8-dev \
  # Computer vision beast mode
  libopencv-dev libopencv-contrib-dev \
  libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev \
  # Scientific computing arsenal
  libopenblas-dev liblapack-dev libatlas-base-dev \
  libgfortran5 gfortran \
  # Machine learning infrastructure
  libhdf5-dev libhdf5-serial-dev \
  libprotobuf-dev protobuf-compiler \
  # Graphics and rendering
  libcairo2-dev libpango1.0-dev libgdk-pixbuf2.0-dev \
  libglib2.0-dev libgobject-2.0-dev \
  # System libraries
  libffi-dev libssl-dev libbz2-dev liblzma-dev \
  libreadline-dev libsqlite3-dev libncurses5-dev \
  # Build tools
  build-essential cmake pkg-config \
  # Everything else we might need
  libxml2-dev libxslt1-dev \
  libfreetype6-dev libfontconfig1-dev \
  libx11-dev libxext-dev libxrender-dev

echo "🔥 System dependencies installed! Now for the Python power..."

# Copy requirements file
cp /Users/brandon/Documents/Projects/urgd/stitch/layers/ultimate-dependencies/requirements.txt .

echo "⚡ Installing Python dependencies (this will take a while)..."

# Install Python dependencies with maximum power
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt -t ./python/ --no-cache-dir

echo "💥 Creating the ultimate layer package..."

# Create the layer zip
zip -r ultimate-dependencies.zip python/

# Get the size
LAYER_SIZE=$(du -h ultimate-dependencies.zip | cut -f1)
echo "🎯 ULTIMATE LAYER BUILT! Size: $LAYER_SIZE"

# Copy to stitch directory
cp ultimate-dependencies.zip /Users/brandon/Documents/Projects/urgd/stitch/layers/

echo "🚀 ULTIMATE LAYER READY FOR DEPLOYMENT!"
echo "💪 This layer contains the most powerful image processing tools ever assembled!"
echo "🔥 Ready to process images like a BOSS!"
