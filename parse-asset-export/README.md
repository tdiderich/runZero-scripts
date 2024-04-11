# Parse runZero JSONL Export

Steps:

1. Export assets of interest in JSONL format
2. Put in the same directory as the script
3. Update filename to `export.jsonl`
4. Update the `FIELDS_I_WANT` value to the keys you want 

Sample Output:

```
$ python3 run.py 
alive: True
sources: ['runZero']
names: ['77.102.173.34.BC.GOOGLEUSERCONTENT.COM']
addresses: ['34.173.102.77']
service_count: 3
alive: True
sources: ['runZero']
names: ['D034F888CB48F04A4BD7D71FC532D0A534681E6B47CA66349AB5FE7841DFFAD6', '2600-6C44-097F-DA1D-2469-67E8-F5AA-727C.INF6.SPECTRUM.COM', '76CB58A49613C11D6C7586DC661773DA']
addresses: ['192.168.86.26', '2600:6c44:97f:da1d:2469:67e8:f5aa:727c', 'fe80::62b7:6eff:fe6c:cb0d']
service_count: 267
alive: True
sources: ['Nessus', 'Sample', 'runZero']
names: ['1457768-00-G-B7S20126Y00028', 'TESLAWALLCONNECTOR_179ACE.LAN']
addresses: ['192.168.86.41']
service_count: 2
...
MORE ASSET INFO
```

TODO: Add option for second level fields. Current implementation would only capture top level fields. 