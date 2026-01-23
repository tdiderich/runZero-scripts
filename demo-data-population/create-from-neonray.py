#!/usr/bin/env python3
import uuid
import time
import datetime
import os
import json
import gzip
import time
import random
import re
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from copy import deepcopy

# -----------------------------------------------------
# CONFIG (kept exactly like your old script)
# -----------------------------------------------------

RUNZERO_BASE_URL = "https://demo.runzero.com/api/v1.0"
RUNZERO_UPLOAD_ORG_ID = "fec36000-264b-4690-bdd6-16a18d82e906"
RUNZERO_UPLOAD_SITE_ID = "8746f1ec-0b7f-4958-8385-4a61c3bb8dc8"
RUNZERO_UPLOAD_ORG_TOKEN = os.environ["RUNZERO_UPLOAD_ORG_TOKEN"]
NEON_RAY_ORG_TOKEN = os.environ["NEON_RAY_ORG_TOKEN"]
JAMF_CUSTOM_INTEGRATION_ID = os.environ["RUNZERO_DEMO_JAMF_ID"]

# API token used to *pull* templates + assets
EXPORT_TOKEN = NEON_RAY_ORG_TOKEN

# Where we cache freshly fetched templates
TEMPLATE_DIR = "templates"

# Integrations we generate synthetic data for
INTEGRATIONS = ["crowdstrike", "qualys", "intune", "ldap", "mecm"]


# -----------------------------------------------------
# Helpers
# -----------------------------------------------------


def now_ts_ns():
    return int(time.time() * 1_000_000_000)


def decompress_jsonl(response):
    raw = response.content
    try:
        text = gzip.decompress(raw).decode()
    except:
        text = raw.decode()

    def parse_jsonl_lines(lines_text):
        out = []
        for line in lines_text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            out.extend(normalize_items([item]))
        return out

    def normalize_items(items):
        out = []
        for item in items:
            # Some JSONL entries are double-encoded as JSON strings.
            if isinstance(item, str):
                try:
                    item = json.loads(item)
                except json.JSONDecodeError:
                    continue
            if isinstance(item, list):
                out.extend(item)
            else:
                out.append(item)
        return out

    # Some endpoints return full JSON (array or object) instead of JSONL.
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        parsed = None
    if parsed is not None:
        if isinstance(parsed, list):
            return normalize_items(parsed)
        if isinstance(parsed, str):
            try:
                parsed = json.loads(parsed)
            except json.JSONDecodeError:
                return parse_jsonl_lines(parsed)
            if isinstance(parsed, list):
                return normalize_items(parsed)
            return normalize_items([parsed])
        if isinstance(parsed, dict):
            for key in ("data", "rows", "results", "items"):
                if key in parsed:
                    value = parsed[key]
                    if isinstance(value, list):
                        return normalize_items(value)
                    if isinstance(value, str):
                        return parse_jsonl_lines(value)
            return [parsed]
        return normalize_items([parsed])

    return parse_jsonl_lines(text)


def write_and_compress(rows, filename):
    gz_path = f"{filename}.json.gz"

    with gzip.open(gz_path, "wb") as gz:
        for rec in rows:
            line = json.dumps(rec, separators=(",", ":"))
            gz.write(line.encode() + b"\n")

    print(f"[output] wrote {gz_path}")
    return gz_path


def clone(obj):
    return json.loads(json.dumps(obj))


