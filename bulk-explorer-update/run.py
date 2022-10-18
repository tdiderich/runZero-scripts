import requests
import os

# DO NOT TOUCH
RUNZERO_ORG_TOKEN = os.environ["RUNZERO_ORG_TOKEN"]
HEADERS = {"Authorization": f"Bearer {RUNZERO_ORG_TOKEN}"}
BASE_URL = "https://console.runZero.com/api/v1.0"

# UPDATE 
DEFAULT_SITE = 'eba73e73-f79f-40dc-b782-cf867485353a'

def update_explorer(explorer_id: str):
    url = BASE_URL + f'/org/explorers/{explorer_id}'
    update = requests.patch(url, headers=HEADERS, json={'site_id': DEFAULT_SITE})
    return update.status_code

def get_explorers():
    url = BASE_URL + "/org/explorers"
    explorers = requests.get(url, headers=HEADERS)
    return explorers.json()


def main():
    explorers = get_explorers()
    for a in explorers:
        site_id = a['site_id']
        explorer_id = a['id']
        if site_id == '00000000-0000-0000-0000-000000000000':
            update = update_explorer(explorer_id=explorer_id)
            if update <= 202:
                print(f'Successfully updated explorer {explorer_id} to {DEFAULT_SITE}')
            else:
                print(f'Failed to update explorer {explorer_id} - status code: {update}')
        else:
            print(f'Explorer {explorer_id} already assigned to a Site')


if __name__ == "__main__":
    main()
