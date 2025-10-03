# Asset Sources Overview

This script processes a JSON export of assets from runZero to generate a detailed CSV report that provides an overview of asset sources. The report helps you understand which sources are contributing to the data for each asset.

## How it Works

The script performs the following steps:

1.  **Parses `assets.json`**: It reads a file named `assets.json`, which is expected to be a JSON export of assets from your runZero inventory.

2.  **Maps Source IDs to Names**: It uses an internal mapping to convert runZero's numeric source IDs into human-readable names (e.g., "1" becomes "rumble").

3.  **Extracts and Correlates Data**: For each asset in the JSON file, the script:
    *   Identifies all the different sources that have contributed to the asset's data.
    *   Extracts every individual identifier (like IP addresses, MAC addresses, hostnames, etc.) and the source it came from.

4.  **Generates a CSV Report**: It creates a CSV file named `asset_sources_report.csv` with the following structure:
    *   **Identifier Columns**: `asset_id`, `source`, `type`, and `value`. These columns show the specific details of each identifier found for an asset.
    *   **Source Summary Columns**: A column for each unique source found in your data (e.g., `rumble`, `aws`, `crowdstrike`). The value in these columns will be either "✅" (if the asset has data from that source) or "❌" (if it does not).

This detailed report allows you to see not only which sources are associated with an asset but also the specific identifiers contributed by each source.

## Usage

1.  **Export Assets from runZero**:
    *   Go to the **Inventory** section in your runZero console.
    *   Export your assets in **JSON** format.
    *   Save the exported file as `assets.json` in the same directory as the script.

2.  **Run the Script**:
    ```bash
    python run.py
    ```

3.  **View the Report**:
    *   Once the script has finished, it will create a file named `asset_sources_report.csv`.
    *   You can open this file in any spreadsheet program to view the results.

## Example Output

