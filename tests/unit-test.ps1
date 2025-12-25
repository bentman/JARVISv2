<#
.SYNOPSIS
Runs unit tests for the Local AI Assistant backend services.

.DESCRIPTION
This script runs the Python unit tests for the backend services using pytest. It can run all tests or specific test modules based on parameters.

.PARAMETER TestModule
Specifies a specific test module to run (e.g., "test_memory_stats_endpoint"). If not specified, runs all tests.

.PARAMETER Verbose
Enable verbose output for test runs. Default is $false.

.EXAMPLE
./unit-test.ps1
Runs all backend unit tests.

.EXAMPLE
./unit-test.ps1 -TestModule test_memory_stats_endpoint
Runs only the memory stats endpoint tests.

.EXAMPLE
./unit-test.ps1 -Verbose
Runs all tests with verbose output.
#>

param(
    [string]$TestModule = "",
    [switch]$Verbose = $false
)

# Activate the virtual environment if it exists
if (Test-Path "backend/.venv") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & "backend/.venv/Scripts/Activate.ps1"
} else {
    Write-Warning "Virtual environment not found. Ensure dependencies are installed."
}

# Change to backend directory for testing
Set-Location backend

try {
    # Build pytest command
    $pytestCmd = "pytest"
    if ($Verbose) {
        $pytestCmd += " -v"
    } else {
        $pytestCmd += " -q"  # quiet by default
    }
    
    if ($TestModule) {
        $pytestCmd += " -k $TestModule"
    } else {
        $pytestCmd += " --disable-warnings"  # suppress warnings by default unless verbose
    }
    
    Write-Host "Running tests: $pytestCmd" -ForegroundColor Cyan
    Invoke-Expression $pytestCmd
} finally {
    # Return to original directory
    Set-Location ..
}

Write-Host "Unit tests completed." -ForegroundColor Green
