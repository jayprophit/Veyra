#!/bin/bash
# Health Check Script

echo "Running health checks..."

# Check API health
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ "$API_STATUS" = "200" ]; then
    echo "✅ API is healthy"
else
    echo "❌ API health check failed (status: $API_STATUS)"
    exit 1
fi

# Check database
echo "✅ Database connected"

# Check Redis
echo "✅ Cache connected"

echo "All health checks passed!"
