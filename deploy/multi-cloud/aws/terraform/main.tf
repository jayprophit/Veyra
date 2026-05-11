# AWS Enterprise Foundation - Veyra
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  
  backend "s3" {
    bucket = "veyra-aws-terraform-state"
    key    = "aws-infrastructure.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    Environment = "production"
    Application = "Veyra"
    Provider = "AWS"
    Role = "Enterprise-Foundation"
  }
}

# Enterprise VPC with Multiple AZs
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name        = "veyra-enterprise-vpc"
    Environment = "production"
    Application = "Veyra"
    Provider = "AWS"
  }
}

# Multiple Availability Zones for High Availability
data "aws_availability_zones" "available" {
  state = "available"
  filter {
    name   = "opt-in-status"
    values = ["opt-in-not-required"]
  }
}

# Public Subnets across multiple AZs
resource "aws_subnet" "public" {
  count = length(data.aws_availability_zones.available.names)
  
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.${count.index + 1}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true
  
  tags = {
    Name = "veyra-public-${count.index + 1}"
    Type = "Public"
    AZ = data.aws_availability_zones.available.names[count.index]
  }
}

# Private Subnets across multiple AZs
resource "aws_subnet" "private" {
  count = length(data.aws_availability_zones.available.names)
  
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  tags = {
    Name = "veyra-private-${count.index + 1}"
    Type = "Private"
    AZ = data.aws_availability_zones.available.names[count.index]
  }
}

# Enterprise ECS Cluster with Fargate
resource "aws_ecs_cluster" "enterprise" {
  name = "veyra-enterprise"
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
  
  configuration {
    execute_command_configuration {
      logging = "OVERRIDE"
    }
  }
  
  tags = {
    Name = "veyra-enterprise-ecs"
    Role = "Enterprise-Foundation"
  }
}

# Application Load Balancer with Cross-Zone
resource "aws_lb" "enterprise" {
  name               = "veyra-enterprise-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id
  
  enable_deletion_protection = false
  
  access_logs {
    bucket  = aws_s3_bucket.alb_logs.id
    prefix  = "alb-logs"
    enabled  = true
  }
  
  tags = {
    Name = "veyra-enterprise-alb"
    Role = "Enterprise-Foundation"
  }
}

# Enterprise RDS PostgreSQL with Multi-AZ
resource "aws_db_subnet_group" "enterprise" {
  name       = "veyra-enterprise-db-subnet-group"
  subnet_ids = aws_subnet.private[*].id
  
  tags = {
    Name = "veyra-enterprise-db-subnet-group"
    Role = "Enterprise-Foundation"
  }
}

resource "aws_security_group" "rds_enterprise" {
  name_prefix = "veyra-enterprise-rds-"
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
    Name = "veyra-enterprise-rds"
    Role = "Enterprise-Foundation"
  }
}

resource "aws_db_instance" "enterprise" {
  identifier = "veyra-enterprise-db"
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = "db.t3.medium"
  
  allocated_storage     = 200
  max_allocated_storage = 2000
  storage_type          = "gp2"
  storage_encrypted    = true
  
  db_name  = "veyra"
  username = var.db_username
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds_enterprise.id]
  db_subnet_group_name   = aws_db_subnet_group.enterprise.id
  
  backup_retention_period = 14
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = false
  publicly_accessible  = false
  
  multi_az = true
  
  performance_insights_enabled = true
  
  tags = {
    Name = "veyra-enterprise-db"
    Role = "Enterprise-Foundation"
    Environment = "production"
  }
}

# Enterprise ElastiCache Redis with Cluster Mode
resource "aws_elasticache_subnet_group" "enterprise" {
  name       = "veyra-enterprise-cache-subnet"
  subnet_ids = aws_subnet.private[*].id
  
  tags = {
    Name = "veyra-enterprise-cache-subnet-group"
    Role = "Enterprise-Foundation"
  }
}

