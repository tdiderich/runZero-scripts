# Subnet utilization reporting 

## Overview 
This script exports your assets based on a given search and provides some basic stats around IP usage.

1. Unique IPs used - unique IPs used by site 
2. Subnet utilization - % of each /24, /16, or /8 used

## Configuration

1. RUNZERO_ORG_TOKEN - runZero org API token
2. RUNZERO_EXPORT_TOKEN - runZero export API token
2. SEARCH - runZero search for assets you'd like included in your report 

## Outputs

1. `unique_ips_full.csv` - CSV with these headers related to unique IPs used per site `site_id,site_name,unique_ip_count,unique_ip_list`
2. `unique_ips_min.csv` - CSV with these headers related to unique IPs used per site `site_id,site_name,unique_ip_count`
3. `utilization_report.csv` - CSV with these headers related to utilization per subnet based on selected range size `site_id,site_name,range,ip_count,utilization`