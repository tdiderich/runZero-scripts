import requests
import os

RUNZERO_ORG_TOKEN = os.environ["RUNZERO_ORG_TOKEN"]
HEADERS = {"Authorization": f"Bearer {RUNZERO_ORG_TOKEN}"}
BASE_URL = "https://console.runZero.com/api/v1.0"

SEARCH = "alive:f"

def main():
    url = BASE_URL + '/org/assets/bulk/delete'
    delete = requests.get(url, headers=HEADERS, params={
        "search": SEARCH})
    if delete.status_code == 200:
        print(f"Deleted all assets matching this search: {SEARCH}. This can take a while for large sets of assets, but it should be done within the next 24hrs.")
    else: 
        print(f"Failed to delete assets. Please try again.")

if __name__ == "__main__":
    main()
