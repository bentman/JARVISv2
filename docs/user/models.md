# Models and Voices

This project does not include model files. Use the provided scripts to download recommended models locally.

## Recommended GGUF LLM
- TinyLlama 1.1B Chat v1.0 (Q4_K_M GGUF)
  - Source: Hugging Face (TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF)
  - License: Apache 2.0 (verify upstream)
  - Size: ~0.7–1.2 GB depending on quantization

## Recommended Piper Voice
- en_US-amy-low.onnx
  - Source: rhasspy/piper-voices releases
  - License: See upstream project

## Usage

- Windows (PowerShell):
  - `./scripts/setup/get-models.ps1`
- macOS/Linux (bash):
  - `./scripts/setup/get-models.sh`

The scripts download model files to `./models` and create `./models/checksums.json` with SHA256 hashes.

## Integrity

- The backend computes and stores SHA256 for discovered `.gguf` files and verifies them pre-inference.
- You can view discovered models, paths, and hashes via `GET /api/v1/models/all`.
- If a file is altered, requests fail with an integrity error until the file is restored.