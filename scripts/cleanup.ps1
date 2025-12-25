<#
.SYNOPSIS
Cleans up development artifacts, build artifacts, and optionally stops Docker services.

.DESCRIPTION
This script removes various development and build artifacts from the project directory.
It can optionally stop Docker services as part of the cleanup process.

.PARAMETER NoDocker
Skip stopping Docker services during cleanup. Default is $false (stops Docker services).

.EXAMPLE
./cleanup.ps1
Performs cleanup including stopping Docker services.

.EXAMPLE
./cleanup.ps1 -NoDocker
Performs cleanup without stopping Docker services.
#>

param(
    [switch]$NoDocker = $false
)

Write-Host "Starting cleanup process..." -ForegroundColor Cyan

# Stop Docker services unless suppressed
if (-not $NoDocker) {
    Write-Host "Stopping Docker services..." -ForegroundColor Yellow
    try {
        $composeFiles = @("docker-compose.yml", "docker-compose.dev.yml", "docker-compose.prod.yml")
        
        foreach ($file in $composeFiles) {
            if (Test-Path $file) {
                Write-Host "Stopping services defined in $file..." -ForegroundColor Gray
                docker compose -f $file down 2>$null | Out-Null
            }
        }
        Write-Host "Docker services stopped." -ForegroundColor Green
    } catch {
        Write-Warning "Could not stop Docker services: $($_.Exception.Message)"
    }
}

# Remove explicit dev/build directories
$pathsToRemove = @(
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
    "coverage",
    "backend/__pycache__",
    "backend/*.pyc",
    "logs",
    "data/*",  # Clear data directory contents but keep the directory
    "storage/*"  # Clear storage directory contents but keep the directory
)

foreach ($path in $pathsToRemove) {
    if (Test-Path $path) {
        try {
            Remove-Item -Path $path -Recurse -Force -ErrorAction Stop
            Write-Host "Removed: $path" -ForegroundColor Green
        } catch {
            Write-Warning "Could not remove $path : $($_.Exception.Message)"
        }
    }
}

# Remove common cache directories recursively
$cachePatterns = @("__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".vscode", ".idea")

foreach ($pattern in $cachePatterns) {
    $items = Get-ChildItem -Path . -Recurse -Force -Directory -Name $pattern -ErrorAction SilentlyContinue
    foreach ($item in $items) {
        $fullPath = Join-Path (Split-Path $item) $item
        if (Test-Path $fullPath) {
            try {
                Remove-Item -Path $fullPath -Recurse -Force -ErrorAction Stop
                Write-Host "Removed: $fullPath" -ForegroundColor Green
            } catch {
                Write-Warning "Could not remove $fullPath : $($_.Exception.Message)"
            }
        }
    }
}

# Remove log files (keep logs dir if any)
if (Test-Path 'logs') {
    $logFiles = Get-ChildItem -Path logs -Recurse -File -Filter "*.log" -ErrorAction SilentlyContinue
    foreach ($logFile in $logFiles) {
        try {
            Remove-Item -Path $logFile.FullName -Force -ErrorAction Stop
            Write-Host "Removed log: $($logFile.FullName)" -ForegroundColor Green
        } catch {
            Write-Warning "Could not remove log $($logFile.FullName) : $($_.Exception.Message)"
        }
    }
}

# Remove coverage files
$coverageFiles = Get-ChildItem -Path . -Force -Filter ".coverage*" -ErrorAction SilentlyContinue
foreach ($covFile in $coverageFiles) {
    try {
        Remove-Item -Path $covFile.FullName -Force -ErrorAction Stop
        Write-Host "Removed coverage file: $($covFile.FullName)" -ForegroundColor Green
    } catch {
        Write-Warning "Could not remove coverage file $($covFile.FullName) : $($_.Exception.Message)"
    }
}

# Clean npm cache directories if node_modules was removed
if (Get-Command npm -ErrorAction SilentlyContinue) {
    try {
        npm cache clean --force 2>$null | Out-Null
        Write-Host "Cleaned npm cache" -ForegroundColor Green
    } catch {
        Write-Warning "Could not clean npm cache: $($_.Exception.Message)"
    }
}

Write-Host "Cleanup complete!" -ForegroundColor Green
Write-Host "Remaining notable directories (if present):" -ForegroundColor Yellow
Get-ChildItem -Force -Directory models, data, storage -ErrorAction SilentlyContinue | ForEach-Object { Write-Host "  $($_.FullName)" -ForegroundColor Yellow }
