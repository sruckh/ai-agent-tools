# Suggested Development Commands

## Running the Application

### Development Server
```bash
# Using FastAPI development server
fastapi dev server.py --host 0.0.0.0

# Or with Python
python server.py
```

### Docker Deployment
```bash
# Standard deployment
docker run --rm -p 8000:8000 -it gyoridavid/ai-agents-no-code-tools:latest

# With GPU support (requires CUDA Toolkit)
docker run --rm --gpus=all -e NVIDIA_VISIBLE_DEVICES=all -e NVIDIA_DRIVER_CAPABILITIES=all -p 8000:8000 -it gyoridavid/ai-agents-no-code-tools:latest-cuda
```

## Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## System Commands (Linux)
- **git**: Version control operations
- **ls**: List directory contents
- **cd**: Change directory
- **grep**: Text search
- **find**: File search
- **ps**: Process management
- **df**: Disk usage
- **htop**: Process monitoring

## API Testing
```bash
# Access API documentation
curl http://localhost:8000/docs

# Health check
curl http://localhost:8000/healthcheck

# Test endpoints via browser
open http://localhost:8000/docs
```

## Development Tools
- **FFmpeg**: Ensure installed for video processing
- **CUDA Toolkit**: For GPU acceleration (optional)
- **Docker**: For containerized development

## Notes
- No specific test, lint, or format commands found in project
- Project relies on FastAPI's built-in development features
- Monitor logs via loguru structured output