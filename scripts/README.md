# Scripts Directory

This directory contains operational scripts organized by purpose and environment.

## Directory Structure

```
scripts/
├── setup/          # Initial setup and installation scripts
├── dev/            # Development environment scripts  
├── prod/           # Production deployment scripts
└── README.md       # This file
```

## Setup Scripts (`scripts/setup/`)

Scripts for initial project setup and model acquisition.

### get-models.ps1 / get-models.sh
Downloads required AI models and voice files for the Local AI Assistant.

**Downloads:**
- TinyLlama 1.1B Chat model (GGUF format)
- Piper English voice model (ONNX format)
- Generates SHA256 checksums for integrity verification

**Usage:**
```powershell
# Windows
./scripts/setup/get-models.ps1

# macOS/Linux
./scripts/setup/get-models.sh
```

**Options:**
- `ModelsDir`: Override models directory (default: `models`)

## Development Scripts (`scripts/dev/`)

Scripts for development workflow and environment management.

### dev.ps1 / dev.sh
Starts the full development environment (backend + frontend).
- Starts Docker Compose backend services
- Installs frontend dependencies (first run)
- Launches Vite dev server

**Usage:**
```powershell
# Windows
./scripts/dev/dev.ps1

# macOS/Linux  
./scripts/dev/dev.sh
```

### cleanup.ps1
Comprehensive development environment cleanup.
- Stops Docker services
- Removes build artifacts (node_modules, dist, target, etc.)
- Clears Python/Rust/JS cache directories
- Removes log files

**Usage:**
```powershell
./scripts/dev/cleanup.ps1

# Skip Docker operations
./scripts/dev/cleanup.ps1 -NoDocker
```

### voice_loop.py
Development tool for testing voice interaction flow.
- Continuous voice input/output testing
- Useful for debugging voice pipeline issues

**Usage:**
```bash
cd scripts/dev && python voice_loop.py
```

## Production Scripts (`scripts/prod/`)

Scripts for production deployment and operations.

### deploy.sh
Comprehensive production deployment script with backup and monitoring.

**Features:**
- Automated pre-deployment backups
- Health checking and readiness verification
- Rollback capabilities
- Service management commands

**Usage:**
```bash
# Deploy application  
./scripts/prod/deploy.sh deploy

# Restore from backup
./scripts/prod/deploy.sh restore /path/to/backup.tar.gz

# View service status
./scripts/prod/deploy.sh status

# View logs
./scripts/prod/deploy.sh logs

# Stop services
./scripts/prod/deploy.sh stop

# Update deployment (backup + redeploy)
./scripts/prod/deploy.sh update
```

**Prerequisites:**
- `.env.prod` environment file configured
- Docker and Docker Compose installed
- Production models downloaded

## Script Execution

### Windows
All PowerShell scripts should be run with:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/path/to/script.ps1
```

### macOS/Linux
Make scripts executable first:
```bash
chmod +x scripts/path/to/script.sh
./scripts/path/to/script.sh
```

## Related Directories

- **`tests/`**: Testing and verification scripts (moved from scripts/)
- **`backend/tests/`**: Python unit tests
- **`frontend/src-tauri/`**: Desktop application build scripts

## Script Development Guidelines

When adding new scripts to this directory:

1. **Categorize properly**: Place in appropriate subdirectory (setup/dev/prod)
2. **Cross-platform**: Provide both .ps1 (Windows) and .sh (macOS/Linux) versions when possible
3. **Error handling**: Use proper exit codes and error messaging
4. **Documentation**: Update this README and add inline documentation
5. **Idempotency**: Scripts should be safe to run multiple times
6. **Logging**: Provide clear, colored output for user feedback