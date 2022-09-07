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

1. RUNZERO_EXPORT_TOKEN - runZero export token
2. RUNZERO_ORG_TOKEN - runZero org API token
3. SITE_ID - site you want the asset associated with (UUID)
4. EXPLORER_ID - explorer you want to run the scan if needed
