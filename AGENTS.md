# AI Assistant Rules

This file guides AI coding assistants contributing to this repository. It consolidates conventions, structure, and guardrails. Refer to [Project.md](Project.md) for requirements (read-only).

## Style & Conventions
- Backend: Python with PEP 8
- Frontend: TypeScript with React functional components and hooks
- Naming: snake_case (Python), camelCase (TypeScript)
- API routes: RESTful with versioning (`/api/v1/...`)
- Type hints: required in Python and TypeScript
- Async: prefer async/await for I/O in Python
- Validation: Pydantic models for request/response

## Project Structure (high-level)
- Backend: `backend/app/`
  - `api/v1/endpoints/` feature routers (chat, hardware, memory, privacy, voice, models, budget, search, health)
  - `services/` (hardware_detector, model_router, memory_service, privacy_service, voice_service, cache_service, budget_service, vector_store, embedding_service)
 - `models/` (database)
 - `core/` (config)
- Frontend: `frontend/` (React + Vite + optional Tauri)
  - `src/components/` (UI components like HardwareStatus.tsx, SettingsModal.tsx)
  - `src/services/` (API service with privacy, budget, and voice session methods)
- Scripts: `scripts/` (cleanup.ps1, cleanup.sh, devtools-windows.md, devtools-linux.md)
- Docs: `docs/` (user, dev, design), `AGENTS.md` (this file)
- Requirements: [Project.md](Project.md) (read-only)

## Common Tasks
- New API endpoint: add file under `backend/app/api/v1/endpoints/`, include in `api/v1/__init__.py`
- New service: add under `backend/app/services/`, single responsibility
- Frontend component: add file under `frontend/src/components/` (e.g., HardwareStatus.tsx, SettingsModal.tsx)
- Frontend service: extend `frontend/src/services/api.ts` with new methods for privacy, budget, and voice session functionality
- New script: add to `scripts/` with corresponding PowerShell (.ps1) and Bash (.sh) versions when cross-platform support is needed; consider if functionality can be integrated into existing consolidated scripts (main, get-models, dev-setup, setup, deploy, cleanup) rather than creating new standalone scripts
- Hardware/model routing: update `model_router.py` (discovery, selection)
- Dev setup: follow [docs/dev/setup.md](docs/dev/setup.md) or comprehensive guides in `scripts/dev/devtools-windows.md` and `scripts/dev/devtools-linux.md`; use Docker Compose and Makefile targets. Do not rely on missing or ad-hoc scripts.

## Implementation Guidelines
- Research similar OSS patterns when adding features
- Model integration: GGUF via llama.cpp; integrity hashed and verified
- Voice: Whisper STT and Piper TTS are built into Docker images (lazy init, 503 when unavailable)
- Wake word: `openwakeword` integration
- Vector embeddings: FAISS + local hashing embeddings
- Privacy: classify/redact; keep everything local-first

## Environment and Tooling (critical)
- Python environment isolation: ALWAYS use the project virtual environment at `backend/.venv` for any local Python tooling (lint, tests, scripts). Never install Python packages globally.
  - Windows (PowerShell):
    - Create: `python -m venv backend/.venv`
    - Activate: `backend/.venv/Scripts/Activate.ps1`
  - macOS/Linux (bash/zsh):
    - Create: `python3 -m venv backend/.venv`
    - Activate: `source backend/.venv/bin/activate`
  - Install deps (only if running locally outside Docker): `pip install -r backend/requirements.txt`
- Docker builds the backend dependencies from `backend/requirements.txt`. Do not mutate the image at runtime with ad-hoc installs.
- Makefile targets are cross-platform. On Windows, install GNU Make (e.g., via winget) or use the provided dev scripts if `make` is unavailable.
- Development environment setup: Use comprehensive guides in `scripts/dev/devtools-windows.md` for Windows or `scripts/dev/devtools-linux.md` for Linux as references for complete toolchain installation.
- Configuration strategy: Use development configuration (`docker-compose.dev.yml`, `backend/Dockerfile.dev`) while developing and testing. Use production configuration (`docker-compose.yml`, `backend/Dockerfile`) for production milestones and releases. For development, use `scripts/dev-setup.sh` (Linux/macOS) or `scripts/dev-setup.ps1` (Windows) to start the development environment.
- Development workflow: During active development, make changes using the development configuration which includes volume mounts for live reloading and development-optimized settings. When development milestones are completed and tested, ensure the changes work in both development and production configurations before committing. Always test changes in production configuration before merging to main branch.
- Environment configuration: For production deployments, copy `.env.example` to `.env` and configure with production values. For development, copy `.env.dev.example` to `.env` and configure with development values.

