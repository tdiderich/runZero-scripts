# Search results or scan

## Overview

This script allows you to get the runZero info on an IP OR scan it depending on what comes back. It does a few things...

1. Searches for an IP
2. IF results

- Returns results

3. ELSE

- Initiates scans of IP
- Checks status of scan until it's complete
- Searches for the IP
- Returns results OR returns nothing if the IP scan came back empty

## Configuration

1. RUNZERO_ORG_TOKEN - runZero API token in .env or added to the script
2. SUBNET_FILE - path to json
3. DEFAULT_SITE - ID for site to add new subnets to
4. DEFAULT_TASK - ID for the recurring scan task to add new subnets to
