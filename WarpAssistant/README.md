# Local AI Assistant

A privacy-focused, local-first AI assistant that runs entirely on your hardware with no cloud dependencies.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](#)

## 🚀 Overview

The Local AI Assistant is a cutting-edge AI application that provides chat, reasoning, and coding tasks with voice interaction while ensuring all data processing occurs locally on your device. Built with privacy as the core principle, it offers a compelling alternative to cloud-based AI assistants. The assistant adapts to hardware configurations (CPU, GPU, NPU) for optimal performance across Windows, macOS, and Linux.

This project has made significant progress with core functionality implemented. The documentation provides a roadmap of planned features and capabilities.

## 🌟 Key Features

### 🔒 Privacy First
- **Local Processing**: All AI inference happens on your device by default
- **End-to-End Encryption**: Conversation data encrypted at rest
- **No Cloud Dependencies**: Zero external data transmission by default
- **Data Classification**: Automatic sensitive data detection and handling

### 🖥️ Hardware Adaptive
- **Automatic Detection**: CPU/GPU/NPU capability detection
- **Dynamic Model Selection**: Optimizes for your hardware configuration
- **Performance Profiles**: 
  - **Light**: For lower-end hardware
  - **Medium**: For mid-range systems
  - **Heavy**: For high-performance devices
  - **NPU Optimized**: For neural processing units
  - **API Integration**: Optional cloud fallback for unsupported tasks

### 🎙️ Voice Interaction
- **Wake Word Detection**: Hands-free activation with local processing
- **Speech-to-Text**: Accurate voice recognition
- **Text-to-Speech**: Natural voice responses
- **Real-time Processing**: Low-latency voice interaction

### ⚙️ System Services
- **Redis Caching**: Short-term caching for chat responses and semantic search results
- **Budget Monitoring**: Endpoints for usage tracking and budget configuration
- **Model Discovery**: Endpoints to list discovered GGUF models and current selection

### 💬 Rich Chat Interface
- **Streaming Responses**: Real-time message updates
- **Conversation History**: Persistent chat storage
- **Multi-modal Input**: Voice and text support

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python), SQLite, ONNX Runtime
- **Cache**: Redis (short-term result caching)
- **Vector Store**: FAISS (semantic search index)
- **Frontend**: Tauri (Rust + React), Tailwind CSS
- **AI Models**: Llama 3.2, Mistral 7B, Whisper, Piper
- **Containerization**: Docker

## 📖 Documentation

- User Guide: `docs/user/index.md`
- Developer Setup: `docs/dev/setup.md`
- API Reference: `docs/dev/api.md`
- AI Assistant Rules: `warp.md`
- Requirements (read-only): `Project.md`
- Architecture: `docs/design/system-design.md`, `docs/design/components.md`
- Packaging & Ops: `docs/dev/packaging.md`, `docs/dev/operations.md`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🛠️ Development Setup

The project uses a Python virtual environment in the backend to isolate dependencies and avoid conflicts with your system-wide Python installation. This ensures consistency across different development environments.

To set up the development environment, run:

```bash
make setup
```

This will create a virtual environment in the `backend/.venv` directory and install all required dependencies.

Backend + Redis via Docker Compose:
- Build and start services:
  - `docker compose build backend`
  - `docker compose up -d`
- This brings up the backend on port 8000 and a Redis instance on 6379. The backend is configured with `REDIS_URL=redis://redis:6379/0`.

The system automatically detects your hardware capabilities and selects the appropriate model profile:
- **Light Profile**: For systems with limited resources
- **Medium Profile**: For mid-range systems with moderate GPU/NPU capabilities  
- **Heavy Profile**: For high-performance devices with sufficient memory
- **NPU Optimized**: For neural processing units with specialized optimizations

## 🖥️ Desktop (Tauri)

- Dev: run your Vite dev server (http://localhost:5173), then start Tauri from `frontend` to load the app window.
- Build: `npm run build` in `frontend`, then package with Tauri to generate desktop installers.

## ⚠️ Important Note on Development Process

During a previous development session, a mistake was made where Python dependencies were installed globally instead of using the project's virtual environment. This violated the project's requirement to use virtual environments for dependency isolation. The mistake has been corrected by removing the globally installed packages.

**Important**: Always ensure you are working within the project's virtual environment to maintain proper dependency isolation.

## 📡 API Quick Reference

- Models
  - GET `/api/v1/models/all` → names, profiles map, and model paths
  - GET `/api/v1/models/select?profile=medium&task_type=chat` → selected model + path
- Budget
  - GET `/api/v1/budget/status` → daily/monthly cost and limits
  - POST `/api/v1/budget/config` → set daily/monthly limits, enforce flag, and cost per token
- Search
  - POST `/api/v1/search/semantic` → FAISS-backed semantic search results

## 📞 Support

For support, please open an issue on GitHub.
