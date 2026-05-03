# Financial Master - Beginner's Guide
## For Users with No-Code Experience

**Welcome!** This guide assumes you have never coded before. We'll walk you through everything step-by-step.

---

## What Is Financial Master?

Financial Master is an **automated trading platform** that:
- Tracks your wealth across all accounts
- Analyzes stocks, crypto, and other assets
- Can automatically trade for you (optional)
- Runs entirely on your computer or in the cloud
- Is **FREE** to start (paper trading)

**Think of it as:** A smart assistant that watches the markets 24/7 and helps you make better investment decisions.

---

## What You Need to Start (Prerequisites)

### Hardware
- ✅ Windows 10 or 11 computer
- ✅ Internet connection
- ✅ 8GB RAM (minimum)
- ✅ 50GB free disk space

### Accounts (All Free)
You'll need to create these accounts (takes ~30 minutes total):

| Account | Purpose | Cost | Time to Setup |
|---------|---------|------|---------------|
| **GitHub** | Store your code | FREE | 5 min |
| **Alpaca** | Paper trading (practice) | FREE | 10 min |
| **Polygon.io** | Stock data | FREE | 5 min |
| **Alpha Vantage** | More stock data | FREE | 5 min |

---

## Step-by-Step Setup (Total Time: ~1 Hour)

### Step 1: Run the Automated Setup (15 minutes)

**What this does:** Installs all the programs you need automatically.

1. **Open PowerShell as Administrator**
   - Press `Windows Key + X`
   - Click "Terminal (Admin)" or "Windows PowerShell (Admin)"
   - Click "Yes" if Windows asks for permission

2. **Navigate to your project folder**
   ```powershell
   cd "C:\Users\jpowe\Desktop\Financial Master"
   ```

3. **Run the setup script**
   ```powershell
   .\scripts\complete_setup.ps1
   ```
   - Press any key to start
   - Wait 15-20 minutes (it will install Python, Git, VS Code, and all dependencies)
   - Don't close the window until it says "SETUP COMPLETE!"

**What just happened?**
- ✅ Installed Python (the programming language)
- ✅ Installed Git (for saving your code)
- ✅ Installed VS Code (where you edit code)
- ✅ Created a virtual environment (isolated workspace)
- ✅ Downloaded all required software libraries

---

### Step 2: Create Free Accounts (30 minutes)

#### Account 1: GitHub (5 minutes)
**Purpose:** Store your code safely in the cloud

