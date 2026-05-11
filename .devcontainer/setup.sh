#!/bin/bash
set -e

echo "🚀 Veyra Codespaces Setup"
echo "========================"

# Update system packages
echo "📦 Updating system packages..."
apt-get update -q && apt-get upgrade -y -q

# Install system dependencies
echo "📦 Installing system dependencies..."
apt-get install -y -q \
    build-essential \
    postgresql-client \
    redis-tools \
    curl \
    wget \
    git-flow \
    jq

# Setup Python virtual environment
echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip setuptools wheel -q

# Install Python dependencies
echo "📦 Installing Python dependencies..."
if [ -f requirements.txt ]; then
    pip install -r requirements.txt -q
fi

if [ -f requirements_ai.txt ]; then
    pip install -r requirements_ai.txt -q
fi

if [ -f requirements_opensource.txt ]; then
    pip install -r requirements_opensource.txt -q
fi

# Install additional development tools
echo "📦 Installing development tools..."
pip install -q \
    pytest \
    pytest-cov \
    black \
    flake8 \
    isort \
    mypy \
    ipython \
    jupyter \
    notebook \
    uvicorn[standard] \
    fastapi \
    flask \
    flask-cors

# Setup Node.js dependencies
echo "📦 Setting up Node.js dependencies..."
if [ -f frontend/package.json ]; then
    cd frontend
    npm install -q
    cd ..
fi

if [ -f mobile/veyra_app/pubspec.yaml ]; then
    cd mobile/veyra_app
    flutter pub get -q
    cd ../..
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/logs
mkdir -p data/cache
mkdir -p data/exports

# Set permissions
chmod +x scripts/*.sh 2>/dev/null || true
chmod +x scripts/deployment/*.sh 2>/dev/null || true
chmod +x scripts/setup/*.sh 2>/dev/null || true

echo ""
echo "✅ Installation Complete!"
echo ""
echo "📊 Veyra Platform Ready:"
echo "  • 1025 Modules"
echo "  • 1063 API Endpoints"
echo "  • 18 Service Types"
echo "  • 5 Integrations"
echo ""
echo "🚀 Quick Start Commands:"
echo "  python3 src/backend/app/veyra_demo_server.py"
echo "  cd frontend && npm start"
echo "  pytest tests/"
echo ""
