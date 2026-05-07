#!/usr/bin/env python3
"""
Cloud Infrastructure Deployment Script
===================================
Automated deployment to AWS, Azure, and GCP
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

class CloudDeployer:
    """Multi-cloud deployment automation"""
    
    def __init__(self, provider: str = "aws"):
        self.provider = provider.lower()
        self.project_root = Path(__file__).parent
        self.configs = self.load_cloud_configs()
        
    def load_cloud_configs(self) -> Dict:
        """Load cloud provider configurations"""
        return {
            "aws": {
                "name": "Amazon Web Services",
                "cost_range": "$50-500/month",
                "best_for": "Enterprise, Global Scale",
                "services": {
                    "frontend": "CloudFront + S3",
                    "backend": "ECS/Fargate",
                    "database": "RDS PostgreSQL",
                    "cache": "ElastiCache Redis",
                    "api_gateway": "API Gateway",
                    "monitoring": "CloudWatch + X-Ray"
                },
                "deployment_files": [
                    "aws/terraform/main.tf",
                    "aws/terraform/variables.tf",
                    "aws/ecs-task-definition.json",
                    "aws/docker/Dockerfile.prod"
                ]
            },
            "azure": {
                "name": "Microsoft Azure",
                "cost_range": "$40-400/month",
                "best_for": "Microsoft Ecosystem, Enterprise",
                "services": {
                    "frontend": "Front Door + Blob Storage",
                    "backend": "Container Instances",
                    "database": "Azure Database for PostgreSQL",
                    "cache": "Azure Cache for Redis",
                    "api_gateway": "API Management",
                    "monitoring": "Azure Monitor + Application Insights"
                },
                "deployment_files": [
                    "azure/main.bicep",
                    "azure/docker/Dockerfile.prod",
                    "azure/deployment.json"
                ]
            },
            "gcp": {
                "name": "Google Cloud Platform",
                "cost_range": "$45-450/month",
                "best_for": "AI/ML, Data Analytics",
                "services": {
                    "frontend": "Cloud CDN + Cloud Storage",
                    "backend": "Cloud Run",
                    "database": "Cloud SQL for PostgreSQL",
                    "cache": "Memorystore (Redis)",
                    "api_gateway": "Cloud Endpoints",
                    "monitoring": "Cloud Monitoring + Cloud Logging"
                },
                "deployment_files": [
                    "gcp/main.tf",
                    "gcp/cloudbuild.yaml",
                    "gcp/docker/Dockerfile.prod"
                ]
            }
        }
    
    def create_aws_infrastructure(self):
        """Create AWS deployment infrastructure"""
        print("🚀 Creating AWS Infrastructure...")
        
        aws_dir = self.project_root / "aws"
        aws_dir.mkdir(exist_ok=True)
        
        # Create directories
        (aws_dir / "terraform").mkdir(exist_ok=True)
        (aws_dir / "docker").mkdir(exist_ok=True)
        (aws_dir / "scripts").mkdir(exist_ok=True)
        
        # Terraform main configuration
        terraform_main = """
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket = "financial-master-terraform-state"
    key    = "terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
}

# Random suffix for unique resource names
resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

# VPC Configuration
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name        = "financial-master-vpc"
    Environment = var.environment
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  
  tags = {
    Name = "financial-master-igw"
  }
}

# Public Subnets
resource "aws_subnet" "public" {
  count = 2
  
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.${count.index + 1}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true
  
  tags = {
    Name = "financial-master-public-${count.index + 1}"
    Type = "Public"
  }
}

# Private Subnets
resource "aws_subnet" "private" {
  count = 2
  
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  tags = {
    Name = "financial-master-private-${count.index + 1}"
    Type = "Private"
  }
}

# Route Tables
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  
  tags = {
    Name = "financial-master-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  count          = length(aws_subnet.public)
  subnet_id       = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "financial-master"
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
  
  tags = {
    Name = "financial-master-ecs"
  }
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "financial-master-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id
  
  enable_deletion_protection = false
  
  tags = {
    Name = "financial-master-alb"
  }
}

