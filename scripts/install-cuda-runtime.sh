#!/bin/bash
# CUDA runtime installation script
# Only installs CUDA if GPU is detected

set -e

echo "🔍 Checking for GPU availability..."

# Check if NVIDIA GPU is available
if command -v nvidia-smi >/dev/null 2>&1; then
    echo "✅ NVIDIA GPU detected"
    GPU_AVAILABLE=true
else
    echo "⚠️  No NVIDIA GPU detected, skipping CUDA installation"
    GPU_AVAILABLE=false
fi

# Environment variables
CACHE_DIR=${CACHE_DIR:-/tmp/ai-agents-cache}

if [ "$GPU_AVAILABLE" = "true" ] && [ "$CUDA_RUNTIME_INSTALL" = "true" ]; then
    echo "🚀 Installing CUDA runtime..."
    
    # Create CUDA cache directory
    mkdir -p "$CACHE_DIR/cuda"
    
    # Download and install CUDA keyring for Ubuntu 24.04
    cd "$CACHE_DIR/cuda"
    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1-1_all.deb
    dpkg -i cuda-keyring_1.1-1_all.deb
    apt-get update
    
    # Install CUDA toolkit 12.6
    apt-get -y install cuda-toolkit-12-6
    
    # Install NVIDIA open source drivers
    apt-get install -y nvidia-open
    
    # Set CUDA environment variables
    export CUDA_HOME=/usr/local/cuda
    export PATH=$CUDA_HOME/bin:$PATH
    export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH
    
    # Save environment variables
    echo "export CUDA_HOME=/usr/local/cuda" >> /etc/environment
    echo "export PATH=\$CUDA_HOME/bin:\$PATH" >> /etc/environment
    echo "export LD_LIBRARY_PATH=\$CUDA_HOME/lib64:\$LD_LIBRARY_PATH" >> /etc/environment
    
    echo "✅ CUDA runtime installed successfully"
    
    # Verify CUDA installation
    if command -v nvcc >/dev/null 2>&1; then
        echo "🔧 CUDA compiler version: $(nvcc --version | grep release)"
    fi
    
else
    echo "⏭️  Skipping CUDA installation (GPU_AVAILABLE=$GPU_AVAILABLE, CUDA_RUNTIME_INSTALL=$CUDA_RUNTIME_INSTALL)"
fi

# Install PyTorch with appropriate CUDA support
echo "🔥 Installing PyTorch..."
if [ "$GPU_AVAILABLE" = "true" ]; then
    echo "Installing PyTorch 2.7.0 with CUDA 12.6 support"
    pip install torch==2.7.0 torchvision==0.22.0 torchaudio==2.7.0 --index-url https://download.pytorch.org/whl/cu126 --cache-dir "$CACHE_DIR/pip"
    
    # Detect Python version and install appropriate flash-attention
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
        echo "   Skipping flash-attention installation"
    fi
    
else
    echo "Installing PyTorch CPU-only"
    pip install torch==2.7.0 torchvision==0.22.0 torchaudio==2.7.0 --index-url https://download.pytorch.org/whl/cpu --cache-dir "$CACHE_DIR/pip"
fi

echo "✅ PyTorch installation completed"