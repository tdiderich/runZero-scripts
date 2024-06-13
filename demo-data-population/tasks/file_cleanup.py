import json
IPS = [
    "194.116.41.76",
]
OUTPUT = []
with open("scan_tplink.json", "r") as file:
    for line in file:
        result = json.loads(line)
        if result.get("host") in IPS:
            OUTPUT.append(result)


with open(f"scan_lab_printer_updated.json", "w") as f:
    for l in OUTPUT:
        f.write(json.dumps(l, separators=(",", ":")) + "\n")
