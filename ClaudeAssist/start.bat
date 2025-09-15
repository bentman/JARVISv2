@echo off
setlocal enabledelayedexpansion

echo 🤖 Starting Local-First AI Assistant
echo ==================================

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker and try again.
    pause
    exit /b 1
)

REM Check if GPU is available
set HAS_GPU=false
nvidia-smi >nul 2>&1
if not errorlevel 1 (
    echo ✅ NVIDIA GPU detected
    set HAS_GPU=true
    set PROFILE=gpu
    echo 🚀 Using GPU-accelerated profile
) else (
    set PROFILE=cpu-only
    echo 🔄 Using CPU-only profile
)

REM Create necessary directories
if not exist "backend\data" mkdir "backend\data"
if not exist "ollama_data" mkdir "ollama_data"

REM Start the services
echo 🔧 Starting backend services...
docker-compose --profile %PROFILE% up -d

REM Wait for services to be ready
echo ⏳ Waiting for services to start...
timeout /t 5 /nobreak >nul

REM Check if backend is healthy
echo 🔍 Checking backend health...
set max_attempts=30
set attempt=1

:check_health
curl -s http://localhost:8080/health >nul 2>&1
if not errorlevel 1 (
    echo ✅ Backend is healthy!
    goto health_check_done
)

if !attempt! geq %max_attempts% (
    echo ❌ Backend failed to start after %max_attempts% attempts
    echo 🔍 Checking logs...
    docker-compose --profile %PROFILE% logs backend
    pause
    exit /b 1
)

echo ⏳ Attempt !attempt!/%max_attempts% - Backend not ready yet...
timeout /t 2 /nobreak >nul
set /a attempt+=1
goto check_health

:health_check_done

echo.
echo 🎉 AI Assistant is ready!
echo ==================================
echo 📍 Backend API: http://localhost:8080
echo 🏥 Health Check: http://localhost:8080/health
echo 🔧 Hardware Info: http://localhost:8080/hardware
echo.

REM Check arguments
if "%1"=="--frontend-only" (
    echo 🖥️  Starting frontend development server...
    cd frontend
    npm run dev
) else if "%1"=="--build-frontend" (
    echo 🏗️  Building and starting frontend...
    cd frontend
    npm run tauri build
) else (
    echo 🖥️  To start the frontend:
    echo    Development: cd frontend ^&^& npm run dev
    echo    Production:  cd frontend ^&^& npm run tauri build
    echo.
    echo 🔧 To view logs: docker-compose --profile %PROFILE% logs -f
    echo 🛑 To stop: docker-compose --profile %PROFILE% down
    pause
)