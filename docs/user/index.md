# User Guide

Welcome to the Local AI Assistant. This guide helps you run the app and start chatting locally with privacy.

## Quickstart (all platforms)

1) Get models and voice (one-time)
- Windows (PowerShell): `./scripts/get-models.ps1`
- macOS/Linux (bash): `./scripts/get-models.sh`

2) Start backend and Redis
- `docker compose up -d`

3) Launch the UI
- `cd frontend && npm install && npm run dev` (http://localhost:5173)
- Optional desktop window: `cargo tauri dev` from `frontend` (requires Rust + Tauri prerequisites)

4) Verify health
- Services: `GET http://localhost:8000/api/v1/health/services`
- Models: `GET http://localhost:8000/api/v1/health/models`

FYI: By default, voice TTS uses Piper when a voice `.onnx` exists under `./models`, otherwise it falls back to `espeak-ng`. External web search is off by default for privacy; see `docs/dev/operations.md` to enable.

## First Chat
- Open the UI (Vite dev) at http://localhost:5173
- Click "Check Backend Health" then "Detect Hardware"
- Type a message and press "Send"

## Voice Session (hands-free)
- You can invoke a one-shot voice session via API: `POST /api/v1/voice/session` with body `{ audio_data: base64 }`.
- The server performs wake word detection (non-fatal), STT, responds via chat, and returns TTS audio `{ audio_data: base64 }`.
- Optional flags: `include_web`, `escalate_llm`.

## Models
- Where: `./models` (created by the scripts)
- View discovered models/hashes: `GET /api/v1/models/all`
- Integrity: the backend verifies SHA256 before inference; altered files will be rejected

## Troubleshooting
- Budget limit exceeded (HTTP 429): adjust via `POST /api/v1/budget/config`
- Missing model / integrity error: run the model scripts again or restore file; check `/api/v1/health/models`
- Voice errors (HTTP 503): ensure whisper/piper executables are bundled (Docker image) and a Piper `.onnx` voice file exists in `./models`
- Privacy cleanup: to remove older messages, call `POST /api/v1/privacy/cleanup` after setting `data_retention_days` in `/api/v1/privacy/settings`.

## Smoke test
- Windows (PowerShell): `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/smoke.ps1`
- The script validates health, chat (including streaming), retrieval, privacy redaction, budget enforcement (429), caching speedup, persistence across restarts, and voice STT/TTS fallbacks.
