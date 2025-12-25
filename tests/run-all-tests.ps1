<#
.SYNOPSIS
Runs all test suites for the Local AI Assistant project with a single command.

.DESCRIPTION
This script executes all available test suites in the proper sequence: unit tests, verification tests, and end-to-end smoke tests. It provides a consolidated way to validate the entire system before commits or deployments.

.PARAMETER TestType
Specifies which test suite to run: 'unit', 'verification', 'e2e', or 'all'. Default is 'all'.

.PARAMETER Verbose
Enable verbose output for test runs. Default is $false.

.EXAMPLE
./run-all-tests.ps1
Runs all test suites in sequence (unit -> verification -> e2e).

.EXAMPLE
./run-all-tests.ps1 -TestType unit
Runs only the unit tests.

.EXAMPLE
./run-all-tests.ps1 -TestType e2e -Verbose
Runs only the end-to-end tests with verbose output.
#>

param(
    [ValidateSet('unit', 'verification', 'e2e', 'all')]
    [string]$TestType = 'all',
    
    [switch]$Verbose = $false
)

# Determine if we should run each test type
$runUnit = ($TestType -eq 'all' -or $TestType -eq 'unit')
$runVerification = ($TestType -eq 'all' -or $TestType -eq 'verification')
$runE2E = ($TestType -eq 'all' -or $TestType -eq 'e2e')

$results = @{
    unit = $null
    verification = $null
    e2e = $null
    overall = "pending"
}

Write-Host "Starting Local AI Assistant test suite..." -ForegroundColor Green
Write-Host "Test Type: $TestType" -ForegroundColor Yellow

# Run unit tests if requested
if ($runUnit) {
    Write-Host "`nRunning unit tests..." -ForegroundColor Cyan
    try {
        if ($Verbose) {
            & "$PSScriptRoot/unit-test.ps1" -Verbose
        } else {
            & "$PSScriptRoot/unit-test.ps1"
        }
        $results.unit = "passed"
        Write-Host "Unit tests: PASSED" -ForegroundColor Green
    } catch {
        $results.unit = "failed"
        Write-Host "Unit tests: FAILED - $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Run verification tests if requested
if ($runVerification) {
    Write-Host "`nRunning verification tests..." -ForegroundColor Cyan
    try {
        & "$PSScriptRoot/verify-models.ps1"
        $results.verification = "passed"
        Write-Host "Verification tests: PASSED" -ForegroundColor Green
    } catch {
        $results.verification = "failed"
        Write-Host "Verification tests: FAILED - $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Run end-to-end tests if requested
if ($runE2E) {
    Write-Host "`nRunning end-to-end tests..." -ForegroundColor Cyan
    try {
        if ($Verbose) {
            & "$PSScriptRoot/smoke.ps1"
        } else {
            & "$PSScriptRoot/smoke.ps1"
        }
        $results.e2e = "passed"
        Write-Host "End-to-end tests: PASSED" -ForegroundColor Green
    } catch {
        $results.e2e = "failed"
        Write-Host "End-to-end tests: FAILED - $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Summary
Write-Host "`nTest Suite Summary:" -ForegroundColor White -BackgroundColor DarkBlue

if ($results.unit -ne $null) {
    $unitColor = if ($results.unit -eq "passed") { [ConsoleColor]::Green } else { [ConsoleColor]::Red }
    Write-Host "  Unit Tests: $($results.unit.ToUpper())" -ForegroundColor $unitColor
}

if ($results.verification -ne $null) {
    $verifyColor = if ($results.verification -eq "passed") { [ConsoleColor]::Green } else { [ConsoleColor]::Red }
    Write-Host "  Verification Tests: $($results.verification.ToUpper())" -ForegroundColor $verifyColor
}

if ($results.e2e -ne $null) {
    $e2eColor = if ($results.e2e -eq "passed") { [ConsoleColor]::Green } else { [ConsoleColor]::Red }
    Write-Host "  End-to-End Tests: $($results.e2e.ToUpper())" -ForegroundColor $e2eColor
}

# Determine overall result
if (($runUnit -and $results.unit -ne "passed") -or
    ($runVerification -and $results.verification -ne "passed") -or
    ($runE2E -and $results.e2e -ne "passed")) {
    $results.overall = "failed"
    Write-Host "`nOVERALL RESULT: FAILED" -ForegroundColor Red -BackgroundColor Black
    exit 1
} else {
    $results.overall = "passed"
    Write-Host "`nOVERALL RESULT: PASSED" -ForegroundColor Green -BackgroundColor Black
    Write-Host "All requested tests completed successfully!" -ForegroundColor Green
    exit 0
}
