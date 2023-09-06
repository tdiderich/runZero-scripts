import json
import csv
import os
import re

TASK_LIST = ["homenet"]
RESULTS_SUMMARY = []
RESULTS_SUMMARY_FULL = []
CHECK_IP_PORT = re.compile(
    r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]):(\d+)(:)?$")
CHECK_IP = re.compile(
    r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$")


def write_to_csv(output: dict, filename: str, fieldnames: list):
    file = open(filename, "w")
    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )
    writer.writeheader()
    writer.writerows(output)
    file.close()


def main(file, filename):

    # make output directory for each task
    if not os.path.exists(f"{filename.strip('.json')}-out"):
        os.mkdir(f"{filename.strip('.json')}-out")

    # handle task data and save key results for later processing
    errors = {}
    errors_csv_output = []
    errors_csv_output_reduced = []
    results = {}
    results_csv_output = []
    for line in file:

        # create dict
        jline = json.loads(line.strip("@cee:"))

        # handle results
        if jline.get("type", "") == "result":
            if jline.get("host", "") in results:
                results[jline.get("host", "")]["ports"].append(
                    jline.get("port", ""))
                results[jline.get("host", "")]["port_count"] += 1
            else:
                results[jline.get("host", "")] = {
                    "ports": [jline.get("port", "")],
                    "port_count": 1
                }

        # handle errors
        if jline.get("level", "") == "error":
            if jline["msg"] in errors:
                errors[jline["msg"]] += 1
            else:
                errors[jline["msg"]] = 1

        # handle SNMP auth errors

        if jline.get("info", "") and jline.get("info", "").get("snmp.failedAuth", ""):
            host = jline.get("host", "")
            failure = jline.get("info", "").get("snmp.failedAuth", "")
            error = f"snmp auth error: {host}:161 {failure}"
            if error in errors:
                errors[error] += 1
            else:
                errors[error] = 1

    # temporary dic for results
    results_summary = {
        "total_hosts": 0,
        "total_hosts_list": [],
        "total_ports": 0,
        "unique_ports": [],
        "unique_ports_count": 0,
    }

    # handle results + write to CSVs
    # create CSV writeable list for results
    for k in results.keys():
        results_csv_output.append({
            "host": k,
            "port_count": results[k]["port_count"],
            "ports": results[k]["ports"],
        })

        # add 1 to host count
        results_summary["total_hosts"] += 1

        # add ports to total port count
        results_summary["total_ports"] += results[k]["port_count"]

        # add port to list if it doesn"t exist yet
        for p in results[k]["ports"]:
            if p not in results_summary["unique_ports"]:
                results_summary["unique_ports"].append(p)

        # add host to list of hosts
        results_summary["total_hosts_list"].append(k)

    # sort results by unique port count
    results_summary["unique_ports"] = sorted(results_summary["unique_ports"])
    results_summary["unique_ports_count"] = len(
        results_summary["unique_ports"])

    # write results to CSV
    write_to_csv(
        output=results_csv_output,
        filename=f"{filename.strip('.json')}-out/results.csv",
        fieldnames=[
            "host",
            "port_count",
            "ports",
        ])

    # write summary to CSV
    write_to_csv(
        output=[results_summary],
        filename=f"{filename.strip('.json')}-out/summary.csv",
        fieldnames=[
            "total_hosts",
            "total_ports",
            "unique_ports_count",
            "unique_ports",
            "total_hosts_list",
        ])

    # save for global summary
    RESULTS_SUMMARY.append({
        "task": filename,
        "total_hosts": results_summary["total_hosts"],
        "total_ports": results_summary["unique_ports_count"],
        "unique_ports_count": results_summary["unique_ports_count"]
    })

    RESULTS_SUMMARY_FULL.append({
        "task": filename,
        "total_hosts": results_summary["total_hosts"],
        "unique_ports_count": results_summary["unique_ports_count"],
        "total_hosts_list": results_summary["total_hosts_list"],
        "total_ports": results_summary["unique_ports_count"],
    })

    # handle errors and write to CSVs
    # create CSV writeable list for errors
    errors_reduced_temp = {}
    for k in errors.keys():
        errors_csv_output.append({
            "error": k,
            "count": errors[k]
        })

        # reduce the errors into high level groups
        # reconnects = packet loss
        if "reconnected" in k.split():
            ips = list(filter(CHECK_IP_PORT.search, k.split()))
            if "reconnected" in errors_reduced_temp:
                errors_reduced_temp["reconnected"]["hosts"] = errors_reduced_temp["reconnected"]["hosts"] + ips
                errors_reduced_temp["reconnected"]["count"] += errors[k]
            else:
                errors_reduced_temp["reconnected"] = {
                    "count": errors[k],
                    "hosts": ips

                }

        # snmp = timeout or credential does not work
        if "snmp" in k.split():
            ips = list(filter(CHECK_IP_PORT.search, k.split()))
            if "snmp" in errors_reduced_temp:
                errors_reduced_temp["snmp"]["hosts"] = errors_reduced_temp["snmp"]["hosts"] + ips
                errors_reduced_temp["snmp"]["count"] += errors[k]
            else:
                errors_reduced_temp["snmp"] = {
                    "count": errors[k],
                    "hosts": ips
                }

    # write errors to CSV
    write_to_csv(
        output=errors_csv_output,
        filename=f"{filename.strip('.json')}-out/errors.csv",
        fieldnames=[
            "error",
            "count"
        ])

    # create CSV writeable for list of reduced errors
    for k in errors_reduced_temp.keys():
        errors_csv_output_reduced.append({
            "error": k,
            "hosts": errors_reduced_temp[k]["hosts"],
            "count": errors_reduced_temp[k]["count"]
        })

    # sort based on error count before writing to CSV for errors
    errors_csv_output_reduced = sorted(
        errors_csv_output_reduced, key=lambda d: d["count"], reverse=True)

    # write errors reduced to CSV
    write_to_csv(
        output=errors_csv_output_reduced,
        filename=f"{filename.strip('.json')}-out/errors_reduced.csv",
        fieldnames=[
            "error",
            "count",
            "hosts"

        ])


if __name__ == "__main__":
    for f in TASK_LIST:
        file = open(f)
        main(file=file, filename=f)

    # write global summary to CSV
    write_to_csv(
        output=RESULTS_SUMMARY,
        filename=f"results_summary.csv",
        fieldnames=[
            "task",
            "total_hosts",
            "total_ports",
            "unique_ports_count",
        ])

    # write global full summary to CSV
    write_to_csv(
        output=RESULTS_SUMMARY_FULL,
        filename=f"results_summary_full.csv",
        fieldnames=[
            "task",
            "total_hosts",
            "total_ports",
            "unique_ports",
            "unique_ports_count",
            "total_hosts_list",
        ])
