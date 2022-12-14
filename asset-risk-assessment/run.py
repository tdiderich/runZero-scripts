import requests
import os
import csv
import json

RUNZERO_EXPORT_TOKEN = os.environ['RUNZERO_EXPORT_TOKEN']
HEADERS = {'Authorization': f'Bearer {RUNZERO_EXPORT_TOKEN}'}
BASE_URL = 'https://console.runZero.com/api/v1.0'


def write_to_csv(output: dict, filename: str, fieldnames: list):
    file = open(filename, 'w')
    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )
    writer.writeheader()
    writer.writerows(output)
    file.close()


def main():
    # read csv
    file = open('queries.csv', 'r')
    reader = csv.reader(file, delimiter=',')

    # dicts for tracking counts and data
    executive_report = []
    asset_report = {}
    risk_report = []

    for row in reader:

        # skip headers
        if row[0] != 'name':
            name = row[0]
            description = row[1]
            search_type = row[2]
            severity = row[4]
            query = row[5]

            if search_type == 'assets':
                url = BASE_URL + '/export/org/assets.json?'
            elif search_type == 'services':
                url = BASE_URL + '/export/org/services.json?'
            elif search_type == 'wireless':
                url = BASE_URL + '/export/org/wireless.json?'
            else:
                print(f'non supported search type {search_type}')

            data = requests.get(url, headers=HEADERS, params={
                                'search': query, 'fields': 'id,addresses,addresses_extra,names'})

            if data.status_code == 200:
                results = data.json()

                if len(results) > 0:
                    executive_report.append({
                        'search_name': name,
                        'search_description': description,
                        'search_type': search_type,
                        'severity': severity,
                        'count': len(results)
                    })

                    risk_report.append({
                        'search_name': name,
                        'search_description': description,
                        'search_type': search_type,
                        'severity': severity,
                        'count': len(results),
                        'asset_ids': [x['id'] for x in results]
                    })

                    for asset in results:
                        if asset['id'] in asset_report.keys():
                            asset_report[asset['id']]['risks'].append(name)
                        else:
                            asset_report[asset['id']] = {
                                'id': asset['id'],
                                'addresses': asset['addresses'],
                                'addresses_extra': asset['addresses_extra'],
                                'names': asset['names'],
                                'risks': [name]
                            }

            else:
                print(f'{name} caused a non-200')

    write_to_csv(
        output=executive_report,
        filename='exec_report.csv',
        fieldnames=[
            'search_name',
            'search_description',
            'search_type',
            'severity',
            'count'
        ])
    
    write_to_csv(
        output=risk_report,
        filename='risk_report.csv',
        fieldnames=[
            'search_name',
            'search_description',
            'search_type',
            'severity',
            'count',
            'asset_ids'
        ])

    asset_report_csv = []
    for a in asset_report.keys():
        temp = {
            'id': asset_report[a]['id'],
            'addresses': asset_report[a]['addresses'],
            'addresses_extra': asset_report[a]['addresses_extra'],
            'names': asset_report[a]['names'],
            'risks': asset_report[a]['risks'],
            'risk_count': len(asset_report[a]['risks'])
        }
        asset_report_csv.append(temp)

    write_to_csv(
        output=asset_report_csv,
        filename='asset_report.csv',
        fieldnames=[
            'id',
            'addresses',
            'addresses_extra',
            'names',
            'risks',
            'risk_count'
        ])


if __name__ == '__main__':
    main()
