import requests
import os

RUNZERO_EXPORT_TOKEN = os.environ["RUNZERO_EXPORT_TOKEN"]
HEADERS = {"Authorization": f"Bearer {RUNZERO_EXPORT_TOKEN}"}
BASE_URL = "https://console.runZero.com/api/v1.0"

MAC = "A0:5C:D5:E7:C1:11"
IP = "192.168.86.250"
NAME = "TYLERS-PHONE"

def main():
    url = BASE_URL + '/export/org/assets.json'
    
    everything = requests.get(url, headers=HEADERS, params={
        "search": "alive:t"})
    print(f"Found {len(everything.json())} total assets alive")
    
    mac_results = requests.get(url, headers=HEADERS, params={
                        "search": f"alive:t mac:{MAC}"})
    print(f"Found {len(mac_results.json())} assets with the MAC address {MAC}")
    
    ip_results = requests.get(url, headers=HEADERS, params={
        "search": f"alive:t address:{IP}"})
    print(f"Found {len(ip_results.json())} assets with the IP address {IP}")
    
    name_results = requests.get(url, headers=HEADERS, params={
        "search": f"alive:t name:{NAME}"})
    print(f"Found {len(name_results.json())} assets with the name {NAME}")


if __name__ == "__main__":
    main()
