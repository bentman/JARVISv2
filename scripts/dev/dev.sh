#!/usr/bin/env bash
set -euo pipefail

API_PORT=${1:-8000}

echo "Starting backend (Docker Compose) and frontend (Vite)..."

docker compose up -d

if [ ! -d frontend/node_modules ]; then
  echo "Installing frontend dependencies..."
  (cd frontend && npm install)
fi

(cd frontend && npm run dev)