# Multi-thread tunnel starter and tester
import subprocess, time, re, threading

urls = {}

def start_one(port, name):
    cmd = [r"I:\n8n\cloudflared.exe", "tunnel", "--url", f"http://127.0.0.1:{port}", "--no-autoupdate"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="ignore")
    for line in iter(p.stdout.readline, ''):
        m = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
        if m:
            urls[port] = m.group(0)
            print(f"[{port}] {name}: {m.group(0)}", flush=True)
            with open(f"I:/CapitalTrain/url_{port}.txt", "w", encoding="utf-8") as f:
                f.write(m.group(0))
            break
    p.wait()

t6 = threading.Thread(target=start_one, args=(6060, "CapitalTrain"), daemon=True)
t8 = threading.Thread(target=start_one, args=(8080, "TafawuqEdu"), daemon=True)
t9 = threading.Thread(target=start_one, args=(9090, "BaytAlArabiya"), daemon=True)

t6.start()
t8.start()
t9.start()

start = time.time()
while time.time() - start < 15:
    if len(urls) == 3:
        break
    time.sleep(1)

with open(r"I:\CapitalTrain\ALL_URLS.txt", "w", encoding="utf-8") as f:
    for p, u in urls.items():
        f.write(f"{p}: {u}\n")

print("FINISHED_CAPTURE:", urls, flush=True)

while True:
    time.sleep(10)
