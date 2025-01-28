import json
IPS = [
    "192.168.0.8",
]
OUTPUT = []
with open("scan_exposure_full.json", "r") as file:
    for line in file:
        result = json.loads(line)
        if result.get("host") in IPS:
            OUTPUT.append(result)


with open(f"scan_exposure.json", "w") as f:
    for l in OUTPUT:
        f.write(json.dumps(l, separators=(",", ":")) + "\n")
