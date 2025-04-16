import csv
import requests
from typing import Dict, Optional, Any, List
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

# ————————————————
# runZero MCP Server
# ————————————————

mcp = FastMCP("runZero MCP Server")
BASE_API_URL = "https://console.runzero.com/api/v1.0"

token_store: Dict[str, str] = {}
config_store: Dict[str, str] = {}


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
    return f"✅ Tokens updated: {list(token_store.keys())}"


@mcp.tool()
def set_config(org_id: Optional[str] = None) -> str:
    if org_id:
        config_store["org_id"] = org_id
    return f"✅ Config updated: {config_store}"


# ————————————————
# Resources: inspect current state
# ————————————————
@mcp.resource("config://tokens")
def get_tokens() -> Dict[str, str]:
    return token_store or {"status": "No tokens set."}


@mcp.resource("config://settings")
def get_config() -> Dict[str, str]:
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
        if ctype in ("text/csv", "text/xml", "application/octet-stream"):
            return {
                "success": True,
                "message": f"Retrieved {endpoint}",
                "content_type": ctype,
            }
        return resp.json()
    except Exception as e:
        return {"error": str(e)}


def _base_search(endpoint: str, query: str, fields: Optional[str]) -> Dict[str, Any]:
    if "export" not in token_store:
        return {"error": "Export token not set. Use set_tokens(export_token=...)"}
    params = {"search": query}
    if fields:
        params["fields"] = fields
    result = make_api_request(endpoint, params=params)
    return (
        {"query": query, "fields": fields, "results": result}
        if isinstance(result, list)
        else result
    )


# ————————————————
# Search tools
# ————————————————
@mcp.tool()
def searchAssets(query: str, fields: Optional[str] = None) -> Any:
    """Search the asset inventory."""
    return _base_search("/export/org/assets.json", query, fields)


@mcp.tool()
def searchServices(query: str, fields: Optional[str] = None) -> Any:
    """Search the service inventory."""
    return _base_search("/export/org/services.json", query, fields)


@mcp.tool()
def searchWireless(query: str, fields: Optional[str] = None) -> Any:
    """Search the wireless inventory."""
    return _base_search("/export/org/wireless.json", query, fields)


@mcp.tool()
def searchUsers(query: str, fields: Optional[str] = None) -> Any:
    """Search the user inventory."""
    return _base_search("/export/org/users.json", query, fields)


# ————————————————
# Query catalog: load from CSV
# ————————————————
def load_query_catalog_from_csv(path: str = "queries.csv") -> List[Dict[str, str]]:
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
    """
    Return every curated query from the PDF (name, type, description, query).
    """
    return QUERIES


# ————————————————
# LLM prompt for dynamic query gen
# ————————————————
@mcp.prompt()
def build_query(topic: str) -> List[base.Message]:
    return [
        base.UserMessage(
            f"Create a runZero search query about “{topic}”.\n"
            f"See docs://query_catalog for full list of examples."
        )
    ]


# ————————————————
# Run
# ————————————————
if __name__ == "__main__":
    print("Starting runZero MCP Server on port 8000…")
    mcp.run()
