# Generate runZero Site Definitions from Active Subnets

This script generates a runZero site definition CSV for each organization in your account. The site definitions are based on the /24 subnets that have at least one asset with a status of `alive:t`. The output CSV can be imported into runZero to create a new site with a scope limited to the subnets where assets are already known to exist. This is useful for creating targeted scans of active subnets.

## How it Works

The script performs the following actions:

1.  **Fetches Organizations**: Retrieves all organizations accessible with your account token.
2.  **Gathers Assets**: For each organization, it exports all assets with a status of `alive:t`.
3.  **Calculates Subnets**: It determines the /24 subnet for each IP address associated with the assets.
4.  **Enriches Data**: If a discovered /24 subnet is part of a larger subnet already defined in a site, the script will copy the tags and description from the existing definition.
5.  **Generates CSV**: It creates a CSV file for each organization, formatted for import as a runZero site definition. The CSV is named `asset-count-by-subnet-<org_name>.csv`.

## Prerequisites

- Python 3
- `requests` library (`pip install requests`)

## Usage

1.  **Set Environment Variable**: Set the `RUNZERO_DEMO_ACCOUNT_TOKEN` environment variable with your runZero account token. You can create a token in the [runZero console](https://console.runzero.com/account).

    ```bash
    export RUNZERO_DEMO_ACCOUNT_TOKEN="<your-token>"
    ```

2.  **Run the Script**:
    ```bash
    python run.py
    ```

3.  **Import the CSV**:
    - In the runZero console, navigate to the organization where you want to create the new site.
    - Go to `Inventory` > `Sites` and click `Add a new site`.
    - Select the `Import from CSV` option.
    - Choose the generated CSV file (e.g., `asset-count-by-subnet-rz_corporation.csv`).
    - The site will be created with the subnets populated in the scope.

## Disclaimer

This script is provided as-is and is not officially supported by runZero. Use at your own risk.
