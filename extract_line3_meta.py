import re
import json

with open("node83.html", "r", encoding="utf-8") as f:
    html = f.read()

# Find <apthschedule ...>
apth = re.findall(r'<apthschedule[^>]*>', html)
for a in apth:
    print("APTH TAG:", a)

# Find stopareas in thermometer
stops = re.findall(r'data-stoparea-id=["\']?([^"\'>\s]+)["\']?[^>]*>([^<]+)', html)
print(f"Stops found in html: {len(stops)}")

# Find drupal settings json
m = re.search(r'<script type="application/json" data-drupal-selector="drupal-settings-json">(.*?)</script>', html, re.DOTALL)
if m:
    data = json.loads(m.group(1))
    with open("drupal_line3.json", "w", encoding="utf-8") as out:
        json.dump(data, out, ensure_ascii=False, indent=2)
    print("Saved drupal_line3.json successfully!")
    print("Keys:", list(data.keys()))
