import os
import requests
import json
import argparse
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


def fetch_assets(base_url, headers, console):
    """Fetches all assets from the runZero Export API."""
    try:
        console.print("[cyan]Fetching all assets from the runZero API...[/cyan]")
        url = f"{base_url}/export/org/assets.json"
        response = requests.get(
            url, headers=headers, params={"search": "source_count:>2"}
        )
        response.raise_for_status()
        assets = response.json()
        console.print(f"[green]Successfully downloaded {len(assets)} assets.[/green]")
        return assets
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]API Error:[/bold red] Could not fetch assets. {e}")
        return None
    except json.JSONDecodeError:
        console.print(
            "[bold red]API Error:[/bold red] Failed to decode the JSON response from the server."
        )
        return None


def analyze_assets(assets, source_map):
    """Parses assets, merges related hostnames, and finds orphaned sources."""
    console = Console()
    console.print("[cyan]Analyzing assets and merging related hostnames...[/cyan]")

    # Step 1: Initial parsing into a temporary structure
    temp_parsed_data = {}
    for asset in assets:
        asset_id = asset.get("id")
        if not asset_id:
            continue
        temp_parsed_data.setdefault(asset_id, {})
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
                            temp_parsed_data[asset_id].setdefault(
                                identifier_key, set()
                            ).add(source_name)

    # Step 2: Post-processing to merge related hostnames
    parsed_data = {}
    for asset_id, identifiers in temp_parsed_data.items():
        parsed_data.setdefault(asset_id, {})

        # Corrected to use "names" instead of "hostname"
        hostname_identifiers = {
            value: sources
            for (id_type, value), sources in identifiers.items()
            if id_type == "names"
        }
        other_identifiers = {
            key: sources for key, sources in identifiers.items() if key[0] != "names"
        }

        # Directly add non-hostname identifiers to the final data
        for key, sources in other_identifiers.items():
            parsed_data[asset_id][key] = sources

        if hostname_identifiers:
            # Sort hosts by length to ensure 'TYLER-MAC' is processed before 'TYLER-MAC.local'
            sorted_hosts = sorted(hostname_identifiers.keys(), key=len)
            processed_hosts = set()

            for base_host in sorted_hosts:
                if base_host in processed_hosts:
                    continue

                processed_hosts.add(base_host)
                variants = []
                combined_sources = set(hostname_identifiers[base_host])

                # Find other FQDNs that contain this base hostname
                for other_host in sorted_hosts:
                    if other_host in processed_hosts:
                        continue
                    if base_host in other_host:
                        variants.append(other_host)
                        processed_hosts.add(other_host)
                        combined_sources.update(hostname_identifiers[other_host])

                # Create the new merged display value
                if variants:
                    display_value = f"{base_host} ({', '.join(sorted(variants))})"
                else:
                    display_value = base_host

                # Corrected to use "names" as the identifier type
                identifier_key = ("names", display_value)
                parsed_data[asset_id][identifier_key] = combined_sources

    # Step 3: Find assets with orphaned sources using the merged data
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

            orphans_for_this_asset = {
                source
                for source, counts in source_to_counts.items()
                if counts and all(c == 1 for c in counts)
            }
            if orphans_for_this_asset:
                assets_with_orphans_map[asset_id] = orphans_for_this_asset

    return assets_with_orphans_map, parsed_data


def run_summary_mode(total_assets, assets_with_orphans_map, console):
    """Displays a high-level summary of the findings."""
    num_orphaned = len(assets_with_orphans_map)
    num_clean = total_assets - num_orphaned

    console.print("\n--- [bold]Orphaned Source Summary[/bold] ---")
    console.print(f"Total assets processed: [bold]{total_assets}[/bold]")
    console.print(f"Assets with orphaned sources: [bold red]{num_orphaned}[/bold red]")
    console.print(f"Cleanly merged assets: [bold green]{num_clean}[/bold green]")

    if assets_with_orphans_map:
        search_query = " OR ".join(
            [f'id:"{asset_id}"' for asset_id in sorted(assets_with_orphans_map.keys())]
        )
        console.print("\n[bold]runZero Search Query to find these assets:[/bold]")
        console.print(search_query)
        console.print(
            "\nTo view details and perform cleanup, run with: [cyan]--mode cleanup[/cyan]"
        )


def run_cleanup_mode(
    assets, assets_with_orphans_map, parsed_data, source_map_reversed, console
):
    """Runs the full interactive table display and cleanup workflow."""
    if not assets_with_orphans_map:
        console.print(
            "\n[bold green]No assets with orphaned sources found. All done![/bold green] 🎉"
        )
        return

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

    rows_by_asset = {
        asset_id: list(group)
        for asset_id, group in groupby(final_rows, key=lambda x: x["asset_id"])
    }

    process_all = False
    asset_data_map = {asset["id"]: asset for asset in assets}

    for asset_id, orphan_sources in sorted(assets_with_orphans_map.items()):
        console.rule(f"[bold]Asset ID: {asset_id}[/bold]", style="magenta")

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

        for source_name in sorted(list(orphan_sources)):
            user_input = ""
            if not process_all:
                if source_name == "rumble":
                    prompt_text = (
                        f"\n[bold red]DELETE ASSET[/] [cyan]{asset_id}[/]? This is the primary Rumble source. "
                        f"([bold]Enter[/] to approve, [bold]all[/] to approve all, [bold]n[/] to skip)"
                    )
                else:
                    prompt_text = (
                        f"\nRemove source [bold red]{source_name}[/] from asset [cyan]{asset_id}[/]? "
                        f"([bold]Enter[/] to approve, [bold]all[/] to approve all, [bold]n[/] to skip)"
                    )
                user_input = Prompt.ask(prompt_text, default="y").lower()

            if user_input == "all":
                process_all = True
            if process_all or user_input in ["y", ""]:
                try:
                    if source_name == "rumble":
                        url = f"{BASE_URL}/org/assets/{asset_id}"
                        response = requests.delete(url, headers=HEADERS)
                        response.raise_for_status()
                        console.print(
                            f"  [green]✅ Success:[/green] Deleted asset '{asset_id}'."
                        )
                        break
                    elif source_name == "custom":
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


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Find and optionally remove orphaned sources from runZero assets."
    )
    parser.add_argument(
        "--mode",
        choices=["summary", "cleanup"],
        default="summary",
        help="Choose operation mode: 'summary' (default) for a quick overview, or 'cleanup' for the interactive removal workflow.",
    )
    args = parser.parse_args()

    console = Console()

    if not RUNZERO_TOKEN:
        console.print(
            "[bold red]Error:[/bold red] The RUNZERO_ORG_TOKEN environment variable is not set."
        )
        return

    source_map, source_map_reversed = get_source_map_from_api(
        BASE_URL, HEADERS, console
    )
    if not source_map:
        return

    assets = fetch_assets(BASE_URL, HEADERS, console)
    if not assets:
        return

    assets_with_orphans_map, parsed_data = analyze_assets(assets, source_map)

    if args.mode == "summary":
        run_summary_mode(len(assets), assets_with_orphans_map, console)
    elif args.mode == "cleanup":
        run_cleanup_mode(
            assets, assets_with_orphans_map, parsed_data, source_map_reversed, console
        )


if __name__ == "__main__":
    main()
