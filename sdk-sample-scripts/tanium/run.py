import requests
import os
import json

TANIUM_URL = os.environ["TANIUM_URL"]
TANIUM_TOKEN = os.environ["TANIUM_TOKEN"]


query = """query getEndpoints($first: Int, $after: Cursor) {
  endpoints(first: $first, after: $after) {
    edges {
      node {
        computerID
        name
        serialNumber
        ipAddress
      }
    }
    pageInfo {
      hasNextPage
      endCursor
      startCursor
    }
    totalRecords
  }
}"""


def get_endpoints():
    cursor = None
    hasNextPage = True
    endpoints = []
    while hasNextPage:
        if cursor:
            variables = {"first": 100, "after": cursor}
        else:
            variables = {"first": 100}

        data = requests.post(TANIUM_URL + "/plugin/products/gateway/graphql",
                             headers={"Content-Type": "application/json", "session": TANIUM_TOKEN}, json={'query': query, 'variables': variables})
        print(json.dumps(data.json(), indent=4))
        endpoints.extend(data.json()["data"]["endpoints"]["edges"])
        hasNextPage = data.json(
        )["data"]["endpoints"]["pageInfo"]["hasNextPage"]
        cursor = data.json()["data"]["endpoints"]["pageInfo"]["startCursor"]

    print("Final endpoint list:\n", json.dumps(endpoints, indent=4))


if __name__ == "__main__":
    get_endpoints()
