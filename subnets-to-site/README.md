# Subnets to site

## Overview

This script is meant to take a list of given subnets and either update an existing site or create a new site with the subnets.

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
3. SITE_ID - optional - add if you are updating an existing site
4. SITE_NAME - optional - add if you are creating a new site