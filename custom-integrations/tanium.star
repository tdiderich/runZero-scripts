load('runzero.types', 'ImportAsset', 'NetworkInterface', 'Software', 'Vulnerability')
load('json', json_encode='encode', json_decode='decode')
load('net', 'ip_address')
load('http', http_post='post', http_get='get', 'url_encode')

def force_string(value):
    if type(value) == "list":
        output = ",".join([str(v) for v in value])
    elif type(value) == "dict":
        output = json_encode(value)
    else:
        output = str(value)

    return output[:1023]

def build_vulnerabilities(vulnerabilities):
    output_vulnerabilities = []
    uuid = 0
    for vuln in vulnerabilities:
        uuid += 1
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
        cvssScore = vuln.get("cvssScore", 0)
        if cvssScore == None:
            cvssScore = 0
        excepted = vuln.get("excepted", "")
        firstFound = vuln.get("firstFound", "")
        isCisaKev = vuln.get("isCisaKev", "")
        lastFound = vuln.get("lastFound", "")
        lastScanDate = vuln.get("lastScanDate", "")
        scanType = vuln.get("scanType", "")

        # take plain text severity and map to rz integer
        severity = vuln.get("severity", 0)

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
        output_vulnerabilities.append(
                Vulnerability(
                    id=str(uuid),
                    name=str(summary)[:255],
                    description=str(summary)[:255],
                    cve=str(cveId)[:13],
                    solution=str(cisaRequiredAction),
                    cvss2BaseScore=float(cvssScore),
                    cvss2TemporalScore=float(cvssScore),
                    cvss3BaseScore=float(cvssScore),
                    cvss3TemporalScore=float(cvssScore),
                    riskScore=float(score),
                    riskRank=risk_rank,
                    severityScore=float(score),
                    severityRank=risk_rank,
                    serviceAddress="127.0.0.1",
                    customAttributes={
                        "affectedProducts": force_string(affectedProducts),
                        "cisaDueDate": force_string(cisaDueDate),
                        "cisaNotes": force_string(cisaNotes),
                        "cisaProduct": force_string(cisaProduct),
                        "cisaRequiredAction": force_string(cisaRequiredAction),
                        "cisaVulnerabilityName": force_string(cisaVulnerabilityName),
                        "cisaVendor": force_string(cisaVendor),
                        "cveYear": force_string(cveYear),
                        "excepted": force_string(excepted),
                        "firstFound": force_string(firstFound),
                        "lastScanDate": force_string(lastScanDate),
                        "scanType": force_string(scanType),
                        "summary": force_string(summary),
                        "cpes": force_string(cpes),
                        "absoluteFirstFoundDate": force_string(absoluteFirstFoundDate),
                        "cisaDateAdded": force_string(cisaDateAdded),
                        "isCisaKev": force_string(isCisaKev),
                        "lastFound": force_string(lastFound),
                        "cisaShortDescription": force_string(cisaShortDescription),
                    },
                )
            )

    return output_vulnerabilities
def build_software(applications, installed_software):
    software = []
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
    for index, value in unique_applications.items():
        final_applications.append(value)

    for index in range(len(final_applications)):
        name = final_applications[index].get("name", "")
        vendor = final_applications[index].get("vendor", "")
        version = final_applications[index].get("version", "")
        software.append(
            Software(
                id=str(index),
                vendor=vendor,
                    product=name,
                    version=version,
                    serviceAddress="127.0.0.1",
                )
            )

    return software
def asset_networks(ips, mac):
    ip4s = []
    ip6s = []
    for ip in ips[:99]:
        ip_addr = ip_address(ip)
        if ip_addr.version == 4:
            ip4s.append(ip_addr)
        elif ip_addr.version == 6:
            ip6s.append(ip_addr)
        else:
            continue

    if not mac:
        return NetworkInterface(ipv4Addresses=ip4s, ipv6Addresses=ip6s)

    return NetworkInterface(macAddress=mac, ipv4Addresses=ip4s, ipv6Addresses=ip6s)


