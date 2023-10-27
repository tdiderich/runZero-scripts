import requests
import os
import json
import ipaddress

# runZero creds
RUNZERO_BASE_URL = "https://console.runZero.com/api/v1.0"
RUNZERO_EXPORT_TOKEN = os.environ["RUNZERO_EXPORT_TOKEN"]


def send_logs(ip: str, hostname: str = None):
    pan_log = f'Oct 25 11:43:01 http://SumPunFw07.sumotest.com 1,2019/10/09 10:21:11,001234567890002,THREAT,vulnerability,2304,2019/10/09 10:21:11,{ip},240.84.1.144,NAT_{ip},230.230.1.33,Rule 95,,,web-browsing,vsys3,z2-FW-Sumo-Internal,Z4-Outbound-internet,ethernet1/2,ethernet1/2,All traffic,2019/10/09 10:21:11,793911,1,37442,443,37442,20077,0x1402000,tcp,alert,"64.99.23.90/sslmgr?scep-profile-name = %99c",Palo Alto Networks GlobalProtect Remote Code Critical Vulnerability(6),unknown,critical,client-to-server,0123456789,0x2000000000000000,United States,10.0.0.0-10.255.255.255,0,,0,,,1,,,,,,,,0,0,0,0,0,,{hostname},,,,,0,,0,,N/A,code-execution,AppThreat-8189-5641,0x4,0,4294967295,,,6bbbbec9-d123-4d51-1204-6aefd221079b,0'
    pan_endpoint = "https://endpoint4.collection.sumologic.com/receiver/v1/http/ZaVnC4dhaV2LXu7AgO8N3VDNXfzeFS7f17nXicNwyxEin4-77ubfuR7gJh_XlMA2WYtpmGvvj1DIHRbBE5W_PSXhK5BzFcBMae8X3Psu2GZFbKNDXKGC4A=="
    azure_log = {"callerIpAddress": f"{ip}", "time": "22023-10-25T17: 40: 31.937Z", "resourceId": "/tenants/10aec237-ff60-49b2-adc0-e8b7837444ac/providers/Microsoft.aadiam", "operationName": "Update conditional access policy", "operationVersion": "1.0", "category": "AuditLogs", "tenantId": "10aec237-ff60-49b2-adc0-e8b7837444ac", "resultSignature": "None", "durationMs": 0, "correlationId": "346b264f-3d36-4c81-aaff-499fbaf093cf", "Level": 4, "properties": {"id": "IPCGraph_346b264f-3d36-4c81-aaff-499fbaf093cf_BCDHJ_24857857", "category": "Policy", "correlationId": "346b264f-3d36-4c81-aaff-499fbaf093cf", "result": "success", "resultReason": None, "activityDisplayName": "Update conditional access policy", "activityDateTime": "22023-10-13T17: 40: 31.937Z", "loggedByService": "Conditional Access", "operationType": "Update", "userAgent": None, "initiatedBy": {"user": {"id": "53f9c53a-7a22-4f96-a370-244699092ae3", "displayName": None, "userPrincipalName": "admin@sumologicinc.onmicrosoft.com", "ipAddress": None, "roles": []}}, "targetResources": [{"id": "d63bcb96-c7de-4aaf-845d-49f3df67551c", "displayName": "TestWillDelete", "type": "Policy", "modifiedProperties": [{"displayName": "ConditionalAccessPolicy",
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       "oldValue": "{\"id\":\"d63bcb96-c7de-4aaf-845d-49f3df67551c\",\"displayName\":\"TestWillDelete\",\"createdDateTime\":\"2022-12-28T20:10:49.423328+00:00\",\"modifiedDateTime\":\"2022-12-28T20:25:11.8085788+00:00\",\"state\":\"enabled\",\"conditions\":{\"applications\":{\"includeApplications\":[\"None\"],\"excludeApplications\":[],\"includeUserActions\":[],\"includeAuthenticationContextClassReferences\":[],\"applicationFilter\":None},\"users\":{\"includeUsers\":[],\"excludeUsers\":[],\"includeGroups\":[\"b33d90f6-6155-4df1-8c23-1f81a25b7235\"],\"excludeGroups\":[],\"includeRoles\":[],\"excludeRoles\":[]},\"locations\":{\"includeLocations\":[\"All\"],\"excludeLocations\":[]},\"userRiskLevels\":[],\"signInRiskLevels\":[],\"clientAppTypes\":[\"all\"],\"servicePrincipalRiskLevels\":[]},\"grantControls\":{\"operator\":\"OR\",\"builtInControls\":[\"mfa\"],\"customAuthenticationFactors\":[],\"termsOfUse\":[]}}", "newValue": "{\"id\":\"d63bcb96-c7de-4aaf-845d-49f3df67551c\",\"displayName\":\"TestWillDelete\",\"createdDateTime\":\"2022-12-28T20:10:49.423328+00:00\",\"modifiedDateTime\":\"22023-10-13T17:40:31.0298892+00:00\",\"state\":\"disabled\",\"conditions\":{\"applications\":{\"includeApplications\":[\"None\"],\"excludeApplications\":[],\"includeUserActions\":[],\"includeAuthenticationContextClassReferences\":[],\"applicationFilter\":None},\"users\":{\"includeUsers\":[],\"excludeUsers\":[],\"includeGroups\":[\"b33d90f6-6155-4df1-8c23-1f81a25b7235\"],\"excludeGroups\":[],\"includeRoles\":[],\"excludeRoles\":[]},\"locations\":{\"includeLocations\":[\"All\"],\"excludeLocations\":[]},\"userRiskLevels\":[],\"signInRiskLevels\":[],\"clientAppTypes\":[\"all\"],\"servicePrincipalRiskLevels\":[]},\"grantControls\":{\"operator\":\"OR\",\"builtInControls\":[\"mfa\"],\"customAuthenticationFactors\":[],\"termsOfUse\":[]}}"}], "administrativeUnits": []}], "additionalDetails": [{"key": "Category", "value": "Conditional Access"}]}}
    azure_endpoint = "https://endpoint4.collection.sumologic.com/receiver/v1/http/ZaVnC4dhaV2Z6R3udjbPEAhQ-EZgnzhP5_5yn0FARHiZ1I-RaCmMCtcz1d_oh4BzfWluac_liusHjivcTJcf9kBj96vlmFU519eH0yHAzLp49cFJwgSdqg=="
    aws_log = {"eventVersion": "1.05", "userIdentity": {"type": "IAMUser", "principalId": "ABCDEFITPLCYIATJMNC5Q", "arn": "arn:aws:iam::000000000000:user/Carlos", "accountId": "000000000000", "accessKeyId": "111111111111111", "userName": "Carlos", "sessionContext": {"sessionIssuer": {"type": "IAMUser", "principalId": "ABCDEFITPLCYIATJMNC5Q", "arn": "arn:aws:iam::000000000000:user/Carlos", "accountId": "000000000000", "userName": "Carlos"}, "webIdFederationData": {}, "attributes": {"mfaAuthenticated": "true",
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      "creationDate": "2023-10-25T17:40:31Z"}}}, "eventTime": "2020-06-12T16:27:09Z", "eventSource": "iam.amazonaws.com", "eventName": "DeleteUserPermissionsBoundary", "awsRegion": "us-east-1", "sourceIPAddress": f"{ip}", "userAgent": "console.amazonaws.com", "requestParameters": {"userName": "Carlos"}, "responseElements": None, "requestID": "abcdef4e-8f64-4d61-9683-e653682d551e", "eventID": "abcdefd6-4d45-4d76-9646-069a41c6b4ef", "eventType": "AwsApiCall", "recipientAccountId": "123456606896"}
    aws_endpoint = "https://endpoint4.collection.sumologic.com/receiver/v1/http/ZaVnC4dhaV08LU92sNoj6nVwhA7AQcseE8LVM6jz9LMSh9ZNJWJmxjR9I4jtzBDqkg-3DEDenMp-xdUheftpzx8qHa89GXl1jMFDU34ys8T-8jgmTJl57g=="
    requests.post(pan_endpoint, data=pan_log)
    requests.post(azure_endpoint, data=azure_log)
    requests.post(aws_endpoint, data=aws_log)


def get_assets():
    url = RUNZERO_BASE_URL + "/export/org/assets.json"

    everything = requests.get(url, headers={"Authorization": f"Bearer {RUNZERO_EXPORT_TOKEN}"}, params={
        "search": "site:primary", "fields": "addresses,addresses_extra,names"})

    return everything.json()


if __name__ == "__main__":
    assets = get_assets()
    for a in assets:
        ips = a.get("addresses", [])
        ips_extra = a.get("addresses_extra", [])
        ips_final = ips + ips_extra
        hostnames = a.get("names", [])

        for ip in ips_final:
            if ipaddress.ip_address(ip).version == 4 and ipaddress.ip_address(ip).is_private:
                for name in hostnames:
                    send_logs(ip=ip, hostname=name)
