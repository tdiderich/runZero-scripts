import os
import csv
import requests
import sys
import re
from typing import Dict, Optional, Any, List
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

# ————————————————
# Load .env into os.environ
# ————————————————
load_dotenv()  # expects .env with RUNZERO_* vars

# ————————————————
# Seed token_store & config_store from env
# ————————————————
token_store: Dict[str, str] = {}
config_store: Dict[str, str] = {}

if env := os.getenv("RUNZERO_EXPORT_TOKEN"):
    token_store["export"] = env
if env := os.getenv("RUNZERO_ORG_TOKEN"):
    token_store["org"] = env
if env := os.getenv("RUNZERO_ACCOUNT_TOKEN"):
    token_store["account"] = env

if env := os.getenv("RUNZERO_ORG_ID"):
    config_store["org_id"] = env

if env := os.getenv("RUNZERO_QUERIES_PATH"):
    RUNZERO_QUERIES_PATH = env

# ————————————————
# Allowed search-key whitelists
# ————————————————
ASSET_KEYS = {
    "id",
    "organization",
    "site",
    "detected_by",
    "type",
    "os",
    "os_version",
    "hw",
    "address",
    "addresses_scope",
    "addresses_extra",
    "newest_mac",
    "newest_mac_vendor",
    "newest_mac_age",
    "macs",
    "mac_vendors",
    "hostname",
    "hostnames",
    "risk",
    "risk_rank",
    "criticality",
    "criticality_rank",
    "owners",
    "tags",
    "domains",
    "service_count",
    "service_count_tcp",
    "service_count_udp",
    "service_count_arp",
    "service_count_icmp",
    "lowest_ttl",
    "lowest_rtt",
    "services",
    "alive",
    "first_seen_unix",
    "first_seen_iso",
    "last_updated_unix",
    "last_updated_iso",
    "last_seen_unix",
    "last_seen_iso",
    "comments",
    "service_ports_tcp",
    "service_ports_udp",
    "service_protocols",
    "service_products",
    "last_agent_name",
    "last_task_id",
    "source_ids",
    "sources",
    "custom_integration_ids",
    "eol_os",
    "eol_os_ext",
    "serialNumbers",
}

SERVICE_KEYS = {
    "service_id",
    "service_created_at",
    "service_address",
    "service_transport",
    "service_port",
    "service_protocol",
    "service_summary",
    "asset_id",
    "organization",
    "site",
    "detected_by",
    "type",
    "os",
    "os_version",
    "hw",
    "address",
    "addresses_scope",
    "addresses_extra",
    "newest_mac",
    "newest_mac_vendor",
    "newest_mac_age",
    "macs",
    "mac_vendors",
    "names",
    "tags",
    "domains",
    "service_count",
    "service_count_tcp",
    "service_count_udp",
    "service_count_arp",
    "service_count_icmp",
    "lowest_ttl",
    "lowest_rtt",
    "services",
    "alive",
    "first_seen_unix",
    "first_seen_iso",
    "last_updated_unix",
    "last_updated_iso",
    "last_seen_unix",
    "last_seen_iso",
    "comments",
    "service_ports_tcp",
    "service_ports_udp",
    "service_protocols",
    "service_products",
    "last_agent_name",
    "last_task_id",
    "service_source_ids",
    "service_custom_integration_ids",
}


def _find_invalid_keys(query: str, allowed: set) -> List[str]:
    raw = re.findall(r"([A-Za-z_][A-Za-z0-9_\.]*)\s*:", query)
    invalid = []
    for key in raw:
        base = key.split(".")[-1]
        if base not in allowed:
            invalid.append(key)
    return invalid


# ————————————————
# Lifespan: startup & shutdown logging via stderr
# ————————————————
@asynccontextmanager
async def lifespan(app: FastMCP):
    print("Initializing server…", file=sys.stderr)
    try:
        yield
        print("Server started and connected successfully", file=sys.stderr)
    finally:
        print("Shutting down server…", file=sys.stderr)


# ————————————————
# runZero MCP Server
# ————————————————
mcp = FastMCP("runZero MCP Server", lifespan=lifespan)
BASE_API_URL = "https://console.runzero.com/api/v1.0"


# ————————————————
# Tools: set_tokens / set_config
# ————————————————
@mcp.tool()
def set_tokens(
    export_token: Optional[str] = None,
    org_token: Optional[str] = None,
    account_token: Optional[str] = None,
) -> str:
    if export_token:
        token_store["export"] = export_token
    if org_token:
        token_store["org"] = org_token
    if account_token:
        token_store["account"] = account_token
    print(f"Tokens updated: {list(token_store.keys())}", file=sys.stderr)
    return f"✅ Tokens updated: {list(token_store.keys())}"


@mcp.tool()
def set_config(org_id: Optional[str] = None) -> str:
    if org_id:
        config_store["org_id"] = org_id
    print(f"Config updated: {config_store}", file=sys.stderr)
    return f"✅ Config updated: {config_store}"


