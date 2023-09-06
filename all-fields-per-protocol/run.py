import requests
import os
import csv

RUNZERO_EXPORT_TOKEN = os.environ["RUNZERO_EXPORT_TOKEN"]
HEADERS = {"Authorization": f"Bearer {RUNZERO_EXPORT_TOKEN}"}
BASE_URL = "https://console.runZero.com/api/v1.0"


def write_to_csv(output: dict, filename: str, fieldnames: list):
    file = open(filename, "w")
    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )
    writer.writeheader()
    writer.writerows(output)
    file.close()


def main():
    tracker = {}
    url = BASE_URL + "/export/org/assets.json?"
    data = requests.get(url, headers=HEADERS)
    assets = data.json()
    for a in assets:
        services = a["services"]
        for s in services.keys():
            protocol = services[s].get("protocol", "NONE")
            if protocol in tracker:
                for k in services[s].keys():
                    tracker[protocol][k] = services[s][k]
            else:
                tracker[protocol] = {}
                for k in services[s].keys():
                    tracker[protocol][k] = services[s][k]
    output = []
    for k in tracker.keys():
        for f in tracker[k]:
            output.append({
                "protocol": k,
                "field": f,
                "sample": tracker[k][f]
            })

    write_to_csv(
        output=output,
        filename="sample_fields.csv",
        fieldnames=[
            "protocol",
            "field",
            "sample"
        ]
    )


if __name__ == "__main__":
    main()
