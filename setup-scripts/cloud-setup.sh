#!/bin/bash
# Cloud Services Setup Script
echo "FINANCIAL MASTER - CLOUD SERVICES SETUP"
echo "==========================================="

echo ""
echo "STEP 1: CLOUDFLARE PAGES SETUP"
echo "================================="

echo "Opening Cloudflare Pages setup..."
echo "Setup details:"
echo "   1. Go to Cloudflare Dashboard -> Pages -> Create application"
echo "   2. Connect to GitHub repository"
echo "   3. Build settings:"
echo "      - Framework preset: None"
echo "      - Build command: mkdir -p dist && cp src/frontend/index.html dist/"
echo "      - Build output directory: dist"
echo "   4. Environment variables:"
echo "      - API_URL: https://financial-master-api.workers.dev"

read -p "Press Enter after setting up Cloudflare Pages..."

echo ""
echo "STEP 2: CLOUDFLARE WORKERS SETUP"
echo "==================================="

echo "Opening Cloudflare Workers setup..."
echo "Setup details:"
echo "   1. Go to Cloudflare Dashboard -> Workers & Pages -> Create application"
echo "   2. Create Worker"
echo "   3. Add the following code:"

cat << 'WORKER_CODE'
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const url = new URL(request.url)
  
  // CORS handling
  if (request.method === 'OPTIONS') {
    return new Response(null, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
      }
    })
  }
  
  // Route to backend
  if (url.pathname.startsWith('/api/')) {
    const backendUrl = 'https://financial-master-api.onrender.com' + url.pathname
    try {
      const response = await fetch(backendUrl, {
        method: request.method,
        headers: request.headers,
        body: request.body
      })
      
      return new Response(response.body, {
        status: response.status,
        headers: {
          ...response.headers,
          'Access-Control-Allow-Origin': '*'
        }
      })
    } catch (error) {
      return new Response(JSON.stringify({
        error: 'Backend service unavailable',
        message: 'The backend service is currently being deployed'
      }), {
        status: 503,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      })
    }
  }
  
  return new Response('Financial Master API Gateway', { status: 200 })
}
WORKER_CODE

read -p "Press Enter after setting up Cloudflare Workers..."

echo ""
echo "STEP 3: RENDER SETUP"
echo "======================"

echo "Opening Render setup..."
echo "Setup details:"
echo "   1. Go to Render Dashboard -> New -> Web Service"
echo "   2. Connect to GitHub repository"
echo "   3. Configuration:"
echo "      - Name: financial-master-api"
echo "      - Environment: Node"
echo "      - Plan: Free"
echo "      - Build Command: npm install"
echo "      - Start Command: npm start"
echo "   4. Environment variables (from api-keys.txt):"
echo "      - DATABASE_URL"
echo "      - REDIS_URL"
echo "      - AUTH0_DOMAIN"
echo "      - AUTH0_CLIENT_ID"
echo "      - AUTH0_CLIENT_SECRET"
echo "      - ALPHA_VANTAGE_KEY"
echo "      - NODE_ENV: production"
echo "      - PORT: 8000"

read -p "Press Enter after setting up Render..."

echo ""
echo "STEP 4: NEON DATABASE SETUP"
echo "=============================="

echo "Opening Neon setup..."
echo "Setup details:"
echo "   1. Go to Neon Dashboard -> New Project"
echo "   2. Project name: financial-master"
echo "   3. Database name: financial_master"
echo "   4. Region: Choose closest to you"
echo "   5. Get connection string and add to Render environment variables"

read -p "Press Enter after setting up Neon database..."

echo ""
echo "STEP 5: AUTH0 SETUP"
echo "====================="

echo "Opening Auth0 setup..."
echo "Setup details:"
echo "   1. Go to Auth0 Dashboard -> Applications -> Create Application"
echo "   2. Application name: Financial Master"
echo "   3. Application type: Single Page Application"
echo "   4. Technologies: React"
echo "   5. Callback URLs:"
echo "      - http://localhost:8000"
echo "      - https://financial-master.pages.dev"
echo "   6. Logout URLs:"
echo "      - http://localhost:8000"
echo "      - https://financial-master.pages.dev"

read -p "Press Enter after setting up Auth0..."

echo ""
echo "STEP 6: UPTIME ROBOT SETUP"
echo "=============================="

echo "Opening Uptime Robot setup..."
echo "Setup details:"
echo "   1. Go to Uptime Robot Dashboard -> Add New Monitor"
echo "   2. Monitor Type: HTTP"
echo "   3. Monitor Name: Financial Master Frontend"
echo "   4. URL: https://financial-master.pages.dev"
echo "   5. Interval: 5 minutes"
echo "   6. Create additional monitors:"
echo "      - Backend: https://financial-master-api.onrender.com/health"
echo "      - API Gateway: https://financial-master-api.workers.dev"

read -p "Press Enter after setting up Uptime Robot..."

echo ""
echo "STEP 7: GITHUB SECRETS SETUP"
echo "================================"

echo "Opening GitHub Secrets setup..."
echo "Setup details:"
echo "   1. Go to your GitHub repository -> Settings -> Secrets and variables -> Actions"
echo "   2. Add these secrets:"
echo "      - CLOUDFLARE_API_TOKEN"
echo "      - CLOUDFLARE_ACCOUNT_ID"
echo "      - RENDER_API_KEY"
echo "      - AUTH0_DOMAIN"
echo "      - AUTH0_CLIENT_ID"
echo "      - ALPHA_VANTAGE_KEY"

read -p "Press Enter after setting up GitHub Secrets..."

echo ""
echo "CLOUD SERVICES SETUP COMPLETE!"
echo "================================"
echo ""
echo "Your services are being deployed:"
echo "   Frontend: https://financial-master.pages.dev"
echo "   Backend: https://financial-master-api.onrender.com"
echo "   API Gateway: https://financial-master-api.workers.dev"
echo "   Database: Neon PostgreSQL"
echo "   Authentication: Auth0"
echo "   Monitoring: Uptime Robot"
echo ""
echo "Wait a few minutes for all services to fully deploy..."
echo "Next step: Run deployment.sh"
