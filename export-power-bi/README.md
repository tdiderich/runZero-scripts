# Export to Power BI

This script can be used to send data to Power BI. You will need to configure Power BI to expect this data prior to running it.

## Setting up Power BI

In order to start streaming runZero data to Power BI, you first need to create the streaming datasets in Power BI. Follow these steps to setup Power BI to receive the data.

### Assets

1. Go to the [create](https://app.powerbi.com/groups/me/create) page
2. Select `Streaming dataset`
3. Select `API` and click `Next`
4. Set the first dataset name to `runzero-assets`
5. Add these fields for the schema values with type `Text` for each

```text
alive,criticality,hw,hw_product,hw_vendor,hw_version,id,os,os_product,os_vendor,os_version,risk
```

6. Add these fields for the schema values with type `Number` for each

```text
service_count,service_count_arp,service_count_icmp,service_count_tcp,service_count_udp,software_count,vulnerability_count
```

7. Enable `Historical data analysis`
8. Click `Create` and save the `Push URL` provided to use as the `assets_power_bi_endpoint` in the script

### Services

1. Go to the [create](https://app.powerbi.com/groups/me/create) page
2. Select `Streaming dataset`
3. Select `API` and click `Next`
4. Set the first dataset name to `runzero-services`
5. Add these fields for the schema values with type `Text` for each

```text
alive,service_id,service_asset_id,service_organization_id,service_address,service_transport,service_vhost,service_summary,id,organization_id,site_id,detected_by,type
```

6. Add these fields for the schema values with type `Number` for each

```text
service_port
```

7. Enable `Historical data analysis`
8. Click `Create` and save the `Push URL` provided to use as the `services_power_bi_endpoint` in the script

## Running the script

1. Update your `RUNZERO_EXPORT_TOKEN` value to allow for you to export data from runZero
2. Update the `assets_power_bi_endpoint` and `services_power_bi_endpoint` values obtained during the Power BI configuration
3. Run the script

_NOTE_: You can update the fields to include more if you need more of the data, but you will need to update those in Power BI first. Power BI only supports Text, Number, and DateTime types for fields.

## Demo in Power BI

<div style="position: relative; padding-bottom: calc(66.66666666666666% + 41px); height: 0; width: 100%"><iframe src="https://demo.arcade.software/4x6aKDfCpf0bZrJhm6MR?embed" frameborder="0" loading="lazy" webkitallowfullscreen mozallowfullscreen allowfullscreen style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;color-scheme: light;" title="runZero Export to Power BI"></iframe></div>
