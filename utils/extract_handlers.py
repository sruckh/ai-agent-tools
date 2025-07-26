import re

with open('server.py', 'r') as f:
    content = f.read()

# Extract base handler code
base_match = re.search(r"runpod_base_code = '''(.*?)'''", content, re.DOTALL)
if base_match:
    with open('runpod_handlers/runpod_base.py', 'w') as f:
        f.write(base_match.group(1).strip())

# Extract TTS handler code
tts_match = re.search(r"tts_handler_code = '''(.*?)'''", content, re.DOTALL)
if tts_match:
    with open('runpod_handlers/tts_handler.py', 'w') as f:
        f.write(tts_match.group(1).strip())

# Extract video handler code
video_match = re.search(r"video_handler_code = '''(.*?)'''", content, re.DOTALL)
if video_match:
    with open('runpod_handlers/video_handler.py', 'w') as f:
        f.write(video_match.group(1).strip())
