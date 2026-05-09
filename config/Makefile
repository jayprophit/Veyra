# Financial Master - Makefile for Unix-like systems
# Use this on WSL2, macOS, or Linux

.PHONY: help install start stop test clean docker backup

help:
	@echo "Financial Master v2.50.0 - Industry Leader (270/100)"
	@echo ""
	@echo "Setup Commands:"
	@echo "  make install       - Install Python and Node dependencies"
	@echo "  make docker        - Start with Docker Compose"
	@echo ""
	@echo "Development Commands:"
	@echo "  make start         - Start all services (API + Frontend)"
	@echo "  make stop          - Stop all services"
	@echo "  make api           - Start API server only"
	@echo "  make frontend      - Start React frontend only"
	@echo "  make dev-backend   - Start API with auto-reload"
	@echo "  make dev-full      - Start backend + frontend"
	@echo ""
	@echo "Testing & Validation:"
	@echo "  make test          - Run all test suites"
	@echo "  make validate      - Validate system health"
	@echo "  make status        - Check system status"
	@echo ""
	@echo "Maintenance:"
	@echo "  make backup        - Create data backup"
	@echo "  make clean         - Clean temp/cache files"
	@echo "  make logs          - View system logs"
	@echo "  make deploy        - Deploy to production"
	@echo ""
	@echo "URLs:"
	@echo "  Frontend: http://localhost:3000"
	@echo "  API:      http://localhost:8000"
	@echo "  API Docs: http://localhost:8000/docs"
	@echo "  Metrics:  http://localhost:9090"

install:
	pip install -r requirements.txt
	cd frontend && npm install

start:
	@echo "Starting Financial Master..."
	python -m src.backend.app.api.unified_api &
	cd frontend && npm start &
	@echo "API: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"

stop:
	-pkill -f "unified_api.py"
	-pkill -f "node.*react-scripts"
	@echo "All services stopped"

test:
	pytest tests/test_new_modules.py -v
	pytest tests/ -v

validate:
	python scripts/health-check.sh

backup:
	python src/backend/app/cli_tool.py backup create

docker:
	cd config/docker && docker-compose up --build -d

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.log" -mtime +7 -delete 2>/dev/null || true

frontend:
	cd frontend && npm start

api:
	python -m src.backend.app.api.unified_api

scheduler:
	python src/backend/app/task_scheduler.py

scrape:
	python src/backend/app/cli_tool.py scrape yahoo --ticker AAPL

status:
	curl -s http://localhost:8000/api/v1/system/status | python -m json.tool

logs:
	tail -f logs/*.log 2>/dev/null || echo "No log files found"

# Development helpers
dev-backend:
	python -m src.backend.app.api.unified_api --reload

dev-frontend:
	cd frontend && npm start

dev-full: dev-backend dev-frontend

# Production
deploy:
	bash scripts/deploy.sh

# Database
db-upgrade:
	alembic upgrade head

db-downgrade:
	alembic downgrade -1
