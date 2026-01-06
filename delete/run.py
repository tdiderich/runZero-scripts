import requests
import os
import time
import random
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# Using your existing configuration
RUNZERO_ORG_TOKEN = os.environ.get("RUNZERO_ORG_TOKEN")
HEADERS = {"Authorization": f"Bearer {RUNZERO_ORG_TOKEN}"}
BASE_URL = "https://console.runZero.com/api/v1.0"
SEARCH = "alive:f"


def get_delete_ids():
    url = f"{BASE_URL}/export/org/assets.json"
    response = requests.get(
        url=url, headers=HEADERS, params={"search": SEARCH, "fields": "id"}
    )

    if response.status_code == 200:
        return [x["id"] for x in response.json()]
    else:
        print(f"Error fetching IDs: {response.status_code}")
        return []


def chunker(data):
    """Yield successive chunks with random sizes (multiples of 10 from 10 to 100)."""
    i = 0
    while i < len(data):
        # Choose a random size: 10, 20, 30... up to 100
        size = random.randrange(10, 110, 10)
        yield data[i : i + size]
        i += size

# Setup a session with automatic retries for basic network hiccups
session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retries))


def delete_assets(asset_chunk: list, attempt=1):
    """Deletes a batch with recursive retry logic for RemoteDisconnected errors."""
    url = f"{BASE_URL}/org/assets/bulk/delete"
    MAX_ATTEMPTS = 3

    start_time = time.perf_counter()

    try:
        # Use session instead of requests.delete
        # Setting a specific timeout (connect, read)
        response = session.delete(
            url, headers=HEADERS, json={"asset_ids": asset_chunk}, timeout=(10, 60)
        )
        duration = time.perf_counter() - start_time

        if response.status_code == 204:
            print(
                f"Batch Size: {len(asset_chunk):<3} | Duration: {duration:.3f}s | Success"
            )
            return True
        else:
            print(f"Server returned {response.status_code}: {response.text}")
            return False

    except (
        requests.exceptions.ConnectionError,
        requests.exceptions.ChunkedEncodingError,
    ) as e:
        if attempt <= MAX_ATTEMPTS:
            wait = attempt * 5
            print(
                f"⚠️ Connection dropped. Attempt {attempt}/{MAX_ATTEMPTS}. Retrying in {wait}s..."
            )
            time.sleep(wait)
            return delete_assets(asset_chunk, attempt + 1)
        else:
            print(f"❌ Failed after {MAX_ATTEMPTS} attempts due to connection issues.")
            return False


def main():
    assets = get_delete_ids()
    if not assets:
        print("No assets found.")
        return

    print(f"Found {len(assets)} assets. Starting deletion...")

    for chunk in chunker(assets):
        success = delete_assets(chunk)
        if not success:
            # If a batch fails completely, we might want to pause longer
            # to let the server recover
            time.sleep(10)

        # Standard cooling period between batches
        time.sleep(1.5)


if __name__ == "__main__":
    main()
