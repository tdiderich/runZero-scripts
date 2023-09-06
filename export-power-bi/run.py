import requests
import os

RUNZERO_EXPORT_TOKEN = os.environ["RUNZERO_EXPORT_TOKEN"]
HEADERS = {"Authorization": f"Bearer {RUNZERO_EXPORT_TOKEN}"}
BASE_URL = "https://console.runZero.com/api/v1.0"

# endpoints for your Power BI API integrations
assets_power_bi_endpoint = "ADD ME"
services_power_bi_endpoint = "ADD ME"

# fields are broken out to INT and STR to show what to set the type as in Power BI
# INT = Number and STR = Text
asset_int_fields = "service_count,service_count_arp,service_count_icmp,service_count_tcp,service_count_udp,software_count,vulnerability_count"
asset_str_fields = "alive,criticality,hw,hw_product,hw_vendor,hw_version,id,os,os_product,os_vendor,os_version,risk"
asset_fields = asset_int_fields + "," + asset_str_fields

service_int_fields = "service_port"
service_str_fields = "alive,service_id,service_asset_id,service_organization_id,service_address,service_transport,service_vhost,service_summary,id,organization_id,site_id,detected_by,type"
service_fields = service_int_fields + "," + service_str_fields


def main():
    # get and post assets
    assets_url = BASE_URL + "/export/org/assets.json"
    assets_request = requests.get(assets_url, headers=HEADERS, params={
        "fields": asset_fields})
    assets = assets_request.json()
    requests.post(assets_power_bi_endpoint, json=assets)

    # get and post services
    services_url = BASE_URL + "/export/org/services.json"
    services_request = requests.get(services_url, headers=HEADERS, params={
                                    "fields": service_fields})
    services = services_request.json()
    requests.post(services_power_bi_endpoint, json=services)


if __name__ == "__main__":
    main()
