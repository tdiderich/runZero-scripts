import logging
import aiohttp
import asyncio
from logging.handlers import RotatingFileHandler
import requests
import os
from datetime import datetime, timezone, timedelta
import uuid
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

# configure runZero environment
RUNZERO_BASE_URL = os.getenv("RUNZERO_BASE_URL")
RUNZERO_ORG_ID = os.getenv("RUNZERO_ORG_ID")
RUNZERO_SITE_NAME = os.getenv("RUNZERO_SITE_NAME")
RUNZERO_CLIENT_ID = os.getenv("RUNZERO_CLIENT_ID")
RUNZERO_CLIENT_SECRET = os.getenv("RUNZERO_CLIENT_SECRET")

# configure jamf environment
JAMF_ID = os.getenv("JAMF_ID")
JAMF_SECRET = os.getenv("JAMF_SECRET")
JAMF_URL = os.getenv("JAMF_URL")

# configure logging
logger = logging.getLogger("runzero_logger")
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    fmt="%(asctime)s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

file_handler = RotatingFileHandler("jamf.log", maxBytes=5 * 1024 * 1024, backupCount=0)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)


def build_assets_from_json(json_input: List[Dict[str, Any]]) -> List[ImportAsset]:
    """
    This function parses data from integration source and builds asset records for import into runZero
    """
    assets: List[ImportAsset] = []
    for item in json_input:
        # grab known API attributes from the json dict that are always present
        asset_id = item.get("udid", "")
        asset_name = item.get("general", {}).get("name", "")

        # parse operating system and check for other os indicators if operatingSystem is empty
        operating_system = item.get("operatingSystem", "")
        if operating_system:
            os_name = item.get("operatingSystem", {}).get("name", "")
            if os_name == None:
                platform = item.get("general", {}).get("platform", "")
                if platform == "Mac":
                    os_name = "macOS"

            os_version = item.get("operatingSystem", {}).get("version", "")
            if os_version == None:
                os = f"{os_name}"
            else:
                os = f"{os_name} {os_version}"

        # parse hardware details
        macs = []
        hardware = item.get("hardware", "")
        if hardware:
            manufacturer = item.get("hardware", {}).get("make", "")
            model = item.get("hardware", {}).get("model", "")
            mac = item.get("hardware", {}).get("macAddress", "")
            if mac:
                macs.append(mac)
            alt_mac = item.get("hardware", {}).get("altMacAddress", "")
            if alt_mac:
                macs.append(alt_mac)

        # parse IP address fields
        ips = []
        last_ip_address = item.get("general", {}).get("lastIpAddress", "")
        if last_ip_address:
            ips.append(last_ip_address)

        last_reported_ip = item.get("general", {}).get("lastReportedIp", "")
        if last_reported_ip:
            ips.append(last_reported_ip)

        # create network interfaces
        networks = []
        for m in macs:
            network = build_network_interface(ips=ips, mac=m)
            networks.append(network)

        # build software inventory
        software = []
        applications = item.get("applications", [])
        if applications:
            for app in applications:
                id = str(uuid.uuid4)
                installed_size = app.get("sizeMegabytes", "")
                product = app.get("name", "")
                version = app.get("version", "")
                bundle_id = app.get("bundleId", None)
                update_available = app.get("updateAvailable", "")
                external_version_id = app.get("externalVersionId", "")
                path = app.get("path", "")
                if last_reported_ip:
                    service_address = last_reported_ip
                else:
                    service_address = "127.0.0.1"

                if id:
                    software.append(
                        Software(
                            id=id,
                            installed_size=installed_size,
                            product=product,
                            version=version,
                            service_address=service_address,
                            custom_attrs={
                                "budleId": bundle_id,
                                "updateAvailable": update_available,
                                "externalVersionId": external_version_id,
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
                if (
                    "extensionAttributes" not in key
                    and "contentCaching" not in key
                    and "storage" not in key
                    and "packageReceipts" not in key
                ):
                    custom_attrs[key] = str(value)[:1023]

        assets.append(
            ImportAsset(
                id=asset_id,
                hostnames=[asset_name],
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
    This function checks for a valid site and imports assets into runZero.
    """
    # create the runzero client
    c = runzero.Client()

    # try to log in using OAuth credentials
    try:
        c.oauth_login(RUNZERO_CLIENT_ID, RUNZERO_CLIENT_SECRET)
    except AuthError as e:
        logger.info(f"Login failed: {e}")
        return

    # create the site manager to get our site information
    site_mgr = Sites(c)
    site = site_mgr.get(RUNZERO_ORG_ID, RUNZERO_SITE_NAME)
    if not site:
        logger.info(f"Unable to find requested site")
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
        logger.info(
            f"Task created! View status here: https://console.runzero.com/tasks?task={import_task.id}"
        )


def get_token():
    url = JAMF_URL + "/api/v1/auth/token"
    headers = {"Accept": "application/json"}
    response = requests.post(url=url, headers=headers, auth=(JAMF_ID, JAMF_SECRET))
    if response.status_code != 200:
        logger.error(
            f"Unable to retrieve API token. HTTP response code {response.status_code} received from {url}"
        )
        exit(1)
    else:
        logger.info(
            f"Successfully retrieved API token. HTTP response code {response.status_code} received from {url}"
        )
        return response.json()


def token_about_to_expire(bearer_token_expiration, threshold_seconds=180):
    expiration_time = datetime.strptime(
        bearer_token_expiration, "%Y-%m-%dT%H:%M:%S.%fZ"
    )
    current_time = datetime.now(timezone.utc).replace(tzinfo=None)
    time_difference = abs(expiration_time - current_time)
    threshold = timedelta(seconds=threshold_seconds)
    logger.debug(
        f"Token expiration time: {expiration_time} current_time: {current_time} time_difference: {time_difference} threshold: {threshold}"
    )
    return time_difference <= threshold


def token_keep_alive(bearer_token):
    url = JAMF_URL + "/api/auth/keep-alive"
    headers = {"Authorization": f"Bearer {bearer_token}"}
    response = requests.post(url=url, headers=headers)
    if response.status_code != 200:
        logger.error(
            f"Unable to retrieve API token. HTTP response code {response.status_code} received from {url}"
        )
        exit(1)
    else:
        logger.info(
            f"Successfully retrieved API token. HTTP response code {response.status_code} received from {url}"
        )
        return response


async def get_extra_info(session, headers, url):
    async with session.get(url, headers=headers) as resp:
        if resp.status != 200:
            logger.error(
                f"Unable to retrieve endpoint details. HTTP response code {resp.status} received from {url}"
            )
            exit(1)
        else:
            extra = await resp.json()

        return extra

async def get_endpoints(token):
    hasNextPage = True
    page = 0
    page_size = 100
    endpoints = []

    bearer_token = token.get("token")
    bearer_token_expiration = token.get("expires")

    # Get asset records from Jamf
    while hasNextPage:
        if token_about_to_expire(bearer_token_expiration):
            logger.info(
                "Token is about to expire. Token expiration: {bearer_token_expiration}. Requesting new token."
            )
            token = token_keep_alive(bearer_token)
            bearer_token = token.get("token")
            bearer_token_expiration = token.get("expires")

        url = JAMF_URL + "/api/v1/computers-inventory"
        headers = {"Authorization": f"Bearer {bearer_token}"}
        computers = requests.get(
            url=url, headers=headers, params={"page": page, "page-size": page_size}
        )

        if computers.status_code != 200:
            logger.error(
                f"Unable to retrieve endpoints. HTTP response code {computers.status_code} received from {url}"
            )
            exit(1)

        results = computers.json().get("results", [])
        count = len(results)

        if len(results) > 0:
            total_count = computers.json().get("totalCount", 0)
            logger.info(
                f"Successfully downloaded {count} records of {total_count} total records from {url}"
            )
            endpoints.extend(results)
            page += 1
        else:
            logger.info(f"No records downloaded on last call to {url}")
            hasNextPage = False

    # Get additional details regarding each asset record
    endpoints_all = []

    asset_count = 0
    asset_chunk = 0
    endpoints_final = []
    async with aiohttp.ClientSession() as session:
        tasks = []
        for e in endpoints:
            uid = e.get("id", "")
            if uid:
                # Renew token if its close to expiring
                if token_about_to_expire(bearer_token_expiration):
                    logger.info(
                        f"Token is about to expire. Token expiration: {bearer_token_expiration}. Requesting new token."
                    )
                    token = token_keep_alive(bearer_token)
                    bearer_token = token.get("token")
                    bearer_token_expiration = token.get("expires")

                headers = {"Authorization": f"Bearer {bearer_token}"}

                url = JAMF_URL + f"/api/v1/computers-inventory-detail/{uid}"
                tasks.append(
                    asyncio.ensure_future(get_extra_info(session, headers, url))
                )

                endpoints_final = await asyncio.gather(*tasks)
    
    return endpoints_final


async def main():
    token = get_token()
    jamf_endpoints = await get_endpoints(token)
    if len(jamf_endpoints) > 0:
        logger.info("Building assets from json to import into runZero")
        runzero_assets = build_assets_from_json(jamf_endpoints)
        logger.info("Importing assets into runZero")
        import_data_to_runzero(runzero_assets)
    else:
        logger.info("No endpoints to upload")


asyncio.run(main())
