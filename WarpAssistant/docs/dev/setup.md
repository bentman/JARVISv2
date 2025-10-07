# Developer Setup

## Prerequisites
- Docker and Docker Compose
- Node.js 18+ and npm
- (Optional) Rust toolchain for Tauri desktop dev

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

## One-command dev
- Windows (PowerShell): `./scripts/dev.ps1`
- macOS/Linux (bash): `./scripts/dev.sh`

## Manual dev steps
1) Backend & Redis
- `docker compose up -d`
2) Frontend (Vite)
- `cd frontend && npm install && npm run dev` (http://localhost:5173)
3) Desktop (Tauri)
- From `frontend`, `cargo tauri dev` (requires platform prerequisites; see `docs/dev/packaging.md`)

## Tests and CI
- `cd backend && pytest -q`
- CI runs on push/PR: `.github/workflows/ci.yml`

## Useful endpoints (dev)
- Health: `/api/v1/health/services`, `/api/v1/health/models`
- Models: `/api/v1/models/all`, `/api/v1/models/select`
- Chat: `/api/v1/chat/send` (429 if budget exceeded)
- Budget: `/api/v1/budget/status`, `/api/v1/budget/config`
- Memory: `/api/v1/memory/stats/{conversation_id}`
- Search: `/api/v1/search/semantic`