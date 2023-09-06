import requests
import time
import os

# DO NOT TOUCH
RUNZERO_EXPORT_TOKEN = os.environ["RUNZERO_EXPORT_TOKEN"]
EXPORT_HEADERS = {"Authorization": f"Bearer {RUNZERO_EXPORT_TOKEN}"}
RUNZERO_ORG_TOKEN = os.environ["RUNZERO_ORG_TOKEN"]
ORG_HEADERS = {"Authorization": f"Bearer {RUNZERO_ORG_TOKEN}"}
BASE_URL = "https://console.runZero.com/api/v1.0"

# UPDATE
IP_EXISTS = "ADD ME"  # using an IP that exsits to verify the search works
IP_MISSING = (
    "ADD ME"  # using an IP that doesn"t exist to verify the scan + search works
)
SITE_ID = "ADD UUID"  # site you want the asset associated with (UUID)
EXPLORER_ID = "ADD UUID"  # explorer you want to run the scan if needed


def handle_missing_ip(ip: str):
    url = BASE_URL + f"/org/sites/{SITE_ID}/scan"
    payload = {
        "targets": ip,
        "scan-name": f"Scan {ip} in automated script",
        "scan-description": f"Scan {ip} in automated script",
        "scan-frequency": "once",
        "scan-start": "0",
        "scan-tags": "type=AUTOMATED",
        "scan-grace-period": "0",
        "agent": EXPLORER_ID,
        "rate": "10000",
        "max-host-rate": "100",
        "passes": "3",
        "max-attempts": "3",
        "max-sockets": "500",
        "max-group-size": "4096",
        "max-ttl": "255",
        "tcp-ports": "defaults",
        "screenshots": "true",
        "nameservers": "8.8.8.8",
        "probes": "arp,bacnet,connect,dns,echo,ike,ipmi,mdns,memcache,mssql,natpmp,netbios,pca,rdns,rpcbind,sip,snmp,ssdp,syn,ubnt,wlan-list,wsd",
    }
    data = requests.put(url, headers=ORG_HEADERS, json=payload)
    task_id = data.json()["id"]
    task_running = True
    while task_running:
        status_url = BASE_URL + f"/org/tasks/{task_id}"
        task_data = requests.get(status_url, headers=ORG_HEADERS)
        status = task_data.json()["status"]
        if status == "processed":
            task_running = False
        else:
            print(
                f"Current scan status: {status.upper()}. Checking status again in 15 seconds."
            )
            time.sleep(15)
    return task_data.json()


def search_ip(ip: str):
    url = BASE_URL + "/export/org/assets.json?"
    data = requests.get(url, headers=EXPORT_HEADERS,
                        params={"search": f"address:{ip}"})
    if len(data.json()) > 0:
        return data.json()
    else:
        data = handle_missing_ip(ip=ip)
        new_ip_data = requests.get(
            url, headers=EXPORT_HEADERS, params={"search": f"address:{ip}"}
        )
        return new_ip_data.json()


def main():
    # did a known IP in the inventory + an IP that wasn"t in the inventory to verify everything works
    for ip in [IP_EXISTS, IP_MISSING]:
        ip_data = search_ip(ip)
        if len(ip_data) > 0:
            print(ip_data)
        else:
            print(
                f"Scanned {ip} and found no data. Either the IP is not in use or the explorer can not route to this IP address."
            )
    # if cloned, you can just pass whatever IP you want to lookup to the search_ip() function like this code below that"s commented out
    # ip_data = search_ip(ip)
    # if len(ip_data) > 0:
    #     print(ip_data)
    # else:
    #     print(
    #         f"Scanned {ip} and found no data. Either the IP is not in use or the explorer can not route to this IP address."
    #     )


if __name__ == "__main__":
    main()
