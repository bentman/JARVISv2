<#
.SYNOPSIS
Main script for the Local AI Assistant project that consolidates all essential functionality.

.DESCRIPTION
This script provides a unified interface for all common operations in the Local AI Assistant project:
- Environment setup (dev/prod)
- Model management (download, verification)
- Development workflows
- Production deployment
- Testing and verification
- Utility functions

.PARAMETER Command
Specifies the command to execute: setup, models, dev, deploy, test, verify, cleanup, voice-test, dev-setup

.PARAMETER Environment
For setup and deploy commands: 'dev' or 'prod'. Default: 'dev'

.PARAMETER SkipModels
For setup command: Skip model download. Default: $false

.PARAMETER SkipDeps
For setup command: Skip dependency installation. Default: $false

.PARAMETER SkipServices
For setup command: Skip service startup. Default: $false

.PARAMETER ModelsDir
Directory for models. Default: 'models'

.PARAMETER ModelsEnvironment
For models command: 'dev' or 'prod' models. Default: same as Environment

.EXAMPLE
./scripts/main.ps1 setup -Environment dev
Sets up a development environment with all components.

.EXAMPLE
./scripts/main.ps1 models -Environment prod
Downloads production models to the models directory.

.EXAMPLE
./scripts/main.ps1 dev
Starts development environment using docker-compose.dev.yml.

.EXAMPLE
./scripts/main.ps1 dev-setup
Sets up and starts development environment with all components.

.EXAMPLE
./scripts/main.ps1 deploy -Environment prod
Deploys to production environment.
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('setup', 'models', 'dev', 'deploy', 'test', 'verify', 'cleanup', 'voice-test', 'dev-setup')]
    [string]$Command,
    
    [ValidateSet('dev', 'prod')]
    [string]$Environment = 'dev',
    
    [bool]$SkipModels = $false,
    
    [bool]$SkipDeps = $false,
    
    [bool]$SkipServices = $false,
    
    [string]$ModelsDir = 'models',
    
    [ValidateSet('dev', 'prod')]
    [string]$ModelsEnvironment = ''
)

# Set default ModelsEnvironment to match Environment if not specified
if ([string]::IsNullOrEmpty($ModelsEnvironment)) {
    $ModelsEnvironment = $Environment
}

Write-Host "Executing command: $Command" -ForegroundColor Green

