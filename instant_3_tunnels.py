import subprocess, time, re

def get_url(port):
    cmd = [r"I:\n8n\cloudflared.exe", "tunnel", "--url", f"http://127.0.0.1:{port}", "--no-autoupdate"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="ignore")
    url = None
    start = time.time()
    while time.time() - start < 12:
        line = p.stdout.readline()
        if not line:
            break
        m = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
        if m:
            url = m.group(0)
            break
    return p, url

p6, u6 = get_url(6060)
p8, u8 = get_url(8080)
p9, u9 = get_url(9090)

print("URL_6060:", u6)
print("URL_8080:", u8)
print("URL_9090:", u9)

with open("I:/CapitalTrain/LIVE_3_URLS.txt", "w", encoding="utf-8") as f:
    f.write(f"CapitalTrain: {u6}\n")
    f.write(f"TafawuqEdu: {u8}\n")
    f.write(f"BaytAlArabiya: {u9}\n")

# Keep them running indefinitely in background
while True:
    time.sleep(10)
