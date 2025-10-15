#!/bin/bash
# Production deployment script for Local AI Assistant

set -e

# Configuration
BACKUP_DIR="/opt/ai-assistant/backups"
DATA_DIR="/opt/ai-assistant/data"
MODELS_DIR="/opt/ai-assistant/models"
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.prod"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed or not in PATH"
        exit 1
    fi
    
    if [[ ! -f "$ENV_FILE" ]]; then
        error "Environment file $ENV_FILE not found"
        error "Please create it from .env.example and configure for production"
        exit 1
    fi
    
    # Check required environment variables
    source "$ENV_FILE"
    if [[ -z "$SECRET_KEY" ]]; then
        error "SECRET_KEY must be set in $ENV_FILE"
        exit 1
    fi
    
    if [[ -z "$PRIVACY_SALT" ]]; then
        error "PRIVACY_SALT must be set in $ENV_FILE"
        exit 1
    fi
    
    log "Prerequisites check passed"
}

# Create backup of existing data
backup_data() {
    if [[ -d "$DATA_DIR" ]]; then
        log "Creating backup of existing data..."
        
        mkdir -p "$BACKUP_DIR"
        BACKUP_FILE="$BACKUP_DIR/data-backup-$(date '+%Y%m%d-%H%M%S').tar.gz"
        
        tar -czf "$BACKUP_FILE" -C "$(dirname "$DATA_DIR")" "$(basename "$DATA_DIR")" 2>/dev/null || {
            warn "Could not create data backup"
        }
        
        # Keep only last 10 backups
        find "$BACKUP_DIR" -name "data-backup-*.tar.gz" -type f -mtime +10 -delete 2>/dev/null || true
        
        log "Data backup created: $BACKUP_FILE"
    else
        log "No existing data directory to backup"
    fi
}

# Deploy the application
deploy() {
    log "Starting production deployment..."
    
    # Pull latest images
    log "Pulling latest images..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" pull
    
    # Build production images
    log "Building production images..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" build --no-cache
    
    # Start services
    log "Starting services..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
    
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
        docker-compose -f "$COMPOSE_FILE" logs
        exit 1
    fi
}

# Restore from backup
restore() {
    if [[ -z "$1" ]]; then
        error "Please specify backup file to restore from"
        echo "Available backups:"
        ls -la "$BACKUP_DIR"/data-backup-*.tar.gz 2>/dev/null || echo "No backups found"
        exit 1
    fi
    
    BACKUP_FILE="$1"
    if [[ ! -f "$BACKUP_FILE" ]]; then
        error "Backup file $BACKUP_FILE not found"
        exit 1
    fi
    
    log "Stopping services for restore..."
    docker-compose -f "$COMPOSE_FILE" down
    
    log "Restoring data from $BACKUP_FILE..."
    tar -xzf "$BACKUP_FILE" -C "$(dirname "$DATA_DIR")"
    
    log "Starting services after restore..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
}

# Show logs
logs() {
    docker-compose -f "$COMPOSE_FILE" logs -f
}

# Show status
status() {
    docker-compose -f "$COMPOSE_FILE" ps
    echo
    log "Health status:"
    curl -s http://localhost:8000/api/v1/health/services | jq . || echo "Services not accessible"
}

# Stop services
stop() {
    log "Stopping services..."
    docker-compose -f "$COMPOSE_FILE" down
}

# Update deployment
update() {
    log "Updating deployment..."
    backup_data
    deploy
}

# Main script logic
case "${1:-deploy}" in
    "deploy")
        check_prerequisites
        backup_data
        deploy
        ;;
    "restore")
        restore "$2"
        ;;
    "logs")
        logs
        ;;
    "status")
        status
        ;;
    "stop")
        stop
        ;;
    "update")
        check_prerequisites
        update
        ;;
    *)
        echo "Usage: $0 {deploy|restore|logs|status|stop|update}"
        echo
        echo "Commands:"
        echo "  deploy  - Deploy the application (default)"
        echo "  restore - Restore from backup (requires backup file path)"
        echo "  logs    - Show service logs"
        echo "  status  - Show service status"
        echo "  stop    - Stop all services"
        echo "  update  - Update deployment (backup + redeploy)"
        exit 1
        ;;
esac