# API Reference (v1)

All endpoints are under `/api/v1` unless noted.

## Health
- GET `/health/services` → { database, redis, models_count, voice: { whisper_exec, piper_exec, piper_voice } }
- GET `/health/models` → { models: [{ name, path, exists, hash }] }

## Models
- GET `/models/all` → { names, profiles, paths, hashes }
- GET `/models/select?profile=medium&task_type=chat` → { profile, task_type, model_name, model_path }

## Chat
- POST `/chat/send` body: { message: string, mode?: "chat" | "coding" | "reasoning", stream?: boolean }
  - 200: [{ type: "thinking" | "response" | "done", content: string, tokens_used?: number }]
  - 429: budget enforcement (detail includes daily/monthly)

## Budget
- GET `/budget/status` → daily/monthly usage and limits
- POST `/budget/config` → set { daily_limit_usd?, monthly_limit_usd?, enforce?, cost_per_token_usd? }

## Memory
- GET `/memory/conversations`
- GET `/memory/conversation/{id}`
- POST `/memory/save` body: { id, content, created_at, tags[], access_level }
- GET `/memory/search?query=...`
- POST `/memory/search` body: { query }
- GET `/memory/stats/{conversation_id}` → { conversation_id, total_messages, total_tokens }

## Search
- POST `/search/semantic` body: { query } → list of message-like results
- POST `/search/unified` body: { query, include_local?: boolean, include_web?: boolean, web_sources?: string[], max_results?: number, escalate_llm?: boolean }
  - Returns: { query, count, web_used, used: { local: boolean, web: string[], llm: boolean }, items: [ { source: "memory" | "web" | "llm", provider?, ... } ] }
  - Web requires: `SEARCH_ENABLED=true` and at least one configured provider. Calls are only allowed when `privacy_level != local_only`. Queries/snippets are redacted before external calls.
  - LLM escalation requires: `REMOTE_LLM_ENABLED=true`, provider/API keys configured, privacy level allows external calls, and budget permits.

## Hardware
- GET `/hardware/detect` → profile and machine capabilities
- GET `/hardware/profile` → current profile

## Privacy
- GET `/privacy/settings` → returns { privacy_level, data_retention_days, redact_aggressiveness }
- POST `/privacy/settings` → set { privacy_level, data_retention_days, redact_aggressiveness }
- POST `/privacy/classify` | `/privacy/enforce-local-processing` | `/privacy/redact-sensitive-data`
- GET `/privacy/classification-info` → lists classification values and privacy-level options
- POST `/privacy/cleanup` → deletes messages older than configured data_retention_days

## Voice
- POST `/voice/stt` body: { audio_data: base64 } → { text, confidence }
  - 400: invalid base64
  - 503: Whisper missing/unavailable
- POST `/voice/tts` body: text → { audio_data: base64 }
  - 503: Piper missing/unavailable/voice not found
- POST `/voice/wake-word` body: { audio_data: base64 } → { detected: boolean }
- POST `/voice/upload-audio` form-data file → { text, confidence, filename }