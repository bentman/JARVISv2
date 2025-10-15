# Production Deployment Guide

This guide covers deploying the Local AI Assistant in production environments with security hardening, monitoring, and operational best practices.

## Quick Start

1. **Copy production configuration**:
   ```bash
   cp .env.prod.example .env.prod
   ```

2. **Configure secrets** (CRITICAL):
   ```bash
   # Generate strong secrets
   openssl rand -base64 32  # Use for SECRET_KEY
   openssl rand -base64 16  # Use for PRIVACY_SALT
   ```

3. **Deploy**:
   ```bash
   chmod +x scripts/prod/deploy.sh
   ./scripts/prod/deploy.sh deploy
   ```

## Security Configuration

### Required Security Settings

**CRITICAL**: The following must be configured before production deployment:

- `SECRET_KEY`: Strong 32+ character secret for encryption/signing
- `PRIVACY_SALT`: Unique salt for privacy key derivation  
- `BACKEND_CORS_ORIGINS`: Restrict to your production domains only

### Production Security Defaults

- **Encryption at rest**: `PRIVACY_ENCRYPT_AT_REST=true`
- **Strict redaction**: `PRIVACY_REDACT_AGGRESSIVENESS=strict`
- **Limited retention**: `PRIVACY_RETENTION_DAYS=7`
- **Budget enforcement**: `BUDGET_ENFORCE=true`
- **External services disabled**: `SEARCH_ENABLED=false`, `REMOTE_LLM_ENABLED=false`

### Additional Security Measures

- **Non-root containers**: All services run as non-root users
- **Read-only filesystems**: Backend container filesystem is read-only
- **Resource limits**: CPU/memory constraints prevent resource exhaustion
- **Health checks**: Kubernetes-style readiness/liveness probes
- **Security options**: `no-new-privileges` prevents privilege escalation

## Production Architecture

### Services

- **Backend**: Gunicorn with Uvicorn workers (production-grade ASGI server)
- **Redis**: Persistent storage with memory limits and eviction policies
- **Volumes**: Named volumes for data persistence and backup capability

### Resource Allocation

**Backend Container**:
- Limits: 2 CPU cores, 4GB RAM
- Reservations: 0.5 CPU cores, 1GB RAM

**Redis Container**:
- Limits: 0.5 CPU cores, 512MB RAM  
- Reservations: 0.1 CPU cores, 128MB RAM
- Memory policy: `allkeys-lru` with 256MB max

### Networking

- **Internal network**: Services communicate over dedicated bridge network
- **External access**: Only backend port 8000 exposed
- **Security**: Services isolated from external networks where possible

## Monitoring & Health Checks

### Health Check Endpoints

- **Readiness**: `GET /api/v1/health/ready`
  - Database connectivity
  - Redis connectivity  
  - Model availability
  - Returns 503 if not ready

- **Liveness**: `GET /api/v1/health/live`
  - Basic service health
  - Process uptime
  - Always returns 200 if service running

- **Metrics**: `GET /api/v1/health/metrics`
  - System metrics (CPU, memory, disk)
  - Process metrics (RSS, VMS, CPU usage)
  - Service metrics (Redis health, model count)

### Structured Logging

Production deployments use JSON structured logging:

```json
{
  \"timestamp\": \"2024-01-15T10:30:45Z\",
  \"level\": \"INFO\",
  \"logger\": \"app.api.chat\",
  \"message\": \"Chat request completed\",
  \"request_id\": \"req-123\",
  \"endpoint\": \"/api/v1/chat/send\",
  \"duration_ms\": 250
}
```

**Log Files** (in production):
- `/app/logs/app.log`: General application logs
- `/app/logs/error.log`: Error-level logs only
- `/app/logs/access.log`: Gunicorn access logs

## Backup & Recovery

### Automated Backups

The deployment script automatically creates backups before deployments:

- **Location**: `/opt/ai-assistant/backups/`
- **Format**: `data-backup-YYYYMMDD-HHMMSS.tar.gz`
- **Retention**: Last 10 backups kept (10+ day retention)
- **Contents**: Complete data directory including database and user files

### Manual Backup

```bash
# Create backup
./scripts/prod/deploy.sh backup

# List available backups  
ls -la /opt/ai-assistant/backups/
```

### Restore from Backup

```bash
# Restore specific backup
./scripts/prod/deploy.sh restore /opt/ai-assistant/backups/data-backup-20240115-103045.tar.gz
```

## Deployment Operations

### Initial Deployment

1. **Prepare environment**:
   ```bash
   # Create directories
   sudo mkdir -p /opt/ai-assistant/{data,models,backups}
   sudo chown $USER:$USER /opt/ai-assistant
   
   # Copy models to production location
   cp -r ./models/* /opt/ai-assistant/models/
   ```

