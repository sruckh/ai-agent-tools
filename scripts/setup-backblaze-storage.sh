#!/bin/bash
# Backblaze B2 S3-compatible storage setup for RunPod serverless
# This script sets up persistent storage using Backblaze B2 as S3-compatible storage

set -e

echo "🔗 Setting up Backblaze B2 storage for persistent data..."

# Required environment variables for S3-compatible storage (Backblaze B2)
: ${AWS_ACCESS_KEY_ID:?'AWS_ACCESS_KEY_ID environment variable is required'}
: ${AWS_SECRET_ACCESS_KEY:?'AWS_SECRET_ACCESS_KEY environment variable is required'}
: ${AWS_S3_BUCKET:?'AWS_S3_BUCKET environment variable is required'}
: ${AWS_ENDPOINT_URL:?'AWS_ENDPOINT_URL environment variable is required (e.g., https://s3.us-west-004.backblazeb2.com)'}
: ${AWS_DEFAULT_REGION:?'AWS_DEFAULT_REGION environment variable is required (e.g., us-west-004)'}

# Local cache directories
LOCAL_CACHE_DIR=${LOCAL_CACHE_DIR:-/tmp/runpod-cache}
MODELS_CACHE_DIR="$LOCAL_CACHE_DIR/models"
PIP_CACHE_DIR="$LOCAL_CACHE_DIR/pip"
DEPS_CACHE_DIR="$LOCAL_CACHE_DIR/deps"

# S3 paths (Backblaze bucket structure)
S3_CACHE_PREFIX="runpod-cache"
S3_MODELS_PATH="$S3_CACHE_PREFIX/models"
S3_PIP_PATH="$S3_CACHE_PREFIX/pip"
S3_DEPS_PATH="$S3_CACHE_PREFIX/deps"

# Create local cache directories
mkdir -p "$MODELS_CACHE_DIR" "$PIP_CACHE_DIR" "$DEPS_CACHE_DIR"

# AWS CLI is already configured via environment variables
# AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION, AWS_ENDPOINT_URL

echo "📋 Checking AWS CLI configuration..."
# Install AWS CLI if not present
if ! command -v aws &> /dev/null; then
    echo "Installing AWS CLI..."
    # Install unzip first (needed for AWS CLI installation)
    apt-get update && apt-get install -y --no-install-recommends unzip
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip -q awscliv2.zip
    ./aws/install
    rm -rf aws awscliv2.zip
    # Clean up
    rm -rf /var/lib/apt/lists/*
fi

# Test connection to S3-compatible storage
echo "🔍 Testing S3 connection..."
if aws s3 ls "s3://$AWS_S3_BUCKET" > /dev/null 2>&1; then
    echo "✅ Successfully connected to S3 bucket: $AWS_S3_BUCKET"
else
    echo "❌ Failed to connect to S3 storage. Please check your credentials and bucket name."
    exit 1
fi

# Function to sync from S3 to local cache
sync_from_s3() {
    local s3_path="$1"
    local local_path="$2"
    local description="$3"
    
    echo "📥 Syncing $description from S3..."
    if aws s3 sync "s3://$AWS_S3_BUCKET/$s3_path" "$local_path" \
        --only-show-errors; then
        echo "✅ $description synced successfully"
    else
        echo "⚠️  $description sync failed or no data found (this is normal for first run)"
    fi
}

# Function to sync from local cache to S3
sync_to_s3() {
    local local_path="$1"
    local s3_path="$2"
    local description="$3"
    
    echo "📤 Backing up $description to S3..."
    if [ -d "$local_path" ] && [ "$(ls -A "$local_path")" ]; then
        aws s3 sync "$local_path" "s3://$AWS_S3_BUCKET/$s3_path" \
            --only-show-errors
        echo "✅ $description backed up successfully"
    else
        echo "ℹ️  No $description data to backup"
    fi
}

# Check if environment is already set up
SETUP_FLAG="$LOCAL_CACHE_DIR/.backblaze_setup_complete"
if [ -f "$SETUP_FLAG" ]; then
    echo "🔄 Environment previously set up, syncing cached data..."
    sync_from_s3 "$S3_MODELS_PATH" "$MODELS_CACHE_DIR" "models"
    sync_from_s3 "$S3_PIP_PATH" "$PIP_CACHE_DIR" "pip packages"
    sync_from_s3 "$S3_DEPS_PATH" "$DEPS_CACHE_DIR" "dependencies"
else
    echo "🆕 First-time setup, downloading any existing cached data..."
    sync_from_s3 "$S3_MODELS_PATH" "$MODELS_CACHE_DIR" "models"
    sync_from_s3 "$S3_PIP_PATH" "$PIP_CACHE_DIR" "pip packages"
    sync_from_s3 "$S3_DEPS_PATH" "$DEPS_CACHE_DIR" "dependencies"
    
    # Mark setup as complete
    touch "$SETUP_FLAG"
fi

# Export cache directories for use by other scripts
export MODELS_CACHE_DIR
export PIP_CACHE_DIR  
export DEPS_CACHE_DIR
export LOCAL_CACHE_DIR

# Create cleanup function for exit
cleanup_and_backup() {
    echo "🔄 Backing up cache data to Backblaze B2..."
    sync_to_s3 "$MODELS_CACHE_DIR" "$S3_MODELS_PATH" "models"
    sync_to_s3 "$PIP_CACHE_DIR" "$S3_PIP_PATH" "pip packages"
    sync_to_s3 "$DEPS_CACHE_DIR" "$S3_DEPS_PATH" "dependencies"
    echo "✅ Backup completed"
}

# Set up trap to backup data on exit
trap cleanup_and_backup EXIT

echo "✅ S3-compatible storage setup complete"
echo "📁 Local cache directory: $LOCAL_CACHE_DIR"
echo "🪣 S3 bucket: $AWS_S3_BUCKET"
echo "🔗 Endpoint: $AWS_ENDPOINT_URL"