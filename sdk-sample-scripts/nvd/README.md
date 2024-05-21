# Custom Integration: NIST NVD + runZero

## Requirements

- runZero API Client Credentials
- runZero Organization ID
- NIST NVD API Key

## Steps

### runZero Configuration

1. Update these values in the code:

- `RUNZERO_BASE_URL` - update if not using SaaS, link you use to login to runZero
- `RUNZERO_ORG_ID` - from the [runZero Organizations page](https://console.runzero.com/organizations)
- `RUNZERO_SITE_NAME` - from the [runZero Sites page](https://console.runzero.com/sites)
- `RUNZERO_CLIENT_ID` - superusers can create API clients on the [API clients page](https://console.runzero.com/account/api/clients)
- `RUNZERO_CLIENT_SECRET` - superusers can create API clients on the [API clients page](https://console.runzero.com/account/api/clients)

### NIST NVD configuration

1. Get your NVD API Key:

- Request your API key [here](https://nvd.nist.gov/developers/request-an-api-key)
- You should receive an email within a few minutes with a link to get your API key

2. Update this value in the code:

- `NVD_API_KEY` - API key captured in the steps above

### Running the script with then do a few things...

- Pulls the services from runZero with the `service.cpe23` attribute
- Loops the services to get the CPEs and service data 
- Enriches the information by using the CPE to query the NVD to get CVEs
- Uploads the vulnerabilities to the runZero asset with the CVE as the name