import json
import requests
import os
import uuid
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
RUNZERO_BASE_URL = 'https://console.runZero.com/api/v1.0'
RUNZERO_ORG_ID = os.environ['RUNZERO_ORG_ID']
RUNZERO_SITE_NAME = os.environ['RUNZERO_SITE_NAME']
RUNZERO_CLIENT_ID = os.environ['RUNZERO_CLIENT_ID']
RUNZERO_CLIENT_SECRET = os.environ['RUNZERO_CLIENT_SECRET']

# FortiThings
FORTI_KEY = os.environ['FORTI_KEY']
FORTI_HEADERS = {'Authorization': f'Basic {FORTI_KEY}'}
FORTI_BASE_URL = 'https://fortixdrnfrconnectna.console.ensilo.com'

# will need to change on a per integration basis to align wtih JSON object keys


def build_assets_from_json(json_input: List[Dict[str, Any]]) -> List[ImportAsset]:
    '''
    This is an example function to highlight how to handle converting data from an API into the ImportAsset format that
    is required for uploading to the runZero platform.
    This function assumes that the json has been converted into a list of dictionaries using `json.loads()` (or any
    similar functions).
    '''

    assets: List[ImportAsset] = []
    for item in json_input:
        # grab known API attributes from the json dict that are always present
        asset_id = item.get('id', uuid.uuid4)
        # I know this looks odd but formats the hostname how you'd normally see it
        name = item.get('name', '').replace(" ", "-").replace("’", "").upper()
        os = item.get('operatingSystem', '')
        macs = item.get('macAddresses', [])
        ip = item.get('ipAddress', '')

        # create network interfaces
        networks = []
        if len(macs) > 0:
            for mac in macs:
                network = build_network_interface(ips=[ip], mac=mac)
                networks.append(network)
        else:
            networks = build_network_interface(ips=[ip], mac=None)

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
                networkInterfaces=networks,
                os=os,
                hostnames=[name],
                customAttributes=custom_attrs,
            )
        )

    return assets

# should not need to change on a per integraton basis


def build_network_interface(ips: List[str], mac: str = None) -> NetworkInterface:
    '''
    This function converts a mac and a list of strings in either ipv4 or ipv6 format and creates a NetworkInterface that
    is accepted in the ImportAsset
    '''
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
        return NetworkInterface(macAddress=mac, ipv4Addresses=ip4s, ipv6Addresses=ip6s)


def import_data_to_runzero(assets: List[ImportAsset]):
    '''
    The code below gives an example of how to create a custom source and upload valid assets from a CSV to a site using
    the new custom source.
    '''
    # create the runzero client
    c = runzero.Client()

    # try to log in using OAuth credentials
    try:
        c.oauth_login(RUNZERO_CLIENT_ID, RUNZERO_CLIENT_SECRET)
    except AuthError as e:
        print(f'login failed: {e}')
        return

    # create the site manager to get our site information
    site_mgr = Sites(c)
    site = site_mgr.get(RUNZERO_ORG_ID, RUNZERO_SITE_NAME)
    if not site:
        print(f'unable to find requested site')
        return

    # get or create the custom source manager and create a new custom source
    custom_source_mgr = CustomIntegrationsAdmin(c)
    my_asset_source = custom_source_mgr.get(name='FortiEDR')
    if my_asset_source:
        source_id = my_asset_source.id
    else:
        my_asset_source = custom_source_mgr.create(name='FortiEDR')
        source_id = my_asset_source.id

    # create the import manager to upload custom assets
    import_mgr = CustomAssets(c)
    import_task = import_mgr.upload_assets(
        org_id=RUNZERO_ORG_ID, site_id=site.id, custom_integration_id=source_id, assets=assets, task_info=ImportTask(
            name='FortiEDR Sync')
    )

    if import_task:
        print(
            f'task created! view status here: https://console.runzero.com/tasks?task={import_task.id}')


def main():
    # Get assets from FortiEDR
    page = 0
    url = f'{FORTI_BASE_URL}/management-rest/inventory/list-collectors'
    go = True
    endpoints = []
    while go:
        # get endpoints from FortiEDR
        assets = requests.get(url, headers=FORTI_HEADERS,
                              params={"itemsPerPage": 1000, "pageNumber": page})
        endpoints_json = assets.json()

        if len(endpoints_json) > 0:
            endpoints.extend(endpoints_json)
            page += 1
        else:
            go = False

    # Imort to runZero
    import_assets = build_assets_from_json(endpoints)
    import_data_to_runzero(assets=import_assets)


if __name__ == '__main__':
    main()
