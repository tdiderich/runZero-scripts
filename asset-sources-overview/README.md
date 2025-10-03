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
$ python3 run.py                                                                                         [10:47:03]
✅ Success! Your hybrid report has been written to 'asset_sources_report.csv'

$ for id in $(tail -n +2 asset_sources_report.csv | cut -d, -f1 | sort -u | tr -d '\r'); do             [11:14:58]
    echo "\n--- Asset ID: $id ---"
    csvgrep -c asset_id -m "$id" asset_sources_report.csv > temp_asset.csv
    rich --csv temp_asset.csv
    rm temp_asset.csv
done

--- Asset ID: 001852cc-da1e-4f5e-936c-b215344589aa ---
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━┓
┃ asset_id                             ┃ source      ┃ type  ┃ value             ┃ aws ┃ azuread ┃ crowdstrike ┃ custom ┃ nessus ┃ qualys ┃ rumble ┃ wiz ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━┩
│ 001852cc-da1e-4f5e-936c-b215344589aa │ azuread     │ names │ RZDC-SERVER-1245  │ ❌  │ ✅      │ ✅          │ ❌     │ ✅     │ ❌     │ ✅     │ ❌  │
│ 001852cc-da1e-4f5e-936c-b215344589aa │ crowdstrike │ addrs │ 10.0.12.45        │ ❌  │ ✅      │ ✅          │ ❌     │ ✅     │ ❌     │ ✅     │ ❌  │
│ 001852cc-da1e-4f5e-936c-b215344589aa │ crowdstrike │ macs  │ 19:3c:1f:a5:d1:4b │ ❌  │ ✅      │ ✅          │ ❌     │ ✅     │ ❌     │ ✅     │ ❌  │
│ 001852cc-da1e-4f5e-936c-b215344589aa │ crowdstrike │ names │ RZDC-SERVER-1245  │ ❌  │ ✅      │ ✅          │ ❌     │ ✅     │ ❌     │ ✅     │ ❌  │
│ 001852cc-da1e-4f5e-936c-b215344589aa │ nessus      │ addrs │ 10.0.12.45        │ ❌  │ ✅      │ ✅          │ ❌     │ ✅     │ ❌     │ ✅     │ ❌  │
│ 001852cc-da1e-4f5e-936c-b215344589aa │ nessus      │ macs  │ 19:3c:1f:a5:d1:4b │ ❌  │ ✅      │ ✅          │ ❌     │ ✅     │ ❌     │ ✅     │ ❌  │
│ 001852cc-da1e-4f5e-936c-b215344589aa │ rumble      │ addrs │ 10.0.12.45        │ ❌  │ ✅      │ ✅          │ ❌     │ ✅     │ ❌     │ ✅     │ ❌  │
│ 001852cc-da1e-4f5e-936c-b215344589aa │ rumble      │ macs  │ 19:3c:1f:a5:d1:4b │ ❌  │ ✅      │ ✅          │ ❌     │ ✅     │ ❌     │ ✅     │ ❌  │
│ 001852cc-da1e-4f5e-936c-b215344589aa │ rumble      │ names │ RZDC-SERVER-1245  │ ❌  │ ✅      │ ✅          │ ❌     │ ✅     │ ❌     │ ✅     │ ❌  │
└──────────────────────────────────────┴─────────────┴───────┴───────────────────┴─────┴─────────┴─────────────┴────────┴────────┴────────┴────────┴─────┘

--- Asset ID: 01845493-75a2-4c86-b239-cd7165704804 ---
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━┓
┃ asset_id                             ┃ source  ┃ type  ┃ value                ┃ aws ┃ azuread ┃ crowdstrike ┃ custom ┃ nessus ┃ qualys ┃ rumble ┃ wiz ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━┩
│ 01845493-75a2-4c86-b239-cd7165704804 │ azuread │ names │ RZBACNET-SERVER-2045 │ ❌  │ ✅      │ ❌          │ ❌     │ ✅     │ ❌     │ ✅     │ ❌  │
│ 01845493-75a2-4c86-b239-cd7165704804 │ nessus  │ addrs │ 10.0.20.45           │ ❌  │ ✅      │ ❌          │ ❌     │ ✅     │ ❌     │ ✅     │ ❌  │
│ 01845493-75a2-4c86-b239-cd7165704804 │ nessus  │ macs  │ 19:3c:1f:f6:ab:f9    │ ❌  │ ✅      │ ❌          │ ❌     │ ✅     │ ❌     │ ✅     │ ❌  │
│ 01845493-75a2-4c86-b239-cd7165704804 │ rumble  │ addrs │ 10.0.20.45           │ ❌  │ ✅      │ ❌          │ ❌     │ ✅     │ ❌     │ ✅     │ ❌  │
│ 01845493-75a2-4c86-b239-cd7165704804 │ rumble  │ macs  │ 19:3c:1f:f6:ab:f9    │ ❌  │ ✅      │ ❌          │ ❌     │ ✅     │ ❌     │ ✅     │ ❌  │
│ 01845493-75a2-4c86-b239-cd7165704804 │ rumble  │ names │ RZBACNET-SERVER-2045 │ ❌  │ ✅      │ ❌          │ ❌     │ ✅     │ ❌     │ ✅     │ ❌  │
└──────────────────────────────────────┴─────────┴───────┴──────────────────────┴─────┴─────────┴─────────────┴────────┴────────┴────────┴────────┴─────┘
```

This format makes it easy to filter and analyze your asset data to see which systems are providing which pieces of information.
