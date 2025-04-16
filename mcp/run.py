# runzero_mcp_server.py

from typing import Dict, Optional, Any
from mcp.server.fastmcp import FastMCP, Context

# Create an MCP server with the name "runZero MCP Server"
mcp = FastMCP("runZero MCP Server")


# Local in-memory store — optionally replace with disk persistence
token_store: Dict[str, str] = {}


# -----------------------------------------------------------
# Tool: set_tokens
# -----------------------------------------------------------
@mcp.tool()
def set_tokens(
    export_token: Optional[str] = None,
    org_token: Optional[str] = None,
    account_token: Optional[str] = None,
) -> str:
    """
    Set one or more runZero API tokens.

    Arguments:
      - export_token: Token for /export endpoints
      - org_token: Token for /org endpoints
      - account_token: Token for /account endpoints
    """
    if export_token:
        token_store["export"] = export_token
    if org_token:
        token_store["org"] = org_token
    if account_token:
        token_store["account"] = account_token

    return f"✅ Tokens updated. Current set: {list(token_store.keys())}"


# -----------------------------------------------------------
# Resource: config://tokens
# -----------------------------------------------------------
@mcp.resource("config://tokens")
def get_tokens() -> Dict[str, str]:
    """Returns currently set tokens by type."""
    return token_store or {"status": "No tokens set."}


# -----------------------------------------------------------
# Internal Helper: select token by API path
# -----------------------------------------------------------
def get_token_for_path(path: str) -> Optional[str]:
    if "/export" in path:
        return token_store.get("export")
    if "/org" in path:
        return token_store.get("org")
    if "/account" in path:
        return token_store.get("account")
    return None


