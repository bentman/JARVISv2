#!/usr/bin/env bash
# Main script for the Local AI Assistant project that consolidates all essential functionality.

set -euo pipefail

# Default values
COMMAND=""
ENVIRONMENT="dev"
SKIP_MODELS=false
SKIP_DEPS=false
SKIP_SERVICES=false
MODELS_DIR="models"
MODELS_ENVIRONMENT=""

# Function to display usage
usage() {
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo " setup     - Set up dev/prod environment"
    echo "  models    - Download models for dev/prod"
    echo "  dev       - Start development environment"
    echo "  dev-setup - Setup and start dev environment (setup + dev)"
    echo "  deploy    - Deploy to production"
    echo "  test      - Run tests"
    echo "  verify    - Verify models and integrity"
    echo "  cleanup   - Clean development artifacts"
    echo "  voice-test - Test voice functionality"
    echo ""
    echo "Options:"
    echo "  -e environment: Specify environment (dev or prod). Default: dev"
    echo "  -s skip_models: Skip model download step. Default: false"
    echo "  -d skip_deps: Skip dependency installation step. Default: false"
    echo "  -v skip_services: Skip service startup step. Default: false"
    echo "  -m models_dir: Directory to download models to. Default: models"
    echo "  -n models_env: Models environment (dev or prod). Default: same as environment"
    echo ""
    echo "Examples:"
    echo "  $0 setup -e dev                    # Setup development environment"
    echo "  $0 models -e prod                 # Download production models"
    echo "  $0 dev                            # Start development environment"
    echo "  $0 dev-setup                      # Setup and start dev environment"
    echo "  $0 deploy -e prod                 # Deploy to production"
    exit 1
}

# Parse command line options
if [ $# -eq 0 ]; then
    usage
fi

COMMAND=$1
shift

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

echo "Executing command: $COMMAND"

case "$COMMAND" in
    "setup")
        echo "Running setup for $ENVIRONMENT environment..."
        
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
            
            # Create models directory if it doesn't exist
            mkdir -p "$MODELS_DIR"
            cd "$MODELS_DIR"

            # Determine model URLs based on environment
            if [[ "$MODELS_ENVIRONMENT" == "dev" ]]; then
                echo "Downloading development models (smaller, faster)..."
                
                # TinyLlama 1.1B Chat (Q2_K - smallest functional chat for dev)
                TLL_URL="https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q2_K.gguf?download=true"
                TLL_FILE="tinyllama-1.1b-chat-v1.0.Q2_K.gguf"
            else
                echo "Downloading production models (optimized for performance)..."
                
                # TinyLlama 1.1B Chat (Q4_K_M - balanced for production)
                TLL_URL="https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf?download=true"
                TLL_FILE="tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
            fi

            # Download LLM model if not present
            if [[ ! -f "$TLL_FILE" ]]; then
                echo "Downloading $TLL_FILE ..."
                curl -L "$TLL_URL" -o "$TLL_FILE"
                echo "Successfully downloaded $TLL_FILE"
            else
                echo "$TLL_FILE already exists, skipping download."
            fi

            # Piper English voice (common for both environments)
            PIPER_URL="https://github.com/rhasspy/piper-voices/releases/download/en_US-amy-low/en_US-amy-low.onnx"
            PIPER_FILE="en_US-amy-low.onnx"
            PIPER_JSON_URL="https://github.com/rhasspy/piper-voices/releases/download/en_US-amy-low/en_US-amy-low.onnx.json"
            PIPER_JSON_FILE="en_US-amy-low.onnx.json"

            if [[ ! -f "$PIPER_FILE" ]]; then
                echo "Downloading $PIPER_FILE (TTS)..."
                curl -L "$PIPER_URL" -o "$PIPER_FILE"
                echo "Successfully downloaded $PIPER_FILE"
            else
                echo "$PIPER_FILE already exists, skipping download."
            fi

            if [[ ! -f "$PIPER_JSON_FILE" ]]; then
                echo "Downloading $PIPER_JSON_FILE (TTS Config)..."
                curl -L "$PIPER_JSON_URL" -o "$PIPER_JSON_FILE"
                echo "Successfully downloaded $PIPER_JSON_FILE"
            else
                echo "$PIPER_JSON_FILE already exists, skipping download."
            fi

            # Whisper Base English (common for both environments)
            WHISPER_URL="https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin?download=true"
            WHISPER_FILE="ggml-base.en.bin"
            if [[ ! -f "$WHISPER_FILE" ]]; then
                echo "Downloading $WHISPER_FILE (STT)..."
                curl -L "$WHISPER_URL" -o "$WHISPER_FILE"
                echo "Successfully downloaded $WHISPER_FILE"
            else
                echo "$WHISPER_FILE already exists, skipping download."
            fi

            # Generate checksums for all model files
            echo "Generating checksums..."
            python3 - <<'PY'
