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