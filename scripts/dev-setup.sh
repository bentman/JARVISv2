#!/usr/bin/env bash
# Sets up the development environment for the Local AI Assistant project using the development Docker configuration.

set -euo pipefail

# Default values
ENVIRONMENT="dev"
SKIP_MODELS=false
SKIP_FRONTEND=false
MODELS_ENVIRONMENT=""
MODELS_DIR="models"

# Function to display usage
usage() {
    echo "Usage: $0 [-e environment] [-s skip_models] [-f skip_frontend] [-m models_env] [-d models_dir]"
    echo "  -e environment: Specify environment (dev or prod). Default: dev"
    echo "  -s skip_models: Skip model download step. Default: false (downloads models)"
    echo "  -f skip_frontend: Skip frontend setup step. Default: false (sets up frontend)"
    echo "  -m models_env: Specify which models to download (dev or prod). Default: same as environment"
    echo "  -d models_dir: Directory to download models to. Default: models"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Setup dev environment with all components"
    echo "  $0 -s                                 # Setup dev environment without downloading models"
    echo "  $0 -e prod -m dev                   # Setup production environment but use dev models"
    exit 1
}

# Parse command line options
while getopts "e:s:f:m:d:h" opt; do
    case $opt in
        e)
            if [[ "$OPTARG" == "dev" || "$OPTARG" == "prod" ]]; then
                ENVIRONMENT="$OPTARG"
            else
                echo "Error: Environment must be 'dev' or 'prod'"
                usage
            fi
            ;;
        s)
            SKIP_MODELS=true
            ;;
        f)
            SKIP_FRONTEND=true
            ;;
        m)
            if [[ "$OPTARG" == "dev" || "$OPTARG" == "prod" ]]; then
                MODELS_ENVIRONMENT="$OPTARG"
            else
                echo "Error: Models environment must be 'dev' or 'prod'"
                usage
            fi
            ;;
        d)
            MODELS_DIR="$OPTARG"
            ;;
        h)
            usage
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            usage
            ;;
    esac
done

# Set default ModelsEnvironment to match Environment if not specified
if [[ -z "$MODELS_ENVIRONMENT" ]]; then
    MODELS_ENVIRONMENT="$ENVIRONMENT"
fi

echo "Setting up Local AI Assistant development environment..."
echo "Environment: $ENVIRONMENT"
echo "Models Environment: $MODELS_ENVIRONMENT"

# Check prerequisites
echo
echo "Checking prerequisites..." >&2

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed or not in PATH. Please install Docker Desktop." >&2
    exit 1
fi
echo "✓ Docker: $(docker --version)" >&2

# Check for Node.js (if not skipping frontend)
if [[ "$SKIP_FRONTEND" == "false" ]]; then
    if ! command -v node &> /dev/null; then
        echo "Error: Node.js is not installed or not in PATH. Please install Node.js." >&2
        exit 1
    fi
    if ! command -v npm &> /dev/null; then
        echo "Error: npm is not installed or not in PATH. Please install Node.js." >&2
        exit 1
    fi
    echo "✓ Node.js: $(node --version)" >&2
    echo "✓ npm: $(npm --version)" >&2
fi

# Check for Python (for model verification and scripts)
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH. Please install Python 3.11+." >&2
    exit 1
fi
echo "✓ Python: $(python3 --version)" >&2

# Step 1: Download models (if not skipped)
if [[ "$SKIP_MODELS" == "false" ]]; then
    echo
    echo "Step 1: Downloading models for $MODELS_ENVIRONMENT environment..." >&2
    ./scripts/get-models.sh -e "$MODELS_ENVIRONMENT" -d "$MODELS_DIR"
    echo "Models download completed." >&2
fi

# Step 2: Start development services
echo "Step 2: Starting development services..." >&2

# Select compose file based on environment
if [[ "$ENVIRONMENT" == "dev" ]]; then
    COMPOSE_FILE="docker-compose.dev.yml"
else
    COMPOSE_FILE="docker-compose.yml"
fi
echo "Using compose file: $COMPOSE_FILE" >&2

# Start services using appropriate compose file
if ! docker compose -f "$COMPOSE_FILE" up -d; then
    echo "Error: Failed to start services with $COMPOSE_FILE" >&2
    exit 1
fi
echo "Services started using $COMPOSE_FILE" >&2

# Step 3: Set up frontend (if not skipped)
if [[ "$SKIP_FRONTEND" == "false" ]]; then
    echo "Step 3: Setting up frontend development environment..." >&2
    
    if [[ ! -d "frontend" ]]; then
        echo "Error: Frontend directory not found. Please ensure you're running this from the project root." >&2
        exit 1
    fi
    
    cd frontend
    
    # Install frontend dependencies if node_modules doesn't exist
    if [[ ! -d "node_modules" ]]; then
        echo "Installing frontend dependencies..." >&2
        npm install
    else
        echo "Frontend dependencies already installed, skipping." >&2
    fi
    
    echo "Frontend setup completed." >&2
    cd ..
fi

# Wait for backend to be ready
echo
echo "Waiting for backend services to be ready..." >&2
sleep 10

MAX_RETRIES=30
RETRY_COUNT=0
SERVICES_READY=false

while [[ $RETRY_COUNT -lt $MAX_RETRIES && "$SERVICES_READY" == "false" ]]; do
    if curl -f http://localhost:8000/api/v1/health/services >/dev/null 2>&1; then
        SERVICES_READY=true
        echo "Backend services are ready!" >&2
        break
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "Waiting for backend services... (attempt $RETRY_COUNT/$MAX_RETRIES)" >&2
    sleep 10
done

if [[ "$SERVICES_READY" == "false" ]]; then
    echo "Error: Backend services failed to become ready within timeout" >&2
    docker compose -f "$COMPOSE_FILE" logs backend || true
    exit 1
fi

echo
echo "Development environment setup completed successfully!" >&2
echo "Environment: $ENVIRONMENT" >&2
echo "Models: $MODELS_ENVIRONMENT" >&2

if [[ "$ENVIRONMENT" == "dev" ]]; then
    echo
    echo "For development, you can now:" >&2
    echo "  - Access the UI at http://localhost:5173" >&2
    echo "  - Access the API at http://localhost:8000" >&2
    echo "  - Run tests with: cd backend && python -m pytest" >&2
    echo "  - Start frontend dev server: cd frontend && npm run dev" >&2
else
    echo
    echo "For production simulation, services are running." >&2
    echo "  - API is available at http://localhost:8000" >&2
    echo "  - Check health at: http://localhost:8000/api/v1/health/services" >&2
fi

echo
echo "To stop services, run: docker compose -f $COMPOSE_FILE down" >&2
