with open("I:/CapitalTrain/index.html", "r", encoding="utf-8") as f:
    c = f.read()

print("Contains btn-transfer-dir-l2m:", "btn-transfer-dir-l2m" in c)
print("Contains setTransferDirection:", "setTransferDirection" in c)
print("Contains Direction 2 logic (lrt_to_metro):", "LRT -> Metro" in c)
print("Contains per-station cumMins in index.html:", "cumMins" in c)
