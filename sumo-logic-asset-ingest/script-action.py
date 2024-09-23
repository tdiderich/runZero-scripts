#!/usr/bin/python
import json
import requests
import os

# RUNZERO CONF
RUNZERO_EXPORT_TOKEN = os.environ['RUNZERO_EXPORT_TOKEN']
HEADERS = {'Authorization': 'Bearer ' + RUNZERO_EXPORT_TOKEN}
BASE_URL = 'https://console.runZero.com/api/v1.0'


def main():
    url = BASE_URL + '/export/org/assets.json'
    assets = requests.get(url, headers=HEADERS)
    if assets.status_code == 200:
        for a in assets.json():
            print(json.dumps(a))
    else:
        print(f"No assets found - status code from runZero API: {assets.status_code}")


if __name__ == '__main__':
    main()
