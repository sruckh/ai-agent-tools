
import os
import uuid
import tempfile
from typing import Dict, Any, List, Optional
from loguru import logger

# Import the base handler and storage utilities
from runpod_base import RunPodBaseHandler, RunPodStorageHandler, create_temp_directory, cleanup_temp_directory, extract_file_from_base64

# Import existing TTS and STT modules
from video.tts import TTS
from video.stt import STT
from video.config import device

class RunPodAudioHandler(RunPodBaseHandler):
    """
    RunPod serverless handler for audio operations.
    Supports TTS, STT, and other audio processing tasks.
    """
    
    def __init__(self):
        """Initialize the audio handler with models and storage."""
        super().__init__()
        self.storage = RunPodStorageHandler()
        self.tts = TTS()
        self.stt = STT()
        logger.info(f"Audio Handler initialized with device: {device}")
    
    def process_request(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process audio requests based on the operation type.
        """
        input_data = self.validate_input(event)
        operation = input_data["operation"]
        parameters = input_data.get("parameters", {})
        
        if operation == "generate_kokoro_tts":
            return self._generate_kokoro_tts(parameters)
        elif operation == "generate_chatterbox_tts":
            return self._generate_chatterbox_tts(parameters)
        elif operation == "get_kokoro_voices":
            return self._get_kokoro_voices(parameters)
        elif operation == "transcribe":
            return self._transcribe(parameters)
        else:
            raise ValueError(f"Unsupported operation: {operation}")

    def _transcribe(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transcribe audio file to text.
        """
        audio_url = parameters.get("audio_url")
        language = parameters.get("language")

        if not audio_url:
            raise ValueError("Missing required parameter: audio_url")

        temp_dir = create_temp_directory()
        try:
            local_audio_path = os.path.join(temp_dir, "audio.wav")
            
            # Download audio file
            import requests
            response = requests.get(audio_url)
            response.raise_for_status()
            with open(local_audio_path, 'wb') as f:
                f.write(response.content)

            captions, duration = self.stt.transcribe(local_audio_path, beam_size=5, language=language)
            transcription = "".join([cap["text"] for cap in captions])

            result = {
                "transcription": transcription,
                "duration": duration,
            }
            return self.create_success_response(result)
        finally:
            cleanup_temp_directory(temp_dir)

    def _generate_kokoro_tts(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        # ... (existing implementation)
        pass
    
    def _generate_chatterbox_tts(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        # ... (existing implementation)
        pass

    def _get_kokoro_voices(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        # ... (existing implementation)
        pass

def handler(event):
    """Main RunPod handler entry point."""
    audio_handler = RunPodAudioHandler()
    return audio_handler.handler(event)

if __name__ == "__main__":
    # For local testing
    pass
