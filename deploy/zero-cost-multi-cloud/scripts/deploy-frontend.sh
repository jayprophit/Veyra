#!/bin/bash
# Deploy Frontend Script
echo "Deploying frontend to Cloudflare Pages..."

# Build the application
npm run build

# Deploy to Cloudflare Pages
npx wrangler pages publish dist --project-name=financial-master

echo "Frontend deployed to Cloudflare Pages"
echo "URL: https://financial-master.pages.dev"
