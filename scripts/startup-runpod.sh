#!/bin/bash
# RunPod-specific startup script
# Handles handler selection and RunPod serverless deployment

set -e

echo "🚀 Starting RunPod handler..."

# Environment variables
RUNTIME_INSTALL=${RUNTIME_INSTALL:-true}

# Validate required S3-compatible storage environment variables
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ] || [ -z "$AWS_S3_BUCKET" ] || [ -z "$AWS_ENDPOINT_URL" ] || [ -z "$AWS_DEFAULT_REGION" ]; then
    echo "❌ Missing required S3-compatible storage environment variables:"
    echo "   AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET, AWS_ENDPOINT_URL, AWS_DEFAULT_REGION"
    echo "   Please set these environment variables in your RunPod endpoint configuration."
    exit 1
fi

echo "🔗 Setting up S3-compatible persistent storage..."
source /app/scripts/setup-backblaze-storage.sh

# Check if dependencies are already installed using Backblaze flag
DEPS_INSTALLED_FLAG="$LOCAL_CACHE_DIR/.deps_installed"

if [ -f "$DEPS_INSTALLED_FLAG" ]; then
    echo "✅ Dependencies already installed, skipping installation"
else
    echo "📦 Installing RunPod dependencies..."
    
    # Install runtime dependencies
    if [ "$RUNTIME_INSTALL" = "true" ]; then
        /app/scripts/install-runpod-deps.sh
    fi
    
    # Mark dependencies as installed
    touch "$DEPS_INSTALLED_FLAG"
    echo "✅ All dependencies installed successfully"
fi

# Set up Python path to include both app and packages directories
PACKAGES_DIR="$LOCAL_CACHE_DIR/packages"
export PYTHONPATH=/app:$PACKAGES_DIR:$PYTHONPATH
echo "🐍 PYTHONPATH set to: $PYTHONPATH"

# Health check
echo "🏥 Running health check..."
python -c "
import sys
try:
    import runpod
    print('✅ RunPod SDK available')
except ImportError as e:
    print(f'❌ Missing RunPod SDK: {e}')
    sys.exit(1)
"

# Change to app directory
cd /app

echo "🎯 Starting unified RunPod handler..."

# Start unified handler that supports all operations
exec python runpod_handler.py