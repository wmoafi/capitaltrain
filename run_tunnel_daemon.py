# Continuous tunnel supervisor for 6060
import subprocess, time, re

EXE_PATH = r"I:\n8n\cloudflared.exe"
cmd = [EXE_PATH, "tunnel", "--url", "http://127.0.0.1:6060", "--no-autoupdate"]

proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="ignore")
with open("I:/CapitalTrain/TUNNEL_6060_LOG.txt", "w", encoding="utf-8") as f:
    for line in iter(proc.stdout.readline, ''):
        f.write(line)
        f.flush()
        m = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
        if m:
            url = m.group(0)
            with open("I:/CapitalTrain/LIVE_TUNNEL_URL.txt", "w", encoding="utf-8") as uf:
                uf.write(url)
            print("CAPTURED_URL:", url, flush=True)
