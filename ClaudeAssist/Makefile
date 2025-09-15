.PHONY: help start stop build clean dev frontend backend logs health check-deps

# Default target
help:
	@echo "🤖 AI Assistant - Available commands:"
	@echo "  make start        - Start all services"
	@echo "  make stop         - Stop all services" 
	@echo "  make build        - Build all components"
	@echo "  make clean        - Clean up containers and volumes"
	@echo "  make dev          - Start development environment"
	@echo "  make frontend     - Build frontend only"
	@echo "  make backend      - Build backend only"
	@echo "  make logs         - Show service logs"
	@echo "  make health       - Check service health"
	@echo "  make check-deps   - Check dependencies"

# Check if GPU is available
GPU_AVAILABLE := $(shell nvidia-smi > /dev/null 2>&1 && echo "true" || echo "false")
PROFILE := $(if $(filter true,$(GPU_AVAILABLE)),gpu,cpu-only)

start: check-deps
	@echo "🚀 Starting AI Assistant (Profile: $(PROFILE))"
	@mkdir -p backend/data ollama_data
	@docker-compose --profile $(PROFILE) up -d
	@echo "⏳ Waiting for services..."
	@sleep 5
	@$(MAKE) health
	@echo "✅ AI Assistant started successfully!"

stop:
	@echo "🛑 Stopping AI Assistant"
	@docker-compose --profile $(PROFILE) down

build: backend frontend

backend:
	@echo "🔧 Building backend"
	@cd backend && cargo build --release
	@docker build -t ai-assistant-backend backend/

frontend: 
	@echo "🖥️  Building frontend"
	@cd frontend && npm install
	@cd frontend && npm run build
	@cd frontend && npm run tauri build

dev:
	@echo "🔧 Starting development environment"
	@$(MAKE) start
	@echo "🖥️  Start frontend with: cd frontend && npm run tauri dev"

clean:
	@echo "🧹 Cleaning up"
	@docker-compose --profile $(PROFILE) down -v
	@docker system prune -f
	@rm -rf backend/target frontend/dist frontend/node_modules
	@rm -rf backend/data ollama_data

logs:
	@docker-compose --profile $(PROFILE) logs -f

health:
	@echo "🔍 Checking service health..."
	@timeout 30s sh -c 'until curl -s http://localhost:8080/health > /dev/null; do sleep 1; done' || (echo "❌ Backend health check failed" && exit 1)
	@echo "✅ All services healthy"

check-deps:
	@echo "🔍 Checking dependencies..."
	@command -v docker >/dev/null 2>&1 || (echo "❌ Docker not found" && exit 1)
	@command -v docker-compose >/dev/null 2>&1 || (echo "❌ Docker Compose not found" && exit 1)
	@docker info >/dev/null 2>&1 || (echo "❌ Docker not running" && exit 1)
	@echo "✅ Dependencies OK"

# Development helpers
backend-dev:
	@cd backend && cargo run

frontend-dev:
	@cd frontend && npm run dev

install-frontend-deps:
	@cd frontend && npm install

install-backend-deps:
	@cd backend && cargo fetch

# Testing
test:
	@cd backend && cargo test
	@cd frontend && npm test

# Docker helpers
docker-build:
	@docker-compose build

docker-pull:
	@docker-compose pull

# Model management  
pull-models:
	@echo "📥 Pulling AI models..."
	@docker exec ai_assistant_ollama ollama pull phi3:3.8b
	@docker exec ai_assistant_ollama ollama pull gemma2:9b
	@docker exec ai_assistant_ollama ollama pull deepseek-coder:6.7b

list-models:
	@docker exec ai_assistant_ollama ollama list