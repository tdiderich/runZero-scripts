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


def create_output(
    assets: list,
    org_name: str,
    search_name: str = None,
    search_type: str = None,
    search: str = None,
    search_url: str = None,
):
    tracker = {}
    output = []

    for asset in assets:
        addresses = asset.get("addresses", [])
        risk = asset.get("risk_rank", 0)
        criticality = asset.get("criticality_rank", 0)
        site = asset.get("site_id", "unknown-site")
        for address in addresses:
            ip = ipaddress.ip_address(address)
            if ip.version == 4:
                address.split(".")
                subnet = ".".join(address.split(".")[0:3]) + ".0/24"
                subnet = f"{site}_{subnet}"
                if subnet not in tracker:
                    # new subnet
                    tracker[subnet] = {}
                    tracker[subnet]["asset_count"] = 0
                    tracker[subnet]["risk"] = risk
                    tracker[subnet]["avg_risk"] = risk
                    tracker[subnet]["criticality"] = criticality
                    tracker[subnet]["avg_criticality"] = criticality
                    search_params = subnet.split("_")

                    safe_search = (
                        urllib.parse.quote_plus(
                            f"{search} AND site:{search_params[0]} AND net:{search_params[1]}"
                        )
                        if search
                        else urllib.parse.quote_plus(
                            f"site:{search_params[0]} AND net:{search_params[1]}"
                        )
                    )

                    tracker[subnet]["search"] = f"{search_url}{safe_search}"

                # handle subnets that already exist
                tracker[subnet]["asset_count"] += 1
                tracker[subnet]["risk"] += risk
                tracker[subnet]["avg_risk"] = round(
                    tracker[subnet]["risk"] / tracker[subnet]["asset_count"], 2
                )
                tracker[subnet]["criticality"] += criticality
                tracker[subnet]["avg_criticality"] = round(
                    tracker[subnet]["criticality"] / tracker[subnet]["asset_count"], 2
                )

    for subnet in tracker.keys():
        output.append(
            {
                "org_name": org_name,
                "site_id": subnet.split("_")[0],
                "subnet": subnet.split("_")[1],
                "asset_count": tracker[subnet]["asset_count"],
                "risk": tracker[subnet]["risk"],
                "avg_risk": tracker[subnet]["avg_risk"],
                "criticality": tracker[subnet]["criticality"],
                "avg_criticality": tracker[subnet]["avg_criticality"],
                "search": tracker[subnet]["search"],
            }
        )

    filename = (
        f"{org_name}/{search_type}/{search_name}.csv"
        if search_type and search_name
        else f"{org_name}/risk_by_subnet.csv"
    )

    write_to_csv(
        output=sorted(output, key=lambda x: x["risk"], reverse=True),
        filename=filename,
        fieldnames=[
            "org_name",
            "asset_count",
            "site_id",
            "subnet",
            "risk",
            "avg_risk",
            "criticality",
            "avg_criticality",
            "search",
        ],
    )

    return output


def handle_search(
    token: str, org_name: str, search_name: str, search_type: str, search: str
):

    # ensure search name is good for file creation
    search_name = search_name.replace(" ", "_").replace("-", "").lower()

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

    data = requests.get(
        url,
        headers=headers,
        params={
            "search": search,
            "fields": "site_id, addresses, addresses_extra, risk_rank, risk, criticality, criticality_rank",
        },
    )
    results = data.json()

    create_output(
        assets=results,
        org_name=org_name,
        search_name=search_name,
        search_type=search_type,
        search=search,
        search_url=search_url,
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
            "fields": "site_id, addresses, addresses_extra, risk_rank, risk, criticality, criticality_rank",
        },
    )

    results = data.json()

    risk_by_subnet_output = create_output(
        assets=results,
        org_name=name,
        search_url="https://console.runzero.com/inventory?search=",
    )

    GLOBAL_RISK.extend(risk_by_subnet_output)


def main():
    orgs = requests.get(BASE_URL + "/account/orgs", headers=HEADERS)
    for o in orgs.json():
        token = o.get("export_token", "")
        name = o.get("name").replace(" ", "_").replace("-", "").lower()
        asset_count = o.get("asset_count")
        max_assets = 100000
        if token and asset_count < max_assets and asset_count > 50:
            handle_org_risk(token=token, name=name)
            for search in SEARCHES:
                handle_search(
                    token=token,
                    org_name=name,
                    search_name=search["name"],
                    search_type=search["type"],
                    search=search["search"],
                )
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
            "asset_count",
            "site_id",
            "subnet",
            "risk",
            "avg_risk",
            "criticality",
            "avg_criticality",
            "search",
        ],
    )


if __name__ == "__main__":
    main()
