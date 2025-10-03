import os
import requests
import json
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from itertools import groupby

# --- Configuration ---
# Ensure you have RUNZERO_ORG_TOKEN set in your environment variables
# This uses the ORG_TOKEN, which has more permissions than an EXPORT_TOKEN
RUNZERO_TOKEN = os.environ.get("RUNZERO_ORG_TOKEN")
HEADERS = {"Authorization": f"Bearer {RUNZERO_TOKEN}"}
BASE_URL = "https://console.runZero.com/api/v1.0"

def get_source_map_from_api(base_url, headers, console):
    """Fetches the source name-to-ID mapping from the /metadata endpoint."""
    try:
        console.print("[cyan]Fetching source metadata from API...[/cyan]")
        url = f"{base_url}/metadata"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        # The 'Sources' key holds a dictionary of ID:name pairs.
        sources_dict = response.json().get("Sources", {})

        # The API gives us the forward map directly.
        source_map = sources_dict
        # We create the reverse map for easy lookups.
        source_map_reversed = {name: str(id) for id, name in sources_dict.items()}

        console.print("[green]Successfully fetched source metadata.[/green]")
        return source_map, source_map_reversed

    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]API Error:[/bold red] Could not fetch metadata. {e}")
        return None, None
    except (json.JSONDecodeError, KeyError):
        console.print(
            "[bold red]API Error:[/bold red] Failed to parse 'Sources' from metadata response."
        )
        return None, None


# --- Main Application Logic ---
def main():
    """Main function to run the asset cleanup process."""
    console = Console()

    if not RUNZERO_TOKEN:
        console.print(
            "[bold red]Error:[/bold red] The RUNZERO_ORG_TOKEN environment variable is not set."
        )
        return

    source_map, source_map_reversed = get_source_map_from_api(
        BASE_URL, HEADERS, console
    )
    if not source_map or not source_map_reversed:
        return

    try:
        console.print("[cyan]Fetching all assets from the runZero API...[/cyan]")
        url = BASE_URL + "/export/org/assets.json"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        assets = response.json()
        console.print(f"[green]Successfully downloaded {len(assets)} assets.[/green]")
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]API Error:[/bold red] Could not fetch assets. {e}")
        return
    except json.JSONDecodeError:
        console.print(
            "[bold red]API Error:[/bold red] Failed to decode the JSON response from the server."
        )
        return

    asset_data_map = {asset["id"]: asset for asset in assets}

    console.print("[cyan]Analyzing assets to find orphaned sources...[/cyan]")

    parsed_data = {}
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
                    for single_value in value.split("\t"):
                        cleaned_value = single_value.strip()
                        if cleaned_value:
                            identifier_key = (identifier_type, cleaned_value)
                            parsed_data[asset_id].setdefault(identifier_key, set()).add(
                                source_name
                            )

    assets_with_orphans_map = {}
    for asset_id, identifiers in parsed_data.items():
        all_sources_on_this_asset = {
            source for sources in identifiers.values() for source in sources
        }

        if len(all_sources_on_this_asset) > 1:
            source_to_counts = {}
            for sources in identifiers.values():
                for source_name in sources:
                    source_to_counts.setdefault(source_name, []).append(len(sources))

            orphans_for_this_asset = set()
            for source, counts in source_to_counts.items():
                if counts and all(c == 1 for c in counts):
                    orphans_for_this_asset.add(source)

            if orphans_for_this_asset:
                assets_with_orphans_map[asset_id] = orphans_for_this_asset

    if not assets_with_orphans_map:
        console.print(
            "\n[bold green]No assets with orphaned sources found. All done![/bold green] 🎉"
        )
        return

    console.print("\n--- [bold red]Assets with Orphaned Sources Found[/] ---")
    console.print(
        "The following assets have at least one source whose identifiers are completely unique (highlighted in red)."
    )

    # Pre-build the table data for easy lookup
    # This whole section is outside the loop to avoid recalculating
    all_sources_in_data = {
        s_name
        for s_set in parsed_data.values()
        for s_names in s_set.values()
        for s_name in s_names
    }
    sorted_sources = sorted(list(all_sources_in_data))
    final_rows = []
    for asset_id, identifiers in parsed_data.items():
        for (identifier_type, value), sources in identifiers.items():
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

    # Group rows by asset for quick table generation
    rows_by_asset = {
        asset_id: list(group)
        for asset_id, group in groupby(final_rows, key=lambda x: x["asset_id"])
    }

    process_all = False
    sorted_orphan_items = sorted(assets_with_orphans_map.items())

    for asset_id, orphan_sources in sorted_orphan_items:
        console.rule(f"[bold]Asset ID: {asset_id}[/bold]", style="magenta")

        # 1. Build and print the table for the current asset
        rows_for_this_asset = rows_by_asset.get(asset_id, [])
        source_status = {}
        if rows_for_this_asset:
            source_to_counts = {source: [] for source in sorted_sources}
            for row in rows_for_this_asset:
                for source_name in sorted_sources:
                    if row[source_name] == "✅":
                        source_to_counts[source_name].append(row["source_count"])

            for source, counts in source_to_counts.items():
                if not counts:
                    source_status[source] = "zero_identifiers"
                elif all(c == 1 for c in counts):
                    source_status[source] = "unique_identifiers"
                else:
                    source_status[source] = "normal"

        fieldnames = ["type", "value", "source_count"] + sorted_sources
        table = Table(title=None, show_header=True, header_style="bold cyan")
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

        # 2. Now, begin the interactive prompt for this asset
        for source_name in sorted(list(orphan_sources)):
            user_input = ""
            if not process_all:
                user_input = Prompt.ask(
                    f"\nRemove source [bold red]{source_name}[/] from asset [cyan]{asset_id}[/]? "
                    f"([bold]Enter[/] to approve, [bold]all[/] to approve all, [bold]n[/] to skip)",
                    default="y",
                ).lower()

            if user_input == "all":
                process_all = True

            if process_all or user_input in ["y", ""]:
                try:
                    if source_name == "custom":
                        custom_ids = asset_data_map.get(asset_id, {}).get(
                            "custom_integration_ids", []
                        )
                        if len(custom_ids) == 1:
                            url = f"{BASE_URL}/org/assets/{asset_id}/custom-integrations/{custom_ids[0]}/remove"
                            response = requests.delete(url, headers=HEADERS)
                            response.raise_for_status()
                            console.print(
                                f"  [green]✅ Success:[/green] Removed custom source."
                            )
                        else:
                            console.print(
                                f"  [yellow]⚠️ Skipped:[/yellow] Asset has multiple or zero custom IDs."
                            )
                    else:
                        source_id = source_map_reversed.get(source_name)
                        if source_id:
                            url = f"{BASE_URL}/org/assets/{asset_id}/sources/{source_id}/remove"
                            response = requests.delete(url, headers=HEADERS)
                            response.raise_for_status()
                            console.print(
                                f"  [green]✅ Success:[/green] Removed source '{source_name}'."
                            )
                        else:
                            console.print(
                                f"  [red]Error:[/red] Could not find ID for source '{source_name}'."
                            )
                except requests.exceptions.RequestException as e:
                    console.print(
                        f"  [bold red]API Error:[/bold red] Failed. Status: {e.response.status_code}, Msg: {e.response.text}"
                    )

            elif user_input in ["n", "no"]:
                console.print(f"  [yellow]-- Skipped.[/yellow]")
            else:
                console.print("[bold red]Cleanup aborted by user.[/bold red]")
                return

    console.print("\n[bold green]Cleanup complete![/bold green]")


if __name__ == "__main__":
    main()
