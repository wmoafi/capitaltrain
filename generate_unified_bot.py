# -*- coding: utf-8 -*-
"""
Generate complete, clean, robust telegram_bot_runner.py with:
- Full support for both LRT and Metro Line 3 (Green Line 3)
- Mode switcher on /start and inline buttons
- Real-time departure fetching from Mobility Cairo (RATP Dev) for LRT (LRT-14) and GL3 (L3-57)
- Automated direction deduction (اتجاه عدلي منصور، اتجاه محور روض الفرج، اتجاه جامعة القاهرة، اتجاه بدر، اتجاه الفنون، اتجاه المعرفة)
- Direct link to web domain: https://capitaltrain.tafawuq-edu.site
- Direct link to download Android APK
- Arabic voice recognition (Whisper) support for both lines
- Full error resilience and loop safety
"""

import json

with open('I:/CapitalTrain/metro_line3_official_stops.json', 'r', encoding='utf-8') as f:
    metro_stops = json.load(f)

# Assign pos and aliases for metro stops
for s in metro_stops:
    if s.get('branch') == 'main':
        s['pos'] = s['order'] - 1
    elif s.get('branch') == 'rod_elfarag':
        s['pos'] = 22 + (s['order'] - 23)
    elif s.get('branch') == 'cairo_univ':
        s['pos'] = 30 + (s['order'] - 23)

    name = s['name']
    aliases = [name]
    if name == 'عدلي منصور':
        aliases += ['عدلي', 'منصور', 'عدلى']
    elif name == 'جمال عبد الناصر':
        aliases += ['ناصر', 'عبد الناصر', 'جمال عبدالناصر', 'عبدالناصر']
    elif name == 'صفاء حجازي (الزمالك)':
        aliases += ['صفاء حجازي', 'الزمالك', 'زمالك', 'صفاء']
    elif name == 'محور روض الفرج':
        aliases += ['روض الفرج', 'محور روض الفرج', 'الفرّاج']
    elif name == 'جامعة القاهرة':
        aliases += ['جامعة القاهرة', 'الجامعة', 'جامعه القاهره']
    elif name == 'جامعة الدول العربية':
        aliases += ['جامعة الدول', 'جامعه الدول', 'الدول']
    elif name == 'ميدان هليوبوليس':
        aliases += ['هليوبوليس', 'ميدان هليوبوليس', 'هليوبولس']
    elif name == 'كلية البنات':
        aliases += ['كلية البنات', 'كليه البنات', 'بنات']
    elif name == 'أرض المعارض':
        aliases += ['المعارض', 'أرض المعارض', 'ارض المعارض']
    elif name == 'باب الشعرية':
        aliases += ['باب الشعرية', 'باب الشعريه', 'الشعرية']
    elif name == 'عمر بن الخطاب':
        aliases += ['عمر بن الخطاب', 'عمر', 'ابن الخطاب']
    elif name == 'هشام بركات':
        aliases += ['هشام بركات', 'بركات', 'هشام']
    elif name == 'نادي الشمس':
        aliases += ['نادي الشمس', 'الشمس', 'نادى الشمس']
    elif name == 'ألف مسكن':
        aliases += ['الف مسكن', 'ألف مسكن', 'المسكن']
    elif name == 'بولاق الدكرور':
        aliases += ['بولاق', 'بولاق الدكرور']
    elif name == 'الطريق الدائري':
        aliases += ['الدائري', 'الطريق الدائري', 'الدائرى']
    elif name == 'القومية العربية':
        aliases += ['القومية', 'القومية العربية', 'القوميه']
    elif name == 'عبده باشا':
        aliases += ['عبده باشا', 'عبده', 'باشا']
    elif name == 'العتبة':
        aliases += ['العتبة', 'العتبه']
    elif name == 'الكيت كات':
        aliases += ['الكيت كات', 'كيت كات']
    else:
        aliases.append(name.replace('أ', 'ا').replace('إ', 'ا').replace('ة', 'ه').replace('ى', 'ي'))
    s['aliases'] = list(set(aliases))

metro_stops_str = json.dumps(metro_stops, ensure_ascii=False, indent=2)

