import requests
import os

RUNZERO_ORG_TOKEN = os.environ["RUNZERO_ORG_TOKEN"]
HEADERS = {"Authorization": f"Bearer {RUNZERO_ORG_TOKEN}"}
BASE_URL = "https://console.runZero.com/api/v1.0"
RUNZERO_ORG_ID = os.environ["RUNZERO_ORG_ID"]

SEARCH = "(source:aws or source:gcp or source:azure) and last_seen:>2days"


def get_delete_ids():
    assets = []
    url = BASE_URL + "/export/org/assets.json"
    get_assets = requests.get(url=url, headers=HEADERS, params={
                              "search": SEARCH, "fields": "id"})
    if get_assets.status_code == 200:
        assets = [x["id"] for x in get_assets.json()]

    return assets


def delete_assets(assets: list):
    url = BASE_URL + "/org/assets/bulk/delete"
    delete = requests.delete(url, headers=HEADERS, json={
        "asset_ids": assets})

    if delete.status_code == 204:
        print(
            f"Deleted all assets matching this search: {SEARCH}. This can take a while for large sets of assets, but it should be done within the next 24hrs.")
    else:
        print(delete.text)
        print(f"Failed to delete assets. Please try again.")


def main():
    assets = get_delete_ids()
    print(assets)
    delete_assets(assets=assets)


if __name__ == "__main__":
    main()