import hashlib, json, os
root = '.'
checks = {}
for fn in os.listdir(root):
    if fn.endswith('.gguf') or fn.endswith('.onnx') or fn.endswith('.bin'):
        h = hashlib.sha256()
        with open(fn,'rb') as f:
            for chunk in iter(lambda: f.read(1024*1024), b''):
                h.update(chunk)
        checks[fn] = h.hexdigest()
with open('checksums.json','w', encoding='utf-8') as f:
    json.dump(checks, f, indent=2, ensure_ascii=False)
print('Checksums written to checksums.json')
PY

            cd ..
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
            echo " - Access the UI at http://localhost:5173"
            echo "  - Access the API at http://localhost:8000"
            echo "  - Run tests with: cd backend && python -m pytest"
        else
            echo
            echo "For production, services are running."
            echo " - API is available at http://localhost:8000"
            echo "  - Check health at: http://localhost:8000/api/v1/health/services"
        fi
        ;;
    "models")
        echo "Managing models for $MODELS_ENVIRONMENT environment..."
        
        # Create models directory if it doesn't exist
        mkdir -p "$MODELS_DIR"
        cd "$MODELS_DIR"

        # Determine model URLs based on environment
        if [[ "$MODELS_ENVIRONMENT" == "dev" ]]; then
            echo "Downloading development models (smaller, faster)..."
            
            # TinyLlama 1.1B Chat (Q2_K - smallest functional chat for dev)
            TLL_URL="https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q2_K.gguf?download=true"
            TLL_FILE="tinyllama-1.1b-chat-v1.0.Q2_K.gguf"
        else
            echo "Downloading production models (optimized for performance)..."
            
            # TinyLlama 1.1B Chat (Q4_K_M - balanced for production)
            TLL_URL="https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf?download=true"
            TLL_FILE="tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
        fi

        # Download LLM model if not present
        if [[ ! -f "$TLL_FILE" ]]; then
            echo "Downloading $TLL_FILE ..."
            curl -L "$TLL_URL" -o "$TLL_FILE"
            echo "Successfully downloaded $TLL_FILE"
        else
            echo "$TLL_FILE already exists, skipping download."
        fi

        # Piper English voice (common for both environments)
        PIPER_URL="https://github.com/rhasspy/piper-voices/releases/download/en_US-amy-low/en_US-amy-low.onnx"
        PIPER_FILE="en_US-amy-low.onnx"
        PIPER_JSON_URL="https://github.com/rhasspy/piper-voices/releases/download/en_US-amy-low/en_US-amy-low.onnx.json"
        PIPER_JSON_FILE="en_US-amy-low.onnx.json"

        if [[ ! -f "$PIPER_FILE" ]]; then
            echo "Downloading $PIPER_FILE (TS)..."
            curl -L "$PIPER_URL" -o "$PIPER_FILE"
            echo "Successfully downloaded $PIPER_FILE"
        else
            echo "$PIPER_FILE already exists, skipping download."
        fi

        if [[ ! -f "$PIPER_JSON_FILE" ]]; then
            echo "Downloading $PIPER_JSON_FILE (TTS Config)..."
            curl -L "$PIPER_JSON_URL" -o "$PIPER_JSON_FILE"
            echo "Successfully downloaded $PIPER_JSON_FILE"
        else
            echo "$PIPER_JSON_FILE already exists, skipping download."
        fi

        # Whisper Base English (common for both environments)
        WHISPER_URL="https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin?download=true"
        WHISPER_FILE="ggml-base.en.bin"
        if [[ ! -f "$WHISPER_FILE" ]]; then
            echo "Downloading $WHISPER_FILE (STT)..."
            curl -L "$WHISPER_URL" -o "$WHISPER_FILE"
            echo "Successfully downloaded $WHISPER_FILE"
        else
            echo "$WHISPER_FILE already exists, skipping download."
        fi

        # Generate checksums for all model files
        echo "Generating checksums..."
        python3 - <<'PY'
