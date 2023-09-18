import requests
import os
import json
import csv

# AUTH
RUNZERO_ORG_TOKEN = os.environ["RUNZERO_ORG_TOKEN"]
ORG_HEADERS = {"Authorization": f"Bearer {RUNZERO_ORG_TOKEN}"}
RUNZERO_ACCOUNT_TOKEN = os.environ["RUNZERO_ACCOUNT_TOKEN"]
ACCOUNT_HEADERS = {"Authorization": f"Bearer {RUNZERO_ACCOUNT_TOKEN}"}
BASE_URL = "https://console.runZero.com/api/v1.0"

# UPDATE IF NEEDED
FIELDS_TO_SKIP = ["params"]


def write_to_csv(output: dict, filename: str, fieldnames: list):
    file = open(filename, "w")
    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )
    writer.writeheader()
    writer.writerows(output)
    file.close()


def get_sites():
    url = BASE_URL + "/org/sites"
    sites = requests.get(url, headers=ORG_HEADERS)
    site_names = {}
    for s in sites.json():
        site_names[s["id"]] = s["name"]
    return site_names


def get_explorers():
    url = BASE_URL + "/org/explorers"
    explorers = requests.get(url, headers=ORG_HEADERS)
    explorer_names = {}
    for e in explorers.json():
        explorer_names[e["id"]] = e["name"]
    return explorer_names


def get_templates():
    url = BASE_URL + "/account/tasks/templates"
    templates = requests.get(url, headers=ACCOUNT_HEADERS)
    template_names = {}
    for t in templates.json():
        template_names[t["id"]] = t["name"]
    return template_names


def get_tasks():
    url = BASE_URL + "/org/tasks"
    tasks = requests.get(
        url, headers=ORG_HEADERS, params={
            "search": "type:scan recur:t"}
    )
    return tasks.json()


def main():
    fields = []
    tasks = get_tasks()
    sites = get_sites()
    explorers = get_explorers()
    templates = get_templates()
    csv_out = []
    if len(tasks) > 0:
        for t in tasks:
            t["explorer_name"] = explorers.get(t["agent_id"], "")
            t["site_name"] = sites.get(t["site_id"], "")
            t["template_name"] = templates.get(t["template_id"], "")
            finished = t["updated_at"]
            started = t["start_time"]
            t["time_taken_seconds"] = finished - started
            t["time_taken_minutes"] = (finished - started) / 60
            t["time_taken_hours"] = (finished - started) / 3600
            csv_out.append(dict((k, t[k])
                           for k in t.keys() if k not in FIELDS_TO_SKIP))
            for key in t.keys():
                if key not in fields and key not in FIELDS_TO_SKIP:
                    fields.append(key)

    write_to_csv(
        output=csv_out,
        filename="tasks.csv",
        fieldnames=fields)


if __name__ == "__main__":
    main()