switch ($Command) {
    'setup' {
        Write-Host "Running setup for $Environment environment..." -ForegroundColor Cyan
        $setupParams = @{
            Environment = $Environment
            SkipModels = $SkipModels
            SkipDeps = $SkipDeps
            SkipServices = $SkipServices
            ModelsDir = $ModelsDir
            ModelsEnvironment = $ModelsEnvironment
        }
        # Inline setup functionality to avoid dependency on separate script
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
            
            # Create models directory if it doesn't exist
            if (-Not (Test-Path $ModelsDir)) { 
                New-Item -ItemType Directory -Path $ModelsDir | Out-Null 
                Write-Host "Created directory: $ModelsDir" -ForegroundColor Green
            }

            Set-Location $ModelsDir

            # Determine model URLs based on environment
            if ($ModelsEnvironment -eq 'dev') {
                Write-Host "Downloading development models (smaller, faster)..." -ForegroundColor Yellow
                
                # TinyLlama 1.1B Chat (Q2_K - smallest functional chat for dev)
                $TllUrl = "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q2_K.gguf?download=true"
                $TllFile = "tinyllama-1.1b-chat-v1.0.Q2_K.gguf"
            }
            else {
                Write-Host "Downloading production models (optimized for performance)..." -ForegroundColor Green
                
                # TinyLlama 1.1B Chat (Q4_K_M - balanced for production)
                $TllUrl = "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf?download=true"
                $TllFile = "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
            }

            # Download LLM model if not present
            if (-Not (Test-Path $TllFile)) {
                Write-Host "Downloading $TllFile ..." -ForegroundColor Cyan
                Invoke-WebRequest -Uri $TllUrl -OutFile $TllFile
                Write-Host "Successfully downloaded $TllFile" -ForegroundColor Green
            } else {
                Write-Host "$TllFile already exists, skipping download." -ForegroundColor Gray
            }

            # Piper English voice (common for both environments)
            $PiperUrl = "https://github.com/rhasspy/piper-voices/releases/download/en_US-amy-low/en_US-amy-low.onnx"
            $PiperFile = "en_US-amy-low.onnx"
            $PiperJsonUrl = "https://github.com/rhasspy/piper-voices/releases/download/en_US-amy-low/en_US-amy-low.onnx.json"
            $PiperJsonFile = "en_US-amy-low.onnx.json"

            if (-Not (Test-Path $PiperFile)) {
                Write-Host "Downloading $PiperFile (TTS)..." -ForegroundColor Cyan
                Invoke-WebRequest -Uri $PiperUrl -OutFile $PiperFile
                Write-Host "Successfully downloaded $PiperFile" -ForegroundColor Green
            } else {
                Write-Host "$PiperFile already exists, skipping download." -ForegroundColor Gray
            }

            if (-Not (Test-Path $PiperJsonFile)) {
                Write-Host "Downloading $PiperJsonFile (TTS Config)..." -ForegroundColor Cyan
                Invoke-WebRequest -Uri $PiperJsonUrl -OutFile $PiperJsonFile
                Write-Host "Successfully downloaded $PiperJsonFile" -ForegroundColor Green
            } else {
                Write-Host "$PiperJsonFile already exists, skipping download." -ForegroundColor Gray
            }

            # Whisper Base English (common for both environments)
            $WhisperUrl = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin?download=true"
            $WhisperFile = "ggml-base.en.bin"
            if (-Not (Test-Path $WhisperFile)) {
                Write-Host "Downloading $WhisperFile (STT)..." -ForegroundColor Cyan
                Invoke-WebRequest -Uri $WhisperUrl -OutFile $WhisperFile
                Write-Host "Successfully downloaded $WhisperFile" -ForegroundColor Green
            } else {
                Write-Host "$WhisperFile already exists, skipping download." -ForegroundColor Gray
            }

            # Generate checksums for all model files
            Write-Host "Generating checksums..." -ForegroundColor Cyan
            $checks = @{}
            Get-ChildItem -File | Where-Object { $_.Extension -in ".gguf", ".onnx", ".bin" } | ForEach-Object {
                $sha = Get-FileHash -Algorithm SHA256 -Path $_.FullName
                $checks[$_.Name] = $sha.Hash
            }
            ($checks | ConvertTo-Json -Depth 3) | Out-File -FilePath "checksums.json" -Encoding utf8
            Write-Host "Checksums written to checksums.json" -ForegroundColor Green

            Set-Location ..
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
    }
    
    'models' {
        Write-Host "Managing models for $ModelsEnvironment environment..." -ForegroundColor Cyan
        
        # Create models directory if it doesn't exist
        if (-Not (Test-Path $ModelsDir)) { 
            New-Item -ItemType Directory -Path $ModelsDir | Out-Null 
            Write-Host "Created directory: $ModelsDir" -ForegroundColor Green
        }

        Set-Location $ModelsDir

        # Determine model URLs based on environment
        if ($ModelsEnvironment -eq 'dev') {
            Write-Host "Downloading development models (smaller, faster)..." -ForegroundColor Yellow
            
            # TinyLlama 1.1B Chat (Q2_K - smallest functional chat for dev)
            $TllUrl = "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q2_K.gguf?download=true"
            $TllFile = "tinyllama-1.1b-chat-v1.0.Q2_K.gguf"
        }
        else {
            Write-Host "Downloading production models (optimized for performance)..." -ForegroundColor Green
            
            # TinyLlama 1.1B Chat (Q4_K_M - balanced for production)
            $TllUrl = "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf?download=true"
            $TllFile = "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
        }

        # Download LLM model if not present
        if (-Not (Test-Path $TllFile)) {
            Write-Host "Downloading $TllFile ..." -ForegroundColor Cyan
            Invoke-WebRequest -Uri $TllUrl -OutFile $TllFile
            Write-Host "Successfully downloaded $TllFile" -ForegroundColor Green
        } else {
            Write-Host "$TllFile already exists, skipping download." -ForegroundColor Gray
        }

        # Piper English voice (common for both environments)
        $PiperUrl = "https://github.com/rhasspy/piper-voices/releases/download/en_US-amy-low/en_US-amy-low.onnx"
        $PiperFile = "en_US-amy-low.onnx"
        $PiperJsonUrl = "https://github.com/rhasspy/piper-voices/releases/download/en_US-amy-low/en_US-amy-low.onnx.json"
        $PiperJsonFile = "en_US-amy-low.onnx.json"

        if (-Not (Test-Path $PiperFile)) {
            Write-Host "Downloading $PiperFile (TTS)..." -ForegroundColor Cyan
            Invoke-WebRequest -Uri $PiperUrl -OutFile $PiperFile
            Write-Host "Successfully downloaded $PiperFile" -ForegroundColor Green
        } else {
            Write-Host "$PiperFile already exists, skipping download." -ForegroundColor Gray
        }

        if (-Not (Test-Path $PiperJsonFile)) {
            Write-Host "Downloading $PiperJsonFile (TTS Config)..." -ForegroundColor Cyan
            Invoke-WebRequest -Uri $PiperJsonUrl -OutFile $PiperJsonFile
            Write-Host "Successfully downloaded $PiperJsonFile" -ForegroundColor Green
        } else {
            Write-Host "$PiperJsonFile already exists, skipping download." -ForegroundColor Gray
        }

        # Whisper Base English (common for both environments)
        $WhisperUrl = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin?download=true"
        $WhisperFile = "ggml-base.en.bin"
        if (-Not (Test-Path $WhisperFile)) {
            Write-Host "Downloading $WhisperFile (STT)..." -ForegroundColor Cyan
            Invoke-WebRequest -Uri $WhisperUrl -OutFile $WhisperFile
            Write-Host "Successfully downloaded $WhisperFile" -ForegroundColor Green
        } else {
            Write-Host "$WhisperFile already exists, skipping download." -ForegroundColor Gray
        }

        # Generate checksums for all model files
        Write-Host "Generating checksums..." -ForegroundColor Cyan
        $checks = @{}
        Get-ChildItem -File | Where-Object { $_.Extension -in ".gguf", ".onnx", ".bin" } | ForEach-Object {
            $sha = Get-FileHash -Algorithm SHA256 -Path $_.FullName
            $checks[$_.Name] = $sha.Hash
        }
        ($checks | ConvertTo-Json -Depth 3) | Out-File -FilePath "checksums.json" -Encoding utf8
        Write-Host "Checksums written to checksums.json" -ForegroundColor Green

        Set-Location ..
        Write-Host "Model download complete!" -ForegroundColor Green
        Write-Host "Environment: $ModelsEnvironment" -ForegroundColor Green
        Write-Host "Models directory: $(Resolve-Path .)" -ForegroundColor Green
    }
    
    'dev' {
        Write-Host "Starting development environment..." -ForegroundColor Cyan
        if (Test-Path "docker-compose.dev.yml") {
            docker compose -f docker-compose.dev.yml up -d
            Write-Host "Development services started using docker-compose.dev.yml" -ForegroundColor Green
            Write-Host "Access the UI at http://localhost:5173" -ForegroundColor Yellow
            Write-Host "Access the API at http://localhost:8000" -ForegroundColor Yellow
        } else {
            Write-Host "Error: docker-compose.dev.yml not found" -ForegroundColor Red
        }
    }

    'dev-setup' {
        Write-Host "Running development setup..." -ForegroundColor Cyan
        # This command combines setup with dev environment settings
        $setupParams = @{
            Environment = 'dev'
            SkipModels = $SkipModels
            SkipDeps = $SkipDeps
            SkipServices = $false  # Always start services for dev-setup
            ModelsDir = $ModelsDir
            ModelsEnvironment = $ModelsEnvironment
        }
        # Execute the setup functionality with dev settings
        # We'll reuse the setup logic but ensure services are started
        $originalSkipServices = $SkipServices
        $SkipServices = $false # Override to ensure services start in dev-setup
        
        # Run the same setup process as above but with dev-specific settings
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
            
            # Create models directory if it doesn't exist
            if (-Not (Test-Path $ModelsDir)) { 
                New-Item -ItemType Directory -Path $ModelsDir | Out-Null 
                Write-Host "Created directory: $ModelsDir" -ForegroundColor Green
            }

            Set-Location $ModelsDir

            # Determine model URLs based on environment
            if ($ModelsEnvironment -eq 'dev') {
                Write-Host "Downloading development models (smaller, faster)..." -ForegroundColor Yellow
                
                # TinyLlama 1.1B Chat (Q2_K - smallest functional chat for dev)
                $TllUrl = "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q2_K.gguf?download=true"
                $TllFile = "tinyllama-1.1b-chat-v1.0.Q2_K.gguf"
            }
            else {
                Write-Host "Downloading production models (optimized for performance)..." -ForegroundColor Green
                
                # TinyLlama 1.1B Chat (Q4_K_M - balanced for production)
                $TllUrl = "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf?download=true"
                $TllFile = "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
            }

            # Download LLM model if not present
            if (-Not (Test-Path $TllFile)) {
                Write-Host "Downloading $TllFile ..." -ForegroundColor Cyan
                Invoke-WebRequest -Uri $TllUrl -OutFile $TllFile
                Write-Host "Successfully downloaded $TllFile" -ForegroundColor Green
            } else {
                Write-Host "$TllFile already exists, skipping download." -ForegroundColor Gray
            }

            # Piper English voice (common for both environments)
            $PiperUrl = "https://github.com/rhasspy/piper-voices/releases/download/en_US-amy-low/en_US-amy-low.onnx"
            $PiperFile = "en_US-amy-low.onnx"
            $PiperJsonUrl = "https://github.com/rhasspy/piper-voices/releases/download/en_US-amy-low/en_US-amy-low.onnx.json"
            $PiperJsonFile = "en_US-amy-low.onnx.json"

            if (-Not (Test-Path $PiperFile)) {
                Write-Host "Downloading $PiperFile (TTS)..." -ForegroundColor Cyan
                Invoke-WebRequest -Uri $PiperUrl -OutFile $PiperFile
                Write-Host "Successfully downloaded $PiperFile" -ForegroundColor Green
            } else {
                Write-Host "$PiperFile already exists, skipping download." -ForegroundColor Gray
            }

            if (-Not (Test-Path $PiperJsonFile)) {
                Write-Host "Downloading $PiperJsonFile (TTS Config)..." -ForegroundColor Cyan
                Invoke-WebRequest -Uri $PiperJsonUrl -OutFile $PiperJsonFile
                Write-Host "Successfully downloaded $PiperJsonFile" -ForegroundColor Green
            } else {
                Write-Host "$PiperJsonFile already exists, skipping download." -ForegroundColor Gray
            }

            # Whisper Base English (common for both environments)
            $WhisperUrl = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin?download=true"
            $WhisperFile = "ggml-base.en.bin"
            if (-Not (Test-Path $WhisperFile)) {
                Write-Host "Downloading $WhisperFile (STT)..." -ForegroundColor Cyan
                Invoke-WebRequest -Uri $WhisperUrl -OutFile $WhisperFile
                Write-Host "Successfully downloaded $WhisperFile" -ForegroundColor Green
            } else {
                Write-Host "$WhisperFile already exists, skipping download." -ForegroundColor Gray
            }

            # Generate checksums for all model files
            Write-Host "Generating checksums..." -ForegroundColor Cyan
            $checks = @{}
            Get-ChildItem -File | Where-Object { $_.Extension -in ".gguf", ".onnx", ".bin" } | ForEach-Object {
                $sha = Get-FileHash -Algorithm SHA256 -Path $_.FullName
                $checks[$_.Name] = $sha.Hash
            }
            ($checks | ConvertTo-Json -Depth 3) | Out-File -FilePath "checksums.json" -Encoding utf8
            Write-Host "Checksums written to checksums.json" -ForegroundColor Green

            Set-Location ..
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

        # Start services for dev environment
        Write-Host "Starting development services..." -ForegroundColor Cyan
        docker compose -f docker-compose.dev.yml up -d
        Write-Host "Development services started using docker-compose.dev.yml`n" -ForegroundColor Green

        Write-Host "Development setup completed!" -ForegroundColor Green
        Write-Host "Access the UI at http://localhost:5173" -ForegroundColor Green
        Write-Host "Access the API at http://localhost:8000" -ForegroundColor Green
    }
    
    'deploy' {
        Write-Host "Deploying to $Environment environment..." -ForegroundColor Cyan
        
        # Ensure running as administrator for production deployment
        if ($Environment -eq 'prod') {
            $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
            if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
                Write-Warning "This script requires administrator privileges for production deployment."
                Write-Host "Please run PowerShell as Administrator." -ForegroundColor Red
                exit 1
            }
        }

        # Configuration
        $RED = "`e[31m"
        $GREEN = "`e[32m"
        $YELLOW = "`e[93m"
        $NC = "`e[0m" # No Color

        function Write-Log {
            param([string]$Message, [string]$Level = "INFO")
            $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            $color = switch ($Level) {
                "ERROR" { $RED }
                "WARN"  { $YELLOW }
                "INFO"  { $GREEN }
                default { "" }
            }
            Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $Level.ToLower()
        }

        Write-Log "Checking prerequisites..." "INFO"
        
        # Check Docker
        try {
            $dockerVersion = docker --version 2>$null
            if ($LASTEXITCODE -ne 0) {
                Write-Log "Docker is not installed or not in PATH" "ERROR"
                exit 1
            }
            Write-Log "Docker: $dockerVersion" "INFO"
        } catch {
            Write-Log "Docker is not installed or not in PATH" "ERROR"
            exit 1
        }
        
        # Check Docker Compose
        try {
            $composeVersion = docker compose version 2>$null
            Write-Log "Docker Compose: $composeVersion" "INFO"
        } catch {
            Write-Log "Docker Compose is not installed or not in PATH" "ERROR"
            exit 1
        }
        
        # Check environment file
        if (!(Test-Path ".env")) {
            Write-Log "Environment file .env not found" "ERROR"
            Write-Log "Please create it from .env.example and configure for production" "ERROR"
            exit 1
        }
        
        # Load environment file and check required variables
        $envContent = Get-Content .env | Where-Object {$_ -notmatch '^#' -and $_ -notmatch '^\s*$'}
        $secretKeyPresent = $envContent | Where-Object {$_ -like "*SECRET_KEY=*"} | Measure-Object | ForEach-Object {$_.Count -gt 0}
        $privacySaltPresent = $envContent | Where-Object {$_ -like "*PRIVACY_SALT=*"} | Measure-Object | ForEach-Object {$_.Count -gt 0}
        
        if (!$secretKeyPresent) {
            Write-Log "SECRET_KEY must be set in .env" "ERROR"
            exit 1
        }
        
        if (!$privacySaltPresent) {
            Write-Log "PRIVACY_SALT must be set in .env" "ERROR"
            exit 1
        }
        
        Write-Log "Prerequisites check passed" "INFO"

        # Create backup of existing data
        Write-Log "Creating backup of existing data..." "INFO"
        $backupDir = "/opt/ai-assistant/backups"
        $dataDir = "/opt/ai-assistant/data"
        New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
        $backupFileName = "data-backup-" + (Get-Date -Format "yyyyMMdd-HHmmss") + ".tar.gz"
        $backupPath = Join-Path $backupDir $backupFileName

        # Create archive of data directory if it exists
        if (Test-Path $dataDir) {
            Compress-Archive -Path $dataDir -DestinationPath $backupPath -Force
            Write-Log "Data backup created: $backupPath" "INFO"
        } else {
            Write-Log "No existing data directory to backup" "INFO"
        }

        # Pull latest images
        Write-Log "Pulling latest images..." "INFO"
        docker compose --env-file .env pull

        # Build production images
        Write-Log "Building production images..." "INFO"
        docker compose --env-file .env build --no-cache

        # Start services
        Write-Log "Starting services..." "INFO"
        docker compose --env-file .env up -d

        # Wait for services to be ready
        Write-Log "Waiting for services to be ready..." "INFO"
        Start-Sleep -Seconds 10

        # Health check
        $maxRetries = 30
        $retryCount = 0
        $servicesReady = $false

        while ($retryCount -lt $maxRetries -and -not $servicesReady) {
            try {
                $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health/ready" -UseBasicParsing -TimeoutSec 10 -ErrorAction Stop
                if ($response.StatusCode -eq 200) {
                    $servicesReady = $true
                    Write-Log "Services are ready!" "INFO"
                    break
                }
            } catch {
                # Ignore errors and continue waiting
            }

            $retryCount++
            Write-Log "Waiting for services... (attempt $retryCount/$maxRetries)" "INFO"
            Start-Sleep -Seconds 10
        }

        if (-not $servicesReady) {
            Write-Log "Services failed to become ready within timeout" "ERROR"
            docker compose logs
            exit 1
        }

        Write-Log "Deployment to $Environment completed successfully!" "INFO"
    }
    
    'test' {
        Write-Host "Running tests..." -ForegroundColor Cyan
        Write-Host "Running backend tests..." -ForegroundColor Yellow
        if (Test-Path "backend/.venv") {
            & backend/.venv/Scripts/Activate.ps1
            cd backend
            python -m pytest -v
            cd ..
        } else {
            Write-Warning "Backend virtual environment not found. Run setup first."
        }
    }
    
    'verify' {
        Write-Host "Verifying models and system integrity..." -ForegroundColor Cyan
        # Inline model verification functionality
        if (-Not (Test-Path "models")) { Write-Host "Models directory not found: models"; exit 1 }
        $checksPath = Join-Path "models" 'checksums.json'
        if (-Not (Test-Path $checksPath)) { Write-Host "checksums.json not found in models"; exit 1 }

        $checks = Get-Content $checksPath | ConvertFrom-Json
        $fail = @()
        Get-ChildItem -Path "models" -File | Where-Object { $_.Extension -in '.gguf','.onnx' } | ForEach-Object {
          $sha = Get-FileHash -Algorithm SHA256 -Path $_.FullName
          $expected = $checks.$($_.Name)
          if (-not $expected) {
            Write-Host "WARN: No expected hash for $($_.Name)" -ForegroundColor Yellow
          } elseif ($expected -ne $sha.Hash) {
            $fail += $_.Name
            Write-Host "MISMATCH: $($_.Name)" -ForegroundColor Red
          } else {
            Write-Host "OK: $($_.Name)" -ForegroundColor Green
          }
        }
        if ($fail.Count -gt 0) { Write-Host "Verification failed." -ForegroundColor Red; exit 2 } else { Write-Host "All model files verified." -ForegroundColor Green }
    }
    
    'cleanup' {
        Write-Host "Cleaning up development artifacts..." -ForegroundColor Cyan
        # Stop Docker services
        $composeFiles = @("docker-compose.yml", "docker-compose.dev.yml")
        foreach ($file in $composeFiles) {
            if (Test-Path $file) {
                Write-Host "Stopping services defined in $file..." -ForegroundColor Yellow
                docker compose -f $file down
            }
        }
        
        # Remove build artifacts
        $pathsToRemove = @(
            "backend/__pycache__",
            "backend/*.pyc",
            "frontend/node_modules",
            "frontend/dist",
            "frontend/.vite",
            "frontend/.cache",
            "frontend/src-tauri/target",
            "build",
            "dist",
            "target",
            "*.log",
            "logs"
        )
        
        foreach ($path in $pathsToRemove) {
            if (Test-Path $path) {
                Remove-Item $path -Recurse -Force -ErrorAction SilentlyContinue
                Write-Host "Removed: $path" -ForegroundColor Green
            }
        }
        
        # Clean Python cache directories
        Get-ChildItem -Path . -Directory -Recurse -Name "__pycache__" | ForEach-Object {
            $fullPath = Join-Path . $_
            Remove-Item $fullPath -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "Removed: $fullPath" -ForegroundColor Green
        }
        
        Write-Host "Cleanup completed." -ForegroundColor Green
    }
    
    'voice-test' {
        Write-Host "Testing voice functionality..." -ForegroundColor Cyan
        if (Test-Path "$PSScriptRoot/voice_loop.py") {
            python "$PSScriptRoot/voice_loop.py"
        } else {
            Write-Host "Voice loop test script not found" -ForegroundColor Red
        }
    }
    
    default {
        Write-Host "Usage: ./scripts/main.ps1 -Command <command>" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Available commands:" -ForegroundColor Cyan
        Write-Host "  setup     - Set up dev/prod environment" -ForegroundColor White
        Write-Host "  models    - Download models for dev/prod" -ForegroundColor White
        Write-Host "  dev       - Start development environment" -ForegroundColor White
        Write-Host "  dev-setup - Setup and start dev environment (setup + dev)" -ForegroundColor White
        Write-Host "  deploy    - Deploy to production" -ForegroundColor White
        Write-Host "  test      - Run tests" -ForegroundColor White
        Write-Host "  verify    - Verify models and integrity" -ForegroundColor White
        Write-Host "  cleanup   - Clean development artifacts" -ForegroundColor White
        Write-Host "  voice-test - Test voice functionality" -ForegroundColor White
        Write-Host ""
        Write-Host "Optional parameters:" -ForegroundColor Cyan
        Write-Host "  -Environment <dev|prod> (default: dev)" -ForegroundColor White
        Write-Host "  -ModelsDir <path> (default: models)" -ForegroundColor White
        Write-Host "  -SkipModels, -SkipDeps, -SkipServices (for setup command)" -ForegroundColor White
    }
}
