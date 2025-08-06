# Populate demo data in runZero

This script generates and uploads realistic demo data to a runZero organization. It creates assets, populates them with data from various sources, and uploads them as scan and integration tasks.

## Supported Data Sources

The script can generate data mimicking the following sources:

-   runZero Scan
-   CrowdStrike
-   Nessus
-   AWS
-   Microsoft Azure AD
-   Jamf
-   Qualys
-   Wiz

## How It Works

1.  **Asset Generation**: The script uses a library of real-world asset templates (servers, laptops, network devices, IoT, OT, etc.). It randomizes and combines these templates to create a diverse set of assets.
2.  **IP and MAC Address Randomization**: It assigns semi-randomized IP and MAC addresses to the generated assets to ensure uniqueness while maintaining realistic network structures.
3.  **Integration Data Simulation**: For each supported integration, the script has data maps that add relevant attributes to the assets. For example, it can add CrowdStrike agent information to endpoints or AWS instance details to cloud servers.
4.  **Task File Creation**: The script outputs the generated data into gzip-compressed JSON files, one for the runZero scan and one for each integration. These files are formatted to be uploaded directly to runZero.

## Setup and Prerequisites

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Set Environment Variables**: The script requires API credentials and IDs for your runZero organization. You can set these in your shell environment or a `.env` file.

    -   `RUNZERO_BASE_URL`: The base URL of your runZero console (e.g., `https://console.runzero.com/api/v1.0`).
    -   `RUNZERO_ORG_ID`: The ID of the organization to upload data to.
    -   `RUNZERO_SITE_ID`: The ID of the site to associate the assets with.
    -   `RUNZERO_ORG_TOKEN`: An organization API key with at least `Uploader` permissions.
    -   `JAMF_CUSTOM_INTEGRATION_ID`: The ID of a custom integration in runZero to use for Jamf data. You must create this manually first.

3.  **Unzip Task Templates**: Before running the script with the `--create` flag, you need to decompress the template files in the `tasks` directory:
    ```bash
    gunzip demo-data-population/tasks/*.gz
    ```

## Usage

The script is controlled via command-line arguments.

### Command-Line Options

-   `--create`: Generate new demo data files.
-   `--delete`: Delete all existing assets within the configured `RUNZERO_SITE_ID` before uploading new data.
-   `--upload`: Upload the generated data files to the runZero organization.
-   `--assets-per-subnet`: The number of assets to create per subnet. The script uses several predefined subnets, so the total number of assets will be a multiple of this value. Defaults to `5`.
-   `--env`: Specify the environment (`demo` or `prod`). This determines which set of environment variables to use (e.g., `RUNZERO_DEMO_ORG_ID` vs. `RUNZERO_ORG_ID`).

### Example Workflow

This example command will delete existing assets in the site, create 50 new assets per subnet, and upload the resulting data to runZero.

```bash
python3 demo-data-population/run.py --delete --create --upload --assets-per-subnet=50
```

### Expected Output

```
STARTING - asset creation
SUCCESS - created 500 HQ assets
SUCCESS - created 50 HQ-BACNET assets
SUCCESS - created 500 DC assets
SUCCESS - created 50 DC-BACNET assets
SUCCESS - created 250 CLOUD assets
SUCCESS - created task for rz scan
SUCCESS - created task for crowdstrike
SUCCESS - created task for nessus
SUCCESS - created task for aws
SUCCESS - created task for azuread
SUCCESS - created task for jamf
SUCCESS - created task for qualys
SUCCESS - created task for wiz
STARTING - asset deletion
IN PROGRESS - runZero is deleting the assets
SUCCESS - all assets deleted
STARTING - uploading tasks to runZero
SUCCESS - uploaded scan_output.json.gz
SUCCESS - uploaded integration_crowdstrike.json.gz
SUCCESS - uploaded integration_nessus.json.gz
SUCCESS - uploaded integration_aws.json.gz
SUCCESS - uploaded integration_azuread.json.gz
SUCCESS - uploaded integration_jamf.json.gz
SUCCESS - uploaded integration_qualys.json.gz
SUCCESS - uploaded integration_wiz.json.gz
```