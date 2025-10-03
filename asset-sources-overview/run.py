import json
import csv
from rich.console import Console
from rich.table import Table
from itertools import groupby

# --- Source ID to Name Mapping ---
# (This section is unchanged)
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

# --- NEW: Data Structure for Aggregation ---
# This new structure will group sources under each unique identifier
# Format: { asset_id: { (type, value): {source1, source2} } }
parsed_data = {}
all_sources_in_data = set()

# --- JSON Parsing ---
try:
    with open("assets.json", "r", encoding="utf-8") as f:
        assets = json.load(f)
except FileNotFoundError:
    print(
        "Error: 'assets.json' not found. Please ensure the file is in the correct directory."
    )
    exit()

# --- REWRITTEN: Parse and Aggregate the Data ---
for asset in assets:
    asset_id = asset.get("id")
    if not asset_id:
        continue

    # Ensure the asset_id key exists in our data structure
    parsed_data.setdefault(asset_id, {})

    attributes = asset.get("attributes", {})
    for key, value in attributes.items():
        if not value:
            continue
        if key.startswith("_source"):
            parts = key.split(".")
            if len(parts) == 3:
                source_id = parts[1]
                identifier_type = parts[2]
                source_name = source_map.get(str(source_id), "Unknown")

                # This is a unique identifier (e.g., ('macs', '00:1A:...'))
                identifier_key = (identifier_type, value)

                # Ensure the set of sources for this identifier exists
                parsed_data[asset_id].setdefault(identifier_key, set())

                # Add the current source to the set for this identifier
                parsed_data[asset_id][identifier_key].add(source_name)
                all_sources_in_data.add(source_name)

# --- REWRITTEN: CSV Preparation from Aggregated Data ---
sorted_sources = sorted(list(all_sources_in_data))
final_rows = []

for asset_id, identifiers in parsed_data.items():
    for identifier_key, sources in identifiers.items():
        identifier_type, value = identifier_key

        row = {
            "asset_id": asset_id,
            "type": identifier_type,
            "value": value,
        }

        # Now, add the checkmarks based on the sources for this specific identifier
        for source_name in sorted_sources:
            row[source_name] = "✅" if source_name in sources else "❌"

        final_rows.append(row)

# Sort the final list of rows for clear, grouped readability
final_rows.sort(key=lambda x: (x["asset_id"], x["type"], x["value"]))

# Define fieldnames for the new data structure (no more 'source' column)
fieldnames = ["asset_id", "type", "value"] + sorted_sources

# --- Terminal Output (Unchanged logic, works with new data) ---
console = Console()
for asset_id, group in groupby(final_rows, key=lambda x: x["asset_id"]):
    table = Table(
        title=f"Asset ID: {asset_id}",
        title_style="bold magenta",
        show_header=True,
        header_style="bold cyan",
    )
    for field in fieldnames:
        table.add_column(field)
    for row_data in group:
        table.add_row(*[str(row_data.get(field, "")) for field in fieldnames])
    console.print(table)

# --- CSV Writing (Unchanged logic, works with new data) ---
output_filename = "asset_sources_report_aggregated.csv"
with open(output_filename, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(final_rows)

print(f"\n✅ Success! Aggregated report has been saved to '{output_filename}'")
