import os
import requests

# Set your API key and org ID here
API_TOKEN = os.getenv("RUNZERO_ORG_TOKEN")  # or replace with hardcoded token string
ORG_ID = os.getenv("RUNZERO_ORG_ID")  # or replace with hardcoded org ID
BASE_URL = "https://console.runzero.com/api/v1.0"

# Add site names here you want to keep
EXCLUDED_SITE_NAMES = {"Primary"}

HEADERS = {"Authorization": f"Bearer {API_TOKEN}", "Content-Type": "application/json"}


def get_sites():
    url = f"{BASE_URL}/org/sites"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def delete_site(site_id):
    url = f"{BASE_URL}/org/sites/{site_id}"
    response = requests.delete(url, headers=HEADERS)
    if response.status_code == 204:
        print(f"Deleted site ID: {site_id}")
    else:
        print(
            f"Failed to delete site ID: {site_id}. Status: {response.status_code} Response: {response.text}"
        )


def main():
    sites = get_sites()
    for site in sites:
        name = site.get("name")
        site_id = site.get("id")
        if name not in EXCLUDED_SITE_NAMES:
            print(f"Deleting site '{name}' (ID: {site_id})")
            delete_site(site_id)
        else:
            print(f"Skipping site '{name}' (ID: {site_id})")


if __name__ == "__main__":
    main()
