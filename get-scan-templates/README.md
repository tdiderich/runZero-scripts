# Get Scan Templates

This script retrieves and prints all available scan templates from your runZero account.

## Prerequisites

- Python 3.x
- `requests` library (`pip install requests`)
- A runZero account and an organization token with at least `Viewer` permissions.

## Setup

1.  **Set the Environment Variable**:
    Set the `RUNZERO_ORG_TOKEN` environment variable to your runZero organization token.

    ```bash
    export RUNZERO_ORG_TOKEN="your_token_here"
    ```

## Usage

Run the script from your terminal:

```bash
python run.py
```

The script will output a JSON object containing a list of all your scan templates.
