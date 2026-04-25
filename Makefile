# Financial Master - Makefile for Unix-like systems
# Use this on WSL2, macOS, or Linux

.PHONY: help install start stop test clean docker backup

help:
	@echo "Financial Master - Available Commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make start      - Start all services"
	@echo "  make stop       - Stop all services"
	@echo "  make test       - Run tests"
	@echo "  make validate   - Validate setup"
	@echo "  make backup     - Create backup"
	@echo "  make docker     - Build and run Docker"
	@echo "  make clean      - Clean temp files"
	@echo "  make dashboard  - Start dashboard only"
	@echo "  make api        - Start API only"

install:
	pip install -r requirements.txt
	cd dashboard && npm install

start:
	python main.py &
	cd dashboard && npm run dev &

stop:
	-pkill -f "19_API_Server.py"
	-pkill -f "15_WebSocket_Real_Time_Feeds.py"
	-pkill -f "main.py"

test:
	python 26_Integration_Tests.py

validate:
	python VALIDATE_SETUP.py

backup:
	python 35_CLI_Tool.py backup create

docker:
	docker-compose up --build -d

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.log" -mtime +7 -delete 2>/dev/null || true

dashboard:
	cd dashboard && npm run dev

api:
	python 19_API_Server.py

scheduler:
	python 32_Task_Scheduler.py

scrape:
	python 35_CLI_Tool.py scrape yahoo --ticker VUAG

status:
	python 35_CLI_Tool.py status
