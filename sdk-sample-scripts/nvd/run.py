import requests
import os
import json
from flatten_json import flatten
from ipaddress import ip_address
from typing import Any, Dict, List
import runzero
from runzero.client import AuthError
from runzero.api import CustomAssets, CustomIntegrationsAdmin, Sites, Tasks
from runzero.types import ImportAsset, ImportTask, Vulnerability

from openai import OpenAI

RUNZERO_EXPORT_TOKEN = os.environ["RUNZERO_EXPORT_TOKEN"]
RUNZERO_CLIENT_ID = os.environ["RUNZERO_CLIENT_ID"]
RUNZERO_CLIENT_SECRET = os.environ["RUNZERO_CLIENT_SECRET"]
RUNZERO_ORG_ID = os.environ["RUNZERO_ORG_ID"]
RUNZERO_SITE_NAME = os.environ["RUNZERO_SITE_NAME"]
RUNZERO_BASE_URL = "https://console.runzero.com/api/v1.0"
NVPD_API_KEY = os.environ["NVD_API_KEY"]


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


def create_upload_assets(assets=list):
    output = []
    for a in assets:
        asset_id = a.get("id", "")
        vulns = []
        for v in a.get("cve_data", {}).get("vulnerabilities", []):

            cve = v.get("cve", {})
            metrics_list = cve.get("metrics", {}).get("cvssMetricV30", [])
            # no metrics = no useful data to upload
            if len(metrics_list) > 0:
                metrics = cve.get("metrics", {}).get("cvssMetricV30")[0].get("cvssData", {})
                exploitability_score = cve.get("metrics", {}).get("cvssMetricV30")[0].get("exploitabilityScore")

                # fudging risk score
                impact_score = cve.get("metrics", {}).get("cvssMetricV30")[0].get("impactScore")
                risk_rank = 0
                if impact_score > 8:
                    risk_rank = 4
                elif impact_score > 6:
                    risk_rank = 3
                elif impact_score > 4:
                    risk_rank = 2
                elif impact_score > 2:
                    risk_rank = 1

                # create severity map
                severity = metrics.get("baseSeverity", "")
                severity_rank_map = {
                    "CRITICAL": 4,
                    "HIGH": 3,
                    "MEDIUM": 2,
                    "LOW": 1,
                }

                # get english description
                descriptions = cve.get("descriptions", [])
                description_out = ""
                for d in descriptions:
                    if d.get("lang", "") == "en":
                        description_out = d.get("value", "")[0:1023]

                # pull ID
                cve_id = cve.get("id", "")
                cve_format = len(cve_id.split("-")[2])

                # skip OLD CVEs that use the olf format 
                if cve_format == 5:
                    vulns.append(
                        Vulnerability(
                            id=cve.get("id", ""),
                            cve=cve.get("id", ""),
                            name=cve.get("id", ""),
                            description=description_out,
                            severityRank=(
                                severity_rank_map[severity]
                                if severity in severity_rank_map
                                else 0
                            ),
                            severityScore=metrics.get("baseScore", 0),
                            riskRank=risk_rank,
                            riskScore=impact_score,
                            exploitable=True if exploitability_score >= 5 else False,
                            cpe23=a.get("cpe", ""),
                            # lastDetectedTS=cve.get("lastModified", ""),
                            customAttributes={
                                "version": str(metrics.get("version", "")),
                                "vectorString": str(metrics.get("vectorString", "")),
                                "attackVector": str(metrics.get("attackVector", "")),
                                "attackComplexity": str(
                                    metrics.get("attackComplexity", "")
                                ),
                                "privilegesRequired": str(
                                    metrics.get("privilegesRequired", "")
                                ),
                                "userInteraction": str(
                                    metrics.get("userInteraction", "")
                                ),
                                "scope": str(metrics.get("scope", "")),
                                "confidentialityImpact": str(
                                    metrics.get("confidentialityImpact", "")
                                ),
                                "integrityImpact": str(
                                    metrics.get("integrityImpact", "")
                                ),
                                "availabilityImpact": str(
                                    metrics.get("availabilityImpact", "")
                                ),
                                "baseScore": str(metrics.get("baseScore", "")),
                                "baseSeverity": str(metrics.get("baseSeverity", "")),
                            },
                        )
                    )

        output.append(
            ImportAsset(id=asset_id, runZeroID=asset_id, vulnerabilities=vulns)
        )

    return output


def get_nvd_vulnerabilitites(cpe: str):
    url = f"https://services.nvd.nist.gov/rest/json/cves/2.0"
    headers = {"apiKey": NVPD_API_KEY}

    critical_response = requests.get(
        url, headers=headers, params={"cpeName": cpe, "cvssV3Severity": "CRITICAL"}
    )

    if critical_response.status_code == 200:
        response = {
            "format": critical_response.json().get("format", None),
            "version": critical_response.json().get("version", None),
            "vulnerabilities": critical_response.json().get("vulnerabilities", []),
        }
        total = critical_response.json().get("totalResults", 0)
        if total < 1000:
            limit = 1000 - total
            high_response = requests.get(
                url,
                headers=headers,
                params={
                    "cpeName": cpe,
                    "cvssV3Severity": "HIGH",
                    "resultsPerPage": limit,
                },
            )
            if high_response.status_code == 200:
                high_response = high_response.json().get("vulnerabilities", [])
                response["vulnerabilities"].extend(high_response)
        return response
    else:
        print(f"failed on: {cpe} - status code: {critical_response.status_code}")


def get_assets():
    url = RUNZERO_BASE_URL + "/export/org/assets.json"

    assets = requests.get(
        url,
        headers={"Authorization": f"Bearer {RUNZERO_EXPORT_TOKEN}"},
        params={"search": 'alive:t attribute:"os.cpe23"'},
    )

    assets_with_cpe = []

    for asset in assets.json():
        cpe = asset.get("attributes", {}).get("os.cpe23", None)
        if cpe:
            if "r0_unofficial" in cpe:
                print(f"skipping r0_unofficial: {cpe}")
            else:
                assets_with_cpe.append(
                    {
                        "id": asset.get("id", ""),
                        "cpe": cpe.replace("cpe:/", "cpe:2.3:"),
                    }
                )

    return assets_with_cpe


if __name__ == "__main__":
    assets = get_assets()
    cpe_cache = {}
    enriched_assets = []
    for a in assets:
        cpe = a.get("cpe")
        if cpe:
            if cpe not in cpe_cache.keys():
                cve_data = get_nvd_vulnerabilitites(cpe)
                cpe_cache[cpe] = cve_data
                enriched_assets.append(
                    {"id": a.get("id", ""), "cpe": cpe, "cve_data": cve_data}
                )
            else:
                enriched_assets.append(
                    {"id": a.get("id", ""), "cpe": cpe, "cve_data": cpe_cache[cpe]}
                )

    assets_to_upload = create_upload_assets(assets=enriched_assets)
    import_data_to_runzero(name="nist_nvd", assets=assets_to_upload)
