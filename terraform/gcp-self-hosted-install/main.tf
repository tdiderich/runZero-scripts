terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.51.0"
    }
  }
}

variable "self_hosted_download_url" {
  type = string
}

variable "initial_user_email" {
  type = string
}

variable "static_ip" {
  type = string
}

variable "gcp_key_location" {
  type = string
}

variable "ssh_key" {
  type = string
}

provider "google" {
  credentials = file(var.gcp_key_location)

  project = "rz-self-hosted"
  region  = "us-central1"
  zone    = "us-central1-c"
}

resource "google_compute_instance" "rz-self-hosted" {
  boot_disk {
    auto_delete = true
    device_name = "rz-self-hosted"

    initialize_params {
      image = "projects/ubuntu-os-cloud/global/images/ubuntu-1804-bionic-v20230418"
      size  = 100
      type  = "pd-ssd"
    }

    mode = "READ_WRITE"
  }

  can_ip_forward      = false
  deletion_protection = false
  enable_display      = false

  # 10k assets or less
  machine_type = "e2-highmem-4"
  # 10-100k assets
  # machine_type = "e2-highmem-8"
  # 100-250k assets
  # machine_type = "e2-highmem-16"
  

  metadata = {
    ssh-keys = var.ssh_key
  }

  name = "rz-self-hosted"

  network_interface {
    access_config {
      network_tier = "PREMIUM"
      nat_ip = var.static_ip
    }

    subnetwork = "projects/rz-self-hosted/regions/us-west4/subnetworks/default"
  }

  # NOTE: this takes 5-10 minutes so feel free to grab a cup of coffee
  # Once this is done, you can run cat /tmp/password.txt to get your password
  metadata_startup_script = "curl -f -o runzero-platform.bin ${var.self_hosted_download_url} && chmod u+x runzero-platform.bin && sudo ./runzero-platform.bin install && sudo ufw allow https/tcp && rumblectl initial ${var.initial_user_email} && rumblectl user reset ${var.initial_user_email} >> /tmp/password.txt"

  scheduling {
    automatic_restart   = true
    on_host_maintenance = "MIGRATE"
    preemptible         = false
    provisioning_model  = "STANDARD"
  }

  shielded_instance_config {
    enable_integrity_monitoring = true
    enable_secure_boot          = false
    enable_vtpm                 = true
  }

  tags = ["http-server", "https-server"]
  zone = "us-west4-b"
}

