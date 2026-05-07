#!/bin/bash
# Setup Environment Variables Script
echo "Setting up environment variables..."

# Create .env file
cat > .env << EOF
# Database
DATABASE_URL=postgresql://username:password@host:5432/database

# Authentication
AUTH0_DOMAIN=your-domain.auth0.com
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-client-secret
AUTH0_AUDIENCE=your-api-identifier

# APIs
ALPHA_VANTAGE_KEY=your-alpha-vantage-key
HUGGINGFACE_API_KEY=your-huggingface-key
OPENAI_API_KEY=your-openai-key

# Cloudflare
CLOUDFLARE_API_TOKEN=your-cloudflare-token
CLOUDFLARE_ACCOUNT_ID=your-cloudflare-account-id

# Render
RENDER_API_KEY=your-render-api-key
RENDER_SERVICE_ID=your-service-id

# Local Development
OLLAMA_URL=http://localhost:11434
REDIS_URL=redis://localhost:6379

# Environment
NODE_ENV=development
EOF

echo "Environment variables file created: .env"
echo "Please update the values with your actual API keys"
