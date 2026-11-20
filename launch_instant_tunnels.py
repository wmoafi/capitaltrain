import subprocess, time, re

def start_tunnel(port):
    cmd = [r"I:\n8n\cloudflared.exe", "tunnel", "--url", f"http://127.0.0.1:{port}", "--no-autoupdate"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="ignore")
    url = None
    start = time.time()
    while time.time() - start < 15:
        line = p.stdout.readline()
        if not line:
            break
        m = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
        if m:
            url = m.group(0)
            break
    return p, url

p6060, url6060 = start_tunnel(6060)
print("CapitalTrain (port 6060) Tunnel URL:", url6060)

with open("I:/CapitalTrain/LIVE_TUNNELS.txt", "w", encoding="utf-8") as f:
    f.write(f"CapitalTrain (6060): {url6060}\n")
