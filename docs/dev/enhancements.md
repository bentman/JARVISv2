# Enhancements (curated)

This page tracks notable enhancements beyond core readiness. Items are prioritized for developer and user experience.

Status key: [P] Priority, [R] Rationale

1) Piper TTS enablement (DONE)
- [P] high  [R] Prefer Piper when voice models are present; local fallback remains
- Implemented: Piper CLI bundled in backend image; voice service prefers Piper with .onnx present

2) Hardware detection breadth (DONE)
- [P] high  [R] Better model routing across hardware
- Implemented: onnxruntime providers (CUDA/ROCm/DirectML/CoreML) considered in detection/profile

3) Desktop packaging CI (DONE)
- [P] medium  [R] Ensure cross-platform builds
- Implemented: GitHub Actions workflow builds Tauri app for Win/macOS/Linux (unsigned)

4) Model provisioning & integrity UX (DONE)
- [P] medium  [R] Safer downloads; clear verification
- Implemented: checksums.json support in router, verify-models scripts

5) Unified Search provider readiness (NEXT)
- [P] high  [R] Enable opt-in web search escalation with robustness
- TODO: Clear provider env setup examples; rate limiting; retries/backoff; error normalization; caching

6) UI/UX polish (NEXT)
- [P] medium  [R] Better control and discoverability
- TODO: Settings panels, tray integration, first-time setup wizard

7) Memory synchronization (NEXT)
- [P] medium  [R] Cross-device continuity
- TODO: Sync framework with versioning, conflict resolution, export/import flow

8) Testing expansion (NEXT)
- [P] medium  [R] Reliability and regression safety
- TODO: Voice endpoint coverage, SSE streaming, privacy redaction edge cases, search escalation E2E

9) Observability & hardening
- [P] medium  [R] Operational clarity
- TODO: Structured logs, optional metrics, production CORS/TLS reverse proxy patterns
