# Custom Integration: JumpCloud + runZero

## Requirements

- runZero API Client Credentials
- runZero Organization ID
- JumpCloud API Key

## Steps

1. runZero Configuration

Update these values in the code:

- `RUNZERO_BASE_URL` - update if not using SaaS, link you use to login to runZero
- `RUNZERO_ORG_ID` - from the [runZero Organizations page](https://console.runzero.com/organizations)
- `RUNZERO_SITE_NAME` - from the [runZero Sites page](https://console.runzero.com/sites)
- `RUNZERO_CLIENT_ID` - superusers can create API clients on the [API clients page](https://console.runzero.com/account/api/clients)
- `RUNZERO_CLIENT_SECRET` - superusers can create API clients on the [API clients page](https://console.runzero.com/account/api/clients)

2. JumpCloud configuration

Get your JumpCloud API Key:

- Documented [here](https://docs.jumpcloud.com/api/1.0/index.html#section/API-Key)

Update this value in the code:

- `JUMPCLOUD_TOKEN` - API key captured in the steps above

3. Running the script with then do a few things...

- Pulls the systems from JumpCloud
- Transforms the system data to the proper format for runZero
- Creates a JumpCloud Custom Integration in runZero (or get the ID if it already exists)
- Uploads the JumpCloud data to runZero
