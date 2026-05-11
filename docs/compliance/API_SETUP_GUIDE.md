# API Setup Guide
## Free API Keys for Veyra

All APIs listed here have **FREE tiers** perfect for testing and personal use.

---

## Quick Summary

| API | What It Does | Free Tier | Sign Up Time | Priority |
|-----|--------------|-----------|--------------|----------|
| **Alpaca** | Paper trading (fake money) | Unlimited | 10 min | 🔴 REQUIRED |
| **Polygon.io** | Real-time stock prices | 5 calls/min | 5 min | 🟡 HIGH |
| **Alpha Vantage** | Stock data & indicators | 25 calls/day | 5 min | 🟡 HIGH |
| **Coinbase** | Crypto trading | Varies | 10 min | 🟢 OPTIONAL |
| **OpenAI** | AI predictions | $5 free credit | 5 min | 🟢 OPTIONAL |

---

## Detailed Setup Instructions

### 1. Alpaca Markets (REQUIRED)

**Purpose:** Paper trading - practice with fake money  
**Website:** https://alpaca.markets  
**Cost:** FREE forever (paper trading)  
**Why you need it:** This is how Veyra places trades

#### Step-by-Step Setup:

1. **Go to alpaca.markets**
   - Click the big green "Get Started" button

2. **Choose Account Type**
   - Select "Individual" (for personal use)
   - Do NOT select "Business" or "IRA"

3. **Enter Your Information**
   - Full name (as on your ID)
   - Email address
   - Phone number
   - Home address
   - Date of birth

4. **Employment & Financial Info**
   - Select your employment status
   - Enter approximate annual income
   - Enter approximate net worth
   - These don't affect approval, just regulatory requirements

5. **Investment Experience**
   - Select your experience level (be honest)
   - Check boxes for what you've traded before

6. **Agreements**
   - Read and check the boxes (standard broker agreements)
   - Click "Open Account"

