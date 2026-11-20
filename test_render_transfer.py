import sys
import os
import pymupdf

def render_smart_transfer_card_image(info, output_path):
    try:
        doc = pymupdf.open()
        width = 800
        height = 680
        page = doc.new_page(width=width, height=height)

        # Background
        page.draw_rect(pymupdf.Rect(0, 0, width, height), color=(0.04, 0.07, 0.14), fill=(0.04, 0.07, 0.14))
        page.draw_rect(pymupdf.Rect(8, 8, width - 8, height - 8), color=(0.12, 0.22, 0.38), width=1.5)

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

        stops1 = info.get("stops1", 19)
        stops2 = info.get("stops2", 3)
        stops1_lbl = "محطات مترو الخط الثالث الأخضر" if is_m2l else "محطات قطار العاصمة الكهربائي"
        stops2_lbl = "محطات قطار العاصمة الكهربائي" if is_m2l else "محطات مترو الخط الثالث الأخضر"
        note1 = "بين كل محطة ومحطة: 1.5 إلى 2 دقيقة" if is_m2l else "بين كل محطة ومحطة: 4 إلى 5 دقائق"
        note2 = "بين كل محطة ومحطة: 4 إلى 5 دقائق" if is_m2l else "بين كل محطة ومحطة: 1.5 إلى 2 دقيقة"

        advice_text = f"سيكون معك <b>{best_diff + 5} دقيقة</b> في محطة عدلي منصور للتبديل والتسوق أو الصعود للرصيف براحة تامة." if best_diff >= 4 else f"ستصل الرصيف قبل تحرك القطار بـ <b>{best_diff} دقائق</b> فقط."
        next_tip = f"💡 القطار البديل التالي يتحرك من رصيف عدلي منصور الساعة <b>{next_time}</b>."

        html = f"""
        <div style="font-family: sans-serif; direction: rtl; text-align: right; color: #f8fafc; padding: 18px;">
          <!-- Header -->
          <table style="width: 100%; border-bottom: 1px solid #1e293b; padding-bottom: 10px; margin-bottom: 14px;">
            <tr>
              <td style="text-align: right; vertical-align: middle;">
                <span style="background: {status_bg}; border: 1px solid {status_border}; color: #ffffff; font-weight: bold; font-size: 14px; padding: 6px 14px; border-radius: 8px;">
                  {status_text}
                </span>
              </td>
              <td style="text-align: left; vertical-align: middle; color: #94a3b8; font-size: 13.5px;">
                المسار الكلي: من <b style="color: #ffffff;">{start_name}</b> إلى <b style="color: #ffffff;">{dest_name}</b>
              </td>
            </tr>
          </table>

          <!-- 4 Uniform Step Cards (2x2 Table) -->
          <table style="width: 100%; border-spacing: 10px; margin-bottom: 10px;">
            <tr>
              <!-- Step 1 -->
              <td style="width: 50%; background: #0f172a; border: 1px solid #334155; border-radius: 10px; padding: 12px; vertical-align: top;">
                <div style="color: #94a3b8; font-size: 12px; font-weight: bold;">{leg1_title}</div>
                <div style="color: #38bdf8; font-size: 26px; font-weight: bold; font-family: monospace; margin: 4px 0;">{leg1_dep}</div>
                <div style="color: #cbd5e1; font-size: 12px; border-top: 1px solid #1e293b; padding-top: 5px;">
                  <b>{start_name}</b> (محطة الانطلاق الأولى)
                </div>
              </td>
              <!-- Step 2 -->
              <td style="width: 50%; background: #0f172a; border: 1px solid #334155; border-radius: 10px; padding: 12px; vertical-align: top;">
                <div style="color: #94a3b8; font-size: 12px; font-weight: bold;">2. الوصول لعدلي منصور المركزية</div>
                <div style="color: #38bdf8; font-size: 26px; font-weight: bold; font-family: monospace; margin: 4px 0;">{adly_arr}</div>
                <div style="color: #cbd5e1; font-size: 12px; border-top: 1px solid #1e293b; padding-top: 5px;">
                  زمن الرحلة الأولى: {leg1_ride} دقيقة
                </div>
              </td>
            </tr>
            <tr>
              <!-- Step 3 -->
              <td style="width: 50%; background: #0f172a; border: 1px solid #334155; border-radius: 10px; padding: 12px; vertical-align: top;">
                <div style="color: #94a3b8; font-size: 12px; font-weight: bold;">{leg2_title}</div>
                <div style="color: #fbbf24; font-size: 26px; font-weight: bold; font-family: monospace; margin: 4px 0;">{leg2_dep}</div>
                <div style="color: #fde68a; font-size: 12px; border-top: 1px solid #1e293b; padding-top: 5px;">
                  جاهز بالرصيف بعد التبديل: <b>{ready_time}</b>
                </div>
              </td>
              <!-- Step 4 -->
              <td style="width: 50%; background: #0f172a; border: 1px solid #334155; border-radius: 10px; padding: 12px; vertical-align: top;">
                <div style="color: #94a3b8; font-size: 12px; font-weight: bold;">4. الوصول لوجهتك النهائية</div>
                <div style="color: #34d399; font-size: 26px; font-weight: bold; font-family: monospace; margin: 4px 0;">{final_arr}</div>
                <div style="color: #cbd5e1; font-size: 12px; border-top: 1px solid #1e293b; padding-top: 5px;">
                  <b>{dest_name}</b> (زمن الرحلة الثانية: {leg2_ride} د)
                </div>
              </td>
            </tr>
          </table>

          <!-- 3 Stats Boxes -->
          <table style="width: 100%; border-spacing: 10px; margin-bottom: 12px;">
            <tr>
              <td style="width: 33.3%; background: #1e1b4b; border: 1px solid #4338ca; border-radius: 10px; padding: 10px;">
                <div style="color: #c7d2fe; font-size: 11px; font-weight: bold;">{stops1_lbl}</div>
                <div style="color: #ffffff; font-size: 20px; font-weight: bold; font-family: monospace; margin: 3px 0;">{stops1} محطة</div>
                <div style="color: #a5b4fc; font-size: 9.5px;">{note1}</div>
              </td>
              <td style="width: 33.3%; background: #134e4a; border: 1px solid #0d9488; border-radius: 10px; padding: 10px;">
                <div style="color: #ccfbf1; font-size: 11px; font-weight: bold;">{stops2_lbl}</div>
                <div style="color: #ffffff; font-size: 20px; font-weight: bold; font-family: monospace; margin: 3px 0;">{stops2} محطة</div>
                <div style="color: #99f6e4; font-size: 9.5px;">{note2}</div>
              </td>
              <td style="width: 33.3%; background: #713f12; border: 1px solid #d97706; border-radius: 10px; padding: 10px;">
                <div style="color: #fef3c7; font-size: 11px; font-weight: bold;">إجمالي زمن الرحلة المشتركة</div>
                <div style="color: #fde047; font-size: 20px; font-weight: bold; font-family: monospace; margin: 3px 0;">{total_time} دقيقة</div>
                <div style="color: #fef08a; font-size: 9.5px;">شاملاً الركوب والتبديل والوصول</div>
              </td>
            </tr>
          </table>

          <!-- Info Tip Box -->
          <div style="background: #0f172a; border: 1px solid #334155; border-radius: 10px; padding: 10px 14px; margin-bottom: 12px; font-size: 12px; line-height: 1.6;">
            <div>ℹ️ {advice_text}</div>
            <div style="color: #94a3b8; margin-top: 4px;">{next_tip}</div>
          </div>

          <!-- Footer -->
          <table style="width: 100%; border-top: 1px solid #1e293b; padding-top: 8px;">
            <tr>
              <td style="text-align: right; color: #10b981; font-size: 11px; font-weight: bold;">
                شبكة النقل الذكية: قطار العاصمة الكهربائي ومترو الخط الثالث
              </td>
              <td style="text-align: left; color: #64748b; font-size: 11px; font-family: monospace;">
                capitaltrain.tafawuq-edu.site
              </td>
            </tr>
          </table>
        </div>
        """

        page.insert_htmlbox(pymupdf.Rect(10, 10, width - 10, height - 10), html)
        pix = page.get_pixmap(dpi=150)
        pix.save(output_path)
        doc.close()
        return True
    except Exception as e:
        print(f"render_smart_transfer_card_image error: {e}", flush=True)
        return False

# Test run
sample_info = {
    "direction": "metro_to_lrt",
    "start_name": "جمال عبد الناصر",
    "dest_name": "الشروق",
    "leg1_name": "مترو الخط الثالث الأخضر",
    "leg2_name": "قطار العاصمة الكهربائي",
    "leg1_dep": "09:15 م",
    "leg1_ride": 41,
    "adly_arr": "09:56 م",
    "ready_time": "10:01 م",
    "best_time": "10:20 م",
    "best_diff": 19,
    "next_time": "10:40 م",
    "leg2_ride": 13,
    "final_arr": "10:33 م",
    "total_time": 78,
    "stops1": 20,
    "stops2": 3
}

out_path = r"I:\CapitalTrain\test_smart_card.png"
ok = render_smart_transfer_card_image(sample_info, out_path)
print("Render smart card result:", ok, os.path.exists(out_path), os.path.getsize(out_path) if os.path.exists(out_path) else 0)
