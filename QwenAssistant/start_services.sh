#!/bin/bash

# QwenAssistant Service Startup Script
# Starts both backend and frontend services with proper coordination

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
BACKEND_DIR="./backend"
FRONTEND_DIR="./frontend"
BACKEND_PORT=${BACKEND_PORT:-8000}
FRONTEND_PORT=${FRONTEND_PORT:-5173}
BACKEND_HOST=${BACKEND_HOST:-localhost}

print_header() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}  $1"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
}

print_step() {
    echo -e "${YELLOW}→${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

check_prerequisites() {
    print_header "Checking Prerequisites"

    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        return 1
    fi
    print_success "Python 3 found: $(python3 --version)"

    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed"
        return 1
    fi
    print_success "Node.js found: $(node --version)"

    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed"
        return 1
    fi
    print_success "npm found: $(npm --version)"

    # Check Docker (optional)
    if command -v docker &> /dev/null; then
        print_success "Docker found: $(docker --version)"
    else
        print_info "Docker not found (optional, for containerized deployment)"
    fi

    return 0
}

setup_backend() {
    print_header "Setting Up Backend"

    if [ ! -d "$BACKEND_DIR" ]; then
        print_error "Backend directory not found: $BACKEND_DIR"
        return 1
    fi

    cd "$BACKEND_DIR"

    # Check if venv exists
    if [ ! -d ".venv" ]; then
        print_step "Creating Python virtual environment..."
        python3 -m venv .venv
        print_success "Virtual environment created"
    fi

    # Activate venv
    print_step "Activating virtual environment..."
    source .venv/bin/activate || . .venv/Scripts/activate
    print_success "Virtual environment activated"

    # Install dependencies
    if [ -f "requirements.txt" ]; then
        print_step "Installing Python dependencies..."
        pip install -q -r requirements.txt
        print_success "Python dependencies installed"
    else
        print_error "requirements.txt not found"
        return 1
    fi

    cd - > /dev/null
    return 0
}

setup_frontend() {
    print_header "Setting Up Frontend"

    if [ ! -d "$FRONTEND_DIR" ]; then
        print_error "Frontend directory not found: $FRONTEND_DIR"
        return 1
    fi

    cd "$FRONTEND_DIR"

    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_step "Installing npm dependencies..."
        npm install -q
        print_success "npm dependencies installed"
    else
        print_success "npm dependencies already installed"
    fi

    cd - > /dev/null
    return 0
}

wait_for_service() {
    local host=$1
    local port=$2
    local name=$3
    local max_attempts=30
    local attempt=0

    print_step "Waiting for $name to be ready..."

    while [ $attempt -lt $max_attempts ]; do
        if nc -z $host $port 2>/dev/null; then
            print_success "$name is ready"
            return 0
        fi
        ((attempt++))
        sleep 1
    done

    print_error "Timeout waiting for $name"
    return 1
}

start_backend() {
    print_header "Starting Backend"

    cd "$BACKEND_DIR"

    # Activate venv
    if [ -d ".venv" ]; then
        source .venv/bin/activate || . .venv/Scripts/activate
    fi

    # Check if requirements are met
    if ! python3 -c "import fastapi" 2>/dev/null; then
        print_error "Backend dependencies not installed. Run setup first."
        return 1
    fi

    # Run backend in background
    print_step "Starting FastAPI backend on port $BACKEND_PORT..."

    uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT --reload > /tmp/backend.log 2>&1 &
    BACKEND_PID=$!

    echo $BACKEND_PID > /tmp/backend.pid

    # Wait for backend to start
    if ! wait_for_service "localhost" "$BACKEND_PORT" "Backend"; then
        print_error "Backend failed to start. Check /tmp/backend.log"
        kill $BACKEND_PID 2>/dev/null || true
        return 1
    fi

    print_success "Backend started (PID: $BACKEND_PID)"

    # Test health endpoint
    sleep 1
    if curl -s http://localhost:$BACKEND_PORT/api/v1/health/services > /dev/null; then
        print_success "Backend health check passed"
    else
        print_info "Backend health check pending (starting up)"
    fi

    cd - > /dev/null
    return 0
}

start_frontend() {
    print_header "Starting Frontend"

    cd "$FRONTEND_DIR"

    # Check if dependencies are met
    if ! npm list react > /dev/null 2>&1; then
        print_error "Frontend dependencies not installed. Run setup first."
        return 1
    fi

    # Run frontend in background
    print_step "Starting React frontend on port $FRONTEND_PORT..."

    npm run dev > /tmp/frontend.log 2>&1 &
    FRONTEND_PID=$!

    echo $FRONTEND_PID > /tmp/frontend.pid

    # Wait for frontend to start
    sleep 3
    if [ -d "node_modules/.vite" ] || [ -f "dist/index.html" ]; then
        print_success "Frontend started (PID: $FRONTEND_PID)"
    else
        print_info "Frontend starting up..."
    fi

    cd - > /dev/null
    return 0
}

show_status() {
    print_header "Service Status"

    echo ""
    echo "Backend:"
    if curl -s http://localhost:$BACKEND_PORT/api/v1/health/services > /dev/null; then
        print_success "Running on http://localhost:$BACKEND_PORT"
        print_info "API docs: http://localhost:$BACKEND_PORT/docs"
    else
        print_error "Backend not responding"
    fi

    echo ""
    echo "Frontend:"
    if curl -s http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
        print_success "Running on http://localhost:$FRONTEND_PORT"
    else
        print_info "Frontend may still be starting"
    fi

    echo ""
    echo "Logs:"
    print_info "Backend: tail -f /tmp/backend.log"
    print_info "Frontend: tail -f /tmp/frontend.log"

    echo ""
}

stop_services() {
    print_header "Stopping Services"

    # Stop backend
    if [ -f "/tmp/backend.pid" ]; then
        BACKEND_PID=$(cat /tmp/backend.pid)
        if ps -p $BACKEND_PID > /dev/null; then
            kill $BACKEND_PID 2>/dev/null || true
            print_success "Backend stopped"
        fi
        rm /tmp/backend.pid
    fi

    # Stop frontend
    if [ -f "/tmp/frontend.pid" ]; then
        FRONTEND_PID=$(cat /tmp/frontend.pid)
        if ps -p $FRONTEND_PID > /dev/null; then
            kill $FRONTEND_PID 2>/dev/null || true
            print_success "Frontend stopped"
        fi
        rm /tmp/frontend.pid
    fi

    echo ""
}

main() {
    case "${1:-start}" in
        start)
            print_header "QwenAssistant Service Startup"

            # Cleanup on exit
            trap stop_services EXIT

            # Check prerequisites
            if ! check_prerequisites; then
                print_error "Prerequisites check failed"
                return 1
            fi

            echo ""

            # Setup services
            if ! setup_backend; then
                print_error "Backend setup failed"
                return 1
            fi

            echo ""

            if ! setup_frontend; then
                print_error "Frontend setup failed"
                return 1
            fi

            echo ""

            # Start services
            if ! start_backend; then
                print_error "Failed to start backend"
                return 1
            fi

            echo ""

            if ! start_frontend; then
                print_error "Failed to start frontend"
                return 1
            fi

            echo ""
            show_status

            echo ""
            print_header "Services Running"
            print_info "Press Ctrl+C to stop all services"
            echo ""

            # Keep script running
            wait

            ;;
        stop)
            stop_services
            ;;
        status)
            show_status
            ;;
        logs)
            echo "Backend logs:"
            tail -f /tmp/backend.log &
            echo ""
            echo "Frontend logs:"
            tail -f /tmp/frontend.log &
            wait
            ;;
        *)
            echo "Usage: $0 {start|stop|status|logs}"
            echo ""
            echo "Commands:"
            echo "  start   - Start both backend and frontend services"
            echo "  stop    - Stop both services"
            echo "  status  - Show service status"
            echo "  logs    - Show service logs"
            return 1
            ;;
    esac
}

main "$@"
