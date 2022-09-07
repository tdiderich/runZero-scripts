import requests
import os

RUNZERO_ORG_TOKEN = os.environ["RUNZERO_ORG_TOKEN"]
HEADERS = {"Authorization": f"Bearer {RUNZERO_ORG_TOKEN}"}
BASE_URL = "https://console.runZero.com/api/v1.0"


def get_org():
    url = BASE_URL + "/org"
    org = requests.get(url, headers=HEADERS)
    return org.json()


def get_agents():
    url = BASE_URL + "/org/agents"
    agents = requests.get(url, headers=HEADERS)
    return agents.json()


def get_sites():
    url = BASE_URL + "/org/sites"
    sites = requests.get(url, headers=HEADERS)
    return sites.json()


def get_tasks():
    url = BASE_URL + "/org/tasks"
    tasks = requests.get(url, headers=HEADERS, params={"search": "recur:t"})
    return tasks.json()


def main():
    org = get_org()
    agents = get_agents()
    sites = get_sites()
    tasks = get_tasks()

    print(f'ORG creator - {org["created_by"]}')
    print(f'ORG ID - {org["id"]}')
    print(f"Agent count - {len(agents)}")
    print(f"Site count - {len(sites)}")
    print(f"Task count - {len(tasks)}")


if __name__ == "__main__":
    main()
