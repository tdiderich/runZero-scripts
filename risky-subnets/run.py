import requests
import os
import csv
import urllib.parse
import ipaddress
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
)
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import os


# auth - navigate here to create an account token: https://console.runzero.com/account
RUNZERO_ACCOUNT_TOKEN = os.environ["RUNZERO_DEMO_ACCOUNT_TOKEN"]
HEADERS = {"Authorization": f"Bearer {RUNZERO_ACCOUNT_TOKEN}"}
BASE_URL = "https://demo.runZero.com/api/v1.0"

# dict for tracking counts and data
GLOBAL_RISK = []

# searches to report on - update as needed

SEARCHES = [
    {
        "name": "assets_missing_crowdstrike",
        "type": "assets",
        "search": "source:runzero not source:crowdstrike (type:server OR type:desktop OR type:laptop) alive:t",
    },
    {
        "name": "expired_tls_certs",
        "type": "services",
        "search": "alive:t protocol:tls tls.notAfterTS:<now",
    },
]

# -----------------------------
# VISUALIZATION HELPERS
# -----------------------------


def chart_top_riskiest_subnets(df, outpath):
    df2 = df.sort_values("risk", ascending=False).head(20)
    plt.figure(figsize=(10, 6))
    plt.barh(df2["subnet"], df2["risk"])
    plt.title("Top 20 Riskiest Subnets")
    plt.xlabel("Total Risk")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()


def chart_scatter_assetcount_vs_avgrisk(df, outpath):
    # Clean numeric values
    df = df.copy()
    df["asset_count"] = pd.to_numeric(df["asset_count"], errors="coerce").fillna(0)
    df["avg_risk"] = pd.to_numeric(df["avg_risk"], errors="coerce").fillna(0)
    df["risk"] = pd.to_numeric(df["risk"], errors="coerce").fillna(0).clip(lower=0)

    sizes = (df["risk"] / 5).clip(lower=10)  # prevent invisible dots

    plt.figure(figsize=(8, 6))
    plt.scatter(df["asset_count"], df["avg_risk"], s=sizes, alpha=0.6)
    plt.title("Asset Count vs Avg Risk")
    plt.xlabel("Asset Count")
    plt.ylabel("Avg Risk")
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()


def chart_risk_by_site(df, outpath):
    site_totals = df.groupby("site_id")["risk"].sum()
    plt.figure(figsize=(7, 7))
    plt.pie(site_totals, labels=site_totals.index, autopct="%1.1f%%")
    plt.title("Risk Distribution by Site")
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()


def chart_search_risk(df, outpath, search_name):
    df2 = df.sort_values("risk", ascending=False).head(20)
    plt.figure(figsize=(10, 6))
    plt.barh(df2["subnet"], df2["risk"])
    plt.title(f"Top Subnets for: {search_name}")
    plt.xlabel("Risk")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()


def chart_search_scatter(df, outpath, search_name):
    plt.figure(figsize=(8, 6))
    plt.scatter(df["asset_count"], df["avg_risk"], s=df["risk"] / 5, alpha=0.6)
    plt.title(f"Asset Count vs Avg Risk: {search_name}")
    plt.xlabel("Asset Count")
    plt.ylabel("Avg Risk")
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()


# -----------------------------
# VALUE TRUNCATION
# -----------------------------


def truncate_value(val, max_items=2):
    if not isinstance(val, str):
        return str(val)
    parts = [p.strip() for p in val.split(",")]
    if len(parts) <= max_items:
        return val
    shown = ", ".join(parts[:max_items])
    remaining = len(parts) - max_items
    return f"{shown}, … and {remaining} more"


# -----------------------------
# PDF BUILDER
# -----------------------------


def wrap_dataframe(df, styles, max_width=500):
    cols = df.columns.tolist()
    col_width = max_width / len(cols)
    style = styles["BodyText"]

    table_data = [cols]
    for _, row in df.iterrows():
        wrapped_row = [Paragraph(truncate_value(x), style) for x in row.tolist()]
        table_data.append(wrapped_row)

    return table_data, [col_width] * len(cols)


