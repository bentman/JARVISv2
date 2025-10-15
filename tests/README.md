# Testing Scripts

This folder contains all testing and verification scripts for the Local AI Assistant.

## Integration Tests

### smoke.ps1
Comprehensive end-to-end smoke test that validates:
- Health endpoints (services, models)
- Basic chat functionality
- Streaming endpoint
- Retrieval-augmented generation (RAG)
- Budget enforcement and limits
- Redis caching performance
- Data persistence across restarts
- Voice TTS/STT functionality

**Usage:**
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tests/smoke.ps1
```

**Options:**
- `BaseUrl`: Override API base URL (default: `http://localhost:8000`)

### budget-test.ps1
Focused test for budget enforcement functionality.
- Sets restrictive budget limits
- Verifies budget enforcement blocking behavior
- Tests budget limit exceeded messages

**Usage:**
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tests/budget-test.ps1
```

## Verification Tests

### verify-models.ps1 / verify-models.sh
Model integrity verification script that:
- Checks SHA256 hashes against `checksums.json`
- Validates all `.gguf` and `.onnx` files in models directory
- Reports mismatches or missing files

**Usage:**
```powershell
# Windows
powershell -NoProfile -ExecutionPolicy Bypass -File tests/verify-models.ps1

# macOS/Linux  
./tests/verify-models.sh
```

**Options:**
- `ModelsDir`: Override models directory path (default: `models`)

## Running Tests

### Prerequisites
- Backend services running (`docker compose up -d`)
- Models downloaded (`scripts/get-models.ps1` or `scripts/get-models.sh`)
- PowerShell 7+ for Windows scripts

### Test Execution Order
1. **Model verification**: Run `verify-models` first to ensure model integrity
2. **Integration tests**: Run `smoke.ps1` for comprehensive system validation
3. **Focused tests**: Run specific tests like `budget-test.ps1` as needed

### CI/CD Integration
Tests are designed to be run in automated environments:
- All tests exit with non-zero codes on failure
- Colored output can be suppressed for log parsing
- Tests include timeout and retry logic for reliability