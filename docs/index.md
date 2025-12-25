# User Guide

Welcome to the Local AI Assistant. This guide helps you run the app and start chatting locally with privacy.

## Quickstart (all platforms)

1) Get models and voice (one-time)
- Windows (PowerShell): `./scripts/get-models.ps1`
- macOS/Linux (bash): `./scripts/get-models.sh`

2) Start services
- Production: `docker compose up -d`
- Development: `./scripts/dev-setup.sh` (Linux/macOS) or `./scripts/dev-setup.ps1` (Windows) (or use main scripts: `./scripts/main.sh dev-setup` or `./scripts/main.ps1 -Command dev-setup`)

3) Launch UI (dev)
- `cd frontend && npm install && npm run dev` → http://localhost:5173

4) Run smoke test (Windows)
- `powershell -NoProfile -ExecutionPolicy Bypass -File tests/smoke.ps1`

FYI: By default, voice TTS uses Piper (bundled in Docker image) when a voice `.onnx` exists under `./models`, otherwise it falls back to `espeak-ng`. External web search is off by default for privacy; configuration options can be found in the application settings.

## First Chat
- Open the UI (Vite dev) at http://localhost:5173
- Click "Check Backend Health" then "Detect Hardware"
- Type a message and press "Send"

## Voice Session (hands-free)
- You can invoke a one-shot voice session via API: `POST /api/v1/voice/session` with body `{ audio_data: base64 }`.
- The server performs wake word detection (non-fatal), STT, responds via chat, and returns TTS audio `{ audio_data: base64 }`.
- Optional flags: `include_web`, `escalate_llm`.

## Models and Voices

### Recommended Models
The project does not include model files. Use the provided scripts to download recommended models locally.

**Recommended GGUF LLM**:
- TinyLlama 1.1B Chat v1.0 (Q4_K_M GGUF for production, Q2_K for development)
  - Source: Hugging Face (TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF)
  - License: Apache 2.0 (verify upstream)
  - Size: ~0.7–1.2 GB depending on quantization

**Recommended Piper Voice**:
- en_US-amy-low.onnx
  - Source: rhasspy/piper-voices releases
  - License: See upstream project

#### Usage
- Windows (PowerShell): `./scripts/get-models.ps1 -Environment dev` or `./scripts/get-models.ps1 -Environment prod`
- macOS/Linux (bash): `./scripts/get-models.sh -e dev` or `./scripts/get-models.sh -e prod`

The scripts download model files to `./models` and create `./models/checksums.json` with SHA256 hashes.

#### Integrity
- The backend computes and stores SHA256 for discovered `.gguf` files and verifies them pre-inference.
- You can view discovered models, paths, and hashes via `GET /api/v1/models/all`.
- If a file is altered, requests fail with an integrity error until the file is restored.

## Troubleshooting
- Budget limit exceeded (HTTP 429): adjust via `POST /api/v1/budget/config`
- Missing model / integrity error: run the model scripts again or restore file; check `/api/v1/health/models`
- Voice errors (HTTP 503): ensure whisper/piper executables are bundled (Docker image) and a Piper `.onnx` voice file exists in `./models`
- Privacy cleanup: to remove older messages, call `POST /api/v1/privacy/cleanup` after setting `data_retention_days` in `/api/v1/privacy/settings`.

## Environment Configuration
- Production: Copy `.env.example` to `.env` for production settings
- Development: Copy `.env.dev.example` to `.env` for development settings

## Smoke test
- Windows (PowerShell): `powershell -NoProfile -ExecutionPolicy Bypass -File tests/smoke.ps1`
- The script validates health, chat (including streaming), retrieval, privacy redaction, budget enforcement (429), caching speedup, persistence across restarts, and voice STT/TTS fallbacks.
