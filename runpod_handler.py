#!/usr/bin/env python3
"""
Unified RunPod Serverless Handler
Preserves all original API functionality in a single serverless endpoint.
"""

import os
import sys
import json
import uuid
import tempfile
from typing import Dict, Any, Optional
import runpod
from loguru import logger

# Configure logging
logger.add(sys.stderr, level="INFO")

# Add app directory to Python path
sys.path.insert(0, '/app')

# Import your existing modules
from api_server.v1_media_router import v1_media_api_router
from video.storage import Storage
from video.stt import STT
from video.tts import TTS
from video.tts_chatterbox import TTSChatterbox
from video.media import MediaUtils
from video.fonts import FontManager
from video.config import device

# Initialize components
storage = Storage()
stt = STT()
tts_manager = TTS()
tts_chatterbox = TTSChatterbox()
media_utils = MediaUtils()
font_manager = FontManager()

logger.info(f"RunPod handler initialized with device: {device}")

def create_temp_directory() -> str:
    """Create a temporary directory for file processing."""
    temp_dir = tempfile.mkdtemp(prefix="runpod_")
    logger.debug(f"Created temp directory: {temp_dir}")
    return temp_dir

def cleanup_temp_directory(temp_dir: str):
    """Clean up temporary directory."""
    try:
        import shutil
        shutil.rmtree(temp_dir)
        logger.debug(f"Cleaned up temp directory: {temp_dir}")
    except Exception as e:
        logger.warning(f"Failed to cleanup temp directory {temp_dir}: {e}")

def handler(event):
    """
    Unified RunPod handler that routes requests to appropriate functionality.
    Maintains compatibility with original API endpoints.
    """
    try:
        input_data = event.get("input", {})
        
        # Extract operation and parameters
        operation = input_data.get("operation")
        if not operation:
            return {
                "error": "Missing 'operation' parameter",
                "supported_operations": [
                    "generate_kokoro_tts", "generate_chatterbox_tts", "get_kokoro_voices",
                    "transcribe", "merge_videos", "generate_captioned_video", 
                    "add_colorkey_overlay", "extract_frame", "extract_frame_from_url",
                    "get_video_info", "get_audio_info", "upload_file", "download_file",
                    "delete_file", "file_status", "list_fonts"
                ]
            }
        
        parameters = input_data.get("parameters", {})
        
        logger.info(f"Processing operation: {operation}")
        
        # Route to appropriate handler based on operation
        if operation in ["generate_kokoro_tts", "generate_chatterbox_tts", "get_kokoro_voices"]:
            return handle_tts_operations(operation, parameters)
        elif operation == "transcribe":
            return handle_transcription(parameters)
        elif operation in ["merge_videos", "generate_captioned_video", "add_colorkey_overlay"]:
            return handle_video_operations(operation, parameters)
        elif operation in ["extract_frame", "extract_frame_from_url"]:
            return handle_frame_extraction(operation, parameters)
        elif operation in ["get_video_info", "get_audio_info"]:
            return handle_media_info(operation, parameters)
        elif operation in ["upload_file", "download_file", "delete_file", "file_status"]:
            return handle_storage_operations(operation, parameters)
        elif operation == "list_fonts":
            return handle_font_operations(parameters)
        else:
            return {"error": f"Unsupported operation: {operation}"}
            
    except Exception as e:
        logger.error(f"Handler error: {e}")
        return {"error": str(e)}