import hashlib, json, os
root = '.'
checks = {}
for fn in os.listdir(root):
    if fn.endswith('.gguf') or fn.endswith('.onnx') or fn.endswith('.bin'):
        h = hashlib.sha256()
        with open(fn,'rb') as f:
            for chunk in iter(lambda: f.read(1024*1024), b''):
                h.update(chunk)
        checks[fn] = h.hexdigest()
with open('checksums.json','w', encoding='utf-8') as f:
    json.dump(checks, f, indent=2, ensure_ascii=False)
print('Checksums written to checksums.json')
PY

        cd ..
        echo "Model download complete!"
        echo "Environment: $MODELS_ENVIRONMENT"
        echo "Models directory: $(pwd)"
        ;;
    "dev")
        echo "Starting development environment..."
        if [[ -f "docker-compose.dev.yml" ]]; then
            docker compose -f docker-compose.dev.yml up -d
            echo "Development services started using docker-compose.dev.yml"
            echo "Access the UI at http://localhost:5173"
            echo "Access the API at http://localhost:8000"
        else
            echo "Error: docker-compose.dev.yml not found"
            exit 1
        fi
        ;;
    "dev-setup")
        echo "Running development setup..."
        
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
            
            # Create models directory if it doesn't exist
            mkdir -p "$MODELS_DIR"
            cd "$MODELS_DIR"

            # Determine model URLs based on environment
            if [[ "$MODELS_ENVIRONMENT" == "dev" ]]; then
                echo "Downloading development models (smaller, faster)..."
                
                # TinyLlama 1.1B Chat (Q2_K - smallest functional chat for dev)
                TLL_URL="https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q2_K.gguf?download=true"
                TLL_FILE="tinyllama-1.1b-chat-v1.0.Q2_K.gguf"
            else
                echo "Downloading production models (optimized for performance)..."
                
                # TinyLlama 1.1B Chat (Q4_K_M - balanced for production)
                TLL_URL="https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf?download=true"
                TLL_FILE="tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
            fi

            # Download LLM model if not present
            if [[ ! -f "$TLL_FILE" ]]; then
                echo "Downloading $TLL_FILE ..."
                curl -L "$TLL_URL" -o "$TLL_FILE"
                echo "Successfully downloaded $TLL_FILE"
            else
                echo "$TLL_FILE already exists, skipping download."
            fi

            # Piper English voice (common for both environments)
            PIPER_URL="https://github.com/rhasspy/piper-voices/releases/download/en_US-amy-low/en_US-amy-low.onnx"
            PIPER_FILE="en_US-amy-low.onnx"
            PIPER_JSON_URL="https://github.com/rhasspy/piper-voices/releases/download/en_US-amy-low/en_US-amy-low.onnx.json"
            PIPER_JSON_FILE="en_US-amy-low.onnx.json"

            if [[ ! -f "$PIPER_FILE" ]]; then
                echo "Downloading $PIPER_FILE (TS)..."
                curl -L "$PIPER_URL" -o "$PIPER_FILE"
                echo "Successfully downloaded $PIPER_FILE"
            else
                echo "$PIPER_FILE already exists, skipping download."
            fi

            if [[ ! -f "$PIPER_JSON_FILE" ]]; then
                echo "Downloading $PIPER_JSON_FILE (TTS Config)..."
                curl -L "$PIPER_JSON_URL" -o "$PIPER_JSON_FILE"
                echo "Successfully downloaded $PIPER_JSON_FILE"
            else
                echo "$PIPER_JSON_FILE already exists, skipping download."
            fi

            # Whisper Base English (common for both environments)
            WHISPER_URL="https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin?download=true"
            WHISPER_FILE="ggml-base.en.bin"
            if [[ ! -f "$WHISPER_FILE" ]]; then
                echo "Downloading $WHISPER_FILE (STT)..."
                curl -L "$WHISPER_URL" -o "$WHISPER_FILE"
                echo "Successfully downloaded $WHISPER_FILE"
            else
                echo "$WHISPER_FILE already exists, skipping download."
            fi

            # Generate checksums for all model files
            echo "Generating checksums..."
            python3 - <<'PY'
