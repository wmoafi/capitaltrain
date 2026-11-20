import urllib.request
import re

url = "https://www.mobilitycairo.com/ar/travel-information/lines/line-commuter-train-lrt"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(req).read().decode("utf-8")

# Find drupal settings full json
match = re.search(r'data-drupal-selector="drupal-settings-json">(.*?)</script>', html)
if match:
    import json
    data = json.loads(match.group(1))
    print(json.dumps(data, indent=2, ensure_ascii=False)[:3000])
