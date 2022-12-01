import requests
import os
import json
import csv

# AUTH
RUNZERO_ORG_TOKEN = os.environ["RUNZERO_ORG_TOKEN"]
HEADERS = {"Authorization": f"Bearer {RUNZERO_ORG_TOKEN}"}
BASE_URL = "https://console.runZero.com/api/v1.0"

# UPDATE IF NEEDED
FIELDS = ['id', 'name', 'template_id']

def write_to_csv(output: dict, filename: str, fieldnames: list):
    file = open(filename, 'w')
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
        url, headers=HEADERS, params={"search": "recur:t type:scan"}
    )
    return tasks.json()


def main():
    tasks = get_tasks()
    csv_out = []
    if len(tasks) > 0:
        for t in tasks:
            csv_out.append(dict((k, t[k]) for k in FIELDS if k in t))
    print(csv_out)
    write_to_csv(
        output=csv_out,
        filename='tasks.csv',
        fieldnames=FIELDS)        
            



if __name__ == "__main__":
    main()
