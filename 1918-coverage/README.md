# RFC1918 Coverage in Sites

This script will read in your runZero Sites and identify gaps in subnet ranges. This allows you to easily see what you are missing in terms of subnets in your Site scope.

A few notes...

1. If you have not ranges in one of the 3 RFC1918 ranges, it returns the entire scope ex. 172.16.0.0/12
2. It uses the _smallest_ subnet mask you have in your Sites to do comparisons, so if you have a /32 in your Site scope, you will get a list of /32 subnets
3. With that being said, it's recommended to consolidate a bit prior to running this to avoid a massive list
4. You can copy the output and add to the `Default scan scope` of a Site to add the outputs

## Sample Output

In this example, the Sites have full 192 and 10 coverage, but there is only a /16 in the 172 range, so I get the rest of the 172 /16 ranges back.

```shell
$ python3 1918-coverage/run.py                                                                                               [9:46:17]
172.17.0.0/16
172.18.0.0/16
172.19.0.0/16
172.20.0.0/16
172.21.0.0/16
172.22.0.0/16
172.23.0.0/16
172.24.0.0/16
172.25.0.0/16
172.26.0.0/16
172.27.0.0/16
172.28.0.0/16
172.29.0.0/16
172.30.0.0/16
172.31.0.0/16
```

In this example, we are missing subnets from all 3 RFC1918 ranges.

```shell
$ python3 1918-coverage/run.py                                                                                               [9:46:36]
10.0.0.0/12
172.18.0.0/16
192.168.16.0/24
192.168.17.0/24
192.168.18.0/24
192.168.19.0/24
192.168.20.0/24
```
