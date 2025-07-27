#!/bin/bash
# RunPod-specific startup script
# Handles handler selection and RunPod serverless deployment

set -e

echo "🚀 Starting RunPod handler..."

# Environment variables
HANDLER_TYPE=${HANDLER_TYPE:-tts}
RUNTIME_INSTALL=${RUNTIME_INSTALL:-true}
RUNPOD_OPTIMIZED=${RUNPOD_OPTIMIZED:-true}
CACHE_DIR=${CACHE_DIR:-/tmp/runpod-cache}

# Create cache directory
mkdir -p "$CACHE_DIR"

# Check if dependencies are already installed (for persistent volumes)
DEPS_INSTALLED_FLAG="$CACHE_DIR/.deps_installed"

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

# Change to handlers directory
cd /app/runpod_handlers

echo "🎯 Starting handler: $HANDLER_TYPE"

# Start appropriate handler
case $HANDLER_TYPE in
    tts)
        echo "Starting TTS Handler..."
        exec python tts_handler.py
        ;;
    video)
        echo "Starting Video Handler..."
        exec python video_handler.py
        ;;
    storage)
        echo "Starting Storage Handler..."
        exec python storage_handler.py
        ;;
    audio)
        echo "Starting Audio Handler..."
        exec python audio_handler.py
        ;;
    *)
        echo "❌ Unknown handler type: $HANDLER_TYPE"
        echo "Available handlers: tts, video, storage, audio"
        exit 1
        ;;
esac