import requests
import os
import json

TANIUM_URL = os.environ["TANIUM_URL"]
TANIUM_TOKEN = os.environ["TANIUM_TOKEN"]


def get_endpoints():
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
    cursor = None
    hasNextPage = True
    endpoints = []
    while hasNextPage:

        # set cursor if it exists (all but the first query)
        if cursor:
            variables = {"first": 100, "after": cursor}
        else:
            variables = {"first": 100}

        # get endpoints
        data = requests.post(TANIUM_URL + "/plugin/products/gateway/graphql",
                             headers={"Content-Type": "application/json", "session": TANIUM_TOKEN}, json={'query': query, 'variables': variables})

        # grab data from the response
        endpoints.extend(data.json()["data"]["endpoints"]["edges"])
        hasNextPage = data.json(
        )["data"]["endpoints"]["pageInfo"]["hasNextPage"]
        cursor = data.json()["data"]["endpoints"]["pageInfo"]["startCursor"]

    print("Final endpoint list:\n", json.dumps(endpoints, indent=4))


if __name__ == "__main__":
    get_endpoints()
