#!/bin/bash

# --- 1. Prerequisite Checks ---
echo "--- Checking Prerequisites ---"
if ! command -v docker &> /dev/null
then
    echo "Docker is not installed. Please install Docker Desktop and try again."
    exit 1
fi

DOCKER_VERSION=$(docker --version)
if [[ ! "$DOCKER_VERSION" =~ "Docker version" ]]; then
    echo "Could not find a valid Docker installation."
    exit 1
fi

echo "Docker is installed: $DOCKER_VERSION"

echo "Checking for Docker Model Runner..."
if ! docker model ls &> /dev/null
then
    echo "Docker Model Runner (DMR) is not enabled. Please enable it in Docker Desktop settings."
    exit 1
fi
echo "DMR is enabled. Proceeding with setup."

# --- 2. Build and Launch Containers ---
echo "--- Building and launching backend ---"
docker-compose -f docker-compose.yml up --build -d

echo "--- Setup Complete! ---"
echo "The backend is now running. You can check its status with: docker-compose logs backend"
echo "Next, you will need to build and run the Tauri frontend to continue."