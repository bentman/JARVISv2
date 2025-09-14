# Hybrid Assistant Client

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0--alpha-orange.svg)]()

A privacy-first, offline-capable AI assistant that automatically adapts to your hardware capabilities. Provides intelligent text and voice conversations, coding assistance, research capabilities, and seamless local/cloud routing—all without compromising data privacy.

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

## 📋 Development Status

This project is currently under active development. See [project_progress.md](project_progress.md) for detailed phase breakdowns and current implementation status.

### Current Phase: Project Setup & Infrastructure

## 🚀 Getting Started

### Prerequisites
- **Operating System**: Windows 10+, macOS 12+, or Linux (Ubuntu 20.04+)
- **Hardware**: 16GB RAM minimum (32GB recommended for full feature support)
- **System**: SSD storage, current CPU with GPU/NPU acceleration if available

### Quick Start (Estimated <5 minutes)
1. Clone the repository:
   ```bash
   git clone https://github.com/bentman/JARVISv2.git
   cd JARVISv2
   ```

2. Set up environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows (or source .venv/bin/activate on POSIX)
   ```

3. Build and run:
   ```bash
   npm install
   npm run tauri dev
   ```

Detailed development environment setup and troubleshooting guides are available in [project.md](Project.md).

## 🤝 Contributing

We welcome contributions from the community! This is a complex cross-platform project that could benefit from expertise in AI/ML, Rust, desktop applications, and hardware optimization.

### Getting Started for Contributors
1. Review the [Project Overview](Project.md) and current status in [project_progress.md](project_progress.md)
2. Set up your development environment following the setup guide
3. Check out active issues and discussions for contribution ideas
4. Join our discussions to align on priority features

### Development Workflow
- Use the isolated environment setup (-noprofile terminals, .venv) to ensure consistency
- Review [project_progress.md](project_progress.md) before starting work
- Create feature branches for changes and submit pull requests
- All major changes should update project_progress.md with course corrections

### Areas for Contributions
- Hardware detection optimization for specific platforms
- Speech processing improvements and model fine-tuning
- UI/UX enhancements and accessibility features
- Performance benchmarking and optimization
- Cross-platform testing and compatibility fixes
- Documentation improvements

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

- **Issues**: [GitHub Issues](https://github.com/bentman/JARVISv2/issues)
- **Discussions**: [GitHub Discussions](https://github.com/bentman/JARVISv2/discussions)
- **Project Documentation**: [Project.md](Project.md) | [Progress.md](project_progress.md)

---

*Hybrid Assistant Client is designed to bring powerful AI capabilities to desktop devices while maintaining user privacy and control. Built with modern technologies for cross-platform compatibility and hardware-aware optimization.*
