#!/bin/bash

set -e

echo "🤖 Starting Local-First AI Assistant"
echo "=================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if GPU is available
HAS_GPU=false
if command -v nvidia-smi &> /dev/null; then
    if nvidia-smi > /dev/null 2>&1; then
        echo "✅ NVIDIA GPU detected"
        HAS_GPU=true
    fi
fi

# Determine Docker Compose profile
if [ "$HAS_GPU" = true ]; then
    PROFILE="gpu"
    echo "🚀 Using GPU-accelerated profile"
else
    PROFILE="cpu-only"
    echo "🔄 Using CPU-only profile"
fi

# Check available memory
TOTAL_MEM_KB=$(grep MemTotal /proc/meminfo 2>/dev/null | awk '{print $2}' || echo "0")
TOTAL_MEM_GB=$((TOTAL_MEM_KB / 1024 / 1024))

if [ "$TOTAL_MEM_GB" -lt 8 ]; then
    echo "⚠️  Warning: Only ${TOTAL_MEM_GB}GB RAM detected. Minimum 8GB recommended."
fi

echo "💾 Available Memory: ${TOTAL_MEM_GB}GB"

# Create necessary directories
mkdir -p backend/data
mkdir -p ollama_data

# Start the services
echo "🔧 Starting backend services..."
docker-compose --profile $PROFILE up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 5

# Check if backend is healthy
echo "🔍 Checking backend health..."
max_attempts=30
attempt=1

while [ $attempt -le $max_attempts ]; do
    if curl -s http://localhost:8080/health > /dev/null 2>&1; then
        echo "✅ Backend is healthy!"
        break
    fi
    
    if [ $attempt -eq $max_attempts ]; then
        echo "❌ Backend failed to start after $max_attempts attempts"
        echo "🔍 Checking logs..."
        docker-compose --profile $PROFILE logs backend
        exit 1
    fi
    
    echo "⏳ Attempt $attempt/$max_attempts - Backend not ready yet..."
    sleep 2
    attempt=$((attempt + 1))
done

echo ""
echo "🎉 AI Assistant is ready!"
echo "=================================="
echo "📍 Backend API: http://localhost:8080"
echo "🏥 Health Check: http://localhost:8080/health"
echo "🔧 Hardware Info: http://localhost:8080/hardware"
echo ""

# Check if we should start the frontend
if [ "$1" = "--frontend-only" ]; then
    echo "🖥️  Starting frontend development server..."
    cd frontend
    npm run dev
elif [ "$1" = "--build-frontend" ]; then
    echo "🏗️  Building and starting frontend..."
    cd frontend
    npm run tauri build
else
    echo "🖥️  To start the frontend:"
    echo "   Development: cd frontend && npm run dev"
    echo "   Production:  cd frontend && npm run tauri build"
    echo ""
    echo "🔧 To view logs: docker-compose --profile $PROFILE logs -f"
    echo "🛑 To stop: docker-compose --profile $PROFILE down"
fi