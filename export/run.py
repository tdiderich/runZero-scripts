import requests
import os

RUMBLE_EXPORT_TOKEN = os.environ["RUMBLE_EXPORT_TOKEN"]
HEADERS = {"Authorization": f"Bearer {RUMBLE_EXPORT_TOKEN}"}
BASE_URL = "https://console.rumble.run/api/v1.0"


def main():
    searches = [
        "_asset.protocol:ntp",
        "_asset.protocol:ntp" "_asset.protocol:ntp and protocol:ntp and has:ntp.skew",
        "_asset.protocol:tls AND tls.notAfterTS:<now",
        'protocol:="mountd" and nfs.allowed:"%=*"',
        "_asset.protocol:tls AND tls.notAfterTS:<6weeks",
        "_asset.protocol:ntp and protocol:ntp and has:ntp.skew",
        '(_asset.protocol:http AND not _asset.protocol:tls) AND ( html.inputs:"password:" OR last.html.inputs:"password:" OR has:http.head.wwwAuthenticate OR has:last.http.head.wwwAuthenticate)',
        "_asset.protocol:kerberos and protocol:kerberos and kerberos.errorCode:68 and os:windows",
        '_asset.protocol:ldap and protocol:ldap and (has:"ldap.isSynchronized" or has:"ldap.domainControllerFunctionality") and type:server and os:windows',
    ]

    for search in searches:
        url = BASE_URL + "/export/org/assets.json"
        assets = requests.get(url, headers=HEADERS, params={"search": search})
        print(assets.json())


if __name__ == "__main__":
    main()
