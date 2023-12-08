import requests
import os
import json
from flatten_json import flatten
from ipaddress import ip_address
from typing import Any, Dict, List
import runzero
from runzero.client import AuthError
from runzero.api import CustomAssets, CustomIntegrationsAdmin, Sites, Tasks
from runzero.types import (
    ImportAsset,
    IPv4Address,
    IPv6Address,
    NetworkInterface,
    ImportTask,
)

from openai import OpenAI

RUNZERO_EXPORT_TOKEN = os.environ["RUNZERO_EXPORT_TOKEN"]
RUNZERO_CLIENT_ID = os.environ["RUNZERO_CLIENT_ID"]
RUNZERO_CLIENT_SECRET = os.environ["RUNZERO_CLIENT_SECRET"]
RUNZERO_ORG_ID = os.environ["RUNZERO_ORG_ID"]
RUNZERO_SITE_NAME = os.environ["RUNZERO_SITE_NAME"]
RUNZERO_BASE_URL = "https://console.runzero.com/api/v1.0"
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]


def openai_chat(vulns: list):
    openai = OpenAI(api_key=OPENAI_API_KEY)
    messages = [
        {
            "role": "system",
            "content": "You are going to be our security advisor assist in vulnerability response. I am going to send you a set of vulnerabilities found on an asset along with some basic information like how many services the asset is running, operating system info, and hardware info. Please provide the top priority action item for improving the security posture of the asset. This response should be less than 1000 characters.",
        }
    ]
    for i, v in enumerate(vulns):
        if i < 4:
            messages.append({"role": "user", "content": f"Vulnerability {i}: {v}"})
    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo", messages=messages
    )
    return str(completion.choices[0].message.content)


def import_data_to_runzero(name: str, assets: List[ImportAsset]):
    """
    The code below gives an example of how to create a custom source and upload valid assets from a CSV to a site using
    the new custom source.
    """
    # create the runzero client
    c = runzero.Client(server_url="https://console.runzero.com")

    # try to log in using OAuth credentials
    try:
        c.oauth_login(RUNZERO_CLIENT_ID, RUNZERO_CLIENT_SECRET)
    except AuthError as e:
        print(f"login failed: {e}")
        return

    # create the site manager to get our site information
    site_mgr = Sites(c)
    site = site_mgr.get(RUNZERO_ORG_ID, RUNZERO_SITE_NAME)
    if not site:
        print(f"unable to find requested site")
        return

    # get or create the custom source manager and create a new custom source
    custom_source_mgr = CustomIntegrationsAdmin(c)
    my_asset_source = custom_source_mgr.get(name=name)
    if my_asset_source:
        source_id = my_asset_source.id
    else:
        my_asset_source = custom_source_mgr.create(name=name)
        source_id = my_asset_source.id

    # create the import manager to upload custom assets
    import_mgr = CustomAssets(c)
    import_task = import_mgr.upload_assets(
        org_id=RUNZERO_ORG_ID,
        site_id=site.id,
        custom_integration_id=source_id,
        assets=assets,
        task_info=ImportTask(name=f"{name} sync"),
    )

    if import_task:
        print(
            f"task created! view status here: https://console.runzero.com/tasks?task={import_task.id}"
        )


def append_openai_response(assets=list):
    output = []

    for a in assets:
        asset_id = a.get("id", "")
        custom_attrs = {"message": str(a.get("message", ""))[0:1000]}
        output.append(
            ImportAsset(id=asset_id, runZeroID=asset_id, customAttributes=custom_attrs)
        )

    return output


def get_data():
    vulnerabilities_url = RUNZERO_BASE_URL + "/export/org/vulnerabilities.json"

    vulnerabilities = requests.get(
        vulnerabilities_url, headers={"Authorization": f"Bearer {RUNZERO_EXPORT_TOKEN}"}
    )
    aggregated_vulnerabilities = {}
    for v in vulnerabilities.json():
        risk = v.get("risk_rank", 0)
        if risk > 0:
            vulnerability_asset_id = v.get("vulnerability_asset_id", "")
            key_values = {
                "vulnerability_risk_rank": v.get("vulnerability_risk_rank", ""),
                "vulnerability_name": v.get("vulnerability_name", ""),
                "vulnerability_severity": v.get("vulnerability_severity", ""),
                "vulnerability_cve": v.get("vulnerability_cve", ""),
                "vulnerability_description": v.get("vulnerability_description", ""),
                "vulnerability_solution": v.get("vulnerability_solution", ""),
                "vulnerability_remediation": v.get("vulnerability_remediation", ""),
                "vulnerability_count": v.get("vulnerability_count", ""),
                "service_count": v.get("service_count", ""),
                "risk_rank": v.get("risk_rank", ""),
                "vulnerability_count": v.get("vulnerability_count", ""),
                "hardware_device": v.get("attributes", {}).get("hw.device"),
                "hardware_vendor": v.get("attributes", {}).get("hw.vendor"),
                "hardware_product": v.get("attributes", {}).get("hw.product"),
                "os_family": v.get("attributes", {}).get("os.family"),
                "os_product": v.get("attributes", {}).get("os.product"),
                "os_vendor": v.get("attributes", {}).get("os.vendor"),
            }

            if vulnerability_asset_id in aggregated_vulnerabilities:
                aggregated_vulnerabilities[vulnerability_asset_id].append(key_values)
            else:
                aggregated_vulnerabilities[vulnerability_asset_id] = [key_values]

    return aggregated_vulnerabilities


if __name__ == "__main__":
    data = get_data()
    assets = []
    for k, v in data.items():
        message = openai_chat(v)
        assets.append({"id": k, "message": str(message)})
    upload_assets = append_openai_response(assets=assets)
    import_data_to_runzero(name="openai", assets=upload_assets)
