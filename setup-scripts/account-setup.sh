#!/bin/bash
# Zero-Cost Account Setup Script
echo "FINANCIAL MASTER - ZERO-COST ACCOUNT SETUP"
echo "=============================================="

# Create accounts directory
mkdir -p ~/financial-master-accounts
cd ~/financial-master-accounts

echo ""
echo "STEP 1: CREATE FREE ACCOUNTS"
echo "================================"

echo "1. CLOUDFLARE"
echo "   URL: https://dash.cloudflare.com/sign-up"
echo "   What you get: Free CDN, Workers, R2, Pages"
echo "   Click to open in browser..."
read -p "Press Enter after creating Cloudflare account..."

echo ""
echo "2. GITHUB"
echo "   URL: https://github.com/signup"
echo "   What you get: Free repos, Actions, Pages"
echo "   Click to open in browser..."
read -p "Press Enter after creating GitHub account..."

echo ""
echo "3. RENDER"
echo "   URL: https://render.com/register"
echo "   What you get: Free web services, PostgreSQL"
echo "   Click to open in browser..."
read -p "Press Enter after creating Render account..."

echo ""
echo "4. NEON"
echo "   URL: https://neon.tech/signup"
echo "   What you get: Free PostgreSQL database (500MB)"
echo "   Click to open in browser..."
read -p "Press Enter after creating Neon account..."

echo ""
echo "5. AUTH0"
echo "   URL: https://auth0.com/signup"
echo "   What you get: Free authentication (7k MAU)"
echo "   Click to open in browser..."
read -p "Press Enter after creating Auth0 account..."

echo ""
echo "6. ALPHA VANTAGE"
echo "   URL: https://www.alphavantage.co/support/#api-key"
echo "   What you get: Free financial data API (500 calls/day)"
echo "   Click to open in browser..."
read -p "Press Enter after getting Alpha Vantage API key..."

echo ""
echo "7. UPTIME ROBOT"
echo "   URL: https://uptimerobot.com/register"
echo "   What you get: Free uptime monitoring (50 monitors)"
echo "   Click to open in browser..."
read -p "Press Enter after creating Uptime Robot account..."

# Save API keys template
cat > api-keys.txt << EOF
# Financial Master API Keys
# Fill in these values after creating accounts

# Cloudflare
CLOUDFLARE_API_TOKEN=your-cloudflare-api-token
CLOUDFLARE_ACCOUNT_ID=your-cloudflare-account-id

# GitHub
# (No API key needed for basic setup)

# Render
RENDER_API_KEY=your-render-api-key

# Neon
NEON_DATABASE_URL=postgresql://username:password@host:5432/database

# Auth0
AUTH0_DOMAIN=your-domain.auth0.com
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-client-secret
AUTH0_AUDIENCE=your-api-identifier

# Alpha Vantage
ALPHA_VANTAGE_KEY=your-alpha-vantage-key

# Uptime Robot
UPTIME_ROBOT_API_KEY=your-uptime-robot-api-key
EOF

echo ""
echo "ACCOUNT SETUP COMPLETE!"
echo "API keys template saved to: ~/financial-master-accounts/api-keys.txt"
echo "Fill in the API keys in the template file"
echo "Next step: Run local-setup.sh"
