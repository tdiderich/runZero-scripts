import os
import datetime
import requests
import json
import time
import random
import re
import gzip
import base64
import uuid
import argparse
import string
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtensionOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from concurrent.futures import ThreadPoolExecutor, as_completed

# Command line args
parser = argparse.ArgumentParser(
    prog="Demo Data Creator",
    description="Creates and uploads demo data to runZero",
)
parser.add_argument("--create", action="store_true", help="create new demo data")
parser.add_argument(
    "--delete", action="store_true", help="delete existing assets in the console"
)
parser.add_argument("--upload", action="store_true", help="upload demo data to runZero")
parser.add_argument(
    "--verify",
    action="store_true",
    help="run checks on the results to verify they are correct",
)
parser.add_argument(
    "--compress",
    action="store_true",
    help="gzips the JSON after uploading to have a smaller file to share",
)
parser.add_argument(
    "--assets-per-subnet",
    type=int,
    default=5,
    help="how many assets to put in each subnet",
)
parser.add_argument("--env", type=str, help="demo or prod")
args = parser.parse_args()

# Creds for uploading tasks to rz
RUNZERO_BASE_URL = (
    "https://demo.runzero.com/api/v1.0"
    if args.env == "demo"
    else "https://console.runzero.com/api/v1.0"
)
RUNZERO_ORG_ID = (
    os.environ["RUNZERO_DEMO_ORG_ID"]
    if args.env == "demo"
    else os.environ["RUNZERO_ORG_ID"]
)
RUNZERO_SITE_ID = (
    os.environ["RUNZERO_DEMO_SITE_ID"]
    if args.env == "demo"
    else os.environ["RUNZERO_SITE_ID"]
)
RUNZERO_ORG_TOKEN = (
    os.environ["RUNZERO_DEMO_ORG_TOKEN"]
    if args.env == "demo"
    else os.environ["RUNZERO_ORG_TOKEN"]
)
JAMF_CUSTOM_INTEGRATION_ID = (
    os.environ["RUNZERO_DEMO_JAMF_ID"]
    if args.env == "demo"
    else os.environ["RUNZERO_JAMF_ID"]
)

# MAC caches
MAC_CACHE = [
    "00:23:47:61:15:30",
    "00:a0:c8:f5:08:a5",
    "3c:2a:f4:ab:e1:c6",
    "e4:aa:5d:43:ed:a0",
    "00:05:33:c6:b0:d6",
    "e4:aa:5d:86:8f:3c",
    "e4:aa:5d:fc:55:8e",
]

ROUTER_SWITCH_SERVER_MAC_CACHE = []

# Output seeded with scan config line
OUTPUT = []

# Markers for common compute assets
SERVER_ASSETS = {
    "Microsoft-Windows Server 2019": {
        "host": "192.168.0.244",
        "filename": "scan_lab.json",
        "hostname": "AUSTIN-TEST-LAB",
        "type": "SERVER",
        "os": "Windows",
        "secondary_v4": "192.168.0.244",
        "mac": "00:02:A5:61:54:57",
        "ami": "ami-0000615e374d82a9a",
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
        "ami": "ami-0011898114361827d",
    },
    "Microsoft-Windows Server": {
        "host": "192.168.40.233",
        "filename": "scan_lab.json",
        "hostname": "WIN-LB4096E0RUP",
        "type": "SERVER",
        "os": "Windows",
        "secondary_v4": "192.168.40.233",
        "mac": "BC:24:11:19:D4:0F",
        "ami": "ami-0014d63892bdf8f1d",
    },
    "Linux-Ubuntu-22.04.2": {
        "host": "192.168.50.20",
        "filename": "scan_lab.json",
        "hostname": "RUNZERO",
        "type": "SERVER",
        "os": "Linux",
        "mac": "94:C6:91:15:4D:91|08:6e:20:4a:e6:56",
        "ami": "ami-0000456e99b2b6a9d",
    },
    "Linux": {
        "host": "192.168.40.26",
        "filename": "scan_lab.json",
        "type": "SERVER",
        "os": "Linux",
        "mac": "08:EA:44:37:F3:40",
        "ami": "ami-00007188242c9f57d",
    },
    "Linux-CentOS-7": {
        "host": "84.244.95.179",
        "filename": "scan_hikivision.json",
        "type": "SERVER",
        "os": "Linux",
        "hostname": "IMAP.GUMOTEXAUTOMOTIVE.CZ|84-244-95-179.STATIC.BLUETONE.CZ|KOALA.TANEXPLASTY.CZ|SMTP.GUMOTEXAUTOMOTIVE.CZ",
        "ami": "ami-00037c9a571a60758",
    },
    "Linux-CentOS-4": {
        "host": "93.51.158.1039",
        "filename": "scan_hikivision.json",
        "type": "SERVER",
        "os": "Linux",
        "hostname": "93-51-158-103.IP267.FASTWEBNET.IT",
        "ami": "ami-0254431cc221ee3ff",
    },
    "Linux-Ubuntu-16.04": {
        "host": "88.87.239.194",
        "filename": "scan_hikivision.json",
        "type": "SERVER",
        "os": "Linux",
        "hostname": "CPE-88-87-239-194.FALU-TV.HU",
        "ami": "ami-0019254849cdb9eb6",
    },
    "Linux-Ubuntu-8.04": {
        "host": "192.168.40.248",
        "filename": "scan_lab_second.json",
        "type": "SERVER",
        "os": "Linux",
        "hostname": "METASPLOITABLE|UBUNTU804-BASE",
        "mac": "00:0C:29:28:20:93",
        "ami": "ami-000280f76a9893805",
    },
}

