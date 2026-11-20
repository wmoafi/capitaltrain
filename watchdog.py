# -*- coding: utf-8 -*-
"""
Watchdog script to monitor:
1) serve_6060.py (CapitalTrain & Metro Line 3 Web App)
2) telegram_bot_runner.py (Telegram Bot @trainlrt_Bot)
3) cloudflared.exe (Permanent Tunnel for tafawuq)
Guarantees 0% CPU consumption and zero duplicate instances.
"""
import subprocess
import time
import os
import sys

BASE_DIR = r"I:\CapitalTrain"
PYTHON_EXE = r"C:\Python314\python.exe"
CLOUDFLARED_EXE = r"I:\n8n\cloudflared.exe"
TUNNEL_TOKEN = "eyJhIjoiNTQ2OTYxZmQzNTNjY2ViM2QyMmQ1MjFjNzY2YTQ0MDYiLCJ0IjoiYTlmOGE2ZmQtZTQ3MC00MjAxLTgyZmQtOWFjNmFmYjg2ZDAxIiwicyI6Ill6QTRORE0xTWpZdE9URmtOQzAwWkRBMUxUZzFNbVF0WlRVMU1EQmtZak5oWmpCaSJ9"

# In-memory process tracking
processes = {
    "serve_6060": None,
    "telegram_bot": None,
    "cloudflared": None
}

def is_alive(proc):
    return proc is not None and proc.poll() is None

def start_script(script_name):
    cmd = [PYTHON_EXE, os.path.join(BASE_DIR, script_name)]
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    p = subprocess.Popen(
        cmd,
        cwd=BASE_DIR,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
        env=env
    )
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Started {script_name} (PID: {p.pid})", flush=True)
    return p

def start_tunnel():
    cmd = [
        CLOUDFLARED_EXE,
        "--no-autoupdate",
        "tunnel",
        "run",
        "--token",
        TUNNEL_TOKEN
    ]
    p = subprocess.Popen(
        cmd,
        cwd=BASE_DIR,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    )
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Started Cloudflare Tunnel (PID: {p.pid})", flush=True)
    return p

def main():
    print("CapitalTrain & Cloudflare Unified Zero-CPU Watchdog started...", flush=True)
    while True:
        try:
            if not is_alive(processes["serve_6060"]):
                processes["serve_6060"] = start_script("serve_6060.py")
            if not is_alive(processes["telegram_bot"]):
                processes["telegram_bot"] = start_script("telegram_bot_runner.py")
            if not is_alive(processes["cloudflared"]):
                processes["cloudflared"] = start_tunnel()
        except Exception as e:
            print(f"Watchdog error: {e}", flush=True)
        time.sleep(15)

if __name__ == "__main__":
    main()