7. **Verify Your Identity**
   - Upload a photo of your ID (passport or driver's license)
   - Upload a selfie
   - Wait for approval (usually instant, sometimes 1-2 days)

8. **Get Your API Keys**
   - Once approved, log in to your dashboard
   - Click "Paper Trading" in the menu
   - Click "API Keys"
   - Click "Generate API Key"
   - **Copy both values:**
     - **API Key ID:** Starts with `PK` (example: `PKA1B2C3D4E5F6G7H8I9`)
     - **Secret Key:** Long random string (keep this PRIVATE!)

9. **Add to Veyra**
   - Open your `.env` file (in Veyra folder)
   - Find these lines:
     ```
     ALPACA_API_KEY=your_alpaca_key_here
     ALPACA_SECRET_KEY=your_alpaca_secret_here
     ```
   - Replace with your actual keys:
     ```
     ALPACA_API_KEY=PKA1B2C3D4E5F6G7H8I9
     ALPACA_SECRET_KEY=your_actual_secret_here
     ```
   - Save the file

**⚠️ IMPORTANT:** 
- Keep your Secret Key PRIVATE - never share it
- Alpaca gives you $100,000 fake money to practice with
- All trades are fake until you specifically enable real trading

---

### 2. Polygon.io (HIGHLY RECOMMENDED)

**Purpose:** Real-time and historical stock market data  
**Website:** https://polygon.io  
**Cost:** FREE (5 API calls per minute)  
**Why you need it:** Get accurate stock prices for analysis

#### Step-by-Step Setup:

1. **Go to polygon.io**
   - Click "Get Started" or "Sign Up"

2. **Create Account**
   - Enter your email
   - Create password
   - Click "Sign Up"

3. **Verify Email**
   - Check your email
   - Click the verification link

4. **Get API Key**
   - Log in to dashboard
   - Click "API Keys" on the left menu
   - Click "Create API Key"
   - Copy the key (looks like: `abcdefghijklmnopqrstuvwxyz123456`)

5. **Add to Veyra**
   - Open `.env` file
   - Find: `POLYGON_API_KEY=your_polygon_key_here`
   - Replace: `POLYGON_API_KEY=abcdefghijklmnopqrstuvwxyz123456`
   - Save file

**Free Tier Limits:**
- 5 API calls per minute
- 2 years historical data
- Real-time data (15-minute delay for free tier)
- Perfect for testing and learning

---

### 3. Alpha Vantage (RECOMMENDED)

**Purpose:** Stock data and technical indicators  
**Website:** https://www.alphavantage.co  
**Cost:** FREE (25 API calls per day)  
**Why you need it:** Backup data source + technical indicators

#### Step-by-Step Setup:

1. **Go to alphavantage.co**
   - Scroll down to "Get Free API Key"

2. **Request API Key**
   - Enter your email address
   - Check "I'm not a robot"
   - Click "Get Free API Key"

3. **Check Your Email**
   - Look for email from Alpha Vantage
   - Subject: "Your Alpha Vantage API Key"
   - Copy the key (looks like: `ABC123DEF456GHI789`)

4. **Add to Veyra**
   - Open `.env` file
   - Find: `ALPHA_VANTAGE_API_KEY=your_alphavantage_key_here`
   - Replace: `ALPHA_VANTAGE_API_KEY=ABC123DEF456GHI789`
   - Save file

**Free Tier Limits:**
- 25 API calls per day
- 5 API calls per minute
- Good for daily analysis, not high-frequency

---

### 4. Coinbase (OPTIONAL - For Crypto)

**Purpose:** Cryptocurrency trading  
**Website:** https://www.coinbase.com  
**Cost:** Varies (free to sign up, fees on trades)  
**Why you might want it:** If you want to trade Bitcoin, Ethereum, etc.

#### Step-by-Step Setup:

1. **Create Coinbase Account**
   - Go to coinbase.com
   - Click "Get Started"
   - Enter email, create password
   - Verify email

2. **Complete Identity Verification**
   - Upload ID documents
   - Wait for approval (usually instant)

3. **Enable API Access**
   - Go to Settings → API
   - Click "+ New API Key"
   - Give it a name: "Veyra"
   - Select permissions (at minimum: "View" and "Trade")
   - Click "Create"

4. **Get API Credentials**
   - Copy the API Key
   - Copy the API Secret
   - **Important:** Store the secret safely - you can't see it again!

5. **Add to Veyra**
   - Open `.env` file
   - Add:
     ```
     COINBASE_API_KEY=your_coinbase_key
     COINBASE_SECRET=your_coinbase_secret
     ```

**Note:** Coinbase is a real exchange with real money. Only connect after you're comfortable with the system.

---

### 5. OpenAI (OPTIONAL - For AI Features)

**Purpose:** AI-powered predictions and analysis  
**Website:** https://platform.openai.com  
**Cost:** $5 free credit (then pay-as-you-go)  
**Why you might want it:** Advanced AI predictions, natural language analysis

#### Step-by-Step Setup:

1. **Go to platform.openai.com**
   - Click "Sign Up"
   - Create account with Google or email

2. **Verify Phone Number**
   - Enter your phone
   - Enter verification code

3. **Create API Key**
   - Click your profile (top right)
   - Click "View API Keys"
   - Click "Create new secret key"
   - Give it a name: "Veyra"
   - Copy the key (starts with `sk-`)
   - **IMPORTANT:** This is the only time you can see it!

4. **Add to Veyra**
   - Open `.env` file
   - Add: `OPENAI_API_KEY=sk-your_key_here`

5. **Monitor Usage**
   - Go to "Usage" to see costs
   - Free tier: $5 credit
   - Typical cost: $0.002-0.02 per request
   - 1000 requests = $2-20 depending on complexity

---

## Alternative Data Sources (All Free)

### Yahoo Finance (No API Key Needed)
Veyra can use Yahoo Finance data without any setup!
- Free
- No API key required
- 15-minute delayed data
- Good for basic price quotes

### FRED (Federal Reserve Economic Data)
**Website:** https://fred.stlouisfed.org  
**Purpose:** Economic indicators (inflation, interest rates, etc.)

1. Go to fred.stlouisfed.org
2. Click "My Account" → "API Keys"
3. Request API key
4. Add to `.env`: `FRED_API_KEY=your_key`

### Finnhub (Alternative Stock Data)
**Website:** https://finnhub.io  
**Free Tier:** 60 API calls/minute

---

## Testing Your APIs

After setting up, test that everything works:

### Test Script:
```powershell
# Run in PowerShell (in Veyra folder)
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

print('Checking API keys...')
print(f'Alpaca Key: {\"Set\" if os.getenv(\"ALPACA_API_KEY\") else \"MISSING\"}')
print(f'Polygon Key: {\"Set\" if os.getenv(\"POLYGON_API_KEY\") else \"MISSING\"}')
print(f'Alpha Vantage Key: {\"Set\" if os.getenv(\"ALPHA_VANTAGE_API_KEY\") else \"MISSING\"}')
"
```

Or simply run:
```powershell
.\scripts\health_check.ps1
```

---

## API Rate Limits & Best Practices

### Understanding Rate Limits

**What is a rate limit?**
APIs restrict how many requests you can make per minute/day to prevent abuse.

**Examples:**
- Polygon: 5 requests per minute = 1 request every 12 seconds
- Alpha Vantage: 25 per day = 1 request per hour (on average)

**Best Practices:**
1. **Cache data locally** - Don't request the same data repeatedly
2. **Use multiple APIs** - If one hits limit, use another
3. **Space out requests** - Don't make 25 requests in 1 minute
4. **Monitor usage** - Check your dashboard regularly

### Handling Rate Limits in Code

Veyra automatically:
- ✅ Caches responses
- ✅ Rotates between APIs
- ✅ Queues requests if limits hit
- ✅ Falls back to free sources (Yahoo Finance)

---

## Troubleshooting API Issues

### "Invalid API Key" Error

**Check:**
1. No extra spaces in key (before or after)
2. Full key copied (not cut off)
3. Correct key for correct service
4. Key is active (not expired or revoked)

**Fix:**
- Re-copy key from API dashboard
- Paste into `.env` file
- Save and restart application

### "Rate Limit Exceeded" Error

**Check:**
1. How many requests made today?
2. Are you hitting the free tier limit?

**Fix:**
- Wait 1 minute (for per-minute limits)
- Wait until tomorrow (for daily limits)
- Upgrade to paid tier (if needed)
- Use alternative API as backup

### "Connection Timeout" Error

**Check:**
1. Internet connection working?
2. API service status (check provider's status page)
3. Firewall blocking connection?

**Fix:**
- Check internet
- Check API provider status page
- Try again in 5 minutes
- Use alternative API

### "Permission Denied" Error

**Check:**
1. Did you enable the right permissions when creating key?
2. Is your account verified?

**Fix:**
- Create new API key with correct permissions
- Complete account verification

---

## Security Best Practices

### ✅ DO:
- Keep API keys in `.env` file only
- Never commit `.env` to GitHub
- Rotate keys every 90 days
- Use separate keys for development vs production
- Monitor API usage for unexpected activity

### ❌ DON'T:
- Share API keys with anyone
- Hardcode keys in your code
- Post keys on forums or chat
- Use production keys for testing
- Ignore unusual API usage spikes

---

## Quick Reference Card

Print this and keep it handy:

```
┌─────────────────────────────────────────────────────────┐
│                  API SETUP CHECKLIST                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  [ ] Alpaca Account: alpaca.markets                     │
│      - Created account                                  │
│      - Verified identity                                │
│      - Generated API keys                               │
│      - Added to .env file                               │
│                                                         │
│  [ ] Polygon.io: polygon.io                             │
│      - Created account                                  │
│      - Verified email                                   │
│      - Copied API key                                   │
│      - Added to .env file                               │
│                                                         │
│  [ ] Alpha Vantage: alphavantage.co                     │
│      - Requested API key via email                      │
│      - Received key in email                            │
│      - Added to .env file                               │
│                                                         │
│  [ ] Tested Configuration                               │
│      - Ran health_check.ps1                             │
│      - All APIs showing "Set"                           │
│      - Started application successfully                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Need More Help?

**Alpaca Support:** https://alpaca.markets/support  
**Polygon Support:** support@polygon.io  
**Alpha Vantage:** support@alphavantage.co

**Veyra Docs:**
- `docs\BEGINNERS_GUIDE.md` - Full setup walkthrough
- `docs\TROUBLESHOOTING.md` - Common issues
- `.\scripts\health_check.ps1` - System diagnostics

---

**Last Updated:** May 2026  
**For:** Veyra v1.0

