# Search results or scan

## Overview

This script gives you some basic stats around your scanning. For each recurring scan task, you will get these metrics...

1. new_assets_all_time - sum of the `change.newAssets` value in the scan stats 
2. offline_assets_all_time - sum of the `change.offlineAssets` value in the scan stats 
3. scan_count - total number of scans run by the task 
4. average_assets_seen - average number of assets found in the scan (new or existing)
5. max_assets_seen - most assets found in a single scan with this task 
6. min_assets_seen - leas assets found in a single scan with this task 

## Configuration

1. RUNZERO_ORG_TOKEN - runZero org API token

## Sample output 

```json
(runZero-scripts) tyler:scan-stats/ (main✗) $ python3 run.py   
{
    "dea25c14-9de6-4307-83ea-7f63ddb6b789": {
        "names": [
            "Test site - continuous scan"
        ],
        "site_ids": [
            "eba73e73-f79f-40dc-b782-cf867485353a"
        ],
        "site_names": [
            "Test"
        ],
        "new_assets_all_time": 40,
        "offline_assets_all_time": 5,
        "total_assets_seen": 264,
        "scan_count": 8,
        "average_assets_seen": 33,
        "max_assets_seen": 41,
        "min_assets_seen": 33
    },
    "9ce51c7b-e691-4e1c-8585-3c1d81f2819c": {
        "names": [
            "Primary site - continuous house scan",
            "Continuous house scan"
        ],
        "site_ids": [
            "a7b2287e-51fa-47fc-bd00-6a68eed0786b"
        ],
        "site_names": [
            "Primary"
        ],
        "new_assets_all_time": 43,
        "offline_assets_all_time": 284,
        "total_assets_seen": 7676,
        "scan_count": 228,
        "average_assets_seen": 34,
        "max_assets_seen": 46,
        "min_assets_seen": 27
    }
}
```
