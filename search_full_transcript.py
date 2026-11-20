# search full transcript for tafawuq
import json, re

t_full = r"C:\Users\wmwafy\.gemini\antigravity\brain\0f610ba6-4831-49dd-9510-a87b731687ee\.system_generated\logs\transcript_full.jsonl"
with open(t_full, "r", encoding="utf-8", errors="ignore") as f:
    for i, line in enumerate(f):
        if "capitaltrain.tafawuq-edu.site" in line:
            # find where it first appeared or mentions of tunnel
            for match in re.finditer(r".{0,100}capitaltrain\.tafawuq-edu\.site.{0,100}", line):
                print(f"L{i}: {match.group(0)}")
