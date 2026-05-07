#!/bin/bash
# Setup Local Development Script
echo "Setting up local development environment..."

# Start local services
docker-compose up -d postgres redis ollama

# Wait for services to start
sleep 10

# Run database migrations
npm run migrate

# Seed database
npm run seed

# Start application
npm run dev

echo "Local development environment started:"
echo "- Database: postgresql://localhost:5432/financial_master"
echo "- Redis: redis://localhost:6379"
echo "- Ollama: http://localhost:11434"
echo "- Application: http://localhost:8000"
