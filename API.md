# API.md - RunPod Serverless Endpoints

## Overview

This document describes the RunPod Serverless API endpoints for the AI Agents A-Z No-Code Server. The system provides multiple specialized handlers for text-to-speech (TTS), audio processing, video generation, and file storage operations.

## Authentication

All requests require a valid RunPod API key provided in the Authorization header:

```
Authorization: Bearer YOUR_RUNPOD_API_KEY
```

## Base URL

**Synchronous Requests (wait for completion):**
```
POST https://api.runpod.ai/v2/{endpoint_id}/runsync
```

**Asynchronous Requests (immediate response with job ID):**
```
POST https://api.runpod.ai/v2/{endpoint_id}/run
```

## Request Format

All requests must include an `input` object with the operation and parameters:

```json
{
  "input": {
    "handler": "tts|audio|video|storage",
    "operation": "operation_name",
    "parameters": {
      // Operation-specific parameters
    }
  }
}
```

## Handler Types

### 1. TTS Handler (`"handler": "tts"`)

#### Generate Kokoro TTS

**Operation:** `generate_kokoro_tts`

**Description:** Generate high-quality TTS audio using Kokoro TTS model with multi-language support.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| text | string | Yes | Text to synthesize (max recommended: 500 chars) |
| voice | string | No | Voice ID (default: "af_heart") |
| speed | float | No | Speech speed multiplier (default: 1.0, range: 0.5-2.0) |
| lang_code | string | No | Language code (auto-detected from voice) |

**Example cURL:**
```bash
curl --request POST \
     --url https://api.runpod.ai/v2/your-endpoint-id/runsync \
     --header "Authorization: Bearer YOUR_API_KEY" \
     --header "Content-Type: application/json" \
     --data '{
       "input": {
         "handler": "tts",
         "operation": "generate_kokoro_tts",
         "parameters": {
           "text": "Hello, this is a test of the Kokoro TTS system.",
           "voice": "af_heart",
           "speed": 1.0
         }
       }
     }'
```

**RunPod Console JSON:**
```json
{
  "input": {
    "handler": "tts",
    "operation": "generate_kokoro_tts",
    "parameters": {
      "text": "Hello, this is a test of the Kokoro TTS system.",
      "voice": "af_heart",
      "speed": 1.0
    }
  }
}
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "audio_url": "https://your-s3-endpoint.com/bucket/tts_output/kokoro_tts_abc123.wav",
    "download_url": "https://presigned-url-for-download.com",
    "audio_length": 3.45,
    "captions": [
      {"start": 0.0, "end": 1.2, "text": "Hello,"},
      {"start": 1.2, "end": 3.45, "text": "this is a test..."}
    ],
    "voice": "af_heart",
    "speed": 1.0,
    "text_length": 42
  },
  "processing_time": 2.1
}
```

---

#### Generate ChatterboxTTS

**Operation:** `generate_chatterbox_tts`

**Description:** Generate TTS audio with voice cloning capabilities using ChatterboxTTS model.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| text | string | Yes | Text to synthesize |
| sample_audio_url | string | No | URL to sample audio for voice cloning |
| exaggeration | float | No | Voice exaggeration level (default: 0.5, range: 0.0-1.0) |
| cfg_weight | float | No | Configuration weight (default: 0.5, range: 0.0-1.0) |
| temperature | float | No | Generation temperature (default: 0.8, range: 0.1-1.0) |

**Example cURL:**
```bash
curl --request POST \
     --url https://api.runpod.ai/v2/your-endpoint-id/runsync \
     --header "Authorization: Bearer YOUR_API_KEY" \
     --header "Content-Type: application/json" \
     --data '{
       "input": {
         "handler": "tts",
         "operation": "generate_chatterbox_tts",
         "parameters": {
           "text": "This is a voice cloning test.",
           "sample_audio_url": "https://example.com/sample.wav",
           "exaggeration": 0.6,
           "cfg_weight": 0.7,
           "temperature": 0.8
         }
       }
     }'
```

