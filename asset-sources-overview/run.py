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
    "18": "ms3d_runtime",
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

# --- Data Structure for Aggregation ---
parsed_data = {}
all_sources_in_data = set()

# --- JSON Parsing ---
# (This section is unchanged)
try:
    with open("assets.json", "r", encoding="utf-8") as f:
        assets = json.load(f)
except FileNotFoundError:
    print(
        "Error: 'assets.json' not found. Please ensure the file is in the correct directory."
    )
    exit()

for asset in assets:
    asset_id = asset.get("id")
    if not asset_id:
        continue
    parsed_data.setdefault(asset_id, {})
    attributes = asset.get("attributes", {})
    for key, value in attributes.items():
        if not value:
            continue
        if key.startswith("_source"):
            parts = key.split(".")
            if len(parts) == 3:
                source_id, identifier_type, source_name = (
                    parts[1],
                    parts[2],
                    source_map.get(str(parts[1]), "Unknown"),
                )
                all_sources_in_data.add(source_name)
                for single_value in value.split("\t"):
                    cleaned_value = single_value.strip()
                    if cleaned_value:
                        identifier_key = (identifier_type, cleaned_value)
                        parsed_data[asset_id].setdefault(identifier_key, set()).add(
                            source_name
                        )

# --- CSV Preparation from Aggregated Data ---
# (This section is unchanged)
sorted_sources = sorted(list(all_sources_in_data))
final_rows = []
for asset_id, identifiers in parsed_data.items():
    for identifier_key, sources in identifiers.items():
        identifier_type, value = identifier_key
        row = {
            "asset_id": asset_id,
            "type": identifier_type,
            "value": value,
            "source_count": len(sources),
        }
        for source_name in sorted_sources:
            row[source_name] = "✅" if source_name in sources else "❌"
        final_rows.append(row)

final_rows.sort(key=lambda x: (x["asset_id"], x["type"], x["value"]))
fieldnames = ["asset_id", "type", "value", "source_count"] + sorted_sources

# --- Terminal Output with Dual Highlighting ---
console = Console()
assets_with_orphans_map = (
    {}
)  # <-- NEW: Dictionary to store IDs and their orphan sources

for asset_id, group in groupby(final_rows, key=lambda x: x["asset_id"]):
    rows_for_this_asset = list(group)

    source_to_counts = {source: [] for source in sorted_sources}
    for row in rows_for_this_asset:
        for source_name in sorted_sources:
            if row[source_name] == "✅":
                source_to_counts[source_name].append(row["source_count"])

    source_status = {}
    for source, counts in source_to_counts.items():
        if not counts:
            source_status[source] = "zero_identifiers"
        elif all(c == 1 for c in counts):
            source_status[source] = "unique_identifiers"
        else:
            source_status[source] = "normal"

    # --- KEY CHANGE IS HERE ---
    # Find the specific sources that have only unique identifiers
    orphans_for_this_asset = {
        source
        for source, status in source_status.items()
        if status == "unique_identifiers"
    }
    # If we found any, add them to our map
    if orphans_for_this_asset:
        assets_with_orphans_map[asset_id] = orphans_for_this_asset
    # --- END OF KEY CHANGE ---

    table = Table(
        title=f"Asset ID: {asset_id}",
        title_style="bold magenta",
        header_style="bold cyan",
    )

    for field in fieldnames:
        status = source_status.get(field)
        if status == "zero_identifiers":
            table.add_column(f"[bold yellow]{field}[/]")
        elif status == "unique_identifiers":
            table.add_column(f"[bold red]{field}[/]")
        elif field == "source_count":
            table.add_column(field, justify="center", style="bold")
        else:
            table.add_column(field)

    for row_data in rows_for_this_asset:
        table.add_row(*[str(row_data.get(field, "")) for field in fieldnames])

    console.print(table)

# --- CSV Writing ---
# (This section is unchanged)
output_filename = "asset_sources_report_aggregated.csv"
with open(output_filename, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(final_rows)

print(f"\n✅ Success! Aggregated report has been saved to '{output_filename}'")

# --- REWRITTEN: Orphaned Asset Summary ---
if assets_with_orphans_map:
    sorted_orphan_items = sorted(assets_with_orphans_map.items())
    console.print("\n--- [bold red]Assets with Orphaned Sources[/] ---")
    console.print(
        "The following assets have at least one source whose identifiers are completely unique (highlighted in red)."
    )

    # Print the list of IDs and their specific orphan sources
    for asset_id, orphan_sources in sorted_orphan_items:
        sources_str = ", ".join(sorted(list(orphan_sources)))
        console.print(f"- {asset_id} (sources: [bold red]{sources_str}[/])")

    # Print the search query
    search_query = " OR ".join(
        [f'id:"{asset_id}"' for asset_id in sorted(assets_with_orphans_map.keys())]
    )
    console.print("\n[bold]Search Query:[/bold]")
    console.print(search_query)
else:
    console.print("\n--- [bold green]No assets with orphaned sources found.[/] ---")
