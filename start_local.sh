#!/bin/bash

# Financial Master - Complete Setup Script
# Installs dependencies, configures database, starts the application

set -e  # Exit on error

echo "======================================================"
echo "Financial Master - Setup & Startup"
echo "======================================================"
echo ""

# Step 1: Check Python version
echo "1️⃣  Checking Python version..."
python3 --version || (echo "❌ Python 3 not found" && exit 1)
echo "✅ Python 3 found"
echo ""

# Step 2: Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "2️⃣  Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "2️⃣  Virtual environment already exists"
fi
echo ""

# Step 3: Activate virtual environment
echo "3️⃣  Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Step 4: Upgrade pip
echo "4️⃣  Upgrading pip..."
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
echo "✅ Pip upgraded"
echo ""

# Step 5: Install dependencies
echo "5️⃣  Installing Python dependencies (this may take a few minutes)..."
pip install -r requirements.txt > /dev/null 2>&1
echo "✅ Dependencies installed"
echo ""

# Step 6: Create environment file if it doesn't exist
echo "6️⃣  Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cat > .env << 'ENVEOF'
# Application Settings
APP_NAME=Financial Master
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=sqlite:///./financial_master.db
DATABASE_ECHO=False

# Authentication
SECRET_KEY=change-me-in-production-12345
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Keys (Add yours here)
POLYGON_API_KEY=
ALPACA_API_KEY=
FINNHUB_API_KEY=
COINMARKETCAP_API_KEY=
ALPHA_VANTAGE_API_KEY=
FMP_API_KEY=
EODHD_API_TOKEN=

# Feature Flags
ENABLE_TRADING=True
ENABLE_AI_ANALYSIS=True
ENABLE_PAPER_TRADING=True
ENABLE_MOCK_DATA=True

# Logging
LOG_LEVEL=INFO
ENVEOF
    echo "✅ .env file created"
else
    echo "✅ .env file already exists"
fi
echo ""

# Step 7: Initialize database
echo "7️⃣  Initializing database..."
python3 << 'PYEOF'
import asyncio
import sys
sys.path.insert(0, '.')

async def init():
    try:
        from src.backend.core.database import init_db
        await init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️  Database init (non-critical): {e}")

asyncio.run(init())
PYEOF
echo ""

# Step 8: Create logs directory
echo "8️⃣  Creating logs directory..."
mkdir -p logs
echo "✅ Logs directory ready"
echo ""

# Step 9: Show startup information
echo "======================================================"
echo "✅ Setup Complete! Starting Financial Master..."
echo "======================================================"
echo ""
echo "📱 Application will be available at:"
echo "   🔗 http://localhost:8000"
echo "   📚 API Docs: http://localhost:8000/docs"
echo "   🔄 Alternative Docs: http://localhost:8000/redoc"
echo ""
echo "Press Ctrl+C to stop the server"
echo "======================================================"
echo ""

# Step 10: Start the application
python3 -m uvicorn src.backend.main:app --reload --host 0.0.0.0 --port 8000