# End user assets
END_USER_ASSETS = {
    "Apple-iOS-15.2": {
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
    "Brother MFC-L5900DW": {
        "host": "192.168.30.20",
        "filename": "scan_lab_printer.json",
        "hostname": "BRN3C2AF4ABE1C6",
        "type": "PRINTER",
        "secondary_v4": "192.168.30.3",
        "mac": "3c:2a:f4:ab:e1:c6|10:5b:ad:4a:69:45|10:5b:ad:4a:e9:45|D4:10:5b:ad:5a:22:39|00:0c:29:01:66:14",
        "cn": "e3248000-80ce-11db-8000-3c2af4abe1c6|39bb2b02-b72f-1d75-6fae-bb0ede560240",
    },
}

# Markers for routers and WAP devices
ROUTING_ASSETS = {
    "Adtran NetVanta AOS": {
        "host": "192.168.40.27",
        "filename": "scan_lab.json",
        "hostname": "ADTRAN225",
        "type": "ROUTER",
        "mac": "00:a0:c8:5d:8e:c6|08:ea:44:37:f3:40|e4:aa:5d:91:3c:17",
    },
    "Ubiquiti UniFi UAP": {
        "host": "192.168.30.246",
        "filename": "scan_lab.json",
        "hostname": "DOWNSTAIRSOFFICE",
        "type": "WAP",
        "mac": "F4:E2:C6:A8:CA:34",
    },
    "Ruckus": {
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
    "Cisco IOS-15.5(1)T1": {
        "host": "10.0.19.1",
        "filename": "scan_hikivision.json",
        "hostname": "D64896-SLCUSTOM",
        "type": "ROUTER",
        "mac": "E4:AA:5D:43:ED:A0|E4:AA:5D:43:ED:A1|e4:aa:5d:43:ed:a0",
        "secondary_v4": "203.115.31.121",
    },
    "TP LINK-Wireless Lite N 3G/4G Router MR3220": {
        "host": "194.116.41.76",
        "filename": "scan_tplink.json",
        "hostname": "194-116-41-76-STATIC.BBBELL.COM",
        "type": "WAP",
    },
}

# Markers for firewalls
FIREWALL_DEVICES = {
    "Zyxel USG60W": {
        "host": "46.247.170.154",
        "filename": "scan_hikivision.json",
        "hostname": "USG60W_5CE28C704730|46.247.170.154.NOT.UPDATED.OPENIP-CS.NET",
        "type": "FIREWALL",
        "mac": "5C:E2:8C:70:47:30|5CE28C704730",
    },
    "Fortinet FortiOS": {
        "host": "62.48.202.126",
        "filename": "scan_ups.json",
        "hostname": "FGT60ETK19086062",
        "type": "FIREWALL",
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
        "secondary_v4": "23.21.0.0",
        "filename": "scan_hikivision.json",
        "hostname": "CHRISMT",
        "type": "CAMERA",
    },
    "Reolink": {
        "host": "45.148.214.167",
        "filename": "scan_hikivision.json",
        "hostname": "UBNT-788A20A2C84C|REO-LINK",
        "type": "CAMERA",
        "mac": "78:8A:20:A2:C8:4C",
        "cn": "UBNT-78:8A:20:fa:ed:b7|UBNT-78:8A:20:fc:ff:ad|ubnt-78:8A:20:71:f2:83",
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
    "Linux-Raspbian-9.0": {
        "host": "192.168.0.8",
        "filename": "scan_lab.json",
        "hostname": "RPI3-ACCESS-CONTROL|PIT.HDM.IO",
        "type": "SERVER",
        "os": "Linux",
        "mac": "B8:27:EB:E6:4D:41",
    },
    "Linux-Raspbian-9.0-Exposure": {
        "host": "192.168.0.8",
        "filename": "scan_exposure.json",
        "hostname": "RPI3-ACCESS-CONTROL|PIT.HDM.IO",
        "type": "SERVER",
        "os": "Linux",
        "mac": "B8:27:EB:E6:4D:41",
    },
    "Microsoft Windows-CE": {
        "host": "80.13.242.26",
        "filename": "scan_ups.json",
        "hostname": "LSTLAMBERT-658-1-223-26.W80-13.ABO.WANADOO.FR",
        "type": "CAMERA",
    },
}

# Markets for OT devices
OT_DEVICES = {
    "Siemens CP343-1 2.0.16": {
        "host": "88.2.1.111",
        "filename": "scan_hikivision.json",
        "hostname": "111.RED-88-2-1.STATICIP.RIMA-TDE.NET",
        "type": "MONITORING",
        "mac": "00:0e:8c:a4:61:84",
        "secondary_v4": "192.168.23.101",
    },
    "Westermo MRD-310": {
        "host": "49.229.153.248",
        "filename": "scan_ups.json",
        "hostname": "WESTERMO-MRD-310",
        "type": "PLC",
        "mac": "00:07:7C:E0:48:E0|00:07:7c:e0:4a:4d|00:20:dd:00:00:01",
        "secondary_v4": "192.168.2.200|192.168.127.100",
    },
    "Wind River VxWorks 6.4": {
        "host": "61.220.231.43",
        "filename": "scan_ups.json",
        "hostname": "61-220-231-43.HINET-IP.HINET.NET",
        "type": "PLC",
        "mac": "00:80:f4:22:8e:f5",
    },
    "Siemens STEP 7-Micro": {
        "host": "10.10.101.5",
        "filename": "scan_plc_windows_linux.json",
        "type": "PLC",
    },
    "Phoenix Contact AXC 1050": {
        "host": "10.10.102.5",
        "filename": "scan_plc_windows_linux.json",
        "hostname": "AXC-1050",
        "type": "PLC",
        "mac": "00:A0:45:A7:8F:14",
    },
    "Shelly Plug": {
        "host": "10.10.104.20",
        "filename": "scan_plc_windows_linux.json",
        "hostname": "SHELLYPRO3-C8F09E8847CC",
        "type": "UPS",
        "mac": "C8:F0:9E:88:47:CC",
    },
    "Cisco IOS 12.2(55)SE11": {
        "host": "192.168.40.24",
        "hostname": "SWITCH3560",
        "filename": "scan_lab_second.json",
        "type": "SWITCH",
        "mac": "dc:7b:94:d7:64:81",
    },
    "Cisco IOS": {
        "host": "192.168.40.231",
        "hostname": "SWITCH.LOCALDOMAIN",
        "filename": "scan_lab_second.json",
        "type": "SWITCH",
        "mac": "E8:04:62:75:89:C0|e4:aa:5d:eb:61:58",
    },
    "HP ProCurve J4905A M.10.104": {
        "host": "192.168.40.13",
        "hostname": "PROCURVE-SWITCH-3400CL-24G",
        "filename": "scan_lab_second.json",
        "type": "SWITCH",
        "mac": "00:23:47:7a:0b:20",
    },
    "Brocade Switch": {
        "host": "192.168.40.29",
        "hostname": "BROCSW2",
        "filename": "scan_lab_second.json",
        "type": "SWITCH",
        "mac": "00:05:33:47:28:52",
    },
    "Raritan Xerus 030002": {
        "host": "192.168.40.73",
        "filename": "scan_lab_printer.json",
        "hostname": "RARITAN",
        "type": "PDU",
        "mac": "00:0d:5d:0c:74:32",
    },
    "DNP3 Outstation Device": {
        "host": "192.168.86.222",
        "hostname": "DNP3 Outstation Device",
        "filename": "scan_ot.json",
        "type": "OT",
    },
    "Step Function I/O": {
        "host": "192.168.86.3",
        "filename": "scan_ot.json",
        "type": "OT",
    },
    "Rockwell Automation 1769-L18ERM": {
        "host": "10.10.103.5",
        "filename": "scan_ethernet_ip.json",
        "type": "OT",
    },
}

# Markers for BACNet devices
BACNET_ASSETS = {
    "Liebert Challenger": {
        "host": "24.42.195.92",
        "hostname": "STATIC-24-42-195-92.KNOLOGY.NET",
        "filename": "scan_public_ot.json",
        "type": "HVAC",
    },
    "eBMGR": {
        "host": "68.227.78.195",
        "hostname": "NIAGARA4|C6CD0C14563E.SN.MYNETNAME.NET",
        "filename": "scan_public_ot.json",
        "type": "HVAC",
    },
    "EX36 V3.5.2": {
        "host": "75.83.97.77",
        "hostname": "CPE-75-83-97-77.SOCAL.RES.RR.COM",
        "filename": "scan_public_ot.json",
        "type": "HVAC",
    },
    "Liebert DS": {
        "host": "99.88.79.23",
        "hostname": "ADSL-99-88-79-23.DSL.FRS2CA.SBCGLOBAL.NET",
        "filename": "scan_public_ot.json",
        "type": "HVAC",
    },
}

# Findings additions

FINDINGS_ASSETS = {
    "AOGHHH.DBRAIN.MTS": {
        "filename": "findings_consolidated.json",
        "host": "198.51.100.3",
        "hostname": "AOGHHH.DBRAIN.MTS",
        "type": "OT",
    },
    "Linux-CentOS": {
        "filename": "findings_consolidated.json",
        "host": "10.0.18.9",
        "hostname": "RZDC-SERVER-189",
        "mac": "19:3c:1f:ae:03:02",
        "os": "CentOS",
        "type": "SERVER",
    },
    "Cisco IOS-15.5(1)T1": {
        "filename": "findings_consolidated.json",
        "host": "10.0.19.1",
        "hostname": "RZDC-ROUTER-191",
        "mac": "19:3c:1f:a8:5a:41",
        "os": "Cisco IOS",
        "secondary_v4": "203.115.19.1",
        "type": "ROUTER",
    },
    "Cisco SLM224GT-NA": {
        "filename": "findings_consolidated.json",
        "host": "10.0.19.1",
        "hostname": "RZDC-ROUTER-SMALL",
        "mac": "e4:aa:5d:2b:bc:6e",
        "os": "Cisco SLM224GT-NA",
        "secondary_v4": "10.0.19.101",
        "type": "SWITCH",
    },
    "Linux-Debian-9": {
        "filename": "findings_consolidated.json",
        "host": "198.51.100.5",
        "hostname": "0NQGN5N",
        "mac": "unknown",
        "os": "Debian Linux",
        "type": "SERVER",
    },
    "Microsoft-Windows 10": {
        "filename": "findings_consolidated.json",
        "host": "10.0.19.36",
        "hostname": "RZDC-SERVER-1936",
        "mac": "00:02:a5:c9:2f:a4",
        "os": "Microsoft Windows 10 (22H2 " "Build 19045)",
        "type": "SERVER",
    },
    "Microsoft-Windows CE": {
        "filename": "findings_consolidated.json",
        "host": "10.0.16.49",
        "hostname": "RZDC-CAMERA-1649",
        "mac": "19:3c:1f:6a:fd:2d",
        "os": "Microsoft Windows CE",
        "type": "IP Camera",
    },
    "Microsoft-Windows Server 2019": {
        "filename": "findings_consolidated.json",
        "host": "23.20.4.34",
        "hostname": "RZCLOUD-SERVER-434",
        "mac": "00:02:a5:36:1b:0f",
        "os": "Microsoft Windows Server 2019",
        "secondary_v4": "172.31.4.34",
        "type": "SERVER",
    },
    "Palo Alto Networks PAN-OS": {
        "filename": "findings_consolidated.json",
        "host": "198.51.100.17",
        "hostname": "P.5-4-OFG7G-GZ1N8-2F.LVT5Z5.0Z6",
        "os": "Palo Alto Networks PAN-OS",
        "type": "VPN",
    },
    "Step Function I/O Example Outstation-1.0.0": {
        "filename": "findings_consolidated.json",
        "host": "10.0.20.8",
        "mac": "19:3c:1f:86:42:ec",
        "os": "Step Function I/O " "Example Outstation",
        "secondary_v4": "197.51.100.222",
        "type": "Industrial Control",
    },
    "Linux-Ubiquiti": {
        "filename": "findings_consolidated.json",
        "host": "10.0.11.21",
        "hostname": "UBNT-788A201D5D97",
        "mac": "78:8a:20:1d:5d:97",
        "os": "Ubiquiti Linux",
        "type": "IP Camera",
    },
    "Linux-Ubuntu": {
        "filename": "findings_consolidated.json",
        "host": "10.0.8.11",
        "hostname": "RZHQ-SERVER-811",
        "mac": "00:0c:29:0e:07:6b",
        "os": "Ubuntu Linux",
        "type": "SERVER",
    },
    "Linux-Ubuntu-14.04": {
        "filename": "findings_consolidated.json",
        "host": "23.20.1.49",
        "hostname": "RZCLOUD-SERVER-149",
        "mac": "00:0c:29:88:46:dd",
        "os": "Ubuntu Linux",
        "secondary_v4": "172.31.1.49",
        "type": "SERVER",
    },
    "Linux-Ubuntu-16.04": {
        "filename": "findings_consolidated.json",
        "host": "10.0.3.13",
        "hostname": "RZHQ-SERVER-313",
        "mac": "19:3c:1f:54:3e:fa",
        "os": "Ubuntu Linux",
        "type": "SERVER",
    },
    "Linux-Ubuntu-16.04_2": {
        "filename": "findings_consolidated.json",
        "host": "10.0.9.41",
        "hostname": "RZHQ-SERVER-941",
        "mac": "19:3c:1f:ab:d2:fe",
        "os": "Ubuntu Linux",
        "type": "SERVER",
    },
    "Linux-Ubuntu": {
        "filename": "findings_consolidated.json",
        "host": "10.0.3.43",
        "hostname": "RZHQ-SERVER-343",
        "mac": "00:0c:29:60:fb:2f",
        "os": "Ubuntu Linux",
        "type": "SERVER",
    },
    "Westermo MRD-310": {
        "filename": "findings_consolidated.json",
        "host": "10.0.8.28",
        "hostname": "RZHQ-PLC-828",
        "mac": "00:07:7c:b0:c6:13",
        "os": "Westermo MRD-310",
        "secondary_v4": "192.168.8.28",
        "type": "PLC",
    },
}


# Maps for integration data
NESSUS_DEVICE_MAP = {
    "SERVER": {"ip": "192.168.86.22", "mac": "60:b7:6e:6c:c6:48"},
    "ROUTER": {"ip": "192.168.86.1", "mac": "60:B7:6E:6C:C6:1C"},
    "WAP": {"ip": "192.168.86.1", "mac": "60:B7:6E:6C:C6:1C"},
    "FIREWALL": {"ip": "192.168.86.1", "mac": "60:B7:6E:6C:C6:1C"},
    "LAPTOP": {"ip": "192.168.86.22", "mac": "60:b7:6e:6c:c6:48"},
    "MOBILE": {
        "ip": "192.168.86.36",
        "mac": "4C:FC:AA:0A:FC:E3",
        "hostname": "tesla_model_s",
    },
    "PRINTER": {"ip": "192.168.86.42", "mac": "A6:51:78:A5:F5|3c:2a:f4:ab:e1:c6"},
    "SWITCH": {"ip": "192.168.86.38", "mac": "D8:6C:63:5C:48:14"},
    "CAMERA": {"ip": "192.168.86.42", "mac": "A6:51:78:A5:F5"},
    "SENSOR": {"ip": "192.168.86.42", "mac": "A6:51:78:A5:F5"},
}

QUALYS_DEVICE_MAP = {
    "SERVER-Windows": {
        "ip": "192.168.40.139",
        "mac": "00:0c:29:3d:57:13",
        "hostname": "win11preview",
    },
    "LAPTOP-Windows": {
        "ip": "192.168.1.6",
        "mac": "zz:zz:zz:zz:zz:zz",
        "hostname": "RUNZERO",
    },
    "LAPTOP-Apple": {
        "ip": "192.168.0.6",
        "mac": "4C:20:B8:AB:B6:A3",
        "hostname": "MAC-MINI-M1",
    },
    "SERVER-Linux": {
        "ip": "192.168.50.9",
        "mac": "zz:zz:zz:zz:zz:zz",
        "hostname": "nanananananana",
    },
    "ROUTER": {
        "ip": "192.168.40.28",
        "mac": "00:1B:D5:D8:72:BE",
        "hostname": "cisco18",
    },
    "PRINTER": {
        "ip": "192.168.30.20",
        "mac": "10:5b:ad:4a:69:45|10:5b:ad:4a:e9:45|3c:2a:f4:ab:e1:c6",
        "hostname": "BRN3C2AF4ABE1C6",
    },
    "PDU": {"ip": "192.168.40.73", "mac": "00:0d:5d:0c:74:32", "hostname": "RARITAN"},
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

AWS_DEVICE_MAP = {
    "SERVER-CLOUD": {
        "ip": "3.16.13.20",
        "hostname": "UTILITY-SYSLOG|EC2-3-16-13-20.US-EAST-2|IP-172-31-16-221.US-EAST-2|EC2-10.0.0.3.US-EAST-2",
        "os": "Linux",
        "secondary_v4": "172.31.16.221",
        "secondary_v6": "2600:1f16:a57:b303:121a:a53d:4232:8e5d",
        "mac": "A4:CF:99:AB:0C:1B|5A:D0:3B:15:84:70|A4:CF:99:AF:67:FF|56:3E:3A:BA:BB:76|A4:CF:99:B2:54:03|06:ac:85:2f:1c:e5",
    },
}

AWS_DEVICE_MAP = {
    "SERVER-CLOUD": {
        "ip": "3.16.13.20",
        "hostname": "UTILITY-SYSLOG|EC2-3-16-13-20.US-EAST-2|IP-172-31-16-221.US-EAST-2|EC2-10.0.0.3.US-EAST-2",
        "os": "Linux",
        "secondary_v4": "172.31.16.221",
        "secondary_v6": "2600:1f16:a57:b303:121a:a53d:4232:8e5d",
        "mac": "A4:CF:99:AB:0C:1B|5A:D0:3B:15:84:70|A4:CF:99:AF:67:FF|56:3E:3A:BA:BB:76|A4:CF:99:B2:54:03|06:ac:85:2f:1c:e5",
    },
}

AWS_DEVICE_TYPES = [
    "t2.micro",
    "t2.small",
    "t2.medium",
    "t2.large",
    "t2.xlarge",
    "m5.large",
    "m5.xlarge",
]


def semi_random_mac(mac: str) -> str:
    # add MACs for the asset profiles to ensure we don't re-use them
    macs = mac.split("|")
    for m in macs:
        MAC_CACHE.append(m)
    dup = True
    while dup:
        start = ":".join(mac.split(":")[:3])
        end = ":".join("%02x" % random.randrange(256) for _ in range(3))
        new_mac = start + ":" + end
        if new_mac not in MAC_CACHE:
            MAC_CACHE.append(new_mac)
            return new_mac


def semi_random_ipv4(old_ip: str, new_ip: str) -> str:
    single_ip = old_ip.split("|")[0]
    start = single_ip.split(".")[:2]
    end = new_ip.split(".")[2:]
    return ".".join(start + end)


def random_ipv6() -> str:
    M = 16**4
    return "fde9:727a:" + ":".join(("%x" % random.randint(0, M) for i in range(6)))


def random_serial_number():
    letters_part1 = "".join(random.choices(string.ascii_uppercase, k=3))
    digits_part1 = "".join(random.choices(string.digits, k=4))
    letter_part2 = random.choice(string.ascii_uppercase)
    digits_part2 = "".join(random.choices(string.digits, k=2))
    serial_number = f"{letters_part1}{digits_part1}{letter_part2}{digits_part2}"
    return serial_number


def check_for_replacements(key: str, asset_replacements: dict):
    match = None
    if key in asset_replacements:
        safe_key = asset_replacements[key].replace(".", "[.]")
        match = re.compile(safe_key, re.IGNORECASE)
    return match


def regex_bulk_sub(match, new_val, result):
    if match and new_val:
        new_result = re.subn(match, new_val, result)
        return new_result[0]
    else:
        return result


def current_rz_time() -> float:
    return round(time.time() * 1000000000)


def decode(data: str = ""):
    return base64.b64decode(data + "==").decode("utf-8")


def encode(data: str = ""):
    return base64.b64encode(data.encode()).decode()


def remove_random_assets(asset_cache: list) -> list:
    # remove 5% of assets
    for _ in range(round(len(asset_cache) / 20)):
        asset_cache.pop(random.randint(0, len(asset_cache) - 1))

    return asset_cache


def is_internal(ip):
    """Return True if the IP is in a common private range."""
    if ip.startswith("10."):
        return True
    if ip.startswith("192.168."):
        return True
    if ip.startswith("172."):
        try:
            second_octet = int(ip.split(".")[1])
            if 16 <= second_octet <= 31:
                return True
        except Exception:
            pass
    return False


def generate_random_public_ip():
    """Generate a random public IP address that does not fall in a private range."""
    while True:
        a = random.randint(1, 223)  # avoid multicast and reserved ranges
        b = random.randint(0, 255)
        c = random.randint(0, 255)
        d = random.randint(1, 254)
        ip = f"{a}.{b}.{c}.{d}"
        if not is_internal(ip):
            return ip


def generate_traceroute_str(asset_ip):
    """
    Generate a traceroute string in the format "ip/ip/ip/ip".

    For internal assets:
      traceroute = source_ip/first_router/asset_network_router/asset_ip
        - source_ip: "10.0.0.118"
        - first_router: "10.0.0.1"
        - asset_network_router: derived from asset_ip's first three octets + ".1"

    For public assets:
      traceroute = source_ip/random_ip1/random_ip2/asset_ip
        - source_ip: "128.199.192.118"
        - random_ip1 and random_ip2: two unique randomly generated public IPs.
    """
    if is_internal(asset_ip):
        source_ip = "10.0.0.118"
        first_router = "10.0.0.1"
        asset_parts = asset_ip.split(".")
        asset_network_router = f"{asset_parts[0]}.{asset_parts[1]}.{asset_parts[2]}.1"
        # Ensure we don't duplicate if asset_ip is the network router (unlikely for a host)
        if asset_ip == asset_network_router:
            return f"{source_ip}/{first_router}/{asset_ip}"
        return f"{source_ip}/{first_router}/{asset_network_router}/{asset_ip}"
    else:
        source_ip = "128.199.192.118"
        random_ip1 = generate_random_public_ip()
        random_ip2 = generate_random_public_ip()
        # Ensure the two random IPs are unique and not equal to the source or asset.
        while (
            random_ip2 == random_ip1
            or random_ip1 in [source_ip, asset_ip]
            or random_ip2 in [source_ip, asset_ip]
        ):
            random_ip2 = generate_random_public_ip()
        return f"{source_ip}/{random_ip1}/{random_ip2}/{asset_ip}"


def generate_self_signed_cert(hostname: str, valid_days: int = 365):
    """
    Generates a self-signed certificate for the given hostname.
    Returns the private key and certificate objects.
    """
    key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )
    subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, hostname)])
    now = datetime.datetime.now(datetime.UTC)
    cert_builder = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + datetime.timedelta(days=valid_days))
    )
    # Add a Subject Alternative Name extension with the hostname.
    cert_builder = cert_builder.add_extension(
        x509.SubjectAlternativeName([x509.DNSName(hostname)]), critical=False
    )
    # Add Subject Key Identifier
    cert_builder = cert_builder.add_extension(
        x509.SubjectKeyIdentifier.from_public_key(key.public_key()), critical=False
    )
    # Add Authority Key Identifier (for self-signed cert, same as subject key id)
    cert_builder = cert_builder.add_extension(
        x509.AuthorityKeyIdentifier.from_issuer_public_key(key.public_key()),
        critical=False,
    )

    cert = cert_builder.sign(
        private_key=key, algorithm=hashes.SHA256(), backend=default_backend()
    )
    return key, cert


def get_cert_details(cert: x509.Certificate):
    """
    Extracts various TLS-related attributes from the certificate and returns them in a dictionary.
    Then, randomizes some attributes and fakes a non-self-signed issuer for a percentage of certificates.
    """
    details = {}

    # Compute certificate fingerprints
    fp_sha1 = cert.fingerprint(hashes.SHA1()).hex()
    fp_sha256 = cert.fingerprint(hashes.SHA256()).hex()

    # Validity dates as ISO strings and Unix timestamps
    not_before = cert.not_valid_before
    not_after = cert.not_valid_after
    details["tls.notBefore"] = not_before.strftime("%Y-%m-%dT%H:%M:%SZ")
    details["tls.notAfter"] = not_after.strftime("%Y-%m-%dT%H:%M:%SZ")
    details["tls.notBeforeTS"] = str(int(not_before.timestamp()))
    details["tls.notAfterTS"] = str(int(not_after.timestamp()))

    # Subject and Issuer information (using RFC4514 string format)
    subject = cert.subject.rfc4514_string()
    issuer = cert.issuer.rfc4514_string()
    details["tls.subject"] = subject
    details["tls.issuer"] = issuer

    # Extract Common Name (CN) from the subject
    cn = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
    details["tls.cn"] = cn

    # Serial number in hexadecimal format
    details["tls.serial"] = format(cert.serial_number, "x")

    # Signature algorithm used
    details["tls.signatureAlgorithm"] = (
        cert.signature_hash_algorithm.name
        if cert.signature_hash_algorithm
        else "unknown"
    )

    # Subject Key Identifier (if available)
    try:
        ski = cert.extensions.get_extension_for_oid(
            ExtensionOID.SUBJECT_KEY_IDENTIFIER
        ).value.digest.hex()
        details["tls.subjectKeyID"] = ski
    except x509.ExtensionNotFound:
        details["tls.subjectKeyID"] = ""

    # Authority Key Identifier (if available)
    try:
        aki = cert.extensions.get_extension_for_oid(
            ExtensionOID.AUTHORITY_KEY_IDENTIFIER
        ).value.key_identifier.hex()
        details["tls.authorityKeyID"] = aki
    except x509.ExtensionNotFound:
        details["tls.authorityKeyID"] = ""

    # Fingerprints – these are sometimes used for validation.
    details["tls.fp.sha1"] = fp_sha1
    details["tls.fp.sha256"] = "SHA256:" + fp_sha256
    # For tls.fp.caSha1, use the authority key ID if available; otherwise, fallback to sha1 fingerprint.
    details["tls.fp.caSha1"] = details["tls.authorityKeyID"] or fp_sha1

    # The PEM-encoded certificate is stored in tls.certificates.
    cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")
    details["tls.certificates"] = cert_pem

    # Dummy URLs for CRL, OCSP, and Issuing URL – these can be customized as needed.
    details["tls.crl"] = "http://rz-corporation-cert-authority.com/crl.pem"
    details["tls.ocsp"] = "http://rz-corporation-cert-authority.com/ocsp"
    details["tls.issuingURL"] = "http://rz-corporation-cert-authority/issuing.crt"

    # For tls.names, we include the common name.
    details["tls.names"] = cn

    # ----- Randomize and Fake TLS Connection Attributes -----
    # (1) Fake that 80% of certificates are issued by a real signing authority
    if random.random() < 0.8:
        # Replace issuer with a fake CA name and generate a fake authority key ID (40 hex characters).
        fake_issuer = "CN=RZCA Inc, O=RZ Certificate Authority, C=US"
        details["tls.issuer"] = fake_issuer
        fake_aki = "".join(random.choice("0123456789abcdef") for _ in range(40))
        details["tls.authorityKeyID"] = fake_aki
        details["tls.fp.caSha1"] = fake_aki

    # (2) Randomize TLS connection attributes

    # Randomize whether a client certificate is required.
    details["tls.requiresClientCertificate"] = random.choice(["true", "false"])

    # Randomize cipher and cipher name.
    cipher_options = [
        ("0xc030", "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384"),
        ("0xc02f", "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256"),
        ("0xc02b", "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256"),
        ("0xcca8", "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256"),
        ("0xcca9", "TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256"),
    ]
    cipher, cipherName = random.choice(cipher_options)
    details["tls.cipher"] = cipher
    details["tls.cipherName"] = cipherName

    # Randomize supported version names and values.
    version_options = [
        ("TLSv1.2", "0x0303", "0x0303", "TLSv1.2"),
        ("TLSv1.3", "0x0304", "0x0304", "TLSv1.3"),
    ]
    (supportedVersionNames, supportedVersions, version, versionName) = random.choice(
        version_options
    )
    details["tls.supportedVersionNames"] = supportedVersionNames
    details["tls.supportedVersions"] = supportedVersions
    details["tls.version"] = version
    details["tls.versionName"] = versionName

    # Randomize a placeholder for tls.rzfp0.
    random_rzfp0 = "v0|t10:" + "".join(
        random.choice("0123456789abcdef") for _ in range(20)
    )
    details["tls.rzfp0"] = random_rzfp0

    return details


