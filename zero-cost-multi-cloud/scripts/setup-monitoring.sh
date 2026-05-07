#!/bin/bash
# Setup Monitoring Script
echo "Setting up monitoring stack..."

# Start monitoring services
docker-compose up -d grafana prometheus

echo "Monitoring services started:"
echo "Grafana: http://localhost:3000 (admin/admin)"
echo "Prometheus: http://localhost:9090"

# Setup Uptime Robot monitors
echo "Setup Uptime Robot monitors at: https://uptimerobot.com/dashboard"
echo "Monitor URLs:"
echo "- Frontend: https://financial-master.pages.dev"
echo "- Backend: https://financial-master.onrender.com"
echo "- API: https://financial-master-api.workers.dev"
