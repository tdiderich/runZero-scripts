import requests
import json
import os
import csv

# DO NOT TOUCH
RUNZERO_ORG_TOKEN = os.environ["RUNZERO_ORG_TOKEN"]
ORG_HEADERS = {"Authorization": f"Bearer {RUNZERO_ORG_TOKEN}"}

# UPDATE IF SELF HOSTED
BASE_URL = "https://console.runZero.com/api/v1.0"


def get_tasks():
    url = BASE_URL + "/org/tasks"
    data = requests.get(url, headers=ORG_HEADERS, params={"search": "recur:t"})
    recurring_tasks = data.json()
    task_stats = {}
    for r in recurring_tasks:
        if r["name"] not in ["Outlier calculation", "Query"]:
            id = r["id"]
            tasks_from_parent = requests.get(url, headers=ORG_HEADERS, params={
                                             "search": f"parent_id:{id}"})
            task_stats[id] = {
                "names": [],
                "site_ids": [],
                "site_names": [],
                "new_assets_all_time": 0,
                "offline_assets_all_time": 0,
                "total_assets_seen": 0,
                "scan_count": len(tasks_from_parent.json()),
                "average_assets_seen": 0,
                "max_assets_seen": 0,
                "min_assets_seen": 10000000000000
            }
            for t in tasks_from_parent.json():
                name = t.get("name", "")
                if name and name not in task_stats[id]["names"]:
                    task_stats[id]["names"].append(name)

                site_id = t.get("site_id", "")
                if site_id and site_id not in task_stats[id]["site_ids"]:
                    task_stats[id]["site_ids"].append(site_id)

                new_assets = t.get("stats", "").get("change.newAssets", "")
                if new_assets:
                    task_stats[id]["new_assets_all_time"] += int(new_assets)

                offline_assets = t.get("stats", "").get(
                    "change.offlineAssets", "")
                if offline_assets:
                    task_stats[id]["offline_assets_all_time"] += int(
                        offline_assets)

                total_assets = t.get("stats", "").get("change.totalAssets", "")
                if total_assets:
                    task_stats[id]["total_assets_seen"] += int(total_assets)
                    task_stats[id]["max_assets_seen"] = total_assets if total_assets > task_stats[
                        id]["max_assets_seen"] else task_stats[id]["max_assets_seen"]
                    task_stats[id]["min_assets_seen"] = total_assets if total_assets < task_stats[
                        id]["min_assets_seen"] else task_stats[id]["min_assets_seen"]

            task_stats[id]["average_assets_seen"] = round(
                task_stats[id]["total_assets_seen"] / task_stats[id]["scan_count"])
            for s in task_stats[id]["site_ids"]:
                get_site_url = BASE_URL + f"/org/sites/{s}"
                site_data = requests.get(get_site_url, headers=ORG_HEADERS)
                site_name = site_data.json().get("name")
                if site_name and site_name not in task_stats[id]["site_names"]:
                    task_stats[id]["site_names"].append(site_name)

    return task_stats


def main():
    # generate stats
    task_stats = get_tasks()

    # write to JSON
    scan_stats_json = open("./data.json", "w")
    scan_stats_json.write(json.dumps(task_stats, indent=4))
    scan_stats_json.close()

    # generate CSV friendly JSON
    csv_output = []
    for id in task_stats.keys():
        temp = task_stats[id]
        temp["id"] = id
        csv_output.append(temp)

    # write to CSV
    scan_stats_csv = open("./data.csv", "w")
    writer = csv.DictWriter(
        scan_stats_csv,
        fieldnames=[
            "id",
            "names",
            "site_ids",
            "site_names",
            "new_assets_all_time",
            "offline_assets_all_time",
            "total_assets_seen",
            "scan_count",
            "average_assets_seen",
            "max_assets_seen",
            "min_assets_seen"
        ])
    writer.writeheader()
    writer.writerows(csv_output)
    scan_stats_csv.close()


if __name__ == "__main__":
    main()
