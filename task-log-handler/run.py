import json
import csv

TASK_LIST = ["task1", "task2"]
COMPARE_LIST = []


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
    errors = {}
    csv_output = []
    for line in file:
        jline = json.loads(line.strip("@cee:"))
        if "error-message" in jline:
            if jline["error-message"] in errors:
                errors[jline["error-message"]] += 1
            else:
                errors[jline["error-message"]] = 1

    for k in errors.keys():
        csv_output.append({
            "error": k,
            "count": errors[k]
        })

    csv_output = sorted(csv_output, key=lambda d: d["count"], reverse=True)

    write_to_csv(
        output=csv_output,
        filename=f"{filename.strip('.json')}_errors.csv",
        fieldnames=[
            "error",
            "count"
        ])


if __name__ == "__main__":
    for f in TASK_LIST:
        file = open(f)
        main(file=file, filename=f)
