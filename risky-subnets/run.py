import requests
import os
import csv
import json
import urllib.parse
import ipaddress

# auth - navigate here to create an account token: https://console.runzero.com/account
RUNZERO_ACCOUNT_TOKEN = os.environ["RUNZERO_ACCOUNT_TOKEN"]
HEADERS = {"Authorization": f"Bearer {RUNZERO_ACCOUNT_TOKEN}"}
BASE_URL = "https://console.runZero.com/api/v1.0"

# dict for tracking counts and data
GLOBAL_RISK = []

# searches to report on - update as needed

SEARCHES = [
    {
        "name": "assets_missing_crowdstrike",
        "type": "assets",
        "search": "source:runzero not source:crowdstrike (type:server OR type:desktop OR type:laptop) alive:t",
    },
    {
        "name": "expired_tls_certs",
        "type": "services",
        "search": "alive:t protocol:tls tls.notAfterTS:<now",
    },
]


def write_to_csv(output: dict, filename: str, fieldnames: list):
    file = open(filename, "w")
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(output)
    file.close()

def handle_search(token: str, org_name: str, search_name: str, search_type: str, search: str):

    # check for folder or create
    if not os.path.exists(f"{org_name}/{search_type}"):
        os.mkdir(f"{org_name}/{search_type}")

    headers = {"Authorization": f"Bearer {token}"}
    if search_type == "assets":
        url = BASE_URL + "/export/org/assets.json?"
        search_url = "https://console.runzero.com/inventory?search="
    elif search_type == "services":
        url = BASE_URL + "/export/org/services.json?"
        search_url = "https://console.runzero.com/inventory/services?search="
    else:
        print(f"non supported search type {search_type}")

    data = requests.get(url, headers=headers, params={
                                "search": search, "fields": "addresses, addresses_extra, risk_rank, risk, criticality, criticality_rank"})
    results = data.json()
    search_results = {}

    for asset in results:
        addresses = asset.get("addresses", [])
        risk = asset.get("risk_rank", 0)
        criticality = asset.get("criticality_rank", 0)
        for address in addresses:
            ip = ipaddress.ip_address(address)
            if ip.version == 4:
                address.split(".")
                subnet = ".".join(address.split(".")[0:3]) + ".0/24"
                if subnet not in search_results:
                    # new subnet
                    search_results[subnet] = {}
                    search_results[subnet]["matches"] = 0
                    search_results[subnet]["risk"] = risk
                    search_results[subnet]["criticality"] = criticality
                    safe_search = urllib.parse.quote_plus(f"{search} AND net:{subnet}")
                    search_results[subnet][
                        "search"
                    ] = f"{search_url}{safe_search}"

                # handle subnets that already exist
                search_results[subnet]["matches"] += 1
                search_results[subnet]["risk"] += risk
                search_results[subnet]["criticality"] += criticality

    search_results_output = []
    for subnet in search_results.keys():
        search_results_output.append(
            {
                "org_name": org_name,
                "subnet": subnet,
                "matches": search_results[subnet]["matches"],
                "risk": search_results[subnet]["risk"],
                "criticality": search_results[subnet]["criticality"],
                "search": search_results[subnet]["search"],
            }
        )


    write_to_csv(
        output=sorted(search_results_output, key=lambda x: x["risk"], reverse=True),
        filename=f"{org_name}/{search_type}/{search_name}.csv",
        fieldnames=[
            "org_name",
            "subnet",
            "matches",
            "risk",
            "criticality",
            "search",
        ],
    )

def handle_org_risk(token: str, name: str):
    print(f"handling {name}...")
    # check for folder or create
    if not os.path.exists(name):
        os.mkdir(name)

    # create export variables
    headers = {"Authorization": f"Bearer {token}"}
    url = BASE_URL + "/export/org/assets.json"

    # total risk by subnet dict
    risk_by_subnet = {}

    data = requests.get(
        url,
        headers=headers,
        params={
            "search": "alive:t",
            "fields": "addresses, addresses_extra, risk_rank, risk, criticality, criticality_rank"
        }
    )

    results = data.json()

    for asset in results:
        addresses = asset.get("addresses", [])
        risk = asset.get("risk_rank", 0)
        criticality = asset.get("criticality_rank", 0)
        for address in addresses:
            ip = ipaddress.ip_address(address)
            if ip.version == 4:
                address.split(".")
                subnet = ".".join(address.split(".")[0:3]) + ".0/24"
                if subnet not in risk_by_subnet:
                    risk_by_subnet[subnet] = {}
                    risk_by_subnet[subnet]["risk"] = risk
                    risk_by_subnet[subnet]["criticality"] = criticality
                    risk_by_subnet[subnet][
                        "search"
                    ] = f"https://console.runzero.com/inventory?search=net%3A{subnet}"

                risk_by_subnet[subnet]["risk"] += risk
                risk_by_subnet[subnet]["criticality"] += criticality

    risk_by_subnet_output = []
    for subnet in risk_by_subnet.keys():
        risk_by_subnet_output.append(
            {
                "org_name": name,
                "subnet": subnet,
                "risk": risk_by_subnet[subnet]["risk"],
                "criticality": risk_by_subnet[subnet]["criticality"],
                "search": risk_by_subnet[subnet]["search"],
            }
        )
    
    GLOBAL_RISK.extend(risk_by_subnet_output)

    write_to_csv(
        output=sorted(risk_by_subnet_output, key=lambda x: x["risk"], reverse=True),
        filename=f"{name}/risk_by_subnet.csv",
        fieldnames=[
            "org_name",
            "subnet",
            "risk",
            "criticality",
            "search",
        ],
    )


def main():
    orgs = requests.get(BASE_URL + "/account/orgs", headers=HEADERS)
    print(orgs)
    for o in orgs.json():
        token = o.get("export_token", "")
        name = o.get("name").replace(" ", "_").replace("-", "").lower()
        asset_count = o.get("asset_count")
        max_assets = 100000
        if token and asset_count < max_assets and asset_count > 50:
            handle_org_risk(token=token, name=name)
            for search in SEARCHES:
                handle_search(token=token, org_name=name, search_name=search["name"], search_type=search["type"], search=search["search"])
        if not token:
            print(
                f"skipping {name} - you need to enable the export token in the UI to run the report"
            )
        elif asset_count > max_assets:
            print(
                f"skipping {name} - you need to increase the max_assets value to be above {max_assets} to run"
            )

    write_to_csv(
        output=sorted(GLOBAL_RISK, key=lambda x: x["risk"], reverse=True),
        filename=f"GLOBAL_RISK.csv",
        fieldnames=[
            "org_name",
            "subnet",
            "risk",
            "criticality",
            "search",
        ],
    )


if __name__ == "__main__":
    main()
