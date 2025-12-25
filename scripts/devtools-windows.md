# Windows Development Tools Setup

Quick reference for setting up the JARVISv2 development environment on Windows.

## Prerequisites

### Install Git
```powershell
winget install --id Git.Git -e
```

### Install Python 3.11+
```powershell
winget install --id Python.Python.3.12 -e
```

### Install Node.js and npm
```powershell
winget install --id OpenJS.NodeJS -e
```

### Install Docker Desktop
```powershell
winget install --id Docker.DockerDesktop
```

### Install Rust (for Tauri desktop app)
```powershell
winget install --id Rustlang.Rustup -e
```

### Install C++ Build Tools
```powershell
winget install --id Microsoft.VisualStudio.2022.BuildTools --override "--add Microsoft.VisualStudio.Component.VC.Tools.x86.x64"
```

### Install CMake
```powershell
winget install --id Kitware.CMake -e
```

### Install GNU Make (optional but recommended)
```powershell
winget install --id GnuWin32.Make
# OR install via Chocolatey if available
choco install make
```

## Verify Installations

```powershell
python --version
node --version
npm --version
docker --version
git --version
rustc --version
cmake --version
make --version  # if installed
```

## Project Setup

### 1. Clone the Repository
```powershell
git clone https://github.com/bentman/JARVISv2.git
cd JARVISv2
```

### 2. Create Python Virtual Environment
```powershell
python -m venv backend\.venv
backend\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

### 3. Install Frontend Dependencies
```powershell
cd frontend
npm install
```

### 4. Configure Environment Variables
```powershell
# Copy the example environment file
Copy-Item .env_example .env
# Edit .env to set your configuration as needed
```

### 5. Start Development Services
```powershell
# Option 1: Using Docker Compose (recommended)
docker compose up -d

# Option 2: Using development script
.\scripts\dev.ps1

# Option 3: Using Make (if GNU Make is available)
make dev

# Option 4: Manual setup
# Terminal 1: Start backend
cd backend
backend\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload

# Terminal 2: Start frontend
cd frontend
npm run dev
```

### 6. Download AI Models
```powershell
# Full model set
.\scripts\get-models.ps1

# Minimal model set
.\scripts\get-modelsmin.ps1
```

### 7. Verify Model Downloads
```powershell
# Windows
.\tests\verify-models.ps1
```

## Common Development Commands

| Command | Description |
|---------|-------------|
| `.\scripts\dev.ps1` | Start both backend and frontend in development mode |
| `docker compose up -d` | Start backend services with Docker |
| `cd backend && backend\.venv\Scripts\Activate.ps1 && uvicorn app.main:app --reload` | Start backend only |
| `cd frontend && npm run dev` | Start frontend only |
| `cd backend && backend\.venv\Scripts\Activate.ps1 && pytest` | Run backend tests |
| `.\scripts\cleanup.ps1` | Clean build artifacts |
| `make setup` | Setup entire development environment (if Make is available) |
| `make test` | Run all tests |
| `.\scripts\get-models.ps1` | Download AI models |

## Tauri Desktop App Development

### Install Tauri CLI
```powershell
cargo install tauri-cli --version "^1"
```

### Development
```powershell
cd frontend
npm run tauri dev
```

### Production Build
```powershell
cd frontend
npm run tauri build
```
