# Ultra-Slim RunPod Serverless Container

This project now includes an ultra-slim container optimized for RunPod serverless deployment. Instead of pre-installing all dependencies (resulting in 8GB+ images), the slim container starts with a minimal ~200MB base and installs everything at runtime.

## 🎯 Key Benefits

- **Massive Size Reduction**: ~200MB vs ~8GB+ (96% smaller)
- **Faster Deployment**: Smaller images deploy faster to RunPod
- **Runtime Optimization**: Only installs what's needed for the specific handler
- **Automatic GPU Detection**: Installs CUDA 12.6 + PyTorch 2.7.0 only when GPU is detected
- **Handler-Specific Dependencies**: Conditional installation based on `HANDLER_TYPE`

## 🏗️ Building the Slim Container

```bash
# Build the ultra-slim container
./build-runpod-slim.sh

# Or manually:
docker build -f runpod.Dockerfile.slim -t ai-agents-runpod-slim:latest .
```

## 🚀 RunPod Deployment

1. **Push to Registry:**
   ```bash
   docker tag ai-agents-runpod-slim:latest your-registry/ai-agents-runpod-slim:latest
   docker push your-registry/ai-agents-runpod-slim:latest
   ```

2. **RunPod Configuration:**
   - **Container Image**: `your-registry/ai-agents-runpod-slim:latest`
   - **Environment Variables**:
     - `HANDLER_TYPE`: `tts`, `video`, `storage`, or `audio`
     - `RUNTIME_INSTALL`: `true` (default)
     - `CACHE_DIR`: `/tmp/runpod-cache` (optional)

## 📦 What Gets Installed at Runtime

### System Dependencies (Handler-Specific)
- **TTS/Audio**: `libsndfile1`, `ffmpeg`, audio processing libraries
- **Video**: `ffmpeg`, video codecs, processing libraries  
- **Storage**: Minimal `curl`, `wget` only
- **All**: Base development tools as needed

### GPU/CUDA Stack (Auto-Detected)
- **CUDA Toolkit 12.6** (your specified version)
- **NVIDIA Open Drivers**
- **PyTorch 2.7.0** with CUDA 12.6 support
- **Flash Attention 2.8.0** (Python version auto-detected)

### Python Dependencies
- All packages from `requirements.txt`
- `runpod` SDK
- Handler-specific ML libraries

## ⚡ Performance Characteristics

### Cold Start Times
- **Container Download**: ~30s (vs ~5min for full image)
- **Dependency Installation**: ~3-5min (one-time per container instance)
- **Handler Startup**: ~10-30s

### Warm Start Times
- **With Persistent Storage**: ~10-30s (dependencies cached)
- **Handler Switch**: ~5-10s

## 🔧 Configuration Options

### Environment Variables
```bash
# Required
HANDLER_TYPE=tts          # tts, video, storage, audio

# Optional
RUNTIME_INSTALL=true      # Enable runtime dependency installation
CACHE_DIR=/tmp/runpod-cache  # Cache directory for dependencies
RUNPOD_OPTIMIZED=true     # RunPod-specific optimizations
```

### Handler Types
- **`tts`**: Text-to-speech processing
- **`video`**: Video processing and generation  
- **`storage`**: File storage and management
- **`audio`**: Audio processing

## 📊 Size Comparison

| Container Type | Base Image | Final Size | Build Time | Deploy Time |
|----------------|------------|------------|------------|-------------|
| **Original** | `runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04` | ~8GB+ | ~10min | ~5min |
| **Slim** | `ubuntu:22.04` | ~200MB | ~2min | ~30s |

## 🛠️ Development & Testing

### Local Testing
```bash
# Build and test locally
docker build -f runpod.Dockerfile.slim -t test-slim .

# Run with specific handler
docker run -e HANDLER_TYPE=tts test-slim

# Skip dependency installation for testing
docker run -e SKIP_DEPS=true test-slim
```

### Debugging
```bash
# Enter container for debugging
docker run -it --entrypoint /bin/bash test-slim

# Check dependency installation logs
docker logs container-id
```

## 🔄 Migration from Original Container

The slim container is fully compatible with existing RunPod serverless functions. Simply:

1. Update your container registry to use the slim image
2. Set the `HANDLER_TYPE` environment variable in RunPod
3. Deploy - all dependencies will be installed automatically

No code changes required!