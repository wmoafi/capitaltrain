import urllib.request
import json

base_api = "https://www.mobilitycairo.com/ar/pthv/get"
url = f"{base_api}/stops-line-discovery?max=1000&reseau=&line=LRT-14&direction=&onlyphysicals=0"

req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
resp = urllib.request.urlopen(req)
obj = json.loads(resp.read().decode("utf-8"))

items = obj["items"]
if "TransfersLines" in items:
    del items["TransfersLines"]

print("=== ALL STATIONS FOR LRT ===")
stations = []
for k, v in items.items():
    name = v.get("StopName", {}).get("value", "")
    spoints = list(v.get("spoints", {}).keys())
    ref = v.get("StopPointRef")
    print(f"{name} | Ref: {ref} | SPoints: {spoints}")
    stations.append({"name": name, "ref": ref, "spoints": spoints})

# Save to json file
with open("lrt_official_stops.json", "w", encoding="utf-8") as f:
    json.dump(stations, f, ensure_ascii=False, indent=2)
print("\nSaved lrt_official_stops.json successfully!")
