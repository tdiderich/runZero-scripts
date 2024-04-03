import requests
import os
import time
import datetime

# runZero creds
RUNZERO_BASE_URL = "https://console.runZero.com/api/v1.0"
RUNZERO_ORG_TOKEN = os.environ["RUNZERO_ORG_TOKEN"]
HEADERS = {"Authorization": f"Bearer {RUNZERO_ORG_TOKEN}"}

def metrics():
    url = RUNZERO_BASE_URL + f"/org/metrics"
    metrics = requests.get(
        url,
        headers=HEADERS,
        params={
            "site": "00000000-0000-0000-0000-000000000000",
            "start": int(time.time() - (3600 * 90 * 1000)),
            "end": int(time.time()),
        },
    )
    datapoints = metrics.json().get("00000000-0000-0000-0000-000000000000")
    for day in datapoints.keys():
        pretty_ts = datetime.datetime.fromtimestamp(int(day)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        asset_recent_count = (
            datapoints.get(day, {}).get("site", {}).get("asset_recent_count", 0)
        )
        print(pretty_ts, "-->", asset_recent_count)


def main():
    metrics()


if __name__ == "__main__":
    main()
