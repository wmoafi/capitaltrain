import urllib.request
import re

url = "https://www.mobilitycairo.com/ar/travel-information/lines/line-commuter-train-lrt"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(req).read().decode("utf-8")

# Let's find all script tags in HTML and print their filenames
scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', html)
for s in scripts:
    print(s)
