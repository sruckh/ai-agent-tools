# Code Structure and Architecture

## Main Application
- **server.py**: FastAPI application entry point (58 lines)
  - App configuration with lifespan management
  - Router mounting and middleware setup
  - Health check endpoint

## API Layer (`api_server/`)
- **auth_middleware.py**: Authentication middleware
- **v1_media_router.py**: Main media processing endpoints
- **v1_utils_router.py**: Utility endpoints

## Core Modules

### Video Processing (`video/`)
- **media.py**: MediaUtils class - core video operations (850+ lines)
  - Video merging, frame extraction
  - FFmpeg command execution with progress tracking
  - Video/audio information retrieval
- **caption.py**: Video captioning and subtitle generation
- **config.py**: Device configuration (CPU/GPU)
- **storage.py**: File storage management

### AI/TTS (`video/`)
- **tts.py**: Text-to-speech implementations
  - Kokoro TTS (English and international)
  - ChatterboxTTS with voice cloning
- **tts_chatterbox.py**: ChatterboxTTS specific implementation
- **stt.py**: Speech-to-text transcription

### Utilities (`utils/`)
- **image.py**: Image processing utilities
- **proxy.py**: Proxy and network utilities

## Directory Structure
```
project/
├── server.py           # FastAPI main app
├── api_server/         # API routes and middleware
├── video/              # Video/audio processing core
├── utils/              # General utilities
├── assets/             # Static assets
├── PLAYBOOKS/          # Operational documentation
└── [documentation files]
```

## Key Design Patterns
- **Class-based services**: MediaUtils, TTS managers
- **Router-based API**: Modular endpoint organization
- **Async/await**: FastAPI async patterns
- **Context logging**: Structured logging with loguru
- **Progress tracking**: Real-time operation feedback