1. Go to: https://github.com/signup
2. Enter your email → Create password → Choose username
3. Verify your email
4. **Note your username** (you'll need it later)

#### Account 2: Alpaca Markets (10 minutes)
**Purpose:** Practice trading with fake money (paper trading)

1. Go to: https://alpaca.markets
2. Click "Get Started" → "Open Account"
3. Select "Individual" account type
4. Fill in your details (this is a real broker, so they need ID verification)
5. Choose "Paper Trading Only" (you can add real money later)
6. Once approved, log in to your dashboard
7. Go to: Paper Trading → API Keys
8. Click "Generate API Key"
9. **Copy and save:**
   - API Key ID (looks like: PKXXXXXXXXXXXXXXXXXX)
   - Secret Key (longer string, keep this SECRET!)

#### Account 3: Polygon.io (5 minutes)
**Purpose:** Get real-time stock prices

1. Go to: https://polygon.io
2. Click "Get Started" → Sign up with email
3. Verify your email
4. Log in to Dashboard
5. Click "API Keys" in the menu
6. Click "Create API Key"
7. **Copy the key** (looks like: abcdef1234567890abcdef1234567890)

#### Account 4: Alpha Vantage (5 minutes)
**Purpose:** Additional stock data (free backup)

1. Go to: https://www.alphavantage.co/support/#api-key
2. Scroll down and click "Get Free API Key"
3. Enter your email
4. Check your email for the API key
5. **Copy the key** (looks like: ABC123DEF456GHI789)

---

### Step 3: Add Your API Keys (5 minutes)

**What this does:** Tells Financial Master how to connect to your accounts.

1. **Find your .env file**
   - Open File Explorer
   - Go to: `C:\Users\jpowe\Desktop\Financial Master`
   - Find the file named `.env` (if you don't see it, look for `.env.example`)

2. **Open the file**
   - Right-click `.env` → Open with → Notepad (or VS Code if installed)

3. **Add your API keys**
   Find these lines and replace the placeholder text:

   ```
   # BEFORE (placeholder):
   ALPACA_API_KEY=your_alpaca_key_here
   ALPACA_SECRET_KEY=your_alpaca_secret_here
   POLYGON_API_KEY=your_polygon_key_here
   ALPHA_VANTAGE_API_KEY=your_alphavantage_key_here

   # AFTER (your real keys):
   ALPACA_API_KEY=PKXXXXXXXXXXXXXXXXXX
   ALPACA_SECRET_KEY=your_actual_secret_here
   POLYGON_API_KEY=your_actual_polygon_key
   ALPHA_VANTAGE_API_KEY=your_actual_alphavantage_key
   ```

4. **Save the file**
   - File → Save
   - Close Notepad

**⚠️ IMPORTANT:** Never share this file or commit it to GitHub. It contains your private keys!

---

### Step 4: Test Everything (5 minutes)

**Run the health check:**
```powershell
.\scripts\health_check.ps1
```

You should see all green checkmarks ✅. If you see any red ❌, run:
```powershell
.\scripts\complete_setup.ps1
```

---

### Step 5: Start the Application (1 minute)

**Launch Financial Master:**
```powershell
.\scripts\start_local.ps1
```

You'll see:
- A bunch of text scrolling by (this is normal!)
- Lines saying "Application startup complete"
- URL: http://localhost:8000

**Open in your browser:**
1. Open Chrome/Edge/Firefox
2. Go to: http://localhost:8000
3. You should see the Financial Master interface!

**To stop the application:**
- Go back to PowerShell
- Press `Ctrl + C` (hold Ctrl and press C)
- Type `Y` if it asks to confirm

---

## Your First Steps in Financial Master

### 1. Check Your Setup

Open: http://localhost:8000/docs

This shows all the API endpoints (think of them as features). You can:
- Click any endpoint to see what it does
- Click "Try it out" to test it
- See the documentation

### 2. Test Paper Trading

1. Go to: http://localhost:8000
2. Look for "Trading" or "Portfolio" section
3. Make sure "Paper Trading" mode is ON (this uses fake money!)
4. Try placing a test trade (buy 1 share of AAPL)

### 3. Explore Features

**Wealth Tracking:**
- Add your accounts
- See total net worth
- Track over time

**Market Analysis:**
- View stock charts
- See AI predictions
- Get trading signals

**Automation:**
- Set up alerts
- Configure auto-trading rules
- Set risk limits

---

## Common Tasks (How-To)

### How to Update the Software

```powershell
# 1. Save your work
cd "C:\Users\jpowe\Desktop\Financial Master"
git add .
git commit -m "Before update"

# 2. Get latest version
git pull origin main

# 3. Update dependencies
.\scripts\complete_setup.ps1
```

### How to Backup Your Data

Your data is stored in:
- `C:\Users\jpowe\Desktop\Financial Master\financial_master.db` (database)
- `C:\Users\jpowe\Desktop\Financial Master\.env` (settings)

**Backup method:**
```powershell
.\scripts\backup.ps1
```

### How to Get Help

1. **Check the health:** `.\scripts\health_check.ps1`
2. **Read troubleshooting:** `docs\TROUBLESHOOTING.md`
3. **Run diagnostics:** `.\scripts\complete_setup.ps1`

---

## Understanding the Basics

### What Are These Files?

```
Financial Master/
├── 📁 .venv/           ← Your isolated workspace (don't touch)
├── 📁 docs/            ← Documentation (help files)
├── 📁 scripts/         ← Helper scripts (run these)
├── 📁 src/             ← The actual code (don't edit yet)
├── 📁 tests/           ← Test files
├── 📄 .env             ← Your API keys (SECRET!)
├── 📄 .gitignore       ← Tells Git what to ignore
├── 📄 README.md        ← Main documentation
└── 📄 requirements.txt ← List of software to install
```

### What Is the Terminal/PowerShell?

Think of it like a text-based control panel:
- You type commands
- The computer does things
- You see results as text

**Basic commands:**
- `cd foldername` - Change directory (go into a folder)
- `cd ..` - Go up one folder
- `ls` or `dir` - List files in current folder
- `.\script.ps1` - Run a PowerShell script

### What Is Git/GitHub?

**Git:** A system that saves every version of your code
- Like "Save As" but for your entire project
- Can go back to any previous version
- Shows what changed and when

**GitHub:** A website that stores your Git repositories
- Backup in the cloud
- Share with others
- Track issues and features

---

## Next Steps

### Learning Path (Optional)

**Week 1:**
- [ ] Get everything running
- [ ] Explore the interface
- [ ] Place 10 paper trades

**Week 2:**
- [ ] Read the API documentation
- [ ] Try different features
- [ ] Customize your dashboard

**Week 3+:**
- [ ] Learn basic Python (if interested)
- [ ] Modify small settings
- [ ] Build your own strategy

### Resources to Learn More

**Free Python Course:**
- https://www.codecademy.com/learn/learn-python-3
- Takes 25 hours, completely free

**Understanding APIs:**
- https://www.youtube.com/watch?v=GZvSYJDk-us
- 15-minute video explaining APIs

**Financial Master Docs:**
- `API_DOCUMENTATION.md` - All the technical details
- `DEPLOYMENT_GUIDE.md` - How to deploy to the cloud
- `COMPLETE_SETUP_GUIDE.md` - Complete reference

---

## Troubleshooting

### "Script won't run" or "execution policy" error

Run this in PowerShell (as Admin):
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Type `Y` when asked.

### "Python not found"

1. Restart your computer
2. Open PowerShell again
3. Try: `python --version`

If still not working:
- Re-run `.\scripts\complete_setup.ps1`
- Or install Python manually from https://python.org

### "Access denied" errors

Make sure you're running PowerShell as Administrator:
- Press `Windows + X`
- Click "Terminal (Admin)"

### "API key invalid"

Double-check:
- No extra spaces in the keys
- Copied the full key (not cut off)
- Saved the .env file after editing
- Restarted the application after saving

---

## Important Safety Rules

### ✅ DO:
- Start with paper trading (fake money)
- Test everything before using real money
- Keep your API keys secret
- Backup your data regularly
- Learn slowly and ask questions

### ❌ DON'T:
- Trade real money until you're confident
- Share your .env file with anyone
- Rush into automated trading
- Ignore error messages
- Skip the paper trading phase

---

## You Did It! 🎉

If you've made it this far, you have:
- ✅ Installed a complete trading platform
- ✅ Set up free API accounts
- ✅ Running your own financial software
- ✅ Ready to start learning algorithmic trading

**Remember:** This is just the beginning. Take your time, learn the basics, and don't rush into real money trading until you're confident.

**Questions?** Check `docs\TROUBLESHOOTING.md` or run `.\scripts\health_check.ps1`

**Ready to trade?** Start with paper trading for at least 1 month before considering real money.

---

**Last Updated:** May 2026  
**For:** Financial Master v1.0  
**Difficulty:** Beginner (No coding experience required)

