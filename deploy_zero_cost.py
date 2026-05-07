#!/usr/bin/env python3
"""
Zero Cost Deployment Script
===========================
Automated deployment of Financial Master to free-tier services
"""

import os
import json
import subprocess
from pathlib import Path

class ZeroCostDeployer:
    """Automated deployment to zero-cost services"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.config = self.load_config()
        
    def load_config(self):
        """Load deployment configuration"""
        config_file = self.project_root / "deployment_config.json"
        if config_file.exists():
            with open(config_file) as f:
                return json.load(f)
        return self.default_config()
    
    def default_config(self):
        """Default zero-cost configuration"""
        return {
            "services": {
                "frontend": {
                    "provider": "cloudflare_pages",
                    "cost": 0,
                    "limits": "Unlimited sites, 1 build/min"
                },
                "backend": {
                    "provider": "render",
                    "cost": 0,
                    "limits": "Free web services, spins down after 15min"
                },
                "database": {
                    "provider": "neon",
                    "cost": 0,
                    "limits": "500MB storage, 190 compute hours/mo"
                },
                "api_gateway": {
                    "provider": "cloudflare_workers",
                    "cost": 0,
                    "limits": "100,000 requests/day"
                },
                "storage": {
                    "provider": "cloudflare_r2",
                    "cost": 0,
                    "limits": "10GB storage, 10M reads/mo"
                },
                "monitoring": {
                    "provider": "sentry_uptimerobot",
                    "cost": 0,
                    "limits": "5k errors/mo, 50 monitors"
                }
            },
            "total_monthly_cost": 0,
            "optional_upgrades": {
                "domain": {"cost": 8, "period": "yearly", "provider": "cloudflare"},
                "mobile_stores": {"cost": 124, "period": "one_time", "providers": ["apple", "google"]},
                "scaling": {"cost": "7-25", "period": "monthly", "provider": "render"}
            }
        }
    
    def create_deployment_files(self):
        """Create all necessary deployment files"""
        print("🚀 Creating deployment files...")
        
        # Create render.yaml
        render_config = """
services:
  - type: web
    name: financial-master
    runtime: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: ALPHA_VANTAGE_KEY
        sync: false
      - key: SENTRY_DSN
        sync: false
      - key: OLLAMA_BASE_URL
        value: http://localhost:11434
"""
        
        with open(self.project_root / "render.yaml", "w") as f:
            f.write(render_config.strip())
        
        # Create wrangler.toml for Cloudflare Workers
        wrangler_config = """
name = "financial-master-api"
main = "api-gateway/worker.js"
compatibility_date = "2024-01-01"

[[r2_buckets]]
binding = "ASSETS"
bucket_name = "financial-master-assets"

[env.production]
vars = { ENVIRONMENT = "production" }
"""
        
        os.makedirs(self.project_root / "api-gateway", exist_ok=True)
        with open(self.project_root / "wrangler.toml", "w") as f:
            f.write(wrangler_config.strip())
        
        # Create Cloudflare Worker
        worker_js = """
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    // Route to backend
    if (url.pathname.startsWith('/api/')) {
      const backendUrl = 'https://financial-master.onrender.com' + url.pathname + url.search;
      
      const response = await fetch(backendUrl, {
        method: request.method,
        headers: request.headers,
        body: request.body
      });
      
      const newResponse = new Response(response.body, response);
      newResponse.headers.set('Access-Control-Allow-Origin', '*');
      newResponse.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE');
      newResponse.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');
      
      return newResponse;
    }
    
    // Serve static files from R2
    if (url.pathname.startsWith('/static/')) {
      return env.ASSETS.fetch(request);
    }
    
    return new Response('Financial Master API - 5-STAR+ Platform', { 
      status: 200,
      headers: { 'Content-Type': 'text/plain' }
    });
  }
};
"""
        
        with open(self.project_root / "api-gateway" / "worker.js", "w") as f:
            f.write(worker_js.strip())
        
        # Create GitHub Actions workflow
        workflow_dir = self.project_root / ".github" / "workflows"
        workflow_dir.mkdir(parents=True, exist_ok=True)
        
        workflow_yml = """
name: Deploy Financial Master

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd src/backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd src/backend
          python -m pytest tests/ -v

  deploy-docs:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Cloudflare Pages
        uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          projectName: financial-master-docs
          directory: docs

  deploy-backend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Trigger Render Deployment
        run: |
          curl -X POST "https://api.render.com/v1/services/srv-xxx/deploys" \\
            -H "Authorization: Bearer ${{ secrets.RENDER_API_KEY }}"
