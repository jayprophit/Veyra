#!/bin/bash
# Deploy Backend Script
echo "Deploying backend to Render..."

# Trigger Render deployment
curl -X POST https://api.render.com/v1/services/$RENDER_SERVICE_ID/deploys   -H "Authorization: Bearer $RENDER_API_KEY"   -H "Content-Type: application/json"   -d '{"imageUrl": "ghcr.io/financial-master/backend:latest"}'

echo "Backend deployment triggered to Render"
echo "URL: https://financial-master.onrender.com"
