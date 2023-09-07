# Custom Integration: Fleet + runZero

## Requirements

- runZero API Client Credentials
- runZero Organization ID
- Fleet API User

## Steps

### runZero Configuration

1. Update these values in the code:

- `RUNZERO_BASE_URL` - update if not using SaaS, link you use to login to runZero
- `RUNZERO_ORG_ID` - from the [runZero Organizations page](https://console.runzero.com/organizations)
- `RUNZERO_SITE_NAME` - from the [runZero Sites page](https://console.runzero.com/sites)
- `RUNZERO_CLIENT_ID` - superusers can create API clients on the [API clients page](https://console.runzero.com/account/api/clients)
- `RUNZERO_CLIENT_SECRET` - superusers can create API clients on the [API clients page](https://console.runzero.com/account/api/clients)

### Fleet configuration

1. Create your Fleet API User:

- Fleet recommends creating an API user to make API calls
- This is documented [here](https://fleetdm.com/docs/using-fleet/fleetctl-cli#create-an-api-only-user)

2. Update this value in the code:

- `FLEET_URL` - URL used to login to fleet
- `FLEETDM_EMAIL` - Email for API user account
- `FLEETDM_PASSWORD` - Password for API user account

### Running the script with then do a few things...

- Pulls the hosts from Fleet
- Transforms the client data to the proper format for runZero
- Creates a Fleet Custom Integration in runZero (or get the ID if it already exists)
- Uploads the Fleet data to runZero
