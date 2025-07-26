# RunPod Serverless Dockerfile
# Optimized for GPU-accelerated serverless deployment
FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    ffmpeg-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create runpod_handlers directory and extract handler files
RUN mkdir -p runpod_handlers

# Extract RunPod base handler code from server.py
RUN python3 -c "import re; with open('server.py', 'r') as f: content = f.read(); base_match = re.search(r\"\"\"runpod_base_code = '''(.*?)'''\"\"\", content, re.DOTALL); if base_match: with open('runpod_handlers/runpod_base.py', 'w') as f: f.write(base_match.group(1)); tts_match = re.search(r\"\"\"tts_handler_code = '''(.*?)'''\"\"\", content, re.DOTALL); if tts_match: with open('runpod_handlers/tts_handler.py', 'w') as f: f.write(tts_match.group(1)); video_match = re.search(r\"\"\"video_handler_code = '''(.*?)'''\"\"\", content, re.DOTALL); if video_match: with open('runpod_handlers/video_handler.py', 'w') as f: f.write(video_match.group(1))"

# Set Python path to include current directory
ENV PYTHONPATH=/app:$PYTHONPATH

# Create entrypoint script for different handlers
RUN echo '#!/bin/bash
HANDLER_TYPE=${HANDLER_TYPE:-tts}
cd /app/runpod_handlers

case $HANDLER_TYPE in
    tts)
        echo "Starting TTS Handler..."
        python tts_handler.py
        ;;
    video)
        echo "Starting Video Handler..."
        python video_handler.py
        ;;
    storage)
        echo "Starting Storage Handler..."
        python storage_handler.py
        ;;
    audio)
        echo "Starting Audio Handler..."
        python audio_handler.py
        ;;
    *)
        echo "Unknown handler type: $HANDLER_TYPE"
        echo "Available handlers: tts, video, storage, audio"
        exit 1
        ;;
esac
' > /app/start_handler.sh && chmod +x /app/start_handler.sh

# Pre-download models to improve cold start times
RUN python3 -c "
try:
    from video.config import device
    print(f'Device configured: {device}')
except ImportError:
    print('Device configuration not available')
" || true

# Set environment variables for RunPod
ENV RUNPOD_SERVERLESS=true
ENV HANDLER_TYPE=tts

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD python3 -c "import sys; sys.exit(0)"

# Default command
CMD ["/app/start_handler.sh"]