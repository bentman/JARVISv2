# Linux Development Tools Setup

Quick reference for setting up the JARVISv2 development environment on Linux.

## Prerequisites

### Install Git
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install -y git

# CentOS/RHEL/Fedora
sudo dnf install -y git
# OR for older systems
sudo yum install -y git

# Arch Linux
sudo pacman -S git
```

### Install Python 3.11+ and pip
```bash
# Ubuntu/Debian
sudo apt install -y python3 python3-pip python3-venv

# CentOS/RHEL/Fedora
sudo dnf install -y python3 python3-pip
# OR for older systems
sudo yum install -y python3 python3-pip

# Arch Linux
sudo pacman -S python python python-pip
```

### Install Node.js and npm
```bash
# Option 1: Using NodeSource repository (recommended)
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs

# CentOS/RHEL/Fedora
curl -fsSL https://rpm.nodesource.com/setup_lts.x | sudo bash -
sudo dnf install -y nodejs

# Option 2: Using Node Version Manager (NVM)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install --lts
nvm use --lts
```

### Install Docker
```bash
# Ubuntu/Debian - Automatic installation script
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER # Add current user to docker group

# Or manual installation for Ubuntu/Debian
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# CentOS/RHEL/Fedora
sudo dnf install -y dnf-plugins-core
sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo usermod -aG docker $USER # Add current user to docker group

# Arch Linux
sudo pacman -S docker docker-compose
sudo usermod -aG docker $USER # Add current user to docker group
```

### Install Rust (for Tauri desktop app)
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source ~/.cargo/env
```

### Install Build Tools and Dependencies
```bash
# Ubuntu/Debian
sudo apt install -y build-essential cmake pkg-config libssl-dev libgtk-3-dev libwebkit2gtk-4.0-dev librsvg2-dev patchelf

# CentOS/RHEL/Fedora
sudo dnf install -y gcc gcc-c++ make cmake pkgconfig openssl-devel gtk3-devel webkit2gtk4.0-devel librsvg2-devel patchelf

# Arch Linux
sudo pacman -S base-devel cmake pkg-config openssl gtk3 webkit2gtk librsvg patchelf
```

### Install GNU Make (usually pre-installed)
```bash
# Check if already installed
make --version

# If not installed:
# Ubuntu/Debian
sudo apt install -y build-essential

# CentOS/RHEL/Fedora
sudo dnf install -y make

# Arch Linux
sudo pacman -S base-devel
```

## Verify Installations

```bash
python3 --version
node --version
npm --version
docker --version
docker compose version
git --version
rustc --version
cmake --version
make --version
```

## Project Setup

### 1. Clone the Repository
```bash
git clone https://github.com/bentman/JARVISv2.git
cd JARVISv2
```

### 2. Create Python Virtual Environment
```bash
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
```

### 3. Install Frontend Dependencies
```bash
cd frontend
npm install
```

### 4. Configure Environment Variables
```bash
# Copy the example environment file
cp .env_example .env
# Edit .env to set your configuration as needed
```

### 5. Start Development Services
```bash
# Option 1: Using Docker Compose (recommended)
docker compose up -d

# Option 2: Using development script
./scripts/dev.sh

# Option 3: Using Make
make dev

# Option 4: Manual setup
# Terminal 1: Start backend
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2: Start frontend
cd frontend
npm run dev
```

### 6. Download AI Models
```bash
# Full model set
./scripts/get-models.sh

# Minimal model set
./scripts/setup/get-modelsmin.sh
```

### 7. Verify Model Downloads
```bash
# Linux/macOS
./tests/verify-models.sh
```

## Common Development Commands

| Command | Description |
|---------|-------------|
| `./scripts/dev.sh` | Start both backend and frontend in development mode |
| `docker compose up -d` | Start backend services with Docker |
| `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload` | Start backend only |
| `cd frontend && npm run dev` | Start frontend only |
| `cd backend && source .venv/bin/activate && pytest` | Run backend tests |
| `./scripts/cleanup.sh` | Clean build artifacts |
| `make setup` | Setup entire development environment |
| `make test` | Run all tests |
| `./scripts/get-models.sh` | Download AI models |

## Tauri Desktop App Development

### Install Tauri CLI
```bash
cargo install tauri-cli --version "^1"
```

### Development
```bash
cd frontend
npm run tauri dev
```

### Production Build
```bash
cd frontend
npm run tauri build
```

## Troubleshooting

### If Docker requires sudo
After installing Docker, you may need to log out and log back in for group changes to take effect, or run:
```bash
newgrp docker
```

### If Python packages fail to install
Make sure you're using the virtual environment:
```bash
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
```

### If Node.js version is too old
Use NVM to install a newer version:
```bash
nvm install --lts
nvm use --lts
