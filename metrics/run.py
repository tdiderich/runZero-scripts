import requests
import os
import time
import datetime
import csv

# runZero creds
RUNZERO_BASE_URL = "https://console.runZero.com/api/v1.0"
RUNZERO_ORG_TOKEN = os.environ["RUNZERO_ORG_TOKEN"]
HEADERS = {"Authorization": f"Bearer {RUNZERO_ORG_TOKEN}"}


def metrics():
    # get metrics
    url = RUNZERO_BASE_URL + f"/org/metrics"
    metrics = requests.get(
        url,
        headers=HEADERS,
        params={
            "site": "00000000-0000-0000-0000-000000000000",
            "start": int(time.time() - (86400 * 365)),
            "end": int(time.time()),
        },
    )

    # CSV output
    file = open("recent_asset_trend.csv", "w", newline="")
    with file:
        # identifying header
        header = ["Date", "Recent Asset Count"]
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()

        datapoints = metrics.json().get("00000000-0000-0000-0000-000000000000")
        for day in datapoints.keys():
            pretty_ts = datetime.datetime.fromtimestamp(int(day)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            asset_recent_count = (
                datapoints.get(day, {}).get("site", {}).get("asset_recent_count", 0)
            )
            writer.writerow({"Date": pretty_ts, "Recent Asset Count": asset_recent_count})


def main():
    metrics()


if __name__ == "__main__":
    main()
