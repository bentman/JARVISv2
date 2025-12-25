#!/bin/bash
# Production deployment script for Local AI Assistant with backup, monitoring, and operational best practices.

set -euo pipefail

# Default values
ACTION="${1:-deploy}"
BACKUP_DIR="/opt/ai-assistant/backups"
DATA_DIR="/opt/ai-assistant/data"
MODELS_DIR="/opt/ai-assistant/models"
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"
BACKUP_FILE=""

# Function to display usage
usage() {
    echo "Usage: $0 {deploy|restore|logs|status|stop|update} [backup-file]"
    echo ""
    echo "Actions:"
    echo "  deploy  - Deploy application with backup and health checks (default)"
    echo "  restore - Restore from backup (requires backup file path)"
    echo "  logs    - Show service logs"
    echo "  status  - Show service status and health"
    echo "  stop    - Stop all services"
    echo "  update  - Update deployment (backup + redeploy)"
    echo ""
    echo "Examples:"
    echo "  $0 deploy                    # Deploy the application"
    echo "  $0 update                    # Update deployment (backup + redeploy)"
    echo "  $0 restore /path/to/backup   # Restore from specific backup"
    exit 1
}

# Parse command line arguments
if [[ $# -gt 0 ]]; then
    ACTION=$1
    shift
    if [[ "$ACTION" == "restore" && $# -gt 0 ]]; then
        BACKUP_FILE=$1
    elif [[ "$ACTION" == "restore" && $# -eq 0 ]]; then
        echo "Error: Backup file path required for restore action"
        echo "Available backups:"
        ls -la "$BACKUP_DIR"/data-backup-*.tar.gz 2>/dev/null || echo "No backups found"
        exit 1
    fi
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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
check_prerequisites() {
    log "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v docker compose &> /dev/null; then
        error "Docker Compose is not installed or not in PATH"
        exit 1
    fi
    
    if [[ ! -f "$ENV_FILE" ]]; then
        error "Environment file $ENV_FILE not found"
        error "Please create it from .env.example and configure for production"
        exit 1
    fi
    
    # Load environment file and check required variables
    if ! grep -q "^SECRET_KEY=" "$ENV_FILE" && ! grep -q "^SECRET_KEY =" "$ENV_FILE"; then
        error "SECRET_KEY must be set in $ENV_FILE"
        exit 1
    fi
    
    if ! grep -q "^PRIVACY_SALT=" "$ENV_FILE" && ! grep -q "^PRIVACY_SALT =" "$ENV_FILE"; then
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
        
        log "Data backup created: $BACKUP_FILE"
        
        # Keep only last 10 backups
        find "$BACKUP_DIR" -name "data-backup-*.tar.gz" -type f -mtime +10 -delete 2>/dev/null || true
    else
        log "No existing data directory to backup"
    fi
}

# Deploy the application
deploy_app() {
    log "Starting production deployment..."
    
    # Pull latest images
    log "Pulling latest images..."
    docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" pull
    
    # Build production images
    log "Building production images..."
    docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" build --no-cache
    
    # Start services
    log "Starting services..."
    docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
    
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
        docker compose -f "$COMPOSE_FILE" logs
        exit 1
    fi
}

# Restore from backup
restore_from_backup() {
    if [[ -z "$BACKUP_FILE" ]]; then
        error "Please specify backup file to restore from"
        echo "Available backups:"
        ls -la "$BACKUP_DIR"/data-backup-*.tar.gz 2>/dev/null || echo "No backups found"
        exit 1
    fi
    
    if [[ ! -f "$BACKUP_FILE" ]]; then
        error "Backup file $BACKUP_FILE not found"
        exit 1
    fi
    
    log "Stopping services for restore..."
    docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down
    
    log "Restoring data from $BACKUP_FILE..."
    tar -xzf "$BACKUP_FILE" -C "$(dirname "$DATA_DIR")"
    
    log "Starting services after restore..."
    docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
}

# Show logs
show_logs() {
    docker compose -f "$COMPOSE_FILE" logs -f
}

# Show status
show_status() {
    echo -e "${BLUE}=== Service Status ===${NC}"
    docker compose -f "$COMPOSE_FILE" ps
    echo ""
    
    echo -e "${BLUE}=== Health Status ===${NC}"
    if curl -sf http://localhost:8000/api/v1/health/services >/dev/null 2>&1; then
        curl -s http://localhost:8000/api/v1/health/services | jq . 2>/dev/null || echo "Health endpoint accessible"
    else
        echo -e "${RED}Services not accessible${NC}"
    fi
}

# Stop services
stop_services() {
    log "Stopping services..."
    docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down
}

# Update deployment
update_deployment() {
    log "Updating deployment..."
    backup_data
    deploy_app
}

# Main script logic
case "$ACTION" in
    "deploy")
        check_prerequisites
        backup_data
        deploy_app
        ;;
    "restore")
        restore_from_backup
        ;;
    "logs")
        show_logs
        ;;
    "status")
        show_status
        ;;
    "stop")
        stop_services
        ;;
    "update")
        check_prerequisites
        update_deployment
        ;;
    *)
        usage
        ;;
esac

log "Deployment action '$ACTION' completed successfully!"
