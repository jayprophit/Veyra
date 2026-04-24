# GitHub Secrets Setup Guide

## Required Secrets for CI/CD Pipeline

### 1. Security & Monitoring
| Secret Name | How to Get | Purpose |
|-------------|------------|---------|
| `SNYK_TOKEN` | snyk.io/auth → API token | Security vulnerability scanning |
| `SENTRY_AUTH_TOKEN` | sentry.io → Settings → Auth Tokens | Error tracking |
| `SENTRY_ORG` | Your Sentry organization slug | Error tracking org |
| `SENTRY_PROJECT` | Your Sentry project name | Error tracking project |

### 2. Deployment - Staging
| Secret Name | How to Get | Purpose |
|-------------|------------|---------|
| `STAGING_HOST` | Your staging server IP/hostname | SSH deployment target |
| `STAGING_USER` | SSH username for staging | SSH authentication |
| `STAGING_SSH_KEY` | `cat ~/.ssh/id_rsa` | Private key for staging SSH |

### 3. Deployment - Production
| Secret Name | How to Get | Purpose |
|-------------|------------|---------|
| `PROD_HOST` | Your production server IP/hostname | SSH deployment target |
| `PROD_USER` | SSH username for production | SSH authentication |
| `PROD_SSH_KEY` | `cat ~/.ssh/id_rsa` | Private key for production SSH |

### 4. Notifications
| Secret Name | How to Get | Purpose |
|-------------|------------|---------|
| `SLACK_WEBHOOK` | Slack Apps → Incoming Webhooks | Deployment notifications |

## Setup Steps

### Step 1: Navigate to Secrets
1. Go to GitHub Repository
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"

### Step 2: Add Each Secret
```bash
# Example values (replace with your actual values)
SNYK_TOKEN: 12345678-1234-1234-1234-123456789abc
SENTRY_AUTH_TOKEN: sntrys_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SENTRY_ORG: your-org-name
SENTRY_PROJECT: financial-master
STAGING_HOST: staging.yourdomain.com
STAGING_USER: deploy
STAGING_SSH_KEY: -----BEGIN OPENSSH PRIVATE KEY-----
...
PROD_HOST: api.yourdomain.com
PROD_USER: deploy
PROD_SSH_KEY: -----BEGIN OPENSSH PRIVATE KEY-----
...
SLACK_WEBHOOK: https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX
```

### Step 3: Verify Setup
```bash
# Test Sentry
curl -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  https://sentry.io/api/0/projects/$SENTRY_ORG/$SENTRY_PROJECT/

# Test SSH (staging)
ssh -i ~/.ssh/id_rsa $STAGING_USER@$STAGING_HOST "echo 'Connected!'"
```

## Railway/Vercel Alternative (Free Tier)

If using Railway + Vercel instead of SSH deployment:

| Secret Name | How to Get | Purpose |
|-------------|------------|---------|
| `RAILWAY_TOKEN` | Railway Dashboard → Tokens | Backend deployment |
| `VERCEL_TOKEN` | Vercel Dashboard → Settings → Tokens | Frontend deployment |
| `DATABASE_URL` | Railway Postgres → Connection String | Database connection |
| `REDIS_URL` | Upstash → Connect → url | Redis connection |

### Railway + Vercel Setup
```bash
# Railway CLI
npm install -g @railway/cli
railway login --token $RAILWAY_TOKEN

# Vercel CLI
npm install -g vercel
vercel --token=$VERCEL_TOKEN
```

## Environment Variables (Non-Secret)

Add these to `.env.example` (not GitHub secrets):
```env
# Application Settings
DEBUG=false
LOG_LEVEL=INFO

# Database (use secrets for production)
DATABASE_URL=postgresql://user:pass@localhost/db

# Redis
REDIS_URL=redis://localhost:6379

# API Keys (use secrets for production)
PLAID_CLIENT_ID=xxx
PLAID_SECRET=xxx
ALPACA_API_KEY=xxx
ALPACA_SECRET_KEY=xxx

# JWT
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Verification Checklist

- [ ] SNYK_TOKEN added
- [ ] SENTRY_AUTH_TOKEN added
- [ ] SENTRY_ORG added
- [ ] SENTRY_PROJECT added
- [ ] STAGING_HOST added
- [ ] STAGING_USER added
- [ ] STAGING_SSH_KEY added
- [ ] PROD_HOST added
- [ ] PROD_USER added
- [ ] PROD_SSH_KEY added
- [ ] SLACK_WEBHOOK added (optional)

## Test Pipeline

Push to `develop` branch to test staging deployment:
```bash
git checkout develop
git merge feature/your-feature
git push origin develop
```

Check GitHub Actions tab for pipeline status.
