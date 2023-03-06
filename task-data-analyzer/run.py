import json
import csv
import os

TASK_LIST = ['task3', 'task4', 'task1']
RESULTS_SUMMARY = []
RESULTS_SUMMARY_FULL = []


def write_to_csv(output: dict, filename: str, fieldnames: list):
    file = open(filename, 'w')
    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )
    writer.writeheader()
    writer.writerows(output)
    file.close()


def main(file, filename):
    if not os.path.exists(f'{filename.strip(".json")}-out'):
        os.mkdir(f'{filename.strip(".json")}-out')

    errors = {}
    errors_csv_output = []
    results = {}
    results_csv_output = []
    for line in file:

        # create dict
        jline = json.loads(line.strip('@cee:'))

        # handle results
        if jline.get('type', '') == 'result':
            if jline.get('host', '') in results:
                results[jline.get('host', '')]['ports'].append(
                    jline.get('port', ''))
                results[jline.get('host', '')]['port_count'] += 1
            else:
                results[jline.get('host', '')] = {
                    "ports": [jline.get('port', '')],
                    "port_count": 1
                }

        # handle errors
        if jline.get('level', '') == 'error':
            if jline['msg'] in errors:
                errors[jline['msg']] += 1
            else:
                errors[jline['msg']] = 1

    # temp
    results_summary = {
        'total_hosts': 0,
        'total_hosts_list': [],
        'total_ports': 0,
        'unique_ports': [],
        'unique_ports_count': 0,
    }

    # create CSV writeable list for results
    for k in results.keys():
        results_csv_output.append({
            'host': k,
            'port_count': results[k]['port_count'],
            'ports': results[k]['ports'],
        })

        # add 1 to host count
        results_summary['total_hosts'] += 1

        # add ports to total port count
        results_summary['total_ports'] += results[k]['port_count']

        # add port to list if it doesn't exist yet
        for p in results[k]['ports']:
            if p not in results_summary['unique_ports']:
                results_summary['unique_ports'].append(p)

        # add host to list of hosts
        results_summary['total_hosts_list'].append(k)

    results_summary['unique_ports'] = sorted(results_summary['unique_ports'])
    results_summary['unique_ports_count'] = len(
        results_summary['unique_ports'])

    # write results to CSV
    write_to_csv(
        output=results_csv_output,
        filename=f'{filename.strip(".json")}-out/results.csv',
        fieldnames=[
            'host',
            'port_count',
            'ports',
        ])

    # write summary to CSV
    write_to_csv(
        output=[results_summary],
        filename=f'{filename.strip(".json")}-out/summary.csv',
        fieldnames=[
            'total_hosts',
            'total_ports',
            'unique_ports_count',
            'unique_ports',
            'total_hosts_list',
        ])

    # save for global summary
    RESULTS_SUMMARY.append({
        'task': filename,
        'total_hosts': results_summary['total_hosts'],
        'total_ports': results_summary['unique_ports_count'],
        'unique_ports_count': results_summary['unique_ports_count']
    })

    RESULTS_SUMMARY_FULL.append({
        'task': filename,
        'total_hosts': results_summary['total_hosts'],
        'unique_ports_count': results_summary['unique_ports_count'],
        'total_hosts_list': results_summary['total_hosts_list'],
        'total_ports': results_summary['unique_ports_count'],
    })

    # create CSV writeable list for errors
    for k in errors.keys():
        errors_csv_output.append({
            'error': k,
            'count': errors[k]
        })

    # sort based on error count before writing to CSV for errors
    errors_csv_output = sorted(
        errors_csv_output, key=lambda d: d['count'], reverse=True)

    # write errors to CSV
    write_to_csv(
        output=errors_csv_output,
        filename=f'{filename.strip(".json")}-out/errors.csv',
        fieldnames=[
            'error',
            'count'
        ])


if __name__ == "__main__":
    for f in TASK_LIST:
        file = open(f)
        main(file=file, filename=f)

    # write global summary to CSV
    write_to_csv(
        output=RESULTS_SUMMARY,
        filename=f'results_summary.csv',
        fieldnames=[
            'task',
            'total_hosts',
            'total_ports',
            'unique_ports_count',
        ])

    # write global full summary to CSV
    write_to_csv(
        output=RESULTS_SUMMARY_FULL,
        filename=f'results_summary_full.csv',
        fieldnames=[
            'task',
            'total_hosts',
            'total_ports',
            'unique_ports',
            'unique_ports_count',
            'total_hosts_list',
        ])
