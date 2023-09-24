terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.51.0"
    }
  }
}

locals {
  project_id = "css-cedric-2023"
}

variable "vm_name_input" {
  type = string
}


provider "google" {
  credentials = file("credentials.json")

  project = local.project_id
  region  = "europe-central2"
  zone    = "europe-central2-a"
}

resource "google_compute_network" "vpc_network" {
  name                    = "terraform-network"
  auto_create_subnetworks = true
  # delete_default_routes_on_create = true
}

resource "google_compute_instance" "vm_instance" {
  name         = var.vm_name_input
  machine_type = "f1-micro"

  labels = {
    course = "css-gcp"
  }

  tags = ["http-server"]

  # metadata_startup_script = file("./apache2.sh")

  metadata = {
    startup-script = <<-EOF
    #!/bin/bash
    sudo apt-get update && sudo apt -y install apache2
    EOF
  }

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network = google_compute_network.vpc_network.self_link
    access_config {
      # Google Cloud will allocate an external IP automatically
    }
  }
}

resource "google_compute_router" "router" {
  name    = "quickstart-router"
  network = google_compute_network.vpc_network.self_link
}

resource "google_compute_router_nat" "nat" {
  name                               = "quickstart-router-nat"
  router                             = google_compute_router.router.name
  region                             = google_compute_router.router.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
}

resource "google_compute_route" "private_network_internet_route" {
  name             = "private-network-internet"
  dest_range       = "0.0.0.0/0"
  network          = google_compute_network.vpc_network.self_link
  next_hop_gateway = "default-internet-gateway"
  priority    = 100
}

resource "google_compute_firewall" "allow-http" {
  depends_on = [
    google_compute_network.vpc_network,
    google_compute_instance.vm_instance
  ]
  
  name        = "allow-http"
  network     = google_compute_network.vpc_network.name
  description = "Allow HTTP traffic"
  allow {
    protocol = "tcp"
    ports    = ["80"]
  }
  source_ranges = ["0.0.0.0/0"] # Allow traffic from any source (for demonstration purposes)
  target_tags   = ["http-server"]
}

output "vm_name" {
  value = google_compute_instance.vm_instance.name
}

output "public_ip" {
  value = google_compute_instance.vm_instance.network_interface.0.access_config.0.nat_ip
}