import requests
import json
from datetime import datetime, timedelta
import uuid
import jwt
import os
import re
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

# cylance creds
CYLANCE_URL = os.environ["CYLANCE_URL"]
CYLANCE_TENANT_ID = os.environ["CYLANCE_TENANT_ID"]
CYLANCE_APP_ID = os.environ["CYLANCE_APP_ID"]
CYLANCE_APP_SECRET = os.environ["CYLANCE_APP_SECRET"]

# mac match check
mac_match = re.compile(
    pattern='^([A-Fa-f0-9]{2}: ){5}[A-Fa-f0-9]{2}$| ^([A-Fa-f0-9]{2}: ){7}[A-Fa-f0-9]{2}$| ^([A-Fa-f0-9]{2}-){5}[A-Fa-f0-9]{2}$| ^([A-Fa-f0-9]{2}-){7}[A-Fa-f0-9]{2}$| ^([A-Fa-f0-9]{4}\.){2}[A-Fa-f0-9]{4}$| ^([A-Fa-f0-9]{4}\.){3}[A-Fa-f0-9]{4}$| ^([A-Fa-f0-9]{4} ){3}[A-Fa-f0-9]{4}$')

# Will need to change on a per integration basis to align wtih JSON object keys


def build_assets_from_json(json_input: List[Dict[str, Any]]) -> List[ImportAsset]:

    assets: List[ImportAsset] = []
    for item in json_input:

        asset_id = item.get("id", "")

        hostnames = []
        host_name = item.get("host_name", None)
        if host_name:
            hostnames.append(host_name)
        name = item.get("name", None)
        if name:
            hostnames.append(name)

        networks = []
        ips = item.get("ip_addresses", [])
        macs = item.get("mac_addresses", [])
        for mac in macs:
            network_interface = build_network_interface(ips=ips, mac=mac)
            networks.append(network_interface)

        os_version = item.get("os_version", "")
        os = item.get("os_version", "")

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
                custom_attrs[key] = CustomAttribute(str(value)[:1022])

        assets.append(ImportAsset(
            id=asset_id,
            networkInterfaces=networks,
            os=os,
            hostnames=hostnames,
            customAttributes=custom_attrs,
            osVersion=os_version
        ))

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
    my_asset_source = custom_source_mgr.get(name="cylance")
    if my_asset_source:
        source_id = my_asset_source.id
    else:
        my_asset_source = custom_source_mgr.create(name="cylance")
        source_id = my_asset_source.id

    # create the import manager to upload custom assets
    import_mgr = CustomAssets(c)
    import_task = import_mgr.upload_assets(
        org_id=RUNZERO_ORG_ID, site_id=site.id, custom_integration_id=source_id, assets=assets, task_info=ImportTask(
            name="cylance Sync")
    )

    if import_task:
        print(
            f"task created! view status here: https://console.runzero.com/tasks?task={import_task.id}")


def get_hosts():
    timeout = 1800
    now = datetime.utcnow()
    timeout_datetime = now + timedelta(seconds=timeout)
    epoch_time = int((now - datetime(1970, 1, 1)).total_seconds())
    epoch_timeout = int(
        (timeout_datetime - datetime(1970, 1, 1)).total_seconds())
    jti_val = str(uuid.uuid4())
    claims = {
        "exp": epoch_timeout,
        "iat": epoch_time,
        "iss": "http://cylance.com",
        "sub": CYLANCE_APP_ID,
        "tid": CYLANCE_TENANT_ID,
        "jti": jti_val
    }

    encoded = jwt.encode(claims, CYLANCE_APP_SECRET, algorithm='HS256')
    payload = {"auth_token": encoded}
    headers = {"Content-Type": "application/json; charset=utf-8"}

    token = requests.post(CYLANCE_URL + "/auth/v2/token",
                          headers=headers, json=payload)

    access_token = token.json().get("access_token", None)
    endpoints = []

    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
        has_next_page = True
        page = 1
        page_size = 100

        while has_next_page:
            host_response = requests.get(
                CYLANCE_URL + "/devices/v2/extended", headers=headers, params={"page": page, "page_size": page_size})
            hosts = host_response.json().get("page_items", [])

            if len(hosts) == 0:
                has_next_page = False
            else:
                endpoints.extend(hosts)
                page += 1

    return endpoints


if __name__ == "__main__":
    cylance_hosts = get_hosts()
    runzero_assets = build_assets_from_json(cylance_hosts)
    import_data_to_runzero(runzero_assets)
