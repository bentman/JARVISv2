#!/usr/bin/env bash
set -euo pipefail
MODELS_DIR=${1:-models}
if [ ! -d "$MODELS_DIR" ]; then echo "Models directory not found: $MODELS_DIR"; exit 1; fi
if [ ! -f "$MODELS_DIR/checksums.json" ]; then echo "checksums.json not found in $MODELS_DIR"; exit 1; fi
python - "$MODELS_DIR" <<'PY'
import sys, os, json, hashlib
root = sys.argv[1]
checks = json.load(open(os.path.join(root,'checksums.json'), encoding='utf-8'))
failed = False
for fn in os.listdir(root):
    if not (fn.endswith('.gguf') or fn.endswith('.onnx')):
        continue
    p = os.path.join(root, fn)
    h = hashlib.sha256()
    with open(p,'rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    val = h.hexdigest()
    exp = checks.get(fn)
    if not exp:
        print(f"WARN: No expected hash for {fn}")
    elif exp != val:
        print(f"MISMATCH: {fn}")
        failed = True
    else:
        print(f"OK: {fn}")
if failed:
    sys.exit(2)
print("All model files verified.")
PY