# Tech Stack and Dependencies

## Core Framework
- **Python**: Main programming language
- **FastAPI**: Web API framework with async support
- **Uvicorn**: ASGI server for FastAPI

## Key Dependencies
- **FFmpeg**: Video/audio processing (external binary)
- **loguru**: Structured logging
- **numpy**: Numerical computations
- **soundfile**: Audio file I/O
- **torch/torchaudio**: PyTorch for AI models

## AI/ML Libraries
- **Kokoro TTS**: Multi-language text-to-speech (82M model)
- **ChatterboxTTS**: Advanced TTS with voice cloning
- **Speech recognition**: For transcription services

## Video Processing
- **FFmpeg**: Core video processing engine
- **ffprobe**: Media file analysis
- Supports common formats: MP4, WAV, various codecs

## Infrastructure
- **Docker**: Containerized deployment
- **CUDA**: GPU acceleration support for AI models
- **Linux**: Primary deployment target

## External Services
- File upload/download capabilities
- Storage management system
- Authentication middleware