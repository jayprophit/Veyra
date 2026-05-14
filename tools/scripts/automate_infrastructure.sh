#!/bin/bash
# Veyra - Infrastructure Automation (Linux/WSL)
# =========================================================
# Automates Docker and Ollama setup for Linux/WSL environments
# Run: ./scripts/automate_infrastructure.sh

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# Helper Functions
# ============================================================================

print_status() {
    local message=$1
    local status=$2
    case $status in
        success) echo -e "${GREEN}✓${NC} $message" ;;
        error) echo -e "${RED}✗${NC} $message" ;;
        warning) echo -e "${YELLOW}⚠${NC} $message" ;;
        info) echo -e "${BLUE}ℹ${NC} $message" ;;
        *) echo "  $message" ;;
    esac
}

# ============================================================================
# Docker Management
# ============================================================================

check_docker() {
    if command -v docker &> /dev/null; then
        if docker info &> /dev/null; then
            return 0
        fi
    fi
    return 1
}

start_docker() {
    print_status "Checking Docker..." "info"
    
    if check_docker; then
        print_status "Docker is running" "success"
        return 0
    fi
    
    # Try to start Docker service
    print_status "Attempting to start Docker..." "info"
    
    if command -v systemctl &> /dev/null; then
        sudo systemctl start docker 2>/dev/null || true
    elif command -v service &> /dev/null; then
        sudo service docker start 2>/dev/null || true
    fi
    
    sleep 3
    
    if check_docker; then
        print_status "Docker started successfully" "success"
        return 0
    else
        print_status "Docker is not running. Please start Docker manually." "error"
        return 1
    fi
}

install_docker() {
    print_status "Installing Docker..." "info"
    
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    
    print_status "Docker installed. Please log out and back in for group changes." "warning"
}

# ============================================================================
# Ollama Management
# ============================================================================

check_ollama() {
    if curl -s http://localhost:11434/api/tags &> /dev/null; then
        return 0
    fi
    return 1
}

install_ollama() {
    print_status "Installing Ollama..." "info"
    curl -fsSL https://ollama.com/install.sh | sh
    print_status "Ollama installed" "success"
}

start_ollama() {
    print_status "Checking Ollama..." "info"
    
    if check_ollama; then
        print_status "Ollama is already running on localhost:11434" "success"
        return 0
    fi
    
    # Check if Ollama is installed
    if ! command -v ollama &> /dev/null; then
        install_ollama
    fi
    
    print_status "Starting Ollama..." "info"
    nohup ollama serve > /tmp/ollama.log 2>&1 &
    sleep 3
    
    if check_ollama; then
        print_status "Ollama started successfully" "success"
        
        # Pull recommended models
        pull_models
        return 0
    else
        print_status "Ollama failed to start" "error"
        return 1
    fi
}

pull_models() {
    print_status "Pulling recommended models..." "info"
    
    local models=("llama3.2:3b" "llama3.1:8b" "mistral:7b")
    
    for model in "${models[@]}"; do
        echo "  Pulling $model..."
        ollama pull "$model" &>/dev/null || print_status "Failed to pull $model" "warning"
    done
    
    print_status "Models pulled successfully" "success"
}

list_models() {
    if check_ollama; then
        echo ""
        echo "Installed Ollama Models:"
        curl -s http://localhost:11434/api/tags | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for m in data.get('models', []):
        print(f'  - {m[\"name\"]} ({m.get(\"details\", {}).get(\"parameter_size\", \"unknown\")})')
except:
    print('  No models found or Ollama not ready')
" 2>/dev/null || echo "  Unable to list models"
    fi
}

# ============================================================================
# System Optimization
# ============================================================================

optimize_for_ollama() {
    print_status "Optimizing system for Ollama..." "info"
    
    # Create swap if needed
    if ! swapon --show &> /dev/null; then
        print_status "Creating 8GB swap file..." "info"
        sudo fallocate -l 8G /swapfile 2>/dev/null || sudo dd if=/dev/zero of=/swapfile bs=1G count=8
        sudo chmod 600 /swapfile
        sudo mkswap /swapfile
        sudo swapon /swapfile
        echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    fi
    
    # Increase file descriptors
    echo '* soft nofile 65536' | sudo tee -a /etc/security/limits.conf
    echo '* hard nofile 65536' | sudo tee -a /etc/security/limits.conf
    
    print_status "System optimized" "success"
}

# ============================================================================
# Veyra Stack
# ============================================================================

start_financial_master() {
    print_status "Starting Veyra..." "info"
    
    local project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    cd "$project_root"
    
    # Create .env if needed
    if [ ! -f .env ] && [ -f .env.example ]; then
        cp .env.example .env
        print_status "Created .env from template" "success"
    fi
    
    # Start Docker Compose
    if [ -f docker-compose.yml ]; then
        docker-compose up --build -d
        print_status "Veyra stack started" "success"
        print_status "API: http://localhost:8000" "info"
        print_status "Frontend: http://localhost:3000" "info"
    else
        # Start native Python
        python3 -m src.backend.app.api.unified_api &
        print_status "Veyra API started (native)" "success"
    fi
}

stop_all() {
    print_status "Stopping all services..." "info"
    
    # Stop Docker
    local project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    cd "$project_root"
    docker-compose down 2>/dev/null || true
    
    # Stop Ollama
    pkill ollama 2>/dev/null || true
    
    print_status "All services stopped" "success"
}

show_status() {
    echo ""
    echo "========================================"
    echo "  Veyra - Infrastructure Status"
    echo "========================================"
    echo ""
    
    # Docker
    if check_docker; then
        print_status "Docker: Running" "success"
    else
        print_status "Docker: Not running" "error"
    fi
    
    # Ollama
    if check_ollama; then
        print_status "Ollama: Running on localhost:11434" "success"
        list_models
    else
        print_status "Ollama: Not running" "warning"
    fi
    
    # Containers
    if check_docker; then
        echo ""
        echo "Docker Containers:"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null | grep veyra || echo "  No Veyra containers"
    fi
    
    echo ""
}

show_help() {
    cat << EOF

Veyra - Infrastructure Automation (Linux/WSL)
========================================================

Usage: ./scripts/automate_infrastructure.sh [COMMAND]

Commands:
    start       Start all services (Docker + Ollama + Stack)
    stop        Stop all services
    status      Show infrastructure status
    setup       Full setup with optimization
    ollama      Start/manage Ollama only
    docker      Start/manage Docker only
    help        Show this help message

Examples:
    ./scripts/automate_infrastructure.sh start
    ./scripts/automate_infrastructure.sh status
    ./scripts/automate_infrastructure.sh setup

EOF
}

# ============================================================================
# Main
# ============================================================================

main() {
    local command=$1
    
    case $command in
        start)
            echo "🚀 Starting Veyra Infrastructure..."
            echo ""
            start_docker
            start_ollama
            start_financial_master
            echo ""
            show_status
            ;;
        stop)
            stop_all
            ;;
        status)
            show_status
            ;;
        setup)
            echo "🔧 Full Setup with Optimization..."
            echo ""
            optimize_for_ollama
            start_docker || install_docker
            start_ollama
            start_financial_master
            echo ""
            show_status
            ;;
        ollama)
            start_ollama
            list_models
            ;;
        docker)
            start_docker || install_docker
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            show_help
            ;;
    esac
}

main "$@"
