# Local AI Assistant

A privacy-first, local-only AI assistant that runs entirely on your hardware. Cross-platform (Windows/macOS/Linux), with chat, voice, and semantic search — all processed locally by default.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platforms](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](#)

## Overview
- Local inference: Llama/Mistral (GGUF), Whisper STT, Piper TTS (fallback to espeak-ng)
- Hardware-aware routing (CPU/GPU/NPU via onnxruntime providers)
- Memory with FAISS vector search, Redis caching, privacy redaction/encryption
- Optional unified web search and LLM escalation (off by default)

## Quick Start
1) Download models (one time)
- Windows: `./scripts/get-models.ps1`
- macOS/Linux: `./scripts/get-models.sh`

2) Start services
- `docker compose up -d`

3) Launch UI (dev)
- `cd frontend && npm install && npm run dev` → http://localhost:5173

4) Run smoke test (Windows)
- `powershell -NoProfile -ExecutionPolicy Bypass -File tests/smoke.ps1`

## Documentation (by audience)
- Users: [docs/user/index.md](docs/user/index.md) (getting started, voice, models)
- Developers: [docs/dev/setup.md](docs/dev/setup.md), [docs/dev/api.md](docs/dev/api.md), [docs/dev/operations.md](docs/dev/operations.md), [docs/dev/packaging.md](docs/dev/packaging.md)
- **Production**: [docs/dev/production.md](docs/dev/production.md) (security, deployment, monitoring, backups)
- Design/Architecture: [docs/design/system-design.md](docs/design/system-design.md), [docs/design/components.md](docs/design/components.md)
- AI Assistant Rules (for LLMs contributing here): [agent.md](agent.md)
- Requirements (read-only): [Project.md](Project.md)

## Tech Stack
Backend: FastAPI (Python), SQLite, FAISS, Redis, ONNX Runtime
Frontend: Tauri (Rust) + React + Tailwind CSS
Models: Llama 3.2, Mistral 7B, Whisper, Piper (CLI in backend image)

## License
MIT — see [LICENSE](LICENSE).
