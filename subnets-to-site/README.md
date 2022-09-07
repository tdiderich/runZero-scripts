# Subnets to site

## Overview

This script is meant to take a list of given subnets and either update an existing site or create a new site with the subnets.

1. Checks if it should update an existing site or create a new site
2. Gets existing site or creates template for new site based on site name
3. Updates the site payload to include all subnets from the JSON
4. Updates/creates the site

## Configuration

1. RUNZERO_ORG_TOKEN - runZero API token in .env or added to the script
2. SUBNET_FILE - path to json
3. SITE_ID - optional - add if you are updating an existing site
4. SITE_NAME - optional - add if you are creating a new site
