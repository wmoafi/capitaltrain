import urllib.request
import re

url = "https://www.mobilitycairo.com/ar/travel-information/lines/line-commuter-train-lrt"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(req).read().decode("utf-8")

# Extract tables
tables = re.findall(r'<table[^>]*>(.*?)</table>', html, re.DOTALL)
print(f"Found {len(tables)} tables")

for i, t in enumerate(tables):
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', t, re.DOTALL)
    print(f"\n=================== TABLE {i+1} ({len(rows)} rows) ===================")
    for r in rows:
        cols = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, re.DOTALL)
        clean_cols = [" ".join(re.sub(r'<[^>]+>', ' ', c).split()) for c in cols]
        if any(clean_cols):
            print(" | ".join(clean_cols))
