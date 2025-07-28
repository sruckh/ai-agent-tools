#!/bin/bash
# RunPod-specific dependency installation script
# Minimal approach - RunPod serverless already has CUDA and basic tools

set -e

echo "🚀 Installing RunPod dependencies (minimal approach)..."

# Set up Backblaze B2 storage first
echo "🔗 Setting up persistent storage..."
source /app/scripts/setup-backblaze-storage.sh

# Use cache directories from Backblaze setup
PIP_CACHE="$PIP_CACHE_DIR"
MODELS_CACHE="$MODELS_CACHE_DIR"

echo "📁 Using cache directories:"
echo "  PIP Cache: $PIP_CACHE"
echo "  Models Cache: $MODELS_CACHE"

echo "📦 Installing minimal system dependencies..."

# Install only essential missing packages
apt-get update
apt-get install -y --no-install-recommends \
    libsndfile1 \
    ffmpeg
    
# Clean up apt cache immediately
rm -rf /var/lib/apt/lists/*

echo "🐍 Installing Python dependencies..."

# Install base requirements
pip install --upgrade pip --cache-dir "$PIP_CACHE"
pip install -r requirements.txt --cache-dir "$PIP_CACHE"

# Install RunPod SDK (should already be in requirements.txt but ensure it's there)
pip install runpod --cache-dir "$PIP_CACHE"

# Install PyTorch with CUDA support (use RunPod's recommended version)
echo "🔥 Installing PyTorch with CUDA support for RunPod"
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --cache-dir "$PIP_CACHE"

echo "✅ RunPod dependencies installed successfully"
echo "📋 Installed packages summary:"
pip list | grep -E "(torch|runpod|kokoro|chatterbox|faster|soundfile)"