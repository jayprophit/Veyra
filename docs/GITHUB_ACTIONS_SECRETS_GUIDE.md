# GitHub Actions Secrets - Complete Guide

## 🔐 How to Add Secrets to GitHub Actions

### Step-by-Step Instructions

#### 1. Navigate to Your Repository
1. Go to https://github.com/jayprophit/Financial-Master
2. Click on **"Settings"** tab (top right of repository)

#### 2. Access Secrets Section
1. In the left sidebar, click **"Secrets and variables"**
2. Click **"Actions"** from the dropdown

#### 3. Add a New Secret
1. Click the green **"New repository secret"** button
2. Fill in the form:

| Field | Description | Example |
|-------|-------------|---------|
| **Name*** | Secret identifier (UPPERCASE with underscores) | `API_KEY_OPENAI` |
| **Secret*** | The actual secret value | `sk-abc123xyz...` |

3. Click **"Add secret"**

### 📋 Common Secrets for Financial Master

```
# API Keys
API_KEY_OPENAI              # OpenAI API for AI features
API_KEY_ALPACA              # Alpaca trading API
API_KEY_PLAID               # Plaid for bank sync
API_KEY_POLYGON             # Polygon.io market data
API_KEY_FINNHUB             # Finnhub financial data
API_KEY_TWELVE_DATA         # Twelve Data API

# Database
DATABASE_URL                # PostgreSQL connection string
DATABASE_PASSWORD           # Database password
REDIS_URL                   # Redis cache connection

# Security
JWT_SECRET_KEY              # JWT signing key
ENCRYPTION_KEY              # Data encryption key

# Cloud Services
AWS_ACCESS_KEY_ID           # AWS credentials
AWS_SECRET_ACCESS_KEY       # AWS secret
AZURE_CLIENT_SECRET         # Azure service principal
GOOGLE_CLOUD_API_KEY        # GCP API key

# Notifications
SLACK_WEBHOOK_URL           # Slack notifications
DISCORD_WEBHOOK_URL         # Discord notifications
TELEGRAM_BOT_TOKEN          # Telegram bot

# Deployment
VERCEL_TOKEN                # Vercel deployment
NETLIFY_AUTH_TOKEN          # Netlify deployment
DOCKER_HUB_TOKEN            # Docker Hub access
```

### 🔧 Using Secrets in Workflows

```yaml
# .github/workflows/ci-cd.yml
jobs:
  deploy:
    steps:
      - name: Use API Key
        env:
          OPENAI_API_KEY: ${{ secrets.API_KEY_OPENAI }}
        run: |
          echo "Using masked secret: ${OPENAI_API_KEY:0:4}****"
          python scripts/ai_analysis.py
```

### 🛡️ Security Best Practices

1. **Never commit secrets to code**
   ```bash
   # BAD - Never do this!
   API_KEY = "sk-abc123..."  # in source code
   ```

2. **Use environment variables in code**
   ```python
   # GOOD
   import os
   api_key = os.getenv('API_KEY_OPENAI')
   if not api_key:
       raise ValueError("API_KEY_OPENAI not set")
   ```

3. **Rotate secrets regularly**
   - Set calendar reminders every 90 days
   - Update both GitHub secret and external service

4. **Use least privilege**
   - Give keys only necessary permissions
   - Create separate keys for dev/prod

### 🔍 Managing Existing Secrets

| Action | Steps |
|--------|-------|
| **Update** | Secrets → Find secret → Click "Update" → Save |
| **Delete** | Secrets → Find secret → Click "Remove" |
| **View usage** | Check workflow files for `${{ secrets.NAME }}` |

### 🚨 Troubleshooting Secrets

**Problem: Secret not found in workflow**
```
Error: Input required and not supplied: api-key
```
**Solution:**
1. Verify secret name matches exactly (case-sensitive)
2. Check it's added to Repository secrets (not Environment secrets)
3. Re-run workflow after adding secret

**Problem: Secret shows as empty**
```
Secret value: 
```
**Solution:**
1. Secret wasn't saved properly - re-add it
2. Secret was deleted - check secrets list

### 📱 Quick Reference: Secret Name Patterns

```
✅ GOOD Names:
- API_KEY_OPENAI
- DATABASE_URL_PROD
- JWT_SECRET_KEY
- AWS_ACCESS_KEY_ID

❌ BAD Names:
- api-key          (lowercase)
- my secret        (spaces)
- secret!          (special chars)
- key123           (too generic)
```

---

## 🔗 Additional Resources

- [GitHub Docs: Encrypted secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Repository Settings](https://github.com/jayprophit/Financial-Master/settings/secrets/actions)
