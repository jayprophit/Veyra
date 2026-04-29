# GitHub Actions Secrets Guide

## How to Add Secrets

1. Go to: https://github.com/jayprophit/Financial-Master/settings/secrets/actions
2. Click **"New repository secret"**
3. Enter:
   - **Name**: `API_KEY_OPENAI` (UPPERCASE_WITH_UNDERSCORES)
   - **Secret**: Your actual API key value
4. Click **"Add secret"**

## Common Secret Names

| Purpose | Secret Name |
|---------|-------------|
| OpenAI API | `API_KEY_OPENAI` |
| Alpaca Trading | `API_KEY_ALPACA` |
| Plaid Bank Sync | `API_KEY_PLAID` |
| Database URL | `DATABASE_URL` |
| JWT Secret | `JWT_SECRET_KEY` |

## Usage in Workflows

```yaml
env:
  OPENAI_API_KEY: ${{ secrets.API_KEY_OPENAI }}
```

## Security Rules

- Never commit secrets to code
- Rotate every 90 days
- Use least privilege access
