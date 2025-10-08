# Developer Setup

## Prerequisites
- Docker and Docker Compose
- Node.js 18+ and npm
- (Optional) Rust toolchain for Tauri desktop dev
- (Optional) GNU Make for convenience targets
  - Windows (PowerShell): `winget install Kitware.CMake` (provides build tooling on Windows) or install a GNU Make package via winget/chocolatey. If `make` is not present, use the provided scripts instead.

## Python environment isolation (important)
Always use the dedicated virtual environment under `backend/.venv` for any local Python tooling (e.g., running tests, scripts). Do not install Python packages globally.

Windows (PowerShell):
```powershell
# one-time create
python -m venv backend/.venv
# activate
backend/.venv/Scripts/Activate.ps1
# install project deps (if needed locally)
pip install -r backend/requirements.txt
```

macOS/Linux (bash/zsh):
```bash
# one-time create
python3 -m venv backend/.venv
# activate
source backend/.venv/bin/activate
# install project deps (if needed locally)
pip install -r backend/requirements.txt
```

Note: The Docker image installs backend dependencies at build time. The `.venv` is for developers who run tools outside Docker (e.g., pytest locally).

## Quickstart with Make (optional)
If you have GNU Make available:
```bash
make help
make setup   # creates backend/.venv, installs backend deps, installs frontend deps
```
Then either:
- Run services via Docker: `docker compose up -d`
- Or run locally: `make dev` (starts backend + frontend dev; requires local prerequisites)

Windows notes:
- On Windows, ensure `make` resolves to a GNU Make binary. If not available, use `./scripts/dev.ps1` instead.

Compose project naming:
- docker-compose.yml sets `name: jarvisv2`, so containers are prefixed `jarvisv2-*` regardless of folder name.
- Alternatively, set `COMPOSE_PROJECT_NAME` via `.env` (see `.env_example`).

## One-command dev (scripts)
- Windows (PowerShell): `./scripts/dev.ps1`
- macOS/Linux (bash): `./scripts/dev.sh`

## Manual dev steps
1) Backend & Redis
- `docker compose up -d`
2) Frontend (Vite)
- `cd frontend && npm install && npm run dev` (http://localhost:5173)
3) Desktop (Tauri)
- From `frontend`, `cargo tauri dev` (requires platform prerequisites; see `docs/dev/packaging.md`)

## Environment configuration
See `docs/dev/operations.md` for full environment variable reference including:
- REDIS_URL, MODEL_PATH
- PRIVACY_ENCRYPT_AT_REST, SECRET_KEY, PRIVACY_SALT
- SEARCH_* flags and provider keys (off by default)
- REMOTE_LLM_* flags (off by default)
- Budget-related envs

## Models: download and verify
- Download: `./scripts/get-models.ps1` (Windows) or `./scripts/get-models.sh` (macOS/Linux)
- Verify hashes (optional but recommended):
  - Windows: `pwsh -NoProfile -File scripts/verify-models.ps1`
  - macOS/Linux: `./scripts/verify-models.sh`

## Tests and CI
- `cd backend && pytest -q`
- CI runs on push/PR: `.github/workflows/ci.yml`

## Useful endpoints (dev)
- Health: `/api/v1/health/services`, `/api/v1/health/models`
- Models: `/api/v1/models/all`, `/api/v1/models/select`
- Chat: `/api/v1/chat/send` and `/api/v1/chat/send/stream` (SSE; 429 if budget exceeded)
- Budget: `/api/v1/budget/status`, `/api/v1/budget/config`
- Memory: `/api/v1/memory/stats/{conversation_id}`
- Search: `/api/v1/search/semantic`, `/api/v1/search/unified`
