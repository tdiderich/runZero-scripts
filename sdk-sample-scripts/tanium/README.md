# Custom Integration: Tanium + runZero

## Requirements

- runZero API Client Credentials
- runZero Organization ID
- Tanium API Key

## Steps

1. runZero Configuration

Update these values in the code:

- `RUNZERO_BASE_URL` - update if not using SaaS, link you use to login to runZero
- `RUNZERO_ORG_ID` - from the [runZero Organizations page](https://console.runzero.com/organizations)
- `RUNZERO_SITE_NAME` - from the [runZero Sites page](https://console.runzero.com/sites)
- `RUNZERO_CLIENT_ID` - superusers can create API clients on the [API clients page](https://console.runzero.com/account/api/clients)
- `RUNZERO_CLIENT_SECRET` - superusers can create API clients on the [API clients page](https://console.runzero.com/account/api/clients)

2. Tanium configuration

Get your Tanium API Key:

- Documented [here](https://docs.tanium.com/platform_user/platform_user/console_api_tokens.html?cloud=true)

Update this value in the code:

- `TANIUM_TOKEN` - API key captured in the steps above
- `TANIUM_URL` - URL you use to login to Tanium

3. Running the script with then do a few things...

- Pulls the clients from Tanium
- Transforms the client data to the proper format for runZero
- Creates a Tanium Custom Integration in runZero (or get the ID if it already exists)
- Uploads the Tanium data to runZero