def create_risk_pdf(org_name, org_path):
    styles = getSampleStyleSheet()
    pdf_path = os.path.join(org_path, "risk_report.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    story = []

    # -----------------
    # TITLE PAGE
    # -----------------

    story.append(Paragraph(f"{org_name.upper()} — Risk by Subnet", styles["Title"]))
    story.append(Spacer(1, 20))

    # -----------------
    # ORG-LEVEL GRAPHS
    # -----------------

    risk_csv = os.path.join(org_path, "risk_by_subnet.csv")
    if os.path.exists(risk_csv):
        df = pd.read_csv(risk_csv)

        # 1. Top 20 Riskiest Subnets
        p1 = os.path.join(org_path, "chart_top_risk.png")
        chart_top_riskiest_subnets(df, p1)
        story.append(Image(p1, width=500, height=300))
        story.append(Spacer(1, 20))

        # 2. Scatter
        p2 = os.path.join(org_path, "chart_scatter.png")
        chart_scatter_assetcount_vs_avgrisk(df, p2)
        story.append(Image(p2, width=500, height=300))
        story.append(Spacer(1, 20))

        # 3. Risk by Site Pie
        p3 = os.path.join(org_path, "chart_risk_by_site.png")
        chart_risk_by_site(df, p3)
        story.append(Image(p3, width=400, height=400))
        story.append(Spacer(1, 20))

    # -----------------
    # PER-SEARCH SECTIONS
    # -----------------

    for search_type in ["assets", "services"]:
        folder = os.path.join(org_path, search_type)
        if not os.path.isdir(folder):
            continue

        for file in sorted(os.listdir(folder)):
            if not file.endswith(".csv"):
                continue

            full_path = os.path.join(folder, file)
            df_search = pd.read_csv(full_path)
            search_name = file.replace(".csv", "")

            # Charts
            img1 = os.path.join(folder, f"{search_name}_bar.png")
            chart_search_risk(df_search, img1, search_name)
            story.append(Paragraph(search_name, styles["Heading2"]))
            story.append(Image(img1, width=500, height=300))
            story.append(Spacer(1, 20))

            img2 = os.path.join(folder, f"{search_name}_scatter.png")
            chart_search_scatter(df_search, img2, search_name)
            story.append(Image(img2, width=500, height=300))
            story.append(Spacer(1, 20))

            # Table Preview
            preview = df_search.head(20)
            table_data, col_widths = wrap_dataframe(preview, styles)

            table = Table(table_data, colWidths=col_widths, splitByRow=1, repeatRows=1)
            table.setStyle(
                TableStyle(
                    [
                        ("FONTSIZE", (0, 0), (-1, -1), 6),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 2),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                    ]
                )
            )

            story.append(table)
            story.append(Spacer(1, 30))

    doc.build(story)
    print(f"PDF created: {pdf_path}")


def write_to_csv(output: dict, filename: str, fieldnames: list):
    file = open(filename, "w")
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(output)
    file.close()


def create_output(
    assets: list,
    org_name: str,
    search_name: str = None,
    search_type: str = None,
    search: str = None,
    search_url: str = None,
):
    tracker = {}
    output = []

    for asset in assets:
        addresses = asset.get("addresses", [])
        risk = asset.get("risk_rank", 0)
        criticality = asset.get("criticality_rank", 0)
        site = asset.get("site_id", "unknown-site")
        for address in addresses:
            ip = ipaddress.ip_address(address)
            if ip.version == 4:
                address.split(".")
                subnet = ".".join(address.split(".")[0:3]) + ".0/24"
                subnet = f"{site}_{subnet}"
                if subnet not in tracker:
                    # new subnet
                    tracker[subnet] = {}
                    tracker[subnet]["asset_count"] = 0
                    tracker[subnet]["risk"] = risk
                    tracker[subnet]["avg_risk"] = risk
                    tracker[subnet]["criticality"] = criticality
                    tracker[subnet]["avg_criticality"] = criticality
                    search_params = subnet.split("_")

                    safe_search = (
                        urllib.parse.quote_plus(
                            f"{search} AND site:{search_params[0]} AND net:{search_params[1]}"
                        )
                        if search
                        else urllib.parse.quote_plus(
                            f"site:{search_params[0]} AND net:{search_params[1]}"
                        )
                    )

                    tracker[subnet]["search"] = f"{search_url}{safe_search}"

                # handle subnets that already exist
                tracker[subnet]["asset_count"] += 1
                tracker[subnet]["risk"] += risk
                tracker[subnet]["avg_risk"] = round(
                    tracker[subnet]["risk"] / tracker[subnet]["asset_count"], 2
                )
                tracker[subnet]["criticality"] += criticality
                tracker[subnet]["avg_criticality"] = round(
                    tracker[subnet]["criticality"] / tracker[subnet]["asset_count"], 2
                )

    for subnet in tracker.keys():
        output.append(
            {
                "org_name": org_name,
                "site_id": subnet.split("_")[0],
                "subnet": subnet.split("_")[1],
                "asset_count": tracker[subnet]["asset_count"],
                "risk": tracker[subnet]["risk"],
                "avg_risk": tracker[subnet]["avg_risk"],
                "criticality": tracker[subnet]["criticality"],
                "avg_criticality": tracker[subnet]["avg_criticality"],
                "search": tracker[subnet]["search"],
            }
        )

    filename = (
        f"{org_name}/{search_type}/{search_name}.csv"
        if search_type and search_name
        else f"{org_name}/risk_by_subnet.csv"
    )

    write_to_csv(
        output=sorted(output, key=lambda x: x["risk"], reverse=True),
        filename=filename,
        fieldnames=[
            "org_name",
            "asset_count",
            "site_id",
            "subnet",
            "risk",
            "avg_risk",
            "criticality",
            "avg_criticality",
            "search",
        ],
    )

    return output