def os_vendor_tokens(value):
    if not value:
        return set()
    if not isinstance(value, str):
        value = str(value)
    text = value.lower()
    tokens = set(re.findall(r"[a-z0-9]+", text))

    if "windows" in tokens or "win" in tokens:
        tokens.add("microsoft")
    if "microsoft" in tokens:
        tokens.add("windows")

    if tokens.intersection({"mac", "macos", "osx", "ios"}):
        tokens.add("apple")
    if "apple" in tokens:
        tokens.update({"mac", "macos", "ios"})

    if "android" in tokens:
        tokens.add("android")

    if tokens.intersection({"chromeos", "chromebook"}):
        tokens.add("google")
    if "google" in tokens:
        tokens.add("google")

    linux_tokens = {
        "linux",
        "ubuntu",
        "debian",
        "redhat",
        "rhel",
        "centos",
        "fedora",
        "suse",
        "opensuse",
        "alpine",
        "kali",
        "arch",
        "mint",
    }
    if tokens.intersection(linux_tokens):
        tokens.add("linux")

    return tokens


def guess_template_os_vendor(integration, template):
    info = template.get("info", {})
    candidates = []

    if integration == "intune":
        candidates = [
            info.get("operatingSystem"),
            info.get("osPlatform"),
            info.get("osVersion"),
            info.get("osType"),
        ]
    elif integration == "ldap":
        candidates = [
            info.get("operatingSystem"),
            info.get("operatingSystemVersion"),
        ]
    elif integration == "qualys":
        candidates = [info.get("host.os"), info.get("os")]
    elif integration == "mecm":
        candidates = [
            info.get("deviceOS"),
            info.get("deviceOSBuild"),
            info.get("deviceOSName"),
        ]
    elif integration == "crowdstrike":
        candidates = [
            info.get("platformName"),
            info.get("osVersion"),
            info.get("osProductName"),
        ]

    for candidate in candidates:
        if isinstance(candidate, str) and candidate.strip():
            return candidate
        if isinstance(candidate, list) and candidate:
            return candidate[0]

    for key, value in info.items():
        if not isinstance(value, str):
            continue
        lowered = key.lower()
        if "os" in lowered or "platform" in lowered:
            return value

    return None


def matches_os_vendor(asset_vendor, template_vendor):
    asset_tokens = os_vendor_tokens(asset_vendor)
    template_tokens = os_vendor_tokens(template_vendor)
    if not asset_tokens or not template_tokens:
        return False
    return not asset_tokens.isdisjoint(template_tokens)


def choose_template(integration, templates, asset):
    if not templates:
        return None, False

    asset_vendor = asset.get("os_vendor")
    matches = [
        t
        for t in templates
        if matches_os_vendor(asset_vendor, guess_template_os_vendor(integration, t))
    ]
    if matches:
        seed = f"{asset.get('id','')}-{integration}-match"
        idx = uuid.uuid5(uuid.NAMESPACE_DNS, seed).int % len(matches)
        return matches[idx], True

    seed = f"{asset.get('id','')}-{integration}-fallback"
    idx = uuid.uuid5(uuid.NAMESPACE_DNS, seed).int % len(templates)
    return templates[idx], False


def scrub_os_fields(integration, info):
    os_fields = {
        "intune": {"operatingSystem", "osPlatform", "osVersion", "osType"},
        "ldap": {"operatingSystem", "operatingSystemVersion"},
        "qualys": {"host.os"},
        "mecm": {"deviceOS", "deviceOSBuild", "deviceOSName"},
        "crowdstrike": {"platformName", "osVersion", "osProductName"},
    }
    for key in os_fields.get(integration, set()):
        info.pop(key, None)


# -----------------------------------------------------
# Integration applicability rules
# -----------------------------------------------------


def qualifies(asset, integration):
    os_vendor = (asset.get("os_vendor") or "").lower()
    asset_type = (asset.get("type") or "").lower()
    has_ip = bool(asset.get("addresses"))

    if integration == "crowdstrike":
        return has_ip and asset_type in ["server", "workstation", "laptop"]

    if integration == "qualys":
        return has_ip

    if integration == "intune":
        return os_vendor in ["microsoft", "apple", "google", "android"]

    if integration == "ldap":
        return os_vendor in ["microsoft"]

    if integration == "mecm":
        return os_vendor == "microsoft" and asset_type in ["server", "workstation"]

    return False


