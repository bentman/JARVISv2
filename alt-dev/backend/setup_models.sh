#!/bin/bash

# QwenAssistant Model Setup Script
# Downloads and configures all required AI models for local inference

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
MODELS_DIR="${MODELS_DIR:-./../models}"
PROFILE="${PROFILE:-medium}"  # light, medium, heavy
DOWNLOAD_TIMEOUT=3600  # 1 hour

# Model URLs and checksums
declare -A MODELS
declare -A MODEL_SIZES

# Light profile models (smallest, fastest)
MODELS["light_chat"]="https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf"
MODELS["light_stt"]="https://huggingface.co/ggerganov/whisper.cpp/resolve/main/models/ggml-tiny.bin"

# Medium profile models (balanced)
MODELS["medium_chat"]="https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_K_M.gguf"
MODELS["medium_stt"]="https://huggingface.co/ggerganov/whisper.cpp/resolve/main/models/ggml-base.bin"

# Heavy profile models (largest, most capable)
MODELS["heavy_chat"]="https://huggingface.co/TheBloke/Llama-2-13B-Chat-GGUF/resolve/main/llama-2-13b-chat.Q4_K_M.gguf"
MODELS["heavy_stt"]="https://huggingface.co/ggerganov/whisper.cpp/resolve/main/models/ggml-small.bin"

# Common models (all profiles)
MODELS["tts"]="https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/kathleen/medium/en_US-kathleen-medium.onnx"
MODELS["tts_config"]="https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/kathleen/medium/en_US-kathleen-medium.onnx.json"

# Approximate sizes (in GB)
MODEL_SIZES["light_chat"]=3.5
MODEL_SIZES["light_stt"]=0.14
MODEL_SIZES["medium_chat"]=5.2
MODEL_SIZES["medium_stt"]=0.27
MODEL_SIZES["heavy_chat"]=7.6
MODEL_SIZES["heavy_stt"]=0.78
MODEL_SIZES["tts"]=0.4
MODEL_SIZES["tts_config"]=0.001

print_header() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}  $1"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
}

print_step() {
    echo -e "${YELLOW}→${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

check_disk_space() {
    local required=$1
    local available=$(df "$MODELS_DIR" | awk 'NR==2 {print $4}')
    available=$((available / 1024 / 1024))  # Convert to GB

    if (( $(echo "$available < $required" | bc -l) )); then
        print_error "Insufficient disk space. Required: ${required}GB, Available: ${available}GB"
        return 1
    fi
    return 0
}

check_internet() {
    print_step "Checking internet connectivity..."
    if ! ping -c 1 huggingface.co &>/dev/null; then
        print_error "No internet connection or cannot reach huggingface.co"
        return 1
    fi
    print_success "Internet connectivity verified"
    return 0
}

download_model() {
    local url=$1
    local filename=$2
    local filepath="$MODELS_DIR/$filename"

    # Skip if already exists
    if [ -f "$filepath" ]; then
        print_info "Model already exists: $filename"
        return 0
    fi

    print_step "Downloading $filename..."

    if ! wget -q --show-progress -O "$filepath" "$url"; then
        print_error "Failed to download $filename"
        rm -f "$filepath"
        return 1
    fi

    # Verify file size
    if [ ! -s "$filepath" ]; then
        print_error "Downloaded file is empty: $filename"
        rm -f "$filepath"
        return 1
    fi

    print_success "Downloaded: $filename ($(du -h "$filepath" | cut -f1))"
    return 0
}

calculate_total_size() {
    local total=0

    # Base models for selected profile
    total=$(echo "$total + ${MODEL_SIZES[${PROFILE}_chat]}" | bc)
    total=$(echo "$total + ${MODEL_SIZES[${PROFILE}_stt]}" | bc)

    # Common models
    total=$(echo "$total + ${MODEL_SIZES[tts]}" | bc)
    total=$(echo "$total + ${MODEL_SIZES[tts_config]}" | bc)

    echo "$total"
}

setup_models() {
    print_header "QwenAssistant AI Model Setup"

    # Check internet
    if ! check_internet; then
        print_error "Cannot proceed without internet connection"
        return 1
    fi

    # Create models directory
    mkdir -p "$MODELS_DIR"
    print_success "Models directory ready: $MODELS_DIR"

    # Calculate and check disk space
    total_size=$(calculate_total_size)
    print_info "Total download size: ~${total_size}GB (${PROFILE} profile)"

    if ! check_disk_space "$((total_size + 2))"; then
        return 1
    fi

    echo ""
    print_header "Downloading Models (${PROFILE} Profile)"

    local failed=0

    # Download LLM
    print_step "Chat Model (${PROFILE})..."
    if ! download_model "${MODELS[${PROFILE}_chat]}" "llama-${PROFILE}-chat.gguf"; then
        ((failed++))
    fi

    # Download STT
    print_step "Speech-to-Text Model (${PROFILE})..."
    if ! download_model "${MODELS[${PROFILE}_stt]}" "whisper-${PROFILE}.bin"; then
        ((failed++))
    fi

    # Download TTS
    print_step "Text-to-Speech Model..."
    if ! download_model "${MODELS[tts]}" "piper-tts.onnx"; then
        ((failed++))
    fi

    print_step "Text-to-Speech Config..."
    if ! download_model "${MODELS[tts_config]}" "piper-tts.onnx.json"; then
        ((failed++))
    fi

    echo ""

    if [ $failed -gt 0 ]; then
        print_error "Failed to download $failed model(s)"
        return 1
    fi

    # Create symlinks for easy access
    print_step "Creating model symlinks..."

    cd "$MODELS_DIR"
    ln -sf "llama-${PROFILE}-chat.gguf" chat_model.gguf 2>/dev/null || true
    ln -sf "whisper-${PROFILE}.bin" stt_model.bin 2>/dev/null || true
    ln -sf piper-tts.onnx tts_model.onnx 2>/dev/null || true

    print_success "Model symlinks created"

    echo ""
    print_header "Setup Complete"
    print_success "All models downloaded and configured for ${PROFILE} profile"

    echo ""
    print_info "Models location: $MODELS_DIR"
    print_info "Profile: $PROFILE"
    print_info "Space used: $(du -sh "$MODELS_DIR" | cut -f1)"

    echo ""
    echo "Next steps:"
    echo "  1. Start the backend: docker compose up -d"
    echo "  2. Configure models path in docker-compose.yml"
    echo "  3. Start the frontend: npm run dev"

    return 0
}

# Main execution
main() {
    case "${1:-setup}" in
        setup)
            setup_models
            ;;
        list)
            echo "Available profiles: light, medium, heavy"
            echo "Model sizes:"
            for model in "${!MODEL_SIZES[@]}"; do
                echo "  $model: ${MODEL_SIZES[$model]}GB"
            done
            ;;
        clean)
            print_step "Removing all downloaded models..."
            rm -rf "$MODELS_DIR"
            print_success "Models directory cleaned"
            ;;
        *)
            echo "Usage: $0 {setup|list|clean} [options]"
            echo ""
            echo "Options:"
            echo "  PROFILE=light|medium|heavy  Select model profile (default: medium)"
            echo "  MODELS_DIR=path             Custom models directory"
            echo ""
            echo "Examples:"
            echo "  PROFILE=light $0 setup      # Download light models"
            echo "  PROFILE=heavy $0 setup      # Download heavy models"
            echo "  $0 list                     # List available models"
            echo "  $0 clean                    # Delete all models"
            return 1
            ;;
    esac
}

main "$@"
