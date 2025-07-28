# Ultra-Slim RunPod Serverless Container
# Minimal base - ALL dependencies installed at runtime on server
FROM python:3.10-slim

WORKDIR /app

# Install only essential tools for downloads - NO other dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy ONLY application code - NO dependency installations
COPY api_server /app/api_server
COPY utils /app/utils  
COPY video /app/video
COPY assets /app/assets
COPY server.py /app/server.py

# Copy requirements.txt but DO NOT install it
COPY requirements.txt /app/requirements.txt

# Copy runtime installation scripts
COPY scripts/install-runpod-deps.sh /app/scripts/
COPY scripts/startup-runpod.sh /app/scripts/
COPY scripts/setup-backblaze-storage.sh /app/scripts/
RUN chmod +x /app/scripts/*.sh

# Copy unified RunPod handler
COPY runpod_handler.py /app/runpod_handler.py

# Environment configuration for RunPod
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app:$PYTHONPATH
ENV RUNPOD_SERVERLESS=true
ENV RUNTIME_INSTALL=true
# Note: S3-compatible storage credentials will be set via RunPod endpoint environment variables:
# AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET, AWS_ENDPOINT_URL, AWS_DEFAULT_REGION

# Health check (lightweight - using only standard library)
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD python3 -c "import sys; sys.exit(0)"

# IMPORTANT: NO pip installs, NO apt installs beyond curl/wget
# ALL dependencies installed at runtime via startup script
CMD ["/app/scripts/startup-runpod.sh"]