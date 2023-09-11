from ipaddress import ip_network, IPv4Network
import requests
import os
import json

RUNZERO_ORG_TOKEN = os.environ["RUNZERO_ORG_TOKEN"]
HEADERS = {"Authorization": f"Bearer {RUNZERO_ORG_TOKEN}"}
BASE_URL = "https://console.runZero.com/api/v1.0"


def get_sites():
    url = BASE_URL + "/org/sites"
    sites = requests.get(url, headers=HEADERS)
    return sites.json()


def get_missing(subnet_networks: list, rfc_range: IPv4Network):
    missing = []
    new_prefix = 8
    has_subnets = False

    for current_subnet in subnet_networks:
        if current_subnet.overlaps(rfc_range):
            has_subnets = True

    if has_subnets:
        for current_subnet in subnet_networks:
            if int(current_subnet.prefixlen) > new_prefix and current_subnet.overlaps(rfc_range):
                new_prefix = current_subnet.prefixlen

        for r in rfc_range.subnets(new_prefix=new_prefix):
            add = True
            if r in subnet_networks:
                add = False

            for current_subnet in subnet_networks:
                if r.subnet_of(current_subnet):
                    add = False

            if add:
                missing.append(r)

    else:
        missing.append(rfc_range)

    final_missing = []
    for sub in missing:
        if sub not in final_missing:
            final_missing.append(sub)

    return final_missing


def create_subnet_diff(subnets: list):

    rfc_ranges = [IPv4Network("10.0.0.0/8"),
                  IPv4Network("172.16.0.0/12"),
                  IPv4Network("192.168.0.0/16")]
    total_missing = []
    subnet_networks = [IPv4Network(x) for x in subnets]

    for range in rfc_ranges:
        missing = get_missing(
            subnet_networks=subnet_networks, rfc_range=range)
        total_missing.extend(missing)

    return total_missing


def main():
    sites = get_sites()
    coverage = []

    for site in sites:
        for subnet in list(site["subnets"].keys()):
            coverage.append(subnet)

    diff = create_subnet_diff(coverage)
    for x in diff:
        print(x)


if __name__ == "__main__":
    main()
