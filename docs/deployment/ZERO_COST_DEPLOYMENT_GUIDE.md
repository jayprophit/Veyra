# 💰 Veyra - Zero Cost Deployment Guide

## Deploy Your 100% Open-Source Platform for $0/month

---

## 🎯 Zero-Cost Architecture Overview

```text
┌─────────────────────────────────────┐
│  Frontend/Docs: Cloudflare Pages    │ ✅ FREE (Unlimited)
│  Domain: Cloudflare Registrar       │ ✅ ~$8/year (optional)
└─────────────────────────────────────┘
                 │
┌─────────────────────────────────────┐
│  Python Backend: Render             │ ✅ FREE (spins down after 15min)
│  Alternative: Fly.io ($1.94/GB)     │ ✅ Ultra cheap
└─────────────────────────────────────┘
                 │
┌─────────────────────────────────────┐
│  Database: Neon Postgres             │ ✅ FREE (500MB, 190hrs/mo)
│  Alternative: Supabase              │ ✅ FREE (500MB)
└─────────────────────────────────────┘
                 │
┌─────────────────────────────────────┐
│  API Gateway: Cloudflare Workers    │ ✅ FREE (100k requests/day)
│  Cache: Redis Cloud                 │ ✅ FREE (30MB)
└─────────────────────────────────────┘
                 │
┌─────────────────────────────────────┐
│  Storage: Cloudflare R2              │ ✅ FREE (10GB storage)
│  Monitoring: Sentry + UptimeRobot    │ ✅ FREE tiers
│  Secrets: GitHub Secrets             │ ✅ FREE
└─────────────────────────────────────┘
```

---

## 📊 Cost Breakdown

### ✅ Truly Free Components

| Component | Service | Cost | Limits |
|-----------|---------|------|--------|
| Documentation | Cloudflare Pages | $0 | Unlimited sites, 1 build/min |
| API Backend | Render | $0 | Free web services, spins down after 15min |
| Database | Neon Postgres | $0 | 500MB storage, 190 compute hours/mo |
| API Gateway | Cloudflare Workers | $0 | 100,000 requests/day |
| File Storage | Cloudflare R2 | $0 | 10GB storage, 10M reads/mo |
| Monitoring | Sentry | $0 | 5,000 errors/mo, 1 user |
| Monitoring | UptimeRobot | $0 | 50 monitors, 5min checks |
| Secrets | GitHub Secrets | $0 | Unlimited repos |
| CI/CD | GitHub Actions | $0 | 2,000 minutes/mo |

### 💰 OPTIONAL PAID UPGRADES
| Component | Service | Cost | When to Upgrade |
|-----------|---------|------|-----------------|
| Domain | Cloudflare Registrar | ~$8/year | Custom domain name |
| Backend Scaling | Render Pro | $7-25/month | High traffic, persistent backend |
| Database Scaling | Neon Pro | $19/month | >500MB storage |
| Additional Storage | Cloudflare R2 | $0.015/GB | >10GB storage |

---

---

## 🚀 Step-by-Step Deployment

### **1. 📋 GitHub Repository Setup**
```bash
# Create GitHub repository
git init
git add .
git commit -m "Initial commit: Veyra 5-STAR+ platform"
git remote add origin https://github.com/yourusername/veyra.git
git push -u origin main

# Set up GitHub Secrets (Settings > Secrets and variables > Actions)
# - ALPHA_VANTAGE_KEY
# - DATABASE_URL
# - SENTRY_DSN
# - CLOUDFLARE_API_TOKEN
```

### **2. 🌐 Cloudflare Pages (Documentation & Frontend)**
```bash
# 1. Go to Cloudflare Dashboard
# 2. Navigate to Pages
# 3. Connect to GitHub repository
# 4. Build settings:
#    - Framework preset: None
#    - Build command: npm run build-docs
#    - Build output directory: docs/
#    - Root directory: /

# Create wrangler.toml for Workers
cat > wrangler.toml << EOF
name = "veyra-api"
main = "api-gateway/worker.js"
compatibility_date = "2024-01-01"

[env.production]
vars = { ENVIRONMENT = "production" }
EOF
```

### **3. 🐍 Render Backend Deployment**
```yaml
# Create render.yaml
services:
  - type: web
    name: veyra-api
    env: python
    repo: https://github.com/yourusername/veyra.git
    rootDir: src/backend
    buildCommand: pip install -r requirements.txt
    startCommand: python main.py
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: ALPHA_VANTAGE_KEY
        sync: false
      - key: OLLAMA_BASE_URL
        value: http://localhost:11434
    healthCheckPath: /health
    autoDeploy: true
```

### **4. 🗄️ Neon Database Setup**
```bash
# 1. Go to https://neon.tech
# 2. Create free account
# 3. Create new project
# 4. Get connection string
# 5. Add to GitHub Secrets as DATABASE_URL

# Example DATABASE_URL format:
# postgresql://username:password@ep-xxx.us-east-2.aws.neon.tech/dbname?sslmode=require
```

### **5. ⚡ Cloudflare Workers API Gateway**
```javascript
// api-gateway/worker.js
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    // Route to backend
    if (url.pathname.startsWith('/api/')) {
      const backendUrl = 'https://your-app.onrender.com' + url.pathname + url.search;
      
      // Add rate limiting headers
      const response = await fetch(backendUrl, {
        method: request.method,
        headers: request.headers,
        body: request.body
      });
      
      // Add CORS headers
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
    
    return new Response('Veyra API', { status: 200 });
  }
};
```

