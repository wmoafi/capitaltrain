import urllib.request
import json
import re

url = "https://www.mobilitycairo.com/ar/pthv/get/proto/stoppoints-discovery?line=L3-57"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
raw = urllib.request.urlopen(req).read()

# Let's inspect raw binary strings
# We want to match stop ID with its Arabic name in the protobuf
with open("line3_verified_stops.json", "r", encoding="utf-8") as f:
    verified = json.load(f)

# Find all 6 digit IDs and their offsets
matches = []
for m in re.finditer(rb'139\d{3}', raw):
    sid = m.group().decode()
    offset = m.start()
    matches.append((offset, sid))

print(f"Total ID occurrences in proto: {len(matches)}")

# For each occurrence, look at the next 200 bytes for Arabic UTF-8 text
stop_name_map = {}
for offset, sid in matches:
    chunk = raw[offset:offset+250]
    # find Arabic characters
    ar_matches = re.findall(rb'[\xd8\xd9][\x80-\xbf]{1,2}(?:[\xd8\xd9][\x80-\xbf]{1,2}|\s)+', chunk)
    for ar in ar_matches:
        txt = ar.decode('utf-8', errors='ignore').strip()
        # ignore generic words like عدلي منصور / جامعة القاهرة if it's not the station name
        if len(txt) > 2 and txt not in ["L3", "L3-57", "RDMC", "Mobility Cairo"]:
            if sid not in stop_name_map:
                stop_name_map[sid] = []
            if txt not in stop_name_map[sid]:
                stop_name_map[sid].append(txt)

print("Extracted mappings count:", len(stop_name_map))
for sid, names in sorted(stop_name_map.items()):
    print(f"ID: {sid} -> {names[:4]}")

with open("line3_stops_named.json", "w", encoding="utf-8") as out:
    json.dump(stop_name_map, out, ensure_ascii=False, indent=2)