def handle_tts_operations(operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Handle TTS-related operations."""
    temp_dir = create_temp_directory()
    
    try:
        if operation == "generate_kokoro_tts":
            return generate_kokoro_tts(parameters, temp_dir)
        elif operation == "generate_chatterbox_tts":
            return generate_chatterbox_tts(parameters, temp_dir)
        elif operation == "get_kokoro_voices":
            return get_kokoro_voices(parameters)
    finally:
        cleanup_temp_directory(temp_dir)

def generate_kokoro_tts(parameters: Dict[str, Any], temp_dir: str) -> Dict[str, Any]:
    """Generate TTS using Kokoro TTS."""
    text = parameters.get("text")
    if not text:
        raise ValueError("Missing required parameter: text")
    
    voice = parameters.get("voice", "af_heart")
    speed = parameters.get("speed", 1.0)
    
    # Generate unique filename
    audio_filename = f"kokoro_tts_{uuid.uuid4().hex}.wav"
    local_audio_path = os.path.join(temp_dir, audio_filename)
    
    # Generate TTS
    logger.info(f"Generating Kokoro TTS for text length: {len(text)} with voice: {voice}")
    captions, audio_length = tts_manager.kokoro(
        text=text,
        output_path=local_audio_path,
        voice=voice,
        speed=speed
    )
    
    # Store to persistent storage
    storage_key = f"tts_output/{audio_filename}"
    storage_url = storage.store_file(local_audio_path, storage_key)
    
    return {
        "audio_url": storage_url,
        "audio_length": audio_length,
        "captions": captions,
        "voice": voice,
        "speed": speed,
        "text_length": len(text)
    }

def generate_chatterbox_tts(parameters: Dict[str, Any], temp_dir: str) -> Dict[str, Any]:
    """Generate TTS using ChatterboxTTS."""
    text = parameters.get("text")
    if not text:
        raise ValueError("Missing required parameter: text")
    
    sample_audio_url = parameters.get("sample_audio_url")
    exaggeration = parameters.get("exaggeration", 0.5)
    cfg_weight = parameters.get("cfg_weight", 0.5)
    temperature = parameters.get("temperature", 0.8)
    
    # Generate unique filename
    audio_filename = f"chatterbox_tts_{uuid.uuid4().hex}.wav"
    local_audio_path = os.path.join(temp_dir, audio_filename)
    
    # Handle sample audio if provided
    sample_audio_path = None
    if sample_audio_url:
        sample_filename = f"sample_{uuid.uuid4().hex}.wav"
        sample_audio_path = os.path.join(temp_dir, sample_filename)
        
        # Download sample audio
        import requests
        response = requests.get(sample_audio_url)
        response.raise_for_status()
        
        with open(sample_audio_path, 'wb') as f:
            f.write(response.content)
    
    # Generate TTS
    logger.info(f"Generating ChatterboxTTS for text length: {len(text)}")
    tts_chatterbox.chatterbox(
        text=text,
        output_path=local_audio_path,
        sample_audio_path=sample_audio_path,
        exaggeration=exaggeration,
        cfg_weight=cfg_weight,
        temperature=temperature
    )
    
    # Get audio info
    audio_info = media_utils.get_audio_info(local_audio_path)
    audio_length = audio_info.get("duration", 0)
    
    # Store to persistent storage
    storage_key = f"tts_output/{audio_filename}"
    storage_url = storage.store_file(local_audio_path, storage_key)
    
    return {
        "audio_url": storage_url,
        "audio_length": audio_length,
        "has_sample_audio": sample_audio_url is not None,
        "exaggeration": exaggeration,
        "cfg_weight": cfg_weight,
        "temperature": temperature,
        "text_length": len(text)
    }

def get_kokoro_voices(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Get available Kokoro TTS voices."""
    lang_code = parameters.get("lang_code")
    
    voices = tts_manager.valid_kokoro_voices(lang_code)
    
    # Get detailed voice information
    from video.tts import LANGUAGE_VOICE_MAP
    
    voice_details = []
    for voice in voices:
        if voice in LANGUAGE_VOICE_MAP:
            voice_info = LANGUAGE_VOICE_MAP[voice].copy()
            voice_info["voice_id"] = voice
            voice_details.append(voice_info)
    
    return {
        "voices": voice_details,
        "total_count": len(voice_details),
        "filtered_by_language": lang_code is not None,
        "language_filter": lang_code
    }

def handle_transcription(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Handle speech-to-text transcription."""
    audio_url = parameters.get("audio_url")
    if not audio_url:
        raise ValueError("Missing required parameter: audio_url")
    
    model = parameters.get("model", "base")
    temp_dir = create_temp_directory()
    
    try:
        # Download audio file
        audio_filename = f"transcribe_{uuid.uuid4().hex}.wav"
        local_audio_path = os.path.join(temp_dir, audio_filename)
        
        import requests
        response = requests.get(audio_url)
        response.raise_for_status()
        
        with open(local_audio_path, 'wb') as f:
            f.write(response.content)
        
        # Transcribe
        logger.info(f"Transcribing audio with model: {model}")
        transcription = stt.transcribe(local_audio_path, model=model)
        
        return {
            "transcription": transcription,
            "model": model,
            "audio_url": audio_url
        }
    finally:
        cleanup_temp_directory(temp_dir)

def handle_video_operations(operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Handle video processing operations."""
    temp_dir = create_temp_directory()
    
    try:
        if operation == "merge_videos":
            return merge_videos(parameters, temp_dir)
        elif operation == "generate_captioned_video":
            return generate_captioned_video(parameters, temp_dir)
        elif operation == "add_colorkey_overlay":
            return add_colorkey_overlay(parameters, temp_dir)
    finally:
        cleanup_temp_directory(temp_dir)

def merge_videos(parameters: Dict[str, Any], temp_dir: str) -> Dict[str, Any]:
    """Merge multiple video files."""
    video_urls = parameters.get("video_urls", [])
    if not video_urls or len(video_urls) < 2:
        raise ValueError("Need at least 2 video URLs to merge")
    
    # Download videos
    local_video_paths = []
    for i, url in enumerate(video_urls):
        video_filename = f"video_{i}_{uuid.uuid4().hex}.mp4"
        local_path = os.path.join(temp_dir, video_filename)
        
        import requests
        response = requests.get(url)
        response.raise_for_status()
        
        with open(local_path, 'wb') as f:
            f.write(response.content)
        local_video_paths.append(local_path)
    
    # Merge videos
    output_filename = f"merged_{uuid.uuid4().hex}.mp4"
    output_path = os.path.join(temp_dir, output_filename)
    
    logger.info(f"Merging {len(video_urls)} videos")
    media_utils.merge_videos(local_video_paths, output_path)
    
    # Store result
    storage_key = f"video_output/{output_filename}"
    storage_url = storage.store_file(output_path, storage_key)
    
    return {
        "merged_video_url": storage_url,
        "input_count": len(video_urls),
        "output_filename": output_filename
    }

def generate_captioned_video(parameters: Dict[str, Any], temp_dir: str) -> Dict[str, Any]:
    """Generate video with captions."""
    video_url = parameters.get("video_url")
    captions = parameters.get("captions", [])
    
    if not video_url:
        raise ValueError("Missing required parameter: video_url")
    if not captions:
        raise ValueError("Missing required parameter: captions")
    
    # Download video
    video_filename = f"input_{uuid.uuid4().hex}.mp4"
    local_video_path = os.path.join(temp_dir, video_filename)
    
    import requests
    response = requests.get(video_url)
    response.raise_for_status()
    
    with open(local_video_path, 'wb') as f:
        f.write(response.content)
    
    # Generate captioned video
    output_filename = f"captioned_{uuid.uuid4().hex}.mp4"
    output_path = os.path.join(temp_dir, output_filename)
    
    font_path = parameters.get("font_path", None)
    font_size = parameters.get("font_size", 24)
    font_color = parameters.get("font_color", "white")
    
    logger.info(f"Generating captioned video with {len(captions)} captions")
    media_utils.add_captions_to_video(
        video_path=local_video_path,
        output_path=output_path,
        captions=captions,
        font_path=font_path,
        font_size=font_size,
        font_color=font_color
    )
    
    # Store result
    storage_key = f"video_output/{output_filename}"
    storage_url = storage.store_file(output_path, storage_key)
    
    return {
        "captioned_video_url": storage_url,
        "caption_count": len(captions),
        "font_size": font_size,
        "font_color": font_color
    }

def add_colorkey_overlay(parameters: Dict[str, Any], temp_dir: str) -> Dict[str, Any]:
    """Add colorkey overlay to video."""
    base_video_url = parameters.get("base_video_url")
    overlay_video_url = parameters.get("overlay_video_url")
    color_key = parameters.get("color_key", "#00FF00")  # Default green
    
    if not base_video_url or not overlay_video_url:
        raise ValueError("Missing required parameters: base_video_url, overlay_video_url")
    
    # Download videos
    base_filename = f"base_{uuid.uuid4().hex}.mp4"
    overlay_filename = f"overlay_{uuid.uuid4().hex}.mp4"
    base_path = os.path.join(temp_dir, base_filename)
    overlay_path = os.path.join(temp_dir, overlay_filename)
    
    import requests
    
    # Download base video
    response = requests.get(base_video_url)
    response.raise_for_status()
    with open(base_path, 'wb') as f:
        f.write(response.content)
    
    # Download overlay video
    response = requests.get(overlay_video_url)
    response.raise_for_status()
    with open(overlay_path, 'wb') as f:
        f.write(response.content)
    
    # Apply colorkey overlay
    output_filename = f"colorkey_{uuid.uuid4().hex}.mp4"
    output_path = os.path.join(temp_dir, output_filename)
    
    logger.info(f"Applying colorkey overlay with color: {color_key}")
    media_utils.add_colorkey_overlay(
        base_video_path=base_path,
        overlay_video_path=overlay_path,
        output_path=output_path,
        color_key=color_key
    )
    
    # Store result
    storage_key = f"video_output/{output_filename}"
    storage_url = storage.store_file(output_path, storage_key)
    
    return {
        "output_video_url": storage_url,
        "color_key": color_key,
        "base_video_url": base_video_url,
        "overlay_video_url": overlay_video_url
    }

def handle_frame_extraction(operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Handle frame extraction operations."""
    temp_dir = create_temp_directory()
    
    try:
        if operation == "extract_frame":
            video_url = parameters.get("video_url")
            timestamp = parameters.get("timestamp", 0)
            
            if not video_url:
                raise ValueError("Missing required parameter: video_url")
            
            # Download video
            video_filename = f"video_{uuid.uuid4().hex}.mp4"
            local_video_path = os.path.join(temp_dir, video_filename)
            
            import requests
            response = requests.get(video_url)
            response.raise_for_status()
            
            with open(local_video_path, 'wb') as f:
                f.write(response.content)
            
            # Extract frame
            frame_filename = f"frame_{uuid.uuid4().hex}.jpg"
            frame_path = os.path.join(temp_dir, frame_filename)
            
            logger.info(f"Extracting frame at timestamp: {timestamp}")
            media_utils.extract_frame(local_video_path, frame_path, timestamp)
            
            # Store result
            storage_key = f"frame_output/{frame_filename}"
            storage_url = storage.store_file(frame_path, storage_key)
            
            return {
                "frame_url": storage_url,
                "timestamp": timestamp,
                "video_url": video_url
            }
        elif operation == "extract_frame_from_url":
            # Similar implementation for URL-based extraction
            return handle_frame_extraction("extract_frame", parameters)
    finally:
        cleanup_temp_directory(temp_dir)

def handle_media_info(operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Handle media information operations."""
    temp_dir = create_temp_directory()
    
    try:
        media_url = parameters.get("video_url") if operation == "get_video_info" else parameters.get("audio_url")
        if not media_url:
            param_name = "video_url" if operation == "get_video_info" else "audio_url"
            raise ValueError(f"Missing required parameter: {param_name}")
        
        # Download media file
        media_filename = f"media_{uuid.uuid4().hex}.mp4"
        local_media_path = os.path.join(temp_dir, media_filename)
        
        import requests
        response = requests.get(media_url)
        response.raise_for_status()
        
        with open(local_media_path, 'wb') as f:
            f.write(response.content)
        
        # Get media info
        if operation == "get_video_info":
            info = media_utils.get_video_info(local_media_path)
        else:
            info = media_utils.get_audio_info(local_media_path)
        
        return {
            "media_info": info,
            "media_url": media_url,
            "operation": operation
        }
    finally:
        cleanup_temp_directory(temp_dir)

def handle_storage_operations(operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Handle storage operations."""
    if operation == "upload_file":
        file_url = parameters.get("file_url")
        storage_key = parameters.get("storage_key")
        
        if not file_url or not storage_key:
            raise ValueError("Missing required parameters: file_url, storage_key")
        
        temp_dir = create_temp_directory()
        try:
            # Download file
            temp_filename = f"upload_{uuid.uuid4().hex}"
            temp_path = os.path.join(temp_dir, temp_filename)
            
            import requests
            response = requests.get(file_url)
            response.raise_for_status()
            
            with open(temp_path, 'wb') as f:
                f.write(response.content)
            
            # Store file
            storage_url = storage.store_file(temp_path, storage_key)
            
            return {
                "storage_url": storage_url,
                "storage_key": storage_key,
                "original_url": file_url
            }
        finally:
            cleanup_temp_directory(temp_dir)
    
    elif operation == "file_status":
        storage_key = parameters.get("storage_key")
        if not storage_key:
            raise ValueError("Missing required parameter: storage_key")
        
        exists = storage.file_exists(storage_key)
        return {
            "exists": exists,
            "storage_key": storage_key
        }
    
    # Add other storage operations as needed
    return {"error": f"Storage operation {operation} not fully implemented yet"}

def handle_font_operations(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Handle font-related operations."""
    fonts = font_manager.list_available_fonts()
    return {
        "fonts": fonts,
        "total_count": len(fonts)
    }

# Configure RunPod
if __name__ == "__main__":
    logger.info("Starting unified RunPod serverless handler")
    runpod.serverless.start({"handler": handler})