import requests
import os
import json
import csv

# AUTH
RUNZERO_ORG_TOKEN = os.environ["RUNZERO_ORG_TOKEN"]
HEADERS = {"Authorization": f"Bearer {RUNZERO_ORG_TOKEN}"}
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


def get_explorers():
    url = BASE_URL + "/org/explorers"
    explorers = requests.get(
        url, headers=HEADERS)
    return explorers.json()


def main():
    explorers = get_explorers()
    csv_out = []
    fields = []
    if len(explorers) > 0:
        for e in explorers:
            explorer_row = {}
            for field in fields:
                explorer_row[field] = e.get(field, "")
            for attribute in e.keys():
                explorer_row[attribute] = e[attribute]
                if attribute not in fields:
                    fields.append(attribute)

            csv_out.append(explorer_row)

    write_to_csv(
        output=csv_out,
        filename="explorers.csv",
        fieldnames=fields)


if __name__ == "__main__":
    main()