```
$ python3 run.py 
                                  Asset ID: 061786a4-4ce3-4f67-9dfd-581bfbbb1633                                  
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━┓
┃ asset_id                             ┃ source ┃ type  ┃ value             ┃ azuread ┃ nessus ┃ qualys ┃ rumble ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━┩
│ 061786a4-4ce3-4f67-9dfd-581bfbbb1633 │ nessus │ addrs │ 10.0.0.2          │ ❌      │ ✅     │ ❌     │ ❌     │
│ 061786a4-4ce3-4f67-9dfd-581bfbbb1633 │ nessus │ macs  │ 5c:e2:8c:12:87:a0 │ ❌      │ ✅     │ ❌     │ ❌     │
│ 061786a4-4ce3-4f67-9dfd-581bfbbb1633 │ rumble │ addrs │ 10.0.0.2          │ ❌      │ ❌     │ ❌     │ ✅     │
│ 061786a4-4ce3-4f67-9dfd-581bfbbb1633 │ rumble │ macs  │ 5c:e2:8c:12:87:a0 │ ❌      │ ❌     │ ❌     │ ✅     │
│ 061786a4-4ce3-4f67-9dfd-581bfbbb1633 │ rumble │ names │ RZHQ-FIREWALL-02  │ ❌      │ ❌     │ ❌     │ ✅     │
└──────────────────────────────────────┴────────┴───────┴───────────────────┴─────────┴────────┴────────┴────────┘
                                                              Asset ID: b0b296d2-9a77-4ee7-9ad4-84cd74bf29df                                                               
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━┓
┃ asset_id                             ┃ source ┃ type  ┃ value                                                                      ┃ azuread ┃ nessus ┃ qualys ┃ rumble ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━┩
│ b0b296d2-9a77-4ee7-9ad4-84cd74bf29df │ nessus │ addrs │ 10.0.0.1        10.0.1.1        10.0.10.1       10.0.15.1       10.0.17.1  │ ❌      │ ✅     │ ❌     │ ❌     │
│                                      │        │       │ 10.0.18.1       10.0.19.1       10.0.9.1                                   │         │        │        │        │
│ b0b296d2-9a77-4ee7-9ad4-84cd74bf29df │ nessus │ macs  │ 00:a0:c8:04:0d:f1       00:a0:c8:67:6f:4a       00:a0:c8:8b:7a:c9          │ ❌      │ ✅     │ ❌     │ ❌     │
│                                      │        │       │ 00:a0:c8:8f:e3:53       00:a0:c8:e8:ed:5c       00:a0:c8:ed:da:d0          │         │        │        │        │
│                                      │        │       │ e4:aa:5d:1d:37:60       e4:aa:5d:27:09:24                                  │         │        │        │        │
│ b0b296d2-9a77-4ee7-9ad4-84cd74bf29df │ qualys │ addrs │ 10.0.0.1        10.0.1.1        10.0.10.1       10.0.15.1       10.0.17.1  │ ❌      │ ❌     │ ✅     │ ❌     │
│                                      │        │       │ 10.0.18.1       10.0.19.1       10.0.9.1                                   │         │        │        │        │
│ b0b296d2-9a77-4ee7-9ad4-84cd74bf29df │ qualys │ macs  │ 00:1b:d5:d8:72:bf       e4:aa:5d:27:09:24                                  │ ❌      │ ❌     │ ✅     │ ❌     │
│ b0b296d2-9a77-4ee7-9ad4-84cd74bf29df │ rumble │ addrs │ 10.0.0.1        10.0.1.1        10.0.10.1       10.0.15.1       10.0.17.1  │ ❌      │ ❌     │ ❌     │ ✅     │
│                                      │        │       │ 10.0.18.1       10.0.19.1       10.0.9.1                                   │         │        │        │        │
│ b0b296d2-9a77-4ee7-9ad4-84cd74bf29df │ rumble │ macs  │ 00:a0:c8:04:0d:f1       00:a0:c8:67:6f:4a       00:a0:c8:8b:7a:c9          │ ❌      │ ❌     │ ❌     │ ✅     │
│                                      │        │       │ 00:a0:c8:8f:e3:53       00:a0:c8:e8:ed:5c       00:a0:c8:ed:da:d0          │         │        │        │        │
│                                      │        │       │ e4:aa:5d:1d:37:60       e4:aa:5d:27:09:24                                  │         │        │        │        │
│ b0b296d2-9a77-4ee7-9ad4-84cd74bf29df │ rumble │ names │ RZBACNET-ROUTER-101     RZDC-ROUTER-151 RZDC-ROUTER-171 RZDC-ROUTER-191    │ ❌      │ ❌     │ ❌     │ ✅     │
│                                      │        │       │ RZHQ-ROUTER-11  RZHQ-ROUTER-91                                             │         │        │        │        │
└──────────────────────────────────────┴────────┴───────┴────────────────────────────────────────────────────────────────────────────┴─────────┴────────┴────────┴────────┘
                                                              Asset ID: eb13fa8b-3a53-4359-a139-1f21ef6ed70e                                                               
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━┓
┃ asset_id                             ┃ source  ┃ type       ┃ value                                                                ┃ azuread ┃ nessus ┃ qualys ┃ rumble ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━┩
│ eb13fa8b-3a53-4359-a139-1f21ef6ed70e │ azuread │ names      │ RZDC-SERVER-1824                                                     │ ✅      │ ❌     │ ❌     │ ❌     │
│ eb13fa8b-3a53-4359-a139-1f21ef6ed70e │ nessus  │ addrs      │ 10.0.0.39       10.0.0.4        10.0.11.12      10.0.11.47           │ ❌      │ ✅     │ ❌     │ ❌     │
│                                      │         │            │ 10.0.18.24      10.0.19.9       10.0.2.37       10.0.6.3             │         │        │        │        │
│ eb13fa8b-3a53-4359-a139-1f21ef6ed70e │ rumble  │ addrs      │ 10.0.0.30       10.0.0.39       10.0.0.4        10.0.1.22            │ ❌      │ ❌     │ ❌     │ ✅     │
│                                      │         │            │ 10.0.1.30       10.0.10.49      10.0.11.12      10.0.11.46           │         │        │        │        │
│                                      │         │            │ 10.0.11.47      10.0.13.17      10.0.15.15      10.0.17.25           │         │        │        │        │
│                                      │         │            │ 10.0.18.24      10.0.19.18      10.0.19.30      10.0.19.9            │         │        │        │        │
│                                      │         │            │ 10.0.2.37       10.0.20.15      10.0.6.3        10.0.7.19            │         │        │        │        │
│                                      │         │            │ 10.0.8.18       10.0.8.8        10.0.9.31       10.0.9.43            │         │        │        │        │
│ eb13fa8b-3a53-4359-a139-1f21ef6ed70e │ rumble  │ addrsExtra │ 198.51.100.6                                                         │ ❌      │ ❌     │ ❌     │ ✅     │
│ eb13fa8b-3a53-4359-a139-1f21ef6ed70e │ rumble  │ names      │ CQKOL   N50LON.NQG      RZBACNET-SERVER-1049    RZBACNET-SERVER-2015 │ ❌      │ ❌     │ ❌     │ ✅     │
│                                      │         │            │ RZDC-SERVER-1112        RZDC-SERVER-1146        RZDC-SERVER-1147     │         │        │        │        │
│                                      │         │            │ RZDC-SERVER-1317        RZDC-SERVER-1515        RZDC-SERVER-1725     │         │        │        │        │
│                                      │         │            │ RZDC-SERVER-1824        RZDC-SERVER-1918        RZDC-SERVER-1930     │         │        │        │        │
│                                      │         │            │ RZDC-SERVER-199 RZHQ-SERVER-030 RZHQ-SERVER-039 RZHQ-SERVER-04       │         │        │        │        │
│                                      │         │            │ RZHQ-SERVER-122 RZHQ-SERVER-130 RZHQ-SERVER-237 RZHQ-SERVER-63       │         │        │        │        │
│                                      │         │            │ RZHQ-SERVER-719 RZHQ-SERVER-818 RZHQ-SERVER-88  RZHQ-SERVER-931      │         │        │        │        │
│                                      │         │            │ RZHQ-SERVER-943                                                      │         │        │        │        │
└──────────────────────────────────────┴─────────┴────────────┴──────────────────────────────────────────────────────────────────────┴─────────┴────────┴────────┴────────┘

✅ Success! Full report has been saved to 'asset_sources_report.csv'
```

This format makes it easy to filter and analyze your asset data to see which systems are providing which pieces of information.
