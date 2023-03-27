import requests
import os
import ipaddress
import random
import uuid
import json
import time
import runzero
from runzero.client import AuthError
from runzero.types import NewAssetCustomSource

# runZero creds
RUNZERO_EXPORT_TOKEN = os.environ['RUNZERO_EXPORT_TOKEN']
RUNZERO_HEADERS = {'Authorization': f'Bearer {RUNZERO_EXPORT_TOKEN}'}
RUNZERO_BASE_URL = 'https://console.runZero.com/api/v1.0'
RUNZERO_ORG_ID = '4ffe8ffb-18e7-451b-9aea-7c967ad07f8e'
WANTED_SITE_NAME = 'Primary'
MY_CLIENT_ID = os.environ['RUNZERO_CLIENT_ID']
MY_CLIENT_SECRET = os.environ['RUNZERO_CLIENT_SECRET']

# fake data stuff
NETWORK_LEVEL_OPTIONS = ['LOW', 'MED', 'HIGH', 'CRITCAL']
OWNER_OPTIONS = ['IT', 'Database', 'Server', 'Remote']

def create_fake_data(assets: list):
    fake_logs = []
    for a in assets:
        for ip in a['addresses']:
            try:
                check = ipaddress.ip_address(ip)
                if check.version == 4:
                    log = {
                        'source': 'ipam',
                        'ip': [{'ipv4Addresses': [ip]}],
                        'network_level': NETWORK_LEVEL_OPTIONS[random.randint(0, 3)],
                        'owner': OWNER_OPTIONS[random.randint(0, 3)],
                        'id': str(uuid.uuid4())
                    }
                    fake_logs.append(log)
            except:
                pass

    return fake_logs


def import_logs_to_runzero(logs: list):
    """
    The code below gives an example of how to create a custom source and upload valid assets from a CSV to a site using
    the new custom source.
    """
    # create the runzero client
    c = runzero.Client()

    # try to log in using OAuth credentials
    try:
        c.oauth_login(MY_CLIENT_ID, MY_CLIENT_SECRET)
    except AuthError as e:
        print(f"login failed: {e}")
        return
    print("login successful")

    # create the site manager to get our site information
    site_mgr = runzero.Sites(c)
    site = site_mgr.get(RUNZERO_ORG_ID, WANTED_SITE_NAME)
    if not site:
        print(f"unable to find requested site")
        return
    print(f"got information for site {site.name}")

    # create the custom source manager and create a new custom source
    custom_source_mgr = runzero.CustomSourcesAdmin(c)
    my_asset_source = custom_source_mgr.get(name="fake-ipam-logs")
    print(f"got custom source: {my_asset_source.id}")

    # create mapper
    mapping = {"network_interfaces": "ip"}

    # load some assets from our csv
    assets = runzero.assets_from_json(json.dumps(logs), mapper=mapping)

    # create the import manager to upload custom assets
    import_mgr = runzero.CustomAssets(c)
    import_task = import_mgr.upload_assets(RUNZERO_ORG_ID, site.id, my_asset_source.id, assets)
    print(f"created an custom asset import task: {import_task.name}")

    # create a task manager, so we can monitor our custom asset import task
    task_mgr = runzero.Tasks(client=c)
    status = task_mgr.get_status(RUNZERO_ORG_ID, import_task.id)

    # keep polling until the task is completed or failed or 30 seconds have elapsed
    iters = 0
    while status not in ("processed", "failed", "error") and iters < 6:
        print("polling on status for custom source upload task....")
        time.sleep(5)
        iters += 1
        status = task_mgr.get_status(RUNZERO_ORG_ID, import_task.id)
        print(f"task status is {status}")

    # check that our task successfully completed
    assert status == "processed"
    print("success! custom assets are uploaded and available in the asset inventory")

def main():
    url = RUNZERO_BASE_URL + '/export/org/assets.json?'
    assets = requests.get(url, headers=RUNZERO_HEADERS, params={
                        'fields': 'addresses'})
    fake_logs = create_fake_data(assets=assets.json())
    import_logs_to_runzero(logs=fake_logs)

if __name__ == '__main__':
    main()
