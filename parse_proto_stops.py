import urllib.request
import re

url = "https://www.mobilitycairo.com/ar/pthv/get/proto/stoppoints-discovery-all?reseau="
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
data = urllib.request.urlopen(req).read()

# The response is protobuf containing stop points
# Let's extract ASCII strings from the bytes
strings = re.findall(rb'[\x20-\x7E]{3,}', data)
decoded = [s.decode('ascii', errors='ignore') for s in strings]
print("Found strings:", len(decoded))
lrt_matches = [s for s in decoded if any(k in s.lower() for k in ['lrt', 'mansour', 'badr', 'shorouk', 'obour', 'culture', 'arts', 'capital', 'knowledge', 'zone', 'heliopolis'])]
print("\nLRT matches:")
for m in set(lrt_matches):
    print(" -", m)
