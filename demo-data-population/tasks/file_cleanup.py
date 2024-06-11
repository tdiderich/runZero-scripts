import json
IPS = [
    "192.168.30.20",
    "192.168.40.73",
]
OUTPUT = []
with open("scan_lab_printer.json", "r") as file:
    for line in file:
        result = json.loads(line)
        if result.get("host") in IPS:
            OUTPUT.append(result)


with open(f"scan_lab_printer_updated.json", "w") as f:
    for l in OUTPUT:
        f.write(json.dumps(l, separators=(",", ":")) + "\n")
