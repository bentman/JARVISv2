<#
.SYNOPSIS
Deploys the Local AI Assistant for production environments with backup, monitoring, and operational best practices.

.DESCRIPTION
This script handles the complete production deployment process including prerequisites check, backup creation, 
service deployment, health verification, and post-deployment validation. It implements security hardening and 
production best practices as outlined in the deployment guide.

.PARAMETER Action
Specifies the deployment action: 'deploy', 'update', 'restore', 'status', 'logs', 'stop'. Default is 'deploy'.

.PARAMETER BackupDir
Directory to store backups. Default is '/opt/ai-assistant/backups'.

.PARAMETER DataDir
Directory for application data. Default is '/opt/ai-assistant/data'.

.PARAMETER ModelsDir
Directory for AI models. Default is '/opt/ai-assistant/models'.

.PARAMETER ComposeFile
Docker Compose file to use. Default is 'docker-compose.yml'.

.PARAMETER EnvFile
Environment file to use. Default is '.env'.

.PARAMETER BackupFile
Path to backup file for restore operation (required for restore action).

.EXAMPLE
./deploy.ps1 -Action deploy
Deploys the application with backup and health checks.

.EXAMPLE
./deploy.ps1 -Action update
Updates the deployment (backup + redeploy).

.EXAMPLE
./deploy.ps1 -Action restore -BackupFile "C:\backups\data-backup-20240115-103045.tar.gz"
Restores from a specific backup file.
#>

param(
    [ValidateSet('deploy', 'update', 'restore', 'status', 'logs', 'stop')]
    [string]$Action = 'deploy',
    
    [string]$BackupDir = "/opt/ai-assistant/backups",
    
    [string]$DataDir = "/opt/ai-assistant/data",
    
    [string]$ModelsDir = "/opt/ai-assistant/models",
    
    [string]$ComposeFile = "docker-compose.yml",
    
    [string]$EnvFile = ".env",
    
    [string]$BackupFile
)

# Ensure running as administrator for production deployment
if ($Action -ne 'status' -and $Action -ne 'logs') {
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

function Test-Prerequisites {
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
    if (!(Test-Path $EnvFile)) {
        Write-Log "Environment file $EnvFile not found" "ERROR"
        Write-Log "Please create it from .env.example and configure for production" "ERROR"
        exit 1
    }
    
    # Load environment file and check required variables
    $envContent = Get-Content $EnvFile | Where-Object {$_ -notmatch '^#' -and $_ -notmatch '^\s*$'}
    $secretKeyPresent = $envContent | Where-Object {$_ -like "*SECRET_KEY=*"} | Measure-Object | ForEach-Object {$_.Count -gt 0}
    $privacySaltPresent = $envContent | Where-Object {$_ -like "*PRIVACY_SALT=*"} | Measure-Object | ForEach-Object {$_.Count -gt 0}
    
    if (!$secretKeyPresent) {
        Write-Log "SECRET_KEY must be set in $EnvFile" "ERROR"
        exit 1
    }
    
    if (!$privacySaltPresent) {
        Write-Log "PRIVACY_SALT must be set in $EnvFile" "ERROR"
        exit 1
    }
    
    Write-Log "Prerequisites check passed" "INFO"
}

function Backup-Data {
    if (Test-Path $DataDir) {
        Write-Log "Creating backup of existing data..." "INFO"
        
        New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
        $backupFileName = "data-backup-" + (Get-Date -Format "yyyyMMdd-HHmmss") + ".tar.gz"
        $backupPath = Join-Path $BackupDir $backupFileName
        
        # Create archive of data directory
        Compress-Archive -Path $DataDir -DestinationPath $backupPath -Force
        Write-Log "Data backup created: $backupPath" "INFO"
        
        # Keep only last 10 backups
        $oldBackups = Get-ChildItem -Path $BackupDir -Filter "data-backup-*.tar.gz" | Sort-Object CreationTime -Descending | Select-Object -Skip 10
        foreach ($oldBackup in $oldBackups) {
            Remove-Item $oldBackup.FullName -Force
            Write-Log "Removed old backup: $($oldBackup.Name)" "INFO"
        }
    } else {
        Write-Log "No existing data directory to backup" "INFO"
    }
}

function Start-Deployment {
    Write-Log "Starting production deployment..." "INFO"
    
    # Pull latest images
    Write-Log "Pulling latest images..." "INFO"
    docker compose -f $ComposeFile --env-file $EnvFile pull
    
    # Build production images
    Write-Log "Building production images..." "INFO"
    docker compose -f $ComposeFile --env-file $EnvFile build --no-cache
    
    # Start services
    Write-Log "Starting services..." "INFO"
    docker compose -f $ComposeFile --env-file $EnvFile up -d
    
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
        docker compose -f $ComposeFile logs
        exit 1
    }
}

