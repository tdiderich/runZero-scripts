# Export API

This is a basic script that runs a few searches + prints the results in JSON format. You can update the endpoint to print in a different format and/or update the list of searches.

```
$ python3 export/run.py
Result count: 0
[{'id': '68af77fb-c89b-4190-ba4e-528d4bfb4eaf', 'created_at': 1637609501, 'updated_at': 1637609501, 'organization_id': '183dc8c7-dfc1-4323-9ba9-7027c0b1a2ce', 'site_id': 'b19a58f7-0c91-4c2a-b6dd-05aea73fb772', 'alive': True, 'last_seen': 1583271230, 'first_seen': 1583271140, 'detected_by': 'arp', 'type': 'NAS', 'os_vendor': 'Synology', 'os_product': 'DSM', 'os_version': '', 'os': 'Synology Linux DSM', 'hw_vendor': 'Synology', 'hw_product': 'NAS', 'hw_version': '', 'hw': 'Synology NAS', 'addresses': ['192.168.0.40'], 'addresses_extra': ['10.100.100.40'], 'macs': ['00:11:32:5b:8b:b9'], 'mac_vendors': ['Synology Incorporated'], 'names': ['SURVEILLANCE'], 'tags': {}, 'tag_descriptions': None, 'domains': [], 'services': {'192.168.0.40/0/arp/': {'mac': '00:11:32:5b:8b:b9', 'macDateAdded': '2004-04-25', 'macVendor': 'Synology Incorporated', 'service.address': '192.168.0.40', 'service.id': '68af77fb-c89b-4190-ba4e-528d4bfb4eaf', 'service.port': '0', 'service.transport': 'arp', 'source': 'arp', 'ts': '1583271140'},
...
more asset/service info
...
```