# ALB Target Group
resource "aws_lb_target_group" "main" {
  name     = "financial-master-tg"
  port     = 8000
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id
  
  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 3
  }
  
  tags = {
    Name = "financial-master-tg"
  }
}

# ALB Listener
resource "aws_lb_listener" "main" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"
  
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.main.arn
  }
}

# RDS PostgreSQL
resource "aws_db_subnet_group" "main" {
  name       = "financial-master-db-subnet-group"
  subnet_ids = aws_subnet.private[*].id
  
  tags = {
    Name = "financial-master-db-subnet-group"
  }
}

resource "aws_security_group" "rds" {
  name_prefix = "financial-master-rds-"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "financial-master-rds"
  }
}

resource "aws_db_instance" "main" {
  identifier     = "financial-master-db"
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = var.db_instance_class
  
  allocated_storage     = 100
  max_allocated_storage = 1000
  storage_type          = "gp2"
  storage_encrypted    = true
  
  db_name  = "financial_master"
  username = var.db_username
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = true
  publicly_accessible  = false
  
  tags = {
    Name = "financial-master-db"
  }
}

# ElastiCache Redis Subnet Group
resource "aws_elasticache_subnet_group" "main" {
  name       = "financial-master-cache-subnet"
  subnet_ids = aws_subnet.private[*].id
}

# ElastiCache Security Group
resource "aws_security_group" "redis" {
  name_prefix = "financial-master-redis-"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "financial-master-redis"
  }
}

# ElastiCache Redis Cluster
resource "aws_elasticache_cluster" "main" {
  cluster_id           = "financial-master-cache"
  engine               = "redis"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 2
  parameter_group_name = "default.redis7"
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.main.name
  security_group_ids   = [aws_security_group.redis.id]
  
  tags = {
    Name = "financial-master-cache"
  }
}

# ECS Task Execution Role
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "financial-master-ecs-task-execution-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# ECS Task Role
resource "aws_iam_role" "ecs_task_role" {
  name = "financial-master-ecs-task-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

# Security Groups
resource "aws_security_group" "alb" {
  name_prefix = "financial-master-alb-"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "financial-master-alb"
  }
}

resource "aws_security_group" "ecs_tasks" {
  name_prefix = "financial-master-ecs-tasks-"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "financial-master-ecs-tasks"
  }
}

# S3 Bucket for static assets
resource "aws_s3_bucket" "assets" {
  bucket = "financial-master-assets-${random_string.bucket_suffix.result}"
  
  tags = {
    Name = "financial-master-assets"
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
    Name = "financial-master-cdn"
  }
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}
"""
        
        with open(aws_dir / "terraform" / "main.tf", "w") as f:
            f.write(terraform_main.strip())
        
        # Terraform variables
        terraform_vars = """
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_username" {
  description = "Database username"
  type        = string
  default     = "financial_master"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "app_image" {
  description = "Docker image for the application"
  type        = string
  default     = "financial-master:latest"
}

variable "app_port" {
  description = "Application port"
  type        = number
  default     = 8000
}

variable "min_capacity" {
  description = "Minimum number of tasks"
  type        = number
  default     = 2
}