import hashlib, json, os
root = '.'
checks = {}
for fn in os.listdir(root):
    if fn.endswith('.gguf') or fn.endswith('.onnx') or fn.endswith('.bin'):
        h = hashlib.sha256()
        with open(fn,'rb') as f:
            for chunk in iter(lambda: f.read(1024*1024), b''):
                h.update(chunk)
        checks[fn] = h.hexdigest()
with open('checksums.json','w', encoding='utf-8') as f:
    json.dump(checks, f, indent=2, ensure_ascii=False)
print('Checksums written to checksums.json')
PY

            cd ..
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

        # Start services for dev environment (always start services for dev-setup)
        echo
        echo "Starting development services..."
        docker compose -f docker-compose.dev.yml up -d
        echo "Development services started using docker-compose.dev.yml"

        echo
        echo "Development setup completed!"
        echo "Access the UI at http://localhost:5173"
        echo "Access the API at http://localhost:8000"
        ;;
    "deploy")
        echo "Deploying to $ENVIRONMENT environment..."
        
        # Configuration
        RED='\033[0;31m'
        GREEN='\033[0;32m'
        YELLOW='\033[1;33m'
        NC='\033[0m' # No Color

        log() {
            echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] $1${NC}"
        }

        warn() {
            echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] [WARN] $1${NC}"
        }

        error() {
            echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $1${NC}"
        }

        # Check prerequisites
        log "Checking prerequisites..."
        
        if ! command -v docker &> /dev/null; then
            error "Docker is not installed or not in PATH"
            exit 1
        fi
        
        if ! command -v docker compose &> /dev/null; then
            error "Docker Compose is not installed or not in PATH"
            exit 1
        fi
        
        if [[ ! -f ".env" ]]; then
            error "Environment file .env not found"
            error "Please create it from .env.example and configure for production"
            exit 1
        fi
        
        # Load environment file and check required variables
        if ! grep -q "^SECRET_KEY=" ".env" && ! grep -q "^SECRET_KEY =" ".env"; then
            error "SECRET_KEY must be set in .env"
            exit 1
        fi
        
        if ! grep -q "^PRIVACY_SALT=" ".env" && ! grep -q "^PRIVACY_SALT =" ".env"; then
            error "PRIVACY_SALT must be set in .env"
            exit 1
        fi
        
        log "Prerequisites check passed"

        # Create backup of existing data
        log "Creating backup of existing data..."
        BACKUP_DIR="/opt/ai-assistant/backups"
        DATA_DIR="/opt/ai-assistant/data"
        mkdir -p "$BACKUP_DIR"
        BACKUP_FILE="$BACKUP_DIR/data-backup-$(date '+%Y%m%d-%H%M%S').tar.gz"
        
        if [[ -d "$DATA_DIR" ]]; then
            tar -czf "$BACKUP_FILE" -C "$(dirname "$DATA_DIR")" "$(basename "$DATA_DIR")" 2>/dev/null || {
                warn "Could not create data backup"
            }
            
            log "Data backup created: $BACKUP_FILE"
        else
            log "No existing data directory to backup"
        fi

        # Pull latest images
        log "Pulling latest images..."
        docker compose --env-file .env pull

        # Build production images
        log "Building production images..."
        docker compose --env-file .env build --no-cache

        # Start services
        log "Starting services..."
        docker compose --env-file .env up -d

        # Wait for services to be ready
        log "Waiting for services to be ready..."
        sleep 10

        # Health check
        MAX_RETRIES=30
        RETRY_COUNT=0
        
        while [[ $RETRY_COUNT -lt $MAX_RETRIES ]]; do
            if curl -f http://localhost:8000/api/v1/health/ready &>/dev/null; then
                log "Services are ready!"
                break
            fi
            
            RETRY_COUNT=$((RETRY_COUNT + 1))
            log "Waiting for services... (attempt $RETRY_COUNT/$MAX_RETRIES)"
            sleep 10
        done
        
        if [[ $RETRY_COUNT -eq $MAX_RETRIES ]]; then
            error "Services failed to become ready within timeout"
            docker compose logs
            exit 1
        fi

        log "Deployment to $ENVIRONMENT completed successfully!"
        ;;
    "test")
        echo "Running tests..."
        echo "Running backend tests..."
        if [[ -d "backend/.venv" ]]; then
            source backend/.venv/bin/activate
            cd backend
            python -m pytest -v
            cd ..
        else
            echo "Warning: Backend virtual environment not found. Run setup first."
        fi
        ;;
    "verify")
        echo "Verifying models and system integrity..."
        # Inline model verification functionality
        if [[ ! -d "models" ]]; then echo "Models directory not found: models"; exit 1; fi
        if [[ ! -f "models/checksums.json" ]]; then echo "checksums.json not found in models"; exit 1; fi
        python - "$MODELS_DIR" <<'PY'