def fudge_jamf_data(asset_cache: list) -> bool:
    # config file requires a custom id
    output = [
        {
            "type": "config",
            "ts": current_rz_time(),
            "probes": ["custom"],
            "params": {
                "_custom-integration-id": JAMF_CUSTOM_INTEGRATION_ID,
                "exclude-unknown": "false",
                "stale-asset-expiration": "180",
            },
        }
    ]
    for asset in asset_cache:
        os = asset.get("os")
        # create records for correct asset types
        if os == "Apple":
            os_info = asset.get("os_full").split("-")

            if len(os_info) == 3:
                os_version = os_info[2]
                os_type = os_info[1]
            else:
                os_version = os_info[0]
                os_type = os_info[0]

            mac = asset.get("new_mac")
            ip = asset.get("ip")
            secondary_ip = asset.get("secondary_v4")

            output.append(
                {
                    "type": "result",
                    "ts": current_rz_time(),
                    "probe": "custom",
                    "info": {
                        "_software": "W3siaWQiOiJcdTAwM2NmdW5jdGlvbiB1dWlkNCBhdCAweDEwNjgwODA0MFx1MDAzZSIsInNlcnZpY2VBZGRyZXNzIjoiMTkyLjE2OC44Ni40NyIsImluc3RhbGxlZFNpemUiOjAsInByb2R1Y3QiOiJNaXNzaW9uIENvbnRyb2wuYXBwIiwidmVyc2lvbiI6IjEuMiJ9LHsiaWQiOiJcdTAwM2NmdW5jdGlvbiB1dWlkNCBhdCAweDEwNjgwODA0MFx1MDAzZSIsInNlcnZpY2VBZGRyZXNzIjoiMTkyLjE2OC44Ni40NyIsImluc3RhbGxlZFNpemUiOjYzLCJwcm9kdWN0IjoiTWFwcy5hcHAiLCJ2ZXJzaW9uIjoiMy4wIn0seyJpZCI6Ilx1MDAzY2Z1bmN0aW9uIHV1aWQ0IGF0IDB4MTA2ODA4MDQwXHUwMDNlIiwic2VydmljZUFkZHJlc3MiOiIxOTIuMTY4Ljg2LjQ3IiwiaW5zdGFsbGVkU2l6ZSI6NCwicHJvZHVjdCI6IkF1dG9tYXRvci5hcHAiLCJ2ZXJzaW9uIjoiMi4xMCJ9LHsiaWQiOiJcdTAwM2NmdW5jdGlvbiB1dWlkNCBhdCAweDEwNjgwODA0MFx1MDAzZSIsInNlcnZpY2VBZGRyZXNzIjoiMTkyLjE2OC44Ni40NyIsImluc3RhbGxlZFNpemUiOjE2NjAsInByb2R1Y3QiOiJHb29nbGUgQ2hyb21lLmFwcCIsInZlcnNpb24iOiIxMjQuMC42MzY3LjIwOCJ9LHsiaWQiOiJcdTAwM2NmdW5jdGlvbiB1dWlkNCBhdCAweDEwNjgwODA0MFx1MDAzZSIsInNlcnZpY2VBZGRyZXNzIjoiMTkyLjE2OC44Ni40NyIsImluc3RhbGxlZFNpemUiOjEsInByb2R1Y3QiOiJUaW1lIE1hY2hpbmUuYXBwIiwidmVyc2lvbiI6IjEuMyJ9LHsiaWQiOiJcdTAwM2NmdW5jdGlvbiB1dWlkNCBhdCAweDEwNjgwODA0MFx1MDAzZSIsInNlcnZpY2VBZGRyZXNzIjoiMTkyLjE2OC44Ni40NyIsImluc3RhbGxlZFNpemUiOjEzMzEsInByb2R1Y3QiOiJWTXdhcmUgRnVzaW9uLmFwcCIsInZlcnNpb24iOiIxMy4wLjIifSx7ImlkIjoiXHUwMDNjZnVuY3Rpb24gdXVpZDQgYXQgMHgxMDY4MDgwNDBcdTAwM2UiLCJzZXJ2aWNlQWRkcmVzcyI6IjE5Mi4xNjguODYuNDciLCJpbnN0YWxsZWRTaXplIjowLCJwcm9kdWN0IjoiR29vZ2xlIFNoZWV0cy5hcHAiLCJ2ZXJzaW9uIjoiODQuMCJ9LHsiaWQiOiJcdTAwM2NmdW5jdGlvbiB1dWlkNCBhdCAweDEwNjgwODA0MFx1MDAzZSIsInNlcnZpY2VBZGRyZXNzIjoiMTkyLjE2OC44Ni40NyIsImluc3RhbGxlZFNpemUiOjAsInByb2R1Y3QiOiJTY3JlZW5zaG90LmFwcCIsInZlcnNpb24iOiIxLjAifSx7ImlkIjoiXHUwMDNjZnVuY3Rpb24gdXVpZDQgYXQgMHgxMDY4MDgwNDBcdTAwM2UiLCJzZXJ2aWNlQWRkcmVzcyI6IjE5Mi4xNjguODYuNDciLCJpbnN0YWxsZWRTaXplIjoyLCJwcm9kdWN0IjoiUHJpbnQgQ2VudGVyLmFwcCIsInZlcnNpb24iOiIxLjAifSx7ImlkIjoiXHUwMDNjZnVuY3Rpb24gdXVpZDQgYXQgMHgxMDY4MDgwNDBcdTAwM2UiLCJzZXJ2aWNlQWRkcmVzcyI6IjE5Mi4xNjguODYuNDciLCJpbnN0YWxsZWRTaXplIjozLCJwcm9kdWN0IjoiU3lzdGVtIEluZm9ybWF0aW9uLmFwcCIsInZlcnNpb24iOiIxMS4wIn0seyJpZCI6Ilx1MDAzY2Z1bmN0aW9uIHV1aWQ0IGF0IDB4MTA2ODA4MDQwXHUwMDNlIiwic2VydmljZUFkZHJlc3MiOiIxOTIuMTY4Ljg2LjQ3IiwiaW5zdGFsbGVkU2l6ZSI6NDEsInByb2R1Y3QiOiJQb2RjYXN0cy5hcHAiLCJ2ZXJzaW9uIjoiMS4xLjAifSx7ImlkIjoiXHUwMDNjZnVuY3Rpb24gdXVpZDQgYXQgMHgxMDY4MDgwNDBcdTAwM2UiLCJzZXJ2aWNlQWRkcmVzcyI6IjE5Mi4xNjguODYuNDciLCJpbnN0YWxsZWRTaXplIjoyMzAsInByb2R1Y3QiOiIxUGFzc3dvcmQgNy5hcHAiLCJ2ZXJzaW9uIjoiNy45LjExIn0seyJpZCI6Ilx1MDAzY2Z1bmN0aW9uIHV1aWQ0IGF0IDB4MTA2ODA4MDQwXHUwMDNlIiwic2VydmljZUFkZHJlc3MiOiIxOTIuMTY4Ljg2LjQ3IiwiaW5zdGFsbGVkU2l6ZSI6MTksInByb2R1Y3QiOiJSZW1pbmRlcnMuYXBwIiwidmVyc2lvbiI6IjcuMCJ9LHsiaWQiOiJcdTAwM2NmdW5jdGlvbiB1dWlkNCBhdCAweDEwNjgwODA0MFx1MDAzZSIsInNlcnZpY2VBZGRyZXNzIjoiMTkyLjE2OC44Ni40NyIsImluc3RhbGxlZFNpemUiOjMsInByb2R1Y3QiOiJQaG90byBCb290aC5hcHAiLCJ2ZXJzaW9uIjoiMTMuMSJ9LHsiaWQiOiJcdTAwM2NmdW5jdGlvbiB1dWlkNCBhdCAweDEwNjgwODA0MFx1MDAzZSIsInNlcnZpY2VBZGRyZXNzIjoiMTkyLjE2OC44Ni40NyIsImluc3RhbGxlZFNpemUiOjQsInByb2R1Y3QiOiJBbmFjb25kYS1OYXZpZ2F0b3IuYXBwIiwidmVyc2lvbiI6IiRQS0dfVkVSU0lPTiJ9LHsiaWQiOiJcdTAwM2NmdW5jdGlvbiB1dWlkNCBhdCAweDEwNjgwODA0MFx1MDAzZSIsInNlcnZpY2VBZGRyZXNzIjoiMTkyLjE2OC44Ni40NyIsImluc3RhbGxlZFNpemUiOjgsInByb2R1Y3QiOiJQcmV2aWV3LmFwcCIsInZlcnNpb24iOiIxMS4wIn0seyJpZCI6Ilx1MDAzY2Z1bmN0aW9uIHV1aWQ0IGF0IDB4MTA2ODA4MDQwXHUwMDNlIiwic2VydmljZUFkZHJlc3MiOiIxOTIuMTY4Ljg2LjQ3IiwiaW5zdGFsbGVkU2l6ZSI6NjEzLCJwcm9kdWN0IjoiTG9vbS5hcHAiLCJ2ZXJzaW9uIjoiMC4yMTUuMCJ9LHsiaWQiOiJcdTAwM2NmdW5jdGlvbiB1dWlkNCBhdCAweDEwNjgwODA0MFx1MDAzZSIsInNlcnZpY2VBZGRyZXNzIjoiMTkyLjE2OC44Ni40NyIsImluc3RhbGxlZFNpemUiOjQsInByb2R1Y3QiOiJOZXdzLmFwcCIsInZlcnNpb24iOiI5LjQifSx7ImlkIjoiXHUwMDNjZnVuY3Rpb24gdXVpZDQgYXQgMHgxMDY4MDgwNDBcdTAwM2UiLCJzZXJ2aWNlQWRkcmVzcyI6IjE5Mi4xNjguODYuNDciLCJpbnN0YWxsZWRTaXplIjo1MDUsInByb2R1Y3QiOiJNaWNyb3NvZnQgVGVhbXMuYXBwIiwidmVyc2lvbiI6IjUzMzM1NiJ9LHsiaWQiOiJcdTAwM2NmdW5jdGlvbiB1dWlkNCBhdCAweDEwNjgwODA0MFx1MDAzZSIsInNlcnZpY2VBZGRyZXNzIjoiMTkyLjE2OC44Ni40NyIsImluc3RhbGxlZFNpemUiOjIwLCJwcm9kdWN0IjoiSnVtcENsb3VkU2VydmljZUFjY291bnQuYXBwIiwidmVyc2lvbiI6IjEuMCJ9LHsiaWQiOiJcdTAwM2NmdW5jdGlvbiB1dWlkNCBhdCAweDEwNjgwODA0MFx1MDAzZSIsInNlcnZpY2VBZGRyZXNzIjoiMTkyLjE2OC44Ni40NyIsImluc3RhbGxlZFNpemUiOjMsInByb2R1Y3QiOiJJbWFnZSBDYXB0dXJlLmFwcCIsInZlcnNpb24iOiI4LjAifSx7ImlkIjoiXHUwMDNjZnVuY3Rpb24gdXVpZDQgYXQgMHgxMDY4MDgwNDBcdTAwM2UiLCJzZXJ2aWNlQWRkcmVzcyI6IjE5Mi4xNjguODYuNDciLCJpbnN0YWxsZWRTaXplIjoxMywicHJvZHVjdCI6IkRpY3Rpb25hcnkuYXBwIiwidmVyc2lvbiI6IjIuMy4wIn0seyJpZCI6Ilx1MDAzY2Z1bmN0aW9uIHV1aWQ0IGF0IDB4MTA2ODA4MDQwXHUwMDNlIiwic2VydmljZUFkZHJlc3MiOiIxOTIuMTY4Ljg2LjQ3IiwiaW5zdGFsbGVkU2l6ZSI6MywicHJvZHVjdCI6IlZvaWNlTWVtb3MuYXBwIiwidmVyc2lvbiI6IjIuNCJ9LHsiaWQiOiJcdTAwM2NmdW5jdGlvbiB1dWlkNCBhdCAweDEwNjgwODA0MFx1MDAzZSIsInNlcnZpY2VBZGRyZXNzIjoiMTkyLjE2OC44Ni40NyIsImluc3RhbGxlZFNpemUiOjYsInByb2R1Y3QiOiJTeXN0ZW0gU2V0dGluZ3MuYXBwIiwidmVyc2lvbiI6IjE1LjAifSx7ImlkIjoiXHUwMDNjZnVuY3Rpb24gdXVpZDQgYXQgMHgxMDY4MDgwNDBcdTAwM2UiLCJzZXJ2aWNlQWRkcmVzcyI6IjE5Mi4xNjguODYuNDciLCJpbnN0YWxsZWRTaXplIjoxNiwicHJvZHVjdCI6Ik5vdGVzLmFwcCIsInZlcnNpb24iOiI0LjExIn0seyJpZCI6Ilx1MDAzY2Z1bmN0aW9uIHV1aWQ0IGF0IDB4MTA2ODA4MDQwXHUwMDNlIiwic2VydmljZUFkZHJlc3MiOiIxOTIuMTY4Ljg2LjQ3IiwiaW5zdGFsbGVkU2l6ZSI6MCwicHJvZHVjdCI6Ikdvb2dsZSBTbGlkZXMuYXBwIiwidmVyc2lvbiI6Ijg0LjAifSx7ImlkIjoiXHUwMDNjZnVuY3Rpb24gdXVpZDQgYXQgMHgxMDY4MDgwNDBcdTAwM2UiLCJzZXJ2aWNlQWRkcmVzcyI6IjE5Mi4xNjguODYuNDciLCJpbnN0YWxsZWRTaXplIjo0MDMsInByb2R1Y3QiOiJHb29nbGUgRHJpdmUuYXBwIiwidmVyc2lvbiI6Ijg0LjAifSx7ImlkIjoiXHUwMDNjZnVuY3Rpb24gdXVpZDQgYXQgMHgxMDY4MDgwNDBcdTAwM2UiLCJzZXJ2aWNlQWRkcmVzcyI6IjE5Mi4xNjguODYuNDciLCJpbnN0YWxsZWRTaXplIjo1LCJwcm9kdWN0IjoiQ2xvY2suYXBwIiwidmVyc2lvbiI6IjEuMSJ9LHsiaWQiOiJcdTAwM2NmdW5jdGlvbiB1dWlkNCBhdCAweDEwNjgwODA0MFx1MDAzZSIsInNlcnZpY2VBZGRyZXNzIjoiMTkyLjE2OC44Ni40NyIsImluc3RhbGxlZFNpemUiOjEwLCJwcm9kdWN0IjoiR3JhcGhlci5hcHAiLCJ2ZXJzaW9uIjoiMi43In0seyJpZCI6Ilx1MDAzY2Z1bmN0aW9uIHV1aWQ0IGF0IDB4MTA2ODA4MDQwXHUwMDNlIiwic2VydmljZUFkZHJlc3MiOiIxOTIuMTY4Ljg2LjQ3IiwiaW5zdGFsbGVkU2l6ZSI6MywicHJvZHVjdCI6IlRlcm1pbmFsLmFwcCIsInZlcnNpb24iOiIyLjE0In0seyJpZCI6Ilx1MDAzY2Z1bmN0aW9uIHV1aWQ0IGF0IDB4MTA2ODA4MDQwXHUwMDNlIiwic2VydmljZUFkZHJlc3MiOiIxOTIuMTY4Ljg2LjQ3IiwiaW5zdGFsbGVkU2l6ZSI6MTMsInByb2R1Y3QiOiJKdW1wY2xvdWQuYXBwIiwidmVyc2lvbiI6InYyLjIuMSJ9LHsiaWQiOiJcdTAwM2NmdW5jdGlvbiB1dWlkNCBhdCAweDEwNjgwODA0MFx1MDAzZSIsInNlcnZpY2VBZGRyZXNzIjoiMTkyLjE2OC44Ni40NyIsImluc3RhbGxlZFNpemUiOjI2MCwicHJvZHVjdCI6Inpvb20udXMuYXBwIiwidmVyc2lvbiI6IjUuMTcuMTEgKDMxNTgwKSJ9LHsiaWQiOiJcdTAwM2NmdW5jdGlvbiB1dWlkNCBhdCAweDEwNjgwODA0MFx1MDAzZSIsInNlcnZpY2VBZGRyZXNzIjoiMTkyLjE2OC44Ni40NyIsImluc3RhbGxlZFNpemUiOjYxNCwicHJvZHVjdCI6IkNpc2NvIFBhY2tldCBUcmFjZXIgOC4xLjEuYXBwIiwidmVyc2lvbiI6Im4vYSJ9LHsiaWQiOiJcdTAwM2NmdW5jdGlvbiB1dWlkNCBhdCAweDEwNjgwODA0MFx1MDAzZSIsInNlcnZpY2VBZGRyZXNzIjoiMTkyLjE2OC44Ni40NyIsImluc3RhbGxlZFNpemUiOjUzLCJwcm9kdWN0IjoiQm9va3MuYXBwIiwidmVyc2lvbiI6IjYuNCJ9LHsiaWQiOiJcdTAwM2NmdW5jdGlvbiB1dWlkNCBhdCAweDEwNjgwODA0MFx1MDAzZSIsInNlcnZpY2VBZGRyZXNzIjoiMTkyLjE2OC44Ni40NyIsImluc3RhbGxlZFNpemUiOjE0LCJwcm9kdWN0IjoiRmFjZVRpbWUuYXBwIiwidmVyc2lvbiI6IjUuMCJ9LHsiaWQiOiJcdTAwM2NmdW5jdGlvbiB1dWlkNCBhdCAweDEwNjgwODA0MFx1MDAzZSIsInNlcnZpY2VBZGRyZXNzIjoiMTkyLjE2OC44Ni40NyIsImluc3RhbGxlZFNpemUiOjEsInByb2R1Y3QiOiJEaWdpdGFsIENvbG9yIE1ldGVyLmFwcCIsInZlcnNpb24iOiI1LjIyIn0seyJpZCI6Ilx1MDAzY2Z1bmN0aW9uIHV1aWQ0IGF0IDB4MTA2ODA4MDQwXHUwMDNlIiwic2VydmljZUFkZHJlc3MiOiIxOTIuMTY4Ljg2LjQ3IiwiaW5zdGFsbGVkU2l6ZSI6OSwicHJvZHVjdCI6IkFjdGl2aXR5IE1vbml0b3IuYXBwIiwidmVyc2lvbiI6IjEwLjE0In0seyJpZCI6Ilx1MDAzY2Z1bmN0aW9uIHV1aWQ0IGF0IDB4MTA2ODA4MDQwXHUwMDNlIiwic2VydmljZUFkZHJlc3MiOiIxOTIuMTY4Ljg2LjQ3IiwiaW5zdGFsbGVkU2l6ZSI6NiwicHJvZHVjdCI6IkNvbnRhY3RzLmFwcCIsInZlcnNpb24iOiIxNC4wIn0seyJpZCI6Ilx1MDAzY2Z1bmN0aW9uIHV1aWQ0IGF0IDB4MTA2ODA4MDQwXHUwMDNlIiwic2VydmljZUFkZHJlc3MiOiIxOTIuMTY4Ljg2LjQ3IiwiaW5zdGFsbGVkU2l6ZSI6NSwicHJvZHVjdCI6IkhvbWUuYXBwIiwidmVyc2lvbiI6IjguMCJ9LHsiaWQiOiJcdTAwM2NmdW5jdGlvbiB1dWlkNCBhdCAweDEwNjgwODA0MFx1MDAzZSIsInNlcnZpY2VBZGRyZXNzIjoiMTkyLjE2OC44Ni40NyIsImluc3RhbGxlZFNpemUiOjYsInByb2R1Y3QiOiJRdWlja1RpbWUgUGxheWVyLmFwcCIsInZlcnNpb24iOiIxMC41In0seyJpZCI6Ilx1MDAzY2Z1bmN0aW9uIHV1aWQ0IGF0IDB4MTA2ODA4MDQwXHUwMDNlIiwic2VydmljZUFkZHJlc3MiOiIxOTIuMTY4Ljg2LjQ3IiwiaW5zdGFsbGVkU2l6ZSI6MywicHJvZHVjdCI6IlNjcmVlbiBTaGFyaW5nLmFwcCIsInZlcnNpb24iOiI0LjMifSx7ImlkIjoiXHUwMDNjZnVuY3Rpb24gdXVpZDQgYXQgMHgxMDY4MDgwNDBcdTAwM2UiLCJzZXJ2aWNlQWRkcmVzcyI6IjE5Mi4xNjguODYuNDciLCJpbnN0YWxsZWRTaXplIjoxMSwicHJvZHVjdCI6IlZvaWNlT3ZlciBVdGlsaXR5LmFwcCIsInZlcnNpb24iOiIxMCJ9LHsiaWQiOiJcdTAwM2NmdW5jdGlvbiB1dWlkNCBhdCAweDEwNjgwODA0MFx1MDAzZSIsInNlcnZpY2VBZGRyZXNzIjoiMTkyLjE2OC44Ni40NyIsImluc3RhbGxlZFNpemUiOjEwLCJwcm9kdWN0IjoiRm9udCBCb29rLmFwcCIsInZlcnNpb24iOiIxMS4wIn0seyJpZCI6Ilx1MDAzY2Z1bmN0aW9uIHV1aWQ0IGF0IDB4MTA2ODA4MDQwXHUwMDNlIiwic2VydmljZUFkZHJlc3MiOiIxOTIuMTY4Ljg2LjQ3IiwiaW5zdGFsbGVkU2l6ZSI6NywicHJvZHVjdCI6IkRpc2sgVXRpbGl0eS5hcHAiLCJ2ZXJzaW9uIjoiMjIuNiJ9LHsiaWQiOiJcdTAwM2NmdW5jdGlvbiB1dWlkNCBhdCAweDEwNjgwODA0MFx1MDAzZSIsInNlcnZpY2VBZGRyZXNzIjoiMTkyLjE2OC44Ni40NyIsImluc3RhbGxlZFNpemUiOjU4LCJwcm9kdWN0IjoiTXVzaWMuYXBwIiwidmVyc2lvbiI6IjEuNC41In0seyJpZCI6Ilx1MDAzY2Z1bmN0aW9uIHV1aWQ0IGF0IDB4MTA2ODA4MDQwXHUwMDNlIiwic2VydmljZUFkZHJlc3MiOiIxOTIuMTY4Ljg2LjQ3IiwiaW5zdGFsbGVkU2l6ZSI6Mjk4LCJwcm9kdWN0IjoiQnJhdmUgQnJvd3Nlci5hcHAiLCJ2ZXJzaW9uIjoiMTE2LjEuNTcuNDcifSx7ImlkIjoiXHUwMDNjZnVuY3Rpb24gdXVpZDQgYXQgMHgxMDY4MDgwNDBcdTAwM2UiLCJzZXJ2aWNlQWRkcmVzcyI6IjE5Mi4xNjguODYuNDciLCJpbnN0YWxsZWRTaXplIjoyNSwicHJvZHVjdCI6IkZyZWVmb3JtLmFwcCIsInZlcnNpb24iOiIyLjQifSx7ImlkIjoiXHUwMDNjZnVuY3Rpb24gdXVpZDQgYXQgMHgxMDY4MDgwNDBcdTAwM2UiLCJzZXJ2aWNlQWRkcmVzcyI6IjE5Mi4xNjguODYuNDciLCJpbnN0YWxsZWRTaXplIjoyLCJwcm9kdWN0IjoiU2NyaXB0IEVkaXRvci5hcHAiLCJ2ZXJzaW9uIjoiMi4xMSJ9LHsiaWQiOiJcdTAwM2NmdW5jdGlvbiB1dWlkNCBhdCAweDEwNjgwODA0MFx1MDAzZSIsInNlcnZpY2VBZGRyZXNzIjoiMTkyLjE2OC44Ni40NyIsImluc3RhbGxlZFNpemUiOjMsInByb2R1Y3QiOiJTdG9ja3MuYXBwIiwidmVyc2lvbiI6IjYuMi4yIn0seyJpZCI6Ilx1MDAzY2Z1bmN0aW9uIHV1aWQ0IGF0IDB4MTA2ODA4MDQwXHUwMDNlIiwic2VydmljZUFkZHJlc3MiOiIxOTIuMTY4Ljg2LjQ3IiwiaW5zdGFsbGVkU2l6ZSI6NSwicHJvZHVjdCI6IkJvb3QgQ2FtcCBBc3Npc3RhbnQuYXBwIiwidmVyc2lvbiI6IjYuMS4wIn0seyJpZCI6Ilx1MDAzY2Z1bmN0aW9uIHV1aWQ0IGF0IDB4MTA2ODA4MDQwXHUwMDNlIiwic2VydmljZUFkZHJlc3MiOiIxOTIuMTY4Ljg2LjQ3IiwiaW5zdGFsbGVkU2l6ZSI6MiwicHJvZHVjdCI6IlRleHRFZGl0LmFwcCIsInZlcnNpb24iOiIxLjE5In0seyJpZCI6Ilx1MDAzY2Z1bmN0aW9uIHV1aWQ0IGF0IDB4MTA2ODA4MDQwXHUwMDNlIiwic2VydmljZUFkZHJlc3MiOiIxOTIuMTY4Ljg2LjQ3IiwiaW5zdGFsbGVkU2l6ZSI6MjUsInByb2R1Y3QiOiJNYWlsLmFwcCIsInZlcnNpb24iOiIxNi4wIn0seyJpZCI6Ilx1MDAzY2Z1bmN0aW9uIHV1aWQ0IGF0IDB4MTA2ODA4MDQwXHUwMDNlIiwic2VydmljZUFkZHJlc3MiOiIxOTIuMTY4Ljg2LjQ3IiwiaW5zdGFsbGVkU2l6ZSI6MywicHJvZHVjdCI6IkNhbGN1bGF0b3IuYXBwIiwidmVyc2lvbiI6IjEwLjE2In0seyJpZCI6Ilx1MDAzY2Z1bmN0aW9uIHV1aWQ0IGF0IDB4MTA2ODA4MDQwXHUwMDNlIiwic2VydmljZUFkZHJlc3MiOiIxOTIuMTY4Ljg2LjQ3IiwiaW5zdGFsbGVkU2l6ZSI6MjIxLCJwcm9kdWN0IjoiV2lyZXNoYXJrLmFwcCIsInZlcnNpb24iOiI0LjAuNCJ9LHsiaWQiOiJcdTAwM2NmdW5jdGlvbiB1dWlkNCBhdCAweDEwNjgwODA0MFx1MDAzZSIsInNlcnZpY2VBZGRyZXNzIjoiMTkyLjE2OC44Ni40NyIsImluc3RhbGxlZFNpemUiOjI4LCJwcm9kdWN0IjoibWFpbnRlbmFuY2V0b29sLmFwcCIsInZlcnNpb24iOiJuL2EifSx7ImlkIjoiXHUwMDNjZnVuY3Rpb24gdXVpZDQgYXQgMHgxMDY4MDgwNDBcdTAwM2UiLCJzZXJ2aWNlQWRkcmVzcyI6IjE5Mi4xNjguODYuNDciLCJpbnN0YWxsZWRTaXplIjoyNTgsInByb2R1Y3QiOiJTbGFjay5hcHAiLCJ2ZXJzaW9uIjoiNC4zOC4xMjEifSx7ImlkIjoiXHUwMDNjZnVuY3Rpb24gdXVpZDQgYXQgMHgxMDY4MDgwNDBcdTAwM2UiLCJzZXJ2aWNlQWRkcmVzcyI6IjE5Mi4xNjguODYuNDciLCJpbnN0YWxsZWRTaXplIjowLCJwcm9kdWN0IjoiR29vZ2xlIERvY3MuYXBwIiwidmVyc2lvbiI6Ijg0LjAifSx7ImlkIjoiXHUwMDNjZnVuY3Rpb24gdXVpZDQgYXQgMHgxMDY4MDgwNDBcdTAwM2UiLCJzZXJ2aWNlQWRkcmVzcyI6IjE5Mi4xNjguODYuNDciLCJpbnN0YWxsZWRTaXplIjozMiwicHJvZHVjdCI6IldlYXRoZXIuYXBwIiwidmVyc2lvbiI6IjQuMi4yIn0seyJpZCI6Ilx1MDAzY2Z1bmN0aW9uIHV1aWQ0IGF0IDB4MTA2ODA4MDQwXHUwMDNlIiwic2VydmljZUFkZHJlc3MiOiIxOTIuMTY4Ljg2LjQ3IiwiaW5zdGFsbGVkU2l6ZSI6NywicHJvZHVjdCI6IkNoZXNzLmFwcCIsInZlcnNpb24iOiIzLjE4In0seyJpZCI6Ilx1MDAzY2Z1bmN0aW9uIHV1aWQ0IGF0IDB4MTA2ODA4MDQwXHUwMDNlIiwic2VydmljZUFkZHJlc3MiOiIxOTIuMTY4Ljg2LjQ3IiwiaW5zdGFsbGVkU2l6ZSI6MTMsInByb2R1Y3QiOiJTYWZhcmkuYXBwIiwidmVyc2lvbiI6IjE3LjUifSx7ImlkIjoiXHUwMDNjZnVuY3Rpb24gdXVpZDQgYXQgMHgxMDY4MDgwNDBcdTAwM2UiLCJzZXJ2aWNlQWRkcmVzcyI6IjE5Mi4xNjguODYuNDciLCJpbnN0YWxsZWRTaXplIjoxLCJwcm9kdWN0IjoiTGF1bmNocGFkLmFwcCIsInZlcnNpb24iOiIxLjAifSx7ImlkIjoiXHUwMDNjZnVuY3Rpb24gdXVpZDQgYXQgMHgxMDY4MDgwNDBcdTAwM2UiLCJzZXJ2aWNlQWRkcmVzcyI6IjE5Mi4xNjguODYuNDciLCJpbnN0YWxsZWRTaXplIjozMSwicHJvZHVjdCI6IkZpbmRNeS5hcHAiLCJ2ZXJzaW9uIjoiNC4wIn0seyJpZCI6Ilx1MDAzY2Z1bmN0aW9uIHV1aWQ0IGF0IDB4MTA2ODA4MDQwXHUwMDNlIiwic2VydmljZUFkZHJlc3MiOiIxOTIuMTY4Ljg2LjQ3IiwiaW5zdGFsbGVkU2l6ZSI6NCwicHJvZHVjdCI6IkNvbG9yU3luYyBVdGlsaXR5LmFwcCIsInZlcnNpb24iOiIxMi4wLjAifSx7ImlkIjoiXHUwMDNjZnVuY3Rpb24gdXVpZDQgYXQgMHgxMDY4MDgwNDBcdTAwM2UiLCJzZXJ2aWNlQWRkcmVzcyI6IjE5Mi4xNjguODYuNDciLCJpbnN0YWxsZWRTaXplIjoxLCJwcm9kdWN0IjoiU3RpY2tpZXMuYXBwIiwidmVyc2lvbiI6IjEwLjIifSx7ImlkIjoiXHUwMDNjZnVuY3Rpb24gdXVpZDQgYXQgMHgxMDY4MDgwNDBcdTAwM2UiLCJzZXJ2aWNlQWRkcmVzcyI6IjE5Mi4xNjguODYuNDciLCJpbnN0YWxsZWRTaXplIjoyLCJwcm9kdWN0IjoiQ29uc29sZS5hcHAiLCJ2ZXJzaW9uIjoiMS4xIn0seyJpZCI6Ilx1MDAzY2Z1bmN0aW9uIHV1aWQ0IGF0IDB4MTA2ODA4MDQwXHUwMDNlIiwic2VydmljZUFkZHJlc3MiOiIxOTIuMTY4Ljg2LjQ3IiwiaW5zdGFsbGVkU2l6ZSI6MiwicHJvZHVjdCI6IlNpcmkuYXBwIiwidmVyc2lvbiI6IjEuMCJ9LHsiaWQiOiJcdTAwM2NmdW5jdGlvbiB1dWlkNCBhdCAweDEwNjgwODA0MFx1MDAzZSIsInNlcnZpY2VBZGRyZXNzIjoiMTkyLjE2OC44Ni40NyIsImluc3RhbGxlZFNpemUiOjE1LCJwcm9kdWN0IjoiQXBwIFN0b3JlLmFwcCIsInZlcnNpb24iOiIzLjAifSx7ImlkIjoiXHUwMDNjZnVuY3Rpb24gdXVpZDQgYXQgMHgxMDY4MDgwNDBcdTAwM2UiLCJzZXJ2aWNlQWRkcmVzcyI6IjE5Mi4xNjguODYuNDciLCJpbnN0YWxsZWRTaXplIjo3MCwicHJvZHVjdCI6ImlUZXJtLmFwcCIsInZlcnNpb24iOiIzLjQuMjMifSx7ImlkIjoiXHUwMDNjZnVuY3Rpb24gdXVpZDQgYXQgMHgxMDY4MDgwNDBcdTAwM2UiLCJzZXJ2aWNlQWRkcmVzcyI6IjE5Mi4xNjguODYuNDciLCJpbnN0YWxsZWRTaXplIjo1NTYsInByb2R1Y3QiOiJWaXN1YWwgU3R1ZGlvIENvZGUuYXBwIiwidmVyc2lvbiI6IjEuODkuMCJ9LHsiaWQiOiJcdTAwM2NmdW5jdGlvbiB1dWlkNCBhdCAweDEwNjgwODA0MFx1MDAzZSIsInNlcnZpY2VBZGRyZXNzIjoiMTkyLjE2OC44Ni40NyIsImluc3RhbGxlZFNpemUiOjEsInByb2R1Y3QiOiJNaWdyYXRpb24gQXNzaXN0YW50LmFwcCIsInZlcnNpb24iOiIxNC41In0seyJpZCI6Ilx1MDAzY2Z1bmN0aW9uIHV1aWQ0IGF0IDB4MTA2ODA4MDQwXHUwMDNlIiwic2VydmljZUFkZHJlc3MiOiIxOTIuMTY4Ljg2LjQ3IiwiaW5zdGFsbGVkU2l6ZSI6MiwicHJvZHVjdCI6IlNob3J0Y3V0cy5hcHAiLCJ2ZXJzaW9uIjoiNy4wIn0seyJpZCI6Ilx1MDAzY2Z1bmN0aW9uIHV1aWQ0IGF0IDB4MTA2ODA4MDQwXHUwMDNlIiwic2VydmljZUFkZHJlc3MiOiIxOTIuMTY4Ljg2LjQ3IiwiaW5zdGFsbGVkU2l6ZSI6MTkxLCJwcm9kdWN0IjoiR2F0aGVyLmFwcCIsInZlcnNpb24iOiIwLjIuMiJ9LHsiaWQiOiJcdTAwM2NmdW5jdGlvbiB1dWlkNCBhdCAweDEwNjgwODA0MFx1MDAzZSIsInNlcnZpY2VBZGRyZXNzIjoiMTkyLjE2OC44Ni40NyIsImluc3RhbGxlZFNpemUiOjM3LCJwcm9kdWN0IjoiQWlyUG9ydCBVdGlsaXR5LmFwcCIsInZlcnNpb24iOiI2LjMuOSJ9LHsiaWQiOiJcdTAwM2NmdW5jdGlvbiB1dWlkNCBhdCAweDEwNjgwODA0MFx1MDAzZSIsInNlcnZpY2VBZGRyZXNzIjoiMTkyLjE2OC44Ni40NyIsImluc3RhbGxlZFNpemUiOjQ1LCJwcm9kdWN0IjoiVFYuYXBwIiwidmVyc2lvbiI6IjEuNC41In0seyJpZCI6Ilx1MDAzY2Z1bmN0aW9uIHV1aWQ0IGF0IDB4MTA2ODA4MDQwXHUwMDNlIiwic2VydmljZUFkZHJlc3MiOiIxOTIuMTY4Ljg2LjQ3IiwiaW5zdGFsbGVkU2l6ZSI6Nzg0LCJwcm9kdWN0IjoiV2ViZXguYXBwIiwidmVyc2lvbiI6IjQzLjIuMC4yNTIxMSJ9LHsiaWQiOiJcdTAwM2NmdW5jdGlvbiB1dWlkNCBhdCAweDEwNjgwODA0MFx1MDAzZSIsInNlcnZpY2VBZGRyZXNzIjoiMTkyLjE2OC44Ni40NyIsImluc3RhbGxlZFNpemUiOjUwMywicHJvZHVjdCI6IkRyYXRhIEFnZW50LmFwcCIsInZlcnNpb24iOiIzLjYuMSJ9LHsiaWQiOiJcdTAwM2NmdW5jdGlvbiB1dWlkNCBhdCAweDEwNjgwODA0MFx1MDAzZSIsInNlcnZpY2VBZGRyZXNzIjoiMTkyLjE2OC44Ni40NyIsImluc3RhbGxlZFNpemUiOjIyLCJwcm9kdWN0IjoiUGhvdG9zLmFwcCIsInZlcnNpb24iOiI5LjAifSx7ImlkIjoiXHUwMDNjZnVuY3Rpb24gdXVpZDQgYXQgMHgxMDY4MDgwNDBcdTAwM2UiLCJzZXJ2aWNlQWRkcmVzcyI6IjE5Mi4xNjguODYuNDciLCJpbnN0YWxsZWRTaXplIjo2LCJwcm9kdWN0IjoiQ2FsZW5kYXIuYXBwIiwidmVyc2lvbiI6IjE0LjAifSx7ImlkIjoiXHUwMDNjZnVuY3Rpb24gdXVpZDQgYXQgMHgxMDY4MDgwNDBcdTAwM2UiLCJzZXJ2aWNlQWRkcmVzcyI6IjE5Mi4xNjguODYuNDciLCJpbnN0YWxsZWRTaXplIjoxLCJwcm9kdWN0IjoiQmx1ZXRvb3RoIEZpbGUgRXhjaGFuZ2UuYXBwIiwidmVyc2lvbiI6IjkuMCJ9LHsiaWQiOiJcdTAwM2NmdW5jdGlvbiB1dWlkNCBhdCAweDEwNjgwODA0MFx1MDAzZSIsInNlcnZpY2VBZGRyZXNzIjoiMTkyLjE2OC44Ni40NyIsImluc3RhbGxlZFNpemUiOjEsInByb2R1Y3QiOiJTZW50aW5lbE9uZSBFeHRlbnNpb25zLmFwcCIsInZlcnNpb24iOiIyMy4yLjYifSx7ImlkIjoiXHUwMDNjZnVuY3Rpb24gdXVpZDQgYXQgMHgxMDY4MDgwNDBcdTAwM2UiLCJzZXJ2aWNlQWRkcmVzcyI6IjE5Mi4xNjguODYuNDciLCJpbnN0YWxsZWRTaXplIjo1LCJwcm9kdWN0IjoiTWVzc2FnZXMuYXBwIiwidmVyc2lvbiI6IjE0LjAifSx7ImlkIjoiXHUwMDNjZnVuY3Rpb24gdXVpZDQgYXQgMHgxMDY4MDgwNDBcdTAwM2UiLCJzZXJ2aWNlQWRkcmVzcyI6IjE5Mi4xNjguODYuNDciLCJpbnN0YWxsZWRTaXplIjo0LCJwcm9kdWN0IjoiS2V5Y2hhaW4gQWNjZXNzLmFwcCIsInZlcnNpb24iOiIxMS4wIn0seyJpZCI6Ilx1MDAzY2Z1bmN0aW9uIHV1aWQ0IGF0IDB4MTA2ODA4MDQwXHUwMDNlIiwic2VydmljZUFkZHJlc3MiOiIxOTIuMTY4Ljg2LjQ3IiwiaW5zdGFsbGVkU2l6ZSI6NDYsInByb2R1Y3QiOiJSYXNwYmVycnkgUGkgSW1hZ2VyLmFwcCIsInZlcnNpb24iOiIxLjcuMyJ9LHsiaWQiOiJcdTAwM2NmdW5jdGlvbiB1dWlkNCBhdCAweDEwNjgwODA0MFx1MDAzZSIsInNlcnZpY2VBZGRyZXNzIjoiMTkyLjE2OC44Ni40NyIsImluc3RhbGxlZFNpemUiOjI1NywicHJvZHVjdCI6IktpbmRsZS5hcHAiLCJ2ZXJzaW9uIjoiMS40MC4zIn0seyJpZCI6Ilx1MDAzY2Z1bmN0aW9uIHV1aWQ0IGF0IDB4MTA2ODA4MDQwXHUwMDNlIiwic2VydmljZUFkZHJlc3MiOiIxOTIuMTY4Ljg2LjQ3IiwiaW5zdGFsbGVkU2l6ZSI6MjYxLCJwcm9kdWN0IjoiSnVtcENsb3VkIFJlbW90ZSBBc3Npc3QuYXBwIiwidmVyc2lvbiI6IjAuMTk1LjAifSx7ImlkIjoiXHUwMDNjZnVuY3Rpb24gdXVpZDQgYXQgMHgxMDY4MDgwNDBcdTAwM2UiLCJzZXJ2aWNlQWRkcmVzcyI6IjE5Mi4xNjguODYuNDciLCJpbnN0YWxsZWRTaXplIjoxLCJwcm9kdWN0IjoiTGluZ3Vpc3QuYXBwIiwidmVyc2lvbiI6Im4vYSJ9LHsiaWQiOiJcdTAwM2NmdW5jdGlvbiB1dWlkNCBhdCAweDEwNjgwODA0MFx1MDAzZSIsInNlcnZpY2VBZGRyZXNzIjoiMTkyLjE2OC44Ni40NyIsImluc3RhbGxlZFNpemUiOjQsInByb2R1Y3QiOiJBdWRpbyBNSURJIFNldHVwLmFwcCIsInZlcnNpb24iOiIzLjYifV0=",
                        "applications": "[{'name': 'Mission Control.app', 'path': '/System/Applications/Mission Control.app', 'version': '1.2', 'macAppStore': False, 'sizeMegabytes': 0, 'bundleId': 'com.apple.exposelauncher', 'updateAvailable': False, 'externalVersionId': '0'}, {'name': 'Maps.app', 'path': '/System/Applications/Maps.app', 'version': '3.0', 'macAppStore': False, 'sizeMegabytes': 63, 'bundleId': 'com.apple.Maps', 'updateAvailable': False, 'externalVersionId': '0'}, {'name': 'Automator.app', 'path': '/System/Applications/Automator.app', 'version': '2.10', 'macAppStore': False, 'sizeMegabytes': 4, 'bundleId': 'com.apple.Automator', 'updateAvailable': False, 'externalVersionId': '0'}, {'name': 'Google Chrome.app', 'path': '/Applications/Google Chrome.app', 'version': '124.0.6367.208', 'macAppStore': False, 'sizeMegabytes': 1660, 'bundleId': 'com.google.Chrome', 'updateAvailable': False, 'externalVersionId': '0'}, {'name': 'Time Machine.app', 'path': '/System/Applications/Time Machine.app', 'version': '1.3', 'macAppStore': False, 'sizeMe",
                        "attachments": "[]",
                        "certificates": "[]",
                        "configurationProfiles": "[]",
                        "diskEncryption_bootPartitionEncryptionDetails_partitionFileVault2Percent": "100",
                        "diskEncryption_bootPartitionEncryptionDetails_partitionFileVault2State": "ENCRYPTED",
                        "diskEncryption_bootPartitionEncryptionDetails_partitionName": "Macintosh HD (Boot Partition)",
                        "diskEncryption_fileVault2EligibilityMessage": "Eligible",
                        "diskEncryption_fileVault2EnabledUserNames_0": "_jumpcloudserviceaccount",
                        "diskEncryption_fileVault2EnabledUserNames_1": asset.get(
                            "username"
                        ),
                        "diskEncryption_individualRecoveryKeyValidityStatus": "UNKNOWN",
                        "diskEncryption_institutionalRecoveryKeyPresent": "False",
                        "fonts": "[]",
                        "general_declarativeDeviceManagementEnabled": "False",
                        "general_enrolledViaAutomatedDeviceEnrollment": "False",
                        "general_itunesStoreAccountActive": "False",
                        "general_jamfBinaryVersion": "11.4.2-t1713554080",
                        "general_lastIpAddress": asset.get("new_secondary_v4", ""),
                        "general_lastReportedIp": asset.get("ip", ""),
                        "general_managementId": str(uuid.uuid4()),
                        "general_mdmCapable_capable": "False",
                        "general_mdmCapable_capableUsers": "[]",
                        "general_name": asset.get("new_hostname"),
                        "general_platform": "Mac",
                        "general_remoteManagement_managed": "True",
                        "general_site_id": "-1",
                        "general_site_name": "None",
                        "general_supervised": "False",
                        "general_userApprovedMdm": "False",
                        "groupMemberships": "[{'groupId': '1', 'groupName': 'All Managed Clients', 'smartGroup': True}]",
                        "hardware_altNetworkAdapterType": "Ethernet",
                        "hardware_appleSilicon": "False",
                        "hardware_batteryCapacityPercent": "1",
                        "hardware_bleCapable": "False",
                        "hardware_bootRom": "10151.121.1",
                        "hardware_busSpeedMhz": "0",
                        "hardware_cacheSizeKilobytes": "0",
                        "hardware_coreCount": "10",
                        "hardware_macAddress": mac,
                        "hardware_make": "Apple",
                        "hardware_networkAdapterType": "IEEE80211",
                        "hardware_nicSpeed": "n/a",
                        "hardware_openRamSlots": "0",
                        "hardware_processorArchitecture": "arm64",
                        "hardware_processorCount": "1",
                        "hardware_processorSpeedMhz": "0",
                        "hardware_serialNumber": "QJFRJ7HC9R",
                        "hardware_supportsIosAppInstalls": "False",
                        "hardware_totalRamMegabytes": "16384",
                        "hostnames": asset.get("new_hostname"),
                        "ibeacons": "[]",
                        "id": asset.get("device_id"),
                        "ipAddresses": f"{ip}\t{secondary_ip}",
                        "licensedSoftware": "[]",
                        "macAddresses": mac,
                        "manufacturer": "Apple",
                        "model": " ".join(os_info),
                        "operatingSystem_activeDirectoryStatus": "Not Bound",
                        "operatingSystem_build": "23F79",
                        "operatingSystem_fileVault2Status": "BOOT_ENCRYPTED",
                        "operatingSystem_name": os_type,
                        "operatingSystem_version": os_version,
                        "os": os_type,
                        "osVersion": os_version,
                        "plugins": "[]",
                        "printers": "[{'name': 'Canon MG3600 series', 'type': 'Canon MG3600 series-AirPrint', 'uri': 'dnssd://Canon%20MG3600%20series._ipps._tcp.local./?uuid=00000000-0000-1000-8000-6C3C7C196E33', 'location': None}]",
                        "purchasing_leased": "False",
                        "purchasing_lifeExpectancy": "0",
                        "purchasing_purchased": "True",
                        "security_activationLockEnabled": "False",
                        "security_autoLoginDisabled": "True",
                        "security_bootstrapTokenEscrowedStatus": "NOT_ESCROWED",
                        "security_externalBootLevel": "UNKNOWN",
                        "security_firewallEnabled": "False",
                        "security_gatekeeperStatus": "APP_STORE_AND_IDENTIFIED_DEVELOPERS",
                        "security_recoveryLockEnabled": "False",
                        "security_remoteDesktopEnabled": "False",
                        "security_secureBootLevel": "UNKNOWN",
                        "security_sipStatus": "ENABLED",
                        "security_xprotectVersion": "2194",
                        "softwareUpdates": "[]",
                        "udid": asset.get("device_id"),
                    },
                }
            )

    # write modified results to file for import
    with open(f"integration_jamf.json", "w") as f:
        for l in output:
            f.write(json.dumps(l, separators=(",", ":")) + "\n")
    return True


