# CHANGE_LOG.md

## Rules
- Append-only record of reported work; corrections may be appended to entries.
- Write an entry only after the mini-phase objective is “done” and supported by evidence.
- No edits/reorders/deletes of past entries. If an entry is wrong, append a corrective entry.
- **Ordering:** Entries are maintained in **descending chronological order** (newest first, oldest last).
- **Append location:** New entries must be added **at the top of the Entries section**, directly under `## Entries`.
- Each entry must include:
  - Timestamp: `YYYY-MM-DD HH:MM`
  - Summary: 1–2 lines, past tense
  - Scope: files/areas touched
  - Evidence: exact command(s) run + a minimal excerpt pointer (or embedded excerpt ≤10 lines)
- If a change is reverted, append a new entry describing the revert and why.

## Entries

- 2026-02-05 08:57
  - Summary: Docker alignment completed; app logs routed to `/app/data/logs`, dev models mount set read-only, and dev/prod runners verified healthy.
  - Scope: backend/app/core/logging_config.py; docker-compose.dev.yml; docker-compose.yml
  - Evidence: `docker compose -f docker-compose.dev.yml ps`; `docker compose -f docker-compose.yml ps`
    ```text
    jarvisv2-backend-1 ... Up ... (healthy)
    jarvisv2-prod-backend-1 ... Up ... (healthy)
    ```

- 2026-02-04 07:25
  - Summary: CHANGE_LOG.md established
  - Scope: CHANGE_LOG.md
  - Evidence: `cat .\CHANGE_LOG.md -head 1`
    ```text
    # CHANGE_LOG.md
    ```