import sys, os, json, hashlib
root = sys.argv[1]
checks = json.load(open(os.path.join(root,'checksums.json'), encoding='utf-8'))
failed = False
for fn in os.listdir(root):
    if not (fn.endswith('.gguf') or fn.endswith('.onnx')):
        continue
    p = os.path.join(root, fn)
    h = hashlib.sha256()
    with open(p,'rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    val = h.hexdigest()
    exp = checks.get(fn)
    if not exp:
        print(f"WARN: No expected hash for {fn}")
    elif exp != val:
        print(f"MISMATCH: {fn}")
        failed = True
    else:
        print(f"OK: {fn}")
if failed:
    sys.exit(2)
print("All model files verified.")
PY
        ;;
    "cleanup")
        echo "Cleaning up development artifacts..."
        # Stop Docker services
        for file in docker-compose.yml docker-compose.dev.yml; do
            if [[ -f "$file" ]]; then
                echo "Stopping services defined in $file..."
                docker compose -f "$file" down
            fi
        done
        
        # Remove build artifacts
        paths_to_remove=(
            "backend/__pycache__"
            "backend/*.pyc"
            "frontend/node_modules"
            "frontend/dist"
            "frontend/.vite"
            "frontend/.cache"
            "frontend/src-tauri/target"
            "build"
            "dist"
            "target"
            "*.log"
            "logs"
        )
        
        for path in "${paths_to_remove[@]}"; do
            if [[ -e $path ]] || [[ -d $path ]]; then
                rm -rf "$path" 2>/dev/null || true
                echo "Removed: $path"
            fi
        done
        
        # Clean Python cache directories
        find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        
        echo "Cleanup completed."
        ;;
    "voice-test")
        echo "Testing voice functionality..."
        if [[ -f "$PWD/scripts/voice_loop.py" ]]; then
            python3 "$PWD/scripts/voice_loop.py"
        else
            echo "Voice loop test script not found"
        fi
        ;;
    *)
        echo "Invalid command: $COMMAND"
        usage
        ;;
esac