# these functions are for integrations that only require key=value updates
def fudge_azuread_data(asset_cache: list) -> bool:
    output = []
    for asset in asset_cache:
        asset_type = asset.get("type")
        asset_location = asset.get("network")

        # create records for correct asset types
        if asset_type in ["SERVER", "LAPTOP", "MOBILE"] and asset_location != "CLOUD":
            os_info = asset.get("os_full").split("-")
            if os_info[0] == "Microsoft":
                manufacter = "Microsoft Corporation"
            elif os_info[0] == "Apple":
                manufacter = "Apple Inc."
            else:
                manufacter = random.choice(["Dell Inc.", "SUSE", "HP", "IBM"])

            if len(os_info) == 3:
                os_version = os_info[2]
                os_type = os_info[1]
            elif len(os_info) == 2:
                os_version = os_info[1]
                os_type = os_info[0]
            else:
                os_version = "RZ-v1.0.0"
                os_type = "Unknown"

            output.append(
                {
                    "type": "result",
                    "ts": current_rz_time(),
                    "probe": "azuread",
                    "info": {
                        "_type": "dev",
                        "accountEnabled": "true",
                        "alternativeSecurityId.keys": "RZID-" + str(uuid.uuid4()),
                        "alternativeSecurityId.types": "2",
                        "approximateLastSignInDateTimeTS": str(
                            round(time.time() - 10000)
                        ),
                        "azureId": str(uuid.uuid4()),
                        "createdDateTimeTS": str(
                            round(time.time() - 10000 * random.choice([1, 2, 3, 4, 5]))
                        ),
                        "deviceId": str(asset.get("device_id", uuid.uuid4())),
                        "deviceOwnership": "Company",
                        "displayName": asset.get("new_hostname"),
                        "enrollmentType": "OnPremiseCoManaged",
                        "isManaged": "true",
                        "isRooted": "false",
                        "managementType": "MDM",
                        "manufacturer": manufacter,
                        "mdmAppId": str(uuid.uuid4()),
                        "onPremisesLastSyncDateTimeTS": str(round(time.time() - 10000)),
                        "onPremisesSyncEnabled": "true",
                        "operatingSystem": os_type,
                        "operatingSystemVersion": os_version,
                        "profileType": "RegisteredDevice",
                        "registrationDateTimeTS": str(
                            round(time.time() - 10000 * random.choice([1, 2, 3, 4, 5]))
                        ),
                        "trustType": (
                            "ServerAd" if asset_type == "SERVER" else "UserEnrollment"
                        ),
                    },
                }
            )

    # write modified results to file for import
    with open(f"integration_azuread.json", "w") as f:
        for l in output:
            f.write(json.dumps(l, separators=(",", ":")) + "\n")
    return True


