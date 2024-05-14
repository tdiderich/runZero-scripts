# Subnet Risk Reporting

This script will 

You could also add your own searches based on your requirements. To do this, just add them to the CSV file. 

# Output

1. `GLOBAL_RISK.csv` - this is a joined CSV of all subnets across all orgs with each subnet risk level reported
2. `Individual Organizations` - folder created called `org_name` with `risk_by_subnet.csv` with that Organizations subnets shown by risk level
3. `Individual Oranizations - Search Types` - `asset` and `services` folders will have results for individual searches added to the `SEARCHES` variable at the top of the script which shows total matches, sum of risk, and sum of criticality
