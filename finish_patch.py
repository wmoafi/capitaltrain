# -*- coding: utf-8 -*-
with open("I:/CapitalTrain/generate_unified_index.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# 1. Update Hero Card header (lines 159-175)
new_hero_header = """      <div class="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-white/10">
        <div class="flex items-center gap-2.5">
          <span class="p-2 bg-amber-400/20 text-amber-300 rounded-xl border border-amber-400/30">
            <i data-lucide="zap" class="w-5 h-5"></i>
          </span>
          <div>
            <h2 id="transfer-card-title" class="font-black text-base sm:text-lg tracking-tight flex items-center gap-2">
              <span>حاسبة الربط وضمان اللحاق بالقطار التبادلي</span>
            </h2>
            <p id="transfer-card-subtitle" class="text-xs text-slate-300">احسب توقيت التبديل بدقة في محطة عدلي منصور التبادلية في كلا الاتجاهين</p>
          </div>
        </div>
        
        <!-- Direction Switcher (Metro -> LRT vs LRT -> Metro) -->
        <div class="flex items-center gap-1 bg-black/40 p-1 rounded-xl border border-white/10 text-xs">
          <button id="btn-transfer-dir-m2l" onclick="setTransferDirection('metro_to_lrt')" class="px-3 py-1.5 rounded-lg font-bold transition flex items-center gap-1.5 bg-amber-400 text-slate-950 shadow-sm">
            <span>🚇 المترو ⬅️ القطار LRT</span>
          </button>
          <button id="btn-transfer-dir-l2m" onclick="setTransferDirection('lrt_to_metro')" class="px-3 py-1.5 rounded-lg font-bold transition flex items-center gap-1.5 text-slate-300 hover:text-white">
            <span>🚆 القطار LRT ⬅️ المترو</span>
          </button>
        </div>
      </div>
"""
lines[158:175] = [new_hero_header]

text = "".join(lines)

# 2. Update labels above dropdowns
text = text.replace(
    '<label class="block text-xs font-bold text-slate-300 mb-1">🚇 محطة المترو الحالية:</label>',
    '<label id="lbl-transfer-start" class="block text-xs font-bold text-slate-300 mb-1">🚇 محطة القيام الحالية (المترو):</label>'
)
text = text.replace(
    '<label class="block text-xs font-bold text-slate-300 mb-1">🚄 وجهتك في قطار العاصمة (LRT):</label>',
    '<label id="lbl-transfer-dest" class="block text-xs font-bold text-slate-300 mb-1">🚄 محطة الوصول النهائية (قطار العاصمة):</label>'
)

# 3. Update populateTransferDropdowns
old_pop = """    function populateTransferDropdowns() {{
      transferMetroStation.innerHTML = '';
      transferLrtStation.innerHTML = '';

      METRO_LINE3_STATIONS.forEach(s => {{
        const opt = new Option(`${{s.name}}${{s.interchange ? ' 🔄' : ''}}`, s.id);
        transferMetroStation.add(opt);
      }});
      transferMetroStation.value = "139909"; // جمال عبد الناصر

      LRT_STATIONS.forEach(s => {{
        if (s.id !== "139886") {{
          const opt = new Option(s.name, s.id);
          transferLrtStation.add(opt);
        }}
      }});
      transferLrtStation.value = "139920"; // الشروق

      const now = new Date();
      transferInputTime.value = `${{String(now.getHours()).padStart(2, '0')}}:${{String(now.getMinutes()).padStart(2, '0')}}`;
    }}"""

new_pop = """    let currentTransferDir = 'metro_to_lrt';

    const btnTransferDirM2L = document.getElementById('btn-transfer-dir-m2l');
    const btnTransferDirL2M = document.getElementById('btn-transfer-dir-l2m');
    const lblTransferStart = document.getElementById('lbl-transfer-start');
    const lblTransferDest = document.getElementById('lbl-transfer-dest');

    window.setTransferDirection = function(dir) {{
      currentTransferDir = dir;
      if (dir === 'metro_to_lrt') {{
        btnTransferDirM2L.className = "px-3 py-1.5 rounded-lg font-bold transition flex items-center gap-1.5 bg-amber-400 text-slate-950 shadow-sm";
        btnTransferDirL2M.className = "px-3 py-1.5 rounded-lg font-bold transition flex items-center gap-1.5 text-slate-300 hover:text-white";
        if (lblTransferStart) lblTransferStart.textContent = "🚇 محطة القيام الحالية (المترو):";
        if (lblTransferDest) lblTransferDest.textContent = "🚄 محطة الوصول النهائية (قطار العاصمة):";
      }} else {{
        btnTransferDirL2M.className = "px-3 py-1.5 rounded-lg font-bold transition flex items-center gap-1.5 bg-amber-400 text-slate-950 shadow-sm";
        btnTransferDirM2L.className = "px-3 py-1.5 rounded-lg font-bold transition flex items-center gap-1.5 text-slate-300 hover:text-white";
        if (lblTransferStart) lblTransferStart.textContent = "🚄 محطة القيام الحالية (قطار العاصمة):";
        if (lblTransferDest) lblTransferDest.textContent = "🚇 محطة الوصول النهائية (المترو):";
      }}
      populateTransferDropdowns();
    }};

    function populateTransferDropdowns() {{
      transferMetroStation.innerHTML = '';
      transferLrtStation.innerHTML = '';

      if (currentTransferDir === 'metro_to_lrt') {{
        METRO_LINE3_STATIONS.forEach(s => {{
          const opt = new Option(`${{s.name}}${{s.interchange ? ' 🔄' : ''}}`, s.id);
          transferMetroStation.add(opt);
        }});
        transferMetroStation.value = "139909";

        LRT_STATIONS.forEach(s => {{
          if (s.id !== "139886") {{
            const opt = new Option(s.name, s.id);
            transferLrtStation.add(opt);
          }}
        }});
        transferLrtStation.value = "139920";
      }} else {{
        LRT_STATIONS.forEach(s => {{
          if (s.id !== "139886") {{
            const opt = new Option(s.name, s.id);
            transferMetroStation.add(opt);
          }}
        }});
        transferMetroStation.value = "139920";

        METRO_LINE3_STATIONS.forEach(s => {{
          if (s.id !== "139886") {{
            const opt = new Option(`${{s.name}}${{s.interchange ? ' 🔄' : ''}}`, s.id);
            transferLrtStation.add(opt);
          }}
        }});
        transferLrtStation.value = "139909";
      }}

      const now = new Date();
      transferInputTime.value = `${{String(now.getHours()).padStart(2, '0')}}:${{String(now.getMinutes()).padStart(2, '0')}}`;
    }}"""

if old_pop in text:
    text = text.replace(old_pop, new_pop, 1)
    print("populateTransferDropdowns successfully updated!")
else:
    print("old_pop NOT found!")

# 4. Update the per-station display in Trip Calculator
text = text.replace(
    "const isKitKat = s.id === \"139906\";",
    "const isKitKat = s.id === \"139906\"; const cumMins = Math.abs((METRO_TO_ADLY_MINS[s.id] ?? 0) - (METRO_TO_ADLY_MINS[startId] ?? 0));"
)
text = text.replace(
    "${isFirst ? '🟢 ' : isLast ? '🔴 ' : isKitKat ? '🔄 ' : ''}${s.name}\n                  </span>",
    "${isFirst ? '🟢 ' : isLast ? '🔴 ' : isKitKat ? '🔄 ' : ''}${s.name}\n                  </span>\n                  <span class=\"text-[10px] text-slate-400 font-mono mt-0.5\">${isFirst ? 'البداية' : '+' + cumMins + ' د'}</span>"
)

text = text.replace(
    "const isBadr = s.id === \"139892\";",
    "const isBadr = s.id === \"139892\"; const cumMins = Math.abs((LRT_FROM_ADLY_MINS[s.id] ?? 0) - (LRT_FROM_ADLY_MINS[startId] ?? 0));"
)
text = text.replace(
    "${isFirst ? '🟢 ' : isLast ? '🔴 ' : isBadr ? '🔄 ' : ''}${s.name}\n                  </span>",
    "${isFirst ? '🟢 ' : isLast ? '🔴 ' : isBadr ? '🔄 ' : ''}${s.name}\n                  </span>\n                  <span class=\"text-[10px] text-slate-400 font-mono mt-0.5\">${isFirst ? 'البداية' : '+' + cumMins + ' د'}</span>"
)

with open("I:/CapitalTrain/generate_unified_index.py", "w", encoding="utf-8") as f:
    f.write(text)

print("generate_unified_index.py written completely!")
