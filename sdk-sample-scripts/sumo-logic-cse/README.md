# Custom Integration: Sumo Logic + runZero

## Requirements

- runZero API Client Credentials
- runZero Organization ID
- Sumo Logic Tenant ID, Application ID, and Application Secret

## Steps

### runZero Configuration

1. Update these values in the code:

- `RUNZERO_BASE_URL` - update if not using SaaS, link you use to login to runZero
- `RUNZERO_ORG_ID` - from the [runZero Organizations page](https://console.runzero.com/organizations)
- `RUNZERO_SITE_NAME` - from the [runZero Sites page](https://console.runzero.com/sites)
- `RUNZERO_CLIENT_ID` - superusers can create API clients on the [API clients page](https://console.runzero.com/account/api/clients)
- `RUNZERO_CLIENT_SECRET` - superusers can create API clients on the [API clients page](https://console.runzero.com/account/api/clients)

### Sumo Logic configuration

1. Get your Sumo Logic API URL

- Options [here](https://help.sumologic.com/docs/api/getting-started/)
- Pick based on the URL you use to login

2. Get your Sumo Logic Access ID and Access Key

- How to guide can be found [here](https://help.sumologic.com/docs/manage/security/access-keys/)

3. Update these values in the code:

- `SUMO_URL` - obtained in step 1
- `SUMO_ID` - obtained in step 2
- `SUMO_KEY` - obtained in step 2

### Running the script with then do a few things...

- Pulls the entities from Sumo Logic CSE
- Transforms the system data to the proper format for runZero
- Creates a Sumo Logic (`sumologic-cse`) Custom Integration in runZero (or get the ID if it already exists)
- Uploads the Sumo Logic data to runZero
