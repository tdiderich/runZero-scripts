import os
import requests
import json
import time
import random
import re
import gzip
import base64

#### NETWORK OVERVIEW ####

# Corporate: 10.0.0.0 - 10.0.255.255

## Standard end user assets - Linux, Apple, and Windows devices
### RZ Scan, CrowdStrike, Nessus, and AzureAD

## Routers
### RZ Scan and Nessus

## WAP
### RZ Scan and Nessus

# Datacenter: 10.1.0.0 - 10.1.255.255 = datacenter

## Servers - Linux and Windows devices
### RZ Scan, CrowdStrike, Nessus, and AzureAD

## Routers
### RZ Scan and Nessus

## Switches
### RZ Scan and Nessus

## UPS
### RZ Scan

## BACnet
### RZ Scan

## PLC
### RZ Scan

# Cloud: 240.0.0.0 - 240.0.255.255
## Servers
### AWS OR Azure OR GCP + RZ Scan, Shodan, CrowdStrike, and Nessus

## Databases
### AWS OR Azure OR GCP + RZ Scan and Shodan

## Load balancers
### AWS OR Azure OR GCP + RZ Scan and Shodan

#### END NETWORK OVERVIEW ####

# Creds for uploading tasks to rz
RUNZERO_BASE_URL = "https://console.runZero.com/api/v1.0"
RUNZERO_ORG_ID = "91bf5f0a-dbf9-4622-8d86-40aaaec90c78"
RUNZERO_SITE_ID = "a1a2ecdb-cea7-4390-a873-ce6322bdd14d"
NESSUS_SITE_ID = "5d6b0c27-962b-4b10-9ee6-b9f887a748e1"
CS_SITE_ID = "680d5979-76dd-4b7d-a10b-ce3f8d369eed"
RUNZERO_ORG_TOKEN = os.environ["RUNZERO_ORG_TOKEN"]

OUTPUT = []

# Markers for common compute assets
COMPUTE_ASSETS = {
    "Microsoft Windows Server 2019": {
        "host": "192.168.0.244",
        "filename": "scan_lab.json",
        "hostname": "AUSTIN-TEST-LAB",
        "type": "SERVER",
        "secondary_v4": "192.168.0.244",
        "mac": "00:02:A5:61:54:57",
    },
    "Microsoft Windows 11": {
        "host": "192.168.40.232",
        "filename": "scan_lab.json",
        "hostname": "WINDOWS11PRO",
        "type": "LAPTOP",
        "secondary_v4": "192.168.40.232",
        "secondary_v6": "fe80::5ab3:e54c:2653:12be",
        "mac": "BC:24:11:32:3E:3B",
    },
    "Microsoft Windows Server 2016": {
        "host": "192.168.40.249",
        "filename": "scan_lab.json",
        "hostname": "RZ2K16SERVER",
        "domain": "RZ2K16",
        "type": "SERVER",
        "secondary_v4": "192.168.40.249",
        "mac": "BC:24:11:A1:D8:AF",
    },
    "Microsoft Windows Server": {
        "host": "192.168.40.233",
        "filename": "scan_lab.json",
        "hostname": "WIN-LB4096E0RUP",
        "type": "SERVER",
        "secondary_v4": "192.168.40.233",
        "mac": "BC:24:11:19:D4:0F",
    },
    "Ubuntu Linux 22.04.2": {
        "host": "192.168.50.20",
        "filename": "scan_lab.json",
        "hostname": "RUNZERO",
        "type": "SERVER",
        "mac": "94:C6:91:15:4D:91",
    },
    "Raspbian Linux 9.0": {
        "host": "192.168.0.8",
        "filename": "scan_lab.json",
        "hostname": "RPI3-ACCESS-CONTROL|PIT.HDM.IO",
        "type": "SERVER",
        "mac": "B8:27:EB:E6:4D:41",
    },
    "Linux": {
        "host": "192.168.40.26",
        "filename": "scan_lab.json",
        "type": "SERVER",
        "mac": "08:EA:44:37:F3:40",
    },
    "Apple iOS": {
        "host": "192.168.30.204",
        "filename": "scan_lab.json",
        "type": "MOBILE",
        "mac": "F8:BE:5A:54:FD:11",
    },
    "Apple macOS 14.0": {
        "host": "192.168.0.53",
        "filename": "scan_lab.json",
        "hostname": "SLAB",
        "type": "LAPTOP",
        "secondary_v4": "192.168.30.56",
        "secondary_v6": "fe80::5ab3:e54c:2653:12be",
        "mac": "BC:D0:74:73:EC:17",
    },
    "Apple tvOS 17.5": {
        "host": "192.168.30.241",
        "filename": "scan_lab.json",
        "hostname": "OPNSENSE.LOCALDOMAIN",
        "type": "SENSOR",
        "secondary_v4": "192.168.30.56",
        "secondary_v6": "fdc5:e46c:5da8:4b48:6:fde2:62f1:8748",
        "mac": "A4:CF:99:AB:0C:1B",
    },
}

