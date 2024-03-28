import requests
import config
import time

RUNZERO_EXPORT_TOKEN = config.config_vars["RUNZERO_EXPORT_TOKEN"]
HEADERS = {"Authorization": f"Bearer {RUNZERO_EXPORT_TOKEN}"}
BASE_URL = "https://console.runZero.com/api/v1.0"
SUMO_HTTP_ENDPOINT = config.config_vars["SUMO_HTTP_ENDPOINT"]

SEARCHES = [
    {
        "name": "Policy: Assets with public and private network connections",
        "type": "assets",
        "search": "haspublic:true AND hasprivate:true",
        "denominator": "alive:t",
    },
    {
        "name": "Policy: Services with soon to expire TLS certificates",
        "type": "services",
        "search": "_asset.protocol:tls AND tls.notAfterTS:<6weeks",
        "denominator": "alive:t protocol:tls",
    },
    {
        "name": "Policy: Services with expired TLS certificates",
        "type": "services",
        "search": "_asset.protocol:tls AND tls.notAfterTS:<now",
        "denominator": "alive:t protocol:tls",
    },
]


def handle_search(search, type):
    url = (
        BASE_URL + "/export/org/assets.json"
        if type == "assets"
        else BASE_URL + "/export/org/services.json"
    )
    data = requests.get(
        url, headers=HEADERS, params={"search": "alive:t " + search, "fields": "id"}
    )
    return data


def main(event, context):
    print(event)
    print(context)
    for search in SEARCHES:
        search_data = handle_search(search=search["search"], type=search["type"])
        search_count = len(search_data.json())
        asset_ids = []
        for id in search_data.json():
            asset_ids.append(id["id"])

        denominator_data = handle_search(
            search=search["denominator"], type=search["type"]
        )
        denominator_count = len(denominator_data.json())

        percentage = round((search_count / denominator_count) * 100)

        search["search_count"] = search_count
        search["denominator_count"] = denominator_count
        search["percentage"] = percentage
        search["timestamp"] = int(time.time())
        search["asset_ids"] = asset_ids
        search_link = (
            "https://console.runzero.com/inventory?search="
            if search["type"] == "assets"
            else "https://console.runzero.com/inventory/services?search="
        )
        for i, id in enumerate(asset_ids):
            if i == 0:
                search_link += (
                    "service_id:" + id if search["type"] == "services" else "id:" + id
                )
            else:
                search_link += (
                    "%20OR%20service_id:" + id
                    if search["type"] == "services"
                    else "%20OR%20id:" + id
                )
        search["search_link"] = search_link

        requests.post(SUMO_HTTP_ENDPOINT, json=search)


if __name__ == "__main__":
    main("data", "context")
