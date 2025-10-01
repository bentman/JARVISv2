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

### 💬 Rich Chat Interface
- **Streaming Responses**: Real-time message updates
- **Conversation History**: Persistent chat storage
- **Multi-modal Input**: Voice and text support

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python), SQLite, ONNX Runtime
- **Frontend**: Tauri (Rust + React), Tailwind CSS
- **AI Models**: Llama 3.2, Mistral 7B, Whisper, Piper
- **Containerization**: Docker

## 📖 Documentation

- [Project_Components.md](Project_Components.md) - System architecture and components
- [Project_Detail.md](Project_Detail.md) - System design and vision
- [WARP.md](WARP.md) - AI coding assistant instructions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🛠️ Development Setup

The project uses a Python virtual environment in the backend to isolate dependencies and avoid conflicts with your system-wide Python installation. This ensures consistency across different development environments.

To set up the development environment, run:

```bash
make setup
```

This will create a virtual environment in the `backend/.venv` directory and install all required dependencies.

The system automatically detects your hardware capabilities and selects the appropriate model profile:
- **Light Profile**: For systems with limited resources
- **Medium Profile**: For mid-range systems with moderate GPU/NPU capabilities  
- **Heavy Profile**: For high-performance devices with sufficient memory
- **NPU Optimized**: For neural processing units with specialized optimizations

## ⚠️ Important Note on Development Process

During a previous development session, a mistake was made where Python dependencies were installed globally instead of using the project's virtual environment. This violated the project's requirement to use virtual environments for dependency isolation. The mistake has been corrected by removing the globally installed packages.

**Important**: Always ensure you are working within the project's virtual environment to maintain proper dependency isolation.

## 📞 Support

For support, please open an issue on GitHub.
