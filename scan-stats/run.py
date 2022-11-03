import requests
import json
import os

# DO NOT TOUCH
RUNZERO_ORG_TOKEN = os.environ["RUNZERO_ORG_TOKEN"]
ORG_HEADERS = {"Authorization": f"Bearer {RUNZERO_ORG_TOKEN}"}

# UPDATE IF SELF HOSTED 
BASE_URL = "https://console.runZero.com/api/v1.0"


def get_tasks():
    url = BASE_URL + "/org/tasks"
    data = requests.get(url, headers=ORG_HEADERS, params={'search': 'recur:t'})
    recurring_tasks = data.json()
    task_stats = {}
    for r in recurring_tasks:
        if r['name'] not in ['Outlier calculation', 'Query']:
            id = r['id']
            tasks_from_parent = requests.get(url, headers=ORG_HEADERS, params={'search': f'parent_id:{id}'})
            task_stats[id] = {
                'names': [],
                'site_ids': [],
                'site_names': [],
                'new_assets_all_time': 0, 
                'offline_assets_all_time': 0,
                'total_assets_seen': 0,
                'scan_count': len(tasks_from_parent.json()),
                'average_assets_seen': 0,
                'max_assets_seen': 0,
                'min_assets_seen': 10000000000000
                }
            for t in tasks_from_parent.json():
                name = t.get('name', '')
                if name and name not in task_stats[id]['names']:
                    task_stats[id]['names'].append(name)
                
                site_id = t.get('site_id', '')
                if site_id and site_id not in task_stats[id]['site_ids']:
                    task_stats[id]['site_ids'].append(site_id)
                
                new_assets = t.get('stats', '').get('change.newAssets', '')
                if new_assets:
                    task_stats[id]['new_assets_all_time'] += int(new_assets)

                offline_assets = t.get('stats', '').get('change.offlineAssets', '')
                if offline_assets:
                    task_stats[id]['offline_assets_all_time'] += int(offline_assets)
                
                total_assets = t.get('stats', '').get('change.totalAssets', '')
                if total_assets:
                    task_stats[id]['total_assets_seen'] += int(total_assets)
                    task_stats[id]['max_assets_seen'] = total_assets if total_assets > task_stats[id]['max_assets_seen'] else task_stats[id]['max_assets_seen']
                    task_stats[id]['min_assets_seen'] = total_assets if total_assets < task_stats[id]['min_assets_seen'] else task_stats[id]['min_assets_seen']
            
            task_stats[id]['average_assets_seen'] = round(task_stats[id]['total_assets_seen'] / task_stats[id]['scan_count'])
            for s in task_stats[id]['site_ids']:
                get_site_url = BASE_URL + f'/org/sites/{s}'
                site_data = requests.get(get_site_url, headers=ORG_HEADERS)
                site_name = site_data.json().get('name')
                if site_name and site_name not in task_stats[id]['site_names']:
                    task_stats[id]['site_names'].append(site_name)

    return task_stats

def main():
    task_stats = get_tasks()
    print(json.dumps(task_stats, indent=4))

if __name__ == "__main__":
    main()