## Git safety

Never run destructive git commands without explicit approval:
- `git restore`, `git reset`, `git clean`, `git rebase`, history rewrites

If rollback is requested, propose the safest approach based on whether changes are committed or uncommitted.

## Requirements Alignment
- Always align with [Project.md](Project.md)
- Favor local-first processing; no cloud by default
- Respect dependency isolation; do not install globally inside dev machines

## Agent Readiness and Truthfulness Policy
* **System of record**
  * **SYSTEM_INVENTORY.md** is used to describe what exists: components, capabilities, and observed system state.
  * **CHANGE_LOG.md** is used to record verified changes to that state over time.
  * Each file defines its own usage guidance at the top and should be treated as the source of truth when making or evaluating entries.
* **Status taxonomy (MUST use in outputs when describing features/code/docs):**
  * **ready-to-use**: Verified with the Verification Checklist and evidence provided.
  * **partial**: Some functionality works; important gaps remain; not production-ready.
  * **placeholder**: Exists but does not implement the intended function.
  * **planned**: Not implemented.
* **Truthfulness**
  * Feature status must reflect observed reality.
  * Never label a feature *ready-to-use* without presenting verification evidence (commands + results).
  * When evidence is absent or incomplete, default to **partial**, **placeholder**, or **planned**, and reflect that state consistently across SYSTEM_INVENTORY.md, documentation, and responses.
* **Definition of Done (DoD) per capability (minimum):**
  * **Chat**: runnable inference binary in image; `.gguf` detected; `/chat/send` returns valid assistant response; budget enforcement and caching exercised.
  * **Voice**: wake-word detected; STT and TTS return outputs with bundled binaries; errors are actionable when voice model missing.
  * **Memory**: add/list/stats/semantic search work; export/import round-trip; referential integrity preserved or reported.
  * **Privacy**: classification + redaction work; data retention cleanup works; external calls gated by privacy level.
  * **Unified Search**: local + at least one web provider returns items; LLM escalation only when enabled and privacy/budget allow.
  * **Budget**: status shows totals and limits; enforcement blocks chat when exceeded; category-aware rate applied.
  * **Deployment**: `docker compose up -d` starts backend + Redis; health endpoints pass.
* **Verification Checklist (used before claiming *ready-to-use*):**
  * Build: `docker compose build backend`
  * Run: `docker compose up -d`
  * Health: `GET /api/v1/health/services`, `GET /api/v1/health/models`
  * Chat: `POST /api/v1/chat/send` with a sample prompt (with `.gguf` present)
  * Memory: conversations/messages/semantic search
  * Privacy: classify + cleanup
  * Search: semantic; unified (when enabled and redacted)
  * Budget: status; enforce 429 path
* **Documentation Integration**
  * Keep SYSTEM_INVENTORY.md aligned with observed system state.
  * Record verified changes in CHANGE_LOG.md.
  * User docs: only *ready-to-use* features.
  * Dev docs: partial features allowed but must be labeled with status and gaps; link to DoD and verification context.
  * Keep documentation lean and organized: consolidate related information, avoid redundancy, and integrate into existing files where appropriate.
* **Task Protocol**
  * Every task includes Scope, Acceptance Criteria, and Verification Steps.
  * Completion claims should align with SYSTEM_INVENTORY.md state and, when applicable, be reflected in CHANGE_LOG.md.
* **Feature Flags**
  * Experimental or remote features default OFF.
  * Enable only with explicit user approval and clear exposure of configuration changes.
* **Standard Response Headers (prepend when applicable):**
  * **Status**: `<ready-to-use | partial | placeholder | planned>`
  * **Evidence**: `<what checks ran / "not executed">`
  * **Next**: `<minimal steps to reach next status>`

## Testing and Validation
- For testing the application, use the consolidated test approach:
  - **Smoke tests**: `tests/smoke.ps1` (Windows) or `tests/smoke.sh` (Linux/macOS) - Full end-to-end validation
  - **Unit tests**: `tests/unit-test.ps1` (Windows) or `tests/unit-test.sh` (Linux/macOS) - Backend service tests
  - **Model verification**: `tests/verify-models.ps1` (Windows) or `tests/verify-models.sh` (Linux/macOS) - Check model integrity
  - **Consolidated runner**: `tests/run-all-tests.ps1` (Windows) or `tests/run-all-tests.sh` (Linux/macOS) - Execute all test suites in sequence
- When adding new functionality, ensure appropriate tests are added to the relevant test category
- Keep documentation concise and organized: consolidate related information into fewer files, eliminate redundant content, and maintain clear, logical structure. When adding new documentation, consider if it can be integrated into existing files rather than creating new ones.
