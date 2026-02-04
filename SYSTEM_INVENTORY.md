# SYSTEM_INVENTORY.md
Authoritative capability ledger. This is not a roadmap or config reference. Inventory entries must reflect only observable artifacts in this repository: files, directories, executable code, configuration, scripts, and explicit UI text. Do not include intent, design plans, or inferred behavior.

## Rules
- One component entry = one capability or feature observed in the repository.
- New capabilities go at the top under `## Inventory` and above `## Observed Initial Inventory:`.
- Entries must include: 
  - Capability: **Brief Descriptive Component Name** - Date/Time
  - State: Planned, Implemented, Verified, Defferred
  - Location: `Relative File Path(s)`
  - Validation: Method &/or `Relative Script Path(s)`
  - Notes: Optional (1 line max).
- Do not include environment values, wiring details, or implementation notes.
- Corrections or clarifications go only below the `## Appendix` section.

## States
- Planned: intent only, not implemented
- Implemented: code exists, not yet validated end-to-end
- Verified: validated with evidence (command)
- Deferred: intentionally postponed (reason noted)

## Inventory

## Observed Initial Inventory: 2026-02-04

### Backend (FastAPI)
- **API application (`backend/app/main.py`)** — FastAPI app with CORS, root and `/health` endpoints.
- **API v1 router (`backend/app/api/v1/__init__.py`)** — mounts endpoint groups: chat, hardware, memory, voice, privacy, budget, search, models, health.

#### API Endpoints (observed in `backend/app/api/v1/endpoints/`)
- **Chat (`chat.py`)** — `/chat/send` and `/chat/send/stream` with retrieval-augmented prompt building, budget enforcement, caching, and memory persistence.
- **Hardware (`hardware.py`)** — `/hardware/detect` and `/hardware/profile` using hardware detector.
- **Memory (`memory.py`)** — conversation/message CRUD, tags, import/export, semantic search, stats.
- **Voice (`voice.py`)** — STT, TTS, wake-word detection, file upload, and one-shot voice session flow.
- **Privacy (`privacy.py`)** — privacy settings, classification, redaction, local-processing enforcement, retention cleanup.
- **Budget (`budget.py`)** — budget status and configuration endpoints.
- **Search (`search.py`)** — semantic search and unified search endpoints with opt-in web search.
- **Models (`models.py`)** — list discovered GGUF models and resolve selection paths.
- **Health/metrics (`health.py`)** — service checks, model integrity, readiness/liveness, and metrics.

#### Backend Services (observed in `backend/app/services/`)
- **Model router (`model_router.py`)** — selects GGUF models, runs llama.cpp inference, scans models directory, verifies hashes.
- **Hardware detector (`hardware_detector.py`)** — CPU/GPU/memory detection, profile selection, NPU heuristics.
- **Memory service (`memory_service.py`)** — conversation storage, semantic search, vector store integration.
- **Vector store (`vector_store.py`)** — FAISS index persistence and search.
- **Embedding service (`embedding_service.py`)** — local hashing-based embeddings (no external model download).
- **Voice service (`voice_service.py`)** — Whisper STT, Piper/espeak TTS, wake-word detection with lazy initialization.
- **Privacy service (`privacy_service.py`)** — data classification, redaction, settings, retention cleanup.
- **Budget service (`budget_service.py`)** — budget event tracking and enforcement.
- **Cache service (`cache_service.py`)** — Redis cache wrapper for chat/memory search.
- **Search providers (`search_providers.py`)** — Bing, Google CSE, Tavily provider wrappers.
- **Unified search (`unified_search_service.py`)** — memory + optional web search, optional remote LLM summarization.
- **External LLM providers (`external_llm_providers.py`)** — OpenAI summarization adapter.

#### Data Layer (observed in `backend/app/models/`)
- **SQLModel DB (`database.py`)** — SQLite-backed conversation/message storage, encryption-at-rest helpers, import/export, tag helpers.

### Frontend (React + Vite + Tailwind)
- **App entry (`frontend/src/App.tsx`)** — renders `ChatInterface` full-screen.
- **Chat interface (`frontend/src/components/ChatInterface.tsx`)** — UI for messaging, voice toggle, settings modal, hardware status; web search toggle present in UI.
- **Hardware status (`frontend/src/components/HardwareStatus.tsx`)** — polls backend hardware endpoint every 30s.
- **Settings modal (`frontend/src/components/SettingsModal.tsx`)** — tabs for privacy, search, budget.
  - **Search tab status: placeholder** — UI text states providers are configured via env vars and not runtime configurable; toggle list is static/disabled.
- **API client (`frontend/src/services/api.ts`)** — fetch-based wrapper for backend endpoints.
- **Voice client (`frontend/src/services/voiceService.ts`)** — browser MediaRecorder + STT + TTS calls.
- **Service index (`frontend/src/services/index.ts`)** — exports voice service singleton.

### Desktop Shell (Tauri)
- **Tauri config (`frontend/src-tauri/tauri.conf.json`)** — build/dev configuration and bundle metadata.
- **Tauri main (`frontend/src-tauri/src/main.rs`)** — minimal Tauri app with devtools in debug.

### Models Directory
- **`models/`** — contains `.gitkeep` only. **Status: placeholder** (no models committed).

### Ops & Configuration
- **Docker** — `backend/Dockerfile`, `backend/Dockerfile.dev`, `docker-compose.yml`, `docker-compose.dev.yml`.
- **Environment templates** — `.env.example`, `.env.dev.example`.
- **Makefiles** — `Makefile`, `Makefile.dev`.

### Scripts (observed in `scripts/`)
- **Main orchestration** — `main.ps1`, `main.sh` (setup/models/dev/deploy/test/verify/cleanup/voice-test).
- **Setup/Dev/Deploy** — `setup.*`, `dev-setup.*`, `dev.*`, `deploy.*`, `cleanup.*`.
- **Model utilities** — `get-models.*`, `verify-models.*`.
- **Smoke utilities** — `smoke.ps1`.
- **Voice loop** — `voice_loop.py`.
- **Docs** — `scripts/README.md`, `devtools-*.md`.

### Tests
- **Backend unit tests (`backend/tests/`)** — budget, memory, model integrity/router, privacy, unified search, vector store, voice lazy init.
- **Scripted tests (`tests/`)** — smoke tests, unit-test runner, model verification, consolidated runners.

### Documentation
- **README (`README.md`)** — project overview and setup instructions; notes project is inactive and points to successor.
- **Docs (`docs/`)** — user guide, script reorganization notes.
- **Requirements (`Project.md`)** — product requirements document (reference-only; not executable code).

## Appendix
