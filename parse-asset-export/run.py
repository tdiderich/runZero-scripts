import json

FIELDS_I_WANT = ["alive", "sources", "names", "addresses", "service_count"]

with open("export.jsonl", "r") as json_file:
    json_list = list(json_file)

for json_str in json_list:
    result = json.loads(json_str)
    alive = result.get("alive", None)
    if alive:
        for field in FIELDS_I_WANT:
            value = result.get(field, None)
            print(f"{field}: {value}")
