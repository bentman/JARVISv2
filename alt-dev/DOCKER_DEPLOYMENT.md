# QwenAssistant Docker Deployment Guide

Complete guide for deploying QwenAssistant using Docker and Docker Compose.

## Prerequisites

- Docker (20.10+): https://docs.docker.com/get-docker/
- Docker Compose (2.0+): https://docs.docker.com/compose/install/
- 30GB disk space for models
- 8GB+ RAM for backend

## Quick Docker Start

### 1. Prepare Models

Download AI models to host machine:

```bash
# Download models (choose profile)
PROFILE=medium bash backend/setup_models.sh

# Models saved in: ./models directory
ls -lh models/
```

### 2. Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit for your environment
nano .env  # or vim, or your editor
```

Key settings to check:
- `DATABASE_URL` - Should point to `/app/data/local_ai.db`
- `MODEL_PATH` - Should point to `/models`
- `HARDWARE_PROFILE` - Choose: light, medium, or heavy

### 3. Start Services

```bash
# Start all services
docker compose -f backend/docker-compose.yml up -d

# View logs
docker compose -f backend/docker-compose.yml logs -f

# Verify services
docker compose -f backend/docker-compose.yml ps
```

### 4. Access Application

- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Frontend:** http://localhost:5173 (requires separate frontend container)

### 5. Stop Services

```bash
docker compose -f backend/docker-compose.yml down

# Also remove volumes (warning: deletes data)
docker compose -f backend/docker-compose.yml down -v
```

---

## Docker Compose Services

### Backend Service

**Port:** 8000
**Image:** Built from `backend/Dockerfile`
**Features:**
- FastAPI application
- SQLite database persistence
- Redis connection
- Health checks
- Resource limits

**Environment Variables:**
```yaml
DATABASE_URL: sqlite:///./data/local_ai.db
MODEL_PATH: /models
REDIS_URL: redis://redis:6379/0
```

### Redis Service

**Port:** 6379
**Image:** redis:7-alpine
**Purpose:** Caching and session storage
**Configuration:**
- AOF persistence
- Memory limit: 256MB
- Auto-LRU eviction policy

---

## Advanced Configuration

### Custom Environment Variables

Edit `backend/docker-compose.yml`:

```yaml
environment:
  - DATABASE_URL=sqlite:///./data/local_ai.db
  - LOG_LEVEL=DEBUG  # Add this
  - HARDWARE_PROFILE=heavy  # Add this
```

### GPU Acceleration

For NVIDIA GPUs, add to backend service:

```yaml
runtime: nvidia
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

### Custom Port Mapping

Change ports in `docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "9000:8000"  # Map 9000 host → 8000 container
```

### Persistent Storage

Data is stored in:
- `data_volume` - Database and files
- `redis_data` - Cache persistence

To backup:
```bash
docker run --rm -v data_volume:/data -v $(pwd):/backup alpine tar czf /backup/data-backup.tar.gz /data

docker run --rm -v redis_data:/data -v $(pwd):/backup alpine tar czf /backup/redis-backup.tar.gz /data
```

---

## Building Custom Images

### Build Backend Image

```bash
docker build -f backend/Dockerfile -t qwen-ai:latest backend/
```

### Build Development Image

```bash
docker build -f backend/Dockerfile.dev -t qwen-ai:dev backend/
```

### Push to Registry

```bash
docker tag qwen-ai:latest myregistry/qwen-ai:latest
docker push myregistry/qwen-ai:latest
```

---

## Production Deployment

### Security Hardening

1. **Change default secrets:**
```bash
export SECRET_KEY=$(openssl rand -hex 32)
export PRIVACY_SALT=$(openssl rand -hex 16)
```

2. **Use secrets file:**
```bash
# Create secrets
echo "your-secret-key" > ./secrets/secret_key
echo "your-salt" > ./secrets/privacy_salt
```

3. **Update docker-compose.yml:**
```yaml
secrets:
  secret_key:
    file: ./secrets/secret_key
  privacy_salt:
    file: ./secrets/privacy_salt

services:
  backend:
    secrets:
      - secret_key
      - privacy_salt
    environment:
      SECRET_KEY_FILE: /run/secrets/secret_key
```

### Health Checks

Health endpoint is already configured:

```bash
# Check manually
curl http://localhost:8000/api/v1/health/services

# Docker automatically monitors
docker ps  # Look at STATUS column
```

### Resource Limits

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 4G
    reservations:
      cpus: '0.5'
      memory: 1G
```

### Network Isolation

Services run on `app-network`:
- Backend ↔ Redis: Connected
- Frontend: Separate network (add if needed)
- External: Only exposed ports accessible

---

## Troubleshooting

### Services Won't Start

```bash
# Check logs
docker compose -f backend/docker-compose.yml logs backend

# Common issues:
# - Port already in use: Change ports in docker-compose.yml
# - Out of memory: Reduce MEMORY_LIMIT in .env
# - Models not found: Check MODEL_PATH volume mount
```

### Database Issues

```bash
# Reset database
docker compose -f backend/docker-compose.yml down -v
docker compose -f backend/docker-compose.yml up -d

# Verify database
docker exec -it <backend-container> python3 verify_structure.py
```

### Performance Issues

```bash
# Monitor resource usage
docker stats

# Check container logs
docker logs -f <backend-container>

# Adjust limits in docker-compose.yml
```

### Redis Connection Failed

```bash
# Check Redis status
docker exec -it <redis-container> redis-cli ping

