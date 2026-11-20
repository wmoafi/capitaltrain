import urllib.request
import json

base_api = "https://www.mobilitycairo.com/ar/pthv/get"
url = f"{base_api}/stops-line-discovery?max=1000&reseau=&line=LRT-14&direction=&onlyphysicals=0"

print("Calling:", url)
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
resp = urllib.request.urlopen(req)
data = resp.read().decode("utf-8")
print("Response length:", len(data))
obj = json.loads(data)
print("Keys:", obj.keys() if isinstance(obj, dict) else "not dict")
if "items" in obj:
    print("Items keys:", list(obj["items"].keys())[:10])
    first_item = list(obj["items"].values())[0]
    print("First item sample:", json.dumps(first_item, indent=2, ensure_ascii=False))
