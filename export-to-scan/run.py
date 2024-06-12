import requests
import os
import ipaddress

# DO NOT TOUCH
RUNZERO_EXPORT_TOKEN = os.environ["RUNZERO_EXPORT_TOKEN"]
EXPORT_HEADERS = {"Authorization": f"Bearer {RUNZERO_EXPORT_TOKEN}"}
RUNZERO_ORG_TOKEN = os.environ["RUNZERO_ORG_TOKEN"]
RUNZERO_SITE_ID = os.environ["RUNZERO_SITE_ID"]
ORG_HEADERS = {"Authorization": f"Bearer {RUNZERO_ORG_TOKEN}"}
BASE_URL = "https://console.runZero.com/api/v1.0"

# UPDATE this to match the assets you want to scan
SEARCH = "has_public:t"

# UPDATE this if you want to use your own explorers rather than the hosted explorers
EXPLORER_ID = None

def create_scan(ip_list: list, ports: str):
    url = BASE_URL + f"/org/sites/{RUNZERO_SITE_ID}/scan"
    payload = {
        "targets": "\n".join(ip_list),
        "scan-name": f"Scan assets from search {SEARCH} in automated script",
        "scan-description": f"Scan assets from search {SEARCH} in automated script",
        "scan-frequency": "once",
        "scan-start": "0",
        "scan-tags": "type=AUTOMATED",
        "scan-grace-period": "0",
        "rate": "10000",
        "max-host-rate": "100",
        "passes": "3",
        "max-attempts": "3",
        "max-sockets": "500",
        "max-group-size": "4096",
        "max-ttl": "255",
        "tcp-ports": ports,
        "screenshots": "true",
        "nameservers": "8.8.8.8",
        "probes": "arp,bacnet,connect,dns,echo,ike,ipmi,mdns,memcache,mssql,natpmp,netbios,pca,rdns,rpcbind,sip,snmp,ssdp,syn,ubnt,wlan-list,wsd",
    }

    # Uses the explorer ID if provided else hosted explorer is used 
    if EXPLORER_ID:
        payload["agent"] = EXPLORER_ID
    else:
        payload["hosted-zone-name"] = "auto"

    data = requests.put(url, headers=ORG_HEADERS, json=payload)

    if data.status_code == 200:
        print("SUCCESS - scan created")
    else:
        print("FAILURE - scan not created: " + data.text)


def search():
    url = BASE_URL + "/export/org/assets.json?"   
    # Adding the SITE_ID as a search filter to ensure the scan is only looking at assets in the same site
    data = requests.get(url, headers=EXPORT_HEADERS,
                        params={"search": SEARCH + f" site:{RUNZERO_SITE_ID}", "fields": "addresses, addresses_extra"}) 
    if len(data.json()) > 0:
        return data.json()
    else:
        print("FAILURE - no assets match the search provided")
        return None
        


def main():
    assets = search()
    if assets:
        ip_list = []
        for asset in assets:
            for address in asset["addresses"] + asset["addresses_extra"]:
                try:
                    ip = ipaddress.ip_address(address)
                    if not ip.is_private and ip.version == 4:
                        ip_list.append(str(ip))
                except ValueError:
                    pass
        
        create_scan(ip_list=ip_list, ports="1-100,22,80,443")

if __name__ == "__main__":
    main()