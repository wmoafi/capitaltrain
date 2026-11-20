import urllib.request
import re
import json

url = "https://www.mobilitycairo.com/ar/pthv/get/proto/stoppoints-discovery?line=L3-57"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
raw = urllib.request.urlopen(req).read()

# Let's inspect chunks in raw binary
# In GTFS protobuf / JSON-like stream, stop points usually have ID (e.g. 139xxx) followed by Name
# Let's find all pairs of (ID, Arabic Name)
pattern = rb'(\d{6})[^\x00-\x1f\x7f-\xff]*?([\xd8\xd9][\x80-\xbf]{1,2}(?:[\xd8\xd9][\x80-\xbf]{1,2}|\s)+)'

# Or let's test querying stop-stoptimes-discovery with each ID!
ids = set([n.decode() for n in re.findall(rb'\b139\d{3}\b', raw)])
print(f"Total IDs to test: {len(ids)}")

valid_line3_stops = {}

for sid in ids:
    test_url = f"https://www.mobilitycairo.com/ar/pthv/get/stop-stoptimes-discovery?nbtimes=1&stop={sid}&reseau=&date=2026-11-10&heure=10:00:00"
    r = urllib.request.Request(test_url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(r, timeout=4) as resp:
            text = resp.read().decode('utf-8')
            if text != "false" and "items" in text:
                data = json.loads(text)
                items = data.get("items", {})
                for k, v in items.items():
                    # check if this is L3-57
                    if "L3-57" in k or v.get("RouteId") == "L3-57" or "L3" in v.get("ShortName", ""):
                        # Extract stop name from schedule
                        sched = v.get("Schedule", [])
                        st_name = ""
                        if sched:
                            st_name = sched[0].get("from_stop_name") or sched[0].get("to_stop_name") or ""
                        dir_label = v.get("DirLabel") or v.get("DirLib") or ""
                        print(f"MATCH! Stop {sid} -> {st_name} | Key: {k} | Dir: {dir_label}")
                        valid_line3_stops[sid] = {
                            "id": sid,
                            "name": st_name,
                            "key": k,
                            "dir": dir_label
                        }
    except Exception as e:
        pass

with open("line3_verified_stops.json", "w", encoding="utf-8") as out:
    json.dump(valid_line3_stops, out, ensure_ascii=False, indent=2)
print("Saved line3_verified_stops.json with", len(valid_line3_stops), "stops!")
