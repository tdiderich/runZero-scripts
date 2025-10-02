# runZero Asset Overview Report

This script generates a series of CSV reports based on asset data from your runZero organizations. It categorizes assets, provides counts for various device types, and creates detailed data dumps for further analysis.

## How it Works

The script connects to the runZero API and iterates through all organizations in your account. For each organization that has assets and an export token enabled, it performs the following actions:

1.  **Creates a Directory:** A directory is created for each organization (e.g., `rz_corporation/`) to store the reports.
2.  **Runs Reports:** It executes a predefined list of reports. There are two types of reports:
    *   **Count Reports:** These reports count assets based on specific search criteria (e.g., "all servers", "end-of-life operating systems"). The results are saved in a `counts_summary.csv` file within the organization's directory.
    *   **Dump Reports:** These reports export a detailed list of assets with specific fields (e.g., IP address, OS, hardware details). Each dump report is saved as a separate CSV file (e.g., `servers.csv`, `workstations.csv`).

## Prerequisites

Before running the script, you need to have a runZero account token with the necessary permissions to access asset data.

## Setup

1.  **Set Environment Variable:** You must set the `RUNZERO_ACCOUNT_TOKEN` environment variable to your runZero account token.
    ```bash
    export RUNZERO_ACCOUNT_TOKEN="YOUR_TOKEN_HERE"
    ```

## Running the Script

To generate the reports, simply run the `run.py` script:

```bash
python run.py
```

The script will process each organization and create the corresponding report files in their respective directories.

## Reports Generated

For each organization, the script generates the following reports:

### Count Summary (`counts_summary.csv`)

This file provides a summary of asset counts for various categories:

*   `end_user_devices_count`
*   `medical_devices_count`
*   `servers_count`
*   `switches_count`
*   `wifi_aps_count`
*   `cameras_count`
*   `firewalls_count`
*   `hypervisors_count`
*   `storage_count`
*   `end_of_life_os_count`

```
$ rich rz_corporation/counts_summary.csv                                              [10:36:09]
┏━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ report_name            ┃ count ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ end_user_devices_count │   159 │
│ medical_devices_count  │     0 │
│ servers_count          │   965 │
│ switches_count         │    40 │
│ wifi_aps_count         │    18 │
│ cameras_count          │    77 │
│ firewalls_count        │    15 │
│ hypervisors_count      │     0 │
│ storage_count          │     0 │
│ end_of_life_os_count   │   389 │
└────────────────────────┴───────┘
```

### Detailed Dumps (Individual CSV Files)

These files contain detailed information about specific asset types:

*   `workstations.csv`
*   `servers.csv`
*   `switches.csv`
*   `wifi_aps.csv`
*   `cameras.csv`
*   `firewalls.csv`
*   `hypervisors.csv`
*   `storage.csv`
*   `end_of_life_os.csv`
*   `other_unclassified_hardware.csv`

Each of these CSV files includes the following fields:

*   `id`
*   `addresses`
*   `names`
*   `os`
*   `os_version`
*   `os_eol`
*   `hw_vendor`
*   `hw_model`
*   `hw_serial`
*   `last_seen`
*   `sources`

```
$ rich rz_corporation/wifi_aps.csv
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ addresses    ┃ hw_vendor        ┃ id                          ┃  last_seen ┃ names        ┃ os                 ┃ os_version        ┃ sources         ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ 10.0.4.1     │ Ruckus           │ 0d3dd67e-92f3-42b7-8890-e7… │ 1759385534 │ RZHQ-WAP-41  │ Linux              │ 5.4.0-122-generic │ Nessus, runZero │
│ 10.0.20.1    │ Ruckus           │ 160b317a-a9b5-4c50-98eb-d6… │ 1759385528 │              │ Linux              │ 5.4.0-122-generic │ Nessus, runZero │
│ 10.0.2.46    │ Extreme Networks │ 405ab6cb-d97d-4463-97ad-c0… │ 1759385532 │              │ Extreme Networks   │                   │ runZero         │
│ 198.51.28.40 │ Extreme Networks │ 4495dfb0-ac1e-4d5c-98b5-1b… │ 1759385533 │              │ Extreme Networks   │                   │ runZero         │
│ 10.0.16.1    │ Ruckus           │ 48ad3dd0-b9bc-4c97-999b-17… │ 1759385535 │              │ Linux              │ 5.4.0-122-generic │ Nessus, runZero │
│ 10.0.7.1     │ Ruckus           │ 59d15a3d-a12a-4481-a90c-c1… │ 1759385537 │              │ Linux              │ 5.4.0-122-generic │ Nessus, runZero │
│ 10.0.16.41   │ Extreme Networks │ 627a49a6-1dc4-4178-a46f-31… │ 1759385536 │              │ Extreme Networks   │                   │ runZero         │
│ 198.51.29.3  │ Extreme Networks │ 62974ac3-ad81-40cf-bcd0-9e… │ 1759385533 │              │ Extreme Networks   │                   │ runZero         │
│ 198.51.29.28 │ Extreme Networks │ 68ed9219-1ec2-4961-b63b-40… │ 1759385534 │              │ Extreme Networks   │                   │ runZero         │
│ 10.0.15.27   │ Extreme Networks │ 947058f6-abba-45bf-95a4-bb… │ 1759385535 │              │ Extreme Networks   │                   │ runZero         │
│ 10.0.3.1     │ Ruckus           │ 98c0086b-a4fe-4559-8ef5-ef… │ 1759385532 │ RZHQ-WAP-31  │ Linux              │ 5.4.0-122-generic │ Nessus, runZero │
│ 10.0.14.1    │ Ruckus           │ 9abcd017-7a9b-409b-af20-08… │ 1759385532 │              │                    │                   │ runZero         │
│ 198.51.25.20 │ Extreme Networks │ a0f3d379-9325-4b1c-8e98-c2… │ 1759385529 │              │ Extreme Networks   │                   │ runZero         │
│ 10.0.5.1     │ Ubiquiti         │ adc48677-0e1e-414a-9db0-a8… │ 1759385535 │ RZHQ-WAP-51  │ Ubiquiti UniFi UAP │ 6.6.65.15248      │ runZero         │
│ 10.0.13.6    │ Extreme Networks │ ac5d3800-d8b7-49c6-9c0c-dd… │ 1759385532 │              │ Extreme Networks   │                   │ runZero         │
│ 10.0.7.9     │ Extreme Networks │ bf8cebdc-ceac-4d3f-94cf-63… │ 1759385538 │              │ Extreme Networks   │                   │ runZero         │
│ 10.0.6.1     │ Ruckus           │ f05dc2fd-9b2b-4f9c-bde9-83… │ 1759385536 │ RZHQ-WAP-61  │ Linux              │                   │ runZero         │
│ 10.0.12.1    │ Ubiquiti         │ fcdf6763-cb5c-46af-a285-9e… │ 1759385529 │ RZDC-WAP-121 │ Ubiquiti UniFi UAP │ 6.6.65.15248      │ Nessus, runZero │
└──────────────┴──────────────────┴─────────────────────────────┴────────────┴──────────────┴────────────────────┴───────────────────┴─────────────────┘
```

## Customization

You can customize the reports by modifying the `REPORTS` list in the `run.py` script. You can add new reports, change the search queries, or adjust the fields to be exported.
