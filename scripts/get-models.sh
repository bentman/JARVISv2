#!/usr/bin/env bash
# Download required models for the Local AI Assistant based on the specified environment (dev or prod).

set -euo pipefail

# Default values
ENVIRONMENT="prod"
MODELS_DIR="models"

# Function to display usage
usage() {
    echo "Usage: $0 [-e environment] [-d models_dir]"
    echo "  -e environment: Specify environment (dev or prod). Default: prod"
    echo "  -d models_dir: Directory to download models to. Default: models"
    echo ""
    echo "Examples:"
    echo "  $0 -e dev                  # Download development models"
    echo "  $0 -e prod -d /path/to/models  # Download production models to custom directory"
    exit 1
}

# Parse command line options
while getopts "e:d:h" opt; do
    case $opt in
        e)
            if [[ "$OPTARG" == "dev" || "$OPTARG" == "prod" ]]; then
                ENVIRONMENT="$OPTARG"
            else
                echo "Error: Environment must be 'dev' or 'prod'"
                usage
            fi
            ;;
        d)
            MODELS_DIR="$OPTARG"
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

# Create models directory if it doesn't exist
mkdir -p "$MODELS_DIR"
cd "$MODELS_DIR"

# Determine model URLs based on environment
if [[ "$ENVIRONMENT" == "dev" ]]; then
    echo "Downloading development models (smaller, faster)..."
    
    # TinyLlama 1.1B Chat (Q2_K - smallest functional chat for dev)
    TLL_URL="https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q2_K.gguf?download=true"
    TLL_FILE="tinyllama-1.1b-chat-v1.0.Q2_K.gguf"
else
    echo "Downloading production models (optimized for performance)..."
    
    # TinyLlama 1.1B Chat (Q4_K_M - balanced for production)
    TLL_URL="https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf?download=true"
    TLL_FILE="tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
fi

# Download LLM model if not present
if [[ ! -f "$TLL_FILE" ]]; then
    echo "Downloading $TLL_FILE ..."
    curl -fL "$TLL_URL" -o "$TLL_FILE"
    echo "Successfully downloaded $TLL_FILE"
else
    echo "$TLL_FILE already exists, skipping download."
fi

# Piper English voice (common for both environments)
PIPER_URL="https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/low/en_US-amy-low.onnx"
PIPER_FILE="en_US-amy-low.onnx"
PIPER_JSON_URL="https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/low/en_US-amy-low.onnx.json"
PIPER_JSON_FILE="en_US-amy-low.onnx.json"

if [[ ! -f "$PIPER_FILE" ]]; then
    echo "Downloading $PIPER_FILE (TTS)..."
    curl -fL "$PIPER_URL" -o "$PIPER_FILE"
    echo "Successfully downloaded $PIPER_FILE"
else
    echo "$PIPER_FILE already exists, skipping download."
fi

if [[ ! -f "$PIPER_JSON_FILE" ]]; then
    echo "Downloading $PIPER_JSON_FILE (TTS Config)..."
    curl -fL "$PIPER_JSON_URL" -o "$PIPER_JSON_FILE"
    echo "Successfully downloaded $PIPER_JSON_FILE"
else
    echo "$PIPER_JSON_FILE already exists, skipping download."
fi

# Whisper Base English (common for both environments)
WHISPER_URL="https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin?download=true"
WHISPER_FILE="ggml-base.en.bin"
if [[ ! -f "$WHISPER_FILE" ]]; then
    echo "Downloading $WHISPER_FILE (STT)..."
    curl -fL "$WHISPER_URL" -o "$WHISPER_FILE"
    echo "Successfully downloaded $WHISPER_FILE"
else
    echo "$WHISPER_FILE already exists, skipping download."
fi

# Generate checksums for all model files
echo "Generating checksums..."
python3 - <<'PY'
import hashlib, json, os
root = '.'
checks = {}
for fn in os.listdir(root):
    if fn.endswith('.gguf') or fn.endswith('.onnx') or fn.endswith('.bin'):
        h = hashlib.sha256()
        with open(fn,'rb') as f:
            for chunk in iter(lambda: f.read(1024*1024), b''):
                h.update(chunk)
        checks[fn] = h.hexdigest()
with open('checksums.json','w', encoding='utf-8') as f:
    json.dump(checks, f, indent=2, ensure_ascii=False)
print('Checksums written to checksums.json')
PY

echo "Model download complete!"
echo "Environment: $ENVIRONMENT"
echo "Models directory: $(pwd)"
