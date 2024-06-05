import os
import requests
import json
import time
import random
import re
import gzip
import base64
import uuid
import argparse


#### NETWORK OVERVIEW ####

# Corporate: 10.0.0.0 - 10.0.10.255

## Standard end user assets - Linux, Apple, and Windows devices
### RZ Scan, CrowdStrike, Nessus, and AzureAD

## Routers
### RZ Scan and Nessus

## WAP
### RZ Scan and Nessus

# Datacenter: 10.0.11.0 - 10.0.20.255 = datacenter

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

# Command line args
parser = argparse.ArgumentParser(
    prog="Demo Data Creator",
    description="Creates and uploads demo data to runZero",
)
parser.add_argument("--create", action="store_true", help="create new demo data")
parser.add_argument("--delete", action="store_true", help="delete existing assets in the console")
parser.add_argument("--upload", action="store_true", help="upload demo data to runZero")
args = parser.parse_args()


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
    "Microsoft-Windows Server 2019": {
        "host": "192.168.0.244",
        "filename": "scan_lab.json",
        "hostname": "AUSTIN-TEST-LAB",
        "type": "SERVER",
        "os": "Windows",
        "secondary_v4": "192.168.0.244",
        "mac": "00:02:A5:61:54:57",
    },
    "Microsoft-Windows 11": {
        "host": "192.168.40.232",
        "filename": "scan_lab.json",
        "hostname": "WINDOWS11PRO",
        "type": "LAPTOP",
        "os": "Windows",
        "secondary_v4": "192.168.40.232",
        "secondary_v6": "fe80::5ab3:e54c:2653:12be",
        "mac": "BC:24:11:32:3E:3B",
    },
    "Microsoft-Windows Server 2016": {
        "host": "192.168.40.249",
        "filename": "scan_lab.json",
        "hostname": "RZ2K16SERVER",
        "domain": "RZ2K16",
        "type": "SERVER",
        "os": "Windows",
        "secondary_v4": "192.168.40.249",
        "mac": "BC:24:11:A1:D8:AF",
    },
    "Microsoft-Windows Server": {
        "host": "192.168.40.233",
        "filename": "scan_lab.json",
        "hostname": "WIN-LB4096E0RUP",
        "type": "SERVER",
        "os": "Windows",
        "secondary_v4": "192.168.40.233",
        "mac": "BC:24:11:19:D4:0F",
    },
    "Linux-Ubuntu-22.04.2": {
        "host": "192.168.50.20",
        "filename": "scan_lab.json",
        "hostname": "RUNZERO",
        "type": "SERVER",
        "os": "Linux",
        "mac": "94:C6:91:15:4D:91|08:6e:20:4a:e6:56",
    },
    "Linux-Raspbian-9.0": {
        "host": "192.168.0.8",
        "filename": "scan_lab.json",
        "hostname": "RPI3-ACCESS-CONTROL|PIT.HDM.IO",
        "type": "SERVER",
        "os": "Linux",
        "mac": "B8:27:EB:E6:4D:41",
    },
    "Linux": {
        "host": "192.168.40.26",
        "filename": "scan_lab.json",
        "type": "SERVER",
        "os": "Linux",
        "mac": "08:EA:44:37:F3:40",
    },
    "Linux-CentOS": {
        "host": "84.244.95.179",
        "filename": "scan_hikivision.json",
        "type": "SERVER",
        "os": "Linux",
        "hostname": "IMAP.GUMOTEXAUTOMOTIVE.CZ|84-244-95-179.STATIC.BLUETONE.CZ|KOALA.TANEXPLASTY.CZ|SMTP.GUMOTEXAUTOMOTIVE.CZ",
    },
    "Linux-CentOS-4": {
        "host": "93.51.158.1039",
        "filename": "scan_hikivision.json",
        "type": "SERVER",
        "os": "Linux",
        "hostname": "93-51-158-103.IP267.FASTWEBNET.IT",
    },
    "Linux-Ubuntu-16.04": {
        "host": "88.87.239.194",
        "filename": "scan_hikivision.json",
        "type": "SERVER",
        "os": "Linux",
        "hostname": "CPE-88-87-239-194.FALU-TV.HU",
    },
    "Apple-iOS": {
        "host": "192.168.30.204",
        "filename": "scan_lab.json",
        "type": "MOBILE",
        "os": "Apple",
        "mac": "fa:be:5a:54:fd:11",
    },
    "Apple-macOS-14.0": {
        "host": "192.168.0.53",
        "filename": "scan_lab.json",
        "hostname": "SLAB",
        "type": "LAPTOP",
        "os": "Apple",
        "secondary_v4": "192.168.30.56",
        "secondary_v6": "fe80::5ab3:e54c:2653:12be",
        "mac": "00:30:93:12:3c:33",
    },
    "Apple-tvOS-17.5": {
        "host": "192.168.30.241",
        "filename": "scan_lab.json",
        "hostname": "OPNSENSE.LOCALDOMAIN|Kitchen-A4CF99AB0C1B",
        "type": "SENSOR",
        "os": "Apple",
        "secondary_v4": "192.168.30.56|192.168.30.3",
        "secondary_v6": "fdc5:e46c:5da8:4b48:6:fde2:62f1:8748",
        "mac": "A4:CF:99:AB:0C:1B|5A:D0:3B:15:84:70|A4:CF:99:AF:67:FF|56:3E:3A:BA:BB:76|A4:CF:99:B2:54:03",
        "cn": "7506644C-DF32-4294-B2A5-49B2FFC09772",
    },
}

