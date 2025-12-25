# Local AI Assistant Makefile

# Variables
PROJECT_NAME = jarvisv2
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
	# Create virtual environment for backend
	python3 -m venv $(BACKEND_DIR)/.venv
	# Activate virtual environment and install backend dependencies
	# On Windows: $(BACKEND_DIR)\\.venv\\Scripts\\activate.bat && pip install -r $(BACKEND_DIR)/requirements.txt
	# On Unix: source $(BACKEND_DIR)/.venv/bin/activate && pip install -r $(BACKEND_DIR)/requirements.txt
	if [ -f $(BACKEND_DIR)/.venv/bin/activate ]; then \
		source $(BACKEND_DIR)/.venv/bin/activate && pip install -r $(BACKEND_DIR)/requirements.txt; \
	else \
		$(BACKEND_DIR)\\.venv\\Scripts\\activate.bat && pip install -r $(BACKEND_DIR)/requirements.txt; \
	fi
	cd $(FRONTEND_DIR) && npm install
	@echo "Setup complete!"

# Backend development
.PHONY: backend-dev
backend-dev:
	@echo "Starting backend in development mode..."
	# Activate virtual environment and start backend server
	# On Windows: $(BACKEND_DIR)\.venv\Scripts\activate.bat && uvicorn app.main:app --reload
	# On Unix: source $(BACKEND_DIR)/.venv/bin/activate && uvicorn app.main:app --reload
	if [ -f $(BACKEND_DIR)/.venv/bin/activate ]; then \
		source $(BACKEND_DIR)/.venv/bin/activate && uvicorn app.main:app --reload; \
	else \
		$(BACKEND_DIR)\.venv\Scripts\activate.bat && uvicorn app.main:app --reload; \
	fi

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
	# Activate virtual environment and start backend server
	# On Windows: $(BACKEND_DIR)\.venv\Scripts\activate.bat && uvicorn app.main:app --reload &
	# On Unix: source $(BACKEND_DIR)/.venv/bin/activate && uvicorn app.main:app --reload &
	if [ -f $(BACKEND_DIR)/.venv/bin/activate ]; then \
		source $(BACKEND_DIR)/.venv/bin/activate && uvicorn app.main:app --reload & \
	else \
		$(BACKEND_DIR)\.venv\Scripts\activate.bat && uvicorn app.main:app --reload & \
	fi
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
	# Activate virtual environment and run backend tests
	# On Windows: $(BACKEND_DIR)\.venv\Scripts\activate.bat && python -m pytest tests/
	# On Unix: source $(BACKEND_DIR)/.venv/bin/activate && python -m pytest tests/
	if [ -f $(BACKEND_DIR)/.venv/bin/activate ]; then \
		source $(BACKEND_DIR)/.venv/bin/activate && python -m pytest tests/; \
	else \
		$(BACKEND_DIR)\.venv\Scripts\activate.bat && python -m pytest tests/; \
	fi

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
