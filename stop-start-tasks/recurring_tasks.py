import json
import datetime
import requests
from enum import Enum
from tenacity import retry, stop_after_attempt, wait_fixed


class RestRequest:
    def _init_(self, method, url, params=None, data=None, headers=None):
        self.method = method
        self.url = url
        self.params = params or {}
        self.data = data or {}
        self.headers = headers or {}

    def execute(self):
        response = requests.request(
            self.method,
            self.url,
            params=self.params,
            data=self.data,
            headers=self.headers,
        )
        return response


class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


TOKEN_ENDPOINT = "account/api/token"
EXPLORER_UPDATE_ENDPOINT = "org/explorers/{explorer_id}/update"
CREATE_SCAN_ENDPOINT = "org/sites/{site_id}/scan"
GET_TASK_ENDPOINT = "org/tasks/{task_id}"
GET_AGENTS_ENDPOINT = "org/agents/{agent_id}"
SCAN_RATE = "10000"
PROBES = "arp"
SCREEN_SHOTS = "false"
DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_api_token():
    client_info = get_runzero_client_info()
    headers = {"accept": "application/json"}
    data = {
        "grant_type": "client_credentials",
        "client_id": client_info["client_id"],
        "client_secret": client_info["client_secret"],
    }
    request = RestRequest(
        method=HTTPMethod.POST.name,
        url=f"{BASE_URL}{TOKEN_ENDPOINT}",
        headers=headers,
        data=data,
    )
    response = request.execute()
    if response.status_code != 200:
        raise Exception(
            f"Error fetching api token from {str(TOKEN_ENDPOINT)}: {response.json()}"
        )
    else:
        api_token = response.json()["access_token"]
        print("Fetched api token")
        return api_token


def get_runzero_client_info():
    return get_secret_value_json(API_CLIENT_INFO_SECRET, REGION)


def update_explorer(api_token):
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }
    parameters = {"_oid": ORGANIZATION_ID}
    data = {"site_id": SITE_ID}
    request = RestRequest(
        method=HTTPMethod.POST.name,
        url=f"{BASE_URL}{EXPLORER_UPDATE_ENDPOINT.format(explorer_id=EXPLORER_ID)}",
        headers=headers,
        params=parameters,
        data=json.dumps(data),
    )
    response = request.execute()
    if response.status_code != 204:
        raise Exception(
            f"Error restarting and updating explorer from {str(EXPLORER_UPDATE_ENDPOINT)}: {response.json()}"
        )
    else:
        print(f"Updated and restarted explorer {EXPLORER_ID}")


def verify_explorer_status(api_token):
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }
    parameters = {
        "agent_id": EXPLORER_ID,
        "_oid": ORGANIZATION_ID,
    }
    request = RestRequest(
        method=HTTPMethod.GET.name,
        url=f"{BASE_URL}{GET_AGENTS_ENDPOINT.format(agent_id=EXPLORER_ID)}",
        headers=headers,
        params=parameters,
    )
    response = request.execute()
    if response.status_code != 200:
        raise Exception(
            f"Error fetching agent information for explorer {EXPLORER_ID}: {response.json()}"
        )
    assert response.json()["connected"]
    print(f"Verified explorer {EXPLORER_ID} is online")


def start_scan(api_token):
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }
    parameters = {"_oid": ORGANIZATION_ID}
    data = {
        "targets": TARGETS,
        "scan-name": f"Canary Test {datetime.now().strftime(DATE_TIME_FORMAT)}",
        "rate": SCAN_RATE,
        "probes": PROBES,
        "screenshots": SCREEN_SHOTS,
    }
    request = RestRequest(
        method=HTTPMethod.PUT.name,
        url=f"{BASE_URL}{CREATE_SCAN_ENDPOINT.format(site_id=SITE_ID)}",
        headers=headers,
        params=parameters,
        data=json.dumps(data),
    )
    response = request.execute()
    response_json = response.json()
    if response.status_code != 200:
        raise Exception(f"Error starting scan {response_json}")
    elif response_json["error"]:
        raise Exception(
            f"Error {response_json['error']} when starting scan {response_json['id']}"
        )
    print(f"Started scan {response_json['id']}")
    return response_json["id"]


@retry(wait=wait_fixed(30), stop=stop_after_attempt(15))
def validate_scan_completion(api_token, task_id):
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }
    parameters = {
        "task_id": task_id,
        "_oid": ORGANIZATION_ID,
    }
    request = RestRequest(
        method=HTTPMethod.GET.name,
        url=f"{BASE_URL}{GET_TASK_ENDPOINT.format(task_id=task_id)}",
        headers=headers,
        params=parameters,
    )
    response = request.execute()
    response_json = response.json()
    task_status = response_json["status"]
    assert task_status == "processed"
    print(f"Processed scan {task_id}")
    total_assets = response.json()["stats"].get("change.totalAssets")
    assert total_assets == EXPECTED_ASSET_COUNT, "Invalid total assets count"
    print(f"Verified total asset count to be expected: {EXPECTED_ASSET_COUNT}")


def canary_test():
    try:
        api_token = get_api_token()
        update_explorer(api_token)
        verify_explorer_status(api_token)
        task_id = start_scan(api_token)
        validate_scan_completion(api_token, task_id)
    except Exception as e:
        raise Exception(f"Failed canary test: {e}")
