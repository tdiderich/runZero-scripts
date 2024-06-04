# Populate demo data in runZero

## Sources currently supported

1. runZero scan
2. CrowdStrike integration
3. Nessus integration

## How it works

- This script uses real data to generate fake runZero tasks 
- There are data maps that randomize the asset types + add integration data in cases that make sense
- The output files can be gzip-ed + uploaded to a tenant to populate the inventory 