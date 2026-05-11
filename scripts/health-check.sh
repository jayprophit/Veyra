#!/bin/bash
# Veyra - Comprehensive Health Check
# =============================================

set -e

API_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:3000"
PROMETHEUS_URL="http://localhost:9090"

echo "🏥 Veyra Health Check"
echo "================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_service() {
    local name=$1
    local url=$2
    local endpoint=${3:-/health}
    
    echo -n "Checking $name... "
    
    if curl -s -o /dev/null -w "%{http_code}" "${url}${endpoint}" | grep -q "200\|401\|403"; then
        echo -e "${GREEN}✅ UP${NC}"
        return 0
    else
        echo -e "${RED}❌ DOWN${NC}"
        return 1
    fi
}

# Check API
check_service "API Server" "$API_URL" "/api/v1/system/status"

# Check Frontend
check_service "Frontend" "$FRONTEND_URL" "/"

# Check Prometheus (optional)
if curl -s "$PROMETHEUS_URL" > /dev/null 2>&1; then
    echo -e "Prometheus... ${GREEN}✅ UP${NC}"
else
    echo -e "Prometheus... ${YELLOW}⚠️  Not running (optional)${NC}"
fi

echo ""
echo "📊 System Status Details:"
echo "-------------------------"

# Get detailed status from API
STATUS=$(curl -s "$API_URL/api/v1/system/status" 2>/dev/null || echo "{}")

# Parse and display key metrics
echo "$STATUS" | python3 -m json.tool 2>/dev/null || echo "$STATUS"

echo ""
echo "✨ All critical services are operational!"
echo ""
echo "URLs:"
echo "  Frontend: $FRONTEND_URL"
echo "  API:      $API_URL"
echo "  API Docs: $API_URL/docs"
echo "  Metrics:  $PROMETHEUS_URL (if enabled)"
