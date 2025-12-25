<#
.SYNOPSIS
Sets up the development environment for the Local AI Assistant project using the development Docker configuration.

.DESCRIPTION
This script prepares a complete development environment for the Local AI Assistant project. It handles model downloads (if needed),
starts development services using the development Docker configuration, and prepares the frontend for development work. The development
configuration includes volume mounts for live reloading and development-optimized settings.

.PARAMETER Environment
Specifies the environment type: 'dev' for development or 'prod' for production. Default is 'dev'.

.PARAMETER SkipModels
Skip the model download step. Default is $false (downloads models).

.PARAMETER SkipFrontend
Skip the frontend setup step. Default is $false (sets up frontend).

.PARAMETER ModelsEnvironment
Specify which models to download: 'dev' for development (smaller) or 'prod' for production (larger). Default is same as Environment parameter.

.PARAMETER ModelsDir
Directory to download models to. Default is 'models'.

.EXAMPLE
./dev-setup.ps1
Sets up the development environment with all components using development models.

.EXAMPLE
./dev-setup.ps1 -SkipModels
Sets up the development environment without downloading models (assuming they're already present).

.EXAMPLE
./dev-setup.ps1 -Environment prod -ModelsEnvironment dev
Sets up a production-like environment but uses development models for faster iteration during testing.
#>

param(
    [ValidateSet('dev', 'prod')]
    [string]$Environment = 'dev',
    
    [bool]$SkipModels = $false,
    
    [bool]$SkipFrontend = $false,
    
    [ValidateSet('dev', 'prod')]
    [string]$ModelsEnvironment = '',
    
    [string]$ModelsDir = 'models'
)

# Set default ModelsEnvironment to match Environment if not specified
if ([string]::IsNullOrEmpty($ModelsEnvironment)) {
    $ModelsEnvironment = $Environment
}

Write-Host "Setting up Local AI Assistant development environment..." -ForegroundColor Green
Write-Host "Environment: $Environment" -ForegroundColor Yellow
Write-Host "Models Environment: $ModelsEnvironment" -ForegroundColor Yellow

# Check prerequisites
Write-Host "`nChecking prerequisites..." -ForegroundColor Cyan

# Check for Docker
try {
    $dockerVersion = docker --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Docker is not installed or not in PATH. Please install Docker Desktop."
        exit 1
    }
    Write-Host "✓ Docker: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Warning "Docker is not installed or not in PATH. Please install Docker Desktop."
    exit 1
}

# Check for Node.js (if not skipping frontend)
if (-not $SkipFrontend) {
    try {
        $nodeVersion = node --version 2>$null
        $npmVersion = npm --version 2>$null
        Write-Host "✓ Node.js: $nodeVersion" -ForegroundColor Green
        Write-Host "✓ npm: $npmVersion" -ForegroundColor Green
    } catch {
        Write-Warning "Node.js is not installed or not in PATH. Please install Node.js."
        exit 1
    }
}

# Check for Python (for model verification and scripts)
try {
    $pythonVersion = python --version 2>$null
    Write-Host "✓ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Warning "Python is not installed or not in PATH. Please install Python 3.11+."
    exit 1
}

# Step 1: Download models (if not skipped)
if (-not $SkipModels) {
    Write-Host "`nStep 1: Downloading models for $ModelsEnvironment environment..." -ForegroundColor Cyan
    $scriptParams = @{
        Environment = $ModelsEnvironment
        ModelsDir = $ModelsDir
    }
    & "$PSScriptRoot/get-models.ps1" @scriptParams
    Write-Host "Models download completed.`n" -ForegroundColor Green
}

# Step 2: Start development services
Write-Host "Step 2: Starting development services..." -ForegroundColor Cyan

# Select compose file based on environment
$composeFile = if ($Environment -eq 'dev') { 'docker-compose.dev.yml' } else { 'docker-compose.yml' }
Write-Host "Using compose file: $composeFile" -ForegroundColor Yellow

# Start services using appropriate compose file
try {
    docker compose -f $composeFile up -d
    Write-Host "Services started using $composeFile" -ForegroundColor Green
} catch {
    Write-Warning "Failed to start services with $composeFile : $($_.Exception.Message)"
    exit 1
}

# Step 3: Set up frontend (if not skipped)
if (-not $SkipFrontend) {
    Write-Host "Step 3: Setting up frontend development environment..." -ForegroundColor Cyan
    
    if (-Not (Test-Path "frontend")) {
        Write-Warning "Frontend directory not found. Please ensure you're running this from the project root."
        exit 1
    }
    
    Set-Location frontend
    
    # Install frontend dependencies if node_modules doesn't exist
    if (-Not (Test-Path "node_modules")) {
        Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
        npm install
    } else {
        Write-Host "Frontend dependencies already installed, skipping." -ForegroundColor Gray
    }
    
    Write-Host "Frontend setup completed." -ForegroundColor Green
    Set-Location ..
}

# Wait for backend to be ready
Write-Host "`nWaiting for backend services to be ready..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

$maxRetries = 30
$retryCount = 0
$servicesReady = $false

while ($retryCount -lt $maxRetries -and -not $servicesReady) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health/services" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            $servicesReady = $true
            Write-Host "Backend services are ready!" -ForegroundColor Green
            break
        }
    } catch {
        # Ignore errors and continue waiting
    }
    
    $retryCount++
    Write-Host "Waiting for backend services... (attempt $retryCount/$maxRetries)" -ForegroundColor Yellow
    Start-Sleep -Seconds 10
}

if (-not $servicesReady) {
    Write-Warning "Backend services failed to become ready within timeout"
    try {
        docker compose -f $composeFile logs backend
    } catch {
        Write-Host "Could not retrieve logs: $($_.Exception.Message)" -ForegroundColor Red
    }
    exit 1
}

Write-Host "`nDevelopment environment setup completed successfully!" -ForegroundColor Green
Write-Host "Environment: $Environment" -ForegroundColor Green
Write-Host "Models: $ModelsEnvironment" -ForegroundColor Green

if ($Environment -eq 'dev') {
    Write-Host "`nFor development, you can now:" -ForegroundColor Cyan
    Write-Host "  - Access the UI at http://localhost:5173" -ForegroundColor White
    Write-Host "  - Access the API at http://localhost:8000" -ForegroundColor White
    Write-Host "  - Run tests with: cd backend && python -m pytest" -ForegroundColor White
    Write-Host "  - Start frontend dev server: cd frontend && npm run dev" -ForegroundColor White
} else {
    Write-Host "`nFor production simulation, services are running." -ForegroundColor Cyan
    Write-Host "  - API is available at http://localhost:8000" -ForegroundColor White
    Write-Host "  - Check health at: http://localhost:8000/api/v1/health/services" -ForegroundColor White
}

Write-Host "`nTo stop services, run: docker compose -f $composeFile down" -ForegroundColor Gray