function Restore-FromBackup {
    if ([string]::IsNullOrEmpty($BackupFile)) {
        Write-Log "Please specify backup file to restore from using -BackupFile parameter" "ERROR"
        $availableBackups = Get-ChildItem -Path $BackupDir -Filter "data-backup-*.tar.gz" -ErrorAction SilentlyContinue
        if ($availableBackups) {
            Write-Log "Available backups:" "INFO"
            $availableBackups | ForEach-Object { Write-Host "  $($_.FullName)" }
        } else {
            Write-Log "No backups found" "INFO"
        }
        exit 1
    }
    
    if (!(Test-Path $BackupFile)) {
        Write-Log "Backup file $BackupFile not found" "ERROR"
        exit 1
    }
    
    Write-Log "Stopping services for restore..." "INFO"
    docker compose -f $ComposeFile --env-file $EnvFile down
    
    Write-Log "Restoring data from $BackupFile..." "INFO"
    Expand-Archive -Path $BackupFile -DestinationPath (Split-Path $DataDir) -Force
    
    Write-Log "Starting services after restore..." "INFO"
    docker compose -f $ComposeFile --env-file $EnvFile up -d
}

function Show-Status {
    Write-Host "=== Service Status ===" -ForegroundColor Cyan
    docker compose -f $ComposeFile ps
    
    Write-Host "`n=== Health Status ===" -ForegroundColor Cyan
    try {
        $health = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/health/services" -TimeoutSec 10
        $health | ConvertTo-Json | Write-Host
    } catch {
        Write-Host "Services not accessible" -ForegroundColor Red
    }
}

function Show-Logs {
    docker compose -f $ComposeFile logs -f
}

function Stop-Services {
    Write-Log "Stopping services..." "INFO"
    docker compose -f $ComposeFile --env-file $EnvFile down
}

function Update-Deployment {
    Write-Log "Updating deployment..." "INFO"
    Backup-Data
    Start-Deployment
}

# Main execution based on action
switch ($Action) {
    "deploy" {
        Test-Prerequisites
        Backup-Data
        Start-Deployment
    }
    "restore" {
        Restore-FromBackup
    }
    "logs" {
        Show-Logs
    }
    "status" {
        Show-Status
    }
    "stop" {
        Stop-Services
    }
    "update" {
        Test-Prerequisites
        Update-Deployment
    }
    default {
        Write-Host "Usage: $MyInvocation.MyCommand.Name [-Action] <deploy|restore|logs|status|stop|update>" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Actions:"
        Write-Host "  deploy  - Deploy the application (default)"
        Write-Host "  restore - Restore from backup (requires -BackupFile)"
        Write-Host "  logs    - Show service logs"
        Write-Host "  status  - Show service status"
        Write-Host "  stop    - Stop all services"
        Write-Host "  update  - Update deployment (backup + redeploy)"
        exit 1
    }
}

Write-Log "Deployment action '$Action' completed successfully!" "INFO"
