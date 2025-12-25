param(
  [string]$ApiPort = "8000"
)

Write-Host "Starting backend (Docker Compose) and frontend (Vite)..."

# Start backend
docker compose up -d | Out-Null

# Install frontend deps on first run
if (-Not (Test-Path "frontend/node_modules")) {
  Write-Host "Installing frontend dependencies..."
  pushd frontend
  npm install
  popd
}

# Start Vite dev server
pushd frontend
npm run dev
popd