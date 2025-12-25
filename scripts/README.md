# Scripts Directory

This directory contains operational scripts consolidated into a simple, easy-to-understand structure for both development and production use. Instead of organizing by subdirectories, we've consolidated the most important functionality into primary scripts with command parameters to handle different scenarios, plus specialized test scripts in the tests/ directory.

## Primary Scripts

### main.ps1 / main.sh
Main entry point for all common operations in the Local AI Assistant project. Handles setup, model management, development workflows, production deployment, testing, and utilities in a single interface.

**Commands:**
- `setup`: Set up dev/prod environment
- `models`: Download models for dev/prod
- `dev`: Start development environment
- `deploy`: Deploy to production
- `test`: Run tests
- `verify`: Verify models and integrity
- `cleanup`: Clean development artifacts
- `voice-test`: Test voice functionality

**Usage:**
```powershell
# Windows
./scripts/main.ps1 -Command setup -Environment dev
./scripts/main.ps1 -Command models -Environment prod
./scripts/main.ps1 -Command dev
./scripts/main.ps1 -Command deploy -Environment prod
```

```bash
# macOS/Linux
./scripts/main.sh setup -e dev
./scripts/main.sh models -e prod
./scripts/main.sh dev
./scripts/main.sh deploy -e prod
```

### get-models.ps1 / get-models.sh
Downloads required AI models and voice files for the Local AI Assistant, with separate options for development and production environments. For development, downloads smaller models for faster iteration. For production, downloads optimized models for better performance.

**Downloads:**
- LLM model (TinyLlama 1.1B Chat - Q2_K for dev, Q4_K_M for prod) (GGUF format)
- Piper English voice model (ONNX format)
- Whisper STT model (for voice processing)
- Generates SHA256 checksums for integrity verification

**Usage:**
```powershell
# Windows - Development models
./scripts/get-models.ps1 -Environment dev

# Windows - Production models
./scripts/get-models.ps1 -Environment prod
```

```bash
# macOS/Linux - Development models
./scripts/get-models.sh -e dev

# macOS/Linux - Production models
./scripts/get-models.sh -e prod
```

### setup.ps1 / setup.sh
Complete setup script that handles the full environment setup for either development or production. Combines model download, dependency installation, and service startup based on the specified environment type. This replaces the need for multiple separate setup scripts by taking environment parameters to determine the appropriate actions.

**Usage:**
```powershell
# Windows - Development setup
./scripts/setup.ps1 -Environment dev

# Windows - Production setup
./scripts/setup.ps1 -Environment prod
```

```bash
# macOS/Linux - Development setup
./scripts/setup.sh -e dev

# macOS/Linux - Production setup
./scripts/setup.sh -e prod
```

### deploy.ps1 / deploy.sh
Comprehensive production deployment script with backup, monitoring, and operational best practices. Handles prerequisites check, backup creation, service deployment, health verification, and post-deployment validation with security hardening for production environments. This replaces the need for separate prod/ directory scripts by providing all deployment functionality in a single script with action parameters.

**Usage:**
```powershell
# Windows
./scripts/deploy.ps1 -Action deploy
./scripts/deploy.ps1 -Action update
./scripts/deploy.ps1 -Action restore -BackupFile "/path/to/backup"
```

```bash
# macOS/Linux
./scripts/deploy.sh deploy
./scripts/deploy.sh update
./scripts/deploy.sh restore /path/to/backup
```

## Development Scripts (still maintained separately)

### dev-setup.ps1 / dev-setup.sh
Complete development environment setup script that handles model downloads, service startup, and frontend preparation using the development Docker configuration. This provides a one-command solution for setting up the complete development environment with volume mounts for live reloading and development-optimized settings. This is kept separate as it's frequently used to initialize development workspaces.

**Usage:**
```powershell
# Windows
./scripts/dev-setup.ps1
# With options
./scripts/dev-setup.ps1 -Environment dev -SkipModels
```

```bash
# macOS/Linux
./scripts/dev-setup.sh
# With options
./scripts/dev-setup.sh -e dev -s
```

### dev.ps1 / dev.sh
Quick development script to start the development environment using docker-compose.dev.yml. This provides a fast way to start development services without going through the full setup process. This is kept separate as it's frequently used during active development work after the initial setup is complete.

**Usage:**
```powershell
# Windows
./scripts/dev.ps1
```

```bash
# macOS/Linux
./scripts/dev.sh
```

### cleanup.ps1 / cleanup.sh
Comprehensive development environment cleanup script that stops Docker services, removes build artifacts, clears cache directories, and removes log files. This replaces the need for multiple cleanup utilities by handling all common cleanup tasks in a single script. This is kept separate as it's frequently used during development cycles to reset the environment.

**Usage:**
```powershell
# Windows
./scripts/cleanup.ps1
```

```bash
# macOS/Linux
./scripts/cleanup.sh
```

## Test Scripts (in tests/ directory)

Test scripts have been moved to the tests/ directory to keep the main scripts directory focused on operational functionality. See the tests/README.md for details on testing scripts.

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

When adding new scripts to this directory, consider first if the functionality can be integrated into one of the main consolidated scripts (main, get-models, deploy) rather than creating a new standalone script. We aim to keep the scripts directory simple and easy to understand by consolidating functionality where possible while maintaining clear, distinct purposes for each primary script. The main script now includes functionality that was previously in separate scripts like dev-setup and dev for better consolidation.