# -----------------------------------------------------
# Patching logic (synthetic values over real template)
# -----------------------------------------------------


def gen_det_uuid(asset, integration, suffix=""):
    base = f"{asset.get('id','')}-{integration}-{suffix}"
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, base))


def patch_row(integration, template, asset, os_matched):
    t = clone(template)
    t["ts"] = now_ts_ns()

    info = t.get("info", {})

    hostname = (asset.get("names") or [None])[0]
    ip = (asset.get("addresses") or [None])[0]
    mac = (asset.get("macs") or [None])[0]
    os_vendor = asset.get("os_vendor")
    os_version = asset.get("os_version")

    def set_or_clear(key, value):
        if value:
            info[key] = value
        else:
            info.pop(key, None)

    # ==========================================================
    # INTUNE
    # ==========================================================
    if integration == "intune":
        if hostname:
            info["deviceName"] = hostname
            info["managedDeviceName"] = (
                hostname + "-" + gen_det_uuid(asset, "intune")[:8]
            )
        else:
            info.pop("deviceName", None)
            info.pop("managedDeviceName", None)

        set_or_clear("ethernetMacAddress", mac)
        if os_matched and os_version:
            info["osVersion"] = os_version
        elif not os_matched:
            info.pop("osVersion", None)

        # Critical unique fields
        info["easDeviceID"] = gen_det_uuid(asset, "intune", "eas")
        info["id"] = gen_det_uuid(asset, "intune", "id")

        info["lastSyncDateTimeTS"] = str(int(time.time()))

    # ==========================================================
    # LDAP
    # ==========================================================
    elif integration == "ldap":
        set_or_clear("dNSHostName", hostname)

        # dnsIPs must be STRING not LIST
        if ip:
            info["dnsIPs"] = ip

        if os_matched and os_vendor:
            info["operatingSystem"] = os_vendor
        elif not os_matched:
            info.pop("operatingSystem", None)

        if os_matched and os_version:
            info["operatingSystemVersion"] = os_version
        elif not os_matched:
            info.pop("operatingSystemVersion", None)

        # Unique IDs
        info["objectGUID"] = gen_det_uuid(asset, "ldap", "guid")
        info["objectSid"] = gen_det_uuid(asset, "ldap", "sid")
        info["id"] = gen_det_uuid(asset, "ldap", "id")

        # DN must be string
        if hostname:
            info["distinguishedName"] = f"CN={hostname},OU=Computers,DC=rz,DC=local"
        else:
            info.pop("distinguishedName", None)

        # objectClass must be tab-separated string (not array)
        if "objectClass" in info and isinstance(info["objectClass"], list):
            info["objectClass"] = "\t".join(info["objectClass"])

        # servicePrincipalName must be tab-separated — usually already is
        if "servicePrincipalName" in info and isinstance(info["servicePrincipalName"], list):
            info["servicePrincipalName"] = "\t".join(info["servicePrincipalName"])

    # ==========================================================
    # QUALYS
    # ==========================================================
    elif integration == "qualys":
        if ip:
            info["host.ip"] = ip
        set_or_clear("host.hostname", hostname)
        if os_matched and os_vendor:
            info["host.os"] = os_vendor
        elif not os_matched:
            info.pop("host.os", None)

        info["id"] = gen_det_uuid(asset, "qualys", "id")
        info["host.id"] = gen_det_uuid(asset, "qualys", "hostid")

        # keep _detections as-is (base64)

        nowts = str(int(time.time()))
        info["detection.firstFoundTS"] = nowts
        info["detection.lastFoundTS"] = nowts
        info["host.lastScannedDateTimeTS"] = nowts
        info["host.lastVMScannedDateTS"] = nowts

    # ==========================================================
    # MECM
    # ==========================================================
    elif integration == "mecm":
        set_or_clear("name", hostname)
        if ip:
            info["ipAddress"] = ip
        set_or_clear("macAddress", mac)
        if os_matched and os_version:
            info["deviceOSBuild"] = os_version
        elif not os_matched:
            info.pop("deviceOSBuild", None)

        # unique identifiers
        info["machineID"] = gen_det_uuid(asset, "mecm", "machine")
        info["smsID"] = gen_det_uuid(asset, "mecm", "sms")
        info["smbiosGUID"] = gen_det_uuid(asset, "mecm", "smbios")

        info["lastActiveTime"] = str(int(time.time()))

    # ==========================================================
    # CROWDSTRIKE
    # ==========================================================
    elif integration == "crowdstrike":
        if ip:
            info["localIP"] = ip
            info["connectionIP"] = ip
            info["discover.currentLocalIP"] = ip
            info["discover.localIPAddresses"] = ip
            info["discover.networkInterfaces.localIP"] = ip
            info["discover.localIPsCount"] = "1"
        else:
            for key in (
                "localIP",
                "connectionIP",
                "discover.currentLocalIP",
                "discover.localIPAddresses",
                "discover.networkInterfaces.localIP",
                "discover.localIPsCount",
            ):
                info.pop(key, None)
        set_or_clear("macAddress", mac)
        set_or_clear("connectionMACAddress", mac)
        set_or_clear("hostname", hostname)
        if os_matched and os_version:
            info["osVersion"] = os_version
        elif not os_matched:
            info.pop("osVersion", None)

        # Unique IDs
        info["deviceID"] = gen_det_uuid(asset, "crowdstrike", "device")
        info["cid"] = gen_det_uuid(asset, "crowdstrike", "cid")
        info["discover.id"] = gen_det_uuid(asset, "crowdstrike", "discover")
        info["instanceID"] = gen_det_uuid(asset, "crowdstrike", "instance")

        # timestamps
        nowts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        info["lastSeen"] = nowts
        info["modifiedTS"] = str(int(time.time()))
        info["firstLoginTS"] = str(int(time.time()) - 5000)

        # keep _applications and _vulnerabilities as-is

        # OS fields
        if os_matched and os_vendor:
            info["platformName"] = os_vendor
        elif not os_matched:
            info.pop("platformName", None)

        if os_matched and os_version:
            info["productTypeDesc"] = asset.get("type", "Workstation")

    # ==========================================================
    # Anything else → unchanged
    # ==========================================================

    if not os_matched:
        scrub_os_fields(integration, info)

    t["info"] = info
    return t


