import sys
import os
import json
import re

sys.stdout.reconfigure(encoding='utf-8')
audio_path = sys.argv[1]

# Tiny model with initial prompt
PROMPT = "محطة الشروق عدلي منصور بدر حدائق العاصمة مدينة الفنون والثقافة العبور المستقبل مدينة المعرفة الروبيكي مطار العاصمة المنطقة الصناعية هليوبوليس الجديدة اتجاه إلى من"

try:
    from faster_whisper import WhisperModel
    # Load tiny model with prompt
    model = WhisperModel("tiny", device="cpu", compute_type="int8", cpu_threads=4)
    segments, info = model.transcribe(audio_path, language="ar", initial_prompt=PROMPT)
    text = " ".join([seg.text for seg in segments]).strip()
    print(text)
except Exception as e:
    sys.stderr.write(str(e))
    sys.exit(1)
