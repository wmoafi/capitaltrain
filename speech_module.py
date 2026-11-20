import urllib.request
import json
import subprocess
import os

FFMPEG_PATH = r"C:\Program Files\File Converter\ffmpeg.exe"

def ogg_to_wav(ogg_path, wav_path):
    cmd = [FFMPEG_PATH, "-y", "-i", ogg_path, "-ac", "1", "-ar", "16000", wav_path]
    res = subprocess.run(cmd, capture_output=True)
    return res.returncode == 0

def speech_to_text_google(wav_path, lang="ar-EG"):
    with open(wav_path, "rb") as f:
        audio_bytes = f.read()
    
    url = f"https://www.google.com/speech-api/v2/recognize?output=json&lang={lang}&key="
    req = urllib.request.Request(
        url,
        data=audio_bytes,
        headers={"Content-Type": "audio/l16; rate=16000"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode("utf-8")
            # Google speech API v2 returns lines of json
            for line in content.splitlines():
                if line.strip():
                    data = json.loads(line)
                    if "result" in data and data["result"]:
                        transcript = data["result"][0]["alternative"][0]["transcript"]
                        return transcript
    except Exception as e:
        print("Speech error:", e)
    return ""

print("Speech recognition module ready.")