# -----------------------------------------------------
# API calls
# -----------------------------------------------------


def fetch_assets():
    url = f"{RUNZERO_BASE_URL}/export/org/assets.json"
    resp = requests.get(url, headers={"Authorization": f"Bearer {EXPORT_TOKEN}"})
    resp.raise_for_status()
    return resp.json()


def fetch_tasks():
    url = f"{RUNZERO_BASE_URL}/export/org/tasks.json"
    resp = requests.get(url, headers={"Authorization": f"Bearer {EXPORT_TOKEN}"})
    resp.raise_for_status()
    return resp.json()


def fetch_metadata():
    url = "https://console.runzero.com/api/v1.0/metadata"
    return requests.get(url).json()


def fetch_task_data(integration, task_id):
    url = f"{RUNZERO_BASE_URL}/org/tasks/{task_id}/data"
    resp = requests.get(url, headers={"Authorization": f"Bearer {EXPORT_TOKEN}"})
    resp.raise_for_status()
    return resp


def fetch_upload_asset_ids():
    url = f"{RUNZERO_BASE_URL}/export/org/assets.json"
    resp = requests.get(
        url,
        headers={"Authorization": f"Bearer {RUNZERO_UPLOAD_ORG_TOKEN}"},
        params={"fields": "id"},
    )
    if resp.status_code == 200:
        return [row["id"] for row in resp.json() if "id" in row]
    print(f"[delete:ERR] fetching assets failed status={resp.status_code}")
    return []


