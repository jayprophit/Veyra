# ☁️ Veyra - Cloud Deployment Guide
## Deploy to AWS, Azure, GCP - Paid Scaling Options

---

## 🎯 **CLOUD DEPLOYMENT OVERVIEW**

```
🏗️ ZERO-COST (Current)     →     🚀 CLOUD INFRASTRUCTURE (Scaling)
┌─────────────────────┐         ┌─────────────────────┐
│ Cloudflare Pages     │  →      │ AWS S3 + CloudFront │
│ Render Backend       │  →      │ AWS ECS/Fargate     │
│ Neon Database        │  →      │ AWS RDS PostgreSQL  │
│ Cloudflare Workers   │  →      │ AWS API Gateway     │
│ Cloudflare R2        │  →      │ AWS S3 + CloudFront │
└─────────────────────┘         └─────────────────────┘
```

---

## 💰 **CLOUD PROVIDER COMPARISON**

| Provider | Monthly Cost | Performance | Scaling | Best For |
|----------|-------------|-------------|----------|----------|
| **AWS** | $50-500+ | Excellent | Auto-scaling | Enterprise, Global |
| **Azure** | $40-400+ | Very Good | Auto-scaling | Enterprise, Microsoft Stack |
| **GCP** | $45-450+ | Excellent | Auto-scaling | AI/ML, Data Analytics |
| **DigitalOcean** | $20-200+ | Good | Manual scaling | Startups, Simplicity |
| **Vultr** | $15-150+ | Good | Manual scaling | Budget-conscious |

---

## 🚀 **AWS DEPLOYMENT CONFIGURATION**

### **📊 AWS Architecture**
```
┌─────────────────────────────────────┐
│  AWS CloudFront (CDN)                │ $20-50/month
│  Global edge locations                │
└─────────────────────────────────────┘
                  │
┌─────────────────────────────────────┐
│  AWS API Gateway                     │ $3.50/million requests
│  Rate limiting, auth, caching        │
└─────────────────────────────────────┘
                  │
┌─────────────────────────────────────┐
│  AWS ECS/Fargate (Containers)        │ $50-200/month
│  Auto-scaling, load balancing       │
└─────────────────────────────────────┘
                  │
┌─────────────────────────────────────┐
│  AWS RDS PostgreSQL                  │ $25-100/month
│  Multi-AZ, backups, scaling         │
└─────────────────────────────────────┘
                  │
┌─────────────────────────────────────┐
│  AWS ElastiCache (Redis)             │ $15-50/month
│  Caching, session management        │
└─────────────────────────────────────┘
```

### **🛠️ AWS Deployment Files**

#### **`aws/terraform/main.tf`**
```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket = "veyra-terraform-state"
    key    = "terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC Configuration
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name = "veyra-vpc"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "veyra"
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "veyra-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id
  
  tags = {
    Name = "veyra-alb"
  }
}

# RDS PostgreSQL
resource "aws_db_instance" "main" {
  identifier     = "veyra-db"
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = var.db_instance_class
  
  allocated_storage     = 100
  max_allocated_storage = 1000
  storage_type          = "gp2"
  storage_encrypted    = true
  
  db_name  = "veyra"
  username = var.db_username
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = true
  
  tags = {
    Name = "veyra-db"
  }
}

# ElastiCache Redis
resource "aws_elasticache_subnet_group" "main" {
  name       = "veyra-cache-subnet"
  subnet_ids = aws_subnet.private[*].id
}

resource "aws_elasticache_cluster" "main" {
  cluster_id           = "veyra-cache"
  engine               = "redis"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 2
  parameter_group_name = "default.redis7"
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.main.name
  security_group_ids   = [aws_security_group.redis.id]
  
  tags = {
    Name = "veyra-cache"
  }
}

# S3 Bucket for static assets
resource "aws_s3_bucket" "assets" {
  bucket = "veyra-assets-${random_string.bucket_suffix.result}"
  
  tags = {
    Name = "veyra-assets"
  }
}

resource "aws_s3_bucket_versioning" "assets" {
  bucket = aws_s3_bucket.assets.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "assets" {
  bucket = aws_s3_bucket.assets.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# CloudFront Distribution
resource "aws_cloudfront_distribution" "main" {
  origin {
    domain_name = aws_lb.main.dns_name
    origin_id   = "alb-origin"
    
    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }
  
  origin {
    domain_name = aws_s3_bucket.assets.bucket_regional_domain_name
    origin_id   = "s3-origin"
  }
  
  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"
  
  default_cache_behavior {
    allowed_methods        = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "alb-origin"
    compress               = true
    viewer_protocol_policy = "redirect-to-https"
    
    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
  }
  
  ordered_cache_behavior {
    path_pattern           = "/static/*"
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "s3-origin"
    compress               = true
    viewer_protocol_policy = "redirect-to-https"
    
    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
  }
  
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
  
  viewer_certificate {
    cloudfront_default_certificate = true
  }
  
  tags = {
    Name = "veyra-cdn"
  }
}
```

