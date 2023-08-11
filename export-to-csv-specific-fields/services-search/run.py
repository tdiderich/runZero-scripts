import requests
import os
import json
import csv

RUNZERO_EXPORT_TOKEN = os.environ["RUNZERO_EXPORT_TOKEN"]
HEADERS = {"Authorization": f"Bearer {RUNZERO_EXPORT_TOKEN}"}
BASE_URL = "https://console.runZero.com/api/v1.0"
SEARCHES = {
    "all_tls_services": "alive:t protocol:tls",
    "soon_to_expire_tls_certs": "alive:t _asset.protocol:tls AND tls.notAfterTS:<6weeks",
    "expired_tls_certs": "alive:t _asset.protocol:tls AND tls.notAfterTS:<now"
}


def main():
    for k in SEARCHES.keys():
        url = BASE_URL + "/export/org/services.json?"
        data = requests.get(url, headers=HEADERS, params={
                            "search": SEARCHES[k]})
        services = data.json()
        output = []
        fields = ['id', 'names', 'service_address', 'service_port', 'created_at', 'updated_at']

        for s in services:
            print(json.dumps(s, indent=4))
            service_row = {'id': s.get('id', ''), 'names': s.get(
                'names', ''), 'service_address': s.get('service_address', ''), 'service_port': s.get('service_port', '')}
            for attribute in s['service_data'].keys():
                if attribute.__contains__('tls'):
                    service_row[attribute] = s['service_data'][attribute]
                    if attribute not in fields:
                        fields.append(attribute)
                    
            output.append(service_row)

        fname = f'{k}.csv'
        tls_csv = open(fname, 'w')
        writer = csv.DictWriter(
            tls_csv,
            fieldnames=fields)
        writer.writeheader()
        writer.writerows(output)
        tls_csv.close()

        print(f'Successfully loaded the data to {fname}')


if __name__ == "__main__":
    main()
