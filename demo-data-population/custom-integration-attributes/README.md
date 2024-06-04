# Populate custom integrations data in demo

## Integrations currently supported

1. Fleet
2. FortiEDR
3. JAMF
4. JumpCloud
5. Tanium

## How it works

- Sample `.json` files of attributes is in this directory (these are from real integrations)
- The script then does a few things...

1. Exports a subnets of assets from demo - current search is `alive:t (type:server or type:desktop or type:laptop) has_private:t`
2. Loops through the list of integrations and grabs the sample attributes file associated with that integration
3. Creates the demo data using IP, MACs, and Hostnames from the demo export (for the asset matching) and the sample attributes from the sample attributes file (for sample data)

## Caveats

- There is no randomization in the sample attributes, so all datapoints will be the same for assets with data from that integration
- Any new additions will require a new sample `.json` file from a real integration to be created
