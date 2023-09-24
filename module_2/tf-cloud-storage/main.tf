terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.51.0"
    }
  }
}

provider "google" {
  credentials = file("credentials.json")

  project = "css-cedric-2023"
  region  = "europe-north1"
  zone    = "europe-north1-a"
}

variable "bucket_name" {
  type = string
}

variable "folder_name" {
  type = string
}

resource "google_storage_bucket" "static" {
  name          = var.bucket_name
  location      = "EU"
  force_destroy = true

  uniform_bucket_level_access = true
}

resource "google_storage_bucket_object" "folder" {
  name    = "${var.folder_name}/"
  bucket  = google_storage_bucket.static.name
  content = " "
}