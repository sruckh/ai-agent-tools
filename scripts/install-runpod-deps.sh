#!/bin/bash
# RunPod-specific dependency installation script
# Optimized for RunPod serverless environment

set -e

echo "🚀 Installing RunPod-specific dependencies..."

# Environment variables
CACHE_DIR=${CACHE_DIR:-/tmp/runpod-cache}
HANDLER_TYPE=${HANDLER_TYPE:-tts}

# Create cache directories
mkdir -p "$CACHE_DIR/pip" "$CACHE_DIR/models"

echo "📦 Installing system dependencies for handler: $HANDLER_TYPE"

# Handler-specific system dependencies
case $HANDLER_TYPE in
    tts|audio)
        echo "Installing audio processing dependencies..."
        apt-get update
        apt-get install -y \
            libsndfile1 \
            ffmpeg \
            libavcodec-dev \
            libavformat-dev \
            libavutil-dev \
            libswresample-dev \
            libswscale-dev
        ;;
    video)
        echo "Installing video processing dependencies..."
        apt-get update
        apt-get install -y \
            ffmpeg \
            libavcodec-dev \
            libavformat-dev \
            libavutil-dev \
            libswresample-dev \
            libswscale-dev \
            libx264-dev \
            libx265-dev
        ;;
    storage)
        echo "Installing storage dependencies..."
        apt-get update
        apt-get install -y \
            curl \
            wget
        ;;
    *)
        echo "Installing minimal dependencies..."
        apt-get update
        apt-get install -y \
            curl \
            wget
        ;;
esac

# Clean up apt cache
rm -rf /var/lib/apt/lists/*

echo "🐍 Installing Python dependencies..."

# Install base requirements first
pip install --upgrade pip --cache-dir "$CACHE_DIR/pip"
pip install --no-cache-dir -r requirements.txt --cache-dir "$CACHE_DIR/pip"

# Install RunPod-specific packages
pip install runpod --cache-dir "$CACHE_DIR/pip"

# Install CUDA toolkit first (RunPod serverless has GPUs)
echo "🔧 Installing CUDA toolkit 12.6..."
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1-1_all.deb
dpkg -i cuda-keyring_1.1-1_all.deb || true
apt-get update
apt-get -y install cuda-toolkit-12-6
apt-get install -y nvidia-open

# Set CUDA environment
export CUDA_HOME=/usr/local/cuda
export PATH=$CUDA_HOME/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH

# Install PyTorch with CUDA 12.6 support (RunPod has GPUs)
echo "🔥 Installing PyTorch 2.7.0 with CUDA 12.6 support"
pip install torch==2.7.0 torchvision==0.22.0 torchaudio==2.7.0 --index-url https://download.pytorch.org/whl/cu126 --cache-dir "$CACHE_DIR/pip"

# Install flash-attention based on Python version
PYTHON_VERSION=$(python -c "import sys; print(f'{sys.version_info.major}{sys.version_info.minor}')")
echo "🔍 Detected Python version: $PYTHON_VERSION"

if [ "$PYTHON_VERSION" = "310" ]; then
    echo "Installing flash-attention for Python 3.10"
    pip install https://github.com/Dao-AILab/flash-attention/releases/download/v2.8.0.post2/flash_attn-2.8.0.post2+cu12torch2.7cxx11abiFALSE-cp310-cp310-linux_x86_64.whl --cache-dir "$CACHE_DIR/pip"
elif [ "$PYTHON_VERSION" = "311" ]; then
    echo "Installing flash-attention for Python 3.11"
    pip install https://github.com/Dao-AILab/flash-attention/releases/download/v2.8.0.post2/flash_attn-2.8.0.post2+cu12torch2.7cxx11abiFALSE-cp311-cp311-linux_x86_64.whl --cache-dir "$CACHE_DIR/pip"
else
    echo "⚠️  Python version $PYTHON_VERSION not supported for flash-attention precompiled wheels"
    echo "   Trying to install from source..."
    pip install flash-attn --no-build-isolation --cache-dir "$CACHE_DIR/pip" || echo "Flash attention installation failed, continuing..."
fi

echo "📋 Pre-warming models for faster cold starts..."

# Pre-download models based on handler type
case $HANDLER_TYPE in
    tts)
        echo "Pre-warming TTS models..."
        python -c "
try:
    import torch
    from video.config import device
    print(f'Device configured: {device}')
    # Pre-load any TTS models here if needed
except Exception as e:
    print(f'Model pre-warming failed: {e}')
" || true
        ;;
    video)
        echo "Pre-warming video models..."
        python -c "
try:
    import torch
    from video.config import device
    print(f'Device configured: {device}')
    # Pre-load any video models here if needed
except Exception as e:
    print(f'Model pre-warming failed: {e}')
" || true
        ;;
esac

echo "✅ RunPod dependencies installed successfully"