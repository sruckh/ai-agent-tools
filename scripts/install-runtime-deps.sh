#!/bin/bash
# Runtime dependency installation script
# Installs dependencies only when needed, with caching

set -e

echo "🚀 Installing runtime dependencies..."

# Environment variables
CACHE_DIR=${CACHE_DIR:-/tmp/ai-agents-cache}
SKIP_AUDIO=${SKIP_AUDIO:-false}
SKIP_VIDEO=${SKIP_VIDEO:-false}
MINIMAL_MODE=${MINIMAL_MODE:-false}

# Create cache directories
mkdir -p "$CACHE_DIR/apt" "$CACHE_DIR/pip" "$CACHE_DIR/models"

# Function to check if package is already installed
package_installed() {
    dpkg -l | grep -q "^ii  $1 " 2>/dev/null
}

# Function to check if pip package is installed
pip_package_installed() {
    python -c "import $1" 2>/dev/null
}

echo "📦 Installing system dependencies..."

# Essential system packages (only if not installed)
apt-get update

PACKAGES_TO_INSTALL=""

# Audio/Video packages (conditional)
if [ "$SKIP_AUDIO" != "true" ]; then
    if ! package_installed "libsndfile1"; then
        PACKAGES_TO_INSTALL="$PACKAGES_TO_INSTALL libsndfile1"
    fi
    if ! package_installed "ffmpeg"; then
        PACKAGES_TO_INSTALL="$PACKAGES_TO_INSTALL ffmpeg"
    fi
fi

if [ "$SKIP_VIDEO" != "true" ]; then
    if ! package_installed "libavcodec-dev"; then
        PACKAGES_TO_INSTALL="$PACKAGES_TO_INSTALL libavcodec-dev libavformat-dev libavutil-dev libswresample-dev libswscale-dev"
    fi
fi

# Development tools (only if not in minimal mode)
if [ "$MINIMAL_MODE" != "true" ]; then
    if ! package_installed "build-essential"; then
        PACKAGES_TO_INSTALL="$PACKAGES_TO_INSTALL build-essential g++"
    fi
fi

# Font packages (optional)
if ! package_installed "fonts-dejavu"; then
    PACKAGES_TO_INSTALL="$PACKAGES_TO_INSTALL fonts-dejavu fonts-ebgaramond"
fi

# Install packages if any are needed
if [ -n "$PACKAGES_TO_INSTALL" ]; then
    echo "Installing: $PACKAGES_TO_INSTALL"
    apt-get install -y $PACKAGES_TO_INSTALL
else
    echo "All system packages already installed"
fi

# Clean up apt cache
rm -rf /var/lib/apt/lists/*

echo "🐍 Installing Python dependencies..."

# Upgrade pip if needed
pip install --upgrade pip --cache-dir "$CACHE_DIR/pip"

# Install requirements with caching
pip install --no-cache-dir -r requirements.txt --cache-dir "$CACHE_DIR/pip"

echo "✅ Runtime dependencies installed successfully"