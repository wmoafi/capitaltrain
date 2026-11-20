# -*- coding: utf-8 -*-
"""
Cloudflare Permanent Tunnel Runner & Watchdog
Tunnel: tafawuq
Domains:
- CapitalTrain.tafawuq-edu.site -> localhost:6060
- tafawuq-edu.site -> localhost:8080
- portal.tafawuq-edu.site -> localhost:8080
- baytualarabia.tafawuq-edu.site -> localhost:9090
- tasks.tafawuq-edu.site -> localhost:8085
"""
import subprocess
import time
import os
import sys

TOKEN = "eyJhIjoiNTQ2OTYxZmQzNTNjY2ViM2QyMmQ1MjFjNzY2YTQ0MDYiLCJ0IjoiYTlmOGE2ZmQtZTQ3MC00MjAxLTgyZmQtOWFjNmFmYjg2ZDAxIiwicyI6Ill6QTRORE0xTWpZdE9URmtOQzAwWkRBMUxUZzFNbVF0WlRVMU1EQmtZak5oWmpCaSJ9"
CLOUDFLARED_EXE = r"I:\n8n\cloudflared.exe"
LOG_FILE = r"I:\CapitalTrain\tunnel_tafawuq.log"

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

def run():
    log("Starting Permanent Cloudflare Tunnel (tafawuq)...")
    cmd = [
        CLOUDFLARED_EXE,
        "tunnel",
        "run",
        "--token",
        TOKEN,
        "--no-autoupdate"
    ]
    
    while True:
        try:
            log("Executing cloudflared tunnel run...")
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="ignore"
            )
            for line in iter(proc.stdout.readline, ''):
                s = line.strip()
                if s:
                    log(s)
            proc.wait()
            log(f"Tunnel process ended with code: {proc.returncode}")
        except Exception as e:
            log(f"Tunnel runner exception: {e}")
        
        log("Restarting tunnel in 3 seconds...")
        time.sleep(3)

if __name__ == "__main__":
    run()
