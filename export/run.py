from email import header
import requests
import os

RUMBLE_EXPORT_TOKEN = os.environ["RUMBLE_EXPORT_TOKEN"]
HEADERS = {"Authorization": f"Bearer {RUMBLE_EXPORT_TOKEN}"}
BASE_URL = "https://console.rumble.run/api/v1.0"


def main():
    search = "source:crowdstrike"
    url = BASE_URL + "/export/org/assets.json"
    assets = requests.get(
        url,
        headers=HEADERS,
        params={"search": search},
    )
    print(assets.json())


if __name__ == "__main__":
    main()
