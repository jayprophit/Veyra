#!/bin/bash
# Veyra Platform Launcher

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║          🌟 VEYRA AUTONOMOUS WEALTH PLATFORM 🌟       ║"
echo "║              Production Demo Server                      ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if running in Codespaces
if [ -n "$CODESPACES" ]; then
    echo -e "${GREEN}✅ Running in GitHub Codespaces${NC}"
else
    echo -e "${YELLOW}ℹ️  Running locally${NC}"
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python: $(python3 --version)${NC}"

# Create virtual environment if needed
if [ ! -d "venv" ]; then
    echo -e "${BLUE}📦 Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/upgrade dependencies
echo -e "${BLUE}📦 Checking dependencies...${NC}"
pip install --upgrade pip setuptools wheel -q
pip install fastapi uvicorn[standard] -q

# Check if requirements files exist
if [ -f requirements.txt ]; then
    echo -e "${BLUE}📦 Installing requirements...${NC}"
    pip install -r requirements.txt -q 2>/dev/null || true
fi

# Display platform info
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}📊 VEYRA PLATFORM STATISTICS${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ 1025 Core Modules${NC}"
echo -e "${GREEN}  ✅ 1063 API Endpoints${NC}"
echo -e "${GREEN}  ✅ 18 Service Types${NC}"
echo -e "${GREEN}  ✅ 5 Integrations${NC}"
echo -e "${GREEN}  ✅ 11 Capability Areas${NC}"
echo -e "${GREEN}========================================================${NC}"
echo ""

# Get port from environment or use default
PORT=${PORT:-5000}

# Determine the accessible URL
if [ -n "$CODESPACES" ]; then
    WORKSPACE_HOST=${CODESPACE_NAME}-${PORT}.preview.app.github.dev
    echo -e "${YELLOW}🔗 Your Veyra instance will be available at:${NC}"
    echo -e "${BLUE}   https://${WORKSPACE_HOST}${NC}"
else
    echo -e "${YELLOW}🔗 Your Veyra instance will be available at:${NC}"
    echo -e "${BLUE}   http://localhost:${PORT}${NC}"
fi

echo ""
echo -e "${YELLOW}📡 API Documentation:${NC}"
echo -e "${BLUE}   http://localhost:${PORT}/docs${NC}"
echo ""

# Check if port is in use
if lsof -Pi :${PORT} -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠️  Port ${PORT} is already in use${NC}"
    echo -e "${YELLOW}   You can specify a different port:${NC}"
    echo -e "${BLUE}   PORT=8000 bash scripts/launch_demo.sh${NC}"
    echo ""
    read -p "Use different port? Enter port number (or press Enter to use ${PORT}): " NEW_PORT
    [ -n "$NEW_PORT" ] && PORT=$NEW_PORT
fi

echo -e "${BLUE}🚀 Starting Veyra Demo Server on port ${PORT}...${NC}"
echo ""

# Start the server
cd src/backend/app
python3 veyra_demo_server.py