2. **Configure environment**:
   ```bash
   cp .env.prod.example .env.prod
   # Edit .env.prod with production values
   ```

3. **Deploy**:
   ```bash
   ./scripts/prod/deploy.sh deploy
   ```

### Updates and Maintenance

```bash
# Update deployment (includes backup)
./scripts/prod/deploy.sh update

# View service status
./scripts/prod/deploy.sh status

# View logs
./scripts/prod/deploy.sh logs

# Stop services
./scripts/prod/deploy.sh stop
```

### Health Monitoring

Monitor these endpoints for operational health:

```bash
# Service readiness (should return 200)
curl -f http://localhost:8000/api/v1/health/ready

# System metrics
curl -s http://localhost:8000/api/v1/health/metrics | jq .

# Service logs
docker-compose -f docker-compose.prod.yml logs -f backend
```

## Performance Tuning

### Gunicorn Configuration

Current production settings (in `Dockerfile.prod`):

```bash
gunicorn app.main:app \\
  --worker-class uvicorn.workers.UvicornWorker \\
  --workers 2 \\
  --worker-connections 1000 \\
  --max-requests 1000 \\
  --max-requests-jitter 100
```

**Tuning Guidelines**:
- **Workers**: Start with `2 * CPU_CORES`
- **Connections**: Adjust based on concurrent user load
- **Max requests**: Restart workers periodically to prevent memory leaks

### Redis Configuration

Production Redis settings optimize for:
- **Persistence**: AOF + RDB snapshots
- **Memory management**: LRU eviction with 256MB limit
- **Durability**: `appendfsync everysec` for balanced performance/durability

### Resource Monitoring

Watch these metrics for capacity planning:

- **CPU utilization**: Keep < 70% sustained
- **Memory usage**: Monitor RSS growth in backend processes  
- **Disk I/O**: Database and model file access patterns
- **Network**: Request rate and response times

## Security Best Practices

### Environment Security

- **File permissions**: Ensure `.env.prod` is not readable by others (`chmod 600`)
- **Secret rotation**: Rotate `SECRET_KEY` and `PRIVACY_SALT` periodically
- **Network isolation**: Use reverse proxy (nginx/traefik) for TLS termination
- **Firewall**: Restrict access to port 8000 to authorized sources only

### Data Protection

- **Encryption**: All sensitive data encrypted at rest (enabled by default)
- **Access control**: No authentication implemented - add auth layer if needed
- **Data retention**: Automatic cleanup based on `PRIVACY_RETENTION_DAYS`
- **Audit logging**: All requests logged with request IDs for tracing

### External Services

**Default**: All external services disabled for maximum privacy

If enabling external services:
- Review privacy implications
- Use dedicated API keys with restricted permissions
- Monitor usage and costs through budget controls
- Consider data residency requirements

## Troubleshooting

### Common Issues

**Services not ready**:
```bash
# Check container status
docker-compose -f docker-compose.prod.yml ps

# Check health endpoints
curl http://localhost:8000/api/v1/health/services

# Review logs
docker-compose -f docker-compose.prod.yml logs backend
```

**High memory usage**:
- Check model sizes and system RAM
- Adjust gunicorn worker count
- Monitor Redis memory usage

**Performance issues**:
- Review metrics endpoint for resource utilization
- Check disk I/O for model loading bottlenecks
- Monitor request/response times in access logs

### Recovery Procedures

**Complete failure**:
1. Stop services: `./scripts/prod/deploy.sh stop`
2. Restore from backup: `./scripts/prod/deploy.sh restore <backup-file>`
3. Verify health: `curl http://localhost:8000/api/v1/health/ready`

**Partial failure**:
1. Check specific service: `docker-compose -f docker-compose.prod.yml ps`
2. Review logs: `docker-compose -f docker-compose.prod.yml logs <service>`
3. Restart individual service: `docker-compose -f docker-compose.prod.yml restart <service>`

## Scaling Considerations

### Horizontal Scaling

Current architecture is single-node. For multi-node deployment:

- **Load balancer**: Distribute requests across backend instances
- **Shared storage**: Move models to shared filesystem (NFS/EFS)
- **Redis cluster**: Replace single Redis with cluster for HA
- **Database**: Consider PostgreSQL for better multi-node support

### Vertical Scaling

- **GPU support**: Add GPU devices to Docker Compose for hardware acceleration
- **NPU optimization**: Enable `NPU_FORCE_ENABLE=true` if NPU available
- **Memory**: Increase container limits based on model requirements
- **Storage**: Monitor disk usage for model files and data growth