def fudge_wiz_data(asset_cache: list) -> bool:
    output = []
    for asset in asset_cache:
        asset_type = asset.get("type")
        asset_location = asset.get("network")

        # create records for correct asset types
        if asset_type == "SERVER" and asset_location == "CLOUD":
            with open(f"./tasks/integration_wiz.json") as f:
                json_data = json.load(f)

                # crate fake values that are used more than once
                aws_id = "i-" + "".join(
                    random.choice(
                        ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
                        + list(string.ascii_lowercase)
                    )
                    for _ in range(17)
                )
                env = random.choice(["dev", "prod", "staging"])
                hostname = asset.get("new_hostname")
                provider_unique_id = (
                    f"arn:aws:ec2:us-east-2:123456789123:instance/{aws_id}"
                )
                provider_url = f"https://us-east-2.console.aws.amazon.com/ec2/v2/home?region=us-east-2#InstanceDetails:instanceId={aws_id}"
                tags = f"name={hostname} env={env}"
                ip_list = [asset.get("ip"), asset.get("ipv6")]
                asset_id = str(uuid.uuid4())

                # update main json data with fake values
                json_data["info"]["_type"] = "dev"
                json_data["info"]["cloudPlatform"] = "AWS"
                json_data["info"]["cloudProviderURL"] = provider_url
                json_data["info"]["creationDateTS"] = str(
                    round(time.time() - 10000 * random.choice([5, 6, 7, 8, 9, 10]))
                )
                json_data["info"]["dns"] = f"{hostname}.us-east-2.compute.amazonaws.com"
                json_data["info"]["externalID"] = aws_id
                json_data["info"]["id"] = asset_id
                json_data["info"]["ipv4"] = asset.get("ip")
                json_data["info"]["ipv6"] = asset.get("ipv6")
                json_data["info"]["isEphemeral"] = "true"
                json_data["info"]["isManaged"] = "true"
                json_data["info"]["name"] = hostname
                json_data["info"]["nativeType"] = "virtualMachine"
                json_data["info"]["providerUniqueID"] = provider_unique_id
                json_data["info"]["region"] = "us-east-2"
                json_data["info"]["regionLocation"] = "US"
                json_data["info"]["sizeGB"] = random.choice(["2", "4", "8", "16", "32"])
                json_data["info"]["status"] = "Active"
                json_data["info"]["subscriptionExternalID"] = "123456789123"
                json_data["info"]["tags"] = tags
                json_data["info"]["totalDisks"] = random.choice(
                    ["1", "2", "3", "4", "5"]
                )
                json_data["info"]["type"] = "Server"
                json_data["info"]["updatedAtTS"] = str(round(time.time()))
                json_data["info"]["vCPUs"] = random.choice(["2", "4", "8", "16", "32"])

                # upddate software and vulns with fake values
                json_data["info"]["_software"] = decode(
                    json_data.get("info").get("_software")
                )
                for s in json.loads(json_data["info"]["_software"]):
                    s["id"] = str(uuid.uuid4())
                    s["properties"]["subscriptionExternalId"] = "123456789123"
                    s["properties"][
                        "externalId"
                    ] = f"CloudPlatform/VirtualMachine##{aws_id}"
                    s["name"] = s["name"].replace("app-small", hostname)
                    s["properties"]["name"] = s["properties"]["name"].replace(
                        "app-small", hostname
                    )

                json_data["info"]["_vulnerabilities"] = decode(
                    json_data.get("info").get("_vulnerabilities")
                )
                for v in json.loads(json_data["info"]["_vulnerabilities"]):
                    v["id"] = asset_id
                    v["name"] = hostname
                    v["providerUniqueId"] = provider_unique_id
                    v["cloudProviderURL"] = provider_url
                    v["subscriptionExternalId"] = "123456789123"
                    v["subscriptionId"] = "123456789123"
                    v["tags"] = tags
                    v["ipAddresses"] = ip_list
                    v["imageId"] = str(uuid.uuid4())
                    v["imageExternalId"] = asset.get("ami")
                    v["imageProviderUniqueId"] = asset.get("ami")
                    v["vulnerableAsset"]["id"] = asset_id
                    v["vulnerableAsset"]["name"] = hostname
                    v["vulnerableAsset"]["providerUniqueId"] = provider_unique_id
                    v["vulnerableAsset"]["cloudProviderURL"] = provider_url
                    v["vulnerableAsset"]["subscriptionExternalId"] = "123456789123"
                    v["vulnerableAsset"]["subscriptionId"] = "123456789123"
                    v["vulnerableAsset"]["tags"] = tags

                    if "imageName" in v:
                        del v["imageName"]
                    if "portalUrl" in v:
                        del v["portalUrl"]

                # encode back to base64
                json_data["info"]["_software"] = encode(json_data["info"]["_software"])
                json_data["info"]["_vulnerabilities"] = encode(
                    json_data["info"]["_vulnerabilities"]
                )
                output.append(json_data)

    # write modified results to file for import
    with open(f"integration_wiz.json", "w") as f:
        for l in output:
            f.write(json.dumps(l, separators=(",", ":")) + "\n")
    return True