#### **`aws/terraform/variables.tf`**
```hcl
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_username" {
  description = "Database username"
  type        = string
  default     = "veyra"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "app_image" {
  description = "Docker image for the application"
  type        = string
  default     = "veyra:latest"
}

variable "app_port" {
  description = "Application port"
  type        = number
  default     = 8000
}
```

#### **`aws/ecs-task-definition.json`**
```json
{
  "family": "veyra",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "veyra-api",
      "image": "YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/veyra:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://username:password@db-host:5432/veyra"
        },
        {
          "name": "REDIS_URL",
          "value": "redis://cache-host:6379"
        },
        {
          "name": "OLLAMA_BASE_URL",
          "value": "http://ollama-service:11434"
        }
      ],
      "secrets": [
        {
          "name": "ALPHA_VANTAGE_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:ACCOUNT:secret:veyra/secrets"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/veyra",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
```

#### **`aws/docker/Dockerfile.prod`**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🔵 **AZURE DEPLOYMENT CONFIGURATION**

### **📊 Azure Architecture**
```
┌─────────────────────────────────────┐
│  Azure Front Door (CDN)             │ $40-80/month
│  Global edge locations                │
└─────────────────────────────────────┘
                  │
┌─────────────────────────────────────┐
│  Azure API Management                │ $25-100/month
│  Rate limiting, auth, caching        │
└─────────────────────────────────────┘
                  │
┌─────────────────────────────────────┐
│  Azure Container Instances          │ $30-150/month
│  Auto-scaling, load balancing       │
└─────────────────────────────────────┘
                  │
┌─────────────────────────────────────┐
│  Azure Database for PostgreSQL       │ $20-80/month
│  Multi-region, backups, scaling     │
└─────────────────────────────────────┘
                  │
┌─────────────────────────────────────┐
│  Azure Cache for Redis               │ $15-50/month
│  Caching, session management        │
└─────────────────────────────────────┘
```

### **🛠️ Azure Deployment Files**

