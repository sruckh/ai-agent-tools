# AI Agents A-Z No-Code Tools

Video editing tools to use with no-code tools like n8n, Zapier, and Make. Brought to you by [AI Agents A-Z](https://www.youtube.com/@aiagentsaz).

## RunPod Serverless API

This Docker image provides a RunPod serverless API for a variety of audio and video processing tasks.

### API Usage

To use the API, send a POST request to your RunPod endpoint with a JSON payload in the following format:

```json
{
  "input": {
    "handler": "handler_name",
    "operation": "operation_name",
    "parameters": {
      ...
    }
  }
}
```

### Storage Handler (`handler": "storage"`)

#### Operations

*   **`upload`**: Upload a file from a URL or base64 data.
*   **`download`**: Get a presigned URL to download a file.
*   **`delete`**: Delete a file.
*   **`status`**: Check the status of a file.

#### Examples

**Upload from URL:**
```json
{
  "input": {
    "handler": "storage",
    "operation": "upload",
    "parameters": {
      "media_type": "image",
      "url": "https://example.com/my-image.png"
    }
  }
}
```

**Upload Base64 Data:**
```json
{
  "input": {
    "handler": "storage",
    "operation": "upload",
    "parameters": {
      "media_type": "image",
      "file_data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA..."
    }
  }
}
```

### Audio Handler (`handler": "audio"`)

#### Operations

*   **`transcribe`**: Transcribe an audio file to text.
*   **`generate_kokoro_tts`**: Generate speech from text using Kokoro TTS.
*   **`generate_chatterbox_tts`**: Generate speech from text using Chatterbox TTS, with optional voice cloning.
*   **`get_kokoro_voices`**: Get a list of available Kokoro TTS voices.

#### Examples

**Transcribe Audio:**
```json
{
  "input": {
    "handler": "audio",
    "operation": "transcribe",
    "parameters": {
      "audio_url": "your_audio_file_url"
    }
  }
}
```

**Generate Chatterbox TTS with Voice Cloning:**
```json
{
  "input": {
    "handler": "audio",
    "operation": "generate_chatterbox_tts",
    "parameters": {
        "text": "Hello, this is a test of the Chatterbox TTS system.",
        "sample_audio_url": "your_sample_audio_url.wav"
    }
  }
}
```

### Video Handler (`handler": "video"`)

#### Operations

*   **`merge_videos`**: Merge multiple videos into one, with optional background music.
*   **`add_colorkey_overlay`**: Overlay a video on another using a color key (e.g., green screen).
*   **`generate_captioned_video`**: Create a video with captions from text and a background image.

#### Examples

**Merge Videos:**
```json
{
  "input": {
    "handler": "video",
    "operation": "merge_videos",
    "parameters": {
      "video_ids": ["video_id_1", "video_id_2"],
      "background_music_id": "music_id",
      "background_music_volume": 0.7
    }
  }
}
```

**Generate Captioned Video:**
```json
{
  "input": {
    "handler": "video",
    "operation": "generate_captioned_video",
    "parameters": {
      "background_id": "your_background_image_id",
      "text": "This is the text for the video.",
      "width": 1080,
      "height": 1920,
      "kokoro_voice": "af_heart",
      "caption_config": {
        "font_size": 120
      }
    }
  }
}
```
