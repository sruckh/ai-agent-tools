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
PACKAGES_DIR="$PACKAGES_CACHE_DIR"

echo "📁 Using cache directories:"
echo "  PIP Cache: $PIP_CACHE"
echo "  Models Cache: $MODELS_CACHE"
echo "  Packages Install: $PACKAGES_DIR"

# Set PYTHONPATH to include our custom package installation directory
export PYTHONPATH="$PACKAGES_DIR:$PYTHONPATH"
echo "🐍 PYTHONPATH updated to include: $PACKAGES_DIR"

# Verify ALL pip environment variables are properly set (done in setup-backblaze-storage.sh)
echo "📁 ALL pip environment variables (set by setup script):"
echo "  TMPDIR: $TMPDIR"
echo "  TEMP: $TEMP"
echo "  TMP: $TMP"
echo "  PIP_BUILD_DIR: $PIP_BUILD_DIR"
echo "  PIP_DOWNLOAD_CACHE: $PIP_DOWNLOAD_CACHE"
echo "  PIP_CACHE_DIR: $PIP_CACHE_DIR"
echo "  PYTHON_EGG_CACHE: $PYTHON_EGG_CACHE"

# Ensure ALL pip environment directories exist (they should already be created by setup script)
for dir_var in TMPDIR TEMP TMP PIP_BUILD_DIR PIP_DOWNLOAD_CACHE PIP_CACHE_DIR PYTHON_EGG_CACHE; do
    dir_path=$(eval echo \$$dir_var)
    if [ ! -d "$dir_path" ]; then
        echo "⚠️  Creating missing $dir_var: $dir_path"
        mkdir -p "$dir_path"
    fi
done

echo "📦 Installing minimal system dependencies..."

# Install only essential missing packages
apt-get update
apt-get install -y --no-install-recommends \
    libsndfile1 \
    ffmpeg
    
# Clean up apt cache immediately
rm -rf /var/lib/apt/lists/*

echo "🐍 Installing Python dependencies..."

# Function to retry pip install with exponential backoff
retry_pip_install() {
    local cmd="$1"
    local max_attempts=3
    local attempt=1
    local delay=1
    
    while [ $attempt -le $max_attempts ]; do
        echo "🔄 Attempt $attempt/$max_attempts: $cmd"
        if eval "$cmd"; then
            echo "✅ Installation successful on attempt $attempt"
            return 0
        else
            echo "❌ Attempt $attempt failed"
            if [ $attempt -lt $max_attempts ]; then
                echo "⏳ Waiting ${delay}s before retry..."
                sleep $delay
                delay=$((delay * 2))  # Exponential backoff
            fi
        fi
        attempt=$((attempt + 1))
    done
    
    echo "❌ All attempts failed for: $cmd"
    return 1
}

# Install base requirements to S3-mounted directory
# Upgrade pip first (without --target to ensure system pip is upgraded)
echo "📦 Upgrading pip..."
retry_pip_install "pip install --upgrade pip --timeout 120"

echo "📦 Installing requirements.txt..."
retry_pip_install "pip install -r requirements.txt --target '$PACKAGES_DIR' --timeout 300"

# Install RunPod SDK (should already be in requirements.txt but ensure it's there)
echo "📦 Installing RunPod SDK..."
retry_pip_install "pip install runpod --target '$PACKAGES_DIR' --timeout 120"

# Install PyTorch with CUDA support (use RunPod's recommended version)
echo "🔥 Installing PyTorch with CUDA support for RunPod"

# Install PyTorch with retry logic (large download, needs extra time)
echo "⚠️  PyTorch is a large download (~2GB), this may take several minutes..."
retry_pip_install "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --target '$PACKAGES_DIR' --timeout 600 --retries 10"

# Install flash-attention with correct Python 3.10 wheel (after other deps to override any conflicts)
echo "⚡ Installing flash-attention for Python 3.10..."
retry_pip_install "pip install https://github.com/Dao-AILab/flash-attention/releases/download/v2.8.0.post2/flash_attn-2.8.0.post2+cu12torch2.6cxx11abiFALSE-cp310-cp310-linux_x86_64.whl --target '$PACKAGES_DIR' --timeout 300"

echo "✅ RunPod dependencies installed successfully"

# Verify packages are installed in the correct location
echo "📍 Verifying package installation location..."
if [ -d "$PACKAGES_DIR" ] && [ "$(ls -A "$PACKAGES_DIR")" ]; then
    echo "✅ Packages found in S3-mounted directory: $PACKAGES_DIR"
    echo "📊 Disk usage of packages directory:"
    du -sh "$PACKAGES_DIR" 2>/dev/null || echo "Unable to calculate size"
    echo "📁 Sample packages installed:"
    ls -la "$PACKAGES_DIR" | head -10
else
    echo "❌ No packages found in target directory: $PACKAGES_DIR"
    echo "🔍 Checking system Python site-packages (should be minimal)..."
    python -c "import site; print('System site-packages:', site.getsitepackages())"
fi

echo "📋 Installed packages summary:"
pip list | grep -E "(torch|runpod|kokoro|chatterbox|faster|soundfile)"

echo "🔍 Python path verification:"
python -c "import sys; print('PYTHONPATH entries:'); [print(f'  {p}') for p in sys.path]"

echo "🧪 Testing critical package imports..."
python -c "
import sys
import os

# Test critical imports
test_packages = ['runpod', 'torch', 'numpy', 'flash_attn']
failed_imports = []

for package in test_packages:
    try:
        __import__(package)
        print(f'✅ {package} - OK')
    except ImportError as e:
        print(f'❌ {package} - FAILED: {e}')
        failed_imports.append(package)

if failed_imports:
    print(f'⚠️  Warning: {len(failed_imports)} packages failed to import: {failed_imports}')
    print('This may indicate installation issues or missing dependencies.')
    sys.exit(1)
else:
    print('✅ All critical packages imported successfully')
"