**RunPod Console JSON:**
```json
{
  "input": {
    "handler": "tts",
    "operation": "generate_chatterbox_tts",
    "parameters": {
      "text": "This is a voice cloning test.",
      "sample_audio_url": "https://example.com/sample.wav",
      "exaggeration": 0.6,
      "cfg_weight": 0.7,
      "temperature": 0.8
    }
  }
}
```

---

#### Get Kokoro Voices

**Operation:** `get_kokoro_voices`

**Description:** Retrieve available Kokoro TTS voices with detailed information.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| lang_code | string | No | Filter voices by language code (e.g., "en", "es", "fr") |

**Example cURL:**
```bash
curl --request POST \
     --url https://api.runpod.ai/v2/your-endpoint-id/runsync \
     --header "Authorization: Bearer YOUR_API_KEY" \
     --header "Content-Type: application/json" \
     --data '{
       "input": {
         "handler": "tts",
         "operation": "get_kokoro_voices",
         "parameters": {
           "lang_code": "en"
         }
       }
     }'
```

**RunPod Console JSON:**
```json
{
  "input": {
    "handler": "tts",
    "operation": "get_kokoro_voices",
    "parameters": {
      "lang_code": "en"
    }
  }
}
```

---

### 2. Audio Handler (`"handler": "audio"`)

#### Transcribe Audio

**Operation:** `transcribe`

**Description:** Convert audio file to text using Whisper STT model.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| audio_url | string | Yes | URL to audio file for transcription |
| language | string | No | Source language code (auto-detected if not provided) |

**Example cURL:**
```bash
curl --request POST \
     --url https://api.runpod.ai/v2/your-endpoint-id/runsync \
     --header "Authorization: Bearer YOUR_API_KEY" \
     --header "Content-Type: application/json" \
     --data '{
       "input": {
         "handler": "audio",
         "operation": "transcribe",
         "parameters": {
           "audio_url": "https://example.com/audio.wav",
           "language": "en"
         }
       }
     }'
```

**RunPod Console JSON:**
```json
{
  "input": {
    "handler": "audio",
    "operation": "transcribe",
    "parameters": {
      "audio_url": "https://example.com/audio.wav",
      "language": "en"
    }
  }
}
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "transcription": "Hello, this is the transcribed text from the audio file.",
    "duration": 5.23
  },
  "processing_time": 1.8
}
```

---

### 3. Video Handler (`"handler": "video"`)

#### Generate Captioned Video

**Operation:** `generate_captioned_video`

**Description:** Create a video with captions from text or audio input.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| background_id | string | Yes | S3 key for background image |
| text | string | No | Text to convert to speech (if no audio_id) |
| width | integer | No | Video width (default: 1080) |
| height | integer | No | Video height (default: 1920) |
| audio_id | string | No | S3 key for audio file (alternative to text) |
| kokoro_voice | string | No | Voice for TTS (default: "af_heart") |
| kokoro_speed | float | No | TTS speed (default: 1.0) |
| language | string | No | Language for transcription |
| image_effect | string | No | Background effect (default: "ken_burns") |
| caption_config | object | No | Caption styling configuration |

**Example cURL:**
```bash
curl --request POST \
     --url https://api.runpod.ai/v2/your-endpoint-id/runsync \
     --header "Authorization: Bearer YOUR_API_KEY" \
     --header "Content-Type: application/json" \
     --data '{
       "input": {
         "handler": "video",
         "operation": "generate_captioned_video",
         "parameters": {
           "background_id": "image/background123.jpg",
           "text": "This is a test video with captions.",
           "width": 1080,
           "height": 1920,
           "kokoro_voice": "af_heart",
           "kokoro_speed": 1.0,
           "image_effect": "ken_burns"
         }
       }
     }'
```

**RunPod Console JSON:**
```json
{
  "input": {
    "handler": "video",
    "operation": "generate_captioned_video",
    "parameters": {
      "background_id": "image/background123.jpg",
      "text": "This is a test video with captions.",
      "width": 1080,
      "height": 1920,
      "kokoro_voice": "af_heart",
      "kokoro_speed": 1.0,
      "image_effect": "ken_burns"
    }
  }
}
```

---

#### Merge Videos

**Operation:** `merge_videos`