# -----------------------------------------------------------
# Tool: searchAssets
# -----------------------------------------------------------
@mcp.tool()
def searchAssets(query: str, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
    """
    Search the asset inventory using runZero's search syntax.

    Parameters:
        query: The search query string (e.g., 'alive:t AND os:linux')
        limit: Max number of results to return (default: 100)
        offset: Result offset for pagination (default: 0)

    Examples:
        - Find Linux assets: 'alive:t AND os:linux'
        - Find SSH hosts with public IPs: 'protocol:ssh AND private:f'
        - Find old TLS Windows hosts: 'os:windows AND tls.version:<1.2'

    Returns:
        A dictionary containing the search input and mock results.
    """
    # Simulated response
    simulated_assets = [
        {
            "id": "asset1",
            "os": "linux",
            "hostname": "server1.example.com",
            "alive": True,
        },
        {
            "id": "asset2",
            "os": "windows",
            "hostname": "server2.example.com",
            "alive": True,
        },
    ]
    return {
        "query": query,
        "limit": limit,
        "offset": offset,
        "results": simulated_assets[:limit],
    }


# -----------------------------------------------------------
# Resource: search://syntax
# -----------------------------------------------------------
@mcp.resource("search://syntax")
def search_syntax() -> str:
    """Returns a reference sheet for runZero query syntax."""
    return """
runZero Search Syntax Reference
==============================

Fields:
  - os: Operating system (e.g., os:linux, os:win*)
  - protocol: Network protocol (e.g., protocol:ssh, protocol:https)
  - alive: Active status (alive:t or alive:f)
  - private: IP type (private:t for private IPs, private:f for public)
  - created_at: Timestamp in ISO 8601 (e.g., created_at:>2024-01-01)
  - tags: Asset tags
  - mac: MAC address
  - hostname: Hostname (supports wildcards)

Modifiers:
  - AND / OR / NOT
  - : (match), :> / :< (range), has_ (exists)

Notes:
  - Case-insensitive
  - Wildcard support with '*'
  - Date filters use ISO 8601 format
"""

@mcp.tool()
def exportAssetsJSON(ctx: Optional[Context] = None) -> str:
    """
    Exports the asset inventory

    Endpoint: /export/org/assets.json
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/assets.json"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def exportAssetsJSONL(ctx: Optional[Context] = None) -> str:
    """
    Asset inventory as JSON line-delimited

    Endpoint: /export/org/assets.jsonl
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/assets.jsonl"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def exportAssetsCSV(ctx: Optional[Context] = None) -> str:
    """
    Asset inventory as CSV

    Endpoint: /export/org/assets.csv
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/assets.csv"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def exportAssetsNmapXML(ctx: Optional[Context] = None) -> str:
    """
    Asset inventory as Nmap-style XML

    Endpoint: /export/org/assets.nmap.xml
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/assets.nmap.xml"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def exportServicesJSON(ctx: Optional[Context] = None) -> str:
    """
    Service inventory as JSON

    Endpoint: /export/org/services.json
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/services.json"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def exportServicesJSONL(ctx: Optional[Context] = None) -> str:
    """
    Service inventory as JSON line-delimited

    Endpoint: /export/org/services.jsonl
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/services.jsonl"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def exportServicesCSV(ctx: Optional[Context] = None) -> str:
    """
    Service inventory as CSV

    Endpoint: /export/org/services.csv
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/services.csv"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def exportSitesJSON(ctx: Optional[Context] = None) -> str:
    """
    Export all sites

    Endpoint: /export/org/sites.json
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/sites.json"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def exportSitesJSONL(ctx: Optional[Context] = None) -> str:
    """
    Site list as JSON line-delimited

    Endpoint: /export/org/sites.jsonl
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/sites.jsonl"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def exportSitesCSV(ctx: Optional[Context] = None) -> str:
    """
    Site list as CSV

    Endpoint: /export/org/sites.csv
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/sites.csv"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def exportWirelessJSON(ctx: Optional[Context] = None) -> str:
    """
    Wireless inventory as JSON

    Endpoint: /export/org/wireless.json
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/wireless.json"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def exportWirelessJSONL(ctx: Optional[Context] = None) -> str:
    """
    Wireless inventory as JSON line-delimited

    Endpoint: /export/org/wireless.jsonl
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/wireless.jsonl"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def exportWirelessCSV(ctx: Optional[Context] = None) -> str:
    """
    Wireless inventory as CSV

    Endpoint: /export/org/wireless.csv
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/wireless.csv"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def exportSoftwareJSON(ctx: Optional[Context] = None) -> str:
    """
    Exports the software inventory

    Endpoint: /export/org/software.json
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/software.json"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def exportSoftwareJSONL(ctx: Optional[Context] = None) -> str:
    """
    Software inventory as JSON line-delimited

    Endpoint: /export/org/software.jsonl
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/software.jsonl"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def exportSoftwareCSV(ctx: Optional[Context] = None) -> str:
    """
    Software inventory as CSV

    Endpoint: /export/org/software.csv
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/software.csv"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def exportVulnerabilitiesJSON(ctx: Optional[Context] = None) -> str:
    """
    Export the vulnerability inventory as JSON

    Endpoint: /export/org/vulnerabilities.json
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/vulnerabilities.json"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def exportVulnerabilitiesJSONL(ctx: Optional[Context] = None) -> str:
    """
    Export the vulnerability inventory as JSON line-delimited

    Endpoint: /export/org/vulnerabilities.jsonl
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/vulnerabilities.jsonl"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def exportVulnerabilitiesCSV(ctx: Optional[Context] = None) -> str:
    """
    Export the vulnerability inventory as CSV

    Endpoint: /export/org/vulnerabilities.csv
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/vulnerabilities.csv"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def exportCertificatesCSV(ctx: Optional[Context] = None) -> str:
    """
    Export the certificate inventory as CSV

    Endpoint: /export/org/certificates.csv
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/certificates.csv"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def exportCertificatesJSON(ctx: Optional[Context] = None) -> str:
    """
    Export the certificate inventory as JSON

    Endpoint: /export/org/certificates.json
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/certificates.json"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def exportCertificatesJSONL(ctx: Optional[Context] = None) -> str:
    """
    Export the certificate inventory as JSONL line-delimited

    Endpoint: /export/org/certificates.jsonl
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/certificates.jsonl"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def exportDirectoryUsersJSON(ctx: Optional[Context] = None) -> str:
    """
    Exports the user inventory

    Endpoint: /export/org/users.json
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/users.json"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def exportDirectoryUsersJSONL(ctx: Optional[Context] = None) -> str:
    """
    User inventory as JSON line-delimited

    Endpoint: /export/org/users.jsonl
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/users.jsonl"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def exportDirectoryUsersCSV(ctx: Optional[Context] = None) -> str:
    """
    User inventory as CSV

    Endpoint: /export/org/users.csv
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/users.csv"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def exportDirectoryGroupsJSON(ctx: Optional[Context] = None) -> str:
    """
    Exports the group inventory

    Endpoint: /export/org/groups.json
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/groups.json"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def exportDirectoryGroupsJSONL(ctx: Optional[Context] = None) -> str:
    """
    Group inventory as JSON line-delimited

    Endpoint: /export/org/groups.jsonl
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/groups.jsonl"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def exportDirectoryGroupsCSV(ctx: Optional[Context] = None) -> str:
    """
    Group inventory as CSV

    Endpoint: /export/org/groups.csv
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/groups.csv"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def exportFindingsCSV(ctx: Optional[Context] = None) -> str:
    """
    Export findings as CSV

    Endpoint: /export/org/findings.csv
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/findings.csv"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def exportFindingsJSON(ctx: Optional[Context] = None) -> str:
    """
    Export findings as JSON

    Endpoint: /export/org/findings.json
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/findings.json"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def exportFindingsJSONL(ctx: Optional[Context] = None) -> str:
    """
    Export findings as JSON line-delimited

    Endpoint: /export/org/findings.jsonl
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/findings.jsonl"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def exportSubnetUtilizationStatsCSV(ctx: Optional[Context] = None) -> str:
    """
    Subnet utilization statistics as as CSV

    Endpoint: /export/org/subnet.stats.csv
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/subnet.stats.csv"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def exportSNMPARPCacheCSV(ctx: Optional[Context] = None) -> str:
    """
    SNMP ARP cache data as CSV

    Endpoint: /export/org/snmp.arpcache.csv
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/snmp.arpcache.csv"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def exportTasksJSON(ctx: Optional[Context] = None) -> str:
    """
    Exports organization tasks

    Endpoint: /export/org/tasks.json
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/tasks.json"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def exportTasksJSONL(ctx: Optional[Context] = None) -> str:
    """
    Organization tasks as JSON line-delimited

    Endpoint: /export/org/tasks.jsonl
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/tasks.jsonl"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def deleteAccountOrganizationExportTokenDeprecated(ctx: Optional[Context] = None) -> str:
    """
    Removes the export token from the specified organization

    Endpoint: /account/orgs/{org_id}/exportToken
    Method: DELETE
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/account/orgs/{org_id}/exportToken"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def rotateAccountOrganizationExportTokenDeprecated(ctx: Optional[Context] = None) -> str:
    """
    Rotates an organization export token and returns the updated token

    Endpoint: /account/orgs/{org_id}/exportToken/rotate
    Method: PATCH
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/account/orgs/{org_id}/exportToken/rotate"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def getAccountOrganizationExportTokens(ctx: Optional[Context] = None) -> str:
    """
    Get all active export tokens for an organization

    Endpoint: /account/orgs/{org_id}/exportTokens
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/account/orgs/{org_id}/exportTokens"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def createAccountOrganizationExportToken(ctx: Optional[Context] = None) -> str:
    """
    Create a new export token for an organization

    Endpoint: /account/orgs/{org_id}/exportTokens
    Method: POST
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/account/orgs/{org_id}/exportTokens"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def getAccountOrganizationExportToken(ctx: Optional[Context] = None) -> str:
    """
    Get export token details

    Endpoint: /account/orgs/{org_id}/exportTokens/{key_id}
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/account/orgs/{org_id}/exportTokens/{key_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def deleteAccountOrganizationExportToken(ctx: Optional[Context] = None) -> str:
    """
    Removes the export token from the specified organization

    Endpoint: /account/orgs/{org_id}/exportTokens/{key_id}
    Method: DELETE
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/account/orgs/{org_id}/exportTokens/{key_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def rotateAccountOrganizationExportToken(ctx: Optional[Context] = None) -> str:
    """
    Rotates an organization export token and returns the updated token

    Endpoint: /account/orgs/{org_id}/exportTokens/{key_id}/rotate
    Method: PATCH
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/account/orgs/{org_id}/exportTokens/{key_id}/rotate"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def splunkAssetSyncCreatedJSON(ctx: Optional[Context] = None) -> str:
    """
    Exports the asset inventory in a sync-friendly manner using created_at as a checkpoint. Requires the Splunk entitlement.

    Endpoint: /export/org/assets/sync/created/assets.json
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/assets/sync/created/assets.json"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def splunkAssetSyncUpdatedJSON(ctx: Optional[Context] = None) -> str:
    """
    Exports the asset inventory in a sync-friendly manner using updated_at as a checkpoint. Requires the Splunk entitlement.

    Endpoint: /export/org/assets/sync/updated/assets.json
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/assets/sync/updated/assets.json"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def snowExportAssetsCSV(ctx: Optional[Context] = None) -> str:
    """
    Export an asset inventory as CSV for ServiceNow integration

    Endpoint: /export/org/assets.servicenow.csv
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/assets.servicenow.csv"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def snowExportAssetsJSON(ctx: Optional[Context] = None) -> str:
    """
    Exports the asset inventory as JSON

    Endpoint: /export/org/assets.servicenow.json
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/assets.servicenow.json"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def snowExportServicesCSV(ctx: Optional[Context] = None) -> str:
    """
    Export a service inventory as CSV for ServiceNow integration

    Endpoint: /export/org/services.servicenow.csv
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/services.servicenow.csv"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def snowServiceGraphExportAssetsJSON(ctx: Optional[Context] = None) -> str:
    """
    Exports the asset inventory as JSON

    Endpoint: /export/org/assets.servicegraph.json
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/assets.servicegraph.json"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

@mcp.tool()
def exportAssetsCiscoCSV(ctx: Optional[Context] = None) -> str:
    """
    Cisco serial number and model name export for Cisco Smart Net Total Care Service.

    Endpoint: /export/org/assets.cisco.csv
    Method: GET
    Requires: export_token
    """
    token = token_store.get("export")
    if not token:
        return "❌ No export token set. Please run set_tokens(export_token='...')"

    url = f"https://console.runzero.com/export/org/assets.cisco.csv"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Simulated call – replace with real `requests.get(url, headers=headers)` as needed
    return f"Simulated request to {url} with export_token (masked: {token[:4]}...{token[-4:]})"

# -----------------------------------------------------------
# Run the MCP Server
# -----------------------------------------------------------
if __name__ == "__main__":
    print("Starting runZero MCP Server on port 8000...")
    mcp.run()