### **6. 📊 Cloudflare R2 Storage Setup**
```bash
# 1. Go to Cloudflare Dashboard > R2 Object Storage
# 2. Create bucket: veyra-assets
# 3. Add to wrangler.toml:
[[r2_buckets]]
binding = "ASSETS"
bucket_name = "veyra-assets"

# Upload assets
wrangler r2 object put veyra-assets/logo.png --file=assets/logo.png
```

### **7. 📱 Sentry Monitoring Setup**
```python
# Add to src/backend/app/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
    environment="production"
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    sentry_sdk.capture_exception(exc)
    return {"error": "Internal server error"}
```

### **8. 🤖 GitHub Actions CI/CD**
```yaml
# .github/workflows/deploy.yml
name: Deploy Veyra

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
          projectName: veyra-docs
          directory: docs

  deploy-backend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Trigger Render Deployment
        run: |
          curl -X POST "https://api.render.com/v1/services/srv-xxx/deploys" \
            -H "Authorization: Bearer ${{ secrets.RENDER_API_KEY }}"
```

---

## 🔧 **CONFIGURATION FILES**

### **Dockerfile (for Render)**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
```

### **requirements.txt**
```txt
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
redis==5.0.1
sentry-sdk==1.38.0
aiohttp==3.9.1
pandas==2.1.4
numpy==1.25.2
scikit-learn==1.3.2
transformers==4.35.2
torch==2.1.2
```

### **render.yaml**
```yaml
services:
  - type: web
    name: veyra
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
```

---

## 📱 **MOBILE APP DEPLOYMENT**

### **iOS App Store (Free)**
```bash
# 1. Apple Developer Program ($99/year - ONLY paid component)
# 2. Build with Xcode
# 3. Upload to App Store Connect
# 4. Submit for review
```

### **Android Play Store (Free)**
```bash
# 1. Google Play Console ($25 one-time - ONLY paid component)
# 2. Build APK/AAB with Android Studio
# 3. Upload to Play Console
# 4. Submit for review
```

---

## 🎯 **PERFORMANCE OPTIMIZATIONS**

### **Reduce Render Spin-down**
```python
# Add health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

# Add keep-alive service
import asyncio
import aiohttp

async def keep_alive():
    """Keep Render service alive"""
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                await session.get("https://your-app.onrender.com/health")
        except:
            pass
        await asyncio.sleep(600)  # Ping every 10 minutes

# Start in background
asyncio.create_task(keep_alive())
```

### **Database Optimization**
```python
# Connection pooling for Neon
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

---

## 📊 **MONITORING SETUP**

### **UptimeRobot Configuration**
```bash
# 1. Go to https://uptimerobot.com
# 2. Create new monitor
# 3. Monitor Type: HTTP
# 4. URL: https://your-app.onrender.com/health
# 5. Interval: 5 minutes
# 6. Alert contacts: Add your email
```

### **Sentry Configuration**
```python
# Error tracking
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    traces_sample_rate=0.1,
    environment="production"
)

# Performance monitoring
from sentry_sdk.tracing import trace

@trace
async def expensive_operation():
    # Your code here
    pass
```

---

## 🚀 **DEPLOYMENT CHECKLIST**

### **✅ Pre-Deployment Checklist**
- [ ] GitHub repository created and pushed
- [ ] All secrets added to GitHub Secrets
- [ ] Neon database created and tested
- [ ] Cloudflare Workers API gateway configured
- [ ] Sentry account created and DSN configured
- [ ] UptimeRobot monitor set up
- [ ] Domain configured (optional)

### **✅ Deployment Steps**
1. **Push to GitHub** → Triggers CI/CD
2. **Tests run** → Validates code quality
3. **Docs deploy** → Cloudflare Pages
4. **Backend deploys** → Render
5. **API Gateway activates** → Cloudflare Workers
6. **Monitoring starts** → Sentry + UptimeRobot

### **✅ Post-Deployment Verification**
- [ ] Site loads at custom domain
- [ ] API endpoints respond
- [ ] Database connections work
- [ ] Health checks pass
- [ ] Monitoring detects issues
- [ ] Mobile apps connect

---

## 💡 **COST OPTIMIZATION TIPS**

### **Stay Within Free Tiers**
- **Render:** Service spins down after 15min inactivity (acceptable for demo/personal use)
- **Neon:** 500MB database sufficient for most users
- **Cloudflare Workers:** 100k requests/day = ~1.2 requests/second
- **R2 Storage:** 10GB enough for most static assets

### **When to Upgrade**
- **High traffic:** Render Pro ($7/month) for persistent backend
- **Large database:** Neon Pro ($19/month) for more storage
- **Custom domain:** Cloudflare Registrar (~$8/year)
- **Mobile stores:** Apple ($99/year) + Google ($25 one-time)

---

## 🎉 **TOTAL COST BREAKDOWN**

### **💰 FREE TIER (£0/month)**
- ✅ All core functionality
- ✅ Documentation hosting
- ✅ API backend (with spin-down)
- ✅ Database (500MB)
- ✅ API gateway
- ✅ Storage (10GB)
- ✅ Monitoring
- ✅ CI/CD

### **💳 OPTIONAL ADD-ONS**
- Custom domain: ~$8/year
- Mobile stores: $124 one-time
- Scaling upgrades: $7-25/month (when needed)

---

## 🚀 **IMMEDIATE ACTION PLAN**

1. **Today:** Set up GitHub repository and secrets
2. **Tomorrow:** Deploy to Cloudflare Pages + Render + Neon
3. **Day 3:** Configure Workers API gateway + monitoring
4. **Day 4:** Test full deployment and optimize
5. **Day 5:** Deploy mobile apps and go live!

---

**🏆 RESULT: Fully functional 5-STAR+ financial platform for £0/month!**

*Last updated: 2026-05-07*  
*Platform: Veyra*  
*Cost: £0/month (optional upgrades available)*
