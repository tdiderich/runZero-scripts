import requests
import os
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

# Tanium creds
TANIUM_URL = os.environ["TANIUM_URL"]
TANIUM_TOKEN = os.environ["TANIUM_TOKEN"]

# Will need to change on a per integration basis to align wtih JSON object keys


def build_assets_from_json(json_input: List[Dict[str, Any]]) -> List[ImportAsset]:

    assets: List[ImportAsset] = []
    for item in json_input:
        asset_id = item.get("id")
        name = item.get("name", "")
        os = item.get("os", {}).get("name", "")
        macs = item.get("macAddresses", [])
        ip = item.get("ipAddress", "")
        domain = item.get("domainName", "")
        firstSeenTS = item.get("eidFirstSeen", "")
        osVersion = item.get("os", {}).get("generation", "")
        manufacturer = item.get("manufacturer", "")
        model = item.get("model", "")
        deviceType = item.get("chassisType", "")

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
                domain=domain,
                firstSeenTS=firstSeenTS,
                osVersion=osVersion,
                manufacturer=manufacturer,
                model=model,
                deviceType=deviceType,
            )
        )

    print(assets)
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
    my_asset_source = custom_source_mgr.get(name="Tanium")
    if my_asset_source:
        source_id = my_asset_source.id
    else:
        my_asset_source = custom_source_mgr.create(name="Tanium")
        source_id = my_asset_source.id

    # create the import manager to upload custom assets
    import_mgr = CustomAssets(c)
    import_task = import_mgr.upload_assets(
        org_id=RUNZERO_ORG_ID, site_id=site.id, custom_integration_id=source_id, assets=assets, task_info=ImportTask(
            name="Tanium Sync")
    )

    if import_task:
        print(
            f"task created! view status here: https://console.runzero.com/tasks?task={import_task.id}")


def get_endpoints():
    query = """query getEndpoints($first: Int, $after: Cursor) {
    endpoints(first: $first, after: $after) {
        edges {
        node {
            id
            eidFirstSeen
            eidLastSeen
            namespace
            computerID
            systemUUID
            name
            domainName
            serialNumber
            manufacturer
            model
            ipAddress
            macAddresses
            primaryUser {
                name
                email
            }
            lastLoggedInUser
            isVirtual
            isEncrypted
            chassisType
            os {
                name 
                platform
                generation
                language
            }
            services {
                name
                status
            }
            installedApplications {
                name
                version
            }
            deployedSoftwarePackages {
                name
                vendor
                version
            }
            risk {
                totalScore
                riskLevel
                assetCriticality
                criticalityScore
            }
        }
        }
        pageInfo {
        hasNextPage
        endCursor
        startCursor
        }
        totalRecords
    }
    }"""
    cursor = None
    hasNextPage = True
    endpoints = []
    while hasNextPage:

        # set cursor if it exists (all but the first query)
        if cursor:
            variables = {"first": 100, "after": cursor}
        else:
            variables = {"first": 100}

        # get endpoints
        data = requests.post(TANIUM_URL + "/plugin/products/gateway/graphql",
                             headers={"Content-Type": "application/json", "session": TANIUM_TOKEN}, json={"query": query, "variables": variables})

        # grab data from the response
        endpoints.extend(data.json()["data"]["endpoints"]["edges"])
        hasNextPage = data.json(
        )["data"]["endpoints"]["pageInfo"]["hasNextPage"]
        cursor = data.json()["data"]["endpoints"]["pageInfo"]["startCursor"]

    return endpoints


if __name__ == "__main__":
    tanium_endpoints = get_endpoints()
    runzero_endpoints = []
    for t in tanium_endpoints:
        runzero_endpoints.append(t["node"])
    runzero_assets = build_assets_from_json(runzero_endpoints)
    import_data_to_runzero(runzero_assets)
