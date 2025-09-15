# Hybrid Assistant Client

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0--alpha-orange.svg)]()

A privacy-first, offline-capable AI assistant that automatically adapts to your hardware capabilities. Provides intelligent text and voice conversations, coding assistance, research capabilities, and seamless local/cloud routing—all without compromising data privacy.

## 📋 Development Status

This repository contains several parallel, experimental attempts at building a local-first, hardware-aware AI assistant. Each subfolder is an independent prototype or integration effort — some have partial, runnable pieces (containers, frontends, scripts), but there is no single, finished application in this repo.

### Repository Layout & Per-Module Summary

The top-level subfolders represent discrete efforts and experiments. Short summaries follow; see each folder for its own README and run instructions.

- `Aider`: Docker-based agentic coding environment integrating Ollama models and the Aider web UI. Comes with `docker-compose.yaml`, an orchestrator FastAPI service (`Aider/orchestrator/orchestrator.py`), and a detailed `runbook.md`. Status: working prototype for local model + Aider integration (model downloads and container orchestration handled via Compose).
- `ClaudeAssist`: A full local-first assistant build with a Tauri + React frontend and a Rust backend. Contains `frontend/` and `backend/` code, `docker-compose.yaml`, and platform scripts (`start.sh`, `start.bat`). Status: advanced prototype with platform-specific build scripts and hardware-aware configuration.
- `GeminiAssist`: Lightweight Docker scaffold (backend + redis + frontend-dev). Contains a `docker-compose.yml` and a small backend. Status: scaffold / early prototype.
- `GrokAssistMMP`: Minimal Docker setup to run Ollama plus a small backend. Contains `docker-compose.yml` under `GrokAssistMMP`. Status: small integration prototype.
- `GrokAssistMVP`: Single-file application-style assistant (`run.py`) with many convenience helpers and bootstrap logic for Ollama, voice I/O, and a tiny verification script. Status: proof-of-concept; contains assistive UI and bootstrap installer logic but is not a finished product.
- `OpenAiAssist`: Local Flask + SocketIO voice assistant scaffolder. Provides `run_assistant.py` which generates a venv, a small Flask backend, and docker-compose helpers. Status: scaffold and local demo generator.
- `OpenHands`: Docker Compose integration for the OpenHands autonomous agent, with multiple Ollama services defined for planning/code/exec models. Status: integration playbook for OpenHands and local models.
- `WebApps`: Two Web Application Concepts
 - `Bolt`: [Bolt.new](https://bolt.new/) & [bolt.diy](https://github.com/stackblitz-labs/bolt.diy/tree/main) - "an AI-powered builder for websites, web apps, and mobile apps"
 - `MGX`: [MGX.dev](https://mgx.dev/) - "chat with AI to build and deploy websites, blogs, dashboards, tools"

Other files:
- `Project.md`: high-level notes and setup guidance for developers.
- `LICENSE`: project license (MIT).

Status note: these modules are experiments and partial integrations. If you are exploring this repository, pick a subfolder that matches your needs (for example, `Aider` for an agentic coding UI or `ClaudeAssist` for a Tauri-based desktop assistant) and follow the folder-specific README/runbooks.
- Hardware detection optimization for specific platforms
- Speech processing improvements and model fine-tuning
- UI/UX enhancements and accessibility features
- Performance benchmarking and optimization
- Cross-platform testing and compatibility fixes
- Documentation improvements

## Noteworthy GitHub References
- `AGENT`: [AGENT.base.md](https://gist.github.com/artpar/60a3c1edfe752450e21547898e801bb7) - Unique approach to AI agent instructions.
- `Cline`: [Cline.bot](https://cline.bot/) - MCP Orchestrator with VSCode Plugin
- `Lobe`: [LobChat](https://lobechat.com/) & [LobeHub](https://github.com/lobehub/lobe-chat)
- `NeuralAgent`: [neuralagent](https://github.com/mosdehcom/neuralagent) - Windows Desktop Assistant
- `PrivateAI-Agent`: [PrivateAI-Agent](https://github.com/privateai-com/PrivateAI-Agent) - Windows Desktop AI Assistant
- `LibreChat`: [private-ai](https://github.com/andreaswittmann/private-ai) - Desktop AI Assistant

## 🚀 Product Overview

Hybrid Assistant Client is a cross-platform desktop application that runs AI models locally on your device when possible, falling back to cloud providers seamlessly. Designed for developers, researchers, and power users who need privacy, speed, and offline access to advanced AI capabilities.

### Key Capabilities
- **Intelligent Conversations**: Multi-modal text and voice interactions with context-aware responses
- **Hardware-Aware Optimization**: Automatically selects optimal models based on CPU, GPU, and NPU availability
- **Multi-Platform Voice**: Natural language TTS/STT using Kokoro and faster-whisper across Windows, macOS, and Linux
- **Coding Assistance**: Specialized modes for code generation, debugging, refactoring, and analysis
- **Research & Analysis**: Aggregate search across local memory, web sources, and AI providers
- **Privacy-First Design**: All data stays local by default; optional cloud features with user control
- **Zero-Config Setup**: One-click installation with automatic model downloading and hardware detection
- **Sub-2s Response Times**: Optimized inference pipeline for real-time conversations

## 🏗️ Technical Architecture

### Core Components
- **Desktop Framework**: Tauri 2.0 (Rust backend + React/TypeScript UI for cross-platform performance and security)
- **AI Inference Stack**:
  - **Text Models**: llama.cpp for GGUF models (heavy/light tiers) + ONNX Runtime for NPU/GPU acceleration
  - **Speech Processing**: Kokoro TTS (ONNX) + faster-whisper STT for cross-platform voice capabilities
- **Data Layer**:
  - SQLite for conversation history and metadata
  - RocksDB/Qdrant-lite for vector embeddings and semantic search
  - Redis for short-term context caching
- **Hardware Abstraction**: Unified API for CPU/GPU/NPU detection across platforms (DirectML, CoreML, QNN)

### Conversation Modes
- **Assistant**: General conversational AI for queries, brainstorming, and Productivity tasks
- **Coding**: Specialized for development workflows including code generation, debugging, and technical analysis
- **Creative**: Support for writing, ideation, content creation and creative exploration
- **Analyzer**: Document analysis, research synthesis, and structured data processing

### Routing & Privacy
- **Intelligent Fallback**: Local inference prioritized, with configurable escalation to cloud providers (OpenAI, Anthropic, GoogleAI, xAI, Hugging Face, etc.)
- **Budget Management**: Token limits and usage tracking for cloud providers
- **End-to-End Encryption**: Optional encryption for exported conversations and model data
- **Telemetry Opt-In**: Anonymous usage statistics only with explicit consent

### Current Phase: Collection of Prototypes and Experiments

## 🚀 Getting Started

### Prerequisites
- **Operating System**: Windows 10+, macOS 12+, or Linux (Ubuntu 20.04+)
- **Hardware**: 16GB RAM minimum (32GB recommended for full feature support)
- **System**: SSD storage, current CPU with GPU/NPU acceleration if available

## 🤝 Contributing

We welcome contributions from the community! This is a complex cross-platform project that could benefit from expertise in AI/ML, Rust, desktop applications, and hardware optimization.

### Getting Started for Contributors
1. Review the `Project.md` overview and the README files inside each subfolder
2. Set up your development environment following the setup guide
3. Check out active issues and discussions for contribution ideas
4. Join our discussions to align on priority features

### Development Workflow
- Use the isolated environment setup (-noprofile terminals, .venv) to ensure consistency
- Review [project_progress.md](project_progress.md) before starting work
- Create feature branches for changes and submit pull requests
- All major changes should update project_progress.md with course corrections

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

- **Issues**: [GitHub Issues](https://github.com/bentman/JARVISv2/issues)
- **Discussions**: [GitHub Discussions](https://github.com/bentman/JARVISv2/discussions)
- **Project Documentation**: [Project.md](Project.md) | [Progress.md](project_progress.md)

---

*Hybrid Assistant Client is designed to bring powerful AI capabilities to desktop devices while maintaining user privacy and control. Built with modern technologies for cross-platform compatibility and hardware-aware optimization.*
