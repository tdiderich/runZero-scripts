import requests
import os
import json
import uuid
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
    ImportTask,
    Software,
    Vulnerability,
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


def force_string(value: Any) -> str:
    if isinstance(value, list):
        output = ",".join(str(v) for v in value)
    elif isinstance(value, dict):
        output = json.dumps(value)
    else:
        output = str(value)

    return output[:1023]


def build_assets_from_json(json_input: List[Dict[str, Any]]) -> List[ImportAsset]:
    assets: List[ImportAsset] = []
    for item in json_input:
        asset_id = item.get("id")
        hostname = item.get("name", "")
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

        software = []
        applications = item.get("installedApplications", [])
        installed_software = item.get("deployedSoftwarePackages", [])
        unique_applications = {}
        for a in applications + installed_software:
            key_list = a.get("name", "").split(" ")
            key_unique = (
                "_".join(key_list[0:2]) if len(key_list) > 1 else "_".join(key_list)
            )
            if key_unique not in unique_applications:
                unique_applications[key_unique] = {
                    "name": a.get("name", ""),
                    "version": a.get("version", ""),
                    "vendor": a.get("vendor", ""),
                }
        final_applications = []
        for _, value in unique_applications.items():
            final_applications.append(value)

        for app in final_applications:
            name = app.get("name", "")
            vendor = app.get("vendor", "")
            version = app.get("version", "")

            software.append(
                Software(
                    id=str(uuid.uuid4()),
                    vendor=vendor,
                    product=name,
                    version=version,
                    service_address="127.0.0.1",
                )
            )

        vulnerabilities = []
        tanium_vulnerabilities = item.get("compliance", {}).get("cveFindings", [])
        for vuln in tanium_vulnerabilities:
            absoluteFirstFoundDate = vuln.get("absoluteFirstFoundDate", "")
            affectedProducts = vuln.get("affectedProducts", "")
            cisaDateAdded = vuln.get("cisaDateAdded", "")
            cisaDueDate = vuln.get("cisaDueDate", "")
            cisaNotes = vuln.get("cisaNotes", "")
            cisaProduct = vuln.get("cisaProduct", "")
            cisaRequiredAction = vuln.get("cisaRequiredAction", "")
            cisaShortDescription = vuln.get("cisaShortDescription", "")
            cisaVendor = vuln.get("cisaVendor", "")
            cisaVulnerabilityName = vuln.get("cisaVulnerabilityName", "")
            cpes = vuln.get("cpes", [])
            cveId = vuln.get("cveId", "")
            cveYear = vuln.get("cveYear", "")
            cvssScore = vuln.get("cvssScore", "")
            excepted = vuln.get("excepted", "")
            firstFound = vuln.get("firstFound", "")
            isCisaKev = vuln.get("isCisaKev", "")
            lastFound = vuln.get("lastFound", "")
            lastScanDate = vuln.get("lastScanDate", "")
            scanType = vuln.get("scanType", "")

            # take plain text severity and map to rz integer
            severity = vuln.get("severity", "")

            rank_map = {
                "Critical": 4,
                "High": 3,
                "Medium": 2,
                "Low": 1,
            }

            score_map = {
                "Critical": 10,
                "High": 7,
                "Medium": 5,
                "Low": 2,
            }

            if severity in rank_map:
                risk_rank = rank_map[severity]
                score = score_map[severity]
            else:
                risk_rank = 0
                score = 0

            summary = vuln.get("summary", "")

            try:
                vulnerabilities.append(
                    Vulnerability(
                        id=str(uuid.uuid4()),
                        name=str(summary)[:255],
                        description=str(summary)[:255],
                        cve=str(cveId)[:13],
                        solution=str(cisaRequiredAction),
                        cvss2BaseScore=cvssScore,
                        cvss2TemporalScore=cvssScore,
                        cvss3BaseScore=cvssScore,
                        cvss3TemporalScore=cvssScore,
                        risk_score=score,
                        risk_rank=risk_rank,
                        severity_score=score,
                        severity_rank=risk_rank,
                        service_address="127.0.0.1",
                        customAttributes={
                            "affectedProducts": force_string(affectedProducts),
                            "cisaDueDate": force_string(cisaDueDate),
                            "cisaNotes": force_string(cisaNotes),
                            "cisaProduct": force_string(cisaProduct),
                            "cisaRequiredAction": force_string(cisaRequiredAction),
                            "cisaVulnerabilityName": force_string(
                                cisaVulnerabilityName
                            ),
                            "cisaVendor": force_string(cisaVendor),
                            "cveYear": force_string(cveYear),
                            "excepted": force_string(excepted),
                            "firstFound": force_string(firstFound),
                            "lastScanDate": force_string(lastScanDate),
                            "scanType": force_string(scanType),
                            "summary": force_string(summary),
                            "cpes": force_string(cpes),
                            "absoluteFirstFoundDate": force_string(
                                absoluteFirstFoundDate
                            ),
                            "cisaDateAdded": force_string(cisaDateAdded),
                            "isCisaKev": force_string(isCisaKev),
                            "lastFound": force_string(lastFound),
                            "cisaShortDescription": force_string(cisaShortDescription),
                        },
                    )
                )

            except:
                vulnerabilities.append(
                    Vulnerability(
                        id=str(uuid.uuid4()),
                        name=str(summary)[:255],
                        description=str(summary)[:255],
                        solution=str(cisaRequiredAction),
                        risk_score=score,
                        risk_rank=risk_rank,
                        severity_score=score,
                        severity_rank=risk_rank,
                        customAttributes={
                            "affectedProducts": force_string(affectedProducts),
                            "cisaDueDate": force_string(cisaDueDate),
                            "cisaNotes": force_string(cisaNotes),
                            "cisaProduct": force_string(cisaProduct),
                            "cisaRequiredAction": force_string(cisaRequiredAction),
                            "cisaVendor": force_string(cisaVendor),
                            "cisaVulnerabilityName": force_string(
                                cisaVulnerabilityName
                            ),
                            "cveYear": force_string(cveYear),
                            "excepted": force_string(excepted),
                            "firstFound": force_string(firstFound),
                            "lastScanDate": force_string(lastScanDate),
                            "scanType": force_string(scanType),
                            "summary": force_string(summary),
                            "cpes": force_string(cpes),
                            "absoluteFirstFoundDate": force_string(
                                absoluteFirstFoundDate
                            ),
                            "cisaDateAdded": force_string(cisaDateAdded),
                            "isCisaKev": force_string(isCisaKev),
                            "lastFound": force_string(lastFound),
                            "cisaShortDescription": force_string(cisaShortDescription),
                        },
                    )
                )

        # handle any additional values and insert into custom_attrs
        custom_attrs: Dict[str] = {}

        root_keys_to_ignore = [
            "installedApplications",
            "deployedSoftwarePackages",
            "compliance",
        ]
        for key, value in item.items():
            if not isinstance(value, dict) and value is not None:
                root_keys_to_ignore.append(key)

        flattened_items = flatten(
            nested_dict=item, root_keys_to_ignore=root_keys_to_ignore
        )

        item = flattened_items

        for key, value in item.items():
            if not isinstance(value, dict) and value is not None:
                if len(custom_attrs) < 1022:
                    custom_attrs[key] = str(value)[:1022]

        assets.append(
            ImportAsset(
                id=asset_id,
                networkInterfaces=networks,
                os=os,
                hostnames=[hostname],
                customAttributes=custom_attrs,
                domain=domain,
                firstSeenTS=firstSeenTS,
                osVersion=osVersion,
                manufacturer=manufacturer,
                model=model,
                deviceType=deviceType,
                software=software[:99],
                vulnerabilities=vulnerabilities[:99],
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
    try:
        return NetworkInterface(macAddress=mac, ipv4Addresses=ip4s, ipv6Addresses=ip6s)
    except:
        return NetworkInterface(ipv4Addresses=ip4s, ipv6Addresses=ip6s)


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
        org_id=RUNZERO_ORG_ID,
        site_id=site.id,
        custom_integration_id=source_id,
        assets=assets,
        task_info=ImportTask(name="Tanium Sync"),
    )

    if import_task:
        print(
            f"task created! view status here: https://console.runzero.com/tasks?task={import_task.id}"
        )


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
            compliance {
                cveFindings {
                    absoluteFirstFoundDate
                    affectedProducts
                    cisaDateAdded
                    cisaDueDate
                    cisaNotes
                    cisaProduct
                    cisaRequiredAction
                    cisaShortDescription
                    cisaVendor
                    cisaVulnerabilityName
                    cpes
                    cveId
                    cveYear
                    cvssScore
                    excepted
                    firstFound
                    isCisaKev
                    lastFound
                    lastScanDate
                    scanType
                    severity
                    summary
                }
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
        data = requests.post(
            TANIUM_URL + "/plugin/products/gateway/graphql",
            headers={"Content-Type": "application/json", "session": TANIUM_TOKEN},
            json={"query": query, "variables": variables},
        )

        # grab data from the response
        endpoints.extend(data.json()["data"]["endpoints"]["edges"])
        hasNextPage = data.json()["data"]["endpoints"]["pageInfo"]["hasNextPage"]
        cursor = data.json()["data"]["endpoints"]["pageInfo"]["endCursor"]

    return endpoints


if __name__ == "__main__":
    tanium_endpoints = get_endpoints()
    runzero_endpoints = []
    for t in tanium_endpoints:
        runzero_endpoints.append(t["node"])
    runzero_assets = build_assets_from_json(runzero_endpoints)
    import_data_to_runzero(runzero_assets)
