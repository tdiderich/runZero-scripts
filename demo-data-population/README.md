# Populate demo data in runZero

## Sources currently supported

1. runZero scan
2. CrowdStrike integration
3. Nessus integration

## How it works

- This script uses real data to generate fake runZero tasks
- There are data maps that randomize the asset types + add integration data in cases that make sense
- The output files can be gzip-ed + uploaded to a tenant to populate the inventory

## Creating files and uploading 

### Prerequisites

1. In order to create new scan and intgration tasks, you need to `gunzip` all of the files in the `tasks` directory 
2. Update all of the global config values 

- `RUNZERO_BASE_URL` - URL to your runZero tenant + `/api/v1.0`
- `RUNZERO_ORG_ID` - Org ID to upload the tasks to
- `RUNZERO_SITE_ID` - Site ID to associate the assets with 
- `RUNZERO_ORG_TOKEN` = Org Token to authenticate 
- `JAMF_CUSTOM_INTEGRATION_ID` - you need to go create this custom integration and grab the ID after creating for JAMF data to be added


### Sample running of the script 

**What the options do:** 
1. `--create` - create new assets rather than use existing files.
2. `--delete` - delete the existing assets in the organization based on the `SITE_ID` provided.
3. `--upload` - upload the scan and integration tasks.
4. `--assets-per-subnet=100` - how many assets per subnet should be created. There are 15 subnets used, so you will get N * 15 assets based on your input here. The defaults to 5 if you do not pass it. 

**Output:**
```
$ python3 demo_data.py --create --delete --upload --assets-per-subnet=100
STARTING - asset creation
SUCCESS - created 1000 HQ + HQ BACNET assets
SUCCESS - created 1000 DC + DC BACNET assets
SUCCESS - created 500 CLOUD assets
SUCCESS - created task for rz scan
SUCCESS - created task for crowdstrike
SUCCESS - created task for nessus
SUCCESS - created task for aws
SUCCESS - created task for azuread
SUCCESS - created task for jamf
STARTING - asset deletion
IN PROGRESS - runZero is deleting the assets
SUCCESS - all assets deleted
STARTING - uploading tasks to runZero
SUCCESS - uploaded scan_output.json
SUCCESS - uploaded integration_crowdstrike.json
SUCCESS - uploaded integration_nessus.json
SUCCESS - uploaded integration_aws.json
SUCCESS - uploaded integration_azuread.json
SUCCESS - uploaded integration_jamf.json
```

