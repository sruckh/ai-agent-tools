#!/bin/bash
# Main startup script for slim containers
# Handles runtime dependency installation and application startup

set -e

echo "🚀 Starting AI Agents application..."

# Environment variables
RUNTIME_INSTALL=${RUNTIME_INSTALL:-true}
CUDA_RUNTIME_INSTALL=${CUDA_RUNTIME_INSTALL:-false}
SKIP_DEPS=${SKIP_DEPS:-false}
CACHE_DIR=${CACHE_DIR:-/tmp/ai-agents-cache}

# Create cache directory
mkdir -p "$CACHE_DIR"

# Check if dependencies are already installed (for persistent volumes)
DEPS_INSTALLED_FLAG="$CACHE_DIR/.deps_installed"

if [ "$SKIP_DEPS" = "true" ]; then
    echo "⏭️  Skipping dependency installation (SKIP_DEPS=true)"
elif [ -f "$DEPS_INSTALLED_FLAG" ]; then
    echo "✅ Dependencies already installed, skipping installation"
else
    echo "📦 Installing runtime dependencies..."
    
    # Install runtime dependencies
    if [ "$RUNTIME_INSTALL" = "true" ]; then
        /app/scripts/install-runtime-deps.sh
    fi
    
    # Install CUDA if requested
    if [ "$CUDA_RUNTIME_INSTALL" = "true" ]; then
        /app/scripts/install-cuda-runtime.sh
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
    import fastapi
    import loguru
    print('✅ Core dependencies available')
except ImportError as e:
    print(f'❌ Missing core dependency: {e}')
    sys.exit(1)
"

echo "🎯 Starting FastAPI server..."

# Start the application
exec fastapi run server.py --host 0.0.0.0 --port 8000