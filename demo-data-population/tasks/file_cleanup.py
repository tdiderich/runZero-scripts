import json
import gzip

IPS = [
    "198.51.100.3",  # Database Accessible Without Authentication
    "198.51.100.5",
    "10.0.19.1",  # End-of-Life Asset
    "10.0.9.41",  # Widely Shared Private Key
    "10.0.8.11",
    "10.0.8.28",
    "10.0.3.13",
    "23.20.4.34",  # Internet Exposed Database
    "23.20.1.49",
    "10.0.20.8",  # Potential External Access To Internal Asset
    "197.51.100.222",  # Publicly Exposed Operational Technology Service
    "198.51.100.17",  # KEV
    "10.0.3.43",  # Rapid Response: Services
    "10.0.18.9",  # Obsolete Protocol
    "10.0.19.36",
    "10.0.11.21",  # Remote Code Execution Vulnerability
    "10.0.16.49",
    "10.0.19.1",
]
OUTPUT = []
WRITE = True

# Open the gzipped JSON file
with gzip.open("consolidated.json.gz", "rt") as file:
    for line in file:
        result = json.loads(line)
        if result.get("host") in IPS:
            OUTPUT.append(result)

# Write the output to a new JSON file (not gzipped)
if WRITE:
    with open("findings_consolidated.json", "w") as f:
        for l in OUTPUT:
            f.write(json.dumps(l, separators=(",", ":")) + "\n")
else: 
    print(f"Found {len(OUTPUT)} results")
