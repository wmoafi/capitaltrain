# -*- coding: utf-8 -*-
"""
Robust, persistent runner for the 3 quick tunnels (6060, 8080, 9090)
with automatic restart and live URL export to text file.
"""
import subprocess
import time
import re
import os
import threading

PORTS = {
    6060: "القطار الكهربائي ومترو الخط الثالث (CapitalTrain)",
    8080: "المنصة التعليمية (Tafawuq Edu Portal)",
    9090: "بيت العربية (Bayt Al-Arabiya)"
}

EXE_PATH = r"I:\n8n\cloudflared.exe"
STATUS_FILE = r"I:\CapitalTrain\ACTIVE_WEB_LINKS.txt"

live_urls = {}
lock = threading.Lock()

def write_status():
    lines = [
        "===========================================================",
        "        روابط المواقع السحابية الخارجية النشطة الآن        ",
        "===========================================================",
        ""
    ]
    for p, name in PORTS.items():
        u = live_urls.get(p, "جارٍ التوليد والاتصال...")
        lines.append(f"🟢 {name} [منفذ {p}]:")
        lines.append(f"   {u}")
        lines.append("")
    lines.append("-----------------------------------------------------------")
    lines.append(f"آخر تحديث: {time.strftime('%Y-%m-%d %I:%M:%S %p')}")
    lines.append("===========================================================")
    
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def worker(port):
    cmd = [EXE_PATH, "tunnel", "--url", f"http://127.0.0.1:{port}", "--no-autoupdate"]
    while True:
        try:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="ignore")
            for line in iter(p.stdout.readline, ''):
                m = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
                if m:
                    found = m.group(0)
                    with lock:
                        live_urls[port] = found
                        write_status()
            p.wait()
        except Exception:
            pass
        time.sleep(5)

if __name__ == "__main__":
    for port in PORTS.keys():
        t = threading.Thread(target=worker, args=(port,), daemon=True)
        t.start()
    
    # Wait for all 3 URLs to be populated
    start = time.time()
    while time.time() - start < 25:
        with lock:
            if len(live_urls) == len(PORTS):
                break
        time.sleep(1)
    
    # Keep running forever
    while True:
        time.sleep(10)