variable "max_capacity" {
  description = "Maximum number of tasks"
  type        = number
  default     = 10
}
"""
        
        with open(aws_dir / "terraform" / "variables.tf", "w") as f:
            f.write(terraform_vars.strip())
        
        # ECS Task Definition
        task_definition = {
            "family": "financial-master",
            "networkMode": "awsvpc",
            "requiresCompatibilities": ["FARGATE"],
            "cpu": "256",
            "memory": "512",
            "executionRoleArn": "${aws_iam_role.ecs_task_execution_role.arn}",
            "taskRoleArn": "${aws_iam_role.ecs_task_role.arn}",
            "containerDefinitions": [
                {
                    "name": "financial-master-api",
                    "image": "YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/financial-master:latest",
                    "portMappings": [
                        {
                            "containerPort": 8000,
                            "protocol": "tcp"
                        }
                    ],
                    "environment": [
                        {
                            "name": "DATABASE_URL",
                            "value": "postgresql://username:password@db-host:5432/financial_master"
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
                            "valueFrom": "arn:aws:secretsmanager:us-east-1:ACCOUNT:secret:financial-master/secrets"
                        }
                    ],
                    "logConfiguration": {
                        "logDriver": "awslogs",
                        "options": {
                            "awslogs-group": "/ecs/financial-master",
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
        
        with open(aws_dir / "ecs-task-definition.json", "w") as f:
            json.dump(task_definition, f, indent=2)
        
        # Production Dockerfile
        dockerfile = """
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    curl \\
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
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
        
        with open(aws_dir / "docker" / "Dockerfile.prod", "w") as f:
            f.write(dockerfile.strip())
        
        print("✅ AWS infrastructure files created!")
    
    def create_azure_infrastructure(self):
        """Create Azure deployment infrastructure"""
        print("🔵 Creating Azure Infrastructure...")
        
        azure_dir = self.project_root / "azure"
        azure_dir.mkdir(exist_ok=True)
        
        # Bicep main template
        bicep_main = """
@description('Environment name')
param environmentName string = 'financial-master-prod'

@description('Azure region')
param location string = resourceGroup().location

@description('Administrator password for PostgreSQL')
@secure()
param adminPassword string

@description('Docker image for the application')
param appImage string = 'financial-master:latest'

@description('Minimum instances')
param minInstances int = 2

@description('Maximum instances')
param maxInstances int = 10

// Resource Group
resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: environmentName
  location: location
  tags: {
    Environment = 'Production'
    Application = 'Financial Master'
  }
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
  tags: {
    Application = 'Financial Master'
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
  tags: {
    Application = 'Financial Master'
  }
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
  tags: {
    Application = 'Financial Master'
  }
}

// Virtual Network
resource vnet 'Microsoft.Network/virtualNetworks@2021-02-01' = {
  name: '${environmentName}-vnet'
  location: location
  resourceGroup: rg.name
  properties: {
    addressSpace: {
      addressPrefixes: [
        '10.0.0.0/16'
      ]
    }
  }
  tags: {
    Application = 'Financial Master'
  }
}

// Subnet for Container Apps
resource subnet 'Microsoft.Network/virtualNetworks/subnets@2021-02-01' = {
  parent: vnet
  name: 'container-apps-subnet'
  properties: {
    addressPrefix: '10.0.1.0/24'
    delegation: [
      {
        name: 'delegationContainerApp'
        properties: {
          serviceName: 'Microsoft.App/environments'
          actions: [
            'Microsoft.Network/virtualNetworks/subnets/action'
          ]
        }
      }
    ]
  }
  tags: {
    Application = 'Financial Master'
  }
}

// PostgreSQL Database
resource postgres 'Microsoft.DBforPostgreSQL/flexibleServers@2022-12-01' = {
  name: '${environmentName}-postgres'
  location: location
  resourceGroup: rg.name
  properties: {
    version: '15'
    administratorLogin: 'financialmaster'
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
      delegatedSubnetResourceId: subnet.id
    }
  }
  sku: {
    name: 'Standard_D2s_v3'
    tier: 'GeneralPurpose'
  }
  tags: {
    Application = 'Financial Master'
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
  tags: {
    Application = 'Financial Master'
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
          value: 'postgresql://financialmaster:${adminPassword}@${postgres.properties.fullyQualifiedDomainName}:5432/financial_master'
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
          name: 'financial-master-api'
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
        minReplicas: minInstances
        maxReplicas: maxInstances
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
  tags: {
    Application = 'Financial Master'
  }
}

// Storage Account for static assets
resource storage 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: '${environmentName}assets${uniqueString(resourceGroup().id)}'
  location: location
  resourceGroup: rg.name
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    networkAcls: {
      defaultAction: 'Allow'
    }
  }
  tags: {
    Application = 'Financial Master'
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
  tags: {
    Application = 'Financial Master'
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
  tags: {
    Application = 'Financial Master'
  }
}

// Output values
output containerAppUrl = {
  value: ca.properties.configuration.ingress.fqdn
}

output databaseHost = {
  value: postgres.properties.fullyQualifiedDomainName
}

output redisHost = {
  value: redis.properties.hostName
}
"""
        
        with open(azure_dir / "main.bicep", "w") as f:
            f.write(bicep_main.strip())
        
        print("✅ Azure infrastructure files created!")
    
    def create_gcp_infrastructure(self):
        """Create GCP deployment infrastructure"""
        print("🟡 Creating GCP Infrastructure...")
        
        gcp_dir = self.project_root / "gcp"
        gcp_dir.mkdir(exist_ok=True)
        
        # Terraform main configuration
        terraform_main = """
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  
  backend "gcs" {
    bucket = "financial-master-terraform-state"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Random suffix for unique resource names
resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

# VPC Network
resource "google_compute_network" "main" {
  name                    = "financial-master-network"
  auto_create_subnetworks = false
  
  tags = {
    Application = "Financial Master"
  }
}

# Subnets
resource "google_compute_subnetwork" "private" {
  name          = "financial-master-private"
  ip_cidr_range = "10.0.1.0/24"
  region        = var.region
  network       = google_compute_network.main.id
  private_ip_google_access = true
  
  tags = {
    Application = "Financial Master"
  }
}

resource "google_compute_subnetwork" "public" {
  name          = "financial-master-public"
  ip_cidr_range = "10.0.2.0/24"
  region        = var.region
  network       = google_compute_network.main.id
  
  tags = {
    Application = "Financial Master"
  }
}

# Cloud Router for NAT
resource "google_compute_router" "main" {
  name    = "financial-master-router"
  region  = var.region
  network = google_compute_network.main.id
  
  bgp {
    asn = 64512
  }
}

# Cloud NAT
resource "google_compute_router_nat" "main" {
  name    = "financial-master-nat"
  router = google_compute_router.main.name
  region = var.region
  
  nat_ip_allocate_option = "AUTO_ONLY"
  
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
}

# Cloud SQL PostgreSQL
resource "google_sql_database_instance" "main" {
  name             = "financial-master-db"
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
  
  tags = {
    Application = "Financial Master"
  }
}

resource "google_sql_database" "main" {
  name     = "financial_master"
  instance = google_sql_database_instance.main.name
}

resource "google_sql_user" "main" {
  name     = "financialmaster"
  instance = google_sql_database_instance.main.name
  password = var.db_password
}

# Memorystore Redis
resource "google_redis_instance" "main" {
  name           = "financial-master-cache"
  tier           = "STANDARD_HA"
  memory_size_gb = 4
  region         = var.region
  
  authorized_network = google_compute_subnetwork.private.ip_cidr_range
  
  redis_version     = "REDIS_7_0"
  display_name      = "Financial Master Cache"
  
  labels = {
    application = "financial-master"
  }
}

# Cloud Run Service
resource "google_cloud_run_v2_service" "main" {
  name     = "financial-master-api"
  location = var.region
  project  = var.project_id
  
  template {
    containers {
      name  = "financial-master"
      image = "gcr.io/${var.project_id}/financial-master:latest"
      
      ports {
        container_port = 8000
      }
      
      env {
        name  = "DATABASE_URL"
        value = "postgresql://${google_sql_user.main.name}:${var.db_password}@${google_sql_database_instance.main.private_ip_address}:5432/financial_master"
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
      min_instances = var.min_instances
      max_instances = var.max_instances
      
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
  
  labels = {
    application = "financial-master"
  }
}

# Cloud Armor Security Policy
resource "google_compute_security_policy" "main" {
  name        = "financial-master-security"
  description = "Security policy for Financial Master"
  
  rule {
    action      = "allow"
    priority    = 1000
    description = "Default allow rule"
    match {
      config {
        src_ip_ranges = ["0.0.0.0/0"]
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
  
  labels = {
    application = "financial-master"
  }
}

# Backend Config for CDN
resource "google_compute_backend_bucket" "assets" {
  name        = "financial-master-assets-backend"
  bucket_name = google_storage_bucket.assets.name
  enable_cdn  = true
  
  cdn_policy {
    cache_mode = "CACHE_ALL_STATIC"
    default_ttl = 3600
  }
}

# CDN Load Balancer
resource "google_compute_global_forwarding_rule" "main" {
  name       = "financial-master-forwarding-rule"
  target     = google_compute_target_http_proxy.main.id
  port_range = "80"
  
  labels = {
    application = "financial-master"
  }
}

resource "google_compute_target_http_proxy" "main" {
  name    = "financial-master-http-proxy"
  url_map = google_compute_url_map.main.id
  
  labels = {
    application = "financial-master"
  }
}

resource "google_compute_url_map" "main" {
  name = "financial-master-url-map"
  
  default_service = google_compute_backend_service.main.id
  
  host_rules {
    hosts = ["*"]
    path_matcher = google_compute_path_matcher.main.id
  }
  
  labels = {
    application = "financial-master"
  }
}

resource "google_compute_path_matcher" "main" {
  name = "financial-master-path-matcher"
  default_service = google_compute_backend_service.main.id
  
  path_rules {
    paths   = ["/static/*"]
    service = google_compute_backend_bucket.assets.id
  }
  
  labels = {
    application = "financial-master"
  }
}

resource "google_compute_backend_service" "main" {
  name        = "financial-master-backend-service"
  port_name   = "http"
  protocol    = "HTTP"
  timeout_sec = 30
  
  backend {
    group = google_cloud_run_v2_service.main.id
  }
  
  health_checks = [google_compute_health_check.main.id]
  
  security_policy = google_compute_security_policy.main.id
  
  labels = {
    application = "financial-master"
  }
}

resource "google_compute_health_check" "main" {
  name               = "financial-master-health-check"
  check_interval_sec = 30
  timeout_sec        = 10
  healthy_threshold   = 2
  unhealthy_threshold = 3
  
  http_health_check {
    port         = 8000
    request_path = "/health"
  }
  
  labels = {
    application = "financial-master"
  }
}

# Storage Bucket for assets
resource "google_storage_bucket" "assets" {
  name          = "financial-master-assets-${random_string.bucket_suffix.result}"
  location      = "US"
  force_destroy = true
  
  uniform_bucket_level_access = true
  
  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD"]
    response_header = ["Content-Type"]
    max_age_seconds = 3600
  }
  
  labels = {
    application = "financial-master"
  }
}

# Secret Manager
resource "google_secret_manager_secret" "alpha_vantage" {
  secret_id = "alpha-vantage-key"
  replication {
    automatic = true
  }
  
  labels = {
    application = "financial-master"
  }
}

resource "google_secret_manager_secret_version" "alpha_vantage" {
  secret      = google_secret_manager_secret.alpha_vantage.id
  secret_data = var.alpha_vantage_key
  
  labels = {
    application = "financial-master"
  }
}

# Service Account for Cloud Run
resource "google_service_account" "cloud_run" {
  account_id   = "financial-master-cloudrun"
  display_name = "Financial Master Cloud Run Service Account"
}

# IAM permissions
resource "google_cloud_run_service_iam_member" "public" {
  location = google_cloud_run_v2_service.main.location
  project  = google_cloud_run_v2_service.main.project
  service = google_cloud_run_v2_service.main.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_project_iam_member" "cloudsql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

resource "google_project_iam_member" "secret_manager_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}
"""
        
        with open(gcp_dir / "main.tf", "w") as f:
            f.write(terraform_main.strip())
        
        # Terraform variables
        terraform_vars = """
variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "alpha_vantage_key" {
  description = "Alpha Vantage API key"
  type        = string
  sensitive   = true
}

variable "min_instances" {
  description = "Minimum Cloud Run instances"
  type        = number
  default     = 2
}

variable "max_instances" {
  description = "Maximum Cloud Run instances"
  type        = number
  default     = 100
}
"""
        
        with open(gcp_dir / "variables.tf", "w") as f:
            f.write(terraform_vars.strip())
        
        # Cloud Build configuration
        cloudbuild_yaml = """
steps:
  # Build the Docker image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/financial-master:$SHORT_SHA', '.']
  
  # Push the Docker image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/financial-master:$SHORT_SHA']
  
  # Deploy to Cloud Run
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'services'
      - 'update'
      - 'financial-master-api'
      - '--image=gcr.io/$PROJECT_ID/financial-master:$SHORT_SHA'
      - '--region=us-central1'
      - '--allow-unauthenticated'

images:
  - 'gcr.io/$PROJECT_ID/financial-master:$SHORT_SHA'
"""
        
        with open(gcp_dir / "cloudbuild.yaml", "w") as f:
            f.write(cloudbuild_yaml.strip())
        
        print("✅ GCP infrastructure files created!")
    
    def create_migration_scripts(self):
        """Create migration scripts for all providers"""
        print("🔄 Creating migration scripts...")
        
        migration_dir = self.project_root / "migration"
        migration_dir.mkdir(exist_ok=True)
        
        # Migration checklist
        checklist = """
# Cloud Migration Checklist
# =======================

## Phase 1: Preparation (1-2 weeks)
- [ ] Choose cloud provider based on requirements
- [ ] Set up cloud accounts and billing
- [ ] Create infrastructure as code (Terraform/Bicep)
- [ ] Set up CI/CD pipelines
- [ ] Configure monitoring and logging
- [ ] Backup current zero-cost deployment

## Phase 2: Database Migration (1 week)
- [ ] Export data from current database
- [ ] Set up cloud database instance
- [ ] Configure network connectivity
- [ ] Migrate data with minimal downtime
- [ ] Update connection strings
- [ ] Test database performance
- [ ] Verify data integrity

## Phase 3: Application Migration (1-2 weeks)
- [ ] Containerize application
- [ ] Set up container registry
- [ ] Deploy to cloud container service
- [ ] Configure load balancer and CDN
- [ ] Set up auto-scaling policies
- [ ] Test application functionality
- [ ] Configure health checks

## Phase 4: DNS and Traffic Switch (1 day)
- [ ] Update DNS records (TTL reduced)
- [ ] Monitor for issues
- [ ] Rollback plan ready
- [ ] Post-migration optimization
- [ ] Update monitoring dashboards

## Phase 5: Optimization (1-2 weeks)
- [ ] Monitor performance metrics
- [ ] Optimize resource allocation
- [ ] Set up cost alerts
- [ ] Configure backup and disaster recovery
- [ ] Document new architecture
- [ ] Train team on new platform

## Cost Comparison
| Provider | Monthly Cost | Migration Effort | Best For |
|----------|-------------|------------------|----------|
| AWS      | $50-500     | Medium          | Enterprise |
| Azure     | $40-400     | Medium          | Microsoft Stack |
| GCP       | $45-450     | Medium          | AI/ML Focus |

## Rollback Plan
- Keep zero-cost deployment active for 30 days
- DNS can be switched back within minutes
- Database backups stored in multiple locations
- Monitoring alerts for all critical services
- 24/7 support contact information ready

## Success Criteria
- [ ] All services operational in cloud
- [ ] Performance meets or exceeds current
- [ ] Costs within expected range
- [ ] Monitoring and alerting functional
- [ ] Team trained on new platform
- [ ] Documentation complete
"""
        
        with open(migration_dir / "checklist.md", "w") as f:
            f.write(checklist.strip())
        
        print("✅ Migration scripts created!")
    
    def compare_providers(self):
        """Compare cloud providers and provide recommendations"""
        print("\n" + "="*60)
        print("☁️ CLOUD PROVIDER COMPARISON")
        print("="*60)
        
        comparison_data = [
            {
                "Provider": "AWS",
                "Cost Range": "$50-500/month",
                "Best For": "Enterprise, Global Scale",
                "Pros": ["Most mature", "Extensive services", "Excellent docs"],
                "Cons": ["Complex pricing", "Steep learning curve"],
                "Migration": "Medium effort",
                "Recommended": True
            },
            {
                "Provider": "Azure",
                "Cost Range": "$40-400/month", 
                "Best For": "Microsoft Ecosystem",
                "Pros": ["Microsoft integration", "Competitive pricing", "Hybrid support"],
                "Cons": ["Less mature than AWS", "Fewer services"],
                "Migration": "Medium effort",
                "Recommended": True
            },
            {
                "Provider": "GCP",
                "Cost Range": "$45-450/month",
                "Best For": "AI/ML, Data Analytics",
                "Pros": ["Superior AI/ML", "Excellent data tools", "Simple pricing"],
                "Cons": ["Smaller ecosystem", "Fewer regions"],
                "Migration": "Medium effort", 
                "Recommended": True
            }
        ]
        
        print(f"{'Provider':<10} {'Cost':<15} {'Best For':<20} {'Recommended':<12}")
        print("-" * 60)
        
        for provider in comparison_data:
            recommended = "✅ Yes" if provider["Recommended"] else "❌ No"
            print(f"{provider['Provider']:<10} {provider['Cost Range']:<15} {provider['Best For']:<20} {recommended:<12}")
        
        print(f"\n🎯 RECOMMENDATIONS:")
        print(f"   🥇 AWS: Best for enterprise, global scale")
        print(f"   🥈 Azure: Best for Microsoft ecosystem")
        print(f"   🥉 GCP: Best for AI/ML focus")
        
        print(f"\n💰 COST SCALING:")
        print(f"   Startup:     $40-100/month")
        print(f"   Growth:      $120-300/month") 
        print(f"   Enterprise:  $400-2000/month")
        print(f"   Global:      $1500+/month")
        
        print("="*60)
    
    def run_deployment(self):
        """Run the cloud deployment setup"""
        print(f"🚀 Starting {self.provider.upper()} Cloud Deployment Setup...")
        print("="*60)
        
        try:
            if self.provider == "aws":
                self.create_aws_infrastructure()
            elif self.provider == "azure":
                self.create_azure_infrastructure()
            elif self.provider == "gcp":
                self.create_gcp_infrastructure()
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
            
            # Create migration scripts for all providers
            self.create_migration_scripts()
            
            # Show provider comparison
            self.compare_providers()
            
            print(f"\n🎉 SUCCESS! {self.provider.upper()} cloud infrastructure created!")
            print(f"📁 Check these directories:")
            print(f"   - {self.provider}/ (Infrastructure as code)")
            print(f"   - migration/ (Migration scripts)")
            print(f"\n🚀 Next: Follow the migration checklist!")
            
        except Exception as e:
            print(f"❌ Cloud deployment setup failed: {e}")
            raise

def main():
    """Main deployment function"""
    print("☁️ Financial Master - Cloud Infrastructure Deployment")
    print("="*60)
    
    # Get provider choice
    providers = ["aws", "azure", "gcp"]
    print("Available cloud providers:")
    for i, provider in enumerate(providers, 1):
        config = {
            "aws": {"name": "Amazon Web Services", "cost": "$50-500/month"},
            "azure": {"name": "Microsoft Azure", "cost": "$40-400/month"},
            "gcp": {"name": "Google Cloud Platform", "cost": "$45-450/month"}
        }
        print(f"   {i}. {config[provider]['name']} ({config[provider]['cost']})")
    
    # Default to AWS for demo
    choice = "1"  # AWS
    
    try:
        provider_idx = int(choice) - 1
        if 0 <= provider_idx < len(providers):
            provider = providers[provider_idx]
        else:
            provider = "aws"
    except:
        provider = "aws"
    
    deployer = CloudDeployer(provider)
    deployer.run_deployment()

if __name__ == "__main__":
    main()
