#!/usr/bin/env python3
"""
Extract handler code from server.py to create individual handler files.
This is a lightweight operation using only Python standard library.
"""
import re
import os

def extract_handlers():
    """Extract embedded handler code from server.py"""
    
    # Read server.py content
    with open('server.py', 'r') as f:
        content = f.read()
    
    # Create handlers directory
    os.makedirs('runpod_handlers', exist_ok=True)
    
    # Extract base handler code
    base_match = re.search(r"runpod_base_code = '''(.*?)'''", content, re.DOTALL)
    if base_match:
        with open('runpod_handlers/runpod_base.py', 'w') as f:
            f.write(base_match.group(1))
        print("Created runpod_handlers/runpod_base.py")
    
    # Extract TTS handler code
    tts_match = re.search(r"tts_handler_code = '''(.*?)'''", content, re.DOTALL)
    if tts_match:
        with open('runpod_handlers/tts_handler.py', 'w') as f:
            f.write(tts_match.group(1))
        print("Created runpod_handlers/tts_handler.py")
    
    # Extract video handler code
    video_match = re.search(r"video_handler_code = '''(.*?)'''", content, re.DOTALL)
    if video_match:
        with open('runpod_handlers/video_handler.py', 'w') as f:
            f.write(video_match.group(1))
        print("Created runpod_handlers/video_handler.py")

if __name__ == "__main__":
    extract_handlers()