# this is for integrations that require bulk regex operations to update the data
def fudge_integration_data(asset_cache: list, integration_name: str) -> bool:
    output = []

    for asset in asset_cache:
        # data to use
        raw_task = open(f"./tasks/integration_{integration_name}.json")

        device_map_key = {
            "nessus": NESSUS_DEVICE_MAP,
            "crowdstrike": CROWDSTRIKE_DEVICE_MAP,
            "aws": AWS_DEVICE_MAP,
            "qualys": QUALYS_DEVICE_MAP,
        }

        device_map = device_map_key.get(integration_name, None)

        # skip if the integration doesn't exist in the map
        if device_map:
            # get device type and check if integration supports
            device_type = asset.get("type", None)

            # match CrowdStrike assets more granularly
            os = asset.get("os", None)
            if os and (
                integration_name == "crowdstrike" or integration_name == "qualys"
            ):
                device_type = device_type + "-" + os

            # only create AWS data for CLOUD assets
            network = asset.get("network", None)
            if network == "CLOUD" and integration_name == "aws":
                device_type = f"{device_type}-CLOUD"

            if device_type:

                # check that the integration supports the type
                if device_type in device_map:

                    # check if the integration has values to replace
                    ip_match = check_for_replacements(
                        key="ip", asset_replacements=device_map[device_type]
                    )

                    # replace old MAC addresses and integrations MACs
                    old_macs = asset.get("mac")
                    int_macs = device_map[device_type]["mac"]
                    if old_macs:
                        device_map[device_type]["mac"] = old_macs + "|" + int_macs
                    mac_match = check_for_replacements(
                        key="mac", asset_replacements=device_map[device_type]
                    )
                    hostname_match = check_for_replacements(
                        key="hostname", asset_replacements=device_map[device_type]
                    )
                    username_match = check_for_replacements(
                        key="username", asset_replacements=device_map[device_type]
                    )

                    for line in raw_task:

                        # check if the log is worth working on
                        temp_result = json.loads(line)
                        temp_result["ts"] = current_rz_time()
                        if integration_name == "nessus":
                            result_ip = temp_result.get("info", {}).get("id", None)
                        elif integration_name == "crowdstrike":
                            result_ip = temp_result.get("info", {}).get("localIP", None)
                        elif integration_name == "aws":
                            result_ip = temp_result.get("info", {}).get(
                                "publicIP", None
                            )
                        elif integration_name == "qualys":
                            result_ip = temp_result.get("info", {}).get("host.ip", None)

                        # check if the result is worth updating

                        device_map_ip = device_map[device_type].get("ip")

                        if (
                            temp_result.get("type") == "result"
                            and result_ip == device_map_ip
                        ):
                            # update timestamp
                            temp_result["ts"] = current_rz_time()

                            # integration specific modifications
                            os_info = asset.get("os_full", "").split("-")
                            if integration_name == "qualys":
                                temp_result["info"]["host.id"] = str(uuid.uuid4())
                                temp_result["info"]["id"] = str(uuid.uuid4())
                                temp_result["info"]["host.lastScannedDateTimeTS"] = str(
                                    round(time.time())
                                )
                                temp_result["info"]["host.lastVMScannedDateTS"] = str(
                                    round(time.time())
                                )
                                temp_result["info"]["detection.firstFoundTS"] = str(
                                    round(time.time())
                                )
                                temp_result["info"]["detection.lastFoundTS"] = str(
                                    round(time.time())
                                )
                                if "host.os" in temp_result["info"]:
                                    if len(os_info) > 1:
                                        temp_result["info"]["host.os"] = os_info[0]
                                    else:
                                        temp_result["info"]["host.os"] = "Linux"

                                temp_result["info"]["_detections"] = decode(
                                    temp_result["info"]["_detections"]
                                )
                            if integration_name == "nessus":
                                temp_result["info"]["lastSeenTS"] = str(
                                    round(time.time())
                                )
                                temp_result["info"]["firstSeenTS"] = str(
                                    round(time.time())
                                )
                                temp_result["info"]["lastScanTimeTS"] = str(
                                    round(time.time())
                                )
                                temp_result["info"]["_vulnerabilities"] = decode(
                                    temp_result["info"]["_vulnerabilities"]
                                )

                                if "operatingSystems" in temp_result["info"]:
                                    if len(os_info) > 1:
                                        temp_result["info"]["operatingSystems"] = (
                                            os_info[0]
                                        )
                                    else:
                                        temp_result["info"][
                                            "operatingSystems"
                                        ] = "Linux"

                                if "systemTypes" in temp_result["info"]:
                                    temp_result["info"][
                                        "systemTypes"
                                    ] = device_type.lower().capitalize()
                                new_mac = asset.get("new_mac")
                                ip = asset.get("ip")
                                temp_result["info"]["macAddresses"] = new_mac
                                temp_result["info"]["macPairs"] = f"{ip}={new_mac}"

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
                                    round(
                                        time.time()
                                        - 10000 * random.choice([5, 6, 7, 8, 9, 10])
                                    )
                                )
                                temp_result["info"]["lastInteractiveTSS"] = str(
                                    round(
                                        time.time()
                                        - 10000 * random.choice([1, 2, 3, 4, 5])
                                    )
                                )
                                temp_result["info"]["lastInteractiveTS"] = str(
                                    round(
                                        time.time()
                                        - 10000 * random.choice([1, 2, 3, 4, 5])
                                    )
                                )
                                temp_result["info"]["lastLoginTS"] = str(
                                    round(
                                        time.time()
                                        - 10000 * random.choice([1, 2, 3, 4, 5])
                                    )
                                )
                                temp_result["info"]["agentLocalTime"] = (
                                    str(
                                        datetime.datetime.now().strftime(
                                            "%Y-%m-%dT%H:%M:%S"
                                        )
                                    )
                                    + "Z"
                                )
                                temp_result["info"]["lastSeen"] = (
                                    str(
                                        datetime.datetime.now().strftime(
                                            "%Y-%m-%dT%H:%M:%S"
                                        )
                                    )
                                    + "Z"
                                )

                                # Windows Server 2019 | Windows 11 | Windows Server 2016 | etc
                                if len(os_info) == 3:
                                    temp_result["info"]["osVersion"] = os_info[2]
                                elif len(os_info) == 2:
                                    temp_result["info"]["osVersion"] = os_info[1]

                                if len(os_info) == 3:
                                    temp_result["info"]["systemProductName"] = (
                                        os_info[1] + " " + os_info[2]
                                    )
                                elif len(os_info) == 2:
                                    temp_result["info"]["systemProductName"] = "Windows"
                                else:
                                    temp_result["info"]["systemProductName"] = os_info[
                                        0
                                    ]

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
                                    temp_result["info"]["systemManufacturer"] = (
                                        random.choice(["Dell", "SUSE", "HP", "IBM"])
                                    )
                                    temp_result["info"]["biosManufacturer"] = "Linux"

                                # get rid of AWS / VMWare stuff
                                temp_result["info"][
                                    "biosVersion"
                                ] = "RZ-CUSTOM-BIOS-v1.0.0"

                                # replace device_id values
                                temp_result["info"]["deviceID"] = asset.get(
                                    "device_id", str(uuid.uuid4())
                                )
                                temp_result["info"]["cid"] = asset.get(
                                    "device_id", str(uuid.uuid4())
                                )

                            if integration_name == "aws":
                                temp_result["info"]["accountEmail"] = "admin@rzcorp.com"
                                temp_result["info"]["keyName"] = "admin@rzcorp.com"
                                temp_result["info"]["accountID"] = "RZ2024"
                                temp_result["info"]["accountName"] = "RUNZERO"
                                temp_result["info"]["id"] = str(uuid.uuid4())
                                temp_result["info"]["imageID"] = asset.get("ami", None)
                                temp_result["info"]["instanceID"] = "i-" + "".join(
                                    random.choice(
                                        ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
                                        + list(string.ascii_lowercase)
                                    )
                                    for _ in range(17)
                                )
                                temp_result["info"]["tags"] = "region=US2"
                                temp_result["info"]["instanceType"] = random.choice(
                                    AWS_DEVICE_TYPES
                                )
                                new_ip = asset.get("ip")
                                new_aws_ip = semi_random_ipv4(
                                    old_ip="172.31.16.221", new_ip=new_ip
                                )
                                asset["ip"] = new_aws_ip
                                temp_result["info"]["ipv4"] = f"{new_aws_ip}\t{new_ip}"
                                temp_result["info"]["privateIP"] = new_aws_ip
                                new_ipv6 = random_ipv6()
                                asset["ipv6"] = new_ipv6
                                temp_result["info"]["ipv6"] = new_ipv6

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

                            # nessus random hostnames
                            nessus_hostnames_match = re.compile(
                                "google-home.lan|tesla_model_s.lan|46d8d572f529283b8ed7c7565033867b.lan|15aa01ac34180re1.lan|esp_a93bf6.lan|esp_003d1d.lan|simplisafe_basestation.lan|teslawallconnector_179ace.lan",
                                re.IGNORECASE,
                            )

                            result = regex_bulk_sub(
                                match=nessus_hostnames_match,
                                new_val=asset.get("new_hostname", None),
                                result=result,
                            )

                            # reencode for upload
                            final_result = json.loads(result)
                            if integration_name == "qualys":
                                final_result["info"]["_detections"] = encode(
                                    final_result["info"]["_detections"]
                                )
                            if integration_name == "nessus":
                                # able to add vulns as needed
                                modifiable_vulns = json.loads(
                                    temp_result["info"]["_vulnerabilities"]
                                )
                                for i, v in enumerate(modifiable_vulns):
                                    if "output" in v:
                                        if "Remote operating system" in v["output"]:
                                            del modifiable_vulns[i]
                                        if "DHCP server" in v["output"]:
                                            del modifiable_vulns[i]
                                    if "asset" in v and "ipv4" in v["asset"]:
                                        v["asset"]["ipv4"] = asset.get("ip", None)

                                final_result["info"]["_vulnerabilities"] = json.dumps(
                                    modifiable_vulns
                                )
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
    ## this verifies the MAC randomizer doesn't accidentally create an already used MAC address
    retry = True
    while retry:
        mac_match = check_for_replacements("mac", asset_info[random_asset_type])
        mac = asset_info[random_asset_type]["mac"] if mac_match else None
        new_mac = (
            semi_random_mac(mac=mac)
            if mac_match
            else semi_random_mac(mac="19:3c:1f:78:f2:cf")
        )

        if mac != new_mac:
            retry = False

    # ensure all assets have an ARP entry with a MAC address
    OUTPUT.append(
        {
            "type": "result",
            "ts": current_rz_time(),
            "host": ip,
            "port": "0",
            "proto": "arp",
            "probe": "arp",
            "info": {
                "arp.mac": new_mac,
                "source": "arp",
            },
        }
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

            if asset_type in ["SWITCH", "ROUTER", "SERVER"]:
                ROUTER_SWITCH_SERVER_MAC_CACHE.append({"ip": ip, "mac": new_mac})

            if "snmp.vlans" in temp_result["info"]:
                temp_result["info"]["snmp.vlans"] = "\t".join(
                    [
                        f"RZ1=RZ-{network}",
                        f"RZ2=RZ-{network}-GUEST",
                        f"RZ3=RZ-{network}-ADMIN",
                    ]
                )

            if "arp.mac" in temp_result["info"]:
                temp_result["info"]["arp.mac"] = new_mac

            if "snmp.sysName" in temp_result["info"]:
                temp_result["info"]["snmp.sysName"] = new_hostname

            if "snmp.serialNumbers" in temp_result["info"]:
                temp_result["info"]["snmp.serialNumbers"] = random_serial_number()

            if "snmp.engineID.mac" in temp_result["info"]:
                temp_result["info"]["snmp.engineID.mac"] = new_mac

            if "ipv4.traceroute" in temp_result["info"]:
                temp_result["info"]["ipv4.traceroute"] = generate_traceroute_str(ip)

            if "snmp.engineID.mac" in temp_result["info"]:
                mac_raw = new_mac.replace(":", "")
                temp_result["info"]["snmp.engineID.raw"] = f"00000000{mac_raw}60001"
                temp_result["info"]["snmp.engineID.mac"] = new_mac

            if "snmp.engineID.raw" in temp_result["info"]:
                temp_result["info"]["snmp.engineID.raw"] = new_mac

            if "tls.supportedVersionNames" in temp_result["info"]:
                _, cert = generate_self_signed_cert(
                    hostname=new_hostname, valid_days=random.randint(1, 365)
                )
                cert_details = get_cert_details(cert)
                for k, v in cert_details.items():
                    if k in temp_result["info"]:
                        temp_result["info"][k] = v

            if "tls.serial" in temp_result["info"]:
                temp_result["info"]["tls.serial"] = random_serial_number()

            snmp_macs = [] if new_mac == None else [new_mac]

            if len(ROUTER_SWITCH_SERVER_MAC_CACHE) > 0 and asset_type in [
                "SWITCH",
                "ROUTER",
            ]:
                snmp_macs.extend([semi_random_mac(mac=new_mac) for _ in range(2)])
                existing_macs = []
                loop_len = (
                    len(ROUTER_SWITCH_SERVER_MAC_CACHE)
                    if len(ROUTER_SWITCH_SERVER_MAC_CACHE) < 10
                    else 10
                )

                for _ in range(loop_len):
                    temp_mac = random.choice(ROUTER_SWITCH_SERVER_MAC_CACHE)["mac"]
                    if temp_mac not in existing_macs:
                        existing_macs.append(temp_mac)

                snmp_macs.extend(existing_macs)

            if "snmp.interfaceMacs" in temp_result["info"]:
                temp_result["info"]["snmp.interfaceMacs"] = new_mac

            if "snmp.macs.ports" in temp_result["info"]:
                mac_ports = [
                    f"1/g{i}={snmp_macs[i]}" for i in range(0, len(snmp_macs) - 1)
                ]
                temp_result["info"]["snmp.macs.ports"] = "\t".join(mac_ports)

            if "snmp.interfaceNames" in temp_result["info"]:
                names = [f"1/g{i}" for i in range(0, len(snmp_macs) - 1)]
                temp_result["info"]["snmp.interfaceNames"] = "\t".join(names)

            if "snmp.arpcache" in temp_result["info"]:
                arp_cache = []
                for _, asset in enumerate(ROUTER_SWITCH_SERVER_MAC_CACHE):
                    arp_ip = asset.get("ip")
                    arp_mac = asset.get("mac")
                    arp_cache.append(f"{arp_ip}={arp_mac}")
                temp_result["info"]["snmp.arpcache"] = "\t".join(arp_cache)

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
        "network": network,
    }

    return asset_info[random_asset_type] | new_asset_info


