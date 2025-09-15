# MVP Product Requirements Document (PRD) – Local-First Version

## 1. Purpose

Deliver a **local-first AI assistant** that runs on different devices (light/medium/heavy), with a **lightweight backend in Docker** for coordination.
Goal: **Voice + chat assistant with reasoning and coding**, using local models tuned to device capacity. Keep setup simple and fast to deploy.

---

## 2. Scope (MVP)

* **Backend (Docker container)**

  * Lightweight orchestration: routes requests, maintains shared memory, and coordinates client connections.
  * Runs locally (no cloud).
  * Provides endpoints: `/chat`, `/memory`, `/search`.
  * Minimal observability (logs only).

* **Client app (runs on device)**

  * Cross-platform: Win, Mac, Linux.
  * Detects hardware (CPU / medium GPU / large GPU or NPU).
  * Chooses one of three local LLM profiles (light, medium, heavy).
  * Supports **voice loop (STT/TTS)** and **chat UI**.
  * Maintains short-term memory cache (recent snippets).

* **Three local LLM profiles**

  1. **Light-capacity (CPU)** → voice, chat, light reasoning.
  2. **Medium-capacity (GPU/NPU mid)** → voice, chat, medium reasoning, basic coding.
  3. **Heavy-capacity (GPU/NPU high)** → voice, chat, large reasoning, extended coding.

---

## 3. Out of Scope (MVP)

* No external cloud AI providers.
* No complex budget governance (local only = no cost).
* No multi-user shared memory.
* No advanced dashboards.

---

## 4. User Stories (MVP)

1. **As a user**, I can install the client, and it auto-detects my device capability (light/medium/heavy).
2. **As a user**, I can ask questions by text or voice, and get responses.
3. **As a user**, I can run reasoning tasks (light/medium/large depending on my device).
4. **As a user**, I can write or refine small code snippets locally on medium/heavy devices.
5. **As a user**, I can see route feedback in the UI (which profile/model is being used).

---

## 5. Functional Requirements

### Backend (Docker)

* Lightweight container with simple services:

  * **/chat** → route chat between client & chosen LLM.
  * **/memory** → store/retrieve snippets (short-term).
  * **/search** → local stub for search (can expand later).
* Maintains a basic log of activity.
* Deployable with one `docker run` command.

### Client App

* Detects device hardware and selects capability profile.
* Provides chat UI + voice loop (wake word → STT → response → TTS).
* Short-term cache for recent snippets.
* Displays active model/profile.

### Local LLM Profiles

* **Light**: CPU, compact model, supports basic conversation + light reasoning.
* **Medium**: GPU/NPU mid-tier, supports chat, moderate reasoning, basic coding.
* **Heavy**: GPU/NPU high-tier, supports chat, extended reasoning, and code tasks.

---

## 6. Non-Functional Requirements

* **Performance**: Light tier must run on CPU with tolerable latency (<5s per response).
* **Portability**: Client install works cross-platform; backend is Docker containerized.
* **Simplicity**: Single-command backend deploy, single client install.
* **Privacy**: All processing local; no external cloud.

---

## 7. Success Criteria

* End-to-end conversation works:
  User → Client (voice or text) → Local LLM → Response.
* Local memory working for follow-ups.
* Light/Medium/Heavy profiles each functional on appropriate hardware.
* Backend and client run with minimal setup.

---

## 8. Milestones

1. **Backend scaffold**: Docker container with `/chat`, `/memory`, `/search` (stubbed).
2. **Client scaffold**: UI + voice loop, hardware detection, capability profiles.
3. **Integrate local LLM profiles** (light/medium/heavy).
4. **Basic memory cache** on client + backend.
5. **Functional MVP release**: text + voice conversation, profile detection, and local reasoning/coding based on tier.
