#!/usr/bin/env bash
# Sets up the Local AI Assistant development or production environment based on specified parameters.

set -euo pipefail

# Default values
ENVIRONMENT="dev"
SKIP_MODELS=false
SKIP_DEPS=false
SKIP_SERVICES=false
MODELS_DIR="models"
MODELS_ENVIRONMENT=""

# Function to display usage
usage() {
    echo "Usage: $0 [-e environment] [-s skip_models] [-d skip_deps] [-v skip_services] [-m models_dir] [-n models_env]"
    echo "  -e environment: Specify environment (dev or prod). Default: dev"
    echo "  -s skip_models: Skip model download step. Default: false"
    echo "  -d skip_deps: Skip dependency installation step. Default: false"
    echo "  -v skip_services: Skip service startup step. Default: false"
    echo "  -m models_dir: Directory to download models to. Default: models"
    echo "  -n models_env: Models environment (dev or prod). Default: same as environment"
    echo ""
    echo "Examples:"
    echo "  $0 -e dev                                    # Setup development environment"
    echo "  $0 -e prod -n dev                           # Setup production env with dev models"
    echo "  $0 -e dev -s                                  # Dev env without downloading models"
    exit 1
}

# Parse command line options
while getopts "e:s:d:v:m:n:h" opt; do
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
        d)
            SKIP_DEPS=true
            ;;
        v)
            SKIP_SERVICES=true
            ;;
        m)
            MODELS_DIR="$OPTARG"
            ;;
        n)
            if [[ "$OPTARG" == "dev" || "$OPTARG" == "prod" ]]; then
                MODELS_ENVIRONMENT="$OPTARG"
            else
                echo "Error: Models environment must be 'dev' or 'prod'"
                usage
            fi
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

echo "Setting up Local AI Assistant environment: $ENVIRONMENT"
echo "Models environment: $MODELS_ENVIRONMENT"

# Check prerequisites
echo
echo "Checking prerequisites..."
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed or not in PATH. Please install Docker Desktop."
    exit 1
fi
echo "✓ Docker: $(docker --version)"

if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed or not in PATH. Please install Node.js."
    exit 1
fi
echo "✓ Node.js: $(node --version)"

if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed or not in PATH. Please install Node.js."
    exit 1
fi
echo "✓ npm: $(npm --version)"

if [[ "$SKIP_DEPS" == "false" ]]; then
    if ! command -v python3 &> /dev/null; then
        echo "Error: Python 3 is not installed or not in PATH. Please install Python 3.11+."
        exit 1
    fi
    echo "✓ Python: $(python3 --version)"
fi

# Step 1: Download models (if not skipped)
if [[ "$SKIP_MODELS" == "false" ]]; then
    echo
    echo "Step 1: Downloading models..."
    ./scripts/get-models.sh -e "$MODELS_ENVIRONMENT" -d "$MODELS_DIR"
    echo "Models download completed."
fi

# Step 2: Install dependencies (if not skipped)
if [[ "$SKIP_DEPS" == "false" ]]; then
    echo
    echo "Step 2: Installing dependencies..."
    
    # Create virtual environment if it doesn't exist
    if [[ ! -d "backend/.venv" ]]; then
        echo "Creating Python virtual environment..."
        python3 -m venv backend/.venv
    fi
    
    # Activate virtual environment and install backend dependencies
    echo "Installing backend dependencies..."
    source backend/.venv/bin/activate
    pip install -r backend/requirements.txt
    
    # Install frontend dependencies
    if [[ ! -d "frontend/node_modules" ]]; then
        echo "Installing frontend dependencies..."
        cd frontend
        npm install
        cd ..
    fi
    echo "Dependency installation completed."
fi

# Step 3: Start services (if not skipped)
if [[ "$SKIP_SERVICES" == "false" ]]; then
    echo
    echo "Step 3: Starting services..."
    
    # Select compose file based on environment
    if [[ "$ENVIRONMENT" == "dev" ]]; then
        COMPOSE_FILE="docker-compose.dev.yml"
    else
        COMPOSE_FILE="docker-compose.yml"
    fi
    echo "Using compose file: $COMPOSE_FILE"
    
    # Start services using appropriate compose file
    docker compose -f "$COMPOSE_FILE" up -d
    
    echo "Services started using $COMPOSE_FILE"
fi

echo
echo "Setup completed for $ENVIRONMENT environment!"
echo "Environment: $ENVIRONMENT"
echo "Models: $MODELS_ENVIRONMENT"

if [[ "$ENVIRONMENT" == "dev" ]]; then
    echo
    echo "For development, you can now:"
    echo "  - Access the UI at http://localhost:5173"
    echo "  - Access the API at http://localhost:8000"
    echo "  - Run tests with: cd backend && python -m pytest"
else
    echo
    echo "For production, services are running."
    echo "  - API is available at http://localhost:8000"
    echo "  - Check health at: http://localhost:8000/api/v1/health/services"
fi