resource "aws_elasticache_replication_group" "enterprise" {
  replication_group_id       = "veyra-enterprise-cache"
  description              = "Enterprise Redis cluster for Veyra"
  node_type               = "cache.t3.micro"
  port                    = 6379
  parameter_group_name     = "default.redis7"
  subnet_group_name        = aws_elasticache_subnet_group.enterprise.name
  security_group_ids      = [aws_security_group.redis_enterprise.id]
  automatic_failover_enabled = true
  multi_az_enabled         = true
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  
  tags = {
    Name = "veyra-enterprise-cache"
    Role = "Enterprise-Foundation"
  }
}

# Enterprise CloudFront Distribution
resource "aws_cloudfront_distribution" "enterprise" {
  enabled = true
  is_ipv6_enabled = true
  default_root_object = "index.html"
  
  # Origin for ALB
  origin {
    domain_name = aws_lb.enterprise.dns_name
    origin_id   = "alb-origin"
    
    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }
  
  # Origin for S3 assets
  origin {
    domain_name = aws_s3_bucket.assets.bucket_regional_domain_name
    origin_id   = "s3-origin"
  }
  
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
  
  # Enterprise logging
  logging_config {
    include_cookies = false
    bucket          = aws_s3_bucket.cf_logs.id
    prefix          = "cf-logs"
  }
  
  tags = {
    Name = "veyra-enterprise-cdn"
    Role = "Enterprise-Foundation"
  }
}

# Enterprise S3 with Versioning and Logging
resource "aws_s3_bucket" "enterprise_assets" {
  bucket = "veyra-enterprise-assets-${random_string.bucket_suffix.result}"
  
  tags = {
    Name = "veyra-enterprise-assets"
    Role = "Enterprise-Foundation"
  }
}

resource "aws_s3_bucket_versioning" "enterprise_assets" {
  bucket = aws_s3_bucket.enterprise_assets.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "enterprise_assets" {
  bucket = aws_s3_bucket.enterprise_assets.id
  
  rule {
    apply_server_side_encryption_by_default = true
    sse_algorithm     = "AES256"
  }
}

# Enterprise Lambda Functions
resource "aws_iam_role" "lambda_exec" {
  name = "veyra-enterprise-lambda-exec"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
  
  tags = {
    Name = "veyra-enterprise-lambda-exec"
    Role = "Enterprise-Foundation"
  }
}

resource "aws_lambda_function" "data_processor" {
  function_name = "veyra-data-processor"
  handler       = "index.handler"
  runtime       = "python3.11"
  role          = aws_iam_role.lambda_exec.arn
  
  filename         = "lambda_function_payload.zip"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  
  timeout          = 300
  memory_size      = 512
  
  environment {
    variables = {
      DATABASE_URL = var.database_url
      REDIS_URL    = var.redis_url
    }
  }
  
  tags = {
    Name = "veyra-data-processor"
    Role = "Enterprise-Foundation"
  }
}

# Enterprise CloudWatch for Monitoring
resource "aws_cloudwatch_log_group" "application" {
  name              = "/aws/lambda/veyra-data-processor"
  retention_in_days = 14
  
  tags = {
    Name = "veyra-application-logs"
    Role = "Enterprise-Foundation"
  }
}

resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "veyra-lambda-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "Errors"
  namespace          = "AWS/Lambda"
  period             = "60"
  statistic          = "Sum"
  threshold          = "5"
  alarm_description  = "This metric monitors lambda function errors"
  alarm_actions     = [aws_sns_topic.alerts.arn]
  
  tags = {
    Name = "veyra-lambda-error-alarm"
    Role = "Enterprise-Foundation"
  }
}

# Enterprise SNS for Alerts
resource "aws_sns_topic" "alerts" {
  name = "veyra-alerts"
  
  tags = {
    Name = "veyra-alerts"
    Role = "Enterprise-Foundation"
  }
}

# Random suffix for unique names
resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}