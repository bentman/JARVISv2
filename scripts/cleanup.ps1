param(
  [switch]$NoDocker
)

# Stop Docker services unless suppressed
if (-not $NoDocker) {
  try { docker compose down --remove-orphans | Out-Null } catch { }
}

# Remove explicit dev/build directories
$paths = @(
  "backend/.venv",
  "frontend/node_modules",
  "frontend/dist",
  "frontend/.vite",
  "frontend/.parcel-cache",
  "frontend/.turbo",
  "frontend/.cache",
  "frontend/src-tauri/target",
  "frontend/src-tauri/target/release/bundle",
  "build",
  "dist",
  "target",
  "coverage"
)
foreach ($p in $paths) {
  if (Test-Path $p) { Remove-Item -Recurse -Force $p }
}

# Remove common cache directories recursively
$cacheNames = @("__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache")
foreach ($name in $cacheNames) {
  Get-ChildItem -Path . -Recurse -Force -Directory -Filter $name |
    ForEach-Object { if (Test-Path $_.FullName) { Remove-Item -Recurse -Force $_.FullName } }
}

# Remove log files (keep logs dir if any)
if (Test-Path 'logs') {
  Get-ChildItem -Path logs -Recurse -File -Filter *.log | ForEach-Object { Remove-Item -Force $_.FullName }
}

# Remove coverage files
Get-ChildItem -Path . -Force -Filter ".coverage*" -ErrorAction SilentlyContinue |
  ForEach-Object { Remove-Item -Force $_.FullName -ErrorAction SilentlyContinue }

# Summary
Write-Output "Cleanup complete."
Write-Output "Remaining notable dirs (if present):"
Get-ChildItem -Force -Directory models, data, storage -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName
