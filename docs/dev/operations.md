# Operations and Troubleshooting

## Budgets
- View: `GET /api/v1/budget/status`
- Configure: `POST /api/v1/budget/config` (daily/monthly limits, enforce flag, cost per token)
- Enforcement: When enabled, chat requests are blocked (HTTP 429) if limits exceeded

## Models
- List: `GET /api/v1/models/all`
- Active selection: `GET /api/v1/models/select?profile=medium&task_type=chat`
- Integrity errors: Fix/restore file on mismatch. See [User Models](../user/models.md) and `scripts/get-models*`

## Health Checks
- Services: `GET /api/v1/health/services` (database, redis, models count, voice presence)
- Models: `GET /api/v1/health/models` (per-model checks)

## Docker/Compose naming
- Compose project name is `jarvisv2` → containers/networks are prefixed `jarvisv2-*`

## Voice
- 503 indicates missing executables or voice model
- Ensure the backend image includes whisper/piper and `./models` has a Piper `.onnx` voice

## Redis
- Used for caching chat responses and semantic search
- Health in `/api/v1/health/services`

## Model verification
- Verify against `checksums.json`:
  - Windows: `pwsh -NoProfile -File tests/verify-models.ps1`
  - macOS/Linux: `./tests/verify-models.sh`
- API surfaces integrity mismatches during selection/inference

## Privacy Configuration
- `/api/v1/privacy/settings`: { privacy_level: local_only|balanced|performance, data_retention_days, redact_aggressiveness }
- Cleanup: `POST /api/v1/privacy/cleanup` deletes messages older than `data_retention_days`
- AES key derived from `SECRET_KEY` + `PRIVACY_SALT` (env)

## Environment
- MODEL_PATH: directory with `.gguf` and voice files
- REDIS_URL: Redis connection string (compose default works)
- SECRET_KEY / PRIVACY_SALT: privacy encryption
- SEARCH_ENABLED (false by default) to allow `/search/unified`
- SEARCH_PROVIDERS: order CSV (e.g., `bing,google,tavily`)
- SEARCH_* provider keys
- REMOTE_LLM_ENABLED, REMOTE_LLM_PROVIDER, OPENAI_* (off by default)
- BUDGET_LLM_WEB_COST_PER_TOKEN_USD: cost control for remote LLM tokens

## Repository hygiene (.gitignore / .dockerignore)
- Source-only repo: no runtime data, models, logs, secrets, or build artifacts
- Excluded by default:
  - Data: `data/**`, `storage/**`, `*.sqlite`, `*.db*`
  - Models: `models/**`, `*.gguf`, `*.onnx`, `*.bin`, `*.safetensors`
  - Logs/artifacts: `logs/**`, `*.log*`, `node_modules/`, `dist/`, `target/`, `build/`, `__pycache__/`
  - Secrets: `.env`, `*.pem`, `*.key`, `*.p12`, `*.keystore` (only `.env.example` tracked)
- Docker context excludes the same sets to speed up builds

## Production Deployment
For production deployments, see the dedicated [Production Deployment Guide](production.md) which covers:
- Security hardening and configuration
- Production Docker Compose setup with resource limits
- Automated backup and restore procedures
- Monitoring, health checks, and structured logging
- Deployment automation scripts

## Smoke tests
- Windows (PowerShell): `powershell -NoProfile -ExecutionPolicy Bypass -File tests/smoke.ps1`
- Validates: health, model discovery/integrity, chat (basic/streaming), retrieval + redaction, budget enforcement, Redis caching, restart persistence, voice STT/TTS fallbacks
