import requests
import os
import csv
import ipaddress
import json

# auth - navigate here to create an account token: https://console.runzero.com/account
RUNZERO_ACCOUNT_TOKEN = os.environ["RUNZERO_DEMO_ACCOUNT_TOKEN"]
HEADERS = {"Authorization": f"Bearer {RUNZERO_ACCOUNT_TOKEN}"}
BASE_URL = "https://demo.runZero.com/api/v1.0"

def write_to_csv(output: list, filename: str, fieldnames: list):
    """Writes a list of dictionaries to a CSV file."""
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output)

def get_assets(token: str):
    """Gets all assets for a given organization."""
    url = f"{BASE_URL}/export/org/assets.json"
    params = {"search": "alive:t", "fields": "id,site_name,addresses"}
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def get_sites(org_id: str):
    """Gets all sites for a given organization."""
    url = f"{BASE_URL}/org/sites"
    response = requests.get(url, params={"_oid": org_id}, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def main():
    """
    Main function to count assets by subnet for each organization.
    """
    orgs = requests.get(f"{BASE_URL}/account/orgs", headers=HEADERS)
    orgs.raise_for_status()

    for o in orgs.json():
        id = o.get("id")
        sites = get_sites(id)
        org_name = o.get("name")
        export_token = o.get("export_token")
        output = []

        if not export_token:
            print(f"Skipping organization {org_name} - no export token found.")
            continue

        print(f"Processing organization: {org_name}")

        assets = get_assets(export_token)
        subnet_counts = {}

        for asset in assets:
            site = asset.get("site_name")
            if not site:
                continue

            addresses = asset.get("addresses", [])
            for address in addresses:
                try:
                    ip = ipaddress.ip_address(address)
                    if ip.version == 4:
                        subnet = ".".join(address.split(".")[:3]) + ".0/24"
                        key = (site, subnet)
                        subnet_counts[key] = subnet_counts.get(key, 0) + 1
                except ValueError:
                    # a small number of addresses are not valid IPs
                    pass

        for (site, subnet), count in subnet_counts.items():
            subnet_tags = ""
            subnet_descriptions = ""
            found_match = False
            for s in sites:
                if s.get('name') == site:
                    for defined_subnet, details in s.get('subnets', {}).items():
                        try:
                            if ipaddress.ip_network(subnet).subnet_of(ipaddress.ip_network(defined_subnet)):
                                tags = details.get('tags', {})
                                subnet_tags = ' '.join([f'{k}={v}' for k,v in tags.items()])
                                subnet_descriptions = details.get('description', '')
                                found_match = True
                                break
                        except ValueError:
                            pass
                    if found_match:
                        break
            
            output.append({
                "name": site,
                "description": "",
                "scope": "",
                "exclusion": "",
                "subnet_ranges": subnet,
                "subnet_tags": subnet_tags,
                "subnet_descriptions": subnet_descriptions,
            })

        if output:
            fieldnames = [
                "name",
                "description",
                "scope",
                "exclusion",
                "subnet_ranges",
                "subnet_tags",
                "subnet_descriptions",
            ]
            filename = f"asset-count-by-subnet-{org_name.replace(' ', '_').lower()}.csv"
            write_to_csv(output, filename, fieldnames)
            print(f"Successfully wrote asset counts to {filename}")
        else:
            print(f"No assets found to process for organization {org_name}.")

if __name__ == "__main__":
    main()