**Description:** Combine multiple video files with optional background music.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| video_ids | array | Yes | Array of S3 keys for video files to merge |
| background_music_id | string | No | S3 key for background music file |
| background_music_volume | float | No | Music volume level (default: 0.5, range: 0.0-1.0) |

**Example cURL:**
```bash
curl --request POST \
     --url https://api.runpod.ai/v2/your-endpoint-id/runsync \
     --header "Authorization: Bearer YOUR_API_KEY" \
     --header "Content-Type: application/json" \
     --data '{
       "input": {
         "handler": "video",
         "operation": "merge_videos",
         "parameters": {
           "video_ids": ["video/clip1.mp4", "video/clip2.mp4"],
           "background_music_id": "audio/music.mp3",
           "background_music_volume": 0.3
         }
       }
     }'
```

**RunPod Console JSON:**
```json
{
  "input": {
    "handler": "video",
    "operation": "merge_videos",
    "parameters": {
      "video_ids": ["video/clip1.mp4", "video/clip2.mp4"],
      "background_music_id": "audio/music.mp3",
      "background_music_volume": 0.3
    }
  }
}
```

---

#### Add Color Key Overlay

**Operation:** `add_colorkey_overlay`

**Description:** Apply color key (green screen) overlay effects to videos.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| video_id | string | Yes | S3 key for base video |
| overlay_video_id | string | Yes | S3 key for overlay video |
| color | string | No | Color to key out (default: "green") |
| similarity | float | No | Color similarity threshold (default: 0.1, range: 0.0-1.0) |
| blend | float | No | Blend amount (default: 0.1, range: 0.0-1.0) |

**Example cURL:**
```bash
curl --request POST \
     --url https://api.runpod.ai/v2/your-endpoint-id/runsync \
     --header "Authorization: Bearer YOUR_API_KEY" \
     --header "Content-Type: application/json" \
     --data '{
       "input": {
         "handler": "video",
         "operation": "add_colorkey_overlay",
         "parameters": {
           "video_id": "video/base.mp4",
           "overlay_video_id": "video/overlay.mp4",
           "color": "green",
           "similarity": 0.15,
           "blend": 0.05
         }
       }
     }'
```

**RunPod Console JSON:**
```json
{
  "input": {
    "handler": "video",
    "operation": "add_colorkey_overlay",
    "parameters": {
      "video_id": "video/base.mp4",
      "overlay_video_id": "video/overlay.mp4",
      "color": "green",
      "similarity": 0.15,
      "blend": 0.05
    }
  }
}
```

---

### 4. Storage Handler (`"handler": "storage"`)

#### Upload File

**Operation:** `upload`

**Description:** Upload files to S3-compatible storage from base64 data or URL.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| media_type | string | Yes | File category ("image", "video", "audio", "document") |
| file_data | string | No | Base64 encoded file data (use this OR url) |
| url | string | No | URL to download and upload file (use this OR file_data) |

**Example cURL (Base64):**
```bash
curl --request POST \
     --url https://api.runpod.ai/v2/your-endpoint-id/runsync \
     --header "Authorization: Bearer YOUR_API_KEY" \
     --header "Content-Type: application/json" \
     --data '{
       "input": {
         "handler": "storage",
         "operation": "upload",
         "parameters": {
           "media_type": "image",
           "file_data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
         }
       }
     }'
```

**Example cURL (URL):**
```bash
curl --request POST \
     --url https://api.runpod.ai/v2/your-endpoint-id/runsync \
     --header "Authorization: Bearer YOUR_API_KEY" \
     --header "Content-Type: application/json" \
     --data '{
       "input": {
         "handler": "storage",
         "operation": "upload",
         "parameters": {
           "media_type": "image",
           "url": "https://example.com/image.jpg"
         }
       }
     }'
```

**RunPod Console JSON:**
```json
{
  "input": {
    "handler": "storage",
    "operation": "upload",
    "parameters": {
      "media_type": "image",
      "url": "https://example.com/image.jpg"
    }
  }
}
```

---

#### Download File

**Operation:** `download`

**Description:** Generate a presigned download URL for a stored file.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| file_id | string | Yes | S3 key of the file to download |

