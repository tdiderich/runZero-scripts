import requests
import os
import json
import csv

# AUTH
RUNZERO_ORG_TOKEN = os.environ["RUNZERO_ORG_TOKEN"]
HEADERS = {"Authorization": f"Bearer {RUNZERO_ORG_TOKEN}"}
BASE_URL = "https://console.runZero.com/api/v1.0"

# UPDATE IF NEEDED
FIELDS = ["id", "name", "template_id", "parent_id",
          "time_taken", "time_taken_minutes", "time_taken_hours"]


def write_to_csv(output: dict, filename: str, fieldnames: list):
    file = open(filename, "w")
    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )
    writer.writeheader()
    writer.writerows(output)
    file.close()


def get_tasks():
    url = BASE_URL + "/org/tasks"
    tasks = requests.get(
        url, headers=HEADERS, params={
            "search": "type:scan status:processed created_at:<7days"}
    )
    return tasks.json()


def main():
    tasks = get_tasks()
    csv_out = []
    if len(tasks) > 0:
        for t in tasks:
            finished = t["updated_at"]
            started = t["start_time"]
            t["time_taken_seconds"] = finished - started
            t["time_taken_minutes"] = (finished - started) / 60
            t["time_taken_hours"] = (finished - started) / 3600
            csv_out.append(dict((k, t[k]) for k in FIELDS if k in t))

    write_to_csv(
        output=csv_out,
        filename="tasks.csv",
        fieldnames=FIELDS)


if __name__ == "__main__":
    main()
