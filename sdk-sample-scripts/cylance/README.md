# Custom Integration: Cylance + runZero

## Requirements

- runZero API Client Credentials
- runZero Organization ID
- Cylance Tenant ID, Application ID, and Application Secret

## Steps

### runZero Configuration

1. Update these values in the code:

- `RUNZERO_BASE_URL` - update if not using SaaS, link you use to login to runZero
- `RUNZERO_ORG_ID` - from the [runZero Organizations page](https://console.runzero.com/organizations)
- `RUNZERO_SITE_NAME` - from the [runZero Sites page](https://console.runzero.com/sites)
- `RUNZERO_CLIENT_ID` - superusers can create API clients on the [API clients page](https://console.runzero.com/account/api/clients)
- `RUNZERO_CLIENT_SECRET` - superusers can create API clients on the [API clients page](https://console.runzero.com/account/api/clients)

### Cylance configuration

1. Get your Cylance API URL

- If you use the cloud hosted version, it will be `https://protectapi.cylance.com`
- If you do not, you may need to confirm your API URL with support

2. Get your Cylance Tenant ID, Application ID, and Application Secret

- How to guide can be found [here](https://docs.blackberry.com/en/unified-endpoint-security/cylance--products/blackberry-extension-qradar-admin-guide/Install-the-extension/Create-Application-ID-and-Application-Secret)

3. Update these values in the code:

- `CYLANCE_URL` - obtained in step 1
- `CYLANCE_TENANT_ID` - obtained in step 2
- `CYLANCE_APP_ID` - obtained in step 2
- `CYLANCE_APP_SECRET` - obtained in step 2

### Running the script with then do a few things...

- Pulls the systems from Cylance
- Transforms the system data to the proper format for runZero
- Creates a Cylance Custom Integration in runZero (or get the ID if it already exists)
- Uploads the Cylance data to runZero
