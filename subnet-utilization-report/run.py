import requests
import json
import os
import csv
import ipaddress

# DO NOT TOUCH
RUNZERO_ORG_TOKEN = os.environ["RUNZERO_ORG_TOKEN"]
ORG_HEADERS = {"Authorization": f"Bearer {RUNZERO_ORG_TOKEN}"}
RUNZERO_EXPORT_TOKEN = os.environ["RUNZERO_EXPORT_TOKEN"]
EXPORT_HEADERS = {"Authorization": f"Bearer {RUNZERO_EXPORT_TOKEN}"}

# UPDATE IF SELF HOSTED
BASE_URL = "https://console.runZero.com/api/v1.0"

# UPDATE TO MATCH SEARCH CRITERIA
SEARCH = 'alive:t'

# UPDATE TO SELECT SUBNET SIZE - options are 8, 16, or 24
MASK = 24


def write_to_csv(output: dict, filename: str, fieldnames: list):
    file = open(filename, 'w')
    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )
    writer.writeheader()
    writer.writerows(output)
    file.close()


def write_unique_ip_to_csv(unique_ips: dict):
    # generate CSV friendly JSON
    csv_output = []
    csv_output_min = []
    for k in unique_ips.keys():
        site = requests.get(BASE_URL + f'/org/sites/{k}', headers=ORG_HEADERS)
        site_name = site.json().get('name', 'N/A')
        temp = {
            'site_id': k,
            'site_name': site_name,
            'unique_ip_count': len(unique_ips[k]),
            'unique_ip_list': unique_ips[k]
        }
        csv_output.append(temp)

        temp_min = {
            'site_id': k,
            'site_name': site_name,
            'unique_ip_count': len(unique_ips[k])
        }
        csv_output_min.append(temp_min)

    # write to CSVs
    write_to_csv(
        output=csv_output,
        filename='unique_ips_full.csv',
        fieldnames=[
            'site_id',
            'site_name',
            'unique_ip_count',
            'unique_ip_list',
        ])

    write_to_csv(
        output=csv_output_min,
        filename='unique_ips_min.csv',
        fieldnames=[
            'site_id',
            'site_name',
            'unique_ip_count',
        ])


def write_subnet_utilization_to_csv(unique_ips: dict):
    output = {}
    ranges = []
    for site in unique_ips.keys():

        output[site] = {}

        for ip in unique_ips[site]:
            if type(ipaddress.ip_address(ip)) is ipaddress.IPv4Address:
                if MASK == 24:
                    temp = '.'.join(ip.split('.')[0:3]) + '.0/24'
                elif MASK == 16:
                    temp = '.'.join(ip.split('.')[0:2]) + '.0.0/16'
                else:
                    temp = ip.split('.')[0] + '.0.0.0/8'

                if temp not in ranges:
                    ranges.append(temp)

        for subnet_range in ranges:
            for ip in unique_ips[site]:
                if type(ipaddress.ip_address(ip)) is ipaddress.IPv4Address:
                    if ipaddress.ip_address(ip) in ipaddress.ip_network(subnet_range):
                        if subnet_range in output[site]:
                            output[site][subnet_range]['ips'].append(ip)
                            output[site][subnet_range]['count'] += 1
                        else:
                            output[site][subnet_range] = {}
                            output[site][subnet_range]['ips'] = []
                            output[site][subnet_range]['ips'].append(ip)
                            output[site][subnet_range]['count'] = 1

    csv_out = []
    for k in output.keys():
        site = requests.get(BASE_URL + f'/org/sites/{k}', headers=ORG_HEADERS)
        site_name = site.json().get('name', 'N/A')

        for r in sorted(output[k]):
            if MASK == 24:
                utilization = output[k][r]['count'] / 256
            elif MASK == 16:
                utilization = output[k][r]['count'] / 65536
            else:
                utilization = output[k][r]['count'] / 16777216

            temp = {
                'site_id': k,
                'site_name': site_name,
                'range': r,
                'ip_count': output[k][r]['count'],
                'utilization': utilization
            }
            csv_out.append(temp)

        write_to_csv(
            output=csv_out,
            filename='utilization_report.csv',
            fieldnames=['site_id',
                        'site_name',
                        'range',
                        'ip_count',
                        'utilization']
        )


def get_unique_ips(assets: list):
    unique_ips = {}
    for a in assets:
        site = a['site_id']
        addresses = a.get('addresses', []) + a.get('addresses_extra', [])
        if site not in unique_ips:
            unique_ips[site] = []
        for address in addresses:
            if address not in unique_ips[site]:
                unique_ips[site].append(address)
    return unique_ips


def get_assets():
    url = BASE_URL + "/export/org/assets.json"
    data = requests.get(url, headers=EXPORT_HEADERS, params={
                        'search': SEARCH, 'fields': 'site_id,addresses,addresses_extra'})
    assets = data.json()
    return assets


def main():
    # generate stats
    assets = get_assets()
    unique_ips = get_unique_ips(assets=assets)
    write_unique_ip_to_csv(unique_ips=unique_ips)
    write_subnet_utilization_to_csv(unique_ips=unique_ips)


if __name__ == "__main__":
    main()
