import json
import gzip

IPS = ["192.168.40.167", "192.168.40.246", "192.168.40.254", "192.168.40.4 "]
OUTPUT = []
WRITE = True

# Open the gzipped JSON file
with gzip.open("default_creds.json.gz", "rt") as file:
    for line in file:
        result = json.loads(line)
        if result.get("host") in IPS:
            OUTPUT.append(result)

# Write the output to a new JSON file (not gzipped)
if WRITE:
    with open("default_creds.json", "w") as f:
        for l in OUTPUT:
            f.write(json.dumps(l, separators=(",", ":")) + "\n")
else: 
    print(f"Found {len(OUTPUT)} results")
