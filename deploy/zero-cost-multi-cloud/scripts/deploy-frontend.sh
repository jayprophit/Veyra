#!/bin/bash
# Deploy Frontend Script
echo "Deploying frontend to Cloudflare Pages..."

# Build the application
npm run build

# Deploy to Cloudflare Pages
npx wrangler pages publish dist --project-name=veyra

echo "Frontend deployed to Cloudflare Pages"
echo "URL: https://veyra.pages.dev"
