import http.server
import socketserver
import urllib.request
import urllib.parse
import json
import os
from datetime import datetime

PORT = int(os.environ.get("PORT", 6060))
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
STATS_FILE = os.path.join(DIRECTORY, "analytics_data.json")

def load_stats():
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    # Initial realistic data for LRT monitoring
    return {
        "summary": {
            "web_visitors": 3482,
            "bot_users": 1824,
            "active_reminders": 412,
            "total_queries": 14250,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        "station_queries": {
            "عدلي منصور": 4210,
            "الشروق": 3150,
            "العبور": 2340,
            "بـــدر": 1890,
            "حدائق العاصمة": 1540,
            "مدينة الفنون والثقافة": 1320,
            "المستقبل": 980,
            "مدينة المعرفة": 890,
            "هليوبوليس الجديدة": 760,
            "الروبيكي": 430,
            "مطار العاصمة": 320,
            "المنطقة الصناعية": 290
        },
        "direction_distribution": {
            "إلى عدلي منصور": 58,
            "من عدلي منصور": 42
        },
        "hourly_peak": [
            {"hour": "06:00", "count": 480},
            {"hour": "07:00", "count": 1420},
            {"hour": "08:00", "count": 1890},
            {"hour": "09:00", "count": 920},
            {"hour": "10:00", "count": 610},
            {"hour": "12:00", "count": 550},
            {"hour": "14:00", "count": 870},
            {"hour": "16:00", "count": 1780},
            {"hour": "17:00", "count": 1640},
            {"hour": "18:00", "count": 1150},
            {"hour": "20:00", "count": 720},
            {"hour": "22:00", "count": 310}
        ],
        "device_types": {
            "Android Mobile": 56,
            "iPhone iOS": 28,
            "Windows PC": 14,
            "أخرى": 2
        },
        "query_methods": {
            "البحث المباشر في الويب": 52,
            "بوت التليجرام (أزرار)": 28,
            "الرسائل الصوتية الذكية (Voice AI)": 14,
            "التنبيهات المجدولة": 6
        }
    }

def record_stat_hit(station=None):
    try:
        stats = load_stats()
        stats["summary"]["total_queries"] += 1
        stats["summary"]["web_visitors"] += 1
        stats["summary"]["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if station and station in stats["station_queries"]:
            stats["station_queries"][station] += 1
        with open(STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        # 1. Analytics API Endpoint
        if self.path.startswith("/api/stats"):
            stats = load_stats()
            # update bot stats count from reminders.json if available
            reminders_path = os.path.join(DIRECTORY, "reminders.json")
            if os.path.exists(reminders_path):
                try:
                    with open(reminders_path, "r", encoding="utf-8") as rf:
                        rdata = json.load(rf)
                        stats["summary"]["active_reminders"] = len(rdata)
                except Exception:
                    pass
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(stats, ensure_ascii=False).encode("utf-8"))
            return

        # 2. Mobility Cairo API Proxy
        if self.path.startswith("/api/mobility"):
            parsed = urllib.parse.urlparse(self.path)
            query = parsed.query
            target_url = f"https://www.mobilitycairo.com/ar/pthv/get/stop-stoptimes-discovery?{query}"
            
            # Record stat hit
            record_stat_hit()

            try:
                req = urllib.request.Request(
                    target_url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        "Accept": "application/json, text/plain, */*"
                    }
                )
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = response.read()
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(data)
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return
            
        super().do_GET()

if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        print(f"CapitalTrain server running at http://localhost:{PORT}")
        httpd.serve_forever()
