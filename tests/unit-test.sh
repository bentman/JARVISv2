#!/usr/bin/env bash
# Runs unit tests for the Local AI Assistant backend services.

set -euo pipefail

# Default values
TEST_MODULE=""
VERBOSE=false

# Function to display usage
usage() {
    echo "Usage: $0 [-m test_module] [-v verbose]"
    echo "  -m test_module: Specific test module to run (e.g., test_memory_stats_endpoint). Default: all tests"
    echo "  -v verbose: Enable verbose output. Default: false"
    echo ""
    echo "Examples:"
    echo "  $0                           # Run all backend unit tests"
    echo "  $0 -m test_memory_stats_endpoint  # Run only memory stats tests"
    echo "  $0 -v                        # Run all tests with verbose output"
    exit 1
}

# Parse command line options
while getopts "m:vh" opt; do
    case $opt in
        m)
            TEST_MODULE="$OPTARG"
            ;;
        v)
            VERBOSE=true
            ;;
        h)
            usage
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            usage
            ;;
    esac
done

# Activate the virtual environment if it exists
if [[ -d "backend/.venv" ]]; then
    echo "Activating virtual environment..." >&2
    source backend/.venv/bin/activate
else
    echo "Warning: Virtual environment not found. Ensure dependencies are installed." >&2
fi

# Change to backend directory for testing
cd backend

# Build pytest command
if [[ "$VERBOSE" == "true" ]]; then
    PYTEST_CMD="python -m pytest -v"
else
    PYTEST_CMD="python -m pytest -q"  # quiet by default
fi

if [[ -n "$TEST_MODULE" ]]; then
    PYTEST_CMD="$PYTEST_CMD -k $TEST_MODULE"
else
    PYTEST_CMD="$PYTEST_CMD --disable-warnings"  # suppress warnings by default unless verbose
fi

echo "Running tests: $PYTEST_CMD" >&2
eval $PYTEST_CMD

cd ..

echo "Unit tests completed." >&2
