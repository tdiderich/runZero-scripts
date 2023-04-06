# runZero Script HUB

## Background

Requirements (Global)

- Python 3.8+
- pipenv - https://pypi.org/project/pipenv/

## runZero API Docs

- How to use the API - https://www.runZero.com/docs/organization-api/
- Swagger - https://app.swaggerhub.com/apis-docs/runZeroDiscovery/runZero/2.11.0#/

## Configuration Explained

- There is a sample environment variables file called .env_sample under the root folder of this project
- You will clone this file and create one called .env where you actually input all of your secrets (API Keys + Access Key Pairs)
- Parameters - explanations of what you see in .env_sample

```
RUNZERO_ORG_TOKEN - used to for management
RUNZERO_EXPORT_TOKEN - used for data export
```

## Getting Started

- Clone this repository

```
git clone https://github.com/tdiderich/runZero.git
```

- Clone .env_sample to .env under the same directory

```
cp .env_sample .env
```

- Update all of the secrets in the `.env` needed based on the script you'd like to run (NOTE: you need to rerun pipenv shell anytime you update these values to reload them)

- Install dependancies

```
pipenv install -r requirements.txt
```

- Enter pipenv

```
pipenv shell
```

- Run scripts

```
python3 starter/run.py
```
