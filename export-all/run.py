import os
import requests
from dotenv import load_dotenv

# load environment variables from .env file
load_dotenv()

# RUNZERO_ACCOUNT_TOKEN should be an account-level API key with permission to list organizations
RUNZERO_ACCOUNT_TOKEN = os.environ.get("RUNZERO_ACCOUNT_TOKEN")
BASE_URL = os.environ.get("RUNZERO_BASE_URL", "https://console.runzero.com/api/v1.0")

# Headers for account-level API calls
ACCOUNT_HEADERS = {"Authorization": f"Bearer {RUNZERO_ACCOUNT_TOKEN}"}

# fields to export
EXPORT_FIELDS = [
    "id",
    "os",
    "os_version",
    "macs",
    "ip",
    "hostname",
    "type",
    "source_count",
    "first_seen",
    "last_seen",
]

def main():
    if not RUNZERO_ACCOUNT_TOKEN:
        print("error: RUNZERO_ACCOUNT_TOKEN environment variable not set.")
        print("Please set this to an Account-level API key.")
        return

    try:
        # Get all organizations
        orgs_url = BASE_URL + "/account/orgs"
        response = requests.get(orgs_url, headers=ACCOUNT_HEADERS)
        response.raise_for_status()  # Raise an exception for bad status codes
        orgs = response.json()

        print(f"Found {len(orgs)} organizations.")

        # Loop through all organizations
        for org in orgs:
            org_name = org.get("name")
            export_token = org.get("export_token")
            
            # Sanitize org_name for filename
            safe_org_name = org_name.replace(" ", "_").replace("/", "_")

            if not export_token:
                print(f"Skipping org '{org_name}': Export token not available in the API response.")
                print("  - Please ensure an export token is generated for this organization in the runZero console.")
                continue

            print(f"Exporting assets for org: {org_name}")

            # Headers for org-level export
            org_headers = {"Authorization": f"Bearer {export_token}"}
            
            # URL for exporting assets from the organization
            export_url = BASE_URL + "/export/org/assets.csv"
            
            params = {
                "fields": ",".join(EXPORT_FIELDS)
            }

            # Export assets to csv
            asset_response = requests.get(export_url, headers=org_headers, params=params)
            asset_response.raise_for_status()

            filename = f"{safe_org_name}_assets.csv"
            output_path = os.path.join("export-all", filename)

            with open(output_path, "w", newline="", encoding="utf-8") as f:
                f.write(asset_response.text)
            
            print(f"  - Assets exported to {output_path}")

    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e}")
        if e.response.status_code == 401:
            print("Authentication failed. Please check your RUNZERO_ACCOUNT_TOKEN.")
        print(f"Response content: {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()