# Markers for routers and WAP devices
ROUTING_ASSETS = {
    "Adtran NetVanta AOS": {
        "host": "192.168.40.27",
        "filename": "scan_lab.json",
        "hostname": "ADTRAN225",
        "type": "ROUTER",
        "mac": "00:a0:c8:5d:8e:c6",
    },
    "Ubiquiti UniFi UAP": {
        "host": "192.168.30.246",
        "filename": "scan_lab.json",
        "hostname": "DOWNSTAIRSOFFICE",
        "type": "WAP",
        "mac": "F4:E2:C6:A8:CA:34",
    },
    "Ruckus Access Point": {
        "host": "192.168.40.136",
        "filename": "scan_lab.json",
        "hostname": "SN-291802001160",
        "type": "WAP",
        "mac": "EC:58:EA:28:D7:90",
    },
}
# Markers for IOT devices
IOT_DEVICES = {
    "FLIR Linux": {
        "host": "192.168.40.26",
        "filename": "scan_lab.json",
        "hostname": "ND0115050063214",
        "type": "IOT",
        "mac": "00:40:7F:77:63:48",
    },
}

NESSUS_DEVICE_MAP = {
    "SERVER": {"ip": "192.168.86.22", "mac": "60:B7:6E:6C:C6:48"},
    "ROUTER": {"ip": "192.168.86.1", "mac": "60:B7:6E:6C:C6:1C"},
    "WAP": {"ip": "192.168.86.1", "mac": "60:B7:6E:6C:C6:1C"},
    "LAPTOP": {"ip": "192.168.86.22", "mac": "60:B7:6E:6C:C6:48"},
    "MOBILE": {
        "ip": "192.168.86.36",
        "mac": "4C:FC:AA:0A:FC:E3",
        "hostname": "tesla_model_s",
    },
}


def semi_rand_mac(mac: str):
    start = ":".join(mac.split(":")[:3])
    end = ":".join("%02x" % random.randrange(256) for _ in range(3))
    return start + ":" + end


def semi_random_ipv4(old_ip: str, new_ip: str):
    start = old_ip.split(".")[:2]
    end = new_ip.split(".")[2:]
    return ".".join(start + end)


def random_ipv6():
    M = 16**4
    return "fde9:727a:" + ":".join(("%x" % random.randint(0, M) for i in range(6)))


def check_for_replacements(key: str, asset_replacements: dict):
    match = None
    if key in asset_replacements:
        match = re.compile(asset_replacements[key], re.IGNORECASE)
    return match


def current_rz_time():
    return round(time.time() * 1000000000)


def fudge_integration_data(
    asset_cache: list, infile: str, outfile: str, device_map: dict = NESSUS_DEVICE_MAP
):
    output = []

    for asset in asset_cache:
        # data to use
        raw_task = open(f"./tasks/{infile}")

        # get device type and check if integration supports
        device_type = asset.get("type", None)
        if device_type:

            # check that the integration supports the type
            if device_type in device_map:
                # check if the integration has values to replace
                ip_match = check_for_replacements(
                    key="ip", asset_replacements=device_map[device_type]
                )
                mac_match = check_for_replacements(
                    key="mac", asset_replacements=device_map[device_type]
                )
                hostname_match = check_for_replacements(
                    key="hostname", asset_replacements=device_map[device_type]
                )

                for line in raw_task:

                    # check if the log is worth working on
                    temp_result = json.loads(line)
                    if temp_result.get("type") == "result" and temp_result.get(
                        "info", {}
                    ).get("id", None) == device_map[device_type].get("ip"):
                        # update timestamp
                        temp_result["ts"] = current_rz_time()

                        # decode for fudging
                        temp_result["info"]["_vulnerabilities"] = base64.b64decode(
                            temp_result["info"]["_vulnerabilities"]
                        ).decode("utf-8")

                        # make modifications
                        result = (
                            ip_match.sub(asset.get("ip"), json.dumps(temp_result))
                            if ip_match and "ip" in asset
                            else json.dumps(temp_result)
                        )
                        result = (
                            mac_match.sub(asset.get("new_mac"), result)
                            if mac_match and "new_mac" in asset
                            else result
                        )
                        result = (
                            hostname_match.sub(asset.get("new_hostname"), result)
                            if hostname_match and "new_hostname" in asset
                            else result
                        )

                        # reencode for upload
                        final_result = json.loads(result)
                        final_result["info"]["_vulnerabilities"] = base64.b64encode(
                            final_result["info"]["_vulnerabilities"].encode()
                        ).decode()
                        output.append(final_result)

    # write modified results to file for import
    with open(outfile, "w") as f:
        for l in output:
            f.write(json.dumps(l, separators=(",", ":")) + "\n")


def fudge_scan_data(asset_info: dict, ip: str):
    # pick random asset type
    random_asset_type = random.choice(list(asset_info.keys()))

    # fix hostnames
    host_match = check_for_replacements("hostname", asset_info[random_asset_type])
    asset_type = asset_info[random_asset_type].get("type", "SERVER")
    ip_hostname_sub = "".join(ip.split(".")[-2:])

    # check for less common attributes to update + create regex and new random value if they exist
    domain_match = check_for_replacements("domain", asset_info[random_asset_type])

    # check for secondary IP v4 and v6 + randomizers
    secondary_v4_match = check_for_replacements(
        "secondary_v4", asset_info[random_asset_type]
    )
    new_secondary_v4 = (
        semi_random_ipv4(
            old_ip=asset_info[random_asset_type]["secondary_v4"], new_ip=ip
        )
        if secondary_v4_match
        else None
    )

    secondary_v6_match = check_for_replacements(
        "secondary_v6", asset_info[random_asset_type]
    )
    new_secondary_v6 = random_ipv6() if secondary_v6_match else None

    ## check for MAC addresses + randomizer
    mac_match = check_for_replacements("mac", asset_info[random_asset_type])
    mac = asset_info[random_asset_type]["mac"] if mac_match else None
    new_mac = semi_rand_mac(mac=mac) if mac_match else None

    # data to use
    filename = asset_info[random_asset_type]["filename"]
    raw_task = open(f"./tasks/{filename}")

    for line in raw_task:
        # check if the log is worth working on
        temp_result = json.loads(line)
        if temp_result.get("host") == asset_info[random_asset_type]["host"]:

            # update host and ts attibutes
            temp_result["ts"] = current_rz_time()
            temp_result["host"] = ip
            primary_ip_match = re.compile(
                asset_info[random_asset_type]["host"], re.IGNORECASE
            )

            if (
                asset_info[random_asset_type]["type"] in ["ROUTER", "WAP"]
                and "snmp.interfaceMacs" in temp_result
            ):
                temp_result["snmp.interfaceMacs"] = "\t".join(
                    (semi_rand_mac(mac=mac) for i in range(10))
                )

            # update hostname + primary IP
            new_hostname = f"RZHQ-{asset_type}-{ip_hostname_sub}"
            result = (
                host_match.sub(
                    new_hostname, json.dumps(temp_result)
                )
                if host_match
                else json.dumps(temp_result)
            )
            result = primary_ip_match.sub(ip, result)

            # update other attributes as needed
            result = domain_match.sub("RUNZERO", result) if domain_match else result
            result = mac_match.sub(new_mac, result) if mac_match else result
            result = (
                secondary_v4_match.sub(new_secondary_v4, result)
                if secondary_v4_match
                else result
            )
            result = (
                secondary_v6_match.sub(new_secondary_v6, result)
                if secondary_v6_match
                else result
            )

            OUTPUT.append(json.loads(result))

    new_asset_info = {
        "ip": ip,
        "new_hostname": new_hostname,
        "new_mac": new_mac,
        "new_secondary_v4": new_secondary_v4,
        "new_secondary_v6": new_secondary_v6,
    }
    return asset_info[random_asset_type] | new_asset_info


def main():
    create_new = True
    if create_new:
        asset_cache = []

        # create scan data for standard assets
        for subnet in range(0, 5):
            for ip in range(1, 10):
                asset = (
                    fudge_scan_data(asset_info=COMPUTE_ASSETS, ip=f"10.0.{subnet}.{ip}")
                    if ip > 1
                    else fudge_scan_data(
                        asset_info=ROUTING_ASSETS, ip=f"10.0.{subnet}.{ip}"
                    )
                )
                if asset:
                    asset_cache.append(asset)

        # clears the output file
        open("scan_output.json", "w").close()

        with open("scan_output.json", "a") as scan_output:
            for l in OUTPUT:
                scan_output.write(json.dumps(l) + "\n")
            scan_output.close()

        # create nessus task
        fudge_integration_data(
            asset_cache=asset_cache,
            infile="integration_nessus.json",
            outfile="integration_nessus.json",
        )

    # delete existing assets first (if you want to)
    delete = True
    if delete:
        export_url = RUNZERO_BASE_URL + "/export/org/assets.json"
        headers = {"Authorization": f"Bearer {RUNZERO_ORG_TOKEN}"}
        params = {"search": f"site:{RUNZERO_SITE_ID}", "fields": "id"}
        resp = requests.get(url=export_url, headers=headers, params=params)
        asset_list = [x["id"] for x in resp.json()]
        if len(asset_list) > 0:
            delete_url = RUNZERO_BASE_URL + "/org/assets/bulk/delete"
            delete = requests.delete(url=delete_url, headers=headers, json={"asset_ids": asset_list}, params={"_oid": RUNZERO_ORG_ID})
            if delete.status_code == 204:
                print("204 - deleted all assets")


    # updload task(s) to rz (if you want to)
    upload = True
    if upload:
        for filename in ["scan_output.json", "integration_nessus.json"]:
            gzip_upload = gzip.compress(open(filename, "rb").read())
            upload_url = RUNZERO_BASE_URL + f"/org/sites/{RUNZERO_SITE_ID}/import"
            params = {"_oid": RUNZERO_ORG_ID}
            headers = {"Authorization": f"Bearer {RUNZERO_ORG_TOKEN}"}
            resp = requests.put(
                url=upload_url, headers=headers, params=params, data=gzip_upload
            )
            if resp.status_code == 200:
                print("200 - uploaded", filename)


if __name__ == "__main__":
    main()
