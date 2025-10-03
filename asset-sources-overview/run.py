import json
import csv
from rich.console import Console
from rich.table import Table
from itertools import groupby

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
all_identifiers = []
asset_source_map = {}

# --- JSON Parsing ---
try:
    with open("assets.json", "r", encoding="utf-8") as f:
        assets = json.load(f)
except FileNotFoundError:
    print(
        "Error: 'assets.json' not found. Please ensure the file is in the correct directory."
    )
    exit()

# Parse the assets
for asset in assets:
    asset_id = asset.get("id")
    if not asset_id:
        continue

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
                asset_source_map[asset_id].add(source_name)
                all_identifiers.append(
                    {
                        "asset_id": asset_id,
                        "source": source_name,
                        "type": identifier_type,
                        "value": value,
                    }
                )

# --- CSV Preparation ---
all_sources_in_data = sorted(
    list(set(s for sources in asset_source_map.values() for s in sources))
)

final_rows = []
for identifier in all_identifiers:
    row = identifier.copy()
    # Add a checkmark ONLY for the source on the current row
    for source_name in all_sources_in_data:
        row[source_name] = "✅" if source_name == identifier["source"] else "❌"
    final_rows.append(row)

# Sort the final list of rows to ensure they are grouped by asset_id
final_rows.sort(key=lambda x: (x["asset_id"], x["source"], x["type"]))

# Define fieldnames here so both terminal output and CSV writer can use them
fieldnames = ["asset_id", "source", "type", "value"] + all_sources_in_data

# --- Terminal Output ---
console = Console()
# Group the sorted rows by 'asset_id' to create one table per asset
for asset_id, group in groupby(final_rows, key=lambda x: x["asset_id"]):
    table = Table(
        title=f"Asset ID: {asset_id}",
        title_style="bold magenta",
        show_header=True,
        header_style="bold cyan",
    )

    # Add table columns
    for field in fieldnames:
        table.add_column(field)

    # Add rows to this asset's table
    for row_data in group:
        table.add_row(*[str(row_data.get(field, "")) for field in fieldnames])

    console.print(table)

# --- CSV Writing ---
output_filename = "asset_sources_report.csv"
with open(output_filename, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(final_rows)

print(f"\n✅ Success! Full report has been saved to '{output_filename}'")
