#!/bin/bash
# Build script for ultra-slim RunPod serverless container

set -e

echo "🏗️  Building ultra-slim RunPod serverless container..."

# Build the container
docker build -f runpod.Dockerfile.slim -t ai-agents-runpod-slim:latest .

echo "📊 Container size comparison:"
echo "Original runpod.Dockerfile:"
docker images | grep ai-agents | grep -v slim || echo "Original image not found"

echo "New slim container:"
docker images | grep ai-agents-runpod-slim

echo ""
echo "✅ Build complete!"
echo ""
echo "🚀 Usage for RunPod deployment:"
echo "1. Push to your container registry:"
echo "   docker tag ai-agents-runpod-slim:latest your-registry/ai-agents-runpod-slim:latest"
echo "   docker push your-registry/ai-agents-runpod-slim:latest"
echo ""
echo "2. In RunPod serverless settings:"
echo "   - Container Image: your-registry/ai-agents-runpod-slim:latest"
echo "   - Handler Type: Set HANDLER_TYPE env var (tts, video, storage, audio)"
echo "   - GPU: The container will auto-detect and install CUDA at runtime"
echo ""
echo "🎯 Key benefits:"
echo "   - Ultra-small base image (~200MB vs ~8GB)"
echo "   - Runtime dependency installation"
echo "   - Automatic GPU detection and CUDA setup"
echo "   - Faster container startup and deployment"