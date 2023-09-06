from ipaddress import ip_network
import site
import requests
import os
import json

# UPDATE "ADD ME" if you aren"t using the .env file
RUNZERO_ORG_TOKEN = os.environ["RUNZERO_ORG_TOKEN"] or "ADD ME"

# ADD ME
SUBNET_FILE = "ADD ME"
DEFAULT_SITE = "ADD ME"
DEFAULT_TASK = "ADD ME"

# DO NOT TOUCH
HEADERS = {"Authorization": f"Bearer {RUNZERO_ORG_TOKEN}"}
BASE_URL = "https://console.runZero.com/api/v1.0"


def get_sites():
    url = BASE_URL + "/org/sites"
    sites = requests.get(url, headers=HEADERS)
    return sites.json()


def get_tasks():
    url = BASE_URL + "/org/tasks"
    tasks = requests.get(url, headers=HEADERS, params={"search": "recur:t"})
    return tasks.json()


def check_for_subnets(subnets: dict, runZero_subnets: list):
    tracker = {}
    for s in subnets:
        cidr = s["cidr"]
        # checks if cidr is an exact match in the runZero list
        if s["cidr"] in runZero_subnets:
            tracker[cidr] = {"state": "exists", "tag": s["name"]}
        else:
            # checks if the cidr is already covered by a larger subnet mask
            for runZero_sub in runZero_subnets:
                if ip_network(s["cidr"]).subnet_of(ip_network(runZero_sub)):
                    tracker[cidr] = {"state": "covered", "tag": s["name"]}
                else:
                    tracker[cidr] = {"state": "missing", "tag": s["name"]}
    return tracker


def handle_missing_subnets(tracker: dict):
    site_url = BASE_URL + f"/org/sites/{DEFAULT_SITE}"
    default_site = requests.get(site_url, headers=HEADERS)
    existing_subnets = default_site.json()["subnets"]
    subnets_to_add = {}

    for cidr in tracker.keys():
        if "state" in tracker[cidr] and tracker[cidr]["state"] == "missing":
            subnets_to_add[cidr] = {"tags": {"location": tracker[cidr]["tag"]}}

    if subnets_to_add:
        data = {**existing_subnets, **subnets_to_add}
        try_update_sites = requests.patch(
            site_url, headers=HEADERS, json={"subnets": data}
        )
        if try_update_sites.status_code != 200:
            print("err updating site")
    else:
        print("no site update required")


def handle_missing_tasks(tracker: dict):
    task_url = BASE_URL + f"/org/tasks/{DEFAULT_TASK}"
    default_task = requests.get(task_url, headers=HEADERS)
    existing_subnets = default_task.json()["params"]["targets"].split(" ")
    subnets_to_add = []

    for cidr in tracker.keys():
        if "state" in tracker[cidr] and tracker[cidr]["state"] == "missing":
            subnets_to_add.append(cidr)

    if subnets_to_add:
        data = existing_subnets + subnets_to_add
        data = " ".join(data)
        try_update_task = requests.patch(
            task_url, headers=HEADERS, json={"params": {"targets": data}}
        )
        print(try_update_task.json())
        if try_update_task.status_code != 200:
            print("err updating task")
    else:
        print("no task update required")


def main(subnets: dict):
    sites = get_sites()
    site_subnets = []
    tasks = get_tasks()
    task_subnets = []

    for site in sites:
        for subnet in list(site["subnets"].keys()):
            site_subnets.append(subnet)
    for task in tasks:
        for subnet in task["params"]["targets"].split(" "):
            task_subnets.append(subnet)

    site_tracker = check_for_subnets(
        subnets=subnets, runZero_subnets=site_subnets)
    handle_missing_subnets(tracker=site_tracker)

    task_tracker = check_for_subnets(
        subnets=subnets, runZero_subnets=task_subnets)
    handle_missing_tasks(tracker=task_tracker)


if __name__ == "__main__":
    f = open(SUBNET_FILE)
    subnets = json.loads(f.read())
    main(subnets)