#### **`azure/main.bicep`**
```bicep
@description('Environment name')
param environmentName string = 'veyra-prod'

@description('Azure region')
param location string = resourceGroup().location

@description('Administrator password for PostgreSQL')
@secure()
param adminPassword string

@description('Docker image for the application')
param appImage string = 'veyra:latest'

// Resource Group
resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: environmentName
  location: location
}

// Container Registry
resource acr 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' = {
  name: '${environmentName}acr'
  location: location
  resourceGroup: rg.name
  sku: {
    name: 'Basic'
  }
  adminUserEnabled: true
}

// Container App Environment
resource cae 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: '${environmentName}-env'
  location: location
  resourceGroup: rg.name
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: la.properties.customerId
        sharedKey: la.listKeys().keys[0].value
      }
    }
  }
}

// Log Analytics Workspace
resource la 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: '${environmentName}-logs'
  location: location
  resourceGroup: rg.name
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// PostgreSQL Database
resource postgres 'Microsoft.DBforPostgreSQL/flexibleServers@2022-12-01' = {
  name: '${environmentName}-postgres'
  location: location
  resourceGroup: rg.name
  properties: {
    version: '15'
    administratorLogin: 'veyra'
    administratorLoginPassword: adminPassword
    storage: {
      storageSizeGB: 128
    }
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: 'Enabled'
    }
    highAvailability: {
      mode: 'ZoneRedundant'
    }
    network: {
      delegatedSubnetResourceId: postgresSubnet.id
    }
  }
  sku: {
    name: 'Standard_D2s_v3'
    tier: 'GeneralPurpose'
  }
}

// Redis Cache
resource redis 'Microsoft.Cache/redis@2022-06-01' = {
  name: '${environmentName}-redis'
  location: location
  resourceGroup: rg.name
  properties: {
    sku: {
      name: 'Basic'
      family: 'C'
      capacity: 1
    }
    enableNonSslPort: false
    minimumTlsVersion: '1.2'
  }
}

// Container App
resource ca 'Microsoft.App/containerApps@2023-05-01' = {
  name: '${environmentName}-api'
  location: location
  resourceGroup: rg.name
  properties: {
    managedEnvironmentId: cae.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        transport: 'http'
        allowInsecure: false
      }
      secrets: [
        {
          name: 'database-password'
          value: adminPassword
        }
        {
          name: 'alpha-vantage-key'
          value: ''
        }
      ]
      env: [
        {
          name: 'DATABASE_URL'
          value: 'postgresql://veyra:${adminPassword}@${postgres.properties.fullyQualifiedDomainName}:5432/veyra'
        }
        {
          name: 'REDIS_URL'
          value: 'redis://${redis.properties.hostName}:6379'
        }
        {
          name: 'OLLAMA_BASE_URL'
          value: 'http://ollama-service:11434'
        }
        {
          name: 'ALPHA_VANTAGE_KEY'
          secretRef: 'alpha-vantage-key'
        }
      ]
    }
    template: {
      containers: [
        {
          image: appImage
          name: 'veyra-api'
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          probe: {
            httpGet: {
              path: '/health'
              port: 8000
            }
            type: 'Liveness'
            initialDelaySeconds: 10
            periodSeconds: 30
          }
        }
      ]
      scale: {
        minReplicas: 2
        maxReplicas: 10
        rules: [
          {
            name: 'cpu-scale'
            custom: {
              type: 'http'
              metadata: {
                concurrentRequests: '100'
              }
            }
          }
        ]
      }
    }
  }
}

// Front Door Profile
resource fd 'Microsoft.Cdn/profiles@2021-06-01' = {
  name: '${environmentName}-fd'
  location: 'global'
  resourceGroup: rg.name
  sku: {
    name: 'Standard_AzureFrontDoor'
  }
}

// Front Door Endpoint
resource fde 'Microsoft.Cdn/profiles/afdEndpoints@2021-06-01' = {
  name: '${environmentName}-endpoint'
  parent: fd
  location: 'global'
  properties: {
    enabledState: 'Enabled'
  }
}

// Front Door Origin Group
resource fdog 'Microsoft.Cdn/profiles/originGroups@2021-06-01' = {
  name: '${environmentName}-og'
  parent: fd
  properties: {
    loadBalancingSettings: {
      sampleSize: 4
      successfulSamplesRequired: 3
      additionalLatencyInMilliseconds: 50
    }
    healthProbeSettings: {
      probePath: '/health'
      probeProtocol: 'Http'
      probeMethod: 'GET'
      intervalInSeconds: 30
    }
    origins: [
      {
        name: 'container-app-origin'
        hostName: ca.properties.configuration.ingress.fqdn
        httpPort: 443
        httpsPort: 443
        originHostHeader: ca.properties.configuration.ingress.fqdn
        priority: 1
        weight: 100
        enabled: true
      }
    ]
  }
}

// Front Door Route
resource fdr 'Microsoft.Cdn/profiles/afdEndpoints/routes@2021-06-01' = {
  name: '${environmentName}-route'
  parent: fde
  properties: {
    originGroupId: fdog.id
    supportedProtocols: [
      'Http'
      'Https'
    ]
    patternsToMatch: [
      '/*'
    ]
    forwardingProtocol: 'HttpsOnly'
    linkToDefaultDomain: true
    httpsRedirect: 'Enabled'
  }
}
```

