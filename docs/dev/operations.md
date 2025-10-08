# Operations and Troubleshooting

## Budgets
- View: `GET /api/v1/budget/status`
- Configure: `POST /api/v1/budget/config` with daily/monthly limits, enforce flag, and cost per token.
- Enforcement: When enabled, chat requests are blocked (HTTP 429) if limits exceeded.

## Models
- List: `GET /api/v1/models/all`
- Active selection: `GET /api/v1/models/select?profile=medium&task_type=chat`
- Integrity errors: If a model file hash mismatches, fix/restore the file. See [Models.md](../user/models.md) and `scripts/get-models`.

## Health Checks
- Services: `GET /api/v1/health/services` (database, redis, models count, voice presence)
- Models: `GET /api/v1/health/models` (per-model checks)

## Docker/Compose naming
- Compose project name is set to `jarvisv2` in `docker-compose.yml`, so containers/networks are prefixed with `jarvisv2-*` regardless of folder name.

## Voice
- Errors 503 indicate missing executables or voice model. Ensure the backend Docker image includes whisper/piper and `./models` has a voice file.

## Redis
- Redis is used for caching chat responses and semantic search
- Health: `GET /api/v1/health/services` shows redis status

## Model verification
- After downloading models, verify file integrity against `checksums.json`:
  - Windows: `pwsh -NoProfile -File scripts/verify-models.ps1`
  - macOS/Linux: `./scripts/verify-models.sh`
- Integrity mismatches will be surfaced by the API as well during model selection and inference.

## Privacy Configuration
- Settings are persisted via `/api/v1/privacy/settings` and include:
  - `privacy_level`: `local_only` | `balanced` | `performance`
  - `data_retention_days`: number of days for retention
  - `redact_aggressiveness`: `standard` | `strict`
- Cleanup: `POST /api/v1/privacy/cleanup` deletes messages older than `data_retention_days`.
- Key derivation: AES key is derived from `SECRET_KEY` and `PRIVACY_SALT` (env). Do not expose these in logs.

## Environment
- MODEL_PATH: directory that contains `.gguf` and voice files
- REDIS_URL: connection string for Redis (default from docker compose)
- SECRET_KEY: used for privacy encryption derivation
- PRIVACY_SALT: used together with SECRET_KEY to derive AES key
- SEARCH_ENABLED: `true` to allow external web search calls via `/search/unified`
- SEARCH_PROVIDERS: provider order CSV (e.g., `bing,google,tavily`)
- SEARCH_PROVIDER: legacy single name (kept for back-compat)
- SEARCH_API_KEY: Tavily API key
- SEARCH_BING_ENDPOINT: Bing endpoint (default `https://api.bing.microsoft.com/v7.0/search`)
- SEARCH_BING_API_KEY: key for Bing Web Search
- SEARCH_GOOGLE_API_KEY: key for Google Programmable Search Engine
- SEARCH_GOOGLE_CX: Custom Search Engine ID (Google CSE)
- REMOTE_LLM_ENABLED: `true` to allow LLM synthesis
- REMOTE_LLM_PROVIDER: `openai` (current support)
- OPENAI_API_KEY / OPENAI_MODEL: provider credentials
- BUDGET_LLM_WEB_COST_PER_TOKEN_USD: cost control for remote LLM tokens

## Smoke tests
- Windows (PowerShell): `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/smoke.ps1`
- The script validates: health, model discovery (integrity), chat (basic + streaming), retrieval + redaction, budget enforcement (429), Redis caching speedup, persistence across restarts, and voice STT/TTS fallbacks.