**Example cURL:**
```bash
curl --request POST \
     --url https://api.runpod.ai/v2/your-endpoint-id/runsync \
     --header "Authorization: Bearer YOUR_API_KEY" \
     --header "Content-Type: application/json" \
     --data '{
       "input": {
         "handler": "storage",
         "operation": "download",
         "parameters": {
           "file_id": "image/abc123def456.jpg"
         }
       }
     }'
```

**RunPod Console JSON:**
```json
{
  "input": {
    "handler": "storage",
    "operation": "download",
    "parameters": {
      "file_id": "image/abc123def456.jpg"
    }
  }
}
```

---

#### Delete File

**Operation:** `delete`

**Description:** Permanently delete a file from storage.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| file_id | string | Yes | S3 key of the file to delete |

**Example cURL:**
```bash
curl --request POST \
     --url https://api.runpod.ai/v2/your-endpoint-id/runsync \
     --header "Authorization: Bearer YOUR_API_KEY" \
     --header "Content-Type: application/json" \
     --data '{
       "input": {
         "handler": "storage",
         "operation": "delete",
         "parameters": {
           "file_id": "image/abc123def456.jpg"
         }
       }
     }'
```

**RunPod Console JSON:**
```json
{
  "input": {
    "handler": "storage",
    "operation": "delete",
    "parameters": {
      "file_id": "image/abc123def456.jpg"
    }
  }
}
```

---

#### Check File Status

**Operation:** `status`

**Description:** Check if a file exists in storage.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| file_id | string | Yes | S3 key of the file to check |

**Example cURL:**
```bash
curl --request POST \
     --url https://api.runpod.ai/v2/your-endpoint-id/runsync \
     --header "Authorization: Bearer YOUR_API_KEY" \
     --header "Content-Type: application/json" \
     --data '{
       "input": {
         "handler": "storage",
         "operation": "status",
         "parameters": {
           "file_id": "image/abc123def456.jpg"
         }
       }
     }'
```

**RunPod Console JSON:**
```json
{
  "input": {
    "handler": "storage",
    "operation": "status",
    "parameters": {
      "file_id": "image/abc123def456.jpg"
    }
  }
}
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "status": "ready"
  },
  "processing_time": 0.1
}
```

---

## Standard Response Format

All successful operations return responses in this format:

```json
{
  "status": "success",
  "result": {
    // Operation-specific data
  },
  "processing_time": 1.23
}
```

## Error Handling

### Error Response Format
```json
{
  "status": "error",
  "error": {
    "type": "ValidationError",
    "message": "Missing required parameter: text"
  }
}
```

### Common Error Types
- `ValidationError` - Invalid or missing parameters
- `ProcessingError` - Error during operation execution
- `StorageError` - S3 storage operation failed
- `ModelError` - AI model processing failed
- `TimeoutError` - Operation exceeded time limit

## Rate Limiting

- **Concurrent requests per endpoint:** 10
- **Queue size:** 100 requests
- **Execution timeout:** 15 minutes (900 seconds)
- **File size limits:** 100MB per file
- **Text length limits:** 10,000 characters per TTS request

## Environment Variables

Required for deployment:

- `AWS_ACCESS_KEY_ID` - S3 access key
- `AWS_SECRET_ACCESS_KEY` - S3 secret key  
- `S3_ENDPOINT_URL` - S3 compatible endpoint URL
- `S3_BUCKET_NAME` - Storage bucket name

## Asynchronous Operations

For long-running operations, use the async endpoint (`/run`) to get immediate response with job ID:

**Response:**
```json
{
  "id": "job-uuid-abc123",
  "status": "IN_QUEUE"
}
```

**Check Status:**
```bash
curl --request GET \
     --url https://api.runpod.ai/v2/your-endpoint-id/status/job-uuid-abc123 \
     --header "Authorization: Bearer YOUR_API_KEY"
```

## Webhook Notifications

Add webhook URL to receive completion notifications:

```json
{
  "input": {
    "handler": "tts",
    "operation": "generate_kokoro_tts",
    "parameters": { ... }
  },
  "webhook": "https://your-webhook-url.com/callback"
}
```

## Keywords <!-- #keywords -->
- runpod
- serverless
- api
- tts
- text-to-speech
- audio-processing
- video-generation
- file-storage
- s3-compatible
- webhook
- ai-agents