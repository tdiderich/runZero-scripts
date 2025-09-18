import requests
import os
import json

# runZero API endpoint
BASE_URL = "https://console.runzero.com/api/v1.0"
RUNZERO_ACCOUNT_TOKEN = os.environ["RUNZERO_ACCOUNT_TOKEN"]
HEADERS = {"Authorization": f"Bearer {RUNZERO_ACCOUNT_TOKEN}"}


def get_scan_templates():
    """
    Retrieves all scan templates from the runZero account.
    """
    url = f"{BASE_URL}/account/tasks/templates"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()  # Raise an exception for bad status codes
    return response.json()


def create_scan_template(name, description, acl, organization_id):
    """
    Creates a new scan template.
    """
    url = f"{BASE_URL}/account/tasks/templates"
    data = {
        "name": name,
        "description": description,
        "acl": acl,
        "organization_id": organization_id,
    }
    response = requests.post(url, headers=HEADERS, json=data)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    try:
        templates = get_scan_templates()
        if templates:
            # Use the acl and organization_id from the first template
            template_to_copy = templates[0]
            acl = template_to_copy.get("acl", {})
            organization_id = template_to_copy.get("organization_id")

            new_template_name = "API Created Template"
            new_template_description = "This template was created via the API."

            new_template = create_scan_template(
                new_template_name,
                new_template_description,
                acl,
                organization_id,
            )
            print("Successfully created new template:")
            print(json.dumps(new_template, indent=4))
        else:
            print("No existing scan templates found to copy.")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")