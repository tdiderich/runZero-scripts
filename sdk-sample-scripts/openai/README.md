# Custom Integration: OpenAI + runZero

## Requirements

- runZero API Client Credentials
- runZero Organization ID
- OpenAI API Key

## Steps

### runZero Configuration

1. Update these values in the code:

- `RUNZERO_EXPORT_TOKEN` - update
- `RUNZERO_ORG_ID` - from the [runZero Organizations page](https://console.runzero.com/organizations)
- `RUNZERO_SITE_NAME` - from the [runZero Sites page](https://console.runzero.com/sites)
- `RUNZERO_CLIENT_ID` - superusers can create API clients on the [API clients page](https://console.runzero.com/account/api/clients)
- `RUNZERO_CLIENT_SECRET` - superusers can create API clients on the [API clients page](https://console.runzero.com/account/api/clients)
- `RUNZERO_BASE_URL` - update if not using SaaS, link you use to login to runZero

### OpenAI configuration

1. Get your OpenAI API Key

- This is documented [here](https://help.openai.com/en/articles/4936850-where-do-i-find-my-api-key)
- After you are authenticated, you can create a key[ here](https://platform.openai.com/api-keys)

2. Update the `OPENAI_API_KEY` in the code

3. Fund your OpenAI account with credits (this won't work unless you have paid to use their API)

- After you are authenticated, you can update your billing account and purchase credits [here](https://platform.openai.com/account/billing/overview)
- This uses the `gpt-3.5-turbo` model by default which is a fairly low cost model
  - Input: $0.0010 / 1K tokens (1,000 tokens is about 750 words)
  - Output: $0.0020 / 1K tokens (1,000 tokens is about 750 words)

### Running the script with then do a few things...

- Pulls your vulnerabilities from runZero
- Aggregates them by asset ID
- Asks OpenAI to give a top priority recommendation for each asset
- Uploads the response for each asset as the `openai` custom integration
