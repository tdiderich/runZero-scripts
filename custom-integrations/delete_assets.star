load('runzero.types', 'ImportAsset', 'NetworkInterface')
load('json', json_encode='encode', json_decode='decode')
load('net', 'ip_address')
load('http', http_post='post', http_get='get', http_delete='delete', 'url_encode')

BASE_URL = "https://console.runZero.com/api/v1.0"
SEARCH = "alive:f"

def get_delete_ids(headers):
    # get assets to delete 
    assets = []
    url = BASE_URL + "/export/org/assets.json"
    get_assets = http_get(url=url, headers=headers, body=bytes(url_encode({"search": SEARCH, "fields": "id"})))
    assets_json = json_decode(get_assets.body)

    # if you got assets, return them as a list of asset IDs 
    if get_assets.status_code == 200:
        assets = [x["id"] for x in assets_json]
        return assets
    else:
        return None


def delete_assets(assets, headers):
    
    # delete assets
    url = BASE_URL + "/org/assets/bulk/delete"
    delete = http_delete(url, headers=HEADERS, body=bytes(json_encode({"asset_ids": assets})))
    
    # verify the delete worked 
    if delete.status_code == 204:
        print(
            "Deleted all assets matching this search: {}".format())
    else:
        print("Failed to delete assets. Please try again.")


def main(*args, **kwargs):
    rz_org_token = kwargs['access_secret']
    headers = {"Authorization": "Bearer {}".format(rz_org_token)}
    assets = get_delete_ids(headers=headers)
    if assets:
        delete_assets(assets=assets)