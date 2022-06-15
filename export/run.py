import requests
import os
import urllib.parse

RUMBLE_EXPORT_TOKEN = os.environ["RUMBLE_EXPORT_TOKEN"]
HEADERS = {"Authorization": f"Bearer {RUMBLE_EXPORT_TOKEN}"}
BASE_URL = "https://console.rumble.run/api/v1.0"


def main():
    searches = [
        {"type": "assets", "search": "_asset.protocol:tls"},
        {"type": "assets", "search": "_asset.protocol:ntp"},
        {
            "type": "services",
            "search": "_asset.protocol:ntp and protocol:ntp and has:ntp.skew",
        },
        {"type": "asset", "search": "_asset.protocol:tls AND tls.notAfterTS:<now"},
        {"type": "asset", "search": 'protocol:="mountd" and nfs.allowed:"%=*"'},
        {"type": "asset", "search": "_asset.protocol:tls AND tls.notAfterTS:<6weeks"},
        {
            "type": "services",
            "search": "_asset.protocol:ntp and protocol:ntp and has:ntp.skew",
        },
        {
            "type": "services",
            "search": '(_asset.protocol:http AND not _asset.protocol:tls) AND ( html.inputs:"password:" OR last.html.inputs:"password:" OR has:http.head.wwwAuthenticate OR has:last.http.head.wwwAuthenticate)',
        },
        {
            "type": "services",
            "search": "_asset.protocol:kerberos and protocol:kerberos and kerberos.errorCode:68 and os:windows",
        },
        {
            "type": "services",
            "search": '_asset.protocol:ldap and protocol:ldap and (has:"ldap.isSynchronized" or has:"ldap.domainControllerFunctionality") and type:server and os:windows',
        },
    ]

    for search in searches:
        if search["type"] == "assets":
            url = BASE_URL + "/export/org/assets.json?"
        else:
            url = BASE_URL + "/export/org/services.json?"
        data = requests.get(url, headers=HEADERS, params={"search": search["search"]})
        print("Result count: " + str(len(data.json())))
        print(data.json())


if __name__ == "__main__":
    main()
