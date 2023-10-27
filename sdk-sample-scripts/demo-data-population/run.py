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
    ImportAsset,
    IPv4Address,
    IPv6Address,
    NetworkInterface,
    ImportTask
)

RUNZERO_DEMO_EXPORT_TOKEN = os.environ["RUNZERO_DEMO_EXPORT_TOKEN"]
RUNZERO_DEMO_CLIENT_ID = os.environ["RUNZERO_DEMO_CLIENT_ID"]
RUNZERO_DEMO_CLIENT_SECRET = os.environ["RUNZERO_DEMO_CLIENT_SECRET"]
RUNZERO_DEMO_ORG_ID = os.environ["RUNZERO_DEMO_ORG_ID"]
RUNZERO_DEMO_SITE_NAME = os.environ["RUNZERO_DEMO_SITE_NAME"]
BASE_URL = "https://demo.runzero.com/api/v1.0"
CUSTOM_INTEGRATIONS = ["fleet", "fortiedr", "jamf", "jumpcloud", "tanium"]


def import_data_to_runzero(name: str, assets: List[ImportAsset]):
    """
    The code below gives an example of how to create a custom source and upload valid assets from a CSV to a site using
    the new custom source.
    """
    # create the runzero client
    c = runzero.Client(server_url="https://demo.runzero.com")

    # try to log in using OAuth credentials
    try:
        c.oauth_login(RUNZERO_DEMO_CLIENT_ID, RUNZERO_DEMO_CLIENT_SECRET)
    except AuthError as e:
        print(f"login failed: {e}")
        return

    # create the site manager to get our site information
    site_mgr = Sites(c)
    site = site_mgr.get(RUNZERO_DEMO_ORG_ID, RUNZERO_DEMO_SITE_NAME)
    if not site:
        print(f"unable to find requested site")
        return

    # get or create the custom source manager and create a new custom source
    custom_source_mgr = CustomIntegrationsAdmin(c)
    my_asset_source = custom_source_mgr.get(name=name)
    if my_asset_source:
        source_id = my_asset_source.id
    else:
        my_asset_source = custom_source_mgr.create(name=name)
        source_id = my_asset_source.id

    # create the import manager to upload custom assets
    import_mgr = CustomAssets(c)
    import_task = import_mgr.upload_assets(
        org_id=RUNZERO_DEMO_ORG_ID, site_id=site.id, custom_integration_id=source_id, assets=assets, task_info=ImportTask(
            name=f"{name} sync")
    )

    if import_task:
        print(
            f"task created! view status here: https://console.runzero.com/tasks?task={import_task.id}")


def create_demo_data(assets=list, sample_attributes=dict):
    output = []

    for a in assets:
        asset_id = a.get("id")
        os_version = a.get("os_version")
        os = a.get("os")

        networks = []
        ips = []
        addresses = a.get("addresses", [])
        ips.extend(addresses)
        addresses_extra = a.get("addresses_extra", [])
        ips.extend(addresses_extra)
        macs = a.get("macs", [])
        names = a.get("names", [])
        for m in macs[:255]:
            network = build_network_interface(ips=ips[:255], mac=m)
            networks.append(network)

        custom_attrs: Dict[str] = {}
        skip = ["computer_name", "ipAddresses", "ipAddress",
                "hostname", "hostnames", "macAddresses", "macPairs", "os", "osVersion", "os_version", "manufacturer", "model", "deviceType"]
        for key, value in sample_attributes.items():
            if key not in skip:
                custom_attrs[key] = str(value)

        output.append(
            ImportAsset(
                id=asset_id,
                networkInterfaces=networks,
                hostnames=names,
                customAttributes=custom_attrs,
            )
        )

    return output


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


def get_assets():
    url = BASE_URL + "/export/org/assets.json"

    everything = requests.get(url, headers={"Authorization": f"Bearer {RUNZERO_DEMO_EXPORT_TOKEN}"}, params={
        "search": "alive:t (type:server or type:desktop or type:laptop) has_private:t", "fields": "id,os_vendor,os_product,os_version,os,addresses,addresses_extra,macs,names"})

    return everything.json()


if __name__ == "__main__":
    demo_assets = get_assets()
    for integration in CUSTOM_INTEGRATIONS:
        f = open(f'{integration}.json')
        data = json.load(f)
        sample_attributes = data.get("info")
        upload_assets = create_demo_data(
            assets=demo_assets, sample_attributes=sample_attributes)
        import_data_to_runzero(name=integration, assets=upload_assets)