---

## 🟡 **GCP DEPLOYMENT CONFIGURATION**

### **📊 GCP Architecture**
```
┌─────────────────────────────────────┐
│  Google Cloud CDN                    │ $45-85/month
│  Global edge locations                │
└─────────────────────────────────────┘
                  │
┌─────────────────────────────────────┐
│  Cloud Endpoints / API Gateway       │ $35-120/month
│  Rate limiting, auth, caching        │
└─────────────────────────────────────┘
                  │
┌─────────────────────────────────────┐
│  Google Cloud Run                   │ $40-180/month
│  Auto-scaling, load balancing       │
└─────────────────────────────────────┘
                  │
┌─────────────────────────────────────┐
│  Cloud SQL for PostgreSQL            │ $25-90/month
│  Multi-region, backups, scaling     │
└─────────────────────────────────────┘
                  │
┌─────────────────────────────────────┐
│  Memorystore (Redis)                 │ $20-60/month
│  Caching, session management        │
└─────────────────────────────────────┘
```

### **🛠️ GCP Deployment Files**

#### **`gcp/main.tf`**
```hcl
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  
  backend "gcs" {
    bucket = "veyra-terraform-state"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# VPC Network
resource "google_compute_network" "main" {
  name                    = "veyra-network"
  auto_create_subnetworks = false
}

# Subnets
resource "google_compute_subnetwork" "private" {
  name          = "veyra-private"
  ip_cidr_range = "10.0.1.0/24"
  region        = var.region
  network       = google_compute_network.main.id
  private_ip_google_access = true
}

resource "google_compute_subnetwork" "public" {
  name          = "veyra-public"
  ip_cidr_range = "10.0.2.0/24"
  region        = var.region
  network       = google_compute_network.main.id
}

# Cloud SQL PostgreSQL
resource "google_sql_database_instance" "main" {
  name             = "veyra-db"
  database_version = "POSTGRES_15"
  region           = var.region
  
  settings {
    tier = "db-n1-standard-1"
    
    ip_configuration {
      ipv4_enabled = false
      private_network = {
        network_id = google_compute_network.main.id
      }
    }
    
    backup_configuration {
      enabled            = true
      binary_log_enabled = true
      location           = "us-central1"
    }
    
    maintenance_window {
      day  = 7
      hour = 2
    }
  }
  
  deletion_protection = false
}

resource "google_sql_database" "main" {
  name     = "veyra"
  instance = google_sql_database_instance.main.name
}

# Memorystore Redis
resource "google_redis_instance" "main" {
  name           = "veyra-cache"
  tier           = "STANDARD_HA"
  memory_size_gb = 4
  region         = var.region
  
  authorized_network = google_compute_subnetwork.private.ip_cidr_range
  
  redis_version     = "REDIS_7_0"
  display_name      = "Veyra Cache"
}

# Cloud Run Service
resource "google_cloud_run_v2_service" "main" {
  name     = "veyra-api"
  location = var.region
  project  = var.project_id
  
  template {
    containers {
      name  = "veyra"
      image = "gcr.io/${var.project_id}/veyra:latest"
      
      ports {
        container_port = 8000
      }
      
      env {
        name  = "DATABASE_URL"
        value = "postgresql://${google_sql_user.main.name}:${random_password.db_password.result}@${google_sql_database_instance.main.private_ip_address}:5432/veyra"
      }
      
      env {
        name  = "REDIS_URL"
        value = "redis://${google_redis_instance.main.host}:${google_redis_instance.main.port}"
      }
      
      env {
        name  = "OLLAMA_BASE_URL"
        value = "http://ollama-service:11434"
      }
      
      env {
        name  = "ALPHA_VANTAGE_KEY"
        value = google_secret_manager_secret_version.alpha_vantage.secret_data
      }
      
      resources {
        limits = {
          cpu    = "1"
          memory = "2Gi"
        }
        
        cpu_idle = true
      }
      
      startup_probe {
        initial_delay_seconds = 10
        timeout_seconds        = 5
        period_seconds         = 10
        failure_threshold      = 3
        
        http_get {
          path = "/health"
          port = 8000
        }
      }
      
      liveness_probe {
        timeout_seconds   = 5
        period_seconds    = 10
        failure_threshold = 3
        
        http_get {
          path = "/health"
          port = 8000
        }
      }
    }
    
    scaling {
      min_instances = 2
      max_instances = 100
      
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
  
  ingress {
    all        = true
    default    = true
    ports {
      name = "http"
      port = 8000
    }
  }
}

# Cloud Armor Security Policy
resource "google_compute_security_policy" "main" {
  name        = "veyra-security"
  description = "Security policy for Veyra"
  
  rule {
    action      = "allow"
        priority    = 1000
        description = "Default allow rule"
        match {
          versioned_expr {
            expr_options {
              recaptcha_options {
                site_key = google_recaptcha_key.main.site_key
              }
            }
          }
        }
  }
  
  rule {
    action      = "deny(403)"
    priority    = 2147483647
    description = "Default deny rule"
    match {
      config {
        src_ip_ranges = ["*"]
      }
    }
  }
}

# Backend Config for CDN
resource "google_compute_backend_bucket" "assets" {
  name        = "veyra-assets-backend"
  bucket_name = google_storage_bucket.assets.name
  enable_cdn  = true
}

# CDN Load Balancer
resource "google_compute_global_forwarding_rule" "main" {
  name       = "veyra-forwarding-rule"
  target     = google_compute_target_http_proxy.main.id
  port_range = "80"
}

resource "google_compute_target_http_proxy" "main" {
  name    = "veyra-http-proxy"
  url_map = google_compute_url_map.main.id
}

resource "google_compute_url_map" "main" {
  name = "veyra-url-map"
  
  default_service = google_compute_backend_service.main.id
  
  host_rules {
    hosts = ["*"]
    path_matcher = google_compute_path_matcher.main.id
  }
}

resource "google_compute_path_matcher" "main" {
  name = "veyra-path-matcher"
  default_service = google_compute_backend_service.main.id
  
  path_rules {
    paths   = ["/static/*"]
    service = google_compute_backend_bucket.assets.id
  }
}

resource "google_compute_backend_service" "main" {
  name        = "veyra-backend-service"
  port_name   = "http"
  protocol    = "HTTP"
  timeout_sec = 30
  
  backend {
    group = google_cloud_run_v2_service.main.id
  }
  
  health_checks = [google_compute_health_check.main.id]
  
  security_policy = google_compute_security_policy.main.id
}

resource "google_compute_health_check" "main" {
  name               = "veyra-health-check"
  check_interval_sec = 30
  timeout_sec        = 10
  healthy_threshold   = 2
  unhealthy_threshold = 3
  
  http_health_check {
    port         = 8000
    request_path = "/health"
  }
}

# Storage Bucket for assets
resource "google_storage_bucket" "assets" {
  name          = "veyra-assets-${random_string.bucket_suffix.result}"
  location      = "US"
  force_destroy = true
  
  uniform_bucket_level_access = true
  
  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD"]
    response_header = ["Content-Type"]
    max_age_seconds = 3600
  }
}

# Secret Manager
resource "google_secret_manager_secret" "alpha_vantage" {
  secret_id = "alpha-vantage-key"
  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "alpha_vantage" {
  secret      = google_secret_manager_secret.alpha_vantage.id
  secret_data = var.alpha_vantage_key
}

# reCAPTCHA for Cloud Armor
resource "google_recaptcha_key" "main" {
  display_name = "Veyra reCAPTCHA"
  project      = var.project_id
}
```