# ————————————————
# Resources: inspect current state
# ————————————————
@mcp.resource("config://tokens")
def get_tokens() -> Dict[str, str]:
    print("Returned tokens resource", file=sys.stderr)
    return token_store or {"status": "No tokens set."}


@mcp.resource("config://settings")
def get_config() -> Dict[str, str]:
    print("Returned config resource", file=sys.stderr)
    return config_store or {"status": "No configuration set."}


# ————————————————
# Internal helpers
# ————————————————
def get_token_for_path(path: str) -> Optional[str]:
    if "/export" in path:
        return token_store.get("export")
    if "/org" in path:
        return token_store.get("org")
    if "/account" in path:
        return token_store.get("account")
    return None


def make_api_request(
    endpoint: str,
    method: str = "GET",
    params: Dict = None,
    data: Dict = None,
    headers: Dict = None,
) -> Any:
    url = f"{BASE_API_URL}{endpoint}"
    token = get_token_for_path(endpoint)
    if not token:
        return {"error": "No token. Run set_tokens first."}

    headers = headers or {}
    headers["Authorization"] = f"Bearer {token}"
    headers["Accept"] = "application/json"

    params = params or {}
    if "_oid" not in params and "org_id" in config_store:
        params["_oid"] = config_store["org_id"]

    try:
        resp = requests.request(method, url, params=params, json=data, headers=headers)
        resp.raise_for_status()
        ctype = resp.headers.get("Content-Type", "")
        if endpoint.endswith(".csv") or "text/csv" in ctype:
            return resp.text
        return resp.json()
    except Exception as e:
        print(f"API request {endpoint} failed: {e}", file=sys.stderr)
        return {"error": str(e)}


def _base_search(endpoint: str, query: str) -> Dict[str, Any]:
    params = {"search": query}
    print(f"Calling API search {endpoint} with query={query!r}", file=sys.stderr)
    result = make_api_request(endpoint, params=params)
    if isinstance(result, str):
        return {"csv": result}
    return result


# ————————————————
# Search tools with validation & override
# ————————————————
@mcp.tool()
def searchAssets(query: str, ignore_invalid: bool = False) -> Any:
    print(
        f"Message: searchAssets(query={query!r}, ignore_invalid={ignore_invalid})",
        file=sys.stderr,
    )
    invalid = _find_invalid_keys(query, ASSET_KEYS)
    if invalid and not ignore_invalid:
        return {
            "error": f"Invalid asset keys: {invalid}. "
            "To override, set ignore_invalid=True and try again."
        }
    if invalid:
        print(f"Warning: invalid asset keys {invalid}", file=sys.stderr)
    return _base_search("/export/org/assets.csv", query)


@mcp.tool()
def searchServices(query: str, ignore_invalid: bool = False) -> Any:
    print(
        f"Message: searchServices(query={query!r}, ignore_invalid={ignore_invalid})",
        file=sys.stderr,
    )
    invalid = _find_invalid_keys(query, SERVICE_KEYS)
    if invalid and not ignore_invalid:
        return {
            "error": f"Invalid service keys: {invalid}. "
            "To override, set ignore_invalid=True and try again."
        }
    if invalid:
        print(f"Warning: invalid service keys {invalid}", file=sys.stderr)
    return _base_search("/export/org/services.csv", query)


# ————————————————
# Query catalog: load from CSV
# ————————————————
def load_query_catalog_from_csv(
    path: str = RUNZERO_QUERIES_PATH,
) -> List[Dict[str, str]]:
    catalog: List[Dict[str, str]] = []
    with open(path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            catalog.append(
                {
                    "name": row["name"],
                    "type": row["type"],
                    "description": row["description"],
                    "query": row["query"],
                }
            )
    return catalog


QUERIES = load_query_catalog_from_csv()


@mcp.resource("docs://query_catalog")
def query_catalog() -> List[Dict[str, str]]:
    print("Message: query_catalog()", file=sys.stderr)
    return QUERIES


# ————————————————
# LLM prompt for dynamic query gen
# ————————————————
@mcp.prompt()
def build_query(topic: str) -> List[base.Message]:
    print(f"Message: build_query(topic={topic!r})", file=sys.stderr)
    return [
        base.SystemMessage(
            "You are a runZero assistant. When generating an asset search, you may use only these fields:\n"
            f"{', '.join(sorted(ASSET_KEYS))}\n\n"
            "When generating a service search, you may use only these fields:\n"
            f"{', '.join(sorted(SERVICE_KEYS))}"
        ),
        base.UserMessage(f"Create a runZero search query about “{topic}.”"),
    ]


# ————————————————
# Run
# ————————————————
if __name__ == "__main__":
    try:
        mcp.run()
    except Exception as e:
        print(f"Server disconnected unexpectedly: {e}", file=sys.stderr)
        raise
