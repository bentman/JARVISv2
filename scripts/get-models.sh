#!/usr/bin/env bash
set -euo pipefail

mkdir -p models
cd models

# TinyLlama 1.1B Chat GGUF (small, for quick testing)
# License: Apache-2.0 (via TinyLlama project). Verify on provider page before use.
TLL_URL="https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf?download=true"
TLL_FILE="tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
if [ ! -f "$TLL_FILE" ]; then
  echo "Downloading $TLL_FILE ..."
  curl -L "$TLL_URL" -o "$TLL_FILE"
fi

# Piper English voice (low size)
# Source: https://github.com/rhasspy/piper-voices/releases (verify license)
PIPER_VOICE_URL="https://github.com/rhasspy/piper-voices/releases/download/en_US-amy-low/en_US-amy-low.onnx"
PIPER_VOICE_FILE="en_US-amy-low.onnx"
if [ ! -f "$PIPER_VOICE_FILE" ]; then
  echo "Downloading $PIPER_VOICE_FILE ..."
  curl -L "$PIPER_VOICE_URL" -o "$PIPER_VOICE_FILE"
fi

# Generate checksums
python - <<'PY'
import hashlib, json, os
root = '.'
checks = {}
for fn in os.listdir(root):
    if fn.endswith('.gguf') or fn.endswith('.onnx'):
        h = hashlib.sha256()
        with open(fn,'rb') as f:
            for chunk in iter(lambda: f.read(1024*1024), b''):
                h.update(chunk)
        checks[fn] = h.hexdigest()
with open('checksums.json','w', encoding='utf-8') as f:
    json.dump(checks, f, indent=2, ensure_ascii=False)
print('Wrote checksums.json')
PY