import json
from datetime import datetime

# Load Core Data
with open("lrt_data.json", "r", encoding="utf-8") as f:
    DATA = json.load(f)

def get_next_trains():
    now = datetime.now()
    cur_mins = now.hour * 60 + now.minute
    start_mins = 6 * 60      # 06:00
    end_mins = 23 * 60 + 20  # 23:20

    if cur_mins < start_mins:
        return "⏰ الخدمة تبدأ الساعة 06:00 صباحاً."
    if cur_mins > end_mins:
        return "🌙 انتهت رحلات اليوم. أول قطار غداً الساعة 06:00 صباحاً."

    # Generate timetable
    departures = []
    t = start_mins
    while t <= end_mins:
        if t >= cur_mins:
            hh = t // 60
            mm = t % 60
            departures.append(f"{hh:02d}:{mm:02d} (بعد {t - cur_mins} دقيقة)")
            if len(departures) >= 3:
                break
        
        # Determine headway
        h_dec = t / 60.0
        headway = 15
        if (7 <= h_dec < 10) or (14 <= h_dec < 17.5):
            headway = 10
        elif h_dec >= 21:
            headway = 20
        t += headway

    return "🚆 الرحلات القادمة الآن:\n" + "\n".join([f"• {d}" for d in departures])

def calculate_ticket(stations_count):
    for rule in DATA["fare_rules"]:
        if stations_count <= rule["max_stations"]:
            return rule["ticket_price_egp"], rule["monthly_pass_egp"]
    return 20, 600

def format_telegram_welcome():
    return (
        "👋 أهلاً بك في بوت قطار العاصمة الكهربائي الخفيف (LRT)!\n\n"
        "الخيارات المتاحة:\n"
        "1️⃣ /next - مواعيد القطارات القادمة فوراً والعد التنازلي\n"
        "2️⃣ /stations - قائمة محطات الخط ونقاط التبديل\n"
        "3️⃣ /fares - قائمة أسعار التذاكر والاشتراكات الشهرية\n"
        "4️⃣ /support - الخط الساخن وأرقام الشكاوى"
    )

if __name__ == "__main__":
    print(format_telegram_welcome())
    print("\n" + "="*40 + "\n")
    print(get_next_trains())
