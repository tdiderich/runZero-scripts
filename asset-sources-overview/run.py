import json
import csv

# --- Source ID to Name Mapping ---
source_map = {
    "1": "rumble",
    "2": "miradore",
    "3": "aws",
    "4": "crowdstrike",
    "5": "azure",
    "6": "censys",
    "7": "vmware",
    "8": "gcp",
    "9": "sentinelone",
    "10": "tenable",
    "11": "nessus",
    "12": "rapid7",
    "13": "insightvm",
    "14": "qualys",
    "15": "shodan",
    "16": "azuread",
    "17": "ldap",
    "18": "ms365defender",
    "19": "intune",
    "20": "googleworkspace",
    "21": "sample",
    "22": "tenablesecuritycenter",
    "23": "packet",
    "24": "wiz",
    "25": "meraki",
    "26": "mecm",
    "27": "tanium",
    "28": "simulator",
    "29": "netbox",
    "30": "cip",
    "31": "pan",
    "32": "prisma",
    "34": "dragos",
    "-1": "custom",
}

# --- Data Structures ---
# To store the detailed list of every identifier found
all_identifiers = []
# To map each asset ID to the set of sources it has
asset_source_map = {}

# --- JSON Parsing ---
# Assuming 'assets.json' is in the same directory
try:
    with open("assets.json", "r", encoding="utf-8") as f:
        assets = json.load(f)
except FileNotFoundError:
    print(
        "Error: 'assets.json' not found. Please ensure the file is in the correct directory."
    )
    exit()

# Parse the assets, collecting both detailed identifiers and the summary of sources per asset
for asset in assets:
    asset_id = asset.get("id")
    if not asset_id:
        continue

    # Initialize a set for the asset if it's the first time we've seen it
    if asset_id not in asset_source_map:
        asset_source_map[asset_id] = set()

    attributes = asset.get("attributes", {})
    for key, value in attributes.items():
        if value == "":
            continue
        if key.startswith("_source"):
            parts = key.split(".")
            if len(parts) == 3:
                source_id = parts[1]
                identifier_type = parts[2]
                source_name = source_map.get(str(source_id), "Unknown")

                # Add the source name to this asset's set of sources
                asset_source_map[asset_id].add(source_name)

                # Append a dictionary with the full identifier details
                all_identifiers.append(
                    {
                        "asset_id": asset_id,
                        "source": source_name,
                        "type": identifier_type,
                        "value": value,
                    }
                )

# --- CSV Preparation ---

# Get a sorted list of all unique source names to use as the summary columns
all_sources_in_data = sorted(
    list(set(s for sources in asset_source_map.values() for s in sources))
)

# Build the final list of rows for the CSV
final_rows = []
for identifier in all_identifiers:
    asset_id = identifier["asset_id"]
    # Get the set of all sources associated with this identifier's parent asset
    sources_for_this_asset = asset_source_map.get(asset_id, set())

    # Create a new row, starting with the identifier's specific details
    row = identifier.copy()

    # Add the summary columns (✅/❌) for all possible sources
    for source_name in all_sources_in_data:
        row[source_name] = "✅" if source_name in sources_for_this_asset else "❌"

    final_rows.append(row)

# Sort the final list of rows for clear, grouped readability
final_rows.sort(key=lambda x: (x["asset_id"], x["source"], x["type"]))


# --- CSV Writing ---

# The header will be the identifier fields plus a column for each source
fieldnames = ["asset_id", "source", "type", "value"] + all_sources_in_data
output_filename = "asset_sources_report.csv"

# Write the data to the CSV file
with open(output_filename, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(final_rows)

print(f"✅ Success! Your source report has been written to '{output_filename}'")
