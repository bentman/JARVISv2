# Local AI Assistant - Validation Script

This script helps validate that all files have been properly moved and the project is ready for development.

## 📋 Validation Checklist

Run through each of these steps to ensure the project is properly set up:

### 1. Directory Structure Validation
```bash
# Check that all main directories exist
ls -la
# Should show:
# - backend/
# - frontend/
# - Documentation files (README.md, INSTALLATION.md, etc.)

# Check backend structure
ls -la backend/
# Should show:
# - app/
# - Dockerfile
# - requirements.txt

# Check frontend structure
ls -la frontend/
# Should show:
# - src/
# - src-tauri/
# - package.json
# - index.html
```

### 2. Backend Validation
```bash
# Check backend app structure
ls -la backend/app/
# Should show:
# - main.py
# - core/
# - api/
# - models/
# - services/

# Check API structure
ls -la backend/app/api/v1/endpoints/
# Should show:
# - chat.py
# - hardware.py
# - memory.py
# - privacy.py
# - voice.py

# Check services
ls -la backend/app/services/
# Should show:
# - hardware_detector.py
# - memory_service.py
# - model_router.py
# - privacy_service.py
# - voice_service.py

# Verify requirements file
cat backend/requirements.txt
# Should show all required Python packages
```

### 3. Frontend Validation
```bash
# Check frontend src structure
ls -la frontend/src/
# Should show:
# - App.tsx
# - main.tsx
# - index.css
# - components/
# - services/

# Check components
ls -la frontend/src/components/
# Should show:
# - ChatInterface.tsx

# Check services
ls -la frontend/src/services/
# Should show:
# - index.ts
# - voiceService.ts

# Check Tauri structure
ls -la frontend/src-tauri/
# Should show:
# - Cargo.toml
# - tauri.conf.json
# - src/
```

### 4. Configuration Files Validation
```bash
# Check Docker configuration
cat backend/Dockerfile
cat docker-compose.yml

# Check package.json
cat frontend/package.json

# Check Makefile
cat Makefile

# Check gitignore
cat .gitignore
```

### 5. Documentation Validation
```bash
# List all documentation files
ls -la *.md
# Should show:
# - README.md
# - INSTALLATION.md
# - DEPLOYMENT.md
# - TESTING.md
# - PROJECT_PLAN.md
# - SUMMARY.md
# - CHECKLIST.md
# - FILE_STRUCTURE.md
# - Minimal_Local_AI_Assistant_PRD.md
```

## 🧪 Development Environment Setup

### Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Verify installation
npm list
```

## ▶️ Next Steps

After completing the validation steps above, you can proceed with development:

1. **Start the backend server**:
   ```bash
   # Navigate to backend directory
   cd backend
   
   # Activate virtual environment (Windows)
   venv\Scripts\activate
   
   # Start the server
   uvicorn app.main:app --reload
   ```

2. **Start the frontend application**:
   ```bash
   # In a new terminal, navigate to frontend directory
   cd frontend
   
   # Start the frontend
   npm run tauri dev
   ```

3. **Run tests**:
   ```bash
   # Backend tests
   cd backend
   python -m pytest tests/
   
   # Frontend tests
   cd frontend
   npm test
   ```

## ▶️ Quick Start Commands

### Using Makefile (Recommended)
```bash
# Install all dependencies
make setup

# Start backend in development mode
make backend-dev

# Start frontend in development mode
make frontend-dev

# Start both backend and frontend
make dev

# Run tests
make test

# Build for production
make build

# Clean build artifacts
make clean
```

### Manual Commands
```bash
# Start backend
cd backend
uvicorn app.main:app --reload

# Start frontend
cd frontend
npm run tauri dev

# Build backend Docker image
cd backend
docker build -t local-ai-assistant-backend .

# Build frontend desktop app
cd frontend
npm run tauri build
```

## 🧪 Testing Validation

### Backend Testing
```bash
# Run backend tests
cd backend
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=app
```

### Frontend Testing
```bash
# Run frontend tests
cd frontend
npm test

# Run tests with coverage
npm test -- --coverage
```

## 🐳 Docker Validation

### Build and Run with Docker Compose
```bash
# Build and start services
docker-compose up --build

# Check running containers
docker-compose ps

# View logs
docker-compose logs backend

# Stop services
docker-compose down
```

## ✅ Success Criteria

After validation, you should see:
1. ✅ All directory structures match the expected layout
2. ✅ All required files are present and readable
3. ✅ Backend dependencies install without errors
4. ✅ Frontend dependencies install without errors
5. ✅ Backend server starts without errors
6. ✅ Frontend application loads without errors
7. ✅ Docker builds successfully
8. ✅ All tests pass

## 🆘 Troubleshooting

### Common Issues

1. **Missing dependencies**:
   ```bash
   # Reinstall dependencies
   cd backend && pip install -r requirements.txt
   cd frontend && npm install
   ```

2. **Port conflicts**:
   ```bash
   # Check if ports are in use
   netstat -an | grep 8000  # Backend
   # Change ports in docker-compose.yml if needed
   ```

3. **Docker issues**:
   ```bash
   # Check Docker is running
   docker version
   
   # Restart Docker Desktop if needed
   ```

4. **Python virtual environment issues**:
   ```bash
   # Recreate virtual environment
   cd backend
   rm -rf venv
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

## 📞 Support

If you encounter issues that aren't resolved by the troubleshooting steps:

1. Check the project documentation files for specific instructions
2. Verify file permissions and ownership
3. Ensure all required software (Python, Node.js, Rust, Docker) is installed
4. Check the project's issue tracker or contact maintainers

---
*This validation script ensures your Local AI Assistant project is properly set up and ready for development.*