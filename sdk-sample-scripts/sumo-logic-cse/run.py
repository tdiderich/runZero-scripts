import requests
import os
from flatten_json import flatten
from ipaddress import ip_address
from typing import Any, Dict, List
import runzero
from runzero.client import AuthError
from runzero.api import CustomAssets, CustomIntegrationsAdmin, Sites, Tasks
from runzero.types import (
    ImportAsset,
    IPv4Address,
    IPv6Address,
    NetworkInterface,
    ImportTask
)

# runZero creds
RUNZERO_BASE_URL = "https://console.runZero.com/api/v1.0"
RUNZERO_ORG_ID = os.environ["RUNZERO_ORG_ID"]
RUNZERO_SITE_NAME = os.environ["RUNZERO_SITE_NAME"]
RUNZERO_CLIENT_ID = os.environ["RUNZERO_CLIENT_ID"]
RUNZERO_CLIENT_SECRET = os.environ["RUNZERO_CLIENT_SECRET"]

# sumologic creds
SUMO_ACCESS_ID = os.environ["SUMO_ACCESS_ID"]
SUMO_ACCESS_KEY = os.environ["SUMO_ACCESS_KEY"]
SUMO_URL = os.environ["SUMO_URL"]


def build_assets_from_json(json_input: List[Dict[str, Any]]) -> List[ImportAsset]:

    assets: List[ImportAsset] = []
    for item in json_input:
        asset_id = item.get("id", "")
        hostname = item.get("hostname", None)
        entity_type = item.get("entityType", "")
        if entity_type == "_ip":
            ip = item.get("value", None)
            item["ipAddress"] = ip
        mac = item.get("macAddress")
        network = build_network_interface(
            ips=[ip], mac=mac if mac else "00:00:00:00:00:00")
        tags = item.get("tags", [])

        # handle any additional values and insert into custom_attrs
        custom_attrs: Dict[str] = {}

        root_keys_to_ignore = []
        for key, value in item.items():
            if not isinstance(value, dict):
                root_keys_to_ignore.append(key)

        flattened_items = flatten(nested_dict=item,
                                  root_keys_to_ignore=root_keys_to_ignore)

        item = flattened_items | item

        for key, value in item.items():
            if not isinstance(value, dict):
                custom_attrs[key] = str(value)[:1022]

        if hostname and ip:
            assets.append(ImportAsset(
                id=asset_id,
                networkInterfaces=[network],
                hostnames=[hostname],
                tags=tags,
                customAttributes=custom_attrs
            ))

    return assets


def build_network_interface(ips: List[str], mac: str = None) -> NetworkInterface:
    """
    This function converts a mac and a list of strings in either ipv4 or ipv6 format and creates a NetworkInterface that
    is accepted in the ImportAsset
    """
    ip4s: List[IPv4Address] = []
    ip6s: List[IPv6Address] = []
    for ip in ips[:99]:
        try:
            ip_addr = ip_address(ip)
            if ip_addr.version == 4:
                ip4s.append(ip_addr)
            elif ip_addr.version == 6:
                ip6s.append(ip_addr)
            else:
                continue
        except:
            continue

    if mac is None:
        return NetworkInterface(ipv4Addresses=ip4s, ipv6Addresses=ip6s)
    else:
        return NetworkInterface(macAddress=mac, ipv4Addresses=ip4s, ipv6Addresses=ip6s)


def import_data_to_runzero(assets: List[ImportAsset]):
    # create the runzero client
    c = runzero.Client()

    # try to log in using OAuth credentials
    try:
        c.oauth_login(RUNZERO_CLIENT_ID, RUNZERO_CLIENT_SECRET)
    except AuthError as e:
        print(f"login failed: {e}")
        return

    # create the site manager to get our site information
    site_mgr = Sites(c)
    site = site_mgr.get(RUNZERO_ORG_ID, RUNZERO_SITE_NAME)
    if not site:
        print(f"unable to find requested site")
        return

    # get or create the custom source manager and create a new custom source
    custom_source_mgr = CustomIntegrationsAdmin(c)
    my_asset_source = custom_source_mgr.get(name="sumologic-cse")
    if my_asset_source:
        source_id = my_asset_source.id
    else:
        my_asset_source = custom_source_mgr.create(name="sumologic-cse")
        source_id = my_asset_source.id

    # create the import manager to upload custom assets
    import_mgr = CustomAssets(c)
    import_task = import_mgr.upload_assets(
        org_id=RUNZERO_ORG_ID, site_id=site.id, custom_integration_id=source_id, assets=assets, task_info=ImportTask(
            name="sumologic-cse sync")
    )

    if import_task:
        print(
            f"task created! view status here: https://console.runzero.com/tasks?task={import_task.id}")


def get_entities():
    url = SUMO_URL + "/api/sec/v1/entities/all"
    entities_final = []
    has_next_page = True
    next_page_token = None
    while has_next_page:
        params = {"nextPageToken": next_page_token} if next_page_token else {}
        entities = requests.get(url, auth=(
            SUMO_ACCESS_ID, SUMO_ACCESS_KEY), params=params)
        data = entities.json().get("data", {}).get("objects", [])
        entities_final.extend(data)

        next_page_token = entities.json().get("nextPageToken", None)
        if not next_page_token:
            has_next_page = False

    return entities_final


if __name__ == "__main__":
    sumologic_entities = get_entities()
    runzero_assets = build_assets_from_json(sumologic_entities)
    import_data_to_runzero(runzero_assets)
