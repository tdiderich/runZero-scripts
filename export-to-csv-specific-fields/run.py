import requests
import os
import json
import csv

RUNZERO_EXPORT_TOKEN = os.environ["RUNZERO_EXPORT_TOKEN"]
HEADERS = {"Authorization": f"Bearer {RUNZERO_EXPORT_TOKEN}"}
BASE_URL = "https://console.runZero.com/api/v1.0"


def main():
    url = BASE_URL + "/export/org/assets.json?"
    data = requests.get(url, headers=HEADERS, params={
                        "search": "protocol:tls alive:t"})
    assets = data.json()
    output = []

    for a in assets:
        asset_row = {'id': a.get('id', ''), 'names': a.get(
            'names', ''), 'addresses': a.get('addresses', '')}
        services = a['services']
        for s in services.keys():
            protocol = services[s].get('protocol', 'NONE')
            if protocol.__contains__('tls'):
                asset_row['service_address'] = services[s].get(
                    'service.address', '')
                asset_row['service_port'] = services[s].get('service.port', '')
                for attribute in services[s].keys():
                    if attribute.__contains__('tls'):
                        asset_row[attribute] = services[s][attribute]
        output.append(asset_row)

    tls_csv = open('./tls_fields.csv', 'w')
    writer = csv.DictWriter(
        tls_csv,
        fieldnames=[
            'id',
            'names',
            'addresses',
            'service_address',
            'service_port',
            'tls.certificates',
            'tls.cipher',
            'tls.cipherName',
            'tls.cn',
            'tls.fp.sha1',
            'tls.fp.sha256',
            'tls.issuer',
            'tls.names',
            'tls.notAfter',
            'tls.notAfterTS',
            'tls.notBefore',
            'tls.notBeforeTS',
            'tls.selfSigned',
            'tls.serial',
            'tls.signatureAlgorithm',
            'tls.subject',
            'tls.supportedVersionNames',
            'tls.supportedVersions',
            'tls.version',
            'tls.versionName',
            'dtls.alert',
            'tls.fp.caSha1', 
            'tls.hostTime', 
            'tls.rzfp0', 
            'tls.hostTimeTS', 
            'tls.requiresClientCertificate',
            'tls.crl', 
            'tls.authorityKeyID', 
            'tls.stack', 
            'tls.ocsp', 
            'tls.issuingURL', 
            'tls.subjectKeyID',
            'tls.caUnknown'
        ])
    writer.writeheader()
    writer.writerows(output)
    tls_csv.close()

    print('Successfully loaded the data to tls_fields.csv')
    print(json.dumps(output, indent=4))


if __name__ == "__main__":
    main()
