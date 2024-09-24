load('runzero.types', 'ImportAsset', 'NetworkInterface')
load('json', json_encode='encode', json_decode='decode')
load('net', 'ip_address')
load('http', http_post='post', http_get='get', 'url_encode')

JAMF_URL = 'https://runzeronfr.jamfcloud.com'


def get_bearer_token(client_id, client_secret):
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'accept': 'application/json'}
    params={'client_id': client_id, 'client_secret': client_secret, 'grant_type': 'client_credentials'}
    url = "{}/{}".format(JAMF_URL, 'api/oauth/token')

    resp = http_post(url, headers=headers, body=bytes(url_encode(params)))
    if resp.status_code != 200:
        print("request bearer token returned status code", resp.status_code)
        return None

    body_json = json_decode(resp.body)
    if not body_json:
        print("invalid json body for bearer token")
        return None

    access_token = body_json['access_token']
    return access_token


def get_jamf_inventory(bearer_token):
    hasNextPage = True
    page = 0
    page_size = 500
    endpoints = []
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    url = JAMF_URL + '/api/v1/computers-inventory'
    while hasNextPage:
        params={"page": page, "page-size": page_size}
        resp = http_get(url=url, headers=headers, params=params)
        if resp.status_code != 200:
            print("unsuccessful request", "url={}".format(url), resp.status_code)
            return endpoints

        inventory = json_decode(resp.body)
        results = inventory.get('results', None)
        if not results:
            hasNextPage = False
            continue

        endpoints.extend(results)
        page += 1

    return endpoints


def get_jamf_details(bearer_token, inventory):
    # Needed to get extra info related to fingerprinting and networking information
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    endpoints_final = []
    for item in inventory:
        uid = item.get('id', None)
        if not uid:
            print("id not found in inventory item {}".format(item))
            continue

        url = "{}/api/v1/computers-inventory-detail/{uid}".format(JAMF_URL, uid=uid)
        resp = http_get(url=url, headers=headers)
        if resp.status_code != 200:
            print("response returned {} status for request {}".format(resp.status, url))
            return endpoints_final

        extra = json_decode(resp.body)
        item.update(extra)
        endpoints_final.append(item)

    return endpoints_final


def asset_ips(item):
    # handle IPs
    general = item.get("general", {})
    ips = []
    last_ip_address = general.get("lastIpAddress", "")
    if last_ip_address:
        ips.append(last_ip_address)

    last_reported_ip = general.get("lastReportedIp", "")
    if last_reported_ip:
        ips.append(last_reported_ip)

    return ips


def asset_os_hardware(item):
    # OS and hardware
    operating_system = item.get("operatingSystem", None)
    if not operating_system:
        print('operatingSystem key not found in item {}'.format(item))
        return {}

    hardware = item.get("hardware", None)
    if not hardware:
        print('hardware key not found in item {}'.format(item))
        return {}

    macs = []
    mac = hardware.get("macAddress", "")
    if mac:
        macs.append(mac)

    alt_mac = hardware.get("altMacAddress", "")
    if alt_mac:
        macs.append(alt_mac)

    return {
        'os_name': operating_system.get("name", ""),
        'os_version': operating_system.get("version", ""),
        'model': hardware.get("model", ""),
        'manufacturer': hardware.get("make", ""),
        'macs': macs
    }


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
    print(item)
    asset_id = item.get('udid', None)
    if not asset_id:
        print("udid not found in asset item {}".format(item))
        return

    general = item.get("general", None)
    if not general:
        print("general not found in asset item {}".format(item))
        return

    # OS and hardware
    os_hardware = asset_os_hardware(item)

    # create network interfaces
    ips = asset_ips(item)
    networks = []
    for m in os_hardware.get('macs', []):
        network = asset_networks(ips=ips, mac=m)
        networks.append(network)

    return ImportAsset(
        id=asset_id,
        networkInterfaces=networks,
        os=os_hardware.get('os', ''),
        osVersion=os_hardware.get('os_version', ''),
        manufacturer=os_hardware.get('manufacturer', ''),
        model=os_hardware.get('model', ''),
    )


def build_assets(inventory):
    assets = []
    for item in inventory:
        asset = build_asset(item)
        print("asset: {}".format(asset))
        assets.append(asset)

    return assets


def main(*args, **kwargs):
    client_id = kwargs['access_key']
    client_secret = kwargs['access_secret']

    bearer_token = get_bearer_token(client_id, client_secret)
    if not bearer_token:
        print("failed to get bearer_token")
        return None
    inventory = get_jamf_inventory(bearer_token)
    if not inventory:
        print("no inventory")
        return None
    details = get_jamf_details(bearer_token, inventory)
    if not details:
        print("no details")
        return None

    assets = build_assets(details)
    print(assets)
    if not assets:
        print("no assets")

    return assets