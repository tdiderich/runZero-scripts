# Custom Integration: JAMF + runZero (multithreaded test version)

## Requirements

- runZero API Client Credentials
- runZero Organization ID
- JAMF API Role and Client

## Steps

### runZero Configuration

1. Update these values in the code:

- `RUNZERO_BASE_URL` - update if not using SaaS, link you use to login to runZero
- `RUNZERO_ORG_ID` - from the [runZero Organizations page](https://console.runzero.com/organizations)
- `RUNZERO_SITE_NAME` - from the [runZero Sites page](https://console.runzero.com/sites)
- `RUNZERO_CLIENT_ID` - superusers can create API clients on the [API clients page](https://console.runzero.com/account/api/clients)
- `RUNZERO_CLIENT_SECRET` - superusers can create API clients on the [API clients page](https://console.runzero.com/account/api/clients)

### JAMF configuration

1. Create a API Role and Client in JAMF:

- Documented [here](https://learn.jamf.com/bundle/jamf-pro-documentation-current/page/API_Roles_and_Clients.html)
- Role permission required is `Read Computers`

2. Update these values in the code:

- `JAMF_ID` - Client ID created above
- `JAMF_SECRET` - Client Secret created above
- `JAMF_URL` - URL you login to JAMF with

### Running the script with then do a few things...

- Pulls the systems from JAMF
- Pulls extra information for each asset not in the basic export
- Transforms the system data to the proper format for runZero
- Creates a JAMF Custom Integration in runZero (or gets the ID if it already exists)
- Uploads the JAMF data to runZero
