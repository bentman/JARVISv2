# AI Assistant Projects Collection

A collection of experimental AI assistant implementations exploring different architectures, technologies, and approaches to local-first AI computing.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](#)

## 🚀 Overview

This repository contains multiple experimental AI assistant projects, each exploring different approaches to privacy-focused, local-first AI computing. These projects represent various stages of development and different architectural philosophies for building AI assistants that prioritize user privacy and local processing.

## 📁 Project Structure

### Desktop Applications

#### **Aider/** - Agentic Coding Environment
- **Status**: Functional Docker setup
- **Technology**: Ollama + Aider web interface
- **Focus**: AI-powered coding assistance with local LLMs
- **Key Features**: Multiple model support, web interface, Docker orchestration

#### **ClaudeAssist/** - Rust-based Local Assistant
- **Status**: Complete architecture, partial implementation
- **Technology**: Rust backend + Tauri frontend
- **Focus**: High-performance local AI with hardware detection
- **Key Features**: Hardware profiling, model routing, voice interface

#### **QwenAssistant/** - FastAPI Local Assistant
- **Status**: Complete project structure
- **Technology**: FastAPI (Python) + Tauri (React)
- **Focus**: Privacy-first AI with comprehensive feature set
- **Key Features**: Hardware detection, voice interaction, memory management

### Web Applications

#### **WebApp/BoltAssist/** - Local-First Web Demo
- **Status**: Working MVP demonstration
- **Technology**: React + TypeScript + Express.js backend
- **Focus**: Browser-based local AI with hardware detection
- **Key Features**: Real hardware detection, voice interface, backend API

#### **WebApp/MgxAssist/** - Hybrid Architecture Prototype
- **Status**: Interactive proof-of-concept
- **Technology**: React + shadcn/ui components
- **Focus**: Hybrid local-cloud routing with budget governance
- **Key Features**: Routing visualization, budget tracking, privacy controls

### Experimental Projects

#### **GeminiAssist/** - Docker Model Runner Integration
- **Status**: Early prototype
- **Technology**: FastAPI + Docker Model Runner
- **Focus**: Model management and orchestration

#### **GrokAssistMMP/** - Minimal Marketable Product
- **Status**: Basic implementation
- **Technology**: Tauri + Rust + Python backend
- **Focus**: Simplified local AI assistant

#### **GrokAssistMVP/** - Minimum Viable Product
- **Status**: Functional prototype
- **Technology**: Python + Tkinter + Ollama
- **Focus**: Simple local AI with voice capabilities

#### **OpenAiAssist/** - Flask-based Assistant
- **Status**: Basic web interface
- **Technology**: Flask + WebSocket + HTML/JS
- **Focus**: Simple voice-enabled web assistant

#### **OpenHands/** - Multi-Model Setup
- **Status**: Docker configuration
- **Technology**: Multiple Ollama instances + OpenHands
- **Focus**: Autonomous development agent integration

## 🎯 Common Themes

All projects in this collection explore:

- **Privacy-First Design**: Local processing by default
- **Hardware Adaptability**: Automatic optimization for available resources
- **Voice Interaction**: Speech-to-text and text-to-speech capabilities
- **Cross-Platform Support**: Desktop and web implementations
- **Model Management**: Dynamic selection based on hardware capabilities

## 🛠️ Technology Stack Comparison

| Project | Backend | Frontend | AI Runtime | Status |
|---------|---------|----------|------------|--------|
| Aider | Docker/Ollama | Web Interface | Ollama | ✅ Functional |
| ClaudeAssist | Rust | Tauri + React | ONNX/llama.cpp | 🔧 In Progress |
| QwenAssistant | FastAPI | Tauri + React | ONNX/llama.cpp | 📋 Planned |
| BoltAssist | Express.js | React + TypeScript | Browser APIs | ✅ Working Demo |
| MgxAssist | Mock Backend | React + shadcn/ui | Simulated | ✅ Interactive POC |
| GrokAssistMVP | Python | Tkinter | Ollama | ⚡ Basic MVP |

## 🚀 Quick Start

### Most Complete Projects

#### **Aider (Functional)**
```bash
cd Aider
docker-compose up -d
# Access at http://localhost:8501
```

#### **BoltAssist (Working Demo)**
```bash
cd WebApp/BoltAssist
npm install
npm run dev
# Backend: http://localhost:3001
# Frontend: http://localhost:5173
```

#### **MgxAssist (Interactive Prototype)**
```bash
cd WebApp/MgxAssist
pnpm install
pnpm run dev
# Access at http://localhost:5173
```

### Development Projects

Each project contains its own README.md with specific setup instructions. Most require:
- Docker Desktop (for containerized projects)
- Node.js 18+ (for web frontends)
- Rust (for Tauri applications)
- Python 3.11+ (for backend services)

## 🔬 Research Areas

These projects collectively explore:

### **Hardware Detection & Optimization**
- CPU/GPU/NPU capability detection
- Dynamic model selection based on hardware
- Performance profiling and optimization

### **Privacy & Security**
- Local-first processing architectures
- Data classification and protection
- Selective cloud escalation policies

### **Voice Interaction**
- Wake word detection
- Real-time speech processing
- Cross-platform audio handling

### **Model Management**
- Dynamic model loading and unloading
- Quantization and optimization
- Multi-model orchestration

### **User Experience**
- Cross-platform desktop applications
- Voice-first interaction design
- Real-time feedback and status

## 📊 Project Maturity

- **Production Ready**: None (all experimental)
- **Functional Demos**: Aider, BoltAssist, MgxAssist
- **Complete Architecture**: ClaudeAssist, QwenAssistant
- **Early Prototypes**: GeminiAssist, GrokAssist variants, OpenAiAssist

## 🤝 Contributing

Each project represents different experimental approaches. To contribute:

1. Choose a project that aligns with your interests
2. Review the project-specific README and documentation
3. Set up the development environment
4. Make improvements or complete missing features
5. Submit pull requests with clear descriptions

## 📄 License

All projects in this collection are licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Future Direction

This collection serves as a research repository for:
- Evaluating different architectural approaches
- Testing various technology stacks
- Exploring privacy-preserving AI techniques
- Developing cross-platform AI applications

The most promising approaches from these experiments may be consolidated into a unified, production-ready AI assistant in the future.

## 📞 Support

For questions about specific projects, refer to their individual documentation. For general repository questions, please open an issue.

---

**Note**: These are experimental projects exploring different approaches to local-first AI assistants. They are not intended for production use without significant additional development and testing.