---

## 💰 **COST COMPARISON & SCALING**

### **📊 Monthly Cost Estimates**

| Scale Level | AWS | Azure | GCP | Best For |
|-------------|------|-------|-----|----------|
| **Startup** | $50-100 | $40-80 | $45-85 | Small user base |
| **Growth** | $150-300 | $120-250 | $135-275 | Medium business |
| **Enterprise** | $500-2000 | $400-1500 | $450-1800 | Large scale |
| **Global** | $2000+ | $1500+ | $1800+ | Worldwide users |

### **🚀 Scaling Triggers**

| Metric | Current Limit | Cloud Upgrade | Cost Impact |
|--------|---------------|----------------|-------------|
| **Users** | 100 concurrent | 1000+ | +$50-100/month |
| **API Calls** | 100k/day | 1M+/day | +$30-80/month |
| **Storage** | 10GB | 100GB+ | +$20-50/month |
| **Database** | 500MB | 10GB+ | +$40-120/month |

---

## 🔄 **MIGRATION PATH**

### **📋 Migration Checklist**

#### **Phase 1: Preparation (1-2 weeks)**
- [ ] Choose cloud provider based on requirements
- [ ] Set up cloud accounts and billing
- [ ] Create infrastructure as code (Terraform/Bicep)
- [ ] Set up CI/CD pipelines
- [ ] Configure monitoring and logging

