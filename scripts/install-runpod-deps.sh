#!/bin/bash
# RunPod-specific dependency installation script
# Optimized for RunPod serverless environment

set -e

echo "🚀 Installing RunPod-specific dependencies..."

# Environment variables
HANDLER_TYPE=${HANDLER_TYPE:-tts}

# Set up Backblaze B2 storage first
echo "🔗 Setting up persistent storage..."
source /app/scripts/setup-backblaze-storage.sh

# Use cache directories from Backblaze setup
PIP_CACHE="$PIP_CACHE_DIR"
MODELS_CACHE="$MODELS_CACHE_DIR"

echo "📁 Using cache directories:"
echo "  PIP Cache: $PIP_CACHE"
echo "  Models Cache: $MODELS_CACHE"

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
pip install --upgrade pip --cache-dir "$PIP_CACHE"
pip install -r requirements.txt --cache-dir "$PIP_CACHE"

# Install RunPod-specific packages
pip install runpod --cache-dir "$PIP_CACHE"

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
pip install torch==2.7.0 torchvision==0.22.0 torchaudio==2.7.0 --index-url https://download.pytorch.org/whl/cu126 --cache-dir "$PIP_CACHE"

# Install flash-attention based on Python version
PYTHON_VERSION=$(python -c "import sys; print(f'{sys.version_info.major}{sys.version_info.minor}')")
echo "🔍 Detected Python version: $PYTHON_VERSION"

if [ "$PYTHON_VERSION" = "310" ]; then
    echo "Installing flash-attention for Python 3.10"
    pip install https://github.com/Dao-AILab/flash-attention/releases/download/v2.8.0.post2/flash_attn-2.8.0.post2+cu12torch2.7cxx11abiFALSE-cp310-cp310-linux_x86_64.whl --cache-dir "$PIP_CACHE"
elif [ "$PYTHON_VERSION" = "311" ]; then
    echo "Installing flash-attention for Python 3.11"
    pip install https://github.com/Dao-AILab/flash-attention/releases/download/v2.8.0.post2/flash_attn-2.8.0.post2+cu12torch2.7cxx11abiFALSE-cp311-cp311-linux_x86_64.whl --cache-dir "$PIP_CACHE"
else
    echo "⚠️  Python version $PYTHON_VERSION not supported for flash-attention precompiled wheels"
    echo "   Trying to install from source..."
    pip install flash-attn --no-build-isolation --cache-dir "$PIP_CACHE" || echo "Flash attention installation failed, continuing..."
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