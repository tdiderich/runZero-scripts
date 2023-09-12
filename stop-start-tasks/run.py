import requests
import os
import json

RUNZERO_ORG_TOKEN = os.environ["RUNZERO_ORG_TOKEN"]
HEADERS = {"Authorization": f"Bearer {RUNZERO_ORG_TOKEN}"}
BASE_URL = "https://console.runZero.com/api/v1.0"

PAUSE_SEARCH = "status:active recur:t not source:passive"
START_SEARCH = "status:paused recur:t not source:passive"


def get_tasks(search: str or None):
    url = BASE_URL + "/org/tasks"
    tasks = requests.get(
        url, headers=HEADERS, params={
            "search": search}
    )
    return tasks.json()


def pause_task(id: str):
    url = BASE_URL + f"/org/tasks/{id}"
    pause = requests.patch(url, headers=HEADERS, json={"status": "paused"})
    if pause.status_code == 200:
        return True
    else:
        return False


def start_task(id: str):
    url = BASE_URL + f"/org/tasks/{id}"
    pause = requests.patch(url, headers=HEADERS, json={"status": "active"})
    if pause.status_code == 200:
        return True
    else:
        return False


def main():

    tasks_to_pause = get_tasks(search=PAUSE_SEARCH)
    if len(tasks_to_pause) > 0:
        for t in tasks_to_pause:
            id = t["id"]
            success = pause_task(id=id)
            if success:
                print(f"Paused: {id}")
            else:
                print(f"Failed to pause: {id}")
    else:
        print("No tasks to pause")

    tasks_to_start = get_tasks(search=START_SEARCH)
    if len(tasks_to_start) > 0:
        for t in tasks_to_start:
            id = t["id"]
            success = start_task(id=id)
            if success:
                print(f"Started: {id}")
            else:
                print(f"Failed to start: {id}")
    else:
        print("No tasks to start ")


if __name__ == "__main__":
    main()