def handle_search(
    token: str, org_name: str, search_name: str, search_type: str, search: str
):

    # ensure search name is good for file creation
    search_name = search_name.replace(" ", "_").replace("-", "").lower()

    # check for folder or create
    if not os.path.exists(f"{org_name}/{search_type}"):
        os.mkdir(f"{org_name}/{search_type}")

    headers = {"Authorization": f"Bearer {token}"}
    if search_type == "assets":
        url = BASE_URL + "/export/org/assets.json?"
        search_url = "https://console.runzero.com/inventory?search="
    elif search_type == "services":
        url = BASE_URL + "/export/org/services.json?"
        search_url = "https://console.runzero.com/inventory/services?search="
    else:
        print(f"non supported search type {search_type}")

    data = requests.get(
        url,
        headers=headers,
        params={
            "search": search,
            "fields": "site_id, addresses, addresses_extra, risk_rank, risk, criticality, criticality_rank",
        },
    )
    results = data.json()

    create_output(
        assets=results,
        org_name=org_name,
        search_name=search_name,
        search_type=search_type,
        search=search,
        search_url=search_url,
    )


def handle_org_risk(token: str, name: str):
    print(f"handling {name}...")
    # check for folder or create
    if not os.path.exists(name):
        os.mkdir(name)

    # create export variables
    headers = {"Authorization": f"Bearer {token}"}
    url = BASE_URL + "/export/org/assets.json"

    # total risk by subnet dict
    risk_by_subnet = {}

    data = requests.get(
        url,
        headers=headers,
        params={
            "search": "alive:t",
            "fields": "site_id, addresses, addresses_extra, risk_rank, risk, criticality, criticality_rank",
        },
    )

    results = data.json()

    risk_by_subnet_output = create_output(
        assets=results,
        org_name=name,
        search_url="https://console.runzero.com/inventory?search=",
    )

    GLOBAL_RISK.extend(risk_by_subnet_output)


def main():
    orgs = requests.get(BASE_URL + "/account/orgs", headers=HEADERS)
    for o in orgs.json():
        token = o.get("export_token", "")
        name = o.get("name").replace(" ", "_").replace("-", "").lower()
        asset_count = o.get("asset_count")
        max_assets = 100000
        if token and asset_count < max_assets and asset_count > 50:
            handle_org_risk(token=token, name=name)
            for search in SEARCHES:
                handle_search(
                    token=token,
                    org_name=name,
                    search_name=search["name"],
                    search_type=search["type"],
                    search=search["search"],
                )
            create_risk_pdf(name, name)
        if not token:
            print(
                f"skipping {name} - you need to enable the export token in the UI to run the report"
            )
        elif asset_count > max_assets:
            print(
                f"skipping {name} - you need to increase the max_assets value to be above {max_assets} to run"
            )

    write_to_csv(
        output=sorted(GLOBAL_RISK, key=lambda x: x["risk"], reverse=True),
        filename=f"GLOBAL_RISK.csv",
        fieldnames=[
            "org_name",
            "asset_count",
            "site_id",
            "subnet",
            "risk",
            "avg_risk",
            "criticality",
            "avg_criticality",
            "search",
        ],
    )


if __name__ == "__main__":
    main()
