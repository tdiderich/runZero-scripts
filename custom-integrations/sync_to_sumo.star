load('runzero.types', 'ImportAsset', 'NetworkInterface')
load('json', json_encode='encode', json_decode='decode')
load('net', 'ip_address')
load('http', http_post='post', http_get='get', 'url_encode')

SUMO_HTTP_ENDPOINT = "<UPDATE_ME>"
BASE_URL = "https://console.runZero.com/api/v1.0"
SEARCH = "alive:t"

def get_assets(headers):
    # get assets to upload to sumo
    assets = []
    url = BASE_URL + "/export/org/assets.json"
    get_assets = http_get(url=url, headers=headers, body=bytes(url_encode({"search": SEARCH})))
    assets_json = json_decode(get_assets.body)
    if get_assets.status_code == 200 and len(assets_json) > 0:
        return assets_json
    else:
        print("runZero did not return any assets - status code {}".format(get_assets.status_code))
        return None

def sync_to_sumo(assets):
    batchsize = 500
    if len(assets) > 0:
        for i in range(0, len(assets), batchsize):
            batch = assets[i:i+batchsize]
            tmp = ""
            for a in batch:
                tmp = tmp + "{}\n".format(json_encode(a))
            post_to_sumo = http_post(url=SUMO_HTTP_ENDPOINT, body=bytes(tmp))
    else:
        print("No assets found")


def main(*args, **kwargs):
    rz_export_token = kwargs['access_secret']
    headers = {"Authorization": "Bearer {}".format(rz_export_token)}
    assets = get_assets(headers=headers)
    if assets:
        sync_to_sumo(assets=assets)