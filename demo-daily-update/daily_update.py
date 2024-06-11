import gzip
import time
import json
import random
import datetime
import os
import requests

RUNZERO_BASE_URL = "https://demo.runZero.com/api/v1.0"
RUNZERO_ORG_ID = "bddd405a-f594-4891-88f9-c4e95d793f68"
RUNZERO_SITE_ID = "43d7ee80-2927-4c68-9be0-1f8cf267cf9a"
RUNZERO_ORG_TOKEN = os.environ["RUNZERO_ORG_TOKEN"]
JAMF_CUSTOM_INTEGRATION_ID = "2ba644ef-2774-4539-b3e6-2dd06770c0a5"
def current_rz_time() -> float:
    return round(time.time() * 1000000000)

def handle_output(output: list, filename: str):
    write_file = filename.split(".")[0] + "_updated.json"
    with open(write_file, "w") as f:
        for l in output:
            f.write(json.dumps(l, separators=(",", ":")) + "\n")

def upload_tasks():
    print("STARTING - uploading tasks to runZero")
    for filename in [
        "scan_output_updated.json",
        "integration_crowdstrike_updated.json",
        "integration_nessus_updated.json",
        "integration_aws_updated.json",
        "integration_azuread_updated.json",
        "integration_jamf_updated.json",
    ]:
        gzip_upload = gzip.compress(open(filename, "rb").read())
        upload_url = RUNZERO_BASE_URL + f"/org/sites/{RUNZERO_SITE_ID}/import"
        params = {"_oid": RUNZERO_ORG_ID}
        headers = {"Authorization": f"Bearer {RUNZERO_ORG_TOKEN}"}
        resp = requests.put(
            url=upload_url, headers=headers, params=params, data=gzip_upload
        )
        if resp.status_code == 200:
            print("SUCCESS - uploaded", filename)

def delete_existing_assets():
    export_url = RUNZERO_BASE_URL + "/export/org/assets.json"
    headers = {"Authorization": f"Bearer {RUNZERO_ORG_TOKEN}"}
    params = {"search": f"site:{RUNZERO_SITE_ID}", "fields": "id"}
    resp = requests.get(url=export_url, headers=headers, params=params)

    # create list of assets to delete
    asset_list = [x["id"] for x in resp.json()]
    if len(asset_list) > 0:
        print("STARTING - asset deletion")
        delete_url = RUNZERO_BASE_URL + "/org/assets/bulk/delete"
        delete = requests.delete(
            url=delete_url,
            headers=headers,
            json={"asset_ids": asset_list},
            params={"_oid": RUNZERO_ORG_ID},
        )
        # verify deleted
        if delete.status_code == 204:
            print("IN PROGRESS - runZero is deleting the assets")
            time.sleep(10)
            deleted = False
            attempts = 0
            # wait for deletion to finish if not done
            while not deleted:
                resp = requests.get(url=export_url, headers=headers, params=params)
                if len(resp.json()) == 0:
                    deleted = True
                    print("SUCCESS - all assets deleted")
                else:
                    time.sleep(5)
                    attempts += 1
                    if attempts > 10:
                        print("FAILURE - unable to delete all assets")
                    print(
                        "WAITING - still deleting assets. Waiting 5 seconds to check again. Current asset count:",
                        len(resp.json()),
                    )
    else:
        print("SUCCESS - no assets to delete")
def main():
    for file in [
            "scan_output.json.gz",
            "integration_crowdstrike.json.gz",
            "integration_nessus.json.gz",
            "integration_aws.json.gz",
            "integration_azuread.json.gz",
            "integration_jamf.json.gz",
        ]:
        output = []
        print("STARTING - updating", file)
        with gzip.open(file, "rt") as unzipped: 
            # fix all the timestamps 
            for line in unzipped.readlines():
                temp_line = json.loads(line)
                temp_line["ts"] = current_rz_time()
                if file in ["scan_output.json.gz", "integration_aws.json.gz", "integration_jamf.json.gz"]:
                    # no more updates needed for these data types
                    output.append(temp_line)
                elif file == "integration_crowdstrike.json.gz":
                    temp_line["info"]["modifiedTS"] = str(round(time.time()))
                    temp_line["info"]["firstLoginTS"] = str(round(time.time() - 10000 * random.choice([5, 6, 7, 8, 9, 10])))
                    temp_line["info"]["lastInteractiveTSS"] = str(round(time.time() - 10000 * random.choice([1, 2, 3, 4, 5])))
                    temp_line["info"]["lastInteractiveTS"] = str(round(time.time() - 10000 * random.choice([1, 2, 3, 4, 5])))
                    temp_line["info"]["lastLoginTS"] = str(round(time.time() - 10000 * random.choice([1, 2, 3, 4, 5])))
                    temp_line["info"]["agentLocalTime"] = str(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")) + "Z"
                    output.append(temp_line)
                elif file == "integration_nessus.json.gz":
                    temp_line["info"]["lastSeenTS"] = str(round(time.time()))
                    temp_line["info"]["firstSeenTS"] = str(
                            round(time.time() - 10000 * random.choice([5, 6, 7, 8, 9, 10]))
                        )
                    temp_line["info"]["lastScanTimeTS"] = str(
                            round(time.time() - 10000 * random.choice([1, 2, 3, 4, 5]))
                        )
                    output.append(temp_line)
                elif file == "integration_azuread.json.gz":
                    temp_line["info"]["approximateLastSignInDateTimeTS"] = str(
                            round(time.time() - 10000)
                        )
                    temp_line["info"]["createdDateTimeTS"] = str(
                            round(time.time() - 10000 * random.choice([1, 2, 3, 4, 5]))
                        )
                    temp_line["info"]["onPremisesLastSyncDateTimeTS"] = str(round(time.time() - 10000))
                    temp_line["info"]["registrationDateTimeTS"] = str(
                            round(time.time() - 10000 * random.choice([1, 2, 3, 4, 5]))
                        )
                    output.append(temp_line)
                else:
                    print("ERROR - file not supported: ", file)
            
            # create the new .json file to upload to rz 
            handle_output(output=output, filename=file)
        
        print("SUCCESS - updated", file)
    
    # delete the existing assets 
    delete_existing_assets()
    # upload the updated tasks     
    upload_tasks()

if __name__ == "__main__":
    main()