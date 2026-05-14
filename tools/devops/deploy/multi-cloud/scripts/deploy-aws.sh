#!/bin/bash
# AWS Enterprise Deployment Script
echo "Deploying Veyra to AWS Enterprise..."

# Set AWS credentials
aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID
aws configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY
aws configure set default.region us-east-1

# Deploy infrastructure
cd multi-cloud/aws/terraform
terraform init
terraform plan -out=tfplan
terraform apply tfplan

# Build and push Docker image
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com
docker build -t veyra:latest .
docker tag veyra:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/veyra:latest
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/veyra:latest

# Deploy to ECS
aws ecs update-service --cluster veyra-enterprise --service veyra-api --force-new-deployment

echo "AWS Enterprise deployment completed!"