import requests
import os
import csv
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet


RUNZERO_ACCOUNT_TOKEN = os.environ["RUNZERO_DEMO_ACCOUNT_TOKEN"]
HEADERS = {"Authorization": f"Bearer {RUNZERO_ACCOUNT_TOKEN}"}
BASE_URL = "https://demo.runZero.com/api/v1.0"

# A list of all the reports to be generated. New reports can be added here.
REPORTS = [
    # --- Count Reports ---
    {
        "name": "end_user_devices_count",
        "type": "count",
        "search": "type:desktop OR type:laptop OR type:tablet OR type:mobile",
    },
    {"name": "medical_devices_count", "type": "count", "search": "type:medical"},
    {"name": "servers_count", "type": "count", "search": "type:server"},
    {"name": "switches_count", "type": "count", "search": "type:switch"},
    {"name": "wifi_aps_count", "type": "count", "search": "type:wap"},
    {"name": "cameras_count", "type": "count", "search": 'type:"ip camera"'},
    {"name": "firewalls_count", "type": "count", "search": "type:firewall"},
    {"name": "hypervisors_count", "type": "count", "search": "type:hypervisor"},
    {"name": "storage_count", "type": "count", "search": "type:storage OR type:nas"},
    {
        "name": "end_of_life_os_count",
        "type": "count",
        "search": "os_eol:<now",
    },
    # --- Full Data Dumps ---
    {
        "name": "workstations",
        "type": "dump",
        "search": "type:desktop OR type:laptop",
        "fields": "id,addresses,names,os,os_version,os_eol,hw_vendor,hw_model,hw_serial,last_seen,sources",
    },
    {
        "name": "servers",
        "type": "dump",
        "search": "type:server",
        "fields": "id,addresses,names,os,os_version,os_eol,hw_vendor,hw_model,hw_serial,last_seen,sources",
    },
    {
        "name": "switches",
        "type": "dump",
        "search": "type:switch",
        "fields": "id,addresses,names,os,os_version,os_eol,hw_vendor,hw_model,hw_serial,last_seen,sources",
    },
    {
        "name": "wifi_aps",
        "type": "dump",
        "search": "type:wap",
        "fields": "id,addresses,names,os,os_version,os_eol,hw_vendor,hw_model,hw_serial,last_seen,sources",
    },
    {
        "name": "cameras",
        "type": "dump",
        "search": 'type:"ip camera"',
        "fields": "id,addresses,names,os,os_version,os_eol,hw_vendor,hw_model,hw_serial,last_seen,sources",
    },
    {
        "name": "firewalls",
        "type": "dump",
        "search": "type:firewall",
        "fields": "id,addresses,names,os,os_version,os_eol,hw_vendor,hw_model,hw_serial,last_seen,sources",
    },
    {
        "name": "hypervisors",
        "type": "dump",
        "search": "type:hypervisor",
        "fields": "id,addresses,names,os,os_version,os_eol,hw_vendor,hw_model,hw_serial,last_seen,sources",
    },
    {
        "name": "storage",
        "type": "dump",
        "search": "type:storage OR type:nas",
        "fields": "id,addresses,names,os,os_version,os_eol,hw_vendor,hw_model,hw_serial,last_seen,sources",
    },
    {
        "name": "end_of_life_os",
        "type": "dump",
        "search": "os_eol:<now",
        "fields": "id,addresses,names,os,os_version,os_eol,hw_vendor,hw_model,hw_serial,last_seen,sources",
    },
    {
        "name": "other_unclassified_hardware",
        "type": "dump",
        "search": '(NOT (type:desktop OR type:laptop OR type:tablet OR type:mobile OR type:server OR type:switch OR type:wap OR type:"ip camera" OR type:firewall OR type:hypervisor OR type:storage OR type:nas)) AND (NOT cidr:0.0.0.0/0)',
        "fields": "id,addresses,names,os,os_version,os_eol,hw_vendor,hw_model,hw_serial,last_seen,sources",
    },
]


