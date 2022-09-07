from ipaddress import ip_network
import site
import requests
import os
import json

# UPDATE 'ADD ME' if you aren't using the .env file
RUNZERO_ORG_TOKEN = os.environ["RUNZERO_ORG_TOKEN"] or "ADD ME"

# ADD ME
SUBNET_FILE = "ADD ME"

# ADD one of the two - defaults to SITE_ID if both exist
SITE_ID = "ADD ME"
SITE_NAME = "ADD ME"

# DO NOT TOUCH
HEADERS = {"Authorization": f"Bearer {RUNZERO_ORG_TOKEN}"}
BASE_URL = "https://console.runZero.com/api/v1.0"

# takes existing site and adds missing subnets
def handle_site_update(site: dict, subnets: dict):
    for s in subnets:
        cidr = s["cidr"]
        name = s["name"]
        site["subnets"][cidr] = {"tags": {"location": name}}
        site["scope"] = site["scope"] + f"\n{cidr}"
    return site


def main(subnets: dict):
    # updates existing site
    if SITE_ID and SITE_ID != "ADD ME":
        url = BASE_URL + f"/org/sites/{SITE_ID}"
        get_site = requests.get(url=url, headers=HEADERS)
        site = get_site.json()
        updated_site = handle_site_update(site=site, subnets=subnets)
        r = requests.patch(url=url, headers=HEADERS, json=updated_site)
        id = r.json()["id"]
    # creates new site
    elif SITE_NAME and SITE_NAME != "ADD ME":
        url = BASE_URL + "/org/sites"
        site = {"name": SITE_NAME, "scope": "", "subnets": {}}
        updated_site = handle_site_update(site=site, subnets=subnets)
        r = requests.put(url=url, headers=HEADERS, json=updated_site)
        id = r.json()["id"]
    # can't do anything if we don't have the site info
    else:
        print("Please add or update a SITE_ID or SITE_NAME to run this script")
        return

    if r.status_code == 200:
        print(f"SUCCESS! View site here: https://console.runZero.com/sites/{id}/edit")
    else:
        print(f"SOMETHING WENT WRONG: {r.status_code}")


if __name__ == "__main__":
    f = open(SUBNET_FILE)
    subnets = json.loads(f.read())
    main(subnets)
