import requests
import os
import json
import csv

RUNZERO_EXPORT_TOKEN = os.environ["RUNZERO_EXPORT_TOKEN"]
HEADERS = {"Authorization": f"Bearer {RUNZERO_EXPORT_TOKEN}"}
BASE_URL = "https://console.runZero.com/api/v1.0"

def get_sites():
    url = BASE_URL + "/org/sites"
    sites = requests.get(url, headers=HEADERS, params={"fields": "id,name"})
    return sites.json()

def get_vulns(sites: list):
    for site in sites:
        safe_site = site.get("name").replace(" ", "_").lower()
        site_id = site.get("id")
        url = BASE_URL + "/export/org/vulnerabilities.json?"
        data = requests.get(url, headers=HEADERS, params={"search": f"source:runzero site:{site_id} (risk:high or risk:critical)"})
        vulns = data.json()
        if len(vulns) > 0:
            output = []
            fields = [
                "site_name",
                "vulnerability_risk_rank",
                "vulnerability_id",
                "vulnerability_asset_id",
                "vulnerability_created_at",
                "vulnerability_updated_at",
                "vulnerability_service_address",
                "vulnerability_service_transport",
                "vulnerability_service_port",
                "vulnerability_cpe23",
                "vulnerability_vuln_id",
                "vulnerability_category",
                "vulnerability_name",
                "vulnerability_description",
                "vulnerability_solution",
                "alive",
                "type",
                "os_vendor",
                "os_product",
                "os_version",
                "os",
                "hw_vendor",
                "hw_product",
                "hw_version",
                "hw",
                "addresses",
                "addresses_extra",
                "macs",
                "names",
                "owners",
            ]

            for v in vulns:
                # normalize the risk rank
                vuln_risk_map = {
                    3: "High",
                    4: "Critical",
                }
                v["vulnerability_risk_rank"] = vuln_risk_map.get(
                    v.get("risk_rank", 0), "Unknown"
                )

                # create CSV row
                vuln_row = {}
                for field in fields:
                    vuln_row[field] = v.get(field, "")

                # add row to output
                output.append(vuln_row)

            fname = f"{safe_site}.csv"
            tls_csv = open(fname, "w")
            writer = csv.DictWriter(tls_csv, fieldnames=fields)
            writer.writeheader()
            writer.writerows(output)
            tls_csv.close()

            print(f"Successfully loaded the data to {fname}")
        else:
            print(f"No vulnerabilities found for {site.get('name')}")


if __name__ == "__main__":
    sites = get_sites()
    get_vulns(sites=sites)
