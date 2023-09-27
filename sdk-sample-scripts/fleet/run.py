import requests
import os
import json
from flatten_json import flatten
from ipaddress import ip_address
from typing import Any, Dict, List
import runzero
from runzero.client import AuthError
from runzero.api import CustomAssets, CustomIntegrationsAdmin, Sites, Tasks
from runzero.types import (
    CustomAttribute,
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

# Fleet creds
FLEET_URL = os.environ["FLEET_URL"]
FLEET_EMAIL = os.environ["FLEET_EMAIL"]
FLEET_PASSWORD = os.environ["FLEET_PASSWORD"]
FLEET_TOKEN = os.environ["FLEET_TOKEN"]

# Will need to change on a per integration basis to align wtih JSON object keys


def build_assets_from_json(json_input: List[Dict[str, Any]]) -> List[ImportAsset]:

    assets: List[ImportAsset] = []
    for item in json_input:
        asset_id = item.get("uuid")
        name = item.get("hostname", "")
        os = item.get("os_version", "")
        mac = item.get("primary_mac", "")
        private_ip = item.get("primary_ip", "")
        public_ip = item.get("public_ip", "")
        osVersion = item.get("os_version", "")
        manufacturer = item.get("hardware_vendor", "")
        model = item.get("hardware_model", "")

        ips = []
        if private_ip is not None:
            ips.append(private_ip)
        if public_ip is not None:
            ips.append(public_ip)

        network_interface = build_network_interface(ips=ips, mac=mac)

        # handle any additional values and insert into custom_attrs
        custom_attrs: Dict[str, CustomAttribute] = {}

        root_keys_to_ignore = []
        for key, value in item.items():
            if not isinstance(value, dict):
                root_keys_to_ignore.append(key)

        flattened_items = flatten(nested_dict=item,
                                  root_keys_to_ignore=root_keys_to_ignore)

        item = flattened_items | item

        for key, value in item.items():
            if not isinstance(value, dict):
                custom_attrs[key] = CustomAttribute(str(value)[:1023])

        assets.append(
            ImportAsset(
                id=asset_id,
                networkInterfaces=[network_interface],
                os=os,
                hostnames=[name],
                customAttributes=custom_attrs,
                osVersion=osVersion,
                manufacturer=manufacturer,
                model=model,
            )
        )

    return assets

# should not need to change on a per integraton basis


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
    """
    The code below gives an example of how to create a custom source and upload valid assets from a CSV to a site using
    the new custom source.
    """
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
    my_asset_source = custom_source_mgr.get(name="Fleet")
    if my_asset_source:
        source_id = my_asset_source.id
    else:
        my_asset_source = custom_source_mgr.create(name="Fleet")
        source_id = my_asset_source.id

    # create the import manager to upload custom assets
    import_mgr = CustomAssets(c)
    import_task = import_mgr.upload_assets(
        org_id=RUNZERO_ORG_ID, site_id=site.id, custom_integration_id=source_id, assets=assets, task_info=ImportTask(
            name="Fleet Sync")
    )

    if import_task:
        print(
            f"task created! view status here: https://console.runzero.com/tasks?task={import_task.id}")


def get_hosts():
    # TODO: can't get this to work - need a real tenant to test again
    # login_data = {
    #     "email": FLEET_EMAIL,
    #     "password": FLEET_PASSWORD
    # }
    # login_response = requests.post(
    #     FLEET_URL + "/api/v1/fleet/login", json=login_data)

    # token based auth
    fleet_headers = {
        "Authorization": f"Bearer {FLEET_TOKEN}"
    }

    has_next_page = True
    page = 0
    per_page = 100
    hosts_list = []
    while has_next_page:

        host_response = requests.get(
            FLEET_URL + "/api/v1/fleet/hosts", headers=fleet_headers, params={"page": page, "per_page": per_page}
        )
        hosts = host_response.json().get(hosts, [])

        if len(hosts) > 0:
            hosts_list.extend(hosts)
            page += 1
        else:
            has_next_page = False

    return hosts_list


if __name__ == "__main__":
    fleet_hosts = get_hosts()
    runzero_assets = build_assets_from_json(fleet_hosts)
    import_data_to_runzero(runzero_assets)
