import urllib.request
import re

url = "https://www.mobilitycairo.com/ar/pthv/get/proto/stoppoints-discovery-all?reseau="
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
data = urllib.request.urlopen(req).read()

# Split by LRT-14 to find station names and their 6-digit codes
blocks = re.findall(rb'place_(\d{6}).*?([A-Za-z\s]+).*?LRT-14', data, re.DOTALL)
print("Found stops associated with LRT-14:")

# Better regex: find 6 digits before LRT
matches = re.finditer(rb'(\d{6}).{1,80}LRT-14', data, re.DOTALL)
for m in matches:
    chunk = m.group(0)
    # extract station name in chunk
    names = re.findall(rb'[A-Za-z\s]{4,}', chunk)
    print("Code:", m.group(1).decode(), "Names:", [n.decode().strip() for n in names])
