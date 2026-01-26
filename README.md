# JARVISv2 - Local AI Assistant

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Status: Inactive](https://img.shields.io/badge/Status-No%20Longer%20Maintained-red)
![Successor: JARVISv3](https://img.shields.io/badge/Successor-JARVISv3-blue)

> This project has evolved and is now succeeded by [**JARVISv3**](https://github.com/bentman/JARVISv3)

- A privacy-first, local-only AI assistant that runs entirely on your hardware. 
- Cross-platform (Windows/macOS/Linux), with chat, voice, and semantic search — all processed locally by default.

## Overview
- Local inference: Llama/Mistral (GGUF), Whisper STT, Piper TTS (fallback to espeak-ng)
- Hardware-aware routing (CPU/GPU/NPU via onnxruntime providers)
- Memory with FAISS vector search, Redis caching, privacy redaction/encryption
- Optional unified web search and LLM escalation (off by default)

## Quick Start
1) Download models (one time)
- Windows: `./scripts/get-models.ps1 -Environment dev` (development) or `./scripts/get-models.ps1 -Environment prod` (production)
- macOS/Linux: `./scripts/get-models.sh -e dev` (development) or `./scripts/get-models.sh -e prod` (production)

2) Start services
- Production: `docker compose up -d`
- Development: `./scripts/dev-setup.sh` (Linux/macOS) or `./scripts/dev-setup.ps1` (Windows)

3) For development workflows, you can also use:
- `make setup` - Set up development environment (creates virtual environment, installs deps)
- `make dev` - Start both backend and frontend in development mode
- `make` - Show all available targets

4) Launch UI (dev)
- `cd frontend && npm install && npm run dev` → http://localhost:5173

5) Run smoke test (Windows)
- `powershell -NoProfile -ExecutionPolicy Bypass -File tests/smoke.ps1`

## Documentation
- **User Guide**: [docs/user-guide.md](docs/user-guide.md) (getting started, voice, models, troubleshooting)
- **AI Assistant Rules** (for LLMs contributing here): [agent.md](agent.md)
- **Requirements** (read-only): [Project.md](Project.md)
- **Script Reorganization**: [docs/script-reorganization.md](docs/script-reorganization.md) (details on script consolidation)
- **Development Tools**: [scripts/devtools-windows.md](scripts/devtools-windows.md) (Windows) and [scripts/devtools-linux.md](scripts/devtools-linux.md) (Linux) comprehensive setup guides

## Script Organization
The project uses a consolidated script approach for simplicity:
- **Primary Scripts**: [scripts/main.ps1](scripts/main.ps1) / [scripts/main.sh](scripts/main.sh) - Main entry point for all common operations (setup, models, dev, dev-setup, deploy, test, etc.)
- **Model Management**: [scripts/get-models.ps1](scripts/get-models.ps1) / [scripts/get-models.sh](scripts/get-models.sh) - Download models for dev or production environments
- **Setup**: [scripts/setup.ps1](scripts/setup.ps1) / [scripts/setup.sh](scripts/setup.sh) - Complete environment setup for dev or production
- **Deployment**: [scripts/deploy.ps1](scripts/deploy.ps1) / [scripts/deploy.sh](scripts/deploy.sh) - Production deployment with backup and monitoring
- **Development Utilities**: [scripts/cleanup.ps1](scripts/cleanup.ps1) / [scripts/cleanup.sh](scripts/cleanup.sh) - Environment cleanup
- **Tests**: [tests/](tests/) directory contains all test and verification scripts

The dev and dev-setup functionality has been integrated into the main script for better consolidation.

## Environment Configuration
- Production: Copy `.env.example` to `.env` and configure for production
- Development: Copy `.env.dev.example` to `.env` and configure for development

## Testing and Validation
For testing the application, we provide comprehensive test suites:
- **Smoke tests**: [tests/smoke.ps1](tests/smoke.ps1) / [tests/smoke.sh](tests/smoke.sh) - Full end-to-end validation
- **Unit tests**: [tests/unit-test.ps1](tests/unit-test.ps1) / [tests/unit-test.sh](tests/unit-test.sh) - Backend service tests
- **Model verification**: [tests/verify-models.ps1](tests/verify-models.ps1) / [tests/verify-models.sh](tests/verify-models.sh) - Check model integrity
- **Consolidated runner**: [tests/run-all-tests.ps1](tests/run-all-tests.ps1) / [tests/run-all-tests.sh](tests/run-all-tests.sh) - Execute all test suites in sequence

## Tech Stack
Backend: FastAPI (Python), SQLite, FAISS, Redis, ONNX Runtime
Frontend: Tauri (Rust) + React + Tailwind CSS
Models: Llama 3.2, Mistral 7B, Whisper, Piper (CLI in backend image)

## License
MIT — see [LICENSE](LICENSE).
