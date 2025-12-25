#!/bin/bash

# Parse command line arguments
NO_DOCKER=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-docker)
            NO_DOCKER=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--no-docker]"
            exit 1
            ;;
    esac
done

# Stop Docker services unless suppressed
if [ "$NO_DOCKER" = false ]; then
    if command -v docker &> /dev/null; then
        docker compose down --remove-orphans 2>/dev/null || true
    fi
fi

# Remove explicit dev/build directories
paths=(
    "backend/.venv"
    "frontend/node_modules"
    "frontend/dist"
    "frontend/.vite"
    "frontend/.parcel-cache"
    "frontend/.turbo"
    "frontend/.cache"
    "frontend/src-tauri/target"
    "frontend/src-tauri/target/release/bundle"
    "build"
    "dist"
    "target"
    "coverage"
)

for path in "${paths[@]}"; do
    if [ -d "$path" ]; then
        rm -rf "$path"
        echo "Removed $path"
    fi
done

# Remove common cache directories recursively
cache_names=(
    "__pycache__"
    ".pytest_cache"
    ".mypy_cache"
    ".ruff_cache"
)

for name in "${cache_names[@]}"; do
    find . -type d -name "$name" -exec rm -rf {} + 2>/dev/null || true
done

# Remove log files (keep logs dir if any)
if [ -d "logs" ]; then
    find logs -type f -name "*.log" -exec rm -f {} + 2>/dev/null || true
fi

# Remove coverage files
find . -type f -name ".coverage*" -exec rm -f {} + 2>/dev/null || true

# Summary
echo "Cleanup complete."
echo "Remaining notable dirs (if present):"
for dir in models data storage; do
    if [ -d "$dir" ]; then
        echo "$dir"
    fi
done
