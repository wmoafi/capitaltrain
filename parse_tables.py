import re

with open("page_lrt.html", "r", encoding="utf-8") as f:
    html = f.read()

# Find tables or schedule data
tables = re.findall(r'<table[^>]*>(.*?)</table>', html, re.DOTALL)
print(f"Found {len(tables)} tables")

for i, t in enumerate(tables):
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', t, re.DOTALL)
    print(f"\n--- Table {i+1} ({len(rows)} rows) ---")
    for r in rows[:15]:
        cols = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, re.DOTALL)
        clean_cols = [re.sub(r'<[^>]+>', '', c).strip() for c in cols]
        if any(clean_cols):
            print(" | ".join(clean_cols))
