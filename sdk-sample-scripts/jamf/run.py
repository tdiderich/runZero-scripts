import requests
import os
from flatten_json import flatten
from ipaddress import ip_address
from typing import Any, Dict, List
import runzero
from runzero.client import AuthError
from runzero.api import CustomAssets, CustomIntegrationsAdmin, Sites
from runzero.types import (
    CustomAttribute,
    ImportAsset,
    IPv4Address,
    IPv6Address,
    NetworkInterface,
    ImportTask,
    Software,
)

# runZero creds
RUNZERO_BASE_URL = "https://console.runZero.com/api/v1.0"
RUNZERO_ORG_ID = os.environ["RUNZERO_ORG_ID"]
RUNZERO_SITE_NAME = os.environ["RUNZERO_SITE_NAME"]
RUNZERO_CLIENT_ID = os.environ["RUNZERO_CLIENT_ID"]
RUNZERO_CLIENT_SECRET = os.environ["RUNZERO_CLIENT_SECRET"]

# JAMF creds
JAMF_ID = os.environ["JAMF_ID"]
JAMF_SECRET = os.environ["JAMF_SECRET"]
JAMF_URL = os.environ["JAMF_URL"]

# Will need to change on a per integration basis to align wtih JSON object keys


def build_assets_from_json(json_input: List[Dict[str, Any]]) -> List[ImportAsset]:
    assets: List[ImportAsset] = []
    for item in json_input:
        # id
        asset_id = item.get("udid", "")

        # handle IPs
        general = item.get("general", {})
        ips = []
        last_ip_address = general.get("lastIpAddress", "")
        if last_ip_address:
            ips.append(last_ip_address)

        last_reported_ip = general.get("lastReportedIp", "")
        if last_reported_ip:
            ips.append(last_reported_ip)

        # OS and harware
        os_name = item.get("operatingSystem", {}).get("name", "")
        os_version = item.get("operatingSystem", {}).get("version", "")
        os = f"{os_name} {os_version}"
        manufacturer = item.get("hardware", {}).get("make", "")
        model = item.get("hardware", {}).get("model", "")
        macs = []
        mac = item.get("hardware", {}).get("macAddress", "")
        if mac:
            macs.append(mac)
        alt_mac = item.get("hardware", {}).get("altMacAddress", "")
        if alt_mac:
            macs.append(alt_mac)

        # create network interfaces
        networks = []
        for m in macs:
            network = build_network_interface(ips=ips, mac=m)
            networks.append(network)

        software = []
        applications = item.get("applications", [])
        for app in applications:
            id = app.get("bundleId", None)
            installed_size = app.get("sizeMegabytes", "")
            product = app.get("name", "")
            version = app.get("version", "")
            updateAvailable = app.get("updateAvailable", "")
            externalVersionId = app.get("externalVersionId", "")
            path = app.get("path", "")

            if id:
                software.append(
                    Software(
                        id=id,
                        installed_size=installed_size,
                        product=product,
                        version=version,
                        service_address="127.0.0.1",
                        custom_attrs={
                            "updateAvailable": updateAvailable,
                            "externalVersionId": externalVersionId,
                            "path": path,
                        },
                    )
                )

        # handle any additional values and insert into custom_attrs
        custom_attrs: Dict[str, CustomAttribute] = {}

        root_keys_to_ignore = []
        for key, value in item.items():
            if not isinstance(value, dict) and value is not None:
                root_keys_to_ignore.append(key)

        flattened_items = flatten(
            nested_dict=item, root_keys_to_ignore=root_keys_to_ignore
        )

        item = flattened_items | item

        for key, value in item.items():
            if not isinstance(value, dict) and value is not None:
                if len(custom_attrs) < 1022:
                    custom_attrs[key] = str(value)[:1022]

        assets.append(
            ImportAsset(
                id=asset_id,
                networkInterfaces=networks,
                os=os,
                osVersion=os_version,
                manufacturer=manufacturer,
                model=model,
                software=software,
                customAttributes=custom_attrs,
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
    my_asset_source = custom_source_mgr.get(name="jamf")
    if my_asset_source:
        source_id = my_asset_source.id
    else:
        my_asset_source = custom_source_mgr.create(name="jamf")
        source_id = my_asset_source.id

    # create the import manager to upload custom assets
    import_mgr = CustomAssets(c)
    import_task = import_mgr.upload_assets(
        org_id=RUNZERO_ORG_ID,
        site_id=site.id,
        custom_integration_id=source_id,
        assets=assets,
        task_info=ImportTask(name="JAMF Sync"),
    )

    if import_task:
        print(
            f"task created! view status here: https://console.runzero.com/tasks?task={import_task.id}"
        )

def get_access_token():
    token_url = f"{JAMF_URL}/api/oauth/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    payload = {
        "client_id": JAMF_ID,
        "client_secret": JAMF_SECRET,
        "grant_type": "client_credentials"
    }
    
    response = requests.post(token_url, headers=headers, data=payload)
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get('access_token')
        return access_token
    else:
        print(f"Failed to retrieve access token. HTTP Status: {response.status_code}")
        return None

def get_endpoints():
    token = get_access_token()
    if token:
        hasNextPage = True
        page = 0
        page_size = 500
        endpoints = []
        headers = {"Authorization": f"Bearer {token}"}
        url = JAMF_URL + "/api/v1/computers-inventory"
        while hasNextPage:
            computers = requests.get(
                url=url, headers=headers, params={"page": page, "page-size": page_size}
            )
            results = computers.json().get("results", [])
            if len(results) > 0:
                endpoints.extend(results)
                page += 1
            else:
                hasNextPage = False
        # TODO: likely needs rate limiting in a real environment
        # Needed to get extra info related to fingerprinting and networking information           
        endpoints_final = []
        for e in endpoints:
            uid = e.get("id", "")
            if uid:
                url = JAMF_URL + f"/api/v1/computers-inventory-detail/{uid}"
                extra_info = requests.get(url=url, headers=headers)
                extra = extra_info.json()
                e.update(extra)
                endpoints_final.append(e)
        return endpoints_final
    else:
        print("Unable to get API token")
        return []

if __name__ == "__main__":
    jamf_endpoints = get_endpoints()
    if len(jamf_endpoints) > 0:
        runzero_assets = build_assets_from_json(jamf_endpoints)
        import_data_to_runzero(runzero_assets)
    else:
        print("No endpoints to upload")