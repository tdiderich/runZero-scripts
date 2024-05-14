import requests
import os
import csv
import json
import ipaddress

# auth - navigate here to create an account token: https://console.runzero.com/account
RUNZERO_ACCOUNT_TOKEN = os.environ["RUNZERO_ACCOUNT_TOKEN"]
HEADERS = {"Authorization": f"Bearer {RUNZERO_ACCOUNT_TOKEN}"}
BASE_URL = "https://console.runZero.com/api/v1.0"
GLOBAL_RISK = []


def write_to_csv(output: dict, filename: str, fieldnames: list):
    file = open(filename, "w")
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(output)
    file.close()


def handle_org(token: str, name: str):
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
            handle_org(token=token, name=name)
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
