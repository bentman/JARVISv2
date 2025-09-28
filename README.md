# JARVIS v2 - Local AI Assistant Experiments

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](#)

This repository serves as a collection of experimental projects exploring privacy-focused, local-first AI assistants. Each sub-project represents an incomplete implementation of an AI assistant, utilizing various AI providers and technologies to enable local processing, hardware adaptation, and multimodal interfaces (voice and chat). The intent is to leverage these experiments as references for iterative improvement and completion toward a unified, working AI assistant model.

## Key Features

- **Local-First Processing**: All AI operations run locally on hardware to minimize external dependencies.
- **Hardware Adaptive Model Selection**: Automatic circuit detection profiling capabilities for routing to optimized local/cloud models per device tier (light/medium/heavy/NPU).
- **Intelligent Routing**: Local-first with policy-based escalation to cloud-lite (small models for gaps in reasoning/coding) or cloud-heavy (large models for complex analysis), balancing performance, privacy, and budget.
- **Unified Search Aggregation**: Combines local conversation memory, vector embeddings, and web/cloud AI sources with ranked results, citations, and summaries.
- **Voice-Enabled**: Support for voice input, output, wake word interactions, and continuous conversation modes.
- **Privacy-Focused**: Emphasis on data security, encryption, and classification with selective escalation (redaction for sensitive data).
- **Multimodal Interaction**: Combines text and voice for seamless, natural user experiences with real-time synchronization.
- **Cross-Platform**: Designed for consistent functionality across Windows, macOS, and Linux with native performance.

## Core Components and Architecture

Common elements across experiments include:

- **Local Inference and Privacy**: Emphasis on running AI models locally to avoid cloud dependencies, with end-to-end encryption where implemented.
- **Hardware Adaptation**: Detection and optimization for CPU/GPU/NPU capabilities, selecting appropriate model sizes and performance tiers (e.g., light/medium/heavy profiles for varying compute power).
- **Voice Interfaces**: Integration of speech-to-text and text-to-speech for hands-free interaction, including potential wake word detection.
- **Chat Interfaces**: Multimodal input support combining text and voice, with persistent conversation history and real-time streaming.
- **Backend Frameworks**: Primarily Python-based API services, with alternative implementations in other languages.
- **Frontend Technologies**: Web-based or desktop applications for user interaction.
- **Containerization**: Use of containerization for deployment consistency and isolation.
- **Security and Memory**: Data classification, encryption, and storage management to ensure privacy and efficiency.

The overarching architecture centers on a modular design: AI model routing for hardware-optimized execution, memory services for context retention, and privacy layers for secure data handling.

## Sub-Projects

Each sub-project explores a different AI provider or approach, with varying levels of completeness. Use these as references for refining and completing the concepts.

## Goal and Usage

These projects are incomplete experiments representing iterative attempts at building personal AI assistants. Reference them to identify patterns, technologies, and architectures for improvement. Contribute by enhancing existing implementations or developing unified solutions combining the best elements (e.g., hardware abstraction, voice handling, and provider flexibility).

### **QwenAssistant (High Completeness)**:
Complete local AI assistant for chat and voice.

  - tech:
    - python fastapi backend
    - react tauri frontend
    - hardware model routing
    - voice interfaces
    - memory storage

  - docs:
    - core: [QwenAssistant/README.md](QwenAssistant/README.md)
    - project: [QwenAssistant/QWEN.md](QwenAssistant/QWEN.md)
    - components: [QwenAssistant/Project_Components.md](QwenAssistant/Project_Components.md)
    - detail: [QwenAssistant/Project_Detail.md](QwenAssistant/Project_Detail.md)

### **ClaudeAssist (Medium Completeness)**:
Local-first AI assistant for chat, voice, reasoning, coding.

  - tech:
    - rust backend with ollama
    - python react tauri frontend
    - docker orchestration
    - sqlite memory
    - voice models

  - docs:
    - core: [ClaudeAssist/readme.md](ClaudeAssist/readme.md)
    - project: [ClaudeAssist/claude.md](ClaudeAssist/claude.md)

### **GrokAssistMMP (Medium Completeness)**:
Multi-modal AI assistant with chat, voice, reasoning, coding as local MMP.

  - tech:
    - python backend orchestration
    - rust tauri frontend
    - docker routing
    - voice loop
    - memory services

  - docs:
    - project: [GrokAssistMMP/grok.md](GrokAssistMMP/grok.md)

### **GeminiAssist (Medium Completeness)**:
AI chat/reasoning with web interface.

  - tech:
    - python backend api
    - web frontend
    - docker setup

  - docs:
    - setup: [GeminiAssist/setup.sh](GeminiAssist/setup.sh)

### **GrokAssistMVP (Low Completeness)**:
Minimal Grok-based AI implementation.

  - tech:
    - python script
    - memory persistence

  - docs:
    - project: [GrokAssistMVP/grok.md](GrokAssistMVP/grok.md)

### **OpenAiAssist (Low Completeness)**:
OpenAI API integration assistant.

  - tech:
    - python fastapi server
    - templates

  - docs:
    - setup: [OpenAiAssist/run_assistant.py](OpenAiAssist/run_assistant.py)

### **OpenHands (Low Completeness)**:
Experimental open-source coding assistant.

  - tech:
    - docker structure

  - docs:
    - setup: [OpenHands/docker-compose.yaml](OpenHands/docker-compose.yaml)

### **Aider (Low Completeness)**:
AI coding assistant variations.

  - tech:
    - python rust orchestrator
    - runbook

  - docs:
    - reference: [Aider/runbook.md](Aider/runbook.md)

### **WebApp/BoltAssist (Medium Completeness)**:
Web-assisted AI for coding/chat.

  - tech:
    - nodejs backend
    - react vite frontend
    - docker
    - bolt integration

  - docs:
    - core: [WebApp/BoltAssist/README.md](WebApp/BoltAssist/README.md)
    - project: [WebApp/BoltAssist/bolt.md](WebApp/BoltAssist/bolt.md)

### **WebApp/MgxAssist (Low-Medium Completeness)**:
Alternative web AI assistant.

  - tech:
    - react vite setup
    - minimal backend

  - docs:
    - core: [WebApp/MgxAssist/README.md](WebApp/MgxAssist/README.md)
    - project: [WebApp/MgxAssist/mgx.md](WebApp/MgxAssist/mgx.md)

## License

This repository is licensed under the MIT License. See [LICENSE](LICENSE) for details.
