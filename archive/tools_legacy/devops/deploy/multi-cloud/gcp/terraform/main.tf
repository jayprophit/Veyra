# GCP AI/ML & Analytics Platform - Veyra
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  
  backend "gcs" {
    bucket = "veyra-gcp-terraform-state"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  
  default_tags = {
    Application = "Veyra"
    Provider = "GCP"
    Role = "AI-ML-Analytics"
  }
}

# Vertex AI for ML Training and Serving
resource "google_ai_platform_notebook_runtime_template" "ml_training" {
  name = "veyra-ml-template"
  location = var.region
  
  container_image {
    repository = "us-docker.pkg.dev/deeplearning-platform-release/gcr.io/helm-cuda"
    tag = "latest"
  }
  
  machine_type = "n1-standard-4"
  accelerator_type = "NVIDIA_TESLA_T4"
  
  metadata = {
    "proxy-mode" = "ssh"
    "proxy-user" = "jupyter"
  }
  
  tags = {
    Application = "Veyra"
    Provider = "GCP"
    Role = "AI-ML-Analytics"
  }
}

# BigQuery Data Warehouse
resource "google_bigquery_dataset" "financial_data" {
  dataset_id = "financial_master_data"
  location = "US"
  
  description = "Veyra data warehouse for analytics"
  
  tags = {
    Application = "Veyra"
    Provider = "GCP"
    Role = "AI-ML-Analytics"
  }
}

resource "google_bigquery_table" "transactions" {
  dataset_id = google_bigquery_dataset.financial_data.dataset_id
  table_id   = "transactions"
  
  schema = jsonencode([
    {
      "name": "transaction_id",
      "type": "STRING",
      "mode": "REQUIRED"
    },
    {
      "name": "user_id",
      "type": "STRING",
      "mode": "REQUIRED"
    },
    {
      "name": "symbol",
      "type": "STRING",
      "mode": "REQUIRED"
    },
    {
      "name": "quantity",
      "type": "FLOAT",
      "mode": "REQUIRED"
    },
    {
      "name": "price",
      "type": "FLOAT",
      "mode": "REQUIRED"
    },
    {
      "name": "transaction_type",
      "type": "STRING",
      "mode": "REQUIRED"
    },
    {
      "name": "timestamp",
      "type": "TIMESTAMP",
      "mode": "REQUIRED"
    }
  ])
  
  description = "Financial transactions data for analytics"
  time_partitioning = {
    type = "DAY"
    field = "timestamp"
    require_partition_filter = false
  }
  
  tags = {
    Application = "Veyra"
    Provider = "GCP"
    Role = "AI-ML-Analytics"
  }
}

# Vertex AI Model Endpoint
resource "google_ai_platform_endpoint" "model_serving" {
  name = "veyra-model-endpoint"
  location = var.region
  
  deployment {
    deployed_model = google_ai_platform_model.financial_model.id
    automatic_resources = {
      min_replica_count = 1
      max_replica_count = 5
    }
  }
  
  tags = {
    Application = "Veyra"
    Provider = "GCP"
    Role = "AI-ML-Analytics"
  }
}

# Cloud Run for AI Model Serving
resource "google_cloud_run_v2_service" "ai_models" {
  name     = "veyra-ai-models"
  location = var.region
  project  = var.project_id
  
  template {
    containers {
      name  = "veyra-ai"
      image = "gcr.io/${var.project_id}/veyra-ai:latest"
      
      ports {
        container_port = 8080
      }
      
      env {
        name  = "VERTEX_AI_ENDPOINT"
        value = google_ai_platform_endpoint.model_serving.id
      }
      
      env {
        name  = "BIGQUERY_DATASET"
        value = google_bigquery_dataset.financial_data.dataset_id
      }
      
      resources {
        limits = {
          cpu    = "2"
          memory = "4Gi"
        }
        
        cpu_idle = true
      }
    }
    
    scaling {
      min_instances = 1
      max_instances = 10
      
      metric {
        name = "cpu"
        target {
          type           = "UTILIZATION"
          utilization   = 0.6
        }
      }
    }
  }
  
  traffic {
    percent = 100
    type   = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }
  
  tags = {
    Application = "Veyra"
    Provider = "GCP"
    Role = "AI-ML-Analytics"
  }
}

# Cloud Storage for Data Lake
resource "google_storage_bucket" "data_lake" {
  name          = "veyra-data-lake-${random_string.bucket_suffix.result}"
  location      = "US"
  force_destroy = true
  
  uniform_bucket_level_access = true
  
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
  
  tags = {
    Application = "Veyra"
    Provider = "GCP"
    Role = "AI-ML-Analytics"
  }
}

# Dataflow for ETL Pipelines
resource "google_dataflow_job" "etl_pipeline" {
  name = "veyra-etl-pipeline"
  region = var.region
  
  template_gcs_path = "gs://veyra-templates/dataflow-template"
  temp_gcs_location = google_storage_bucket.temp_files.name
  
  environment {
    temp_location = google_storage_bucket.temp_files.name
    zone         = var.zone
  }
  
  tags = {
    Application = "Veyra"
    Provider = "GCP"
    Role = "AI-ML-Analytics"
  }
}

# AutoML for Automated Machine Learning
resource "google_ml_model" "automl_model" {
  name = "veyra-automl"
  region = var.region
  
  dataset {
    dataset_id = google_auto_ml_table_dataset.financial_data.dataset_id
  }
  
  model {
    prediction_type = "classification"
    training_fraction = 0.8
  }
  
  tags = {
    Application = "Veyra"
    Provider = "GCP"
    Role = "AI-ML-Analytics"
  }
}

# Notebooks for Data Science
resource "google_notebooks_instance" "data_science" {
  name = "veyra-data-science"
  location = var.region
  machine_type = "n1-standard-4"
  
  vm_image {
    project      = "deeplearning-platform-release"
    image_family = "common-cpu"
  }
  
  tags = {
    Application = "Veyra"
    Provider = "GCP"
    Role = "AI-ML-Analytics"
  }
}

# Random suffix for unique names
resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}