def handle_integration(integration_name, asset_cache):
    if integration_name in ["crowdstrike", "nessus", "aws", "qualys"]:
        return fudge_integration_data(
            asset_cache=(
                asset_cache
                if integration_name == "aws"
                else remove_random_assets(asset_cache)
            ),
            integration_name=integration_name,
        )
    elif integration_name == "azuread":
        return fudge_azuread_data(remove_random_assets(asset_cache))
    elif integration_name == "jamf":
        return fudge_jamf_data(remove_random_assets(asset_cache))
    elif integration_name == "wiz":
        return fudge_wiz_data(asset_cache)
    else:
        print(f"WARNING - Unknown integration: {integration_name}")
        return False


def create_assets(
    subnet_start: int, subnet_finish: int, ip_start: int, ip_finish: int, network: str
):
    asset_cache = []

    for subnet in range(subnet_start, subnet_finish):
        for ip in range(ip_start, ip_finish):
            # Define the IP address based on the network type
            if network == "CLOUD":
                final_ip = f"23.20.{subnet}.{ip}"
            elif network == "DMZ":
                final_ip = f"198.51.{subnet}.{ip}"  # Use a public IP range different from the 23.x.x.x range
            else:
                final_ip = f"10.0.{subnet}.{ip}"

            asset = None

            # BACNET includes routers, OT, and BACnet
            if network == "BACNET":
                if ip == 1:
                    asset = fudge_scan_data(
                        asset_info=ROUTING_ASSETS,
                        ip=final_ip,
                        network=network,
                    )
                else:
                    asset = fudge_scan_data(
                        asset_info=OT_DEVICES | BACNET_ASSETS | FINDINGS_ASSETS,
                        ip=final_ip,
                        network=network,
                    )

            # Cloud is just servers
            if network == "CLOUD":
                asset = fudge_scan_data(
                    asset_info=SERVER_ASSETS, ip=final_ip, network=network
                )

            # HQ and Datacenters include routers, firewalls, a few IOT/OT devices, and mostly servers and end user devices
            if network in ["HQ", "DC"]:
                if ip == 1:
                    asset = fudge_scan_data(
                        asset_info=ROUTING_ASSETS,
                        ip=final_ip,
                        network=network,
                    )
                elif ip == 2:
                    asset = fudge_scan_data(
                        asset_info=FIREWALL_DEVICES,
                        ip=final_ip,
                        network=network,
                    )
                elif ip % 7 == 0:
                    asset = fudge_scan_data(
                        asset_info=IOT_DEVICES | OT_DEVICES,
                        ip=final_ip,
                        network=network,
                    )
                else:
                    asset = fudge_scan_data(
                        asset_info=END_USER_ASSETS | SERVER_ASSETS | FINDINGS_ASSETS,
                        ip=final_ip,
                        network=network,
                    )

            # DMZ is similar to CLOUD but uses a different public IP range.
            if network == "DMZ":
                asset = fudge_scan_data(
                    asset_info=SERVER_ASSETS, ip=final_ip, network=network
                )

            if asset:
                asset_cache.append(asset)

    return asset_cache

def main():
    # create new tasks for demo data if enabled
    # python3 demo_data.py --create
    if args.create:
        print("STARTING - asset creation")
        OUTPUT.append(
            {
                "type": "config",
                "ts": current_rz_time(),
                "probes": [
                    "arp",
                    "aws-instances",
                    "bacnet",
                    "censys",
                    "crestron",
                    "dns",
                    "dtls",
                    "echo",
                    "ike",
                    "ipmi",
                    "l2t",
                    "mdns",
                    "memcache",
                    "mssql",
                    "natpmp",
                    "netbios",
                    "ntp",
                    "openvpn",
                    "pca",
                    "rdns",
                    "rpcbind",
                    "sip",
                    "snmp",
                    "ssdp",
                    "ssh",
                    "syn",
                    "tftp",
                    "ubnt",
                    "vmware",
                    "wlan-list",
                    "wsd",
                ],
                "addresses": [],
                "networks": [
                    "10.0.0.0/24",
                    "10.0.1.0/24",
                    "10.0.2.0/24",
                    "10.0.3.0/24",
                    "10.0.4.0/24",
                    "10.0.5.0/24",
                    "10.0.6.0/24",
                    "10.0.7.0/24",
                    "10.0.8.0/24",
                    "10.0.9.0/24",
                    "10.0.10.0/24",
                    "10.0.11.0/24",
                    "10.0.12.0/24",
                    "10.0.13.0/24",
                    "10.0.14.0/24",
                    "10.0.15.0/24",
                    "10.0.16.0/24",
                    "10.0.17.0/24",
                    "10.0.18.0/24",
                    "10.0.19.0/24",
                    "10.0.20.0/24",
                    "23.20.0.0/24",
                    "23.20.1.0/24",
                    "23.20.2.0/24",
                    "23.20.3.0/24",
                    "23.20.4.0/24",
                    "23.20.5.0/24",
                    "198.51.0.0/16",
                ],
                "params": {
                    "arp-fast": "false",
                    "aws-instances-delete-stale": "false",
                    "aws-instances-exclude-unknown": "false",
                    "aws-instances-include-stopped": "false",
                    "aws-instances-service-options": "defaults",
                    "aws-instances-site-per-account": "false",
                    "aws-instances-site-per-vpc": "false",
                    "bacnet-ports": "46808,47808,48808",
                    "censys-exclude-unknown": "false",
                    "censys-mode": "targets",
                    "censys-query": "",
                    "clock-offset": "0",
                    "crestron-port": "41794",
                    "dns-disable-google-myaddr": "false",
                    "dns-disable-meraki-detection": "false",
                    "dns-port": "53",
                    "dns-resolve-name": "www.google.com",
                    "dns-trace-domain": "helper.rumble.network",
                    "dtls-ports": "443,3391,4433,5246,5349,5684",
                    "echo-report-errors": "false",
                    "excludes": "192.168.168.0/24",
                    "host-ping-probes": "arp,echo,syn,connect,netbios,snmp,ntp,sunrpc,ike,openvpn,mdns",
                    "ike-port": "500",
                    "ipmi-port": "623",
                    "l2t-port": "2228",
                    "max-attempts": "3",
                    "max-group-size": "4096",
                    "max-host-rate": "40",
                    "max-sockets": "2048",
                    "max-ttl": "255",
                    "mdns-port": "5353",
                    "memcache-port": "11211",
                    "mssql-port": "1434",
                    "nameservers": "",
                    "natpmp-port": "5351",
                    "netbios-port": "137",
                    "nopcap": "false",
                    "ntp-port": "123",
                    "openvpn-ports": "1194",
                    "passes": "1",
                    "pca-port": "5632",
                    "ping-only": "false",
                    "probes": "arp,aws-instances,bacnet,censys,crestron,dns,dtls,echo,ike,ipmi,l2t,mdns,memcache,mssql,natpmp,netbios,ntp,openvpn,pca,rdns,rpcbind,sip,snmp,ssdp,ssh,syn,connect,tftp,ubnt,vmware,wlan-list,wsd",
                    "rate": "1000",
                    "rdns-max-concurrent": "64",
                    "rdns-timeout": "3",
                    "rpcbind-port": "111",
                    "rpcbind-port-nfs": "2049",
                    "scan-mode": "host",
                    "scanner-name": "main",
                    "screenshots": "true",
                    "sip-port": "5060",
                    "skip-broadcast": "true",
                    "snmp-disable-bulk": "false",
                    "snmp-max-repetitions": "16",
                    "snmp-max-retries": "1",
                    "snmp-poll-interval": "300",
                    "snmp-port": "161",
                    "snmp-timeout": "5",
                    "snmp-v3-context": "",
                    "snmp-walk-timeout": "60",
                    "ssdp-port": "1900",
                    "ssh-fingerprint": "true",
                    "ssh-fingerprint-username": "_STATUS_",
                    "subnet-ping-net-size": "256",
                    "subnet-ping-probes": "arp,echo,syn,connect,netbios,snmp,ntp,sunrpc,ike,openvpn,mdns",
                    "subnet-ping-sample-rate": "3",
                    "syn-disable-bogus-filter": "false",
                    "syn-forwarding-check": "true",
                    "syn-forwarding-check-target": "13.248.161.247",
                    "syn-max-retries": "2",
                    "syn-report-resets": "true",
                    "syn-reset-sessions": "true",
                    "syn-reset-sessions-delay": "0",
                    "syn-reset-sessions-limit": "50",
                    "syn-traceroute": "true",
                    "syn-udp-trace-port": "65535",
                    "tcp-excludes": "",
                    "tcp-ports": "3306,8834,2083,2604,8028,8180,9443,10008,47002,21,1582,5061,5985,8883,8902,9300,264,512,5521,5903,17783,50013,993,2049,8800,9091,15671,17185,25000,5989,8000,2638,8686,42,1755,7879,27888,445,6661,9200,17,3033,6262,7579,50021,2100,5906,8471,8488,4443,7778,10259,28017,53,1091,8006,8020,8205,65535,5060,5353,1433,4949,6101,8090,9401,9418,500,1098,10162,10202,44334,65002,3050,6082,8445,8181,8888,34205,40007,1723,7144,5902,9593,32913,80,3001,8850,9000,41080,50070,61616,123,4343,6443,37,4322,6001,26000,5905,9001,8095,1801,3900,1521,5347,5901,9090,1030,1241,22222,38292,3200,16992,998,8023,4366,7902,8787,49,1533,5405,7070,61614,1514,2362,5907,8010,11333,17781,37777,3780,5093,17777,55580,9080,44818,1100,3389,2224,7210,9,623,111,19810,2181,110,280,6502,14330,37892,82,902,17791,32764,5275,8089,9855,46823,873,3268,2023,5988,6503,8081,9084,9152,636,903,5666,6504,9390,10250,1260,3071,5560,7510,7787,13838,28784,54922,102,137,7801,10001,17782,135,2103,1468,9002,7580,10050,139,4659,2375,3460,4092,4567,8172,9060,119,1000,50051,6106,12203,13364,20222,3502,5250,1199,8182,43,1035,50090,23,3128,1443,8903,8300,25565,79,1129,5631,20031,444,689,10628,4950,8127,4730,4848,7770,8503,10000,15672,1024,2381,13778,16993,17798,9809,10080,2380,5038,5040,1581,1611,40317,3000,28222,2376,2443,3300,3500,7777,515,1604,8099,25672,2074,6070,5351,6514,27000,34962,52311,69,587,2809,5800,7080,10203,20101,50000,912,1494,62514,5400,17775,26122,48899,1,1090,6050,20034,41025,52302,2533,3351,5683,6000,8889,1102,4369,5671,5672,6379,8082,12401,30000,1440,3628,3311,6161,6905,8444,9100,85,717,4433,4840,5355,6988,8880,9092,1220,3790,38102,54921,62078,9471,10255,10616,5392,7800,143,8088,10257,11234,6542,8443,4353,8008,9042,25025,402,2207,6112,1900,5938,540,1300,20010,20111,5555,8001,27018,54923,524,2002,37891,8009,20171,9099,9391,32844,921,7000,2525,2601,5601,17472,664,1128,7077,1270,5986,23791,2000,7001,47001,179,8083,4368,7547,47290,3299,3312,5000,8871,161,4444,34963,55553,442,9111,6667,31099,3269,5900,1434,1811,8098,10098,10443,105,1211,19300,33060,44343,513,1103,5432,5007,8030,13,1083,5814,5920,6556,8531,9081,9594,2105,5498,2947,4000,13500,88,1158,3872,11099,27019,109,1311,5911,5984,8400,8812,17778,38008,1099,1101,113,1830,4987,8333,9495,37890,7,22,5908,8649,17200,3037,5037,17784,2379,12221,5433,7002,9524,34964,19,2082,5168,34443,83,2222,2121,8222,8901,4445,5247,523,1352,5580,8012,222,1883,384,12174,5051,5909,8086,8500,830,1610,5222,8123,8983,20293,57772,1080,3220,7676,2323,2598,3260,41523,70,771,12379,910,12345,7373,18881,7474,8087,54321,631,7443,7700,8080,8890,2068,2967,5520,45230,23943,995,8545,6405,6660,7100,9530,18264,465,6060,9160,9380,1089,4679,11211,548,783,4365,16102,17790,20000,23472,49152,743,3057,443,27017,9999,888,8303,1583,3217,3273,8100,81,84,8161,17776,51443,2199,3817,9527,27080,46824,4786,5904,19888,3871,9440,15200,41524,8003,12397,617,2021,5022,7021,10051,37718,25,502,5910,6002,6080,8530,8899,11000,1530,3083,31001,705,3632,5001,50121,389,554,9595,9600,38080,1234,5632,7071,7181,8014,38010,990,3003,5554,16443,407,3690",
                    "tcp-skip-protocol": "false",
                    "tftp-ports": "69",
                    "tos": "0",
                    "ubnt-port": "10001",
                    "verbose": "true",
                    "very-verbose": "false",
                    "wlan-list-poll-interval": "300",
                    "wsd-port": "3702",
                },
                "scan_targets": {
                    "networks": [
                        "10.0.0.0/24",
                        "10.0.1.0/24",
                        "10.0.2.0/24",
                        "10.0.3.0/24",
                        "10.0.4.0/24",
                        "10.0.5.0/24",
                        "10.0.6.0/24",
                        "10.0.7.0/24",
                        "10.0.8.0/24",
                        "10.0.9.0/24",
                        "10.0.10.0/24",
                        "10.0.11.0/24",
                        "10.0.12.0/24",
                        "10.0.13.0/24",
                        "10.0.14.0/24",
                        "10.0.15.0/24",
                        "10.0.16.0/24",
                        "10.0.17.0/24",
                        "10.0.18.0/24",
                        "10.0.19.0/24",
                        "10.0.20.0/24",
                        "23.20.0.0/24",
                        "23.20.1.0/24",
                        "23.20.2.0/24",
                        "23.20.3.0/24",
                        "23.20.4.0/24",
                        "23.20.5.0/24",
                        "198.51.0.0/16",
                    ],
                    "enable_dns": True,
                    "enable_ip6": True,
                    "enable_zero_mask": False,
                    "enable_ip6_mask": False,
                    "enable_loopback": False,
                    "enable_multicast": False,
                    "inputs": [
                        "10.0.0.0/24",
                        "10.0.1.0/24",
                        "10.0.2.0/24",
                        "10.0.3.0/24",
                        "10.0.4.0/24",
                        "10.0.5.0/24",
                        "10.0.6.0/24",
                        "10.0.7.0/24",
                        "10.0.8.0/24",
                        "10.0.9.0/24",
                        "10.0.10.0/24",
                        "10.0.11.0/24",
                        "10.0.12.0/24",
                        "10.0.13.0/24",
                        "10.0.14.0/24",
                        "10.0.15.0/24",
                        "10.0.16.0/24",
                        "10.0.17.0/24",
                        "10.0.18.0/24",
                        "10.0.19.0/24",
                        "10.0.20.0/24",
                        "23.20.0.0/24",
                        "23.20.1.0/24",
                        "23.20.2.0/24",
                        "23.20.3.0/24",
                        "23.20.4.0/24",
                        "23.20.5.0/24",
                    ],
                    "dns_timeout": 2000000000,
                    "concurrency": 40,
                    "hostnames": [],
                },
                "seed_targets": {
                    "networks": [
                        "10.0.0.0/24",
                        "10.0.1.0/24",
                        "10.0.2.0/24",
                        "10.0.3.0/24",
                        "10.0.4.0/24",
                        "10.0.5.0/24",
                        "10.0.6.0/24",
                        "10.0.7.0/24",
                        "10.0.8.0/24",
                        "10.0.9.0/24",
                        "10.0.10.0/24",
                        "10.0.11.0/24",
                        "10.0.12.0/24",
                        "10.0.13.0/24",
                        "10.0.14.0/24",
                        "10.0.15.0/24",
                        "10.0.16.0/24",
                        "10.0.17.0/24",
                        "10.0.18.0/24",
                        "10.0.19.0/24",
                        "10.0.20.0/24",
                        "23.20.0.0/24",
                        "23.20.1.0/24",
                        "23.20.2.0/24",
                        "23.20.3.0/24",
                        "23.20.4.0/24",
                        "23.20.5.0/24",
                        "198.51.0.0/16",
                    ],
                    "enable_dns": True,
                    "enable_ip6": True,
                    "enable_zero_mask": False,
                    "enable_ip6_mask": False,
                    "enable_loopback": False,
                    "enable_multicast": False,
                    "inputs": [
                        "10.0.0.0/24",
                        "10.0.1.0/24",
                        "10.0.2.0/24",
                        "10.0.3.0/24",
                        "10.0.4.0/24",
                        "10.0.5.0/24",
                        "10.0.6.0/24",
                        "10.0.7.0/24",
                        "10.0.8.0/24",
                        "10.0.9.0/24",
                        "10.0.10.0/24",
                        "10.0.11.0/24",
                        "10.0.12.0/24",
                        "10.0.13.0/24",
                        "10.0.14.0/24",
                        "10.0.15.0/24",
                        "10.0.16.0/24",
                        "10.0.17.0/24",
                        "10.0.18.0/24",
                        "10.0.19.0/24",
                        "10.0.20.0/24",
                        "23.20.0.0/24",
                        "23.20.1.0/24",
                        "23.20.2.0/24",
                        "23.20.3.0/24",
                        "23.20.4.0/24",
                        "23.20.5.0/24",
                        "198.51.0.0/16",
                    ],
                    "dns_timeout": 2000000000,
                    "concurrency": 40,
                    "hostnames": [],
                },
                "disc_targets": {
                    "networks": [],
                    "enable_dns": True,
                    "enable_ip6": True,
                    "enable_zero_mask": False,
                    "enable_ip6_mask": False,
                    "enable_loopback": False,
                    "enable_multicast": False,
                    "dns_timeout": 2000000000,
                    "concurrency": 40,
                    "hostnames": [],
                },
                "version": "4.0.240607.0 (build 20240607195406) [da7d44913ffb8b6f9d39f7e7700122613e4a4e96]",
            }
        )

        # Parallelize asset creation for the different subnets
        create_jobs = [
            (0, 10, 1, args.assets_per_subnet + 1, "HQ"),
            (10, 11, 1, args.assets_per_subnet + 1, "BACNET"),
            (11, 20, 1, args.assets_per_subnet + 1, "DC"),
            (20, 21, 1, args.assets_per_subnet + 1, "BACNET"),
            (25, 30, 1, args.assets_per_subnet + 1, "DMZ"),
            (0, 5, 1, args.assets_per_subnet + 1, "CLOUD"),
        ]

        all_created_assets = []  

        with ThreadPoolExecutor() as executor:
            future_map = {
                executor.submit(create_assets, *job_args): job_args
                for job_args in create_jobs
            }

            # as_completed yields futures as they finish
            for future in as_completed(future_map):
                net_info = future_map[future]  # which (subnet_start, etc) we used
                try:
                    assets = future.result()
                    all_created_assets.extend(assets)
                    print(f"SUCCESS - created {len(assets)} assets for {net_info}")
                except Exception as exc:
                    print(f"FAILED - create_assets for {net_info} with error {exc}")

        # Now all asset generation is done, combine them
        asset_cache = all_created_assets

        with open("scan_output.json", "w") as scan_output:
            for entry in OUTPUT:
                scan_output.write(json.dumps(entry, separators=(",", ":")) + "\n")
        print("SUCCESS - created task for rz scan")

        # Parallelize integration tasks creation
        integrations = [
            "crowdstrike",
            "nessus",
            "aws",
            "azuread",
            "jamf",
            "qualys",
            "wiz",
        ]
        with ThreadPoolExecutor() as executor:
            future_integrations = {
                executor.submit(
                    handle_integration,  
                    integration,
                    asset_cache,
                ): integration
                for integration in integrations
            }
            for future in as_completed(future_integrations):
                name = future_integrations[future]
                try:
                    success = future.result()
                    if success:
                        print(f"SUCCESS - created task for {name}")
                    else:
                        print(f"FAILURE - on create task for {name}")
                except Exception as exc:
                    print(f"FAILED - {name} with error {exc}")

    # delete existing assets if enabled
    # python3 demo_data.py --delete
    if args.delete:
        # export current assets
        export_url = RUNZERO_BASE_URL + "/export/org/assets.json"
        headers = {"Authorization": f"Bearer {RUNZERO_ORG_TOKEN}"}
        params = {"search": f"site:{RUNZERO_SITE_ID}", "fields": "id"}
        resp = requests.get(url=export_url, headers=headers, params=params)

        # create list of assets to delete
        asset_list = [x["id"] for x in resp.json()]
        if len(asset_list) > 0:
            print("STARTING - asset deletion")
            delete_url = RUNZERO_BASE_URL + "/org/assets/bulk/delete"
            delete = requests.delete(
                url=delete_url,
                headers=headers,
                json={"asset_ids": asset_list},
                params={"_oid": RUNZERO_ORG_ID},
            )
            # verify deleted
            if delete.status_code == 204:
                print("IN PROGRESS - runZero is deleting the assets")
                time.sleep(10)
                deleted = False
                # wait for deletion to finish if not done
                while not deleted:
                    resp = requests.get(url=export_url, headers=headers, params=params)
                    if len(resp.json()) == 0:
                        deleted = True
                        print("SUCCESS - all assets deleted")
                    else:
                        time.sleep(5)
                        print(
                            "WAITING - still deleting assets. Waiting 5 seconds to check again. Current asset count:",
                            len(resp.json()),
                        )
        else:
            print("SUCCESS - no assets to delete")

    # upload task(s) to rz if enabled
    # python3 demo_data.py --upload
    if args.upload:
        print("STARTING - uploading tasks to runZero")
        for filename in [
            "scan_output.json",
            "integration_crowdstrike.json",
            "integration_nessus.json",
            "integration_aws.json",
            "integration_azuread.json",
            "integration_jamf.json",
            "integration_qualys.json",
            "integration_wiz.json",
            "scan_output.json",
        ]:
            last_task_id = "d8781eaf-b98c-4013-8d8c-5d2a424026ac"
            gzip_upload = gzip.compress(open(filename, "rb").read())
            upload_url = RUNZERO_BASE_URL + f"/org/sites/{RUNZERO_SITE_ID}/import"
            friendly_name_map = {
                "scan_output.json": "runZero Scan",
                "integration_crowdstrike.json": "CrowdStrike Integration",
                "integration_nessus.json": "Nessus Integration",
                "integration_aws.json": "AWS Integration",
                "integration_azuread.json": "Azure AD Integration",
                "integration_jamf.json": "Jamf Integration",
                "integration_qualys.json": "Qualys Integration",
                "integration_wiz.json": "Wiz Integration",
            }
            params = {
                "_oid": RUNZERO_ORG_ID,
                "name": friendly_name_map.get(filename, "runZero Scan"),
            }
            headers = {"Authorization": f"Bearer {RUNZERO_ORG_TOKEN}"}
            resp = requests.put(
                url=upload_url, headers=headers, params=params, data=gzip_upload
            )
            if resp.status_code == 200:
                last_task_id = resp.json()["id"]
                print("SUCCESS - uploaded", filename)

        if args.compress:
            # create compressed version as well
            os.system(f"gzip {filename} -k -f")
            print(f"SUCCESS - compressed {filename} to {filename}.gz")

        if args.verify and last_task_id:
            wait = True
            while wait:
                task_status = requests.get(
                    url=RUNZERO_BASE_URL + f"/org/tasks/{last_task_id}",
                    headers={"Authorization": f"Bearer {RUNZERO_ORG_TOKEN}"},
                )
                if task_status.status_code == 200:
                    status = task_status.json().get("status", None)
                    if status == "processed":
                        print("SUCCESS - task is processed")
                        wait = False
                    else:
                        print("IN PROGRESS - waiting for last task to be processed")
                        time.sleep(10)

            headers = {"Authorization": f"Bearer {RUNZERO_ORG_TOKEN}"}

            # check for overlapping MACs
            params = {
                "search": f"site:{RUNZERO_SITE_ID} mac_overlap:t",
                "fields": "os,macs,names",
            }
            mac_overlaps = requests.get(
                url=RUNZERO_BASE_URL + "/export/org/assets.json",
                headers=headers,
                params=params,
            )
            macs = {}
            for a in mac_overlaps.json():
                for mac in a["macs"]:
                    if mac in macs:
                        macs[mac]["count"] += 1
                        macs[mac]["os"] = macs[mac]["os"] + "," + a["os"]
                        new_names = a["names"]
                        macs[mac]["names"] = macs[mac]["names"] + new_names
                    else:
                        macs[mac] = {"count": 1, "os": a["os"], "names": a["names"]}
            for dup in macs:
                if macs[dup].get("count") > 1:
                    print(dup)
                    print(macs[dup])


if __name__ == "__main__":
    main()
