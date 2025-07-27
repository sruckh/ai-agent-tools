#!/bin/bash
# RunPod-specific startup script
# Handles handler selection and RunPod serverless deployment

set -e

echo "🚀 Starting RunPod handler..."

# Environment variables
RUNTIME_INSTALL=${RUNTIME_INSTALL:-true}

# Validate required Backblaze environment variables
if [ -z "$BACKBLAZE_KEY_ID" ] || [ -z "$BACKBLAZE_APPLICATION_KEY" ] || [ -z "$BACKBLAZE_BUCKET" ] || [ -z "$BACKBLAZE_ENDPOINT" ]; then
    echo "❌ Missing required Backblaze B2 environment variables:"
    echo "   BACKBLAZE_KEY_ID, BACKBLAZE_APPLICATION_KEY, BACKBLAZE_BUCKET, BACKBLAZE_ENDPOINT"
    echo "   Please set these environment variables in your RunPod endpoint configuration."
    exit 1
fi

echo "🔗 Setting up Backblaze B2 persistent storage..."
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

# Set up Python path
export PYTHONPATH=/app:$PYTHONPATH

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