"""
        
        with open(workflow_dir / "deploy.yml", "w") as f:
            f.write(workflow_yml.strip())
        
        print("✅ Deployment files created successfully!")
    
    def create_dockerfile(self):
        """Create Dockerfile for Render deployment"""
        dockerfile = """
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
        
        with open(self.project_root / "src" / "backend" / "Dockerfile", "w") as f:
            f.write(dockerfile.strip())
        
        print("✅ Dockerfile created for Render deployment!")
    
    def create_requirements_txt(self):
        """Create optimized requirements.txt for free tier"""
        requirements = """
# Core Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0

# Database
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1

# Cache & Queue
redis==5.0.1

# Monitoring & Error Tracking
sentry-sdk[fastapi]==1.38.0

# HTTP Client
aiohttp==3.9.1
httpx==0.25.2

# Data Processing
pandas==2.1.4
numpy==1.25.2

# Machine Learning (optimized for CPU)
scikit-learn==1.3.2
joblib==1.3.2

# AI/ML (lightweight versions)
transformers==4.35.2
torch==2.1.2
sentencepiece==0.1.99

# Financial Data
yfinance==0.2.28
python-dotenv==1.0.0

# Utilities
python-dateutil==2.8.2
pydantic==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
"""
        
        with open(self.project_root / "src" / "backend" / "requirements.txt", "w") as f:
            f.write(requirements.strip())
        
        print("✅ Optimized requirements.txt created!")
    
    def setup_environment_files(self):
        """Create environment configuration files"""
        # .env.example
        env_example = """
# Database (Neon)
DATABASE_URL=postgresql://username:password@ep-xxx.us-east-2.aws.neon.tech/dbname?sslmode=require

# API Keys (Free tier)
ALPHA_VANTAGE_KEY=your_alpha_vantage_key_here

# AI Configuration (Local Ollama)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

# Monitoring
SENTRY_DSN=your_sentry_dsn_here

# Cloudflare
CLOUDFLARE_API_TOKEN=your_cloudflare_token
CLOUDFLARE_ACCOUNT_ID=your_account_id

# Render (auto-set)
PORT=8000

# Security
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_here
"""
        
        with open(self.project_root / ".env.example", "w") as f:
            f.write(env_example.strip())
        
        # .gitignore
        gitignore = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite3

# Node (if any frontend)
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Deployment specific
.render/
.vercel/
"""
        
        with open(self.project_root / ".gitignore", "w") as f:
            f.write(gitignore.strip())
        
        print("✅ Environment files created!")
    
    def create_health_check_endpoints(self):
        """Add health check endpoints to prevent spin-down"""
        health_check_code = """
# Add to main.py for Render health checks
from fastapi import FastAPI
from datetime import datetime
import asyncio
import aiohttp

app = FastAPI(title="Financial Master API", version="1.0.0")

@app.get("/health")
async def health_check():
    \"\"\"Health check endpoint for Render monitoring\"\"\"
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "service": "Financial Master"
    }

@app.get("/")
async def root():
    \"\"\"Root endpoint\"\"\"
    return {
        "message": "Financial Master - 5-STAR+ Platform",
        "status": "operational",
        "docs": "/docs",
        "health": "/health"
    }

# Keep-alive service to prevent Render spin-down
async def keep_alive():
    \"\"\"Ping the service every 10 minutes to prevent spin-down\"\"\"
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                await session.get("https://financial-master.onrender.com/health")
        except Exception as e:
            print(f"Keep-alive ping failed: {e}")
        await asyncio.sleep(600)  # 10 minutes

# Start keep-alive in background
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(keep_alive())
"""
        
        health_file = self.project_root / "src" / "backend" / "health_endpoints.py"
        with open(health_file, "w") as f:
            f.write(health_check_code.strip())
        
        print("✅ Health check endpoints created!")
    
    def calculate_costs(self):
        """Calculate and display cost breakdown"""
        print("\n" + "="*60)
        print("💰 ZERO-COST DEPLOYMENT BREAKDOWN")
        print("="*60)
        
        total_monthly = 0
        
        for service, config in self.config["services"].items():
            print(f"\n📊 {service.replace('_', ' ').title()}:")
            print(f"   Provider: {config['provider']}")
            print(f"   Cost: ${config['cost']}/month")
            print(f"   Limits: {config['limits']}")
            total_monthly += config['cost']
        
        print(f"\n💳 TOTAL MONTHLY COST: ${total_monthly}")
        
        print(f"\n🎯 OPTIONAL UPGRADES:")
        for upgrade, config in self.config["optional_upgrades"].items():
            print(f"   {upgrade.replace('_', ' ').title()}: ${config['cost']}/{config['period']}")
        
        print(f"\n🏆 RESULT: 5-STAR+ Financial Platform for ${total_monthly}/month!")
        print("="*60)
    
    def generate_deployment_commands(self):
        """Generate deployment commands for each service"""
        commands = """
DEPLOYMENT COMMANDS
====================

1. GitHub Setup
   git init
   git add .
   git commit -m "Initial commit: Financial Master 5-STAR+ platform"
   git remote add origin https://github.com/yourusername/financial-master.git
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
"""
        
        with open(self.project_root / "DEPLOYMENT_COMMANDS.md", "w") as f:
            f.write(commands.strip())
        
        print("✅ Deployment commands guide created!")
    
    def run_deployment(self):
        """Run the complete zero-cost deployment setup"""
        print("🚀 Starting Zero-Cost Deployment Setup...")
        print("="*60)
        
        try:
            # Create all deployment files
            self.create_deployment_files()
            self.create_dockerfile()
            self.create_requirements_txt()
            self.setup_environment_files()
            self.create_health_check_endpoints()
            self.generate_deployment_commands()
            
            # Show cost breakdown
            self.calculate_costs()
            
            print(f"\n🎉 SUCCESS! Zero-cost deployment files created!")
            print(f"📁 Check these files:")
            print(f"   - render.yaml (Backend configuration)")
            print(f"   - wrangler.toml (API Gateway)")
            print(f"   - .github/workflows/deploy.yml (CI/CD)")
            print(f"   - DEPLOYMENT_COMMANDS.md (Step-by-step guide)")
            print(f"\n🚀 Next: Follow the deployment commands guide!")
            
        except Exception as e:
            print(f"❌ Deployment setup failed: {e}")
            raise

def main():
    """Main deployment function"""
    deployer = ZeroCostDeployer()
    deployer.run_deployment()

if __name__ == "__main__":
    main()
