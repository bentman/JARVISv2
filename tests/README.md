# Tests Directory

This directory contains all test and verification scripts for the Local AI Assistant project, organized for both automated testing and manual verification purposes.

## Test Categories

### End-to-End Tests

#### smoke.ps1 / smoke.sh
Comprehensive end-to-end smoke test that validates core functionality across all system components:
- Health checks (services and models)
- Chat functionality (basic and streaming)
- Retrieval and privacy redaction
- Budget enforcement
- Redis caching performance
- Data persistence across restarts
- Voice STT/TTS functionality

**Usage:**
```powershell
# Windows
./tests/smoke.ps1
```

```bash
# macOS/Linux
./tests/smoke.sh
```

### Unit Tests

#### unit-test.ps1 / unit-test.sh
Runs backend unit tests for individual service components using pytest. Can run all tests or specific test modules based on parameters for targeted testing and development workflows.

**Usage:**
```powershell
# Windows - All tests
./tests/unit-test.ps1

# Windows - Specific test module
./tests/unit-test.ps1 -TestModule test_memory_stats_endpoint

# Windows - Verbose output
./tests/unit-test.ps1 -Verbose
```

```bash
# macOS/Linux - All tests
./tests/unit-test.sh

# macOS/Linux - Specific test module
./tests/unit-test.sh -m test_memory_stats_endpoint

# macOS/Linux - Verbose output
./tests/unit-test.sh -v
```

### Verification Tests

#### verify-models.ps1 / verify-models.sh
Verifies the integrity of downloaded models by comparing SHA256 checksums against the expected values in checksums.json. Ensures model files have not been corrupted or tampered with since download.

**Usage:**
```powershell
# Windows
./tests/verify-models.ps1
```

```bash
# macOS/Linux
./tests/verify-models.sh
```

### Specialized Tests

#### budget-test.ps1
Specific test for budget enforcement functionality, validating that spending limits are properly enforced and that the system behaves correctly when budget thresholds are exceeded.

## Running Tests

### Prerequisites
- Docker and Docker Compose
- Backend services running (use `docker compose up -d`)

### Execution
Run tests after starting the backend services. The smoke test is the most comprehensive and validates the entire system operation.

### Consolidated Test Runner
For convenience, we provide a consolidated test runner that executes all test suites in sequence:
- **PowerShell**: `./tests/run-all-tests.ps1` (runs unit -> verification -> e2e tests)
- **Bash**: `./tests/run-all-tests.sh` (runs unit -> verification -> e2e tests)

Both runners support specifying which test types to run (unit, verification, e2e, or all) and provide detailed summary reports.
