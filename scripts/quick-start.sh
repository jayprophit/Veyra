#!/bin/bash
# Financial Master - Quick Start Script
# =======================================
# One-command setup for development

set -e

echo "🚀 Financial Master v2.50.0 - Quick Start"
echo "=========================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11+"
    exit 1
fi

# Check Node
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node 18+"
    exit 1
fi

# Setup environment if needed
if [ ! -f .env ]; then
    echo "📄 Creating .env from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your API keys"
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt --quiet

echo "📦 Installing Node dependencies..."
cd frontend && npm install --silent && cd ..

# Start services
echo "🏁 Starting services..."
echo "   API will run on http://localhost:8000"
echo "   Frontend will run on http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Trap to kill background processes on exit
trap "echo ''; echo '🛑 Stopping services...'; kill 0" EXIT

# Start backend
python -m src.backend.app.api.unified_api &

# Wait for API to be ready
sleep 3

# Start frontend
cd frontend && npm start &

# Wait for all background jobs
wait
