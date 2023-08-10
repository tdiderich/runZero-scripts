# Export API to CSV with specific fields

This is a basic script that runs a search + converts specific fields from asset services to a CSV.

```
$ cd export-to-csv-specific-fields
$ python3 run.py
Successfully printed this object to tls_fields.csv:
[
    {
        "id": "9450da08-e42f-42a7-abdc-b9f14676278e",
        "names": [
            "LIVING-ROOM-SPEAKER",
            "GOOGLE-NEST-MINI.LAN"
        ],
        "addresses": [
            "192.168.86.43"
        ],
        "service_address": "192.168.86.43",
        "service_port": "8009",
        "tls.certificates": "MIIC2jCCAcKgAwIBAgIEEIcbQjANBgkqhkiG9w0BAQsFADAvMS0wKwYDVQQDDCQyNjg4NDEyMS02MTgzLTFiNjMtYTVmMC1hYTRlN2YyOTVhNDMwHhcNMjIwOTA2MjAwMzA2WhcNMjIwOTA4MjAwMzA2WjAvMS0wKwYDVQQDDCQyNjg4NDEyMS02MTgzLTFiNjMtYTVmMC1hYTRlN2YyOTVhNDMwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDa+5OX0zZxZcThAlrl5rnjgQ8/QX+00fed51AeodMQ3wVl8EFJzlpZop/UfbHEpxbteJNZP0aEV8ppDSis43vOc17KgcZWieRVK+oF13VCbMjvgudBgabw2y6Qhcg5sBaDODV2SXjKhBs/5+UYUjisKkJ3S0ycJpFiO3EVpCY0XEwbPFQK9R7aJkSHJGZyvegdIpSa6LAnY44RSudkbzG4XEEQ0LmOLY4fmuM+Qp+m1cCaY35IJ97vGSQwNfkvwT+D6O4gmeHND1T0LBMXO46E+XLUNIcAXYVwOwOUNPIym8ZhUfuNQh4fv8THfhGTfYxIQ9J1KY+5dqJCuO3/szMpAgMBAAEwDQYJKoZIhvcNAQELBQADggEBAI1+SPSOMOz/gsalMR4fVlpov7QsNrqbcOK7IwcePt9Kk4DsmXcgFik+Gfhj173JDL0NByNeGZqkYNxz9GzSmOM6LB0VlJiL5XP3KVTZsUyEMCRl6+ybQb70UX1LPJdvAeVmIMG1Xmsr5TNtisVZdjQw99/QECDsNiyUh5Ol2P9f1+6AAijhwEU/ijCAE06+IDlt+BbVOpfG6O5OW8c0cF5wG5Cw3kWovrM2uhgMge/mqVNjbyoPqIpCQUH3p1OqvmIhd0vpQD30e1av0DYXH42WJDsgG2aBxXscN03ZlyhPLZwp6i5exGSgA1A/NEcsPV4qeMRRsoAJBP1y3mEWQ0A=",
        "tls.cipher": "0x1301",
        "tls.cipherName": "TLS_AES_128_GCM_SHA256",
        "tls.cn": "26884121-6183-1b63-a5f0-aa4e7f295a43",
        "tls.fp.sha1": "d4c5b7a58ea818b1d907eca864be3a0c15d402ca",
        "tls.fp.sha256": "SHA256:9OIvUWoPZ1ITyAgAr/B5RCipFPrub42sF3MT/TlbJoQ=",
        "tls.issuer": "CN=26884121-6183-1b63-a5f0-aa4e7f295a43",
        "tls.names": "26884121-6183-1b63-a5f0-aa4e7f295a43",
        "tls.notAfter": "2022-09-08T20:03:06Z",
        "tls.notAfterTS": "1662667386",
        "tls.notBefore": "2022-09-06T20:03:06Z",
        "tls.notBeforeTS": "1662494586",
        "tls.selfSigned": "serial=10871b42",
        "tls.serial": "10871b42",
        "tls.signatureAlgorithm": "sha256WithRSAEncryption",
        "tls.subject": "CN=26884121-6183-1b63-a5f0-aa4e7f295a43",
        "tls.supportedVersionNames": "TLSv1.0\tTLSv1.1\tTLSv1.2\tTLSv1.3",
        "tls.supportedVersions": "0x0301\t0x0302\t0x0303\t0x0304",
        "tls.version": "0x0304",
        "tls.versionName": "TLSv1.3"
    },
    {
        "id": "73f5785d-f849-40de-9ee0-59c1a7d5315c",
        "names": [
            "MASTER-BEDROOM-SPEAKER",
            "GOOGLE-HOME.LAN"
        ],
        "addresses": [
            "192.168.86.234"
        ],
        "service_address": "192.168.86.234",
        "service_port": "8009",
        "tls.certificates": "MIIC2jCCAcKgAwIBAgIEEIczQzANBgkqhkiG9w0BAQsFADAvMS0wKwYDVQQDDCRjNmEyODY0ZS1kNzNhLTZiMTItZDljMi0yNWI4NDZmYWY0OTAwHhcNMjIwOTA2MjE0NTMxWhcNMjIwOTA4MjE0NTMxWjAvMS0wKwYDVQQDDCRjNmEyODY0ZS1kNzNhLTZiMTItZDljMi0yNWI4NDZmYWY0OTAwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQC4TTrr5Y6Y1uRXy98iQ9mi5FK9JisOlVdsC2RHvl4w3+J+NrrNavjQ9HzoHdRtiurd1bIYb1Nzb8VN2vgANkr5WZ6vyKmKe1uKsSs54gclqdT66YHBNEfghhBLVRV8tFQCRIurNro4ZTazJswUWqmrm9BMY/HmKR3HhkPkL1xHsw2lMGm/23Fs1AjmhV+NWLgWPLGofbnnZx90VdP0GSVxl9SlUzebE8EXg5Ufx/FZKDd2st4y7Oy9yCRtceTMHHs5L+bIXveTzrPeUpI72gEAtPyiVNzChe5jwx5A/hIqmqGDk6jJvaig23sTgGTnw82GP6F647yVVbXrw3yXC9p9AgMBAAEwDQYJKoZIhvcNAQELBQADggEBACPLoz5/oSQZeZ/J9dLQ7k7DfU88h3wnst6vNEBmkpJQ3SHgo2ySNpy66yeTOryrcubkziYxVddFUjSWMxm8p/Wxpc/e1D/eF8Ys13vGAP4pZdFvjoGrniF6niZ0uqeF96c8lOzm6DS7QtnuxyG1uyqoqN+fBDwYgJSe0zRfa4nL+bpSO+ivnDQCQt2s6TSW54cXvWG2pFxJXkXxL3CAdpYgWiXZh0CUw9K9+6DZI/VLOH89zGK8SaQPENsTKYXEpJ40btt2HbEB2nRGoVoSz2jOH6l7pBcHiL1Iabh0fXakkAIBBzpCj6NAjkrCN6mBD+hO5mK89vSY8vfR/dkF6GI=",
        "tls.cipher": "0x1303",
        "tls.cipherName": "TLS_CHACHA20_POLY1305_SHA256",
        "tls.cn": "c6a2864e-d73a-6b12-d9c2-25b846faf490",
        "tls.fp.sha1": "6a47eafa9ef28d13f04f39620ecba078a7400e72",
        "tls.fp.sha256": "SHA256:hhawxCgtlFNYwlW1v/imcVXixG+NXq+UYLw7L/5kkPY=",
        "tls.issuer": "CN=c6a2864e-d73a-6b12-d9c2-25b846faf490",
        "tls.names": "c6a2864e-d73a-6b12-d9c2-25b846faf490",
        "tls.notAfter": "2022-09-08T21:45:31Z",
        "tls.notAfterTS": "1662673531",
        "tls.notBefore": "2022-09-06T21:45:31Z",
        "tls.notBeforeTS": "1662500731",
        "tls.selfSigned": "serial=10873343",
        "tls.serial": "10873343",
        "tls.signatureAlgorithm": "sha256WithRSAEncryption",
        "tls.subject": "CN=c6a2864e-d73a-6b12-d9c2-25b846faf490",
        "tls.supportedVersionNames": "TLSv1.0\tTLSv1.1\tTLSv1.2\tTLSv1.3",
        "tls.supportedVersions": "0x0301\t0x0302\t0x0303\t0x0304",
        "tls.version": "0x0304",
        "tls.versionName": "TLSv1.3"
    },
    {
        "id": "96bd5458-128d-47fb-8766-99de440cd1b3",
        "names": [
            "FINNIE226128153S-SPEAKER"
        ],
        "addresses": [
            "192.168.86.235"
        ],
        "service_address": "192.168.86.235",
        "service_port": "8009",
        "tls.certificates": "MIIC2jCCAcKgAwIBAgIEEIcftjANBgkqhkiG9w0BAQsFADAvMS0wKwYDVQQDDCQzOWJiMmIwMi1iNzJmLTFkNzUtNmZhZS1iYjBlZGU1NjAyNDAwHhcNMjIwOTA2MjAyMjA2WhcNMjIwOTA4MjAyMjA2WjAvMS0wKwYDVQQDDCQzOWJiMmIwMi1iNzJmLTFkNzUtNmZhZS1iYjBlZGU1NjAyNDAwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDqjTlnbNwkqDJncxQ16tcavC0WMssMFPaJCUQ1DE5fXnHvIRFw3oUbb22ILHrEqmQb8yREoUUqpzgevYT4F2/AJvAVlXQxeoEtOdDWkaQpjKNWCfqQ8EknkLKib+WKHxKbZ+OfAxsKT25+wCjc68sAp1PM2tqw3iyoC0ssqyEZlbDZMMiVTnS5iiZOVZhoRAhaUmhydWzScQ+yjU+yRc0QIMRJAJzdh6fE3wPzHEbdhjM0vao/WA/hjjC/lSX6gQMD3TfWDLg2bv0fRDfGlqGT7oummuxRgtNNhvbUQhs9juk7BpT9Hv5xXSg7ZVWpeZT4tIypCUphWrUh7vmLKdRvAgMBAAEwDQYJKoZIhvcNAQELBQADggEBAN18entdh8ddE/ATFxMGY5osBFagHxEKpu+gTnZnge09KULCiVkP2RYvpbOQj4ESvyPwdwDuE5mOEqja5eldAiQQZe1xjfv5oJAl4jusf2o1j4crhmCAXdoOM7MO+PsN5IsUwcNXxwt0edQ/W0aYVIwEyL+L4yXuUFVqhJsisjU/Y0zU61RiHyuGtv4WQso6qtp2e7+s/KbYnNkm+WfMasbIpNXGdY5MMbdrqrGNCjK6STKO9vVYQaDEepCx8u13ExE5aKGcOryZ0/u2pQvqgRh8VG4Cxu5inMeNNW1iMUlbNu0pBASJW+krcHp0MKlbSIuKPhgDS25jha6U9gxaOw0=",
        "tls.cipher": "0x1303",
        "tls.cipherName": "TLS_CHACHA20_POLY1305_SHA256",
        "tls.cn": "39bb2b02-b72f-1d75-6fae-bb0ede560240",
        "tls.fp.sha1": "28b9ae8b6dfa267bf5349b06231de5c6a1aa4ed7",
        "tls.fp.sha256": "SHA256:ik9sFQj2po3c0Rd2QxqOaMzwpcaSScAPV4XF+Tsikkk=",
        "tls.issuer": "CN=39bb2b02-b72f-1d75-6fae-bb0ede560240",
        "tls.names": "39bb2b02-b72f-1d75-6fae-bb0ede560240",
        "tls.notAfter": "2022-09-08T20:22:06Z",
        "tls.notAfterTS": "1662668526",
        "tls.notBefore": "2022-09-06T20:22:06Z",
        "tls.notBeforeTS": "1662495726",
        "tls.selfSigned": "serial=10871fb6",
        "tls.serial": "10871fb6",
        "tls.signatureAlgorithm": "sha256WithRSAEncryption",
        "tls.subject": "CN=39bb2b02-b72f-1d75-6fae-bb0ede560240",
        "tls.supportedVersionNames": "TLSv1.0\tTLSv1.1\tTLSv1.2\tTLSv1.3",
        "tls.supportedVersions": "0x0301\t0x0302\t0x0303\t0x0304",
        "tls.version": "0x0304",
        "tls.versionName": "TLSv1.3"
    },
    {
        "id": "610531e0-5b5e-4fd9-b015-cfa463857c79",
        "names": [
            "FUCHSIA-1CF2-9A44-741B",
            "KITCHEN-DISPLAY"
        ],
        "addresses": [
            "192.168.86.241"
        ],
        "service_address": "192.168.86.241",
        "service_port": "8009",
        "tls.certificates": "MIIC2jCCAcKgAwIBAgIEEIcOeTANBgkqhkiG9w0BAQsFADAvMS0wKwYDVQQDDCQ0ZjVjMzg4MS02MjFlLTJlNGYtNTQ0Yy0zYTFiZWE5N2Y0ZjMwHhcNMjIwOTA2MTkwODMzWhcNMjIwOTA4MTkwODMzWjAvMS0wKwYDVQQDDCQ0ZjVjMzg4MS02MjFlLTJlNGYtNTQ0Yy0zYTFiZWE5N2Y0ZjMwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDsxuq0RwCDA0byaIvdMxm27J7w6dlerHOd2NQmOUjne7J3Q3wLBZE+sWP+WViKR5neVhQpD7M1wP4cLUqLlla1EWtX9PD1+Q/jC1YPiw8rjCv1xlDD5BtNPsAItmOz7SGurNV2KqLu8HMG9ItA0FX+2Ll4n2SqTll1yhWjSygQZwXABedOOY56UHesXZXeeeBwMWynPixwE6q1lIfVE1CYULj7741OrHHJGz74b2kn0hOeJw79N+uPxxO7MqXxAzU2lBMIpcxyYieV03o1vSkNW8jqmZc3CkMAMDA4fTaRBf4EjoSWB0Tvd+x8w6FJPwJxeaOvZMCHtuZ1j9RFi7HtAgMBAAEwDQYJKoZIhvcNAQELBQADggEBANxbzRFXVRWRxNGmrIry1kKYKYGWYWbwCwmMb3sRQUqFvmpMHIIuG/YW6FisOWiaBvrUnYxZZTl1/FT14xC9YBNAKcTAk2mARLm5KzIVeFDyv4SuAnJ6hnBuYAuGasPKuRoMo6GIXl910srcfzzGoq7nc7/YGujoDNJlS3vossWXQZwTqULncbm3It3aHFALvlJoDh9M7B1s7wrW1iPXrSFzRsnBDRNA1Ax2gzDhhMJWwmID41FByH5xCofpohgfebbkFtYL1cbckam6nt1ub5dTeX5D/2kyVPWMprSgpzz2Pow7lE9qZTSDdxKH1tGRtl7/6dlh4+/COwMfXYKHZvU=",
        "tls.cipher": "0x1303",
        "tls.cipherName": "TLS_CHACHA20_POLY1305_SHA256",
        "tls.cn": "4f5c3881-621e-2e4f-544c-3a1bea97f4f3",
        "tls.fp.sha1": "d28d7738f498f6bb1693ec1d0b4291715fc24462",
        "tls.fp.sha256": "SHA256:6nrTWqiEoacTSJwZCVXPxHQp9Gqtwdbe2OcTXid/thU=",
        "tls.issuer": "CN=4f5c3881-621e-2e4f-544c-3a1bea97f4f3",
        "tls.names": "4f5c3881-621e-2e4f-544c-3a1bea97f4f3",
        "tls.notAfter": "2022-09-08T19:08:33Z",
        "tls.notAfterTS": "1662664113",
        "tls.notBefore": "2022-09-06T19:08:33Z",
        "tls.notBeforeTS": "1662491313",
        "tls.selfSigned": "serial=10870e79",
        "tls.serial": "10870e79",
        "tls.signatureAlgorithm": "sha256WithRSAEncryption",
        "tls.subject": "CN=4f5c3881-621e-2e4f-544c-3a1bea97f4f3",
        "tls.supportedVersionNames": "TLSv1.0\tTLSv1.1\tTLSv1.2\tTLSv1.3",
        "tls.supportedVersions": "0x0301\t0x0302\t0x0303\t0x0304",
        "tls.version": "0x0304",
        "tls.versionName": "TLSv1.3"
    },
    {
        "id": "7b795986-6137-4afa-b1dd-95c22498ec5a",
        "names": [
            "MASTER-BEDROOM",
            "ROOT-CA"
        ],
        "addresses": [
            "192.168.86.244"
        ],
        "service_address": "192.168.86.244",
        "service_port": "58515",
        "tls.certificates": "MIIBwjCCASugAwIBAgIBATANBgkqhkiG9w0BAQUFADAnMRMwEQYDVQQKEwpBcHBsZSBJbmMuMRAwDgYDVQQDEwdSb290IENBMB4XDTIyMDgyODIzNDgzNloXDTIzMDgyODIzNDgzNlowJzETMBEGA1UEChMKQXBwbGUgSW5jLjEQMA4GA1UEAxMHUm9vdCBDQTCBnzANBgkqhkiG9w0BAQEFAAOBjQAwgYkCgYEAznqM5GYGhrggDgvY7azwGKG/sduDDT0xPbufybnGiIaY2/gAfWIpo+DYSmSgin95dKMITzvXNHDP+anr+jgfPmuoobK4aFOsQ6jagS99aRLgIi4rIgMdGTYdFGgR8UdiWb07QyUdTXg1PJdRINn73kiDDkPVed76KZdRPiUByt0CAwEAATANBgkqhkiG9w0BAQUFAAOBgQBgNbU63AK2lNJzxZ/ux4VTyYqKvRfa7enzuUmR21JikHgK1FNS65fhz1xARMYrUjMlC0uWmtItL0eRxsEGxYdmOWpPwubb5xlsbo9s4kT6PRqx9HyR1JYv5BhCCiMD4ygwfpt+7MA7E6stYh87a3ZMY479BgpTdgYnnxPv1MZjlA==",
        "tls.cipher": "0x1301",
        "tls.cipherName": "TLS_AES_128_GCM_SHA256",
        "tls.cn": "Root CA",
        "tls.fp.sha1": "8b5ad10657890d1a1c81a34eda832077d90506b3",
        "tls.fp.sha256": "SHA256:/UJN/77SXRjYrCTZxOzyR+3Df8fop2MR4Z7qkqQkKcQ=",
        "tls.issuer": "CN=Root CA,O=Apple Inc.",
        "tls.names": "root ca",
        "tls.notAfter": "2023-08-28T23:48:36Z",
        "tls.notAfterTS": "1693266516",
        "tls.notBefore": "2022-08-28T23:48:36Z",
        "tls.notBeforeTS": "1661730516",
        "tls.selfSigned": "serial=1",
        "tls.serial": "1",
        "tls.signatureAlgorithm": "sha1WithRSAEncryption",
        "tls.subject": "CN=Root CA,O=Apple Inc.",
        "tls.supportedVersionNames": "TLSv1.0\tTLSv1.1\tTLSv1.2\tTLSv1.3",
        "tls.supportedVersions": "0x0301\t0x0302\t0x0303\t0x0304",
        "tls.version": "0x0304",
        "tls.versionName": "TLSv1.3"
    },
    {
        "id": "8b63baa8-0da4-4360-940f-af9003d127de",
        "names": [
            "SAMSUNG",
            "TV-SAMSUNG-7-SERIES-65",
            "SAMSUNG.LAN"
        ],
        "addresses": [
            "192.168.86.250"
        ],
        "service_address": "192.168.86.250",
        "service_port": "52120",
        "dtls.alert": "15feff000000000000000000020246\t15feff000000000000000100020228"
    }
]
```
