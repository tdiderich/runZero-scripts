import json
import urllib3
import os

# RUNZERO CONF
RUNZERO_EXPORT_TOKEN = os.environ["RUNZERO_EXPORT_TOKEN"]
HEADERS = {"Authorization": f"Bearer {RUNZERO_EXPORT_TOKEN}"}
BASE_URL = "https://console.runZero.com/api/v1.0"

# SUMO LOGIC CONF
HTTP_ENDPOINT = os.environ["SUMO_HTTP_ENDPOINT"]


def lambda_handler(event, context):
    http = urllib3.PoolManager()
    url = BASE_URL + "/export/org/assets.json"
    response = http.request("GET", url, headers=HEADERS)
    data = response.data
    assets = json.loads(data)
    batchsize = 500
    if len(assets.json()) > 0 and assets.status_code == 200:
        for i in range(0, len(assets.json()), batchsize):
            batch = assets.json()[i : i + batchsize]
            f = open("upload.txt", "w")
            f.truncate(0)
            for a in batch:
                json.dump(a, f)
                f.write("\n")
            f.close()
            r = open("upload.txt")
            http.request("POST", HTTP_ENDPOINT, data=r.read())
            r.close()
    else:
        print(f"No assets found - status code from runZero API: {assets.status_code}")