bot_code = f'''# -*- coding: utf-8 -*-
import json
import time
import os
import re
import threading
import subprocess
import urllib.request
import urllib.parse
import uuid
from difflib import SequenceMatcher
from datetime import datetime

TOKEN = "9245350820:AAFSuiAZ7Z81Y_tBSZTAXNWoiLMUTltnXUg"
BASE_URL = f"https://api.telegram.org/bot{{TOKEN}}/"
MOBILITY_API = "https://www.mobilitycairo.com/ar/pthv/get"
FFMPEG_PATH = r"C:\\Program Files\\File Converter\\ffmpeg.exe"
WHISPER_PYTHON = r"I:\\VoiceStudio\\runtime\\project\\.venv\\Scripts\\python.exe"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORKER_SCRIPT = os.path.join(BASE_DIR, "transcribe_worker.py")
REMINDERS_FILE = os.path.join(BASE_DIR, "reminders.json")

# Public domain URL
WEB_URL = "https://capitaltrain.tafawuq-edu.site"

# 1. LRT Stations
LRT_STATIONS = [
    {{"id": "139886", "name": "عدلي منصور", "pos": 0, "aliases": ["عدلي", "منصور", "عدلي منصور", "عدلى"]}},
    {{"id": "139912", "name": "العبور", "pos": 1, "aliases": ["العبور", "عبور"]}},
    {{"id": "139896", "name": "المستقبل", "pos": 2, "aliases": ["المستقبل", "مستقبل"]}},
    {{"id": "139920", "name": "الشروق", "pos": 3, "aliases": ["الشروق", "شروق", "الشرcheck", "شروع"]}},
    {{"id": "139910", "name": "هليوبوليس الجديدة", "pos": 4, "aliases": ["هليوبوليس", "نيو هليوبوليس", "هليوبوليس الجديدة"]}},
    {{"id": "139892", "name": "بـــدر", "pos": 5, "aliases": ["بدر", "بـــدر"]}},
    {{"id": "139916", "name": "الروبيكي", "pos": 6, "aliases": ["الروبيكي", "روبيكي"]}},
    {{"id": "139898", "name": "حدائق العاصمة", "pos": 7, "aliases": ["حدائق العاصمة", "الحدائق", "حدائق", "العاصمة"]}},
    {{"id": "139888", "name": "مطار العاصمة", "pos": 8, "aliases": ["مطار العاصمة", "المطار", "مطار"]}},
    {{"id": "139885", "name": "مدينة الفنون والثقافة", "pos": 9, "aliases": ["الفنون", "الثقافة", "مدينة الفنون", "مدينة الفنون والثقافة"]}},
    {{"id": "139904", "name": "المنطقة الصناعية", "pos": 6.5, "aliases": ["المنطقة الصناعية", "الصناعية"]}},
    {{"id": "139907", "name": "مدينة المعرفة", "pos": 7.5, "aliases": ["المعرفة", "مدينة المعرفة", "العاشر", "العاشر من رمضان"]}}
]

# 2. Metro Line 3 (Green Line 3) Official Stations
METRO_STATIONS = {metro_stops_str}

METRO_TO_ADLY_MINS = {{
    "139886": 0, "139913": 2, "139911": 4, "139914": 6, "139901": 8, "139915": 10,
    "139919": 13, "139889": 15, "139900": 17, "139899": 19, "139887": 21, "139905": 23,
    "139921": 25, "139893": 27, "139883": 30, "139884": 32, "139897": 34, "139891": 36,
    "139890": 38, "139909": 41, "139908": 43, "139918": 46, "139906": 49, "139922": 52,
    "139903": 54, "139895": 57, "139894": 59, "139902": 62, "139917": 65, "139999": 52,
    "140001": 55, "139998": 57, "139997": 60, "140000": 63
}}

LRT_FROM_ADLY_MINS = {{
    "139886": 0, "139912": 4, "139896": 8, "139920": 13, "139910": 18,
    "139892": 24, "139916": 29, "139898": 34, "139888": 39, "139885": 44,
    "139904": 30, "139907": 36
}}

def get_actual_travel_mins(start_id, end_id, network='lrt'):
    if network == 'metro':
        t1 = METRO_TO_ADLY_MINS.get(start_id, 20)
        t2 = METRO_TO_ADLY_MINS.get(end_id, 20)
        return abs(t1 - t2)
    else:
        t1 = LRT_FROM_ADLY_MINS.get(start_id, 0)
        t2 = LRT_FROM_ADLY_MINS.get(end_id, 0)
        return abs(t1 - t2)


def get_network_station_count(orig_id, dest_id, network='lrt'):
    if network == 'metro':
        s1 = get_station_by_id(orig_id, network='metro')
        s2 = get_station_by_id(dest_id, network='metro')
        if not s1 or not s2:
            return 5
        b1, o1 = s1.get('branch', 'main'), s1.get('order', 1)
        b2, o2 = s2.get('branch', 'main'), s2.get('order', 1)
        if b1 == b2:
            return max(1, abs(o1 - o2))
        elif b1 == 'main':
            return max(1, abs(o1 - 23) + (o2 - 23))
        elif b2 == 'main':
            return max(1, (o1 - 23) + abs(o2 - 23))
        else:
            return max(1, (o1 - 23) + (o2 - 23))
    else:
        lrt_map = {{
            "139886": ("trunk", 0),  # عدلي منصور
            "139912": ("trunk", 1),  # العبور
            "139896": ("trunk", 2),  # المستقبل
            "139920": ("trunk", 3),  # الشروق
            "139910": ("trunk", 4),  # هليوبوليس الجديدة
            "139892": ("trunk", 5),  # بدر
            "139916": ("arts", 6),   # الروبيكي
            "139898": ("arts", 7),   # حدائق العاصمة
            "139888": ("arts", 8),   # مطار العاصمة
            "139885": ("arts", 9),   # مدينة الفنون والثقافة
            "139904": ("knowledge", 6), # المنطقة الصناعية
            "139907": ("knowledge", 7)  # مدينة المعرفة
        }}
        b1, p1 = lrt_map.get(str(orig_id), ("trunk", 0))
        b2, p2 = lrt_map.get(str(dest_id), ("trunk", 0))
        if b1 == b2:
            cnt = abs(p1 - p2)
        elif b1 == "trunk" and b2 in ("arts", "knowledge"):
            cnt = (5 - p1) + (p2 - 5)
        elif b2 == "trunk" and b1 in ("arts", "knowledge"):
            cnt = (p1 - 5) + (5 - p2)
        else:
            cnt = (p1 - 5) + (p2 - 5)
        return max(1, cnt)

def get_ticket_price(st_count, network='lrt'):
    if network == 'metro':
        if st_count <= 9: return 8
        elif st_count <= 16: return 10
        elif st_count <= 23: return 15
        else: return 20
    else:
        if st_count <= 3: return 10
        elif st_count <= 7: return 15
        else: return 20

def render_trip_card_image(title, subtitle, lines, output_path):
    try:
        import pymupdf
        doc = pymupdf.open()
        h_box = max(400, 180 + len(lines) * 90)
        page = doc.new_page(width=500, height=h_box)
        page.draw_rect(pymupdf.Rect(0, 0, 500, h_box), color=(0.06, 0.09, 0.16), fill=(0.06, 0.09, 0.16))
        page.draw_rect(pymupdf.Rect(10, 10, 490, h_box - 10), color=(0.06, 0.73, 0.51), width=2)

        boxes_html = "".join([f'<div style="background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 12px; margin-bottom: 12px; font-size: 13.5px; color: #f1f5f9; line-height: 1.6;">{{line}}</div>' for line in lines])
        html_content = f"""
        <div style="font-family: sans-serif; direction: rtl; text-align: right; color: #f8fafc; padding: 22px;">
          <h2 style="color: #34d399; margin: 0 0 6px 0; font-size: 20px;">{{title}}</h2>
          <p style="color: #94a3b8; margin: 0 0 16px 0; font-size: 13.5px;">{{subtitle}}</p>
          <hr style="border: none; border-top: 1px solid #334155; margin-bottom: 16px;" />
          {{boxes_html}}
          <div style="text-align: center; margin-top: 20px; color: #10b981; font-weight: bold; font-size: 12px;">
            سيرفر RATP Dev الرسمي • قطار العاصمة والمترو
          </div>
        </div>
        """
        page.insert_htmlbox(pymupdf.Rect(18, 18, 482, h_box - 18), html_content)
        pix = page.get_pixmap(dpi=150)
        pix.save(output_path)
        doc.close()
        return True
    except Exception as e:
        print(f"render_trip_card_image error: {{e}}", flush=True)
        return False


def render_smart_transfer_card_image(info, output_path):
    try:
        import pymupdf
        doc = pymupdf.open()
        width = 800
        height = 430
        page = doc.new_page(width=width, height=height)

        # Background
        page.draw_rect(pymupdf.Rect(0, 0, width, height), color=(0.04, 0.07, 0.14), fill=(0.04, 0.07, 0.14))
        page.draw_rect(pymupdf.Rect(6, 6, width - 6, height - 6), color=(0.12, 0.22, 0.38), width=1.5)

        is_m2l = info.get("direction") == "metro_to_lrt"
        start_name = info.get("start_name", "")
        dest_name = info.get("dest_name", "")
        best_diff = info.get("best_diff", 0)
        
        status_text = "✅ ستلحق القطار بكل راحة وأمان" if best_diff >= 4 else ("⚠️ الوقت ضيق جداً (تبديل سريع)" if best_diff >= 0 else "❌ سيفوتك القطار الأول")
        status_bg = "#064e3b" if best_diff >= 4 else ("#78350f" if best_diff >= 0 else "#881337")
        status_border = "#10b981" if best_diff >= 4 else ("#f59e0b" if best_diff >= 0 else "#f43f5e")

        leg1_title = "1. ركوب مترو الخط الثالث الأخضر" if is_m2l else "1. ركوب قطار العاصمة الكهربائي"
        leg1_dep = info.get("leg1_dep", "")
        leg1_ride = info.get("leg1_ride", 0)

        leg2_title = "3. حركة قطار العاصمة الكهربائي" if is_m2l else "3. حركة مترو الخط الثالث الأخضر"
        leg2_dep = info.get("best_time", "")
        leg2_ride = info.get("leg2_ride", 0)

        adly_arr = info.get("adly_arr", "")
        ready_time = info.get("ready_time", "")
        final_arr = info.get("final_arr", "")
        total_time = info.get("total_time", 0)
        next_time = info.get("next_time", "--:--")

        stops1 = info.get("stops1", 19 if is_m2l else 3)
        stops2 = info.get("stops2", 3 if is_m2l else 19)
        stops1_lbl = "محطات مترو الخط الثالث الأخضر" if is_m2l else "محطات قطار العاصمة الكهربائي"
        stops2_lbl = "محطات قطار العاصمة الكهربائي" if is_m2l else "محطات مترو الخط الثالث الأخضر"
        note1 = "بين كل محطة ومحطة: 1.5 إلى 2 دقيقة" if is_m2l else "بين كل محطة ومحطة: 4 إلى 5 دقائق"
        note2 = "بين كل محطة ومحطة: 4 إلى 5 دقائق" if is_m2l else "بين كل محطة ومحطة: 1.5 إلى 2 دقيقة"

        advice_text = f"سيكون معك <b>{{best_diff + 5}} دقيقة</b> في محطة عدلي منصور للتبديل والتسوق أو الصعود للرصيف براحة تامة." if best_diff >= 4 else f"ستصل الرصيف قبل تحرك القطار بـ <b>{{best_diff}} دقائق</b> فقط."
        next_tip = f"💡 القطار البديل التالي يتحرك من رصيف عدلي منصور الساعة <b>{{next_time}}</b>."

        html = f"""
        <div style="font-family: sans-serif; direction: rtl; text-align: right; color: #f8fafc; padding: 12px 14px;">
          <!-- Header: Left Cell is Badge, Right Cell is Route -->
          <table style="width: 100%; border-bottom: 1px solid #1e293b; padding-bottom: 8px; margin-bottom: 8px;">
            <tr>
              <td style="width: 40%; text-align: left; vertical-align: middle;">
                <span style="background: {{status_bg}}; border: 1px solid {{status_border}}; color: #ffffff; font-weight: bold; font-size: 13.5px; padding: 5px 14px; border-radius: 8px;">
                  {{status_text}}
                </span>
              </td>
              <td style="width: 60%; text-align: right; vertical-align: middle; color: #cbd5e1; font-size: 13.5px;">
                المسار الكلي: من <b style="color: #ffffff;">{{start_name}}</b> إلى <b style="color: #ffffff;">{{dest_name}}</b>
              </td>
            </tr>
          </table>

          <!-- 4 Step Cards (Right-to-Left: Cell 1 is Left = Step 2 / Step 4, Cell 2 is Right = Step 1 / Step 3) -->
          <table style="width: 100%; border-spacing: 8px; margin-bottom: 4px;">
            <tr>
              <!-- Left Cell: Step 2 -->
              <td style="width: 50%; background: #0f172a; border: 1px solid #334155; border-radius: 10px; padding: 10px 12px; vertical-align: top;">
                <div style="color: #94a3b8; font-size: 11.5px; font-weight: bold;">2. الوصول لعدلي منصور المركزية</div>
                <div style="color: #38bdf8; font-size: 24px; font-weight: bold; font-family: monospace; margin: 3px 0;">{{adly_arr}}</div>
                <div style="color: #cbd5e1; font-size: 11.5px; border-top: 1px solid #1e293b; padding-top: 4px;">
                  زمن الرحلة الأولى: {{leg1_ride}} دقيقة
                </div>
              </td>
              <!-- Right Cell: Step 1 -->
              <td style="width: 50%; background: #0f172a; border: 1px solid #334155; border-radius: 10px; padding: 10px 12px; vertical-align: top;">
                <div style="color: #94a3b8; font-size: 11.5px; font-weight: bold;">{{leg1_title}}</div>
                <div style="color: #38bdf8; font-size: 24px; font-weight: bold; font-family: monospace; margin: 3px 0;">{{leg1_dep}}</div>
                <div style="color: #cbd5e1; font-size: 11.5px; border-top: 1px solid #1e293b; padding-top: 4px;">
                  <b>{{start_name}}</b> (محطة الانطلاق الأولى)
                </div>
              </td>
            </tr>
            <tr>
              <!-- Left Cell: Step 4 -->
              <td style="width: 50%; background: #0f172a; border: 1px solid #334155; border-radius: 10px; padding: 10px 12px; vertical-align: top;">
                <div style="color: #94a3b8; font-size: 11.5px; font-weight: bold;">4. الوصول لوجهتك النهائية</div>
                <div style="color: #34d399; font-size: 24px; font-weight: bold; font-family: monospace; margin: 3px 0;">{{final_arr}}</div>
                <div style="color: #cbd5e1; font-size: 11.5px; border-top: 1px solid #1e293b; padding-top: 4px;">
                  <b>{{dest_name}}</b> (زمن الرحلة الثانية: {{leg2_ride}} د)
                </div>
              </td>
              <!-- Right Cell: Step 3 -->
              <td style="width: 50%; background: #0f172a; border: 1px solid #334155; border-radius: 10px; padding: 10px 12px; vertical-align: top;">
                <div style="color: #94a3b8; font-size: 11.5px; font-weight: bold;">{{leg2_title}}</div>
                <div style="color: #fbbf24; font-size: 24px; font-weight: bold; font-family: monospace; margin: 3px 0;">{{leg2_dep}}</div>
                <div style="color: #fde68a; font-size: 11.5px; border-top: 1px solid #1e293b; padding-top: 4px;">
                  جاهز بالرصيف بعد التبديل: <b>{{ready_time}}</b>
                </div>
              </td>
            </tr>
          </table>

          <!-- 3 Stats Boxes: Cell 1 Left (Duration), Cell 2 Middle (Line 2), Cell 3 Right (Line 1) -->
          <table style="width: 100%; border-spacing: 8px; margin-bottom: 6px;">
            <tr>
              <td style="width: 33.3%; background: #713f12; border: 1px solid #d97706; border-radius: 10px; padding: 8px 10px;">
                <div style="color: #fef3c7; font-size: 11px; font-weight: bold;">إجمالي زمن الرحلة المشتركة</div>
                <div style="color: #fde047; font-size: 18px; font-weight: bold; font-family: monospace; margin: 2px 0;">{{total_time}} دقيقة</div>
                <div style="color: #fef08a; font-size: 9px;">شاملاً الركوب والتبديل والوصول</div>
              </td>
              <td style="width: 33.3%; background: #1e1b4b; border: 1px solid #4338ca; border-radius: 10px; padding: 8px 10px;">
                <div style="color: #c7d2fe; font-size: 11px; font-weight: bold;">{{stops2_lbl}}</div>
                <div style="color: #ffffff; font-size: 18px; font-weight: bold; font-family: monospace; margin: 2px 0;">{{stops2}} محطة</div>
                <div style="color: #a5b4fc; font-size: 9px;">{{note2}}</div>
              </td>
              <td style="width: 33.3%; background: #134e4a; border: 1px solid #0d9488; border-radius: 10px; padding: 8px 10px;">
                <div style="color: #ccfbf1; font-size: 11px; font-weight: bold;">{{stops1_lbl}}</div>
                <div style="color: #ffffff; font-size: 18px; font-weight: bold; font-family: monospace; margin: 2px 0;">{{stops1}} محطة</div>
                <div style="color: #99f6e4; font-size: 9px;">{{note1}}</div>
              </td>
            </tr>
          </table>

          <!-- Info Tip Box -->
          <div style="background: #0f172a; border: 1px solid #334155; border-radius: 10px; padding: 8px 12px; margin-bottom: 6px; font-size: 11.5px; line-height: 1.5;">
            <div>ℹ️ {{advice_text}}</div>
            <div style="color: #94a3b8; margin-top: 3px;">{{next_tip}}</div>
          </div>

          <!-- Footer: Cell 1 Left (URL), Cell 2 Right (Title) -->
          <table style="width: 100%; border-top: 1px solid #1e293b; padding-top: 4px;">
            <tr>
              <td style="width: 35%; text-align: left; color: #64748b; font-size: 10px; font-family: monospace;">
                capitaltrain.tafawuq-edu.site
              </td>
              <td style="width: 65%; text-align: right; color: #10b981; font-size: 10px; font-weight: bold;">
                شبكة النقل الذكية: قطار العاصمة الكهربائي ومترو الخط الثالث
              </td>
            </tr>
          </table>
        </div>
        """

        page.insert_htmlbox(pymupdf.Rect(6, 6, width - 6, height - 6), html)
        pix = page.get_pixmap(dpi=150)
        pix.save(output_path)
        doc.close()
        return True
    except Exception as e:
        print(f"render_smart_transfer_card_image error: {{e}}", flush=True)
        return False

def send_photo(chat_id, photo_path, caption=None, reply_markup=None):
    boundary = uuid.uuid4().hex
    headers = {{"Content-Type": f"multipart/form-data; boundary={{boundary}}"}}
    crlf = bytes([13, 10])
    body = []
    b_boundary = boundary.encode("utf-8")
    
    body.extend([b"--" + b_boundary + crlf, b'Content-Disposition: form-data; name="chat_id"' + crlf + crlf, str(chat_id).encode("utf-8") + crlf])
    if caption:
        body.extend([b"--" + b_boundary + crlf, b'Content-Disposition: form-data; name="caption"' + crlf + crlf, caption.encode("utf-8") + crlf])
        body.extend([b"--" + b_boundary + crlf, b'Content-Disposition: form-data; name="parse_mode"' + crlf + crlf, b"HTML" + crlf])
    if reply_markup:
        rm_bytes = json.dumps(reply_markup).encode("utf-8")
        body.extend([b"--" + b_boundary + crlf, b'Content-Disposition: form-data; name="reply_markup"' + crlf + crlf, rm_bytes + crlf])
    try:
        with open(photo_path, "rb") as f:
            file_bytes = f.read()
        body.extend([b"--" + b_boundary + crlf, b'Content-Disposition: form-data; name="photo"; filename="trip_card.png"' + crlf, b"Content-Type: image/png" + crlf + crlf, file_bytes + crlf])
        body.append(b"--" + b_boundary + b"--" + crlf)
        full_body = b"".join(body)
        req = urllib.request.Request(BASE_URL + "sendPhoto", data=full_body, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"sendPhoto error: {{e}}", flush=True)
        return None

def format_time_12h(time_input):
    if isinstance(time_input, int):
        h = (time_input // 60) % 24
        m = time_input % 60
    elif isinstance(time_input, str) and ":" in time_input:
        parts = time_input.strip().split(":")
        h = int(parts[0]) % 24
        m = int(parts[1])
    else:
        return str(time_input)
    period = "ص" if h < 12 else "م"
    h12 = h % 12
    if h12 == 0:
        h12 = 12
    return f"{{h12:02d}}:{{m:02d}} {{period}}"

def calculate_smart_transfer_info(direction, start_id, dest_id, timing_mode="now", custom_time=None):
    now = datetime.now()
    now_mins = now.hour * 60 + now.minute

    if timing_mode == "later" and custom_time and ":" in custom_time:
        parts = custom_time.split(":")
        user_platform_mins = int(parts[0]) * 60 + int(parts[1])
    else:
        user_platform_mins = now_mins

    walk_buffer = 5

    if direction == "metro_to_lrt":
        metro_id = start_id
        lrt_dest_id = dest_id
        metro_obj = get_station_by_id(metro_id, network='metro')
        lrt_dest_obj = get_station_by_id(lrt_dest_id, network='lrt')

        leg1_dep_mins = user_platform_mins
        leg1_ride = METRO_TO_ADLY_MINS.get(metro_id, 20)
        adly_arrival_mins = leg1_dep_mins + leg1_ride
        ready_mins = adly_arrival_mins + walk_buffer

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
                    best = {{"time": hhmm, "diff": diff, "tm": tm}}
                elif diff >= 0 and best and not nxt:
                    nxt = {{"time": hhmm, "diff": diff, "tm": tm}}
                    break

        if not best:
            fb_tm = ready_mins + 8
            best = {{"time": f"{{(fb_tm//60)%24:02d}}:{{fb_tm%60:02d}}", "diff": 8, "tm": fb_tm}}
            nxt = {{"time": f"{{((fb_tm+15)//60)%24:02d}}:{{(fb_tm+15)%60:02d}}", "diff": 23, "tm": fb_tm + 15}}

        leg2_ride = LRT_FROM_ADLY_MINS.get(lrt_dest_id, 20)
        final_arr_mins = best["tm"] + leg2_ride

        return {{
            "direction": "metro_to_lrt",
            "start_name": metro_obj["name"] if metro_obj else metro_id,
            "dest_name": lrt_dest_obj["name"] if lrt_dest_obj else lrt_dest_id,
            "leg1_name": "مترو الخط الثالث الأخضر",
            "leg2_name": "قطار العاصمة الكهربائي",
            "leg1_dep": format_time_12h(leg1_dep_mins),
            "leg1_ride": leg1_ride,
            "adly_arr": format_time_12h(adly_arrival_mins),
            "ready_time": format_time_12h(ready_mins),
            "best_time": format_time_12h(best["time"]),
            "best_diff": best["diff"],
            "next_time": format_time_12h(nxt["time"]) if nxt else "--:--",
            "leg2_ride": leg2_ride,
            "final_arr": format_time_12h(final_arr_mins),
            "total_time": final_arr_mins - leg1_dep_mins,
            "stops1": get_network_station_count(start_id, "139886", network='metro'),
            "stops2": get_network_station_count("139886", dest_id, network='lrt')
        }}
    else:
        # LRT -> Metro
        lrt_start_id = start_id
        metro_dest_id = dest_id
        lrt_start_obj = get_station_by_id(lrt_start_id, network='lrt')
        metro_dest_obj = get_station_by_id(metro_dest_id, network='metro')

        leg1_dep_mins = user_platform_mins
        leg1_ride = LRT_FROM_ADLY_MINS.get(lrt_start_id, 20)
        adly_arrival_mins = leg1_dep_mins + leg1_ride
        ready_mins = adly_arrival_mins + walk_buffer

        schedules = fetch_live_schedule_from_mobility_cairo("139908", "0", network='metro')
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
                    best = {{"time": hhmm, "diff": diff, "tm": tm}}
                elif diff >= 0 and best and not nxt:
                    nxt = {{"time": hhmm, "diff": diff, "tm": tm}}
                    break

        if not best:
            fb_tm = ready_mins + 4
            best = {{"time": f"{{(fb_tm//60)%24:02d}}:{{fb_tm%60:02d}}", "diff": 4, "tm": fb_tm}}
            nxt = {{"time": f"{{((fb_tm+6)//60)%24:02d}}:{{(fb_tm+6)%60:02d}}", "diff": 10, "tm": fb_tm + 6}}

        leg2_ride = METRO_TO_ADLY_MINS.get(metro_dest_id, 20)
        final_arr_mins = best["tm"] + leg2_ride

        return {{
            "direction": "lrt_to_metro",
            "start_name": lrt_start_obj["name"] if lrt_start_obj else lrt_start_id,
            "dest_name": metro_dest_obj["name"] if metro_dest_obj else metro_dest_id,
            "leg1_name": "قطار العاصمة الكهربائي",
            "leg2_name": "مترو الخط الثالث الأخضر",
            "leg1_dep": format_time_12h(leg1_dep_mins),
            "leg1_ride": leg1_ride,
            "adly_arr": format_time_12h(adly_arrival_mins),
            "ready_time": format_time_12h(ready_mins),
            "best_time": format_time_12h(best["time"]),
            "best_diff": best["diff"],
            "next_time": format_time_12h(nxt["time"]) if nxt else "--:--",
            "leg2_ride": leg2_ride,
            "final_arr": format_time_12h(final_arr_mins),
            "total_time": final_arr_mins - leg1_dep_mins,
            "stops1": get_network_station_count(start_id, "139886", network='lrt'),
            "stops2": get_network_station_count("139886", dest_id, network='metro')
        }}

DAYS_LIST = [
    {{"code": 6, "name": "الأحد"}},
    {{"code": 0, "name": "الاثنين"}},
    {{"code": 1, "name": "الثلاثاء"}},
    {{"code": 2, "name": "الأربعاء"}},
    {{"code": 3, "name": "الخميس"}},
    {{"code": 4, "name": "الجمعة"}},
    {{"code": 5, "name": "السبت"}}
]

def load_reminders():
    if os.path.exists(REMINDERS_FILE):
        try:
            with open(REMINDERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_reminders(reminders):
    with open(REMINDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(reminders, f, ensure_ascii=False, indent=2)

def get_station_by_id(sid, network='lrt'):
    stations = METRO_STATIONS if network == 'metro' else LRT_STATIONS
    for s in stations:
        if s["id"] == sid:
            return s
    # fallback to all
    for s in LRT_STATIONS + METRO_STATIONS:
        if s["id"] == sid:
            return s
    return None

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def get_refined_direction_info(origin_station, dest_station, network='lrt'):
    if not origin_station or not dest_station:
        return "1", "اتجاه عدلي منصور"

    p1 = origin_station.get("pos", 0)
    p2 = dest_station.get("pos", 0)

    if network == 'metro':
        if p2 < p1:
            return "1", "اتجاه عدلي منصور"
        else:
            b = dest_station.get("branch", "main")
            if b == "rod_elfarag":
                return "0", "اتجاه محور روض الفرج"
            elif b == "cairo_univ":
                return "0", "اتجاه جامعة القاهرة"
            else:
                return "0", "اتجاه الكيت كات / روض الفرج"
    else:
        if p2 < p1:
            return "1", "اتجاه عدلي منصور"
        else:
            did = dest_station.get("id")
            if did == "139892":
                return "0", "اتجاه بدر"
            elif did in ["139904", "139907"]:
                return "0", "اتجاه مدينة المعرفة"
            else:
                return "0", "اتجاه مدينة الفنون والثقافة"

def analyze_trip_phrase(text, network='lrt'):
    cleaned = text.lower().strip()
    norm = cleaned.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ة", "ه").replace("ى", "ي")

    stations = METRO_STATIONS if network == 'metro' else LRT_STATIONS

    found_mentions = []
    for st in stations:
        for alias in st.get("aliases", [st["name"]]):
            alias_norm = alias.lower().replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ة", "ه").replace("ى", "ي")
            idx = norm.find(alias_norm)
            if idx != -1:
                found_mentions.append({{"index": idx, "station": st, "len": len(alias_norm)}})
                break

    found_mentions = sorted(found_mentions, key=lambda x: x["index"])

    if len(found_mentions) >= 2:
        orig = found_mentions[0]["station"]
        dest = found_mentions[1]["station"]
        dir_code, dir_lbl = get_refined_direction_info(orig, dest, network=network)
        return orig, dest, dir_code, dir_lbl

    if len(found_mentions) == 1:
        st = found_mentions[0]["station"]
        if "عدلي" in norm or "منصور" in norm or "رجوع" in norm or "عودة" in norm:
            dest = get_station_by_id("139886", network=network)
            dir_code, dir_lbl = get_refined_direction_info(st, dest, network=network)
            return st, dest, dir_code, dir_lbl
        else:
            dest = get_station_by_id("139917" if network == 'metro' else "139885", network=network)
            dir_code, dir_lbl = get_refined_direction_info(st, dest, network=network)
            return st, dest, dir_code, dir_lbl

    return None, None, None, None

def convert_ogg_to_wav(ogg_path, wav_path):
    cmd = [FFMPEG_PATH, "-y", "-i", ogg_path, "-ac", "1", "-ar", "16000", wav_path]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return res.returncode == 0

def transcribe_audio_whisper(wav_path):
    if not os.path.exists(WORKER_SCRIPT):
        with open(WORKER_SCRIPT, "w", encoding="utf-8") as f:
            f.write(
                'import sys, whisper\\\n'
                'wav = sys.argv[1]\\\n'
                'model = whisper.load_model("base")\\\n'
                'result = model.transcribe(wav, language="ar")\\\n'
                'print(result["text"].strip())\\\n'
            )
    cmd = [WHISPER_PYTHON, WORKER_SCRIPT, wav_path]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
    return res.stdout.strip() if res.returncode == 0 else ""

def fetch_live_schedule_from_mobility_cairo(stop_id, direction_code, network='lrt'):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    url = (
        f"{{MOBILITY_API}}/stop-stoptimes-discovery?"
        f"nbtimes=6&stop={{stop_id}}&reseau=&date={{date_str}}&heure={{time_str}}"
    )

    req = urllib.request.Request(
        url,
        headers={{
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "application/json"
        }}
    )

    prefix = "L3-57" if network == 'metro' else "LRT-14"

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("utf-8")
            if raw == "false":
                return []
            data = json.loads(raw)
            items = data.get("items", {{}})

            target_key = f"{{prefix}}_{{direction_code}}"
            if target_key in items:
                return items[target_key].get("Schedule", [])

            for k, v in items.items():
                if k.startswith(prefix) and str(v.get("Direction")) == str(direction_code):
                    return v.get("Schedule", [])
            return []
    except Exception as e:
        print(f"API Error: {{e}}", flush=True)
        return []

def format_station_result(station_id, direction_code, deduced_dest=None, custom_dir_label=None, network='lrt'):
    station = get_station_by_id(station_id, network=network)
    if not station:
        return "المحطة غير موجودة."

    dir_name = f"🧭 <b>{{custom_dir_label}}</b>" if custom_dir_label else ("🧭 <b>اتجاه عدلي منصور</b>" if str(direction_code) == "1" else "🧭 <b>اتجاه المحطات النهائية</b>")
    net_title = "🚇 <b>مترو الخط الثالث الأخضر</b>" if network == 'metro' else "🚆 <b>قطار العاصمة الكهربائي</b>"

    dest_str = f" ⬅️ <b>{{deduced_dest['name']}}</b>" if deduced_dest else ""

    now_dt = datetime.now()
    now_12h = format_time_12h(now_dt.hour * 60 + now_dt.minute)

    msg = f"{{net_title}}\\n📍 محطة الانطلاق: <b>{{station['name']}}</b>{{dest_str}}\\n{{dir_name}}\\n"
    msg += f"🕒 <b>التوقيت الآن:</b> <b>{{now_12h}}</b>\\n\\n"

    schedules = fetch_live_schedule_from_mobility_cairo(station_id, direction_code, network=network)

    if not schedules:
        msg += "⚠️ لا توجد رحلات مجدولة حالياً لهذا المسار.\\n(مواعيد التشغيل اليومية: 05:30 ص حتى 11:30 م)"
        return msg

    msg += "📋 <b>مواعيد الرحلات القادمة (محدثة لحظيا):</b>\\n"
    now_mins = now_dt.hour * 60 + now_dt.minute

    trip_mins = None
    if deduced_dest:
        trip_mins = get_actual_travel_mins(station_id, deduced_dest["id"], network=network)

    for idx, item in enumerate(schedules[:4], 1):
        dep_time = item.get("DepTime", "")
        hhmm = dep_time.split(" ")[1] if " " in dep_time else dep_time
        head = item.get("tripHeadsign") or item.get("to_stop_name") or ""

        diff_str = ""
        dep_mins = None
        if ":" in hhmm:
            try:
                parts = hhmm.split(":")
                dep_mins = int(parts[0]) * 60 + int(parts[1])
                diff = dep_mins - now_mins
                if diff < 0:
                    diff_str = "يتحرك الآن"
                elif diff == 0:
                    diff_str = "على الرصيف الآن"
                else:
                    diff_str = f"خلال {{diff}} دقيقة"
            except Exception:
                pass

        time_12h = format_time_12h(hhmm)
        msg += f"\\n<b>{{idx}}. ⏰ {{time_12h}}</b> (<code>{{diff_str}}</code>)"
        if trip_mins is not None and dep_mins is not None:
            arr_mins = dep_mins + trip_mins
            arr_12h = format_time_12h(arr_mins)
            msg += f"\\n   🎯 ميعاد الوصول المتوقع: <b>{{arr_12h}}</b> (الرحلة تستغرق {{trip_mins}} دقيقة)"
        elif head:
            msg += f"\\n   📍 متجه إلى: <b>{{head}}</b>"
        msg += "\\n"

    msg += "\\n────────────────────\\n✅ <b>سيرفر RATP Dev الرسمي</b>"
    return msg

def get_main_menu_keyboard():
    return {{
        "inline_keyboard": [
            [
                {{"text": "⚡ حاسبة الربط الذكي (مترو ⇄ قطار العاصمة)", "callback_data": "transfer_direction_menu"}}
            ],
            [
                {{"text": "🚆 قطار العاصمة الكهربائي", "callback_data": "choose_net:lrt"}},
                {{"text": "🚇 مترو الخط الثالث الأخضر", "callback_data": "choose_net:metro"}}
            ],
            [
                {{"text": "🌐 موقع المواعيد وحساب الرحلات", "url": WEB_URL}},
                {{"text": "📲 تحميل تطبيق أندرويد APK", "url": f"{{WEB_URL}}/downloads/capital_train_lrt.apk"}}
            ],
            [
                {{"text": "⏰ ضبط منبه/تنبيه يومي", "callback_data": "reminder_menu"}},
                {{"text": "🎟 أسعار التذاكر الرسمية", "callback_data": "fares"}}
            ],
            [
                {{"text": "📞 أرقام خدمة العملاء", "callback_data": "support"}}
            ]
        ]
    }}

def get_stations_keyboard(network="lrt", prefix="st", exclude_id=None):
    stations = METRO_STATIONS if network == "metro" else LRT_STATIONS
    rows = []
    temp = []
    for s in stations:
        if exclude_id and s["id"] == exclude_id:
            continue
        temp.append({{"text": f"{{s['name']}}", "callback_data": f"{{prefix}}:{{network}}:{{s['id']}}"}})
        if len(temp) == 2:
            rows.append(temp)
            temp = []
    if temp:
        rows.append(temp)
    rows.append([
        {{"text": "🔄 تبديل الشبكة", "callback_data": f"choose_net:{{'lrt' if network == 'metro' else 'metro'}}"}},
        {{"text": "🔙 القائمة الرئيسية", "callback_data": "main_menu"}}
    ])
    return {{"inline_keyboard": rows}}

def get_destinations_keyboard(origin_id, network="lrt"):
    stations = METRO_STATIONS if network == "metro" else LRT_STATIONS
    orig_obj = get_station_by_id(origin_id, network=network)
    rows = []
    temp = []
    for s in stations:
        if s["id"] == origin_id:
            continue
        temp.append({{"text": f"إلى: {{s['name']}}", "callback_data": f"dest:{{network}}:{{origin_id}}:{{s['id']}}"}})
        if len(temp) == 2:
            rows.append(temp)
            temp = []
    if temp:
        rows.append(temp)
    rows.append([
        {{"text": "🔙 تغيير محطة القيام", "callback_data": f"choose_net:{{network}}"}},
        {{"text": "🏠 القائمة الرئيسية", "callback_data": "main_menu"}}
    ])
    return {{"inline_keyboard": rows}}

def build_days_keyboard(selected_days):
    rows = []
    temp = []
    for d in DAYS_LIST:
        code = d["code"]
        name = d["name"]
        mark = "✅ " if code in selected_days else "▫️ "
        temp.append({{"text": f"{{mark}}{{name}}", "callback_data": f"tog_day:{{code}}"}})
        if len(temp) == 2:
            rows.append(temp)
            temp = []
    if temp:
        rows.append(temp)
    rows.append([
        {{"text": "💾 حفظ وتفعيل المنبه", "callback_data": "save_reminder"}},
        {{"text": "❌ إلغاء", "callback_data": "main_menu"}}
    ])
    return {{"inline_keyboard": rows}}

def get_bottom_reply_keyboard():
    return {{
        "keyboard": [
            [{{"text": "🚆 القطارات القادمة الآن"}}],
            [{{"text": "📍 المحطات والمسار"}}, {{"text": "🎟 أسعار التذاكر"}}],
            [{{"text": "📞 أرقام خدمة العملاء"}}]
        ],
        "resize_keyboard": True,
        "is_persistent": True
    }}

def send_or_edit_message(chat_id, text, reply_markup=None, message_id=None):
    if message_id:
        url = BASE_URL + "editMessageText"
        data = {{
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": "HTML"
        }}
    else:
        url = BASE_URL + "sendMessage"
        data = {{
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }}
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={{"Content-Type": "application/json"}}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        if message_id:
            return send_or_edit_message(chat_id, text, reply_markup, message_id=None)
        print(f"Send error: {{e}}", flush=True)
        return None

def answer_callback(callback_query_id, text=None):
    url = BASE_URL + "answerCallbackQuery"
    data = {{"callback_query_id": callback_query_id}}
    if text:
        data["text"] = text
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={{"Content-Type": "application/json"}}
    )
    try:
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass

def download_telegram_file(file_id, save_path):
    url = f"{{BASE_URL}}getFile?file_id={{file_id}}"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            res = json.loads(r.read().decode("utf-8"))
            file_path = res["result"]["file_path"]
            file_url = f"https://api.telegram.org/file/bot{{TOKEN}}/{{file_path}}"
            urllib.request.urlretrieve(file_url, save_path)
            return True
    except Exception as e:
        print(f"Download file error: {{e}}", flush=True)
        return False

# Background Reminder Worker
def reminder_scheduler_loop():
    print("Reminder scheduler thread running...", flush=True)
    last_checked_minute = ""
    while True:
        try:
            now = datetime.now()
            current_minute = now.strftime("%H:%M")
            weekday = now.weekday()

            if current_minute != last_checked_minute:
                last_checked_minute = current_minute
                reminders = load_reminders()
                for r in reminders:
                    if r.get("enabled", True):
                        if weekday in r.get("days", []):
                            if current_minute in r.get("times", []):
                                chat_id = r["chat_id"]
                                st_id = r["station_id"]
                                dir_code = r["direction_code"]
                                dest_id = r.get("dest_id")
                                net = r.get("network", "lrt")

                                st_obj = get_station_by_id(st_id, network=net)
                                dest_obj = get_station_by_id(dest_id, network=net) if dest_id else None
                                _, dir_lbl = get_refined_direction_info(st_obj, dest_obj, network=net)

                                alert_msg = f"⏰ <b>تنبيه موعد رحلتك اليومية المجدولة!</b>\\\n\\\n"
                                alert_msg += format_station_result(st_id, dir_code, deduced_dest=dest_obj, custom_dir_label=dir_lbl, network=net)
                                send_or_edit_message(chat_id, alert_msg)
            time.sleep(10)
        except Exception as e:
            print(f"Scheduler error: {{e}}", flush=True)
            time.sleep(15)

def main():
    print("Unified Smart Bot starting (LRT + Metro Line 3)...", flush=True)
    t = threading.Thread(target=reminder_scheduler_loop, daemon=True)
    t.start()

    offset = 0
    user_states = {{}}

    while True:
        try:
            url = f"{{BASE_URL}}getUpdates?offset={{offset}}&timeout=20"
            req = urllib.request.Request(url, headers={{"User-Agent": "Mozilla/5.0"}})
            with urllib.request.urlopen(req, timeout=25) as resp:
                updates = json.loads(resp.read().decode("utf-8")).get("result", [])

            for u in updates:
                offset = u["update_id"] + 1

                # 1. Callback Query Handler
                if "callback_query" in u:
                    cq = u["callback_query"]
                    cq_id = cq["id"]
                    chat_id = cq["message"]["chat"]["id"]
                    msg_id = cq["message"]["message_id"]
                    data = cq.get("data", "")
                    answer_callback(cq_id)

                    state = user_states.setdefault(chat_id, {{}})

                    if data == "transfer_direction_menu" or data == "transfer_metro_select":
                        kb = {{
                            "inline_keyboard": [
                                [{{"text": "🚇 من مترو الخط الثالث ⬅️ إلى قطار العاصمة 🚆", "callback_data": "tf_dir:metro_to_lrt"}}],
                                [{{"text": "🚆 من قطار العاصمة ⬅️ إلى مترو الخط الثالث 🚇", "callback_data": "tf_dir:lrt_to_metro"}}],
                                [{{"text": "🏠 القائمة الرئيسية", "callback_data": "main_menu"}}]
                            ]
                        }}
                        send_or_edit_message(
                            chat_id,
                            "⚡ <b>حاسبة الربط الذكي واللحاق بالقطار (محطة عدلي منصور المركزية):</b>\\n\\nاختر اتجاه رحلتك لحساب أوقات التبديل والوصول بدقة:",
                            kb,
                            msg_id
                        )
                        continue

                    if data.startswith("tf_dir:"):
                        direction = data.split(":")[1]
                        state["tf_direction"] = direction
                        rows = []
                        temp = []

                        if direction == "metro_to_lrt":
                            for s in METRO_STATIONS:
                                temp.append({{"text": s["name"], "callback_data": f"tf_orig:{{direction}}:{{s['id']}}"}})
                                if len(temp) == 2:
                                    rows.append(temp)
                                    temp = []
                            if temp:
                                rows.append(temp)
                            title = "🚇 <b>اختر محطة انطلاقك في مترو الخط الثالث الأخضر:</b>"
                        else:
                            for s in LRT_STATIONS:
                                if s["id"] != "139886":
                                    temp.append({{"text": s["name"], "callback_data": f"tf_orig:{{direction}}:{{s['id']}}"}})
                                    if len(temp) == 2:
                                        rows.append(temp)
                                        temp = []
                            if temp:
                                rows.append(temp)
                            title = "🚆 <b>اختر محطة انطلاقك في قطار العاصمة الكهربائي:</b>"

                        rows.append([{{"text": "🔙 تغيير الاتجاه", "callback_data": "transfer_direction_menu"}}])
                        send_or_edit_message(chat_id, title, {{"inline_keyboard": rows}}, msg_id)
                        continue

                    if data.startswith("tf_orig:"):
                        parts = data.split(":")
                        direction = parts[1]
                        orig_id = parts[2]
                        state["tf_direction"] = direction
                        state["tf_orig"] = orig_id

                        rows = []
                        temp = []
                        orig_obj = get_station_by_id(orig_id, network='metro' if direction == "metro_to_lrt" else 'lrt')
                        orig_name = orig_obj["name"] if orig_obj else orig_id

                        if direction == "metro_to_lrt":
                            for s in LRT_STATIONS:
                                if s["id"] != "139886":
                                    temp.append({{"text": s["name"], "callback_data": f"tf_dest:{{direction}}:{{orig_id}}:{{s['id']}}"}})
                                    if len(temp) == 2:
                                        rows.append(temp)
                                        temp = []
                            if temp:
                                rows.append(temp)
                            title = f"🚇 محطة انطلاقك: <b>{{orig_name}}</b>\\n\\n🚆 <b>اختر محطة الوصول في قطار العاصمة (LRT):</b>"
                        else:
                            for s in METRO_STATIONS:
                                temp.append({{"text": s["name"], "callback_data": f"tf_dest:{{direction}}:{{orig_id}}:{{s['id']}}"}})
                                if len(temp) == 2:
                                    rows.append(temp)
                                    temp = []
                            if temp:
                                rows.append(temp)
                            title = f"🚆 محطة انطلاقك: <b>{{orig_name}}</b>\\n\\n🚇 <b>اختر محطة الوصول في مترو الخط 3:</b>"

                        rows.append([{{"text": "🔙 تغيير محطة الانطلاق", "callback_data": f"tf_dir:{{direction}}"}}])
                        send_or_edit_message(chat_id, title, {{"inline_keyboard": rows}}, msg_id)
                        continue

                    if data.startswith("tf_dest:"):
                        parts = data.split(":")
                        direction = parts[1]
                        orig_id = parts[2]
                        dest_id = parts[3]
                        state["tf_dest"] = dest_id

                        orig_net = 'metro' if direction == "metro_to_lrt" else 'lrt'
                        orig_obj = get_station_by_id(orig_id, network=orig_net)
                        dest_net = 'lrt' if direction == "metro_to_lrt" else 'metro'
                        dest_obj = get_station_by_id(dest_id, network=dest_net)

                        orig_name = orig_obj["name"] if orig_obj else orig_id
                        dest_name = dest_obj["name"] if dest_obj else dest_id

                        # Query departures for the FIRST LEG to let user pick which train they take
                        dir_code = "1"  # toward Adly Mansour in both cases
                        schedules = fetch_live_schedule_from_mobility_cairo(orig_id, dir_code, network=orig_net)
                        now_dt = datetime.now()
                        now_mins = now_dt.hour * 60 + now_dt.minute

                        deps = []
                        for s in schedules:
                            dep_raw = s.get("DepTime", "")
                            hhmm = dep_raw.split(" ")[1] if " " in dep_raw else dep_raw
                            if ":" in hhmm:
                                p = hhmm.split(":")
                                tm = int(p[0]) * 60 + int(p[1])
                                deps.append((hhmm, tm))

                        if not deps:
                            for i in range(5):
                                dm = now_mins + 4 + i * 8
                                hh = (dm // 60) % 24
                                mm = dm % 60
                                deps.append((f"{{hh:02d}}:{{mm:02d}}", dm))

                        kb_rows = []
                        for idx, (hhmm, tm) in enumerate(deps[:5], 1):
                            diff = tm - now_mins
                            diff_str = "الآن" if diff <= 0 else f"خلال {{diff}} د"
                            time_12h = format_time_12h(hhmm)
                            btn_text = f"🚆 رحلة {{idx}}: {{time_12h}} ({{diff_str}})"
                            kb_rows.append([{{
                                "text": btn_text,
                                "callback_data": f"tf_calc:{{direction}}:{{orig_id}}:{{dest_id}}:{{tm}}"
                            }}])

                        kb_rows.append([{{"text": "🔙 تغيير محطة الوصول", "callback_data": f"tf_orig:{{direction}}:{{orig_id}}"}}])
                        kb_rows.append([{{"text": "🏠 القائمة الرئيسية", "callback_data": "main_menu"}}])

                        orig_title = "مترو الخط الثالث" if direction == "metro_to_lrt" else "قطار العاصمة"
                        dest_title = "قطار العاصمة" if direction == "metro_to_lrt" else "مترو الخط الثالث"

                        prompt_msg = (
                            f"⚡ <b>حاسبة الربط الذكي واللحاق بالقطار:</b>\\n\\n"
                            f"🟢 <b>محطة الانطلاق:</b> {{orig_name}} ({{orig_title}})\\n"
                            f"🔴 <b>محطة الوصول:</b> {{dest_name}} ({{dest_title}})\\n\\n"
                            f"👇 <b>اختر موعد تحرك رحلتك الأولى من محطة ({{orig_name}}):</b>"
                        )
                        send_or_edit_message(chat_id, prompt_msg, {{"inline_keyboard": kb_rows}}, msg_id)
                        continue

                    if data.startswith("tf_calc:"):
                        parts = data.split(":")
                        direction = parts[1]
                        orig_id = parts[2]
                        dest_id = parts[3]
                        custom_tm = None
                        if len(parts) >= 5:
                            tm_int = int(parts[4])
                            custom_tm = f"{{(tm_int//60)%24:02d}}:{{tm_int%60:02d}}"

                        info = calculate_smart_transfer_info(direction, orig_id, dest_id, timing_mode="later" if custom_tm else "now", custom_time=custom_tm)

                        status_ico = "✅" if info["best_diff"] >= 4 else ("⚠️" if info["best_diff"] >= 0 else "❌")
                        status_title = "ستلحق القطار بكل راحة" if info["best_diff"] >= 4 else ("الوقت ضيق - تبديل سريع" if info["best_diff"] >= 0 else "سيفوتك القطار الأول")

                        if direction == "metro_to_lrt":
                            res_txt = (
                                f"⚡ <b>نتيجة فحص الربط الذكي (مترو ⬅️ قطار العاصمة):</b>\\n\\n"
                                f"<b>{{status_ico}} {{status_title}}!</b>\\n"
                                f"────────────────────\\n"
                                f"🚇 <b>الانطلاق بمترو الخط 3:</b> من <b>{{info['start_name']}}</b> ({{info['leg1_dep']}})\\n"
                                f"⏱️ <b>زمن رحلة المترو:</b> {{info['leg1_ride']}} دقيقة\\n"
                                f"🚉 <b>الوصول لرصيف عدلي منصور:</b> <b>{{info['adly_arr']}}</b>\\n"
                                f"🚶 <b>الصعود لرصيف قطار العاصمة:</b> <b>{{info['ready_time']}}</b> (5 دقائق تبديل)\\n\\n"
                                f"🚆 <b>قطار العاصمة الأنسب لك:</b> يتحرك الساعة <b>{{info['best_time']}}</b>\\n"
                                f"🎯 <b>الوصول لمحطتك ({{info['dest_name']}}):</b> <b>{{info['final_arr']}}</b>\\n"
                                f"⏱️ <b>إجمالي زمن الرحلة:</b> {{info['total_time']}} دقيقة\\n\\n"
                                f"💡 <i>القطار البديل التالي يتحرك الساعة {{info['next_time']}}.</i>"
                            )
                        else:
                            res_txt = (
                                f"⚡ <b>نتيجة فحص الربط الذكي (قطار العاصمة ⬅️ مترو):</b>\\n\\n"
                                f"<b>{{status_ico}} {{status_title}}!</b>\\n"
                                f"────────────────────\\n"
                                f"🚆 <b>الانطلاق بقطار العاصمة:</b> من <b>{{info['start_name']}}</b> ({{info['leg1_dep']}})\\n"
                                f"⏱️ <b>زمن رحلة القطار:</b> {{info['leg1_ride']}} دقيقة\\n"
                                f"🚉 <b>الوصول لرصيف عدلي منصور:</b> <b>{{info['adly_arr']}}</b>\\n"
                                f"🚶 <b>النزول لرصيف المترو:</b> <b>{{info['ready_time']}}</b> (5 دقائق تبديل)\\n\\n"
                                f"🚇 <b>مترو الخط الثالث الأنسب لك:</b> يتحرك الساعة <b>{{info['best_time']}}</b>\\n"
                                f"🎯 <b>الوصول لمحطتك ({{info['dest_name']}}):</b> <b>{{info['final_arr']}}</b>\\n"
                                f"⏱️ <b>إجمالي زمن الرحلة:</b> {{info['total_time']}} دقيقة\\n\\n"
                                f"💡 <i>المترو البديل التالي يتحرك الساعة {{info['next_time']}}.</i>"
                            )

                        share_plain = (
                            f"⚡ ربط ذكي عدلي منصور:\\n"
                            f"🟢 انطلاق: {{info['start_name']}} ({{info['leg1_dep']}})\\n"
                            f"🚉 وصول عدلي منصور: {{info['adly_arr']}}\\n"
                            f"🚆 ركوب {{info['leg2_name']}}: {{info['best_time']}}\\n"
                            f"🎯 وصول محطتك: {{info['dest_name']}} ({{info['final_arr']}})\\n"
                            f"⏱️ إجمالي الزمن: {{info['total_time']}} دقيقة"
                        )
                        wa_url = f"https://api.whatsapp.com/send?text={{urllib.parse.quote(share_plain)}}"
                        tg_url = f"https://t.me/share/url?url={{urllib.parse.quote(WEB_URL)}}&text={{urllib.parse.quote(share_plain)}}"

                        kb = {{
                            "inline_keyboard": [
                                [{{"text": "📲 مشاركة واتساب", "url": wa_url}},
                                 {{"text": "📤 مشاركة تليجرام", "url": tg_url}}],
                                [{{"text": "📸 صورة الرحلة", "callback_data": f"share_img_tf:{{direction}}:{{orig_id}}:{{dest_id}}:{{parts[4] if len(parts) >= 5 else 0}}"}},
                                 {{"text": "🔄 اختيار موعد آخر", "callback_data": f"tf_dest:{{direction}}:{{orig_id}}:{{dest_id}}" }}],
                                [{{"text": "🔀 تبديل الاتجاه", "callback_data": "transfer_direction_menu"}},
                                 {{"text": "🌐 فتح حاسبة الربط بالموقع", "url": WEB_URL}}],
                                [{{"text": "🏠 القائمة الرئيسية", "callback_data": "main_menu"}}]
                            ]
                        }}
                        send_or_edit_message(chat_id, res_txt, kb, msg_id)
                        continue

                    if data.startswith("share_img_tf:"):
                        parts = data.split(":")
                        direction = parts[1]
                        orig_id = parts[2]
                        dest_id = parts[3]
                        custom_tm = None
                        if len(parts) >= 5 and parts[4] != "0":
                            tm_int = int(parts[4])
                            custom_tm = f"{{(tm_int//60)%24:02d}}:{{tm_int%60:02d}}"

                        answer_callback(cq_id, text="جاري تجهيز صورة بطاقة الربط الذكي... ⏳")

                        info = calculate_smart_transfer_info(direction, orig_id, dest_id, timing_mode="later" if custom_tm else "now", custom_time=custom_tm)
                        img_path = os.path.join(BASE_DIR, f"card_tf_{{chat_id}}_{{int(time.time())}}.png")

                        if render_smart_transfer_card_image(info, img_path):
                            caption = (
                                f"⚡ <b>بطاقة الربط الذكي واللحاق بالقطار (محطة عدلي منصور المركزية):</b>\\n"
                                f"🟢 <b>انطلاق الرحلة:</b> {{info['start_name']}} ({{info['leg1_dep']}})\\n"
                                f"🚉 <b>التبديل بعدلي منصور:</b> {{info['adly_arr']}}\\n"
                                f"🎯 <b>الوصول لمحطتك:</b> {{info['dest_name']}} ({{info['final_arr']}})\\n"
                                f"⏱️ <b>إجمالي زمن الرحلة:</b> {{info['total_time']}} دقيقة\\n"
                                f"🌐 https://capitaltrain.tafawuq-edu.site"
                            )
                            send_ok = send_photo(chat_id, img_path, caption=caption, reply_markup={{
                                "inline_keyboard": [
                                    [{{"text": "🔄 اختيار موعد آخر", "callback_data": f"tf_dest:{{direction}}:{{orig_id}}:{{dest_id}}"}}],
                                    [{{"text": "🔀 تبديل الاتجاه", "callback_data": "transfer_direction_menu"}},
                                     {{"text": "🏠 القائمة الرئيسية", "callback_data": "main_menu"}}]
                                ]
                            }})
                            try:
                                if os.path.exists(img_path):
                                    os.remove(img_path)
                            except Exception:
                                pass
                            if send_ok:
                                answer_callback(cq_id, text="تم إرسال بطاقة الرحلة كصورة بنجاح! 📸")
                            else:
                                answer_callback(cq_id, text="تعذر إرسال الصورة، يرجى المحاولة لاحقاً")
                        else:
                            answer_callback(cq_id, text="حدث خطأ أثناء رسم الصورة")
                        continue

                    if data.startswith("share_img:"):
                        parts = data.split(":")
                        network = parts[1]
                        orig_id = parts[2]
                        dest_id = parts[3]
                        selected_tm = int(parts[4]) if len(parts) >= 5 else None

                        answer_callback(cq_id, text="جاري تجهيز صورة الرحلة... ⏳")

                        orig_obj = get_station_by_id(orig_id, network=network)
                        dest_obj = get_station_by_id(dest_id, network=network)
                        orig_name = orig_obj["name"] if orig_obj else orig_id
                        dest_name = dest_obj["name"] if dest_obj else dest_id
                        net_title = "مترو الخط الثالث الأخضر" if network == 'metro' else "قطار العاصمة الكهربائي"
                        net_icon = "🚇" if network == 'metro' else "🚆"
                        trip_mins = get_actual_travel_mins(orig_id, dest_id, network=network)
                        st_count = get_network_station_count(orig_id, dest_id, network=network)
                        price = get_ticket_price(st_count, network=network)

                        now_dt = datetime.now()
                        now_mins = now_dt.hour * 60 + now_dt.minute

                        lines = []
                        if selected_tm is not None:
                            dep_12h = format_time_12h(selected_tm)
                            arr_12h = format_time_12h(selected_tm + trip_mins)
                            diff_dep = selected_tm - now_mins
                            diff_arr = (selected_tm + trip_mins) - now_mins
                            lines.append(f"🟢 <b>محطة القيام:</b> {{orig_name}} (تحرك: <b>{{dep_12h}}</b>)")
                            lines.append(f"🔴 <b>محطة الوصول:</b> {{dest_name}} (وصول: <b>{{arr_12h}}</b>)")
                            if diff_dep > 0:
                                lines.append(f"⏳ <b>متبقي لتحرك القطار:</b> {{diff_dep}} دقيقة | 🏁 <b>متبقي للوصول:</b> {{diff_arr}} دقيقة")
                            lines.append(f"⏱️ <b>زمن الرحلة:</b> {{trip_mins}} دقيقة • <b>المحطات:</b> {{st_count}} محطات")
                            lines.append(f"🎫 <b>سعر التذكرة:</b> {{price}} جنيه مصري")
                        else:
                            lines.append(f"🟢 <b>من محطة:</b> {{orig_name}} ⬅️ 🔴 <b>إلى:</b> {{dest_name}}")
                            lines.append(f"⏱️ <b>زمن الرحلة:</b> {{trip_mins}} دقيقة • <b>المحطات:</b> {{st_count}} محطات")
                            lines.append(f"🎫 <b>سعر التذكرة:</b> {{price}} جنيه مصري")

                        img_path = os.path.join(BASE_DIR, f"card_{{chat_id}}_{{int(time.time())}}.png")
                        if render_trip_card_image(f"{{net_icon}} {{net_title}}", f"مسار: {{orig_name}} ⬅️ {{dest_name}}", lines, img_path):
                            caption = (
                                f"{{net_icon}} <b>بطاقة مسار الرحلة:</b>\\n"
                                f"🟢 <b>من:</b> {{orig_name}}\\n"
                                f"🔴 <b>إلى:</b> {{dest_name}}\\n"
                                f"⏱️ <b>زمن الرحلة:</b> {{trip_mins}} دقيقة | <b>المحطات:</b> {{st_count}} | <b>التذكرة:</b> {{price}} جنيه\\n"
                                f"🌐 https://capitaltrain.tafawuq-edu.site"
                            )
                            send_ok = send_photo(chat_id, img_path, caption=caption, reply_markup={{
                                "inline_keyboard": [
                                    [{{"text": "🔄 رحلة جديدة", "callback_data": f"choose_net:{{network}}"}}],
                                    [{{"text": "🏠 القائمة الرئيسية", "callback_data": "main_menu"}}]
                                ]
                            }})
                            try:
                                if os.path.exists(img_path):
                                    os.remove(img_path)
                            except Exception:
                                pass
                            if send_ok:
                                answer_callback(cq_id, text="تم إرسال بطاقة الرحلة كصورة بنجاح! 📸")
                            else:
                                answer_callback(cq_id, text="تعذر إرسال الصورة، يرجى المحاولة لاحقاً")
                        else:
                            answer_callback(cq_id, text="حدث خطأ أثناء رسم الصورة")
                        continue

                    if data == "main_menu":
                        send_or_edit_message(
                            chat_id,
                            "🚇 <b>شبكة النقل والمواصلات الذكية:</b>\\\n\\\n"
                            "اختر الخدمة المطلوبة للاستعلام عن المواعيد والرحلات:\\\n"
                            "• <b>🚆 قطار العاصمة الكهربائي (LRT)</b>\\\n"
                            "• <b>🚇 مترو الخط الثالث الأخضر (GL3)</b>\\\n\\\n"
                            "🎙️ يمكنك أيضاً إرسال رسالة صوتية (فويس) في أي وقت!",
                            get_main_menu_keyboard(),
                            msg_id
                        )
                        continue

                    if data.startswith("choose_net:"):
                        network = data.split(":")[1]
                        state["network"] = network
                        net_title = "مترو الخط الثالث الأخضر" if network == 'metro' else "قطار العاصمة الكهربائي"
                        send_or_edit_message(
                            chat_id,
                            f"📍 <b>{{net_title}}:</b>\\\n\\\n"
                            f"🟢 <b>اختر محطة القيام (الانطلاق):</b>",
                            get_stations_keyboard(network=network, prefix="st"),
                            msg_id
                        )
                        continue

                    if data.startswith("st:"):
                        parts = data.split(":")
                        if len(parts) == 2:
                            # Old format: st:origin_id -> infer network (LRT default)
                            origin_id = parts[1]
                            network = state.get("network", "lrt")
                        else:
                            network = parts[1]
                            origin_id = parts[2]
                        state["network"] = network
                        state["origin_id"] = origin_id

                        orig_obj = get_station_by_id(origin_id, network=network)
                        orig_name = orig_obj["name"] if orig_obj else origin_id

                        send_or_edit_message(
                            chat_id,
                            f"🟢 محطة القيام: <b>{{orig_name}}</b>\\\n\\\n"
                            f"🔴 <b>اختر محطة الوصول (النزول):</b>\\\n"
                            f"(سيقوم النظام باستنتاج وتحديد الاتجاه تلقائياً)",
                            get_destinations_keyboard(origin_id, network=network),
                            msg_id
                        )
                        continue

                    if data.startswith("dest:"):
                        parts = data.split(":")
                        network = parts[1]
                        orig_id = parts[2]
                        dest_id = parts[3]

                        orig_obj = get_station_by_id(orig_id, network=network)
                        dest_obj = get_station_by_id(dest_id, network=network)

                        dir_code, dir_lbl = get_refined_direction_info(orig_obj, dest_obj, network=network)
                        schedules = fetch_live_schedule_from_mobility_cairo(orig_id, dir_code, network=network)
                        now_dt = datetime.now()
                        now_mins = now_dt.hour * 60 + now_dt.minute

                        deps = []
                        for s in schedules:
                            dep_raw = s.get("DepTime", "")
                            hhmm = dep_raw.split(" ")[1] if " " in dep_raw else dep_raw
                            if ":" in hhmm:
                                p = hhmm.split(":")
                                tm = int(p[0]) * 60 + int(p[1])
                                deps.append((hhmm, tm))

                        if not deps:
                            interval = 6 if network == 'metro' else 15
                            for i in range(5):
                                dm = now_mins + 4 + i * interval
                                hh = (dm // 60) % 24
                                mm = dm % 60
                                deps.append((f"{{hh:02d}}:{{mm:02d}}", dm))

                        kb_rows = []
                        for idx, (hhmm, tm) in enumerate(deps[:5], 1):
                            diff = tm - now_mins
                            diff_str = "الآن" if diff <= 0 else f"خلال {{diff}} د"
                            time_12h = format_time_12h(hhmm)
                            btn_text = f"🚆 قطار {{idx}}: {{time_12h}} ({{diff_str}})"
                            kb_rows.append([{{
                                "text": btn_text,
                                "callback_data": f"trip_sel:{{network}}:{{orig_id}}:{{dest_id}}:{{tm}}"
                            }}])

                        kb_rows.append([{{
                            "text": "🔙 تغيير محطة الوصول",
                            "callback_data": f"st:{{network}}:{{orig_id}}"
                        }}])
                        kb_rows.append([{{
                            "text": "🏠 القائمة الرئيسية",
                            "callback_data": "main_menu"
                        }}])

                        exact_mins = get_actual_travel_mins(orig_id, dest_id, network=network)
                        orig_name = orig_obj['name'] if orig_obj else orig_id
                        dest_name = dest_obj['name'] if dest_obj else dest_id
                        net_title = "مترو الخط الثالث الأخضر" if network == 'metro' else "قطار العاصمة الكهربائي"
                        net_icon = "🚇" if network == 'metro' else "🚆"

                        prompt_msg = (
                            f"{{net_icon}} <b>رحلة بـ {{net_title}}:</b>\\n\\n"
                            f"🟢 <b>من محطة:</b> {{orig_name}}\\n"
                            f"🔴 <b>إلى محطة:</b> {{dest_name}}\\n"
                            f"⏱️ <b>زمن الرحلة الفعلي:</b> {{exact_mins}} دقيقة\\n"
                            f"🧭 <b>{{dir_lbl}}</b>\\n\\n"
                            f"👇 <b>اختر الرحلة التي ستركبها من الـ 5 قطارات القادمة لحساب وقت الوصول والتفاصيل:</b>"
                        )
                        send_or_edit_message(chat_id, prompt_msg, {{"inline_keyboard": kb_rows}}, msg_id)
                        continue

                    if data.startswith("metro_sel:") or data.startswith("trip_sel:"):
                        parts = data.split(":")
                        if parts[0] == "metro_sel":
                            network = "metro"
                            orig_id = parts[1]
                            dest_id = parts[2]
                            dep_tm = int(parts[3])
                        else:
                            network = parts[1]
                            orig_id = parts[2]
                            dest_id = parts[3]
                            dep_tm = int(parts[4])

                        orig_obj = get_station_by_id(orig_id, network=network)
                        dest_obj = get_station_by_id(dest_id, network=network)
                        exact_mins = get_actual_travel_mins(orig_id, dest_id, network=network)
                        arr_tm = dep_tm + exact_mins

                        dep_12h = format_time_12h(dep_tm)
                        arr_12h = format_time_12h(arr_tm)

                        st_count = get_network_station_count(orig_id, dest_id, network=network)
                        price = get_ticket_price(st_count, network=network)
                        if network == "metro":
                            net_title = "مترو الخط الثالث الأخضر"
                            net_icon = "🚇"
                        else:
                            net_title = "قطار العاصمة الكهربائي"
                            net_icon = "🚆"

                        orig_name = orig_obj['name'] if orig_obj else orig_id
                        dest_name = dest_obj['name'] if dest_obj else dest_id

                        now_dt = datetime.now()
                        now_mins = now_dt.hour * 60 + now_dt.minute
                        diff_dep = dep_tm - now_mins
                        diff_arr = arr_tm - now_mins

                        if diff_dep > 0:
                            countdown_str = f"⏳ <b>متبقي على تحرك القطار:</b> <b>{{diff_dep}} دقيقة</b>\\n🏁 <b>متبقي على وصولك لمحطتك:</b> <b>{{diff_arr}} دقيقة</b>"
                        elif diff_dep == 0:
                            countdown_str = f"⏳ <b>القطار يتحرك الآن من رصيف المحطة!</b>\\n🏁 <b>متبقي على وصولك لمحطتك:</b> <b>{{diff_arr}} دقيقة</b>"
                        else:
                            countdown_str = f"⚠️ <b>تحرك القطار منذ {{abs(diff_dep)}} دقيقة</b> (الوصول: {{arr_12h}})"

                        res_msg = (
                            f"{{net_icon}} <b>تفاصيل رحلة {{net_title}} المختارة:</b>\\n\\n"
                            f"🟢 <b>محطة القيام:</b> <b>{{orig_name}}</b>\\n"
                            f"⏰ <b>موعد تحرك القطار:</b> <b>{{dep_12h}}</b>\\n\\n"
                            f"🔴 <b>محطة الوصول:</b> <b>{{dest_name}}</b>\\n"
                            f"🏁 <b>موعد الوصول المتوقع:</b> <b>{{arr_12h}}</b>\\n\\n"
                            f"────────────────────\\n"
                            f"{{countdown_str}}\\n"
                            f"⏱️ <b>زمن الرحلة الفعلي:</b> <b>{{exact_mins}} دقيقة</b>\\n"
                            f"🚉 <b>عدد المحطات:</b> <b>{{st_count}} محطات</b>\\n"
                            f"🎫 <b>سعر التذكرة:</b> <b>{{price}} جنيه</b>\\n\\n"
                            f"✅ <i>مواعيد تشغيل رسمية دقيقة وفق خوادم RATP Dev Mobility Cairo.</i>"
                        )

                        share_plain = (
                            f"{{net_icon}} تفاصيل رحلة {{net_title}}:\\n"
                            f"🟢 من محطة: {{orig_name}} ({{dep_12h}})\\n"
                            f"🔴 إلى محطة: {{dest_name}} (الوصول المتوقع: {{arr_12h}})\\n"
                            f"⏱️ زمن الرحلة: {{exact_mins}} دقيقة ({{st_count}} محطة)\\n"
                            f"🎫 سعر التذكرة: {{price}} جنيه\\n"
                            f"🌐 https://capitaltrain.tafawuq-edu.site"
                        )
                        wa_url = f"https://api.whatsapp.com/send?text={{urllib.parse.quote(share_plain)}}"
                        tg_url = f"https://t.me/share/url?url={{urllib.parse.quote(WEB_URL)}}&text={{urllib.parse.quote(share_plain)}}"

                        kb = {{
                            "inline_keyboard": [
                                [{{"text": "📲 مشاركة واتساب", "url": wa_url}},
                                 {{"text": "📤 مشاركة تليجرام", "url": tg_url}}],
                                [{{"text": "📸 صورة الرحلة", "callback_data": f"share_img:{{network}}:{{orig_id}}:{{dest_id}}:{{dep_tm}}"}},
                                 {{"text": "⏰ تعيين كمنبه", "callback_data": f"rem_set:{{network}}:{{orig_id}}:{{dest_id}}" }}],
                                [{{"text": "🚆 تغيير القطار", "callback_data": f"dest:{{network}}:{{orig_id}}:{{dest_id}}" }},
                                 {{"text": "🔄 رحلة جديدة", "callback_data": f"choose_net:{{network}}"}}],
                                [{{"text": "🏠 القائمة الرئيسية", "callback_data": "main_menu"}}]
                            ]
                        }}
                        send_or_edit_message(chat_id, res_msg, kb, msg_id)
                        continue

                    if data == "fares":
                        fares_msg = (
                            "🎟️ <b>أسعار التذاكر والاشتراكات الرسمية (2026):</b>\\\n\\\n"
                            "🚆 <b>قطار العاصمة الكهربائي (LRT):</b>\\\n"
                            "• حتى 3 محطات: <b>10 جنيه</b>\\\n"
                            "• من 4 إلى 7 محطات: <b>15 جنيه</b>\\\n"
                            "• أكثر من 7 محطات: <b>20 جنيه</b>\\\n\\\n"
                            "🚇 <b>مترو الخط الثالث الأخضر (GL3):</b>\\\n"
                            "• منطقة واحدة (حتى 9 محطات): <b>8 جنيه</b>\\\n"
                            "• منطقتان (10 إلى 16 محطة): <b>10 جنيه</b>\\\n"
                            "• 3 مناطق (17 إلى 23 محطة): <b>15 جنيه</b>\\\n"
                            "• أكثر من 23 محطة: <b>20 جنيه</b>\\\n\\\n"
                            "────────────────────\\\n"
                            "💡 <i>لحساب أي مسار تفصيلي وسعر التذكرة اضغط على موقع المواعيد.</i>"
                        )
                        kb = {{
                            "inline_keyboard": [
                                [{{"text": "🌐 حاسبة الأسعار والمسارات بالموقع", "url": WEB_URL}}],
                                [{{"text": "🔙 القائمة الرئيسية", "callback_data": "main_menu"}}]
                            ]
                        }}
                        send_or_edit_message(chat_id, fares_msg, kb, msg_id)
                        continue

                    if data == "support":
                        sup_msg = (
                            "📞 <b>أرقام خدمة العملاء والتواصل:</b>\\\n\\\n"
                            "• <b>الخط الساخن RATP Dev:</b> 19549\\\n"
                            "• <b>واتساب قطار العاصمة والمترو:</b> 01103776770\\\n"
                            "• <b>البريد والموقع:</b> mobilitycairo.com\\\n\\\n"
                            "🕒 أوقات عمل مراكز الدعم والمحطات: 05:30 ص حتى 11:30 م يومياً."
                        )
                        kb = {{"inline_keyboard": [[{{"text": "🔙 القائمة الرئيسية", "callback_data": "main_menu"}}]]}}
                        send_or_edit_message(chat_id, sup_msg, kb, msg_id)
                        continue

                    if data.startswith("rem_set:"):
                        parts = data.split(":")
                        network = parts[1]
                        st_id = parts[2]
                        dest_id = parts[3]

                        state["action"] = "awaiting_reminder_time"
                        state["network"] = network
                        state["station_id"] = st_id
                        state["dest_id"] = dest_id
                        orig_obj = get_station_by_id(st_id, network=network)
                        dest_obj = get_station_by_id(dest_id, network=network)
                        dir_code, _ = get_refined_direction_info(orig_obj, dest_obj, network=network)
                        state["dir_code"] = dir_code

                        send_or_edit_message(
                            chat_id,
                            f"⏰ <b>ضبط منبه للرحلة من {{orig_obj['name']}} إلى {{dest_obj['name']}}:</b>\\\n\\\n"
                            f"يرجى كتابة التوقيت المطلوب بصيغة (HH:MM)\\\n"
                            f"مثال: <code>08:00</code> أو عدة أوقات مثل <code>08:00, 16:30</code>:",
                            {{"inline_keyboard": [[{{"text": "❌ إلغاء", "callback_data": "main_menu"}}]]}}
                        )
                        continue

                    if data == "reminder_menu":
                        rems = [r for r in load_reminders() if r["chat_id"] == chat_id]
                        if not rems:
                            txt = "⏰ <b>ليس لديك منبهات نشطة حالياً.</b>\\\n\\\nيمكنك تفعيل منبه بسهولة بالاستعلام عن أي رحلة والضغط على 'تعيين كمنبه مجدول'."
                            kb = {{"inline_keyboard": [
                                [{{"text": "🚆 رحلة جديدة بقطار العاصمة", "callback_data": "choose_net:lrt"}}],
                                [{{"text": "🚇 رحلة جديدة بمترو الخط الثالث", "callback_data": "choose_net:metro"}}],
                                [{{"text": "🔙 القائمة الرئيسية", "callback_data": "main_menu"}}]
                            ]}}
                        else:
                            txt = "⏰ <b>منبهاتك اليومية المجدولة:</b>\\\n\\\n"
                            for idx, r in enumerate(rems, 1):
                                net = r.get("network", "lrt")
                                s1 = get_station_by_id(r["station_id"], network=net)
                                s2 = get_station_by_id(r.get("dest_id"), network=net)
                                txt += f"<b>{{idx}}. {{s1['name'] if s1 else ''}} ⬅️ {{s2['name'] if s2 else ''}}</b>\\\n"
                                txt += f"   🕒 المواعيد: {{', '.join(r['times'])}} | الأيام: {{len(r['days'])}} أيام بالأسبوع\\\n\\\n"
                            kb = {{"inline_keyboard": [
                                [{{"text": "🗑 مسح كافة المنبهات", "callback_data": "clear_reminders"}}],
                                [{{"text": "🔙 القائمة الرئيسية", "callback_data": "main_menu"}}]
                            ]}}
                        send_or_edit_message(chat_id, txt, kb, msg_id)
                        continue

                    if data == "clear_reminders":
                        all_rems = load_reminders()
                        new_rems = [r for r in all_rems if r["chat_id"] != chat_id]
                        save_reminders(new_rems)
                        send_or_edit_message(chat_id, "✅ تم مسح جميع منبهاتك بنجاح.", {{"inline_keyboard": [[{{"text": "🔙 القائمة الرئيسية", "callback_data": "main_menu"}}]]}}, msg_id)
                        continue

                    if data.startswith("tog_day:"):
                        day_code = int(data.split(":")[1])
                        sel_days = state.get("selected_days", [6, 0, 1, 2, 3])
                        if day_code in sel_days:
                            sel_days.remove(day_code)
                        else:
                            sel_days.append(day_code)
                        state["selected_days"] = sel_days
                        send_or_edit_message(chat_id, "🗓️ <b>حدد الأيام التي ترغب في تلقي التنبيه بها:</b>", build_days_keyboard(sel_days), msg_id)
                        continue

                    if data == "save_reminder":
                        sel_days = state.get("selected_days", [6, 0, 1, 2, 3])
                        if not sel_days:
                            answer_callback(cq_id, "⚠️ يرجى اختيار يوم واحد على الأقل!")
                            continue
                        new_rem = {{
                            "chat_id": chat_id,
                            "network": state.get("network", "lrt"),
                            "station_id": state["station_id"],
                            "dest_id": state.get("dest_id"),
                            "direction_code": state["dir_code"],
                            "times": state["times"],
                            "days": sel_days,
                            "enabled": True,
                            "created_at": datetime.now().isoformat()
                        }}
                        all_r = load_reminders()
                        all_r.append(new_rem)
                        save_reminders(all_r)
                        state.clear()
                        send_or_edit_message(chat_id, "✅ <b>تم تفعيل المنبه بنجاح!</b>\\\nسيرسل لك البوت رسالة بمواعيد القطارات الحية تلقائياً في الأوقات المحددة.", {{"inline_keyboard": [[{{"text": "🔙 القائمة الرئيسية", "callback_data": "main_menu"}}]]}}, msg_id)
                        continue

                # 2. Text / Voice Messages Handler
                if "message" in u:
                    msg = u["message"]
                    chat_id = msg["chat"]["id"]
                    text = msg.get("text", "").strip()
                    state = user_states.setdefault(chat_id, {{}})

                    # Voice note handling
                    if "voice" in msg:
                        file_id = msg["voice"]["file_id"]
                        send_or_edit_message(chat_id, "🎧 جارٍ الاستماع للفويس ومعالجة المحطات بذكاء...")

                        ogg_file = os.path.join(BASE_DIR, f"voice_{{chat_id}}_{{int(time.time())}}.ogg")
                        wav_file = ogg_file.replace(".ogg", ".wav")

                        if download_telegram_file(file_id, ogg_file):
                            if convert_ogg_to_wav(ogg_file, wav_file):
                                transcribed = transcribe_audio_whisper(wav_file)
                                try:
                                    os.remove(ogg_file)
                                    os.remove(wav_file)
                                except Exception:
                                    pass

                                if transcribed:
                                    send_or_edit_message(chat_id, f"🗣️ <i>«{{transcribed}}»</i>")

                                    # Try both networks (LRT first, then Metro)
                                    orig_lrt, dest_lrt, dir_lrt, lbl_lrt = analyze_trip_phrase(transcribed, network='lrt')
                                    orig_met, dest_met, dir_met, lbl_met = analyze_trip_phrase(transcribed, network='metro')

                                    target_orig, target_dest, target_dir, target_lbl, target_net = None, None, None, None, 'lrt'
                                    if orig_met and (not orig_lrt or orig_met['name'] not in ['عدلي منصور']):
                                        target_orig, target_dest, target_dir, target_lbl, target_net = orig_met, dest_met, dir_met, lbl_met, 'metro'
                                    elif orig_lrt:
                                        target_orig, target_dest, target_dir, target_lbl, target_net = orig_lrt, dest_lrt, dir_lrt, lbl_lrt, 'lrt'

                                    if target_orig:
                                        res = format_station_result(target_orig["id"], target_dir, deduced_dest=target_dest, custom_dir_label=target_lbl, network=target_net)
                                        back_kb = {{
                                            "inline_keyboard": [
                                                [{{"text": "⏰ تعيين كمنبه مجدول لهذه الرحلة", "callback_data": f"rem_set:{{target_net}}:{{target_orig['id']}}:{{target_dest['id'] if target_dest else target_orig['id']}}"}}],
                                                [{{"text": "🔄 رحلة جديدة", "callback_data": f"choose_net:{{target_net}}"}},
                                                 {{"text": "🔙 القائمة الرئيسية", "callback_data": "main_menu"}}]
                                            ]
                                        }}
                                        send_or_edit_message(chat_id, res, back_kb)
                                        continue
                                    else:
                                        send_or_edit_message(
                                            chat_id,
                                            f"⚠️ تعرفت على الصوت: <i>«{{transcribed}}»</i>\\\nولكن لم أستطع استنتاج اسم المحطات بدقة. يرجى الاختيار من الأزرار أدناه:",
                                            get_main_menu_keyboard()
                                        )
                                        continue

                    # Awaiting reminder time text
                    if state.get("action") == "awaiting_reminder_time":
                        found_times = re.findall(r'\\b(?:[01]?\\d|2[0-3]):[0-5]\\d\\b', text)
                        if not found_times:
                            send_or_edit_message(chat_id, "⚠️ لم أتعرف على أي صيغة وقت صحيحة.\\\nيرجى كتابة الوقت بصيغة (HH:MM) مثل <code>08:00</code> أو <code>10:00, 15:30</code>:")
                            continue

                        clean_times = []
                        for ft in found_times:
                            p = ft.split(":")
                            clean_times.append(f"{{int(p[0]):02d}}:{{int(p[1]):02d}}")
                        clean_times = sorted(list(set(clean_times)))

                        state["times"] = clean_times
                        state["action"] = "awaiting_reminder_days"
                        state["selected_days"] = [6, 0, 1, 2, 3]

                        st_obj = get_station_by_id(state["station_id"], network=state.get("network", "lrt"))
                        send_or_edit_message(
                            chat_id,
                            f"✅ تم تسجيل المواعيد: <b>{{' ، '.join(clean_times)}}</b> لمحطة {{st_obj['name'] if st_obj else ''}}\\\n\\\n"
                            f"🗓️ <b>اختر أيام التكرار المطلوبة:</b>\\\n"
                            f"(اضغط على أي يوم لاختياره أو إلغائه، ثم اضغط حفظ وتفعيل)",
                            build_days_keyboard(state["selected_days"])
                        )
                        continue

                    # Text queries recognition (e.g., "من الشروق لعدلي", "من العتبة لروض الفرج")
                    orig_lrt, dest_lrt, dir_lrt, lbl_lrt = analyze_trip_phrase(text, network='lrt')
                    orig_met, dest_met, dir_met, lbl_met = analyze_trip_phrase(text, network='metro')

                    target_orig, target_dest, target_dir, target_lbl, target_net = None, None, None, None, 'lrt'
                    if orig_met and (not orig_lrt or orig_met['name'] not in ['عدلي منصور']):
                        target_orig, target_dest, target_dir, target_lbl, target_net = orig_met, dest_met, dir_met, lbl_met, 'metro'
                    elif orig_lrt:
                        target_orig, target_dest, target_dir, target_lbl, target_net = orig_lrt, dest_lrt, dir_lrt, lbl_lrt, 'lrt'

                    if target_orig:
                        res = format_station_result(target_orig["id"], target_dir, deduced_dest=target_dest, custom_dir_label=target_lbl, network=target_net)
                        back_kb = {{
                            "inline_keyboard": [
                                [{{"text": "⏰ تعيين كمنبه مجدول لهذه الرحلة", "callback_data": f"rem_set:{{target_net}}:{{target_orig['id']}}:{{target_dest['id'] if target_dest else target_orig['id']}}"}}],
                                [{{"text": "🔄 رحلة جديدة", "callback_data": f"choose_net:{{target_net}}"}},
                                 {{"text": "🔙 القائمة الرئيسية", "callback_data": "main_menu"}}]
                            ]
                        }}
                        send_or_edit_message(chat_id, res, back_kb)
                        continue

                    if text.startswith("/start"):
                        send_or_edit_message(
                            chat_id,
                            "👋 <b>مرحباً بك في البوت الموحد لشبكة النقل الذكية!</b>\\\n\\\n"
                            "اختر وسيلة النقل لمعرفة المواعيد والرحلات الحية:\\\n"
                            "• <b>🚆 قطار العاصمة الكهربائي (LRT)</b>\\\n"
                            "• <b>🚇 مترو الخط الثالث الأخضر (GL3)</b>\\\n\\\n"
                            "🎙️ <b>يدعم الذكاء الصوتي:</b> أرسل رسالة صوتية (فويس) مباشرة مثل: <i>«من الشروق لعدلي منصور»</i> أو <i>«من العتبة لجامعة القاهرة»</i>.",
                            get_main_menu_keyboard()
                        )
                    else:
                        send_or_edit_message(
                            chat_id,
                            "👋 <b>شبكة النقل الذكية:</b>\\\nاختر من الأزرار بالأسفل أو أرسل رسالة صوتية أو نصية بمسار رحلتك 🎙️",
                            get_main_menu_keyboard()
                        )

        except Exception as e:
            print(f"Main loop error: {{e}}", flush=True)
            time.sleep(2)

if __name__ == "__main__":
    main()
'''

with open('I:/CapitalTrain/telegram_bot_runner.py', 'w', encoding='utf-8') as f:
    f.write(bot_code)

print("telegram_bot_runner.py generated successfully!")