def create_count_chart(df, output_path):
    """Create a bar chart for count-based reports."""
    plt.figure(figsize=(10, 5))
    plt.bar(df["report_name"], df["count"])
    plt.xticks(rotation=45, ha="right")
    plt.title("Asset Summary Counts")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def create_pdf_report(org_name, org_path):
    """Generate a PDF summary report combining counts and CSV previews with truncated long values."""
    pdf_path = os.path.join(org_path, "report.pdf")
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    story = []

    # ----------- Truncation helper -----------
    def truncate_value(val, max_items=2):
        """Truncate comma-separated lists and append '… and X more'."""
        if not isinstance(val, str):
            return str(val)

        # Split on comma + space
        parts = [p.strip() for p in val.split(",")]

        if len(parts) <= max_items:
            return val

        shown = ", ".join(parts[:max_items])
        remaining = len(parts) - max_items
        return f"{shown}, … and {remaining} more"

    # ----------- Wrap DataFrame for PDF table -----------
    def wrap_dataframe(df, max_width=500):
        cols = df.columns.tolist()
        col_width = max_width / len(cols)
        style = styles["BodyText"]

        table_data = [cols]
        for _, row in df.iterrows():
            wrapped_row = [Paragraph(truncate_value(x), style) for x in row.tolist()]
            table_data.append(wrapped_row)

        return table_data, [col_width] * len(cols)

    # Title
    story.append(Paragraph(f"{org_name.upper()} Asset Report", styles["Title"]))
    story.append(Spacer(1, 20))

    # ----------- Counts Summary -----------
    count_csv = os.path.join(org_path, "counts_summary.csv")
    if os.path.exists(count_csv):
        df_counts = pd.read_csv(count_csv)

        # Chart
        chart_path = os.path.join(org_path, "counts_chart.png")
        create_count_chart(df_counts, chart_path)

        story.append(Paragraph("Asset Type Summary", styles["Heading2"]))
        story.append(Image(chart_path, width=500, height=300))
        story.append(Spacer(1, 20))

        # Count table
        story.append(Paragraph("Count Details", styles["Heading3"]))
        table_data, col_widths = wrap_dataframe(df_counts)
        table = Table(table_data, colWidths=col_widths, repeatRows=1, splitByRow=1)

        table.setStyle(
            TableStyle(
                [
                    ("FONTSIZE", (0, 0), (-1, -1), 7),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 2),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                ]
            )
        )

        story.append(table)
        story.append(Spacer(1, 20))

    # ----------- Dump Files (truncated preview) -----------
    for file in sorted(os.listdir(org_path)):
        if not file.endswith(".csv") or file == "counts_summary.csv":
            continue

        df = pd.read_csv(os.path.join(org_path, file))

        story.append(
            Paragraph(file.replace(".csv", "").capitalize(), styles["Heading2"])
        )

        preview_df = df.head(20)
        table_data, col_widths = wrap_dataframe(preview_df)

        table = Table(table_data, colWidths=col_widths, repeatRows=1, splitByRow=1)

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
        story.append(Spacer(1, 20))

    doc.build(story)
    print(f"PDF report created: {pdf_path}")


def write_to_csv(output: list, filename: str):
    """Writes the given data to a CSV file."""
    if not output:
        print(f"No data to write for {filename}")
        return

    fieldnames = list(output[0].keys())
    with open(filename, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output)
    print(f"Successfully wrote {len(output)} rows to {filename}")


def get_runzero_data(token: str, search: str, fields: str = "id"):
    """Fetches data from the runZero API."""
    headers = {"Authorization": f"Bearer {token}"}
    url = BASE_URL + "/export/org/assets.json"
    try:
        response = requests.get(
            url, headers=headers, params={"search": search, "fields": fields}
        )
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from runZero: {e}")
        return None


def main():
    """Main function to generate reports for all organizations."""
    try:
        orgs_response = requests.get(BASE_URL + "/account/orgs", headers=HEADERS)
        orgs_response.raise_for_status()
        orgs = orgs_response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching organizations: {e}")
        return

    for org in orgs:
        token = org.get("export_token")
        org_name = org.get("name").replace(" ", "_").replace("-", "").lower()
        asset_count = org.get("asset_count")

        if not token:
            print(f"Skipping {org_name} - export token not enabled.")
            continue
        if asset_count == 0:
            print(f"Skipping {org_name} - no assets found.")
            continue

        print(f"--- Processing organization: {org_name} ---")

        # Create a directory for the organization's reports
        if not os.path.exists(org_name):
            os.mkdir(org_name)

        # A list to hold the results of the count reports for this org
        count_summary = []

        # Process each report defined in the REPORTS list
        for report in REPORTS:
            print(f"Running report: {report['name']}...")
            if report["type"] == "count":
                data = get_runzero_data(token, report["search"])
                if data is not None:
                    count_summary.append(
                        {"report_name": report["name"], "count": len(data)}
                    )

            elif report["type"] == "dump":
                data = get_runzero_data(token, report["search"], report["fields"])
                if data:
                    # Clean up the data for CSV writing
                    for row in data:
                        for key, value in row.items():
                            if isinstance(value, list):
                                row[key] = ", ".join(map(str, value))
                    write_to_csv(data, f"{org_name}/{report['name']}.csv")

        # Write the count summary report for the organization
        if count_summary:
            write_to_csv(count_summary, f"{org_name}/counts_summary.csv")
            create_pdf_report(org_name, org_name)


if __name__ == "__main__":
    main()
