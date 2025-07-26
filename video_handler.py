
import os
import uuid
from typing import Dict, Any

from loguru import logger

from runpod_base import RunPodBaseHandler, RunPodStorageHandler, create_temp_directory, cleanup_temp_directory
from video.tts import TTS
from video.stt import STT
from video.caption import Caption
from video.media import MediaUtils
from video.builder import VideoBuilder
from utils.image import resize_image_cover


class RunPodVideoHandler(RunPodBaseHandler):
    def __init__(self):
        super().__init__()
        self.storage = RunPodStorageHandler()
        self.tts = TTS()
        self.stt = STT()
        self.caption = Caption()
        self.media_utils = MediaUtils()

    def process_request(self, event: Dict[str, Any]) -> Dict[str, Any]:
        input_data = self.validate_input(event)
        operation = input_data["operation"]
        parameters = input_data.get("parameters", {})

        if operation == "generate_captioned_video":
            return self._generate_captioned_video(parameters)
        elif operation == "merge_videos":
            return self._merge_videos(parameters)
        elif operation == "add_colorkey_overlay":
            return self._add_colorkey_overlay(parameters)
        else:
            raise ValueError(f"Unsupported operation: {operation}")

    def _add_colorkey_overlay(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        video_id = parameters.get("video_id")
        overlay_video_id = parameters.get("overlay_video_id")
        color = parameters.get("color", "green")
        similarity = parameters.get("similarity", 0.1)
        blend = parameters.get("blend", 0.1)

        if not video_id or not overlay_video_id:
            raise ValueError("Missing required parameter: video_id and overlay_video_id")

        temp_dir = create_temp_directory()
        try:
            video_path = self.storage.download_file(f"video/{video_id}", os.path.join(temp_dir, video_id))
            overlay_video_path = self.storage.download_file(f"video/{overlay_video_id}", os.path.join(temp_dir, overlay_video_id))

            output_filename = f"video/{uuid.uuid4().hex}.mp4"
            local_output_path = os.path.join(temp_dir, output_filename)

            self.media_utils.colorkey_overlay(
                input_video_path=video_path,
                overlay_video_path=overlay_video_path,
                output_video_path=local_output_path,
                color=color,
                similarity=similarity,
                blend=blend,
            )

            video_url = self.storage.upload_file(local_output_path, output_filename)
            download_url = self.storage.generate_presigned_url(output_filename)

            result = {
                "file_id": output_filename,
                "video_url": video_url,
                "download_url": download_url,
            }
            return self.create_success_response(result)
        finally:
            cleanup_temp_directory(temp_dir)

    def _merge_videos(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        video_ids = parameters.get("video_ids", [])
        background_music_id = parameters.get("background_music_id")
        background_music_volume = parameters.get("background_music_volume", 0.5)

        if not video_ids:
            raise ValueError("Missing required parameter: video_ids")

        temp_dir = create_temp_directory()
        try:
            video_paths = []
            for video_id in video_ids:
                video_path = self.storage.download_file(f"video/{video_id}", os.path.join(temp_dir, video_id))
                video_paths.append(video_path)

            background_music_path = None
            if background_music_id:
                background_music_path = self.storage.download_file(f"audio/{background_music_id}", os.path.join(temp_dir, background_music_id))

            output_filename = f"video/{uuid.uuid4().hex}.mp4"
            local_output_path = os.path.join(temp_dir, output_filename)

            self.media_utils.merge_videos(
                video_paths=video_paths,
                output_path=local_output_path,
                background_music_path=background_music_path,
                background_music_volume=background_music_volume,
            )

            video_url = self.storage.upload_file(local_output_path, output_filename)
            download_url = self.storage.generate_presigned_url(output_filename)

            result = {
                "file_id": output_filename,
                "video_url": video_url,
                "download_url": download_url,
            }
            return self.create_success_response(result)
        finally:
            cleanup_temp_directory(temp_dir)

    def _generate_captioned_video(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        # Extract parameters
        background_id = parameters.get("background_id")
        text = parameters.get("text")
        width = parameters.get("width", 1080)
        height = parameters.get("height", 1920)
        audio_id = parameters.get("audio_id")
        kokoro_voice = parameters.get("kokoro_voice", "af_heart")
        kokoro_speed = parameters.get("kokoro_speed", 1.0)
        language = parameters.get("language")
        image_effect = parameters.get("image_effect", "ken_burns")
        caption_config = parameters.get("caption_config", {})

        # Create a temp dir for processing
        temp_dir = create_temp_directory()
        
        try:
            # Create video builder
            dimensions = (width, height)
            builder = VideoBuilder(dimensions=dimensions)
            builder.set_media_utils(self.media_utils)

            # Handle audio and captions
            if audio_id:
                audio_path = self.storage.download_file(f"audio/{audio_id}", os.path.join(temp_dir, audio_id))
                captions, _ = self.stt.transcribe(audio_path, language=language)
                builder.set_audio(audio_path)
            else:
                tts_audio_path = os.path.join(temp_dir, f"{uuid.uuid4()}.wav")
                captions, _ = self.tts.kokoro(text, tts_audio_path, kokoro_voice, kokoro_speed)
                builder.set_audio(tts_audio_path)

            # Create subtitles
            subtitle_path = os.path.join(temp_dir, f"{uuid.uuid4()}.ass")
            segments = self.caption.create_subtitle_segments_english(captions, **caption_config)
            self.caption.create_subtitle(segments, subtitle_path, dimensions, **caption_config)
            builder.set_captions(subtitle_path)

            # Handle background
            background_path = self.storage.download_file(f"image/{background_id}", os.path.join(temp_dir, background_id))
            
            # Resize background if needed
            info = self.media_utils.get_video_info(background_path)
            if info.get("width", 0) != width or info.get("height", 0) != height:
                resized_background_path = os.path.join(temp_dir, f"resized_{background_id}")
                resize_image_cover(background_path, resized_background_path, width, height)
                background_path = resized_background_path

            builder.set_background_image(background_path, effect_config={"effect": image_effect})

            # Execute video generation
            output_filename = f"video/{uuid.uuid4().hex}.mp4"
            local_output_path = os.path.join(temp_dir, output_filename)
            builder.set_output_path(local_output_path)
            builder.execute()

            # Upload to S3
            video_url = self.storage.upload_file(local_output_path, output_filename)
            download_url = self.storage.generate_presigned_url(output_filename)

            result = {
                "file_id": output_filename,
                "video_url": video_url,
                "download_url": download_url,
            }
            return self.create_success_response(result)

        finally:
            cleanup_temp_directory(temp_dir)


def handler(event):
    video_handler = RunPodVideoHandler()
    return video_handler.handler(event)

if __name__ == "__main__":
    # This is for local testing
    pass
