<#
.SYNOPSIS
Sets up the Local AI Assistant development or production environment based on specified parameters.

.DESCRIPTION
This script handles the complete setup process for either development or production environments. It manages
model downloads, dependency installations, and service startup based on the specified environment type.

.PARAMETER Environment
Specifies the environment: 'dev' for development or 'prod' for production. Default is 'dev'.

.PARAMETER SkipModels
Skip model download step. Default is $false (downloads models).

.PARAMETER SkipDeps
Skip dependency installation step. Default is $false (installs dependencies).

.PARAMETER SkipServices
Skip service startup step. Default is $false (starts services).

.PARAMETER ModelsDir
Directory to download models to. Default is 'models'.

.PARAMETER ModelsEnvironment
Specify which models to download: 'dev' for development models or 'prod' for production models. Default is same as Environment parameter.

.EXAMPLE
./setup.ps1 -Environment dev
Sets up a development environment with all steps performed using development models.

.EXAMPLE
./setup.ps1 -Environment prod -ModelsEnvironment dev
Sets up a production environment but uses development models for testing purposes.
#>

param(
    [ValidateSet('dev', 'prod')]
    [string]$Environment = 'dev',
    
    [bool]$SkipModels = $false,
    
    [bool]$SkipDeps = $false,
    
    [bool]$SkipServices = $false,
    
    [string]$ModelsDir = 'models',
    
    [ValidateSet('dev', 'prod', '')]
    [string]$ModelsEnvironment = ''
)

# Set default ModelsEnvironment to match Environment if not specified
if ([string]::IsNullOrEmpty($ModelsEnvironment)) {
    $ModelsEnvironment = $Environment
}

Write-Host "Setting up Local AI Assistant environment: $Environment" -ForegroundColor Green
Write-Host "Models environment: $ModelsEnvironment" -ForegroundColor Green

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

# Check for Node.js
try {
    $nodeVersion = node --version 2>$null
    $npmVersion = npm --version 2>$null
    Write-Host "✓ Node.js: $nodeVersion" -ForegroundColor Green
    Write-Host "✓ npm: $npmVersion" -ForegroundColor Green
} catch {
    Write-Warning "Node.js is not installed or not in PATH. Please install Node.js."
    exit 1
}

# Check for Python (if not skipping deps)
if (-not $SkipDeps) {
    try {
        $pythonVersion = python --version 2>$null
        Write-Host "✓ Python: $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Warning "Python is not installed or not in PATH. Please install Python 3.11+."
        exit 1
    }
}

# Step 1: Download models (if not skipped)
if (-not $SkipModels) {
    Write-Host "`nStep 1: Downloading models..." -ForegroundColor Cyan
    $scriptParams = @{
        Environment = $ModelsEnvironment
        ModelsDir = $ModelsDir
    }
    & "$PSScriptRoot/get-models.ps1" @scriptParams
    Write-Host "Models download completed.`n" -ForegroundColor Green
}

# Step 2: Install dependencies (if not skipped)
if (-not $SkipDeps) {
    Write-Host "Step 2: Installing dependencies..." -ForegroundColor Cyan
    
    # Create virtual environment if it doesn't exist
    if (-Not (Test-Path "backend/.venv")) {
        Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
        python -m venv backend/.venv
    }
    
    # Activate virtual environment and install backend dependencies
    Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
    & backend/.venv/Scripts/Activate.ps1
    pip install -r backend/requirements.txt
    
    # Install frontend dependencies
    if (-Not (Test-Path "frontend/node_modules")) {
        Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
        Set-Location frontend
        npm install
        Set-Location ..
    }
    Write-Host "Dependency installation completed.`n" -ForegroundColor Green
}

# Step 3: Start services (if not skipped)
if (-not $SkipServices) {
    Write-Host "Step 3: Starting services..." -ForegroundColor Cyan
    
    # Select compose file based on environment
    $composeFile = if ($Environment -eq 'dev') { 'docker-compose.dev.yml' } else { 'docker-compose.yml' }
    Write-Host "Using compose file: $composeFile" -ForegroundColor Yellow
    
    # Start services using appropriate compose file
    docker compose -f $composeFile up -d
    
    Write-Host "Services started using $composeFile`n" -ForegroundColor Green
}

Write-Host "Setup completed for $Environment environment!" -ForegroundColor Green
Write-Host "Environment: $Environment" -ForegroundColor Green
Write-Host "Models: $ModelsEnvironment" -ForegroundColor Green

if ($Environment -eq 'dev') {
    Write-Host "`nFor development, you can now:" -ForegroundColor Cyan
    Write-Host "  - Access the UI at http://localhost:5173" -ForegroundColor White
    Write-Host "  - Access the API at http://localhost:8000" -ForegroundColor White
    Write-Host "  - Run tests with: cd backend && python -m pytest" -ForegroundColor White
} else {
    Write-Host "`nFor production, services are running." -ForegroundColor Cyan
    Write-Host "  - API is available at http://localhost:8000" -ForegroundColor White
    Write-Host "  - Check health at: http://localhost:8000/api/v1/health/services" -ForegroundColor White
}
