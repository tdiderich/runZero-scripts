import requests
import os

RUNZERO_ORG_TOKEN = os.environ["RUNZERO_ORG_TOKEN"]
HEADERS = {"Authorization": f"Bearer {RUNZERO_ORG_TOKEN}"}
BASE_URL = "https://console.runZero.com/api/v1.0"


def get_tasks():
    url = BASE_URL + "/org/tasks"
    tasks = requests.get(
        url, headers=HEADERS, params={"search": "status:active or status:queued"}
    )
    return tasks.json()


def stop_task(id: str):
    url = BASE_URL + f"/org/tasks/{id}/stop"
    stop = requests.post(url, headers=HEADERS)
    if stop.status_code == 200:
        return True
    else:
        return False


def main():
    tasks = get_tasks()
    if len(tasks) > 0:
        for t in tasks:
            id = t["id"]
            success = stop_task(id=id)
            if success:
                print(f"Stopped: {id}")
            else:
                print(f"Failed to stop: {id}")
    else:
        print("No tasks running.")


if __name__ == "__main__":
    main()
