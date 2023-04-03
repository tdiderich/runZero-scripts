import requests
import os
import json
import random
import uuid
from ipaddress import ip_address
from typing import Any, Dict, List, Optional
import time
import runzero
from runzero.client import AuthError
from runzero.types import (
    CustomAttribute,
    ImportAsset,
    IPv4Address,
    IPv6Address,
    NetworkInterface,
)

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


def build_assets_from_json(json_input: List[Dict[str, Any]]) -> List[ImportAsset]:
    """
    This is an example function to highlight how to handle converting data from an API into the ImportAsset format that
    is required for uploading to the runZero platform.
    This function assumes that the json has been converted into a list of dictionaries using `json.loads()` (or any
    similar functions).
    """

    assets: List[ImportAsset] = []
    for item in json_input:
        # grab known API attributes from the json dict that are always present
        asset_id = item.pop("asset_id")
        asset_domain = item.pop("asset_domain")
        asset_type = item.pop("type")
        other_attr = item.pop("other_attribute")
        mac = item.pop("mac")
        ip = item.pop("ip_addresses")

        # create the network interface
        network = build_network_interface(mac, ip)

        # handle the custom attributes
        custom_attrs: Dict[str, CustomAttribute] = {
            "otherAttribute": CustomAttribute(other_attr)}
        # in this case drive might not always be present and needs to be checked
        drive = item.get("drive_type")
        if drive is not None:
            custom_attrs["driveType"] = CustomAttribute(item.pop("drive_type"))

        # handle any additional values and insert into custom_attrs
        # this works because of the use of items.pop for all other attributes which removed them from the dict
        for key, value in item.items():
            custom_attrs[key] = CustomAttribute(value)

        assets.append(
            ImportAsset(
                id=asset_id,
                domain=asset_domain,
                deviceType=asset_type,
                networkInterfaces=[network],
                customAttributes=custom_attrs,
            )
        )
    return assets


def build_network_interface(ips: List[str], mac: str = None) -> NetworkInterface:
    """
    This function converts a mac and a list of strings in either ipv4 or ipv6 format and creates a NetworkInterface that
    is accepted in the ImportAsset
    """
    ip4s: List[IPv4Address] = []
    ip6s: List[IPv6Address] = []
    for ip in ips[:99]:
        ip_addr = ip_address(ip)
        if ip_addr.version == 4:
            ip4s.append(ip_addr)
        elif ip_addr.version == 6:
            ip6s.append(ip_addr)
        else:
            continue

    if mac is None:
        return NetworkInterface(ipv4Addresses=ip4s, ipv6Addresses=ip6s)
    else:
        print(mac)
        return NetworkInterface(macAddress=mac, ipv4Addresses=ip4s, ipv6Addresses=ip6s)

def create_fake_data(assets: list):
    fake_logs: List[ImportAsset] = []
    for a in assets:
        macs = a.get('macs', [])
        if len(macs) > 0:
            network = build_network_interface(
                mac=macs[0], ips=a['addresses'] + a['addresses_extra'])
        else:
            network = build_network_interface(
                ips=a['addresses'] + a['addresses_extra'])
        asset = ImportAsset(
            id=a['id'],
            networkInterfaces=[network],
            hostnames=a['names'][:99],
            network_level=NETWORK_LEVEL_OPTIONS[random.randint(
                0, 3)],
            owner=OWNER_OPTIONS[random.randint(0, 3)]
        )
        fake_logs.append(asset)

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

    # create the import manager to upload custom assets
    import_mgr = runzero.CustomAssets(c)
    import_task = import_mgr.upload_assets(
        RUNZERO_ORG_ID, site.id, my_asset_source.id, logs)
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
    assets = requests.get(url, headers=RUNZERO_HEADERS)
    fake_logs = create_fake_data(assets=assets.json())
    # import_logs_to_runzero(logs=fake_logs)


if __name__ == '__main__':
    main()
