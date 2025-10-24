#!/usr/bin/env python3
import os
import requests
import sys
import logging

RUNZERO_ORG_TOKEN = os.environ.get("RUNZERO_ORG_TOKEN")
if not RUNZERO_ORG_TOKEN:
    print("❌ RUNZERO_ORG_TOKEN not set in environment.")
    sys.exit(1)

HEADERS = {"Authorization": f"Bearer {RUNZERO_ORG_TOKEN}"}
BASE_URL = "https://console.runzero.com/api/v1.0"


def main():
    print("📡 Fetching all sites from /org/sites...")
    resp = requests.get(BASE_URL + "/org/sites", headers=HEADERS)

    if not resp.ok:
        print(f"❌ Failed to fetch sites: {resp.status_code} {resp.text}")
        sys.exit(1)

    sites = resp.json()
    print(f"✅ Found {len(sites)} sites. Processing each one...\n")

    for site in sites:
        site_name = site.get("name", "Unnamed Site")
        subnets = site.get("subnets", {})

        if not subnets:
            print(f"⚠️  No subnets found for site '{site_name}'. Skipping.\n")
            continue

        print(f"🏷 Processing site: {site_name}")
        for subnet, subnet_data in subnets.items():
            tags_dict = subnet_data.get("tags", {})

            if not tags_dict:
                print(f"  ⚠️  Subnet {subnet} has no tags. Skipping.")
                continue

            # Convert dict to string of "key=value" pairs separated by spaces
            tags_str = " ".join(f"{k}={v}" if v else k for k, v in tags_dict.items())

            payload = {"search": f"net:{subnet}", "tags": tags_str}

            print(f"  🌐 Applying tags '{tags_str}' to subnet {subnet}...")

            response = requests.patch(
                f"{BASE_URL}/org/assets/bulk/tags", headers=HEADERS, json=payload
            )

            if response.ok:
                print(
                    f"  ✅ Successfully initiated bulk tag update for subnet {subnet}"
                )
            else:
                print(
                    f"  ❌ Failed to tag subnet {subnet}: {response.status_code} {response.text}"
                )

        print(f"--- Finished site: {site_name} ---\n")

    print("🎉 Site subnet tag propagation completed.")


if __name__ == "__main__":
    main()
