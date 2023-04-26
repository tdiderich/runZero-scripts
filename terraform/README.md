## Terraform
### Terraform setup
1. Install Terraform: https://developer.hashicorp.com/terraform/tutorials/gcp-get-started/install-cli
2. Setup GCP: https://developer.hashicorp.com/terraform/tutorials/gcp-get-started/install-cli
3. Save the `Key` to your computer for reference during `terraform apply`
4. Create your SSH key to SSH into your VM following this guide: https://cloud.google.com/compute/docs/connect/create-ssh-keys#create_an_ssh_key_pair
5. Copy the `.pub` file that is generated and navigate here to add to GCP: https://console.cloud.google.com/compute/metadata?tab=sshkeys

### Deployment
1. Reserve static IP (copy for later use): https://cloud.google.com/compute/docs/ip-addresses/reserve-static-external-ip-address#reserve_new_static
2. Update the `machine_type` value in your Terraform plan as needed: https://www.runzero.com/docs/self-hosting
- 10k assets or less `machine_type = "e2-highmem-4"`
- 10-100k assets `machine_type = "e2-highmem-8"`
- 100-250k assets - `machine_type = "e2-highmem-16"`
- Consult your account team for deployments over 250k assets 
3. Run `terraform apply` to deploy your VM
- `var.gcp_key` - location of the GCP Key created in Terraform setup Step 3
- `var.initial_user_email` - admin email
- `var.self_hosted_download_url` - download URL for your self-hosted instance that can be found here: https://console.runzero.com/deploy/download/platform
- `var.ssh_key` - your public SSH key created in the Terraform setup Step 4
- `var.static_ip` - IP from Step 1
4. SSH into the VM to configure 
5. Install the self-hosted console 
6. Update the `/etc/rumble/config` file to set the correct IP for external access
- `RUMBLE_CONSOLE=https://{IP ADDRESS OR HOSTNAME}:443`
7. Regenerate the TLS certificate 
- `rumblectl generate-certificate && rumblectl restart`
8. You are ready to log in 
- Navigate to `https://{IP ADDRESS OR HOSTNAME}:443` in your browser 
- Your password can be obtained using this command `cat /tmp/password.txt`

## GUI
1. Reserve static IP: https://cloud.google.com/compute/docs/ip-addresses/reserve-static-external-ip-address#reserve_new_static
2. Create VM with specs outlined in the docs: https://www.runzero.com/docs/self-hosting
3. Attach static IP while configuring: https://cloud.google.com/compute/docs/ip-addresses/reserve-static-external-ip-address#assign_new_instance
4. SSH into the VM to configure 
5. Install the self-hosted console 
6. Update the `/etc/rumble/config` file to set the correct IP for external access
- `RUMBLE_CONSOLE=https://{IP ADDRESS OR HOSTNAME}:443`
7. Regenerate the TLS certificate 
- `rumblectl generate-certificate && rumblectl restart`
8. Create your admin users with this command `rumblectl initial <INSERT_YOUR_EMAIL>`
9. You are ready to log in 
- Navigate to `https://{IP ADDRESS OR HOSTNAME}:443` in your browser 
- Use the credentials generated in Step 8
