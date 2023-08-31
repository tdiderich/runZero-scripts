# Custom Integration: FortiEDR + runZero

## Requirements

- runZero API Client Credentials
- runZero Organization ID
- FortiEDR Basic Authentication Key
- FortiEDR Console URL

## Steps

1. runZero configuration

Update these values in the code:

- `RUNZERO_BASE_URL` - update if not using SaaS, link you use to login to runZero
- `RUNZERO_ORG_ID` - from the [runZero Organizations page](https://console.runzero.com/organizations)
- `RUNZERO_SITE_NAME` - from the [runZero Sites page](https://console.runzero.com/sites)
- `RUNZERO_CLIENT_ID` - superusers can create API clients on the [API clients page](https://console.runzero.com/account/api/clients)
- `RUNZERO_CLIENT_SECRET` - superusers can create API clients on the [API clients page](https://console.runzero.com/account/api/clients)

2. FortiEDR configuration

Get our FortiEDR API key:

- Configure a FortiEDR user with a Rest API role, as described in the Basic Authentication section on page 9.
- Encode the user and password in base64: `echo -n "user:password" | base64`.

Update these values in the code:

- `FORTI_KEY` - output of the step above
- `FORTI_BASE_URL` - link you use to login to FortiEDR

3. Running the script with then do a few things...

- Pull the collectors from FortiEDR
- Transform the collector data to the proper format for runZero
- Create a FortiEDR Custom Integration in runZero (or get the id if it already exists)
- Upload the FortEDR collector data to runZero