def build_asset(item):
    asset_id = item.get('id', None)
    if not asset_id:
        return None
    
    eid_first_seen = item.get("eidFirstSeen", None)
    computer_id = item.get("computerID", None)
    eid_last_seen = item.get("eidLastSeen", None)
    namespace = item.get("namespace", None)
    system_uuid = item.get("systemUUID", None)
    name = item.get("name", None)
    domain_name = item.get("domainName", None)
    serial_number = item.get("serialNumber", None)
    manufacturer = item.get("manufacturer", None)
    model = item.get("model", None)
    ip_address = item.get("ipAddress", None)
    mac_addresses = item.get("macAddresses", None)
    primary_user = item.get("primaryUser", None)
    last_logged_in_user = item.get("lastLoggedInUser", None)
    is_virtual = item.get("isVirtual", None)
    is_encrypted = item.get("isEncrypted", None)
    chassis_type = item.get("chassisType", None)
    os = item.get("os", None)
    services = item.get("services", None)
    installed_applications = item.get("installedApplications", None)
    deployed_software_packages = item.get("deployedSoftwarePackages", None)
    risk = item.get("risk", None)
    compliance = item.get("compliance", None)

    # create network interfaces
    ips = [ip_address]
    networks = []
    for m in mac_addresses:
        network = asset_networks(ips=ips, mac=m)
        networks.append(network)

    software = build_software(applications=installed_applications, installed_software=deployed_software_packages)
    vulnerabilities = build_vulnerabilities(vulnerabilities=compliance.get("cveFindings", []))
    return ImportAsset(
        id=asset_id,
        networkInterfaces=networks,
        os=os.get("name", None),
        osVersion=os.get('generation', ''),
        manufacturer=manufacturer,
        model=model,
        hostnames=[name],
        customAttributes={
            "eid_first_seen": eid_first_seen,
            "eid_last_seen": eid_last_seen,
            "namespace": namespace,
            "system_uuid": system_uuid,
            "serial_number": serial_number,
            "mac_addresses": mac_addresses,
            "primary_user": primary_user,
            "last_logged_in_user": last_logged_in_user,
            "is_virtual": is_virtual,
            "is_encrypted": is_encrypted,
            "risk": risk,
            "computer_id": computer_id,
        },
        domain=domain_name,
        # firstSeenTS=eid_first_seen, # TODO: add parsing
        deviceType=chassis_type,
        software=software[:99],
        vulnerabilities=vulnerabilities[:99]
    )


def build_assets(inventory):
    assets = []
    for item in inventory:
        asset_info = item.get("node", {})
        asset = build_asset(asset_info)
        if asset:
            assets.append(asset)

    return assets

def get_endpoints(tanium_url, tanium_token):
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

        body = {"query": query, "variables": variables}

        # get endpoints
        data = http_post(
            tanium_url + "/plugin/products/gateway/graphql",
            headers={"Content-Type": "application/json", "session": tanium_token},
            body=bytes(json_encode(body)),
        )
        
        # unnpack results and add to the endpoints
        json_data = json_decode(data.body)
        new_endpoints = json_data.get("data", {}).get("endpoints", {}).get("edges", [])
        endpoints.extend(new_endpoints)
        
        # check if there is a next page
        hasNextPage = json_data.get("data", {}).get("endpoints", {}).get("pageInfo", {}).get("hasNextPage", False)
        cursor = json_data.get("data", {}).get("endpoints", {}).get("pageInfo", {}).get("endCursor", None)
    
    return endpoints

def main(*args, **kwargs):
    tanium_url = "https://tk-runzero-api.titankube.com"
    tanium_token = kwargs['access_secret']

    tanium_endpoints = get_endpoints(tanium_url, tanium_token)

    if not tanium_endpoints:
        print("got nothing from Tanium")
        return None

    assets = build_assets(tanium_endpoints)

    if not assets:
        print("no assets")

    return assets