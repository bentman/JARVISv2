#!/usr/bin/env bash
# Runs all test suites for the Local AI Assistant project with a single command.
#
# This script executes all available test suites in the proper sequence: 
# unit tests, verification tests, and end-to-end smoke tests.
# It provides a consolidated way to validate the entire system before commits or deployments.
#
# Usage:
#   ./run-all-tests.sh [test-type] [options]
#   
# Arguments:
#   test-type: Type of tests to run ('unit', 'verification', 'e2e', or 'all'). Default: 'all'
#   -v, --verbose: Enable verbose output for test runs
#   -h, --help: Show this help message
#
# Examples:
#   ./run-all-tests.sh              # Run all test suites in sequence
#   ./run-all-tests.sh unit         # Run only unit tests
#   ./run-all-tests.sh e2e -v       # Run only end-to-end tests with verbose output
#   ./run-all-tests.sh verification # Run only verification tests

set -euo pipefail

# Default values
TEST_TYPE="all"
VERBOSE=false

# Function to display usage
usage() {
    echo "Usage: $0 [test-type] [options]"
    echo ""
    echo "Arguments:"
    echo "  test-type: Type of tests to run ('unit', 'verification', 'e2e', or 'all'). Default: 'all'"
    echo ""
    echo "Options:"
    echo "  -v, --verbose: Enable verbose output for test runs"
    echo "  -h, --help: Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                           # Run all test suites in sequence"
    echo "  $0 unit                      # Run only unit tests"
    echo "  $0 e2e -v                    # Run only end-to-end tests with verbose output"
    echo "  $0 verification              # Run only verification tests"
    exit 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        unit|verification|e2e|all)
            TEST_TYPE="$1"
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "Unknown argument: $1"
            usage
            ;;
    esac
done

# Determine which tests to run
run_unit=false
run_verification=false
run_e2e=false

case "$TEST_TYPE" in
    all)
        run_unit=true
        run_verification=true
        run_e2e=true
        ;;
    unit)
        run_unit=true
        ;;
    verification)
        run_verification=true
        ;;
    e2e)
        run_e2e=true
        ;;
esac

# Initialize results
unit_result=""
verification_result=""
e2e_result=""
overall_result="pending"

echo "Starting Local AI Assistant test suite..." >&2
echo "Test Type: $TEST_TYPE" >&2

# Run unit tests if requested
if [[ "$run_unit" == "true" ]]; then
    echo "" >&2
    echo "Running unit tests..." >&2
    if [[ "$VERBOSE" == "true" ]]; then
        ./tests/unit-test.sh -v
    else
        ./tests/unit-test.sh
    fi
    
    if [[ $? -eq 0 ]]; then
        unit_result="passed"
        echo "Unit tests: PASSED" >&2
    else
        unit_result="failed"
        echo "Unit tests: FAILED" >&2
    fi
fi

# Run verification tests if requested
if [[ "$run_verification" == "true" ]]; then
    echo "" >&2
    echo "Running verification tests..." >&2
    ./tests/verify-models.sh
    
    if [[ $? -eq 0 ]]; then
        verification_result="passed"
        echo "Verification tests: PASSED" >&2
    else
        verification_result="failed"
        echo "Verification tests: FAILED" >&2
    fi
fi

# Run end-to-end tests if requested
if [[ "$run_e2e" == "true" ]]; then
    echo "" >&2
    echo "Running end-to-end tests..." >&2
    if [[ "$VERBOSE" == "true" ]]; then
        ./tests/smoke.sh
    else
        ./tests/smoke.sh
    fi
    
    if [[ $? -eq 0 ]]; then
        e2e_result="passed"
        echo "End-to-end tests: PASSED" >&2
    else
        e2e_result="failed"
        echo "End-to-end tests: FAILED" >&2
    fi
fi

# Print summary
echo "" >&2
echo "Test Suite Summary:" >&2

if [[ -n "$unit_result" ]]; then
    if [[ "$unit_result" == "passed" ]]; then
        echo "  Unit Tests: PASSED" >&2
    else
        echo "  Unit Tests: FAILED" >&2
    fi
fi

if [[ -n "$verification_result" ]]; then
    if [[ "$verification_result" == "passed" ]]; then
        echo "  Verification Tests: PASSED" >&2
    else
        echo "  Verification Tests: FAILED" >&2
    fi
fi

if [[ -n "$e2e_result" ]]; then
    if [[ "$e2e_result" == "passed" ]]; then
        echo "  End-to-End Tests: PASSED" >&2
    else
        echo "  End-to-End Tests: FAILED" >&2
    fi
fi

# Determine overall result
overall_exit=0
if { [[ "$run_unit" == "true" ]] && [[ "$unit_result" != "passed" ]]; } || \
   { [[ "$run_verification" == "true" ]] && [[ "$verification_result" != "passed" ]]; } || \
   { [[ "$run_e2e" == "true" ]] && [[ "$e2e_result" != "passed" ]]; }; then
    overall_result="failed"
    echo "" >&2
    echo "OVERALL RESULT: FAILED" >&2
    overall_exit=1
else
    overall_result="passed"
    echo "" >&2
    echo "OVERALL RESULT: PASSED" >&2
    echo "All requested tests completed successfully!" >&2
fi

exit $overall_exit
