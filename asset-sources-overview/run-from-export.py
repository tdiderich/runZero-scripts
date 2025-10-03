import json
import csv
from rich.console import Console
from rich.table import Table
from itertools import groupby

# --- Source ID to Name Mapping ---
FALLBACK_SOURCE_MAP = {
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


def load_assets_from_file(filename, console):
    """Loads and parses the JSON asset data from a local file."""
    try:
        console.print(f"[cyan]Loading assets from '{filename}'...[/cyan]")
        with open(filename, "r", encoding="utf-8") as f:
            assets = json.load(f)
        console.print(f"[green]Successfully loaded {len(assets)} assets.[/green]")
        return assets
    except FileNotFoundError:
        console.print(f"[bold red]Error:[/bold red] Input file '{filename}' not found.")
        return None
    except json.JSONDecodeError:
        console.print(
            f"[bold red]Error:[/bold red] Could not parse JSON from '{filename}'."
        )
        return None


def parse_and_aggregate(assets, source_map):
    """Parses asset data to find and group identifiers by source."""
    parsed_data = {}
    all_sources_in_data = set()
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
                    source_id, identifier_type = parts[1], parts[2]
                    source_name = source_map.get(str(source_id), "Unknown")
                    all_sources_in_data.add(source_name)
                    for single_value in value.split("\t"):
                        cleaned_value = single_value.strip()
                        if cleaned_value:
                            identifier_key = (identifier_type, cleaned_value)
                            parsed_data[asset_id].setdefault(identifier_key, set()).add(
                                source_name
                            )
    return parsed_data, sorted(list(all_sources_in_data))


def prepare_final_rows(parsed_data, sorted_sources):
    """Prepares the final list of dictionaries for CSV writing and terminal output."""
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
    return final_rows


def display_and_summarize(final_rows, sorted_sources, fieldnames, console):
    """Displays tables for ALL assets and prints the final summary."""
    assets_with_orphans_map = {}
    rows_by_asset = {
        asset_id: list(group)
        for asset_id, group in groupby(final_rows, key=lambda x: x["asset_id"])
    }

    console.print("\n--- [bold]Asset Details[/bold] ---")
    # --- KEY CHANGE IS HERE: Loop through all assets ---
    for asset_id, rows_for_this_asset in rows_by_asset.items():
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
                # Populate the map for the final summary
                assets_with_orphans_map.setdefault(asset_id, set()).add(source)
            else:
                source_status[source] = "normal"

        table = Table(
            title=f"Asset ID: {asset_id}",
            title_style="bold magenta",
            header_style="bold cyan",
        )

        table_fieldnames = ["type", "value", "source_count"] + sorted_sources
        for field in table_fieldnames:
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
            table.add_row(*[str(row_data.get(field, "")) for field in table_fieldnames])

        console.print(table)

    # --- Final Summary (prints after all tables) ---
    if assets_with_orphans_map:
        sorted_orphan_items = sorted(assets_with_orphans_map.items())
        console.print(
            "\n--- [bold red]Assets with Orphaned Sources Summary[/bold red] ---"
        )
        for asset_id, orphan_sources in sorted_orphan_items:
            sources_str = ", ".join(sorted(list(orphan_sources)))
            console.print(f"- {asset_id} (sources: [bold red]{sources_str}[/])")

        search_query = " OR ".join(
            [f'id:"{asset_id}"' for asset_id in sorted(assets_with_orphans_map.keys())]
        )
        console.print("\n[bold]Search Query:[/bold]")
        console.print(search_query)
    else:
        console.print(
            "\n--- [bold green]No assets with orphaned sources found.[/bold green] ---"
        )


def write_csv_report(final_rows, fieldnames, output_filename, console):
    """Writes the final aggregated data to a CSV file."""
    try:
        with open(output_filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(final_rows)
        console.print(
            f"\n✅ Success! Full aggregated report has been saved to '{output_filename}'"
        )
    except IOError as e:
        console.print(
            f"[bold red]Error:[/bold red] Could not write to file '{output_filename}'. {e}"
        )


def main():
    """Main function to run the asset analysis and reporting script."""

    console = Console()

    assets = load_assets_from_file("assets.json", console)
    if not assets:
        return

    parsed_data, sorted_sources = parse_and_aggregate(assets, FALLBACK_SOURCE_MAP)
    final_rows = prepare_final_rows(parsed_data, sorted_sources)

    fieldnames = ["asset_id", "type", "value", "source_count"] + sorted_sources

    display_and_summarize(final_rows, sorted_sources, fieldnames, console)
    write_csv_report(final_rows, fieldnames, "asset-source-report.csv", console)


if __name__ == "__main__":
    main()
