import requests
import os
import csv
import json

RUNZERO_ACCOUNT_TOKEN = os.environ["RUNZERO_DEMO_ACCOUNT_TOKEN"]
HEADERS = {"Authorization": f"Bearer {RUNZERO_ACCOUNT_TOKEN}"}
BASE_URL = "https://demo.runZero.com/api/v1.0"

# A list of all the reports to be generated. New reports can be added here.
REPORTS = [
    # --- Count Reports ---
    {
        "name": "end_user_devices_count",
        "type": "count",
        "search": "type:desktop OR type:laptop OR type:tablet OR type:mobile",
    },
    {"name": "medical_devices_count", "type": "count", "search": "type:medical"},
    {"name": "servers_count", "type": "count", "search": "type:server"},
    {"name": "switches_count", "type": "count", "search": "type:switch"},
    {"name": "wifi_aps_count", "type": "count", "search": "type:wap"},
    {"name": "cameras_count", "type": "count", "search": 'type:"ip camera"'},
    {"name": "firewalls_count", "type": "count", "search": "type:firewall"},
    {"name": "hypervisors_count", "type": "count", "search": "type:hypervisor"},
    {"name": "storage_count", "type": "count", "search": "type:storage OR type:nas"},
    {
        "name": "end_of_life_os_count",
        "type": "count",
        "search": "os_eol:<now",
    },
    # --- Full Data Dumps ---
    {
        "name": "workstations",
        "type": "dump",
        "search": "type:desktop OR type:laptop",
        "fields": "id,addresses,names,os,os_version,os_eol,hw_vendor,hw_model,hw_serial,last_seen,sources",
    },
    {
        "name": "servers",
        "type": "dump",
        "search": "type:server",
        "fields": "id,addresses,names,os,os_version,os_eol,hw_vendor,hw_model,hw_serial,last_seen,sources",
    },
    {
        "name": "switches",
        "type": "dump",
        "search": "type:switch",
        "fields": "id,addresses,names,os,os_version,os_eol,hw_vendor,hw_model,hw_serial,last_seen,sources",
    },
    {
        "name": "wifi_aps",
        "type": "dump",
        "search": "type:wap",
        "fields": "id,addresses,names,os,os_version,os_eol,hw_vendor,hw_model,hw_serial,last_seen,sources",
    },
    {
        "name": "cameras",
        "type": "dump",
        "search": 'type:"ip camera"',
        "fields": "id,addresses,names,os,os_version,os_eol,hw_vendor,hw_model,hw_serial,last_seen,sources",
    },
    {
        "name": "firewalls",
        "type": "dump",
        "search": "type:firewall",
        "fields": "id,addresses,names,os,os_version,os_eol,hw_vendor,hw_model,hw_serial,last_seen,sources",
    },
    {
        "name": "hypervisors",
        "type": "dump",
        "search": "type:hypervisor",
        "fields": "id,addresses,names,os,os_version,os_eol,hw_vendor,hw_model,hw_serial,last_seen,sources",
    },
    {
        "name": "storage",
        "type": "dump",
        "search": "type:storage OR type:nas",
        "fields": "id,addresses,names,os,os_version,os_eol,hw_vendor,hw_model,hw_serial,last_seen,sources",
    },
    {
        "name": "end_of_life_os",
        "type": "dump",
        "search": "os_eol:<now",
        "fields": "id,addresses,names,os,os_version,os_eol,hw_vendor,hw_model,hw_serial,last_seen,sources",
    },
    {
        "name": "other_unclassified_hardware",
        "type": "dump",
        "search": '(NOT (type:desktop OR type:laptop OR type:tablet OR type:mobile OR type:server OR type:switch OR type:wap OR type:"ip camera" OR type:firewall OR type:hypervisor OR type:storage OR type:nas)) AND (NOT cidr:0.0.0.0/0)',
        "fields": "id,addresses,names,os,os_version,os_eol,hw_vendor,hw_model,hw_serial,last_seen,sources",
    },
]


def write_to_csv(output: list, filename: str):
    """Writes the given data to a CSV file."""
    if not output:
        print(f"No data to write for {filename}")
        return

    fieldnames = list(output[0].keys())
    with open(filename, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output)
    print(f"Successfully wrote {len(output)} rows to {filename}")


def get_runzero_data(token: str, search: str, fields: str = "id"):
    """Fetches data from the runZero API."""
    headers = {"Authorization": f"Bearer {token}"}
    url = BASE_URL + "/export/org/assets.json"
    try:
        response = requests.get(
            url, headers=headers, params={"search": search, "fields": fields}
        )
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from runZero: {e}")
        return None


def main():
    """Main function to generate reports for all organizations."""
    try:
        orgs_response = requests.get(BASE_URL + "/account/orgs", headers=HEADERS)
        orgs_response.raise_for_status()
        orgs = orgs_response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching organizations: {e}")
        return

    for org in orgs:
        token = org.get("export_token")
        org_name = org.get("name").replace(" ", "_").replace("-", "").lower()
        asset_count = org.get("asset_count")

        if not token:
            print(f"Skipping {org_name} - export token not enabled.")
            continue
        if asset_count == 0:
            print(f"Skipping {org_name} - no assets found.")
            continue

        print(f"--- Processing organization: {org_name} ---")

        # Create a directory for the organization's reports
        if not os.path.exists(org_name):
            os.mkdir(org_name)

        # A list to hold the results of the count reports for this org
        count_summary = []

        # Process each report defined in the REPORTS list
        for report in REPORTS:
            print(f"Running report: {report['name']}...")
            if report["type"] == "count":
                data = get_runzero_data(token, report["search"])
                if data is not None:
                    count_summary.append(
                        {"report_name": report["name"], "count": len(data)}
                    )

            elif report["type"] == "dump":
                data = get_runzero_data(token, report["search"], report["fields"])
                if data:
                    # Clean up the data for CSV writing
                    for row in data:
                        for key, value in row.items():
                            if isinstance(value, list):
                                row[key] = ", ".join(map(str, value))
                    write_to_csv(data, f"{org_name}/{report['name']}.csv")

        # Write the count summary report for the organization
        if count_summary:
            write_to_csv(count_summary, f"{org_name}/counts_summary.csv")


if __name__ == "__main__":
    main()
