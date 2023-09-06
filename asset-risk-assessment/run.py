import requests
import os
import csv
import json

# auth - navigate here to create an account token: https://console.runzero.com/account
RUNZERO_ACCOUNT_TOKEN = os.environ["RUNZERO_ACCOUNT_TOKEN"]
HEADERS = {"Authorization": f"Bearer {RUNZERO_ACCOUNT_TOKEN}"}
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


def handle_org(token: str, name: str):
    print(f"handling {name}...")
    # check for folder or create
    if not os.path.exists(name):
        os.mkdir(name)

    # create export headers
    headers = {"Authorization": f"Bearer {token}"}

    # dicts for tracking counts and data
    executive_report = []
    asset_report = {}
    risk_report = []

    # queries to run
    queries = open("queries.csv", "r")
    reader = csv.reader(queries, delimiter=",")

    for row in reader:

        # skip headers
        if row[0] != "name":
            search_name = row[0]
            description = row[1]
            search_type = row[2]
            severity = row[4]
            query = row[5]

            if search_type == "assets":
                url = BASE_URL + "/export/org/assets.json?"
            elif search_type == "services":
                url = BASE_URL + "/export/org/services.json?"
            elif search_type == "wireless":
                url = BASE_URL + "/export/org/wireless.json?"
            else:
                print(f"non supported search type {search_type}")

            data = requests.get(url, headers=headers, params={
                                "search": query, "fields": "id,addresses,addresses_extra,names"})

            if data.status_code == 200:
                results = data.json()

                if len(results) > 0:
                    executive_report.append({
                        "org_name": name,
                        "search_name": search_name,
                        "search_description": description,
                        "search_type": search_type,
                        "severity": severity,
                        "count": len(results)
                    })

                    risk_report.append({
                        "org_name": name,
                        "search_name": search_name,
                        "search_description": description,
                        "search_type": search_type,
                        "severity": severity,
                        "count": len(results),
                        "asset_ids": [x["id"] for x in results]
                    })

                    for asset in results:
                        if asset["id"] in asset_report.keys():
                            asset_report[asset["id"]]["risks"].append(
                                search_name)
                        else:
                            asset_report[asset["id"]] = {
                                "org_name": name,
                                "id": asset.get("id", ""),
                                "addresses": asset.get("addresses", ""),
                                "addresses_extra": asset.get("addresses_extra", ""),
                                "names": asset.get("names", ""),
                                "risks": [search_name]
                            }

            else:
                print(f"{search_name} caused a non-200")

    write_to_csv(
        output=executive_report,
        filename=f"{name}/exec_report.csv",
        fieldnames=[
            "org_name",
            "search_name",
            "search_description",
            "search_type",
            "severity",
            "count"
        ])

    write_to_csv(
        output=risk_report,
        filename=f"{name}/risk_report.csv",
        fieldnames=[
            "org_name",
            "search_name",
            "search_description",
            "search_type",
            "severity",
            "count",
            "asset_ids"
        ])

    asset_report_csv = []
    for a in asset_report.keys():
        temp = {
            "id": asset_report[a]["id"],
            "addresses": asset_report[a]["addresses"],
            "addresses_extra": asset_report[a]["addresses_extra"],
            "names": asset_report[a]["names"],
            "risks": asset_report[a]["risks"],
            "risk_count": len(asset_report[a]["risks"])
        }
        asset_report_csv.append(temp)

    write_to_csv(
        output=asset_report_csv,
        filename=f"{name}/asset_report.csv",
        fieldnames=[
            "id",
            "addresses",
            "addresses_extra",
            "names",
            "risks",
            "risk_count"
        ])


def main():
    orgs = requests.get(BASE_URL + "/account/orgs", headers=HEADERS)
    for o in orgs.json():
        token = o.get("export_token", "")
        name = o.get("name").replace(" ", "_").replace("-", "").lower()
        asset_count = o.get("asset_count")
        max_assets = 100000
        if token and asset_count < max_assets:
            handle_org(token=token, name=name)
        if not token:
            print(
                f"skipping {name} - you need to enable the export token in the UI to run the report")
        elif asset_count > max_assets:
            print(
                f"skipping {name} - you need to increase the max_assets value to be above {max_assets} to run")


if __name__ == "__main__":
    main()
