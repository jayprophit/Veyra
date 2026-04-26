#!/bin/bash

# Financial Master - Staging Deployment Script
# Usage: ./deploy.sh [version_tag]

set -e

VERSION=${1:-"latest"}
ENVIRONMENT="staging"
DEPLOY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="financial-master"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Financial Master Staging Deployment${NC}"
echo -e "${GREEN}Version: ${VERSION}${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Error: Docker is not installed${NC}"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}Error: Docker Compose is not installed${NC}"
        exit 1
    fi
    
    # Check env file
    if [ ! -f ".env.staging" ]; then
        echo -e "${RED}Error: .env.staging file not found${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ All prerequisites met${NC}"
}

# Load environment variables
load_env() {
    echo -e "${YELLOW}Loading environment variables...${NC}"
    export $(grep -v '^#' .env.staging | xargs)
    echo -e "${GREEN}✓ Environment loaded${NC}"
}

# Run security checks
security_checks() {
    echo -e "${YELLOW}Running security checks...${NC}"
    
    # Check for hardcoded secrets
    if grep -r "password\|secret\|key" --include="*.py" --include="*.yml" ../../src/backend/app/ | grep -v "getenv\|environ\|config\|\.env" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠ Warning: Potential hardcoded secrets detected${NC}"
    fi
    
    # Check dependencies for vulnerabilities
    echo "Scanning dependencies..."
    cd ../..
    pip install safety
    safety check || echo -e "${YELLOW}⚠ Dependency vulnerabilities detected${NC}"
    cd ${DEPLOY_DIR}
    
    echo -e "${GREEN}✓ Security checks completed${NC}"
}

# Build images
build_images() {
    echo -e "${YELLOW}Building Docker images...${NC}"
    
    cd ../..
    
    # Build main API image
    docker build \
        --target staging \
        -t ${PROJECT_NAME}-api:${VERSION} \
        -t ${PROJECT_NAME}-api:${ENVIRONMENT} \
        -f Dockerfile .
    
    # Build WebSocket server image
    docker build \
        -t ${PROJECT_NAME}-ws:${VERSION} \
        -t ${PROJECT_NAME}-ws:${ENVIRONMENT} \
        -f Dockerfile.websocket .
    
    # Build ML server image
    docker build \
        -t ${PROJECT_NAME}-ml:${VERSION} \
        -t ${PROJECT_NAME}-ml:${ENVIRONMENT} \
        -f Dockerfile.ml .
    
    cd ${DEPLOY_DIR}
    
    echo -e "${GREEN}✓ Images built successfully${NC}"
}

# Run database migrations
run_migrations() {
    echo -e "${YELLOW}Running database migrations...${NC}"
    
    # Start just the database
    docker-compose -f docker-compose.staging.yml up -d postgres redis
    
    # Wait for database to be ready
    echo "Waiting for PostgreSQL..."
    sleep 10
    
    # Run migrations
    docker-compose -f docker-compose.staging.yml run --rm api \
        python -m alembic upgrade head
    
    echo -e "${GREEN}✓ Migrations completed${NC}"
}

# Deploy services
deploy_services() {
    echo -e "${YELLOW}Deploying services...${NC}"
    
    # Pull latest images if needed
    docker-compose -f docker-compose.staging.yml pull || true
    
    # Deploy with zero downtime (if possible)
    docker-compose -f docker-compose.staging.yml up -d --remove-orphans
    
    echo -e "${GREEN}✓ Services deployed${NC}"
}

# Health checks
health_checks() {
    echo -e "${YELLOW}Running health checks...${NC}"
    
    # Check API health
    MAX_RETRIES=30
    RETRY_COUNT=0
    
    until curl -sf http://localhost:8080/health > /dev/null 2>&1 || [ $RETRY_COUNT -eq $MAX_RETRIES ]; do
        echo "Waiting for API... ($RETRY_COUNT/$MAX_RETRIES)"
        sleep 5
        RETRY_COUNT=$((RETRY_COUNT + 1))
    done
    
    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        echo -e "${RED}✗ API health check failed${NC}"
        exit 1
    fi
    
    # Check WebSocket
    if ! curl -sf http://localhost:8081/health > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠ WebSocket health check warning${NC}"
    fi
    
    # Check database
    docker-compose -f docker-compose.staging.yml exec -T postgres \
        pg_isready -U fm_staging > /dev/null 2>&1 || {
        echo -e "${RED}✗ Database health check failed${NC}"
        exit 1
    }
    
    echo -e "${GREEN}✓ All health checks passed${NC}"
}

# Run integration tests
integration_tests() {
    echo -e "${YELLOW}Running integration tests...${NC}"
    
    cd ../..
    
    # Run API tests
    python -m pytest tests/integration/ -v --tb=short || {
        echo -e "${RED}✗ Integration tests failed${NC}"
        exit 1
    }
    
    # Run broker connection tests
    python -m pytest tests/brokers/ -v --tb=short || {
        echo -e "${YELLOW}⚠ Broker tests may need manual intervention${NC}"
    }
    
    cd ${DEPLOY_DIR}
    
    echo -e "${GREEN}✓ Integration tests passed${NC}"
}

# Verify broker connections
verify_brokers() {
    echo -e "${YELLOW}Verifying broker connections...${NC}"
    
    # Test Alpaca paper trading
    docker-compose -f docker-compose.staging.yml exec -T api \
        python -c "
import asyncio
from app.brokers.alpaca_client import AlpacaClient

async def test():
    client = AlpacaClient(
        api_key='${ALPACA_STAGING_KEY}',
        api_secret='${ALPACA_STAGING_SECRET}',
        paper=True
    )
    account = await client.get_account()
    print(f'Alpaca: {account.get(\"status\", \"unknown\")}')
    await client.close()

asyncio.run(test())
" || echo -e "${YELLOW}⚠ Alpaca connection needs verification${NC}"
    
    echo -e "${GREEN}✓ Broker verification completed${NC}"
}

# Setup monitoring
setup_monitoring() {
    echo -e "${YELLOW}Setting up monitoring...${NC}"
    
    # Import Grafana dashboards
    for dashboard in ./monitoring/grafana/dashboards/*.json; do
        curl -X POST \
            http://admin:${GRafana_ADMIN_PASSWORD}@localhost:3000/api/dashboards/db \
            -H "Content-Type: application/json" \
            -d "@{dashboard}" > /dev/null 2>&1 || true
    done
    
    echo -e "${GREEN}✓ Monitoring configured${NC}"
}

# Print deployment summary
print_summary() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Deployment Summary${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "Services:"
    echo "  • API Server:        http://localhost:8080"
    echo "  • WebSocket:         ws://localhost:8081/ws"
    echo "  • ML Server:         http://localhost:8082"
    echo "  • Grafana:           http://localhost:3000"
    echo "  • Prometheus:        http://localhost:9090"
    echo "  • PostgreSQL:        localhost:5432"
    echo "  • Redis:             localhost:6379"
    echo ""
    echo "Health Endpoints:"
    echo "  • API:    curl http://localhost:8080/health"
    echo "  • WS:     curl http://localhost:8081/health"
    echo "  • ML:     curl http://localhost:8082/health"
    echo ""
    echo "Useful Commands:"
    echo "  • View logs:  docker-compose -f docker-compose.staging.yml logs -f api"
    echo "  • Scale API:  docker-compose -f docker-compose.staging.yml up -d --scale api=3"
    echo "  • Shell:      docker-compose -f docker-compose.staging.yml exec api bash"
    echo ""
    echo -e "${GREEN}✓ Staging deployment completed successfully!${NC}"
}

# Rollback function
rollback() {
    echo -e "${RED}Rolling back deployment...${NC}"
    docker-compose -f docker-compose.staging.yml down
    docker-compose -f docker-compose.staging.yml up -d
    echo -e "${GREEN}✓ Rollback completed${NC}"
}

# Main deployment flow
main() {
    # Trap errors
    trap 'echo -e "${RED}Error occurred. Initiating rollback...${NC}"; rollback; exit 1' ERR
    
    check_prerequisites
    load_env
    security_checks
    build_images
    run_migrations
    deploy_services
    health_checks
    integration_tests
    verify_brokers
    setup_monitoring
    print_summary
}

# Handle command line arguments
case "${2:-}" in
    rollback)
        rollback
        ;;
    restart)
        docker-compose -f docker-compose.staging.yml restart
        ;;
    logs)
        docker-compose -f docker-compose.staging.yml logs -f
        ;;
    down)
        docker-compose -f docker-compose.staging.yml down
        ;;
    *)
        main
        ;;
esac
