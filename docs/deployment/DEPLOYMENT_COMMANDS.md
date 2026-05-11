DEPLOYMENT COMMANDS
====================

1. GitHub Setup
   git init
   git add .
   git commit -m "Initial commit: Veyra 5-STAR+ platform"
   git remote add origin https://github.com/yourusername/veyra.git
   git push -u origin main

2. Cloudflare Pages (Documentation)
   # Go to: https://dash.cloudflare.com/pages
   # Connect GitHub repository
   # Build settings:
   #   - Framework: None
   #   - Build command: echo "No build needed"
   #   - Build output: docs/

3. Render (Backend)
   # Go to: https://render.com
   # Connect GitHub repository
   # Use render.yaml file
   # Set environment variables from .env.example

4. Neon Database
   # Go to: https://neon.tech
   # Create free account
   # Create new project
   # Copy connection string to Render environment

5. Cloudflare Workers (API Gateway)
   # Install Wrangler: npm install -g wrangler
   # Login: wrangler login
   # Deploy: wrangler deploy

6. Monitoring Setup
   # Sentry: https://sentry.io
   # UptimeRobot: https://uptimerobot.com

7. Test Everything
   # Health check: curl https://your-app.onrender.com/health
   # API test: curl https://your-api.your-subdomain.workers.dev/api/health
   # Documentation: https://your-pages.pages.dev