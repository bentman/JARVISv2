# Local AI Assistant Makefile

# Variables
PROJECT_NAME = local-ai-assistant
BACKEND_DIR = backend
FRONTEND_DIR = frontend

# Default target
.PHONY: help
help:
	@echo "Local AI Assistant - Development Commands"
	@echo ""
	@echo "Usage:"
	@echo "  make setup              Install all dependencies"
	@echo "  make backend-dev        Start backend in development mode"
	@echo "  make frontend-dev       Start frontend in development mode"
	@echo "  make dev                Start both backend and frontend in development mode"
	@echo "  make backend-build      Build backend Docker image"
	@echo "  make frontend-build     Build frontend desktop application"
	@echo "  make build              Build both backend and frontend"
	@echo "  make test               Run all tests"
	@echo "  make test-backend       Run backend tests"
	@echo "  make test-frontend      Run frontend tests"
	@echo "  make clean              Clean build artifacts"
	@echo "  make help               Show this help message"

# Setup
.PHONY: setup
setup:
	@echo "Setting up development environment..."
	cd $(BACKEND_DIR) && pip install -r requirements.txt
	cd $(FRONTEND_DIR) && npm install
	@echo "Setup complete!"

# Backend development
.PHONY: backend-dev
backend-dev:
	@echo "Starting backend in development mode..."
	cd $(BACKEND_DIR) && uvicorn app.main:app --reload

# Frontend development
.PHONY: frontend-dev
frontend-dev:
	@echo "Starting frontend in development mode..."
	cd $(FRONTEND_DIR) && npm run tauri dev

# Both development
.PHONY: dev
dev:
	@echo "Starting both backend and frontend in development mode..."
	@echo "Starting backend..."
	cd $(BACKEND_DIR) && uvicorn app.main:app --reload &
	@echo "Starting frontend..."
	cd $(FRONTEND_DIR) && npm run tauri dev

# Backend build
.PHONY: backend-build
backend-build:
	@echo "Building backend Docker image..."
	cd $(BACKEND_DIR) && docker build -t $(PROJECT_NAME)-backend .

# Frontend build
.PHONY: frontend-build
frontend-build:
	@echo "Building frontend desktop application..."
	cd $(FRONTEND_DIR) && npm run tauri build

# Both build
.PHONY: build
build: backend-build frontend-build

# Testing
.PHONY: test
test: test-backend test-frontend

.PHONY: test-backend
test-backend:
	@echo "Running backend tests..."
	cd $(BACKEND_DIR) && python -m pytest tests/

.PHONY: test-frontend
test-frontend:
	@echo "Running frontend tests..."
	cd $(FRONTEND_DIR) && npm test

# Clean
.PHONY: clean
clean:
	@echo "Cleaning build artifacts..."
	cd $(BACKEND_DIR) && rm -rf __pycache__ *.pyc
	cd $(FRONTEND_DIR) && rm -rf node_modules/.cache
	@echo "Clean complete!"