# Markers for routers and WAP devices
ROUTING_ASSETS = {
    "Adtran NetVanta AOS": {
        "host": "192.168.40.27",
        "filename": "scan_lab.json",
        "hostname": "ADTRAN225",
        "type": "ROUTER",
        "mac": "00:a0:c8:5d:8e:c6|08:ea:44:37:f3:40",
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
    "DrayTek Vigor": {
        "host": "192.168.40.136",
        "filename": "scan_hikivision.json",
        "hostname": "VIGOR",
        "type": "WAP",
        "mac": "EC:58:EA:28:D7:90",
    },
    "Zyxel USG60W": {
        "host": "46.247.170.154",
        "filename": "scan_hikivision.json",
        "hostname": "USG60W_5CE28C704730|46.247.170.154.NOT.UPDATED.OPENIP-CS.NET",
        "type": "FIREWALL",
        "mac": "5CE28C704730",
    },
    "Cisco IOS 15.5(1)T1": {
        "host": "203.115.7.170",
        "filename": "scan_hikivision.json",
        "hostname": "D64896-SLCUSTOM",
        "type": "ROUTER",
        "mac": "E4:AA:5D:43:ED:A0|E4:AA:5D:43:ED:A1|e4:aa:5d:43:ed:a0",
        "secondary_v4": "203.115.31.121",
    },
}
# Markers for IOT devices
IOT_DEVICES = {
    "FLIR Linux": {
        "host": "192.168.40.26",
        "filename": "scan_lab.json",
        "hostname": "ND0115050063214",
        "type": "IOT",
        "mac": "00:40:7F:77:63:48|08:ea:44:37:f3:40",
    },
    "Hikivision Camera": {
        "host": "89.174.39.70",
        "filename": "scan_hikivision.json",
        "hostname": "CHRISMT",
        "type": "CAMERA",
    },
    "Reolink": {
        "host": "45.148.214.167",
        "filename": "scan_hikivision.json",
        "hostname": "UBNT-788A20A2C84C",
        "type": "CAMERA",
        "mac": "78:8A:20:A2:C8:4C",
    },
}

OT_DEVICES = {
    "Siemens CP343-1 2.0.16": {
        "host": "88.2.1.111",
        "filename": "scan_hikivision.json",
        "hostname": "111.RED-88-2-1.STATICIP.RIMA-TDE.NET",
        "type": "MONITORING",
        "mac": "00:0e:8c:a4:61:84",
        "secondary_v4": "192.168.23.101",
    },
}

# Maps for integration data
NESSUS_DEVICE_MAP = {
    "SERVER": {"ip": "192.168.86.22", "mac": "60:b7:6e:6c:c6:48"},
    "ROUTER": {"ip": "192.168.86.1", "mac": "60:B7:6E:6C:C6:1C"},
    "WAP": {"ip": "192.168.86.1", "mac": "60:B7:6E:6C:C6:1C"},
    "LAPTOP": {"ip": "192.168.86.22", "mac": "60:b7:6e:6c:c6:48"},
    "MOBILE": {
        "ip": "192.168.86.36",
        "mac": "4C:FC:AA:0A:FC:E3",
        "hostname": "tesla_model_s",
    },
}

CROWDSTRIKE_DEVICE_MAP = {
    "SERVER-Linux": {
        "ip": "172.31.33.53",
        "mac": "0a-6e-20-4a-e6-56",
        "hostname": "UTILITY-NODE",
        "username": "=man",
    },
    "SERVER-Windows": {
        "ip": "192.168.1.97",
        "mac": "00-0c-29-2b-65-bb",
        "hostname": "WINDOWS-10",
        "username": "=corey",
    },
    "LAPTOP-Windows": {
        "ip": "192.168.1.97",
        "mac": "00-0c-29-2b-65-bb",
        "hostname": "WINDOWS-10",
        "username": "=corey",
    },
    "LAPTOP-Apple": {
        "ip": "192.168.0.5",
        "mac": "f0-18-98-ee-7c-7b",
        "hostname": "Developers-Mac-mini.local",
        "username": "=developer",
    },
}


def semi_rand_mac(mac: str) -> str:
    start = ":".join(mac.split(":")[:3])
    end = ":".join("%02x" % random.randrange(256) for _ in range(3))
    return start + ":" + end


def semi_random_ipv4(old_ip: str, new_ip: str) -> str:
    start = old_ip.split(".")[:2]
    end = new_ip.split(".")[2:]
    return ".".join(start + end)


def random_ipv6() -> str:
    M = 16**4
    return "fde9:727a:" + ":".join(("%x" % random.randint(0, M) for i in range(6)))


def check_for_replacements(key: str, asset_replacements: dict):
    match = None
    if key in asset_replacements:
        match = re.compile(asset_replacements[key], re.IGNORECASE)
    return match


def regex_bulk_sub(match, new_val, result):
    if match and new_val:
        return match.sub(new_val, result)
    else:
        return result


def current_rz_time() -> float:
    return round(time.time() * 1000000000)


def decode(data: str = ""):
    return base64.b64decode(data + "==").decode("utf-8")


def encode(data: str = ""):
    return base64.b64encode(data.encode()).decode()


def fudge_integration_data(asset_cache: list, integration_name: str) -> bool:
    output = []

    for asset in asset_cache:
        # data to use
        raw_task = open(f"./tasks/integration_{integration_name}.json")

        device_map_key = {
            "nessus": NESSUS_DEVICE_MAP,
            "crowdstrike": CROWDSTRIKE_DEVICE_MAP,
        }

        device_map = device_map_key.get(integration_name, None)

        # skip if the integration doesn't exist in the map
        if device_map:
            # get device type and check if integration supports
            device_type = asset.get("type", None)

            # match CrowdStrike assets more granularly
            os = asset.get("os", None)
            if os and integration_name == "crowdstrike":
                device_type = device_type + "-" + os

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
                    username_match = check_for_replacements(
                        key="username", asset_replacements=device_map[device_type]
                    )
                    cn_match = check_for_replacements(
                        key="cn", asset_replacements=device_map[device_type]
                    )

                    for line in raw_task:

                        # check if the log is worth working on
                        temp_result = json.loads(line)
                        if integration_name == "nessus":
                            result_ip = temp_result.get("info", {}).get("id", None)
                        elif integration_name == "crowdstrike":
                            result_ip = temp_result.get("info", {}).get("localIP", None)

                        device_map_ip = device_map[device_type].get("ip")

                        if (
                            temp_result.get("type") == "result"
                            and result_ip == device_map_ip
                        ):

                            # update timestamp
                            temp_result["ts"] = current_rz_time()

                            # integration specific modifications
                            if integration_name == "nessus":
                                temp_result["info"]["_vulnerabilities"] = decode(
                                    temp_result["info"]["_vulnerabilities"]
                                )
                            if integration_name == "crowdstrike":
                                temp_result["info"]["_applications"] = decode(
                                    temp_result["info"]["_applications"]
                                )
                                temp_result["info"]["_vulnerabilities"] = decode(
                                    temp_result["info"]["_vulnerabilities"]
                                )
                                temp_result["info"]["modifiedTS"] = str(
                                    round(time.time())
                                )
                                temp_result["info"]["firstLoginTS"] = str(
                                    round(time.time() - 10000)
                                )
                                temp_result["info"]["lastInteractiveTSS"] = str(
                                    round(time.time() - 10000)
                                )
                                temp_result["info"]["lastInteractiveTS"] = str(
                                    round(time.time() - 10000)
                                )
                                temp_result["info"]["lastLoginTS"] = str(
                                    round(time.time())
                                )
                                # Windows Server 2019 | Windows 11 | Windows Server 2016 | etc
                                os_info = asset.get("os_full", "").split("0")
                                if len(os_info) == 3:
                                    temp_result["info"]["osVersion"] = os_info[2]
                                elif len(os_info) == 2:
                                    temp_result["info"]["osVersion"] = os_info[1]

                                # Windows | Mac | Linux
                                temp_result["info"]["platformName"] = os_info[0]

                                # Workstation | Server
                                temp_result["info"]["productTypeDesc"] = asset.get(
                                    "type", "Workstation"
                                )

                                # Microsoft Corporation | Apple Inc. | VMWare Inc.
                                if os_info[0] == "Microsoft":
                                    temp_result["info"][
                                        "systemManufacturer"
                                    ] = "Microsoft Corporation"
                                    temp_result["info"][
                                        "biosManufacturer"
                                    ] = "Microsoft Corporation"
                                elif os_info[0] == "Apple":
                                    temp_result["info"][
                                        "systemManufacturer"
                                    ] = "Apple Inc."
                                    temp_result["info"][
                                        "biosManufacturer"
                                    ] = "Apple Inc."
                                else:
                                    temp_result["info"]["systemManufacturer"] = "Linux"
                                    temp_result["info"][
                                        "biosManufacturer"
                                    ] = "Apple Inc."

                                # get rid of AWS / VMWare stuff
                                temp_result["info"][
                                    "biosVersion"
                                ] = "RZ-CUSTOM-BIOS-v1.0.0"

                                # Device Type
                                temp_result["info"]["systemProductName"] = asset.get(
                                    "os_full", ""
                                )

                                # replace device_id values
                                temp_result["info"]["deviceID"] = asset.get(
                                    "device_id", str(uuid.uuid4())
                                )
                                temp_result["info"]["cid"] = asset.get(
                                    "device_id", str(uuid.uuid4())
                                )

                            # make regex based modifications
                            result = regex_bulk_sub(
                                match=ip_match,
                                new_val=asset.get("ip", None),
                                result=json.dumps(temp_result),
                            )
                            result = regex_bulk_sub(
                                match=mac_match,
                                new_val=asset.get("new_mac", None),
                                result=result,
                            )
                            result = regex_bulk_sub(
                                match=hostname_match,
                                new_val=asset.get("new_hostname", None),
                                result=result,
                            )
                            result = regex_bulk_sub(
                                match=username_match,
                                new_val=asset.get("username", None),
                                result=result,
                            )

                            # reencode for upload
                            final_result = json.loads(result)
                            if integration_name == "nessus":
                                final_result["info"]["_vulnerabilities"] = encode(
                                    final_result["info"]["_vulnerabilities"]
                                )
                            if integration_name == "crowdstrike":
                                # verified this logic works to add custom apps/vulns
                                apps_appendable = json.loads(
                                    final_result["info"]["_applications"]
                                )
                                apps_appendable.append(
                                    {
                                        "id": "RZ-123",
                                        "name": "Tyler's Custom App",
                                        "vendor": "Tyler Corp",
                                    }
                                )
                                final_result["info"]["_applications"] = json.dumps(
                                    apps_appendable
                                )
                                final_result["info"]["_applications"] = encode(
                                    final_result["info"]["_applications"]
                                )
                                final_result["info"]["_vulnerabilities"] = encode(
                                    final_result["info"]["_vulnerabilities"]
                                )
                            output.append(final_result)
        else:
            return False

    # write modified results to file for import
    with open(f"integration_{integration_name}.json", "w") as f:
        for l in output:
            f.write(json.dumps(l, separators=(",", ":")) + "\n")

    return True


def fudge_scan_data(asset_info: dict, ip: str, network: str) -> dict:
    # pick random asset type
    random_asset_type = random.choice(list(asset_info.keys()))

    # fix hostnames
    host_match = check_for_replacements("hostname", asset_info[random_asset_type])
    asset_type = asset_info[random_asset_type].get("type", "SERVER")
    ip_hostname_sub = "".join(ip.split(".")[-2:])
    new_hostname = f"RZ{network}-{asset_type}-{ip_hostname_sub}"

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
    new_mac = (
        semi_rand_mac(mac=mac) if mac_match else semi_rand_mac(mac="19:3c:1f:78:f2:cf")
    )

    # replace tls.cn with random value
    cn_match = check_for_replacements("cn", asset_info[random_asset_type])
    new_cn = str(uuid.uuid4())

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

            if (
                asset_info[random_asset_type]["type"] in ["ROUTER", "WAP"]
                and "snmp.interfaceMacs" in temp_result
            ):
                temp_result["snmp.interfaceMacs"] = "\t".join(
                    (semi_rand_mac(mac=mac) for i in range(10))
                )

            # update hostname + primary IP
            result = regex_bulk_sub(
                match=host_match, new_val=new_hostname, result=json.dumps(temp_result)
            )
            result = regex_bulk_sub(match=primary_ip_match, new_val=ip, result=result)

            # update other attributes as needed
            result = regex_bulk_sub(
                match=domain_match, new_val="RUNZERO", result=result
            )
            result = regex_bulk_sub(match=mac_match, new_val=new_mac, result=result)
            if "56:3E:3A:BA:BB:76" in result:
                print(mac_match, new_mac)

            result = regex_bulk_sub(
                match=secondary_v4_match, new_val=new_secondary_v4, result=result
            )
            result = regex_bulk_sub(
                match=secondary_v6_match, new_val=new_secondary_v6, result=result
            )
            result = regex_bulk_sub(
                match=cn_match,
                new_val=new_cn,
                result=result,
            )

            OUTPUT.append(json.loads(result))

    new_asset_info = {
        "ip": ip,
        "new_hostname": new_hostname,
        "new_mac": new_mac,
        "new_secondary_v4": new_secondary_v4,
        "new_secondary_v6": new_secondary_v6,
        "new_cn": new_cn,
        "os_full": random_asset_type,
        "username": f"USER-{ip_hostname_sub}",
        "device_id": str(uuid.uuid4()),
    }
    return asset_info[random_asset_type] | new_asset_info


def main():
    if args.create:
        asset_cache = []

        # create scan data for HQ assets
        for subnet in range(0, 5):
            for ip in range(1, 5):
                asset = (
                    fudge_scan_data(
                        asset_info=COMPUTE_ASSETS,
                        ip=f"10.0.{subnet}.{ip}",
                        network="HQ",
                    )
                    if ip > 1
                    else fudge_scan_data(
                        asset_info=ROUTING_ASSETS,
                        ip=f"10.0.{subnet}.{ip}",
                        network="HQ",
                    )
                )
                if asset:
                    asset_cache.append(asset)

        # create scan data for datacenter assets
        for subnet in range(11, 15):
            for ip in range(1, 5):
                asset = (
                    fudge_scan_data(
                        asset_info=COMPUTE_ASSETS | IOT_DEVICES | OT_DEVICES,
                        ip=f"10.0.{subnet}.{ip}",
                        network="DC",
                    )
                    if ip > 1
                    else fudge_scan_data(
                        asset_info=ROUTING_ASSETS,
                        ip=f"10.0.{subnet}.{ip}",
                        network="DC",
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
            print("SUCCESS - created task for rz scan")

        for integration in ["nessus", "crowdstrike"]:
            success = fudge_integration_data(
                asset_cache=asset_cache, integration_name=integration
            )
            if success:
                print(f"SUCCESS - created task for {integration}")
            else:
                print(f"FAILURE - on create task for {integration}")

    # delete existing assets first (if you want to)
    if args.delete:
        # export current assets
        export_url = RUNZERO_BASE_URL + "/export/org/assets.json"
        headers = {"Authorization": f"Bearer {RUNZERO_ORG_TOKEN}"}
        params = {"search": f"site:{RUNZERO_SITE_ID}", "fields": "id"}
        resp = requests.get(url=export_url, headers=headers, params=params)
        asset_list = [x["id"] for x in resp.json()]
        if len(asset_list) > 0:
            delete_url = RUNZERO_BASE_URL + "/org/assets/bulk/delete"
            delete = requests.delete(
                url=delete_url,
                headers=headers,
                json={"asset_ids": asset_list},
                params={"_oid": RUNZERO_ORG_ID},
            )
            if delete.status_code == 204:
                print("SUCCESS - started asset deletion")
                deleted = False
                while not deleted:
                    resp = requests.get(url=export_url, headers=headers, params=params)
                    if len(resp.json()) == 0:
                        deleted = True
                        print("SUCCESS - all assets deleted")
                    else:
                        time.sleep(5)
                        print(
                            "WAITING - still deleting assets. Waiting 5 seconds to check again. Current asset count:",
                            len(asset_list),
                        )

    # updload task(s) to rz (if you want to)
    if args.upload:
        for filename in [
            "scan_output.json",
            "integration_crowdstrike.json",
            "integration_nessus.json",
        ]:
            gzip_upload = gzip.compress(open(filename, "rb").read())
            upload_url = RUNZERO_BASE_URL + f"/org/sites/{RUNZERO_SITE_ID}/import"
            params = {"_oid": RUNZERO_ORG_ID}
            headers = {"Authorization": f"Bearer {RUNZERO_ORG_TOKEN}"}
            resp = requests.put(
                url=upload_url, headers=headers, params=params, data=gzip_upload
            )
            if resp.status_code == 200:
                print("SUCCESS - uploaded", filename)


if __name__ == "__main__":
    main()