def chunker(data):
    """Yield successive chunks with random sizes (multiples of 10 from 10 to 100)."""
    i = 0
    while i < len(data):
        size = random.randrange(10, 110, 10)
        yield data[i : i + size]
        i += size


DELETE_SESSION = requests.Session()
DELETE_RETRIES = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
DELETE_SESSION.mount("https://", HTTPAdapter(max_retries=DELETE_RETRIES))


def delete_assets(asset_chunk, attempt=1):
    url = f"{RUNZERO_BASE_URL}/org/assets/bulk/delete"
    max_attempts = 3
    start_time = time.perf_counter()

    try:
        resp = DELETE_SESSION.delete(
            url,
            headers={"Authorization": f"Bearer {RUNZERO_UPLOAD_ORG_TOKEN}"},
            json={"asset_ids": asset_chunk},
            timeout=(10, 60),
        )
        duration = time.perf_counter() - start_time

        if resp.status_code == 204:
            print(
                f"[delete] batch size={len(asset_chunk):<3} duration={duration:.3f}s OK"
            )
            return True
        print(f"[delete:ERR] status={resp.status_code} body={resp.text}")
        return False
    except (
        requests.exceptions.ConnectionError,
        requests.exceptions.ChunkedEncodingError,
    ):
        if attempt <= max_attempts:
            wait = attempt * 5
            print(
                f"[delete:WARN] connection dropped attempt={attempt}/{max_attempts}, retry in {wait}s"
            )
            time.sleep(wait)
            return delete_assets(asset_chunk, attempt + 1)
        print(f"[delete:ERR] failed after {max_attempts} attempts")
        return False


def delete_existing_assets():
    assets = fetch_upload_asset_ids()
    if not assets:
        print("[delete] no assets found")
        return

    print(f"[delete] found {len(assets)} assets; deleting...")
    for chunk in chunker(assets):
        success = delete_assets(chunk)
        if not success:
            time.sleep(10)
        time.sleep(1.5)


# -----------------------------------------------------
# Template extraction
# -----------------------------------------------------


def extract_templates(tasks_by_integration):
    os.makedirs(TEMPLATE_DIR, exist_ok=True)
    templates = {}

    for integ, task_id in tasks_by_integration.items():
        resp = fetch_task_data(integ, task_id)
        rows = decompress_jsonl(resp)

        config_row = next(
            (r for r in rows if isinstance(r, dict) and r.get("type") == "config"),
            None,
        )
        result_rows = [
            r for r in rows if isinstance(r, dict) and r.get("type") == "result"
        ]

        if not config_row:
            types = sorted(
                {r.get("type") for r in rows if isinstance(r, dict) and r.get("type")}
            )
            print(f"[WARN] no config row for {integ}; types seen={types}")
            continue
        if not result_rows:
            types = sorted(
                {r.get("type") for r in rows if isinstance(r, dict) and r.get("type")}
            )
            print(f"[WARN] no result rows for {integ}; types seen={types}")
            continue

        # Save templates
        path_cfg = f"{TEMPLATE_DIR}/integration_{integ}_config.json"
        path_res = f"{TEMPLATE_DIR}/integration_{integ}_results.json"

        with open(path_cfg, "w") as f:
            f.write(json.dumps(config_row, separators=(",", ":")))

        with open(path_res, "w") as f:
            f.write(json.dumps(result_rows, separators=(",", ":")))

        templates[integ] = {
            "config": config_row,
            "results": result_rows,
        }

        print(f"[template] wrote {path_cfg} and {path_res}")

    return templates


def load_template_config(integration):
    with open(f"{TEMPLATE_DIR}/integration_{integration}_config.json") as f:
        return json.loads(f.read())


def load_template_results(integration):
    with open(f"{TEMPLATE_DIR}/integration_{integration}_results.json") as f:
        return json.loads(f.read())


# -----------------------------------------------------
# MAIN
# -----------------------------------------------------