# Verify network
docker network inspect app-network

# Restart Redis
docker compose -f backend/docker-compose.yml restart redis
```

---

## Docker Compose Reference

### Common Commands

```bash
# Start in background
docker compose -f backend/docker-compose.yml up -d

# Start in foreground (see logs)
docker compose -f backend/docker-compose.yml up

# View logs
docker compose -f backend/docker-compose.yml logs -f

# Stop services
docker compose -f backend/docker-compose.yml stop

# Restart services
docker compose -f backend/docker-compose.yml restart

# Remove services
docker compose -f backend/docker-compose.yml down

# Remove with volumes (delete data)
docker compose -f backend/docker-compose.yml down -v

# Execute command in container
docker compose -f backend/docker-compose.yml exec backend bash

# View service status
docker compose -f backend/docker-compose.yml ps

# Pull latest images
docker compose -f backend/docker-compose.yml pull
```

---

## Multi-Node Deployment

For scaling across multiple machines:

### Using Swarm Mode

```bash
# Initialize swarm
docker swarm init

# Deploy service
docker stack deploy -c backend/docker-compose.yml qwen

# View services
docker service ls

# Scale service
docker service scale qwen_backend=3
```

### Using Kubernetes

```bash
# Convert compose to Kubernetes manifests
kompose convert -f backend/docker-compose.yml -o k8s/

# Deploy
kubectl apply -f k8s/

# Monitor
kubectl get pods
kubectl logs -f deployment/backend
```

---

## Monitoring & Logging

### View Logs

```bash
# All services
docker compose -f backend/docker-compose.yml logs

# Specific service
docker compose -f backend/docker-compose.yml logs backend

# Follow logs
docker compose -f backend/docker-compose.yml logs -f

# Last 100 lines
docker compose -f backend/docker-compose.yml logs --tail 100
```

### Health Status

```bash
# Docker health status
docker inspect --format='{{.State.Health.Status}}' <container>

# API health endpoint
curl http://localhost:8000/api/v1/health/services
```

### Performance Metrics

```bash
# Real-time stats
docker stats

# CPU/Memory usage
docker compose -f backend/docker-compose.yml top backend

# Network stats
docker stats --no-stream --format "table {{.Container}}\t{{.NetIO}}"
```

---

## Environment-Specific Configs

### Development

```yaml
# docker-compose.dev.yml
services:
  backend:
    build:
      context: backend
      dockerfile: Dockerfile.dev
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG
      - RELOAD=true
    volumes:
      - ./backend:/app
```

### Staging

```yaml
# docker-compose.staging.yml
services:
  backend:
    environment:
      - DEBUG=false
      - LOG_LEVEL=WARNING
      - ENV=staging
```

### Production

```yaml
# docker-compose.prod.yml
services:
  backend:
    image: myregistry/qwen-ai:latest
    environment:
      - DEBUG=false
      - LOG_LEVEL=INFO
      - ENV=production
    deploy:
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 5
```

---

## Backup & Recovery

### Backup Volumes

```bash
#!/bin/bash
# backup.sh

TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Backup database volume
docker run --rm \
  -v data_volume:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/data_$TIMESTAMP.tar.gz /data

# Backup Redis data
docker run --rm \
  -v redis_data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/redis_$TIMESTAMP.tar.gz /data

echo "Backup completed: data_$TIMESTAMP.tar.gz"
```

### Restore from Backup

```bash
#!/bin/bash
# restore.sh

BACKUP_FILE=$1

# Stop services
docker compose -f backend/docker-compose.yml down

# Restore volumes
docker run --rm \
  -v data_volume:/data \
  -v $(pwd)/backups:/backup \
  alpine tar xzf /backup/$BACKUP_FILE -C /data

# Start services
docker compose -f backend/docker-compose.yml up -d

echo "Restored from: $BACKUP_FILE"
```

---

## Docker Best Practices

1. **Use specific image tags** - Avoid `latest` in production
2. **Set resource limits** - Prevent one service from consuming all resources
3. **Use health checks** - Docker monitors and restarts unhealthy services
4. **Store secrets securely** - Use Docker secrets, not environment variables
5. **Log aggregation** - Collect logs from all containers
6. **Regular backups** - Back up volumes regularly
7. **Update images** - Keep images updated with security patches
8. **Use private registry** - For proprietary images

---

## Getting Help

### Common Issues

**Container exits immediately:**
- Check logs: `docker compose -f backend/docker-compose.yml logs backend`
- Verify requirements.txt: `docker compose -f backend/docker-compose.yml exec backend python -m pip list`

**Port conflicts:**
- Find what's using port: `lsof -i :8000`
- Change port in docker-compose.yml

**Slow performance:**
- Monitor: `docker stats`
- Check CPU throttling: `docker exec backend ps aux`

### Documentation

- Docker Compose: https://docs.docker.com/compose/
- Docker CLI: https://docs.docker.com/engine/reference/commandline/cli/
- Best Practices: https://docs.docker.com/develop/dev-best-practices/

---

## Next Steps

1. Start services: `docker compose -f backend/docker-compose.yml up -d`
2. Verify health: `curl http://localhost:8000/api/v1/health/services`
3. Access API docs: http://localhost:8000/docs
4. Start frontend: `cd frontend && npm run dev`
5. Open browser: http://localhost:5173

---

**Happy deploying! 🐳**
