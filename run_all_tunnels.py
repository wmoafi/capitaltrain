# Multi-tunnel runner for 6060, 8080, and 9090
import subprocess, time, re, os, threading

PORTS = {
    6060: "القطار الكهربائي (CapitalTrain)",
    8080: "المنصة التعليمية (Tafawuq Edu)",
    9090: "بيت العربية (Bayt Al-Arabiya)"
}

EXE_PATH = r"I:\n8n\cloudflared.exe"
URL_LOG_FILE = r"I:\CapitalTrain\ALL_LIVE_TUNNELS.txt"

live_urls = {}

def monitor_tunnel(port, label):
    cmd = [EXE_PATH, "tunnel", "--url", f"http://127.0.0.1:{port}", "--no-autoupdate"]
    while True:
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="ignore"
            )
            for line in iter(proc.stdout.readline, ''):
                m = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
                if m:
                    u = m.group(0)
                    if live_urls.get(port) != u:
                        live_urls[port] = u
                        save_status()
            proc.wait()
        except Exception as e:
            pass
        time.sleep(5)

def save_status():
    lines = [
        "===========================================================",
        "           روابط المواقع السحابية النشطة الآن             ",
        "==========================================================="
    ]
    for p, name in PORTS.items():
        u = live_urls.get(p, "جارٍ التوليد...")
        lines.append(f"🔹 {name} [منفذ {p}]:")
        lines.append(f"   {u}\n")
    lines.append(f"تاريخ التحديث: {time.strftime('%Y-%m-%d %I:%M:%S %p')}")
    lines.append("===========================================================")
    content = "\n".join(lines)
    with open(URL_LOG_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print(content, flush=True)

if __name__ == "__main__":
    for p, lbl in PORTS.items():
        t = threading.Thread(target=monitor_tunnel, args=(p, lbl), daemon=True)
        t.start()
    
    # Keep alive
    while True:
        time.sleep(1)
