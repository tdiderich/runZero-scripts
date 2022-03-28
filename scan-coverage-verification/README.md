# Scan coverage verification

## Overview

This script is meant to verify you have full scan coverage in Rumble based on a given json array. It does a few things...

1. Gets all sites
2. Gets all recurring scan tasks
3. Gets the json of subnets
4. Checks that all subnets are in a site
5. Checks that all subnets are in a recurring scan task
6. Adds new subnets to a given site 
7. Adds new subnets to a given recurring subtask 

## Configuration

1. RUMBLE_ORG_TOKEN - Rumble API token in .env or added to the script
2. SUBNET_FILE - path to json
3. DEFAULT_SITE - ID for site to add new subnets to 
4. DEFAULT_TASK - ID for the recurring scan task to add new subnets to 