def main():
    metadata = fetch_metadata()
    source_map = metadata["Sources"]

    assets = fetch_assets()
    tasks = fetch_tasks()

    print(f"[info] {len(assets)} assets found")
    print(f"[info] {len(tasks)} tasks found")

    # Build map: integration -> latest task_id
    integ_task_map = {}

    for t in tasks:
        source_id = str(t.get("source_id"))
        tid = t.get("id")
        integ = source_map.get(source_id)
        if integ in INTEGRATIONS:
            integ_task_map[integ] = tid

    print("[info] integrations found:", integ_task_map)

    # Step 1: extract templates from NeonRay
    extract_templates(integ_task_map)

    # Step 2: produce synthetic output from templates
    for integ in INTEGRATIONS:
        if integ not in integ_task_map:
            print(f"[skip] no real template for {integ}")
            continue

        cfg = load_template_config(integ)
        results = load_template_results(integ)

        out = []

        # Add REAL config row first
        out.append(cfg)

        # Then synthetic results
        if not results:
            print(f"[warn] no result templates for {integ}")
            continue

        for a in assets:
            if qualifies(a, integ):
                template, os_matched = choose_template(integ, results, a)
                if template:
                    out.append(patch_row(integ, template, a, os_matched))

        if out:
            write_and_compress(out, f"integration_{integ}")
        else:
            print(f"[warn] no assets qualified for {integ}")

    if "rumble" in source_map.values():
        # find the rumble task_id
        rumble_task_id = None
        for t in tasks:
            sid = str(t.get("source_id"))
            name = source_map.get(sid)
            if name == "rumble":
                rumble_task_id = t["id"]

        if rumble_task_id:
            print(f"[rumble] fetching raw task {rumble_task_id}")

            resp = fetch_task_data("rumble", rumble_task_id)

            # Rumble data is already gzipped
            raw_path = "integration_rumble.json.gz"
            with open(raw_path, "wb") as f:
                f.write(resp.content)

            print(f"[rumble] wrote raw {raw_path}")

        else:
            print("[rumble] no rumble task found")

    # -----------------------------------------------------
    # AUTO-UPLOAD GENERATED DATA TO RUNZERO
    # -----------------------------------------------------
    print("\n[delete] removing existing assets before upload...")
    delete_existing_assets()

    print("\n[upload] starting uploads to runZero...")

    upload_map = {
        "crowdstrike": "CrowdStrike Integration",
        "qualys": "Qualys Integration",
        "intune": "Intune Integration",
        "ldap": "LDAP Integration",
        "mecm": "MECM Integration",
        "rumble": "runZero Scan",
    }

    upload_integrations = ["rumble"] + INTEGRATIONS

    for integ in upload_integrations:
        gz_name = f"integration_{integ}.json.gz"

        if not os.path.exists(gz_name):
            print(f"[upload:skip] no file for {integ}")
            continue

        friendly_name = upload_map.get(integ, integ.capitalize())

        upload_url = f"{RUNZERO_BASE_URL}/org/sites/{RUNZERO_UPLOAD_SITE_ID}/import"

        params = {
            "_oid": RUNZERO_UPLOAD_ORG_ID,
            "name": friendly_name,
        }

        headers = {
            "Authorization": f"Bearer {RUNZERO_UPLOAD_ORG_TOKEN}",
        }

        with open(gz_name, "rb") as f:
            body = f.read()

        print(f"[upload] uploading {gz_name} as '{friendly_name}'...")

        resp = requests.put(
            upload_url,
            headers=headers,
            params=params,
            data=body,
        )

        if resp.status_code == 200:
            new_task_id = resp.json().get("id")
            print(f"[upload:success] {gz_name} → task {new_task_id}")
        else:
            print(f"[upload:FAIL] {gz_name} status={resp.status_code} body={resp.text}")


if __name__ == "__main__":
    main()
