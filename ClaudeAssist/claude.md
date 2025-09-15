# MMP Product Requirements Document (PRD) – Local-First AI Assistant

## 1. Goal

Deliver a **local-first AI assistant** as a Minimum Marketable Product (MMP). It must support **chat + voice interaction + reasoning + coding**. The product must run **fully offline**, across hardware tiers (CPU, GPU, NPU), with a **Docker-based backend** and a **Tauri (Rust) desktop frontend**.

AI generating this repo must output **full usable files** (no truncation, no TODOs, no placeholders).

---

## 2. System Overview

* **Backend** (Docker container): lightweight orchestration service with endpoints for chat, memory, and search. Handles model routing, local persistence, and API for frontend.
* **Frontend** (Tauri desktop app): cross-platform UI with chat + voice loop. Handles hardware detection, user interaction, and simple model configuration.
* **Local model execution**: select models by **hardware tier**. Use VRAM/NPU detection rules, not hardcoded models.

### Hardware Profiles (research required)

* **Light (CPU only)**: single small model, acceptable latency (<5s).
* **Medium (GPU 4–8 GB VRAM)**: chat + reasoning/coding model pair.
* **Heavy (GPU >8 GB VRAM)**: multi-model (chat + reasoning + coding).
* **NPU (Apple, Qualcomm, Intel, others)**: 2–3 ONNX/CoreML-optimized models for speech + reasoning.

---

## 3. Requirements

### Backend

* Implement in Docker container.
* Endpoints:

  * `/chat`: routes chat between frontend and models.
  * `/memory`: local persistence (SQLite or lightweight alternative).
  * `/search`: stub/local search expansion point.
* Routing logic:

  * Select model(s) based on detected hardware tier.
  * Route queries to chat, reasoning, or code models depending on input type.
* Research open-source projects (e.g., LocalAI, LangChain) for routing and embeddings but build minimal custom service.

### Frontend

* Built with Tauri (Rust).
* Cross-platform: Windows, macOS, Linux.
* Features:

  * Chat UI (borrow design patterns from AnythingLLM).
  * Voice loop (wake word → STT → response → TTS).
  * Hardware detection (research ONNX Runtime or equivalent).
  * Display active hardware tier + model usage; allow simple model override.
* Research Pipecat or similar for STT/TTS integration.

### Models

* Selected dynamically per hardware tier (not hard-coded).
* Research best-fit models for chat, reasoning, coding, and speech (prioritize open-source, permissive licenses).
* Execution via Docker Model Runner (DMR): support `docker model pull/run` and `docker model ls`.

---

## 4. Non-Functional

* **Privacy**: 100% local, no cloud calls.
* **Performance**:

  * CPU tier must remain usable (<5s latency).
  * GPU/NPU tiers should scale up to faster reasoning and speech.
* **Simplicity**: turn-key with `docker-compose up`.
* **Portability**: works cross-platform.

---

## 5. Deliverables (AI Output)

* Complete repo with:

  * Backend container implementation (Dockerfile + service code).
  * Frontend Tauri app (Rust).
  * docker-compose.yml integrating backend + frontend.
* Full, direct file outputs — no truncation, no placeholders, no instructions-only responses.
* Each generated file must be self-contained and production-usable.
* Where research is required (e.g., model selection, voice libraries), AI must **research and integrate best candidate** rather than leaving gaps.

---

## 6. References (for research, not cloning)

* **LocalAI** – RAG/LLM orchestration.
* **Pipecat** – STT/TTS voice pipeline.
* **AnythingLLM** – UI patterns.
* **LangChain** – structured prompt handling.
* **ONNX Runtime** – hardware detection + acceleration.

---

## 7. Success Criteria

* Running `docker-compose up` launches assistant with working frontend + backend.
* Voice + text chat functional.
* Models auto-selected based on hardware profile.
* User can see + override active model profile.
* End-to-end reasoning + coding responses generated locally.
