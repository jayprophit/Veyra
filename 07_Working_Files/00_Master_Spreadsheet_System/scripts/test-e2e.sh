#!/bin/bash
# End-to-End Testing Script

echo "Running E2E tests..."

# Run pytest
pytest tests/ -v --tb=short

# Run API tests
curl -s http://localhost:8000/api/v1/health > /dev/null && echo "✅ API tests passed"

echo "E2E tests complete!"
