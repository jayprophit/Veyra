#!/bin/bash
# Deployment Script for Financial Master
# Supports: local, staging, production

set -e

ENVIRONMENT=${1:-"local"}
VERSION=$(git describe --tags --always --dirty 2>/dev/null || echo "dev")

echo "========================================"
echo "Financial Master Deployment"
echo "Environment: $ENVIRONMENT"
echo "Version: $VERSION"
echo "========================================"

case $ENVIRONMENT in
    local)
        echo "Starting local deployment..."
        docker-compose -f docker-compose.yml up --build -d
        echo "Local deployment complete!"
        echo "API: http://localhost:8000"
        echo "Dashboard: http://localhost:3000"
        ;;
    staging)
        echo "Deploying to staging..."
        # Railway/Render staging
        git push staging main
        echo "Staging deployment complete!"
        ;;
    production)
        echo "Deploying to production..."
        # Blue-green deployment
        echo "Building production image..."
        docker build -t financial-master:$VERSION .
        echo "Running health checks..."
        ./health-check.sh
        echo "Production deployment complete!"
        ;;
    *)
        echo "Usage: $0 {local|staging|production}"
        exit 1
        ;;
esac

echo "========================================"
echo "Deployment finished successfully!"
echo "========================================"
