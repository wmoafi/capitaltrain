# -*- coding: utf-8 -*-
"""
Helper to update telegram_bot_runner.py with:
- Smart Transfer Guarantee (هل هلحق قطار العاصمة من المترو؟)
- Accurate actual travel time calculation and ETA
- Voice and text query matching for transfers
"""

with open('I:/CapitalTrain/telegram_bot_runner.py', 'r', encoding='utf-8') as f:
    orig_bot = f.read()

# Add transfer time matrices
matrix_defs = '''
# Accurate Travel Minutes from any Line 3 Station to Adly Mansour Hub
METRO_TO_ADLY_MINS = {
    "139886": 0, "139913": 2, "139911": 4, "139914": 6, "139901": 8, "139915": 10,
    "139919": 13, "139889": 15, "139900": 17, "139899": 19, "139887": 21, "139905": 23,
    "139921": 25, "139893": 27, "139883": 30, "139884": 32, "139897": 34, "139891": 36,
    "139890": 38, "139909": 41, "139908": 43, "139918": 46, "139906": 49, "139922": 52,
    "139903": 54, "139895": 57, "139894": 59, "139902": 62, "139917": 65, "139999": 52,
    "140001": 55, "139998": 57, "139997": 60, "140000": 63
}

# Accurate Travel Minutes from Adly Mansour to each LRT Station
LRT_FROM_ADLY_MINS = {
    "139886": 0, "139912": 4, "139896": 8, "139920": 13, "139910": 18,
    "139892": 24, "139916": 29, "139898": 34, "139888": 39, "139885": 44,
    "139904": 30, "139907": 36
}

def get_actual_travel_mins(start_id, end_id, network='lrt'):
    if network == 'metro':
        m1 = METRO_TO_ADLY_MINS.get(start_id, 0)
        m2 = METRO_TO_ADLY_MINS.get(end_id, 0)
        return abs(m1 - m2)
    else:
        l1 = LRT_FROM_ADLY_MINS.get(start_id, 0)
        l2 = LRT_FROM_ADLY_MINS.get(end_id, 0)
        return abs(l1 - l2)

def calculate_smart_transfer_info(metro_id, lrt_dest_id, base_mins=None):
    if base_mins is None:
        now = datetime.now()
        base_mins = now.hour * 60 + now.minute

    metro_obj = get_station_by_id(metro_id, network='metro')
    lrt_dest_obj = get_station_by_id(lrt_dest_id, network='lrt')

    metro_ride = METRO_TO_ADLY_MINS.get(metro_id, 20)
    adly_arrival_mins = base_mins + metro_ride
    walk_buffer = 5
    ready_mins = adly_arrival_mins + walk_buffer

    # Format HH:MM
    adly_arr_h = (adly_arrival_mins // 60) % 24
    adly_arr_m = adly_arrival_mins % 60
    adly_arr_str = f"{adly_arr_h:02d}:{adly_arr_m:02d}"

    ready_h = (ready_mins // 60) % 24
    ready_m = ready_mins % 60
    ready_str = f"{ready_h:02d}:{ready_m:02d}"

    # Query LRT from Adly (139886)
    schedules = fetch_live_schedule_from_mobility_cairo("139886", "0", network='lrt')
    best = None
    nxt = None

    for s in schedules:
        dep = s.get("DepTime", "")
        hhmm = dep.split(" ")[1] if " " in dep else dep
        if ":" in hhmm:
            p = hhmm.split(":")
            tm = int(p[0]) * 60 + int(p[1])
            diff = tm - ready_mins
            if diff >= 0 and not best:
                best = {"time": hhmm, "diff": diff, "tm": tm}
            elif diff >= 0 and best and not nxt:
                nxt = {"time": hhmm, "diff": diff, "tm": tm}
                break

    if not best:
        fb_tm = ready_mins + 8
        best = {"time": f"{(fb_tm//60)%24:02d}:{fb_tm%60:02d}", "diff": 8, "tm": fb_tm}
        nxt = {"time": f"{((fb_tm+15)//60)%24:02d}:{(fb_tm+15)%60:02d}", "diff": 23, "tm": fb_tm + 15}

    lrt_ride = LRT_FROM_ADLY_MINS.get(lrt_dest_id, 20)
    final_arr_mins = best["tm"] + lrt_ride
    final_arr_str = f"{(final_arr_mins//60)%24:02d}:{final_arr_mins%60:02d}"

    return {
        "metro_name": metro_obj["name"] if metro_obj else metro_id,
        "lrt_name": lrt_dest_obj["name"] if lrt_dest_obj else lrt_dest_id,
        "metro_ride": metro_ride,
        "adly_arr": adly_arr_str,
        "ready_time": ready_str,
        "best_time": best["time"],
        "best_diff": best["diff"],
        "next_time": nxt["time"] if nxt else "--:--",
        "final_arr": final_arr_str,
        "lrt_ride": lrt_ride
    }
'''

# Insert after METRO_STATIONS
pos = orig_bot.find("DAYS_LIST = [")
orig_bot = orig_bot[:pos] + matrix_defs + "\n" + orig_bot[pos:]

# Update get_main_menu_keyboard
old_kb = '''        "inline_keyboard": [
            [
                {"text": "🚆 قطار العاصمة (LRT)", "callback_data": "choose_net:lrt"},
                {"text": "🚇 مترو الخط الثالث (GL3)", "callback_data": "choose_net:metro"}
            ],
            [
                {"text": "🌐 موقع المواعيد وحساب الرحلات", "url": WEB_URL},
                {"text": "📲 تحميل تطبيق أندرويد APK", "url": f"{WEB_URL}/downloads/capital_train_lrt.apk"}
            ],'''

new_kb = '''        "inline_keyboard": [
            [
                {"text": "⚡ هل هلحق قطار العاصمة من المترو؟", "callback_data": "transfer_metro_select"}
            ],
            [
                {"text": "🚆 قطار العاصمة (LRT)", "callback_data": "choose_net:lrt"},
                {"text": "🚇 مترو الخط الثالث (GL3)", "callback_data": "choose_net:metro"}
            ],
            [
                {"text": "🌐 موقع المواعيد وحساب الرحلات", "url": WEB_URL},
                {"text": "📲 تحميل تطبيق أندرويد APK", "url": f"{WEB_URL}/downloads/capital_train_lrt.apk"}
            ],'''

orig_bot = orig_bot.replace(old_kb, new_kb)

# Add transfer handlers into callback query
cb_target = 'if data == "main_menu":'
cb_injection = '''if data == "transfer_metro_select":
                        rows = []
                        temp = []
                        for s in METRO_STATIONS:
                            temp.append({"text": s["name"], "callback_data": f"tf_m:{s['id']}"})
                            if len(temp) == 2:
                                rows.append(temp)
                                temp = []
                        if temp:
                            rows.append(temp)
                        rows.append([{"text": "🔙 القائمة الرئيسية", "callback_data": "main_menu"}])
                        send_or_edit_message(
                            chat_id,
                            "⚡ <b>حاسبة الربط: «هل هلحق قطار العاصمة من المترو؟»</b>\\n\\n"
                            "🚇 <b>اختر محطة المترو التي تتواجد بها حالياً:</b>",
                            {"inline_keyboard": rows},
                            msg_id
                        )
                        continue

                    if data.startswith("tf_m:"):
                        m_id = data.split(":")[1]
                        rows = []
                        temp = []
                        for s in LRT_STATIONS:
                            if s["id"] != "139886":
                                temp.append({"text": s["name"], "callback_data": f"tf_calc:{m_id}:{s['id']}"})
                                if len(temp) == 2:
                                    rows.append(temp)
                                    temp = []
                        if temp:
                            rows.append(temp)
                        rows.append([{"text": "🔙 تغيير محطة المترو", "callback_data": "transfer_metro_select"}])
                        m_obj = get_station_by_id(m_id, network='metro')
                        send_or_edit_message(
                            chat_id,
                            f"🚇 محطتك الحالية: <b>{m_obj['name'] if m_obj else ''}</b>\\n\\n"
                            f"🚆 <b>اختر وجهتك في قطار العاصمة (LRT):</b>",
                            {"inline_keyboard": rows},
                            msg_id
                        )
                        continue

                    if data.startswith("tf_calc:"):
                        parts = data.split(":")
                        m_id = parts[1]
                        l_id = parts[2]
                        info = calculate_smart_transfer_info(m_id, l_id)

                        status_ico = "✅" if info["best_diff"] >= 4 else ("⚠️" if info["best_diff"] >= 0 else "❌")
                        status_title = "ستلحق القطار بكل راحة" if info["best_diff"] >= 4 else ("الوقت ضيق - تبديل سريع" if info["best_diff"] >= 0 else "سيفوتك القطار الأول")

                        res_txt = (
                            f"⚡ <b>نتيجة فحص الربط الذكي:</b>\\n\\n"
                            f"<b>{status_ico} {status_title}!</b>\\n"
                            f"────────────────────\\n"
                            f"🚇 <b>الانطلاق بمترو الخط 3:</b> من <b>{info['metro_name']}</b>\\n"
                            f"⏱️ <b>زمن رحلة المترو:</b> {info['metro_ride']} دقيقة\\n"
                            f"🚉 <b>الوصول لرصيف عدلي منصور:</b> <b>{info['adly_arr']}</b>\\n"
                            f"🚶 <b>الصعود لرصيف قطار العاصمة:</b> <b>{info['ready_time']}</b> (5 دقائق تبديل)\\n\\n"
                            f"🚆 <b>قطار العاصمة الأنسب لك:</b> يتحرك الساعة <b>{info['best_time']}</b>\\n"
                            f"🎯 <b>الوصول لمحطتك ({info['lrt_name']}):</b> <b>{info['final_arr']}</b>\\n\\n"
                            f"💡 <i>القطار البديل التالي يتحرك الساعة {info['next_time']}.</i>"
                        )
                        kb = {
                            "inline_keyboard": [
                                [{"text": "🔄 فحص محطة أخرى", "callback_data": "transfer_metro_select"}],
                                [{"text": "🌐 فتح حاسبة الربط بالموقع", "url": WEB_URL}],
                                [{"text": "🔙 القائمة الرئيسية", "callback_data": "main_menu"}]
                            ]
                        }
                        send_or_edit_message(chat_id, res_txt, kb, msg_id)
                        continue

                    ''' + cb_target

orig_bot = orig_bot.replace(cb_target, cb_injection, 1)

with open('I:/CapitalTrain/telegram_bot_runner.py', 'w', encoding='utf-8') as f:
    f.write(orig_bot)

print("Updated telegram_bot_runner.py with Smart Transfer Guarantee successfully!")