#### **Phase 2: Database Migration (1 week)**
- [ ] Export data from Neon
- [ ] Set up cloud database
- [ ] Migrate data with minimal downtime
- [ ] Update connection strings
- [ ] Test database performance

#### **Phase 3: Application Migration (1-2 weeks)**
- [ ] Containerize application
- [ ] Set up container registry
- [ ] Deploy to cloud container service
- [ ] Configure load balancer and CDN
- [ ] Test application functionality

#### **Phase 4: DNS and Traffic Switch (1 day)**
- [ ] Update DNS records
- [ ] Monitor for issues
- [ ] Rollback plan ready
- [ ] Post-migration optimization

#### **Phase 5: Optimization (1-2 weeks)**
- [ ] Monitor performance metrics
- [ ] Optimize resource allocation
- [ ] Set up auto-scaling policies
- [ ] Configure backup and disaster recovery

---

## 🎯 **RECOMMENDATIONS**

### **🏆 Best Cloud Provider for Veyra:**

#### **🥇 AWS (Recommended for Enterprise)**
- **Pros:** Most mature, extensive services, excellent documentation
- **Best for:** Global deployment, enterprise features, compliance
- **Cost:** $50-500/month depending on scale

#### **🥈 Azure (Recommended for Microsoft Stack)**
- **Pros:** Excellent integration with Microsoft services, competitive pricing
- **Best for:** Enterprise with Microsoft ecosystem, hybrid deployments
- **Cost:** $40-400/month depending on scale

#### **🥉 GCP (Recommended for AI/ML Focus)**
- **Pros:** Superior AI/ML services, excellent data analytics
- **Best for:** AI-heavy applications, data analytics, innovation
- **Cost:** $45-450/month depending on scale

---

## 🚀 **IMMEDIATE NEXT STEPS**

### **1. Choose Your Cloud Provider**
- **AWS:** Best for enterprise, global scale
- **Azure:** Best for Microsoft ecosystem
- **GCP:** Best for AI/ML focus

### **2. Start with Small Scale**
- Begin with minimum resources
- Monitor performance and costs
- Scale up as needed

### **3. Use Infrastructure as Code**
- All configurations provided
- Version control your infrastructure
- Automated deployments

### **4. Monitor and Optimize**
- Set up comprehensive monitoring
- Regular cost reviews
- Performance optimization

---

**🎉 Your Veyra is now ready for cloud deployment with multiple provider options!**

*Choose your preferred cloud provider and follow the specific deployment guide for that platform.*
