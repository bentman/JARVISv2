# Local AI Assistant

A privacy-focused, local-first AI assistant that runs entirely on your hardware with no cloud dependencies.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](#)

## 🚀 Overview

The Local AI Assistant is a cutting-edge AI application that provides chat, voice interaction, and reasoning capabilities while ensuring all data processing occurs locally on your device. Built with privacy as the core principle, it offers a compelling alternative to cloud-based AI assistants.

## 🌟 Key Features

### 🔒 Privacy First
- **Local Processing**: All AI inference happens on your device
- **End-to-End Encryption**: Conversation data encrypted at rest
- **No Cloud Dependencies**: Zero external data transmission
- **Data Classification**: Automatic sensitive data detection

### 🖥️ Hardware Adaptive
- **Automatic Detection**: CPU/GPU/NPU capability detection
- **Dynamic Model Selection**: Optimizes for your hardware
- **Three Performance Tiers**: 
  - Light (CPU-only): 3-7B parameter models
  - Medium (GPU/NPU): 7-13B parameter models
  - Heavy (High-end GPU): 13B+ parameter models

### 🎙️ Voice Interaction
- **Wake Word Detection**: Hands-free activation ("Hey assistant")
- **Speech-to-Text**: Accurate voice recognition with Whisper
- **Text-to-Speech**: Natural voice responses with Piper
- **Real-time Processing**: Low-latency voice interaction

### 💬 Rich Chat Interface
- **Streaming Responses**: Real-time message updates
- **Conversation History**: Persistent chat storage
- **Multi-modal Input**: Voice and text support
- **Responsive Design**: Works on all screen sizes

### 🌍 Cross-Platform
- **Windows**: Native desktop application
- **macOS**: Native desktop application
- **Linux**: Native desktop application
- **Consistent Experience**: Same features across platforms

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Desktop Application                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Voice     │  │   Chat UI   │  │  Hardware Detection │  │
│  │ Interface   │  │             │  │                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    Backend Services                         │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Model     │  │  Memory     │  │   Privacy &         │  │
│  │  Routing    │  │  Storage    │  │  Security           │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                   AI Model Execution                        │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   LLM       │  │   Voice     │  │  Hardware-          │  │
│  │  Inference  │  │  Models     │  │  Optimized          │  │
│  └─────────────┘  └─────────────┘  │  Execution          │  │
│                                    └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Technology Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Database**: [SQLite](https://www.sqlite.org/) with [SQLModel](https://sqlmodel.tiangolo.com/)
- **AI Inference**: [ONNX Runtime](https://onnxruntime.ai/), [llama.cpp](https://github.com/ggerganov/llama.cpp)
- **Containerization**: [Docker](https://www.docker.com/)

### Frontend
- **Desktop Framework**: [Tauri](https://tauri.app/) (Rust + React)
- **UI Library**: [React](https://reactjs.org/) with [Tailwind CSS](https://tailwindcss.com/)
- **State Management**: [Zustand](https://github.com/pmndrs/zustand)
- **Voice Processing**: Web Audio API

### AI Models
- **Chat Models**: Llama 3.2, Mistral 7B, Llama 3.3
- **Voice Models**: Whisper (STT), Piper (TTS)
- **Wake Word**: Porcupine
- **Model Format**: GGUF for optimal local performance

## 📁 Project Structure

```
qwenassistant/
├── backend/              # FastAPI backend services
│   ├── app/              # Main application code
│   │   ├── api/          # API endpoints
│   │   │   └── v1/       # API version 1
│   │   │       ├── endpoints/  # Individual endpoint handlers
│   │   │       │   ├── chat.py
│   │   │       │   ├── hardware.py
│   │   │       │   ├── memory.py
│   │   │       │   ├── privacy.py
│   │   │       │   └── voice.py
│   │   │       └── __init__.py
│   │   ├── core/         # Core application logic
│   │   │   └── config.py
│   │   ├── models/       # Data models
│   │   │   └── database.py
│   │   ├── services/     # Business logic services
│   │   │   ├── hardware_detector.py
│   │   │   ├── memory_service.py
│   │   │   ├── model_router.py
│   │   │   ├── privacy_service.py
│   │   │   └── voice_service.py
│   │   └── main.py       # Application entry point
│   ├── tests/            # Unit and integration tests
│   ├── Dockerfile        # Backend Docker image
│   └── requirements.txt  # Python dependencies
├── frontend/             # Tauri desktop application
│   ├── src/              # React application source
│   │   ├── components/   # React components
│   │   │   └── ChatInterface.tsx
│   │   ├── services/     # Frontend services
│   │   │   ├── index.ts
│   │   │   └── voiceService.ts
│   │   ├── App.tsx       # Main app component
│   │   ├── index.css     # Global styles
│   │   └── main.tsx      # Entry point
│   ├── src-tauri/        # Tauri backend code (Rust)
│   │   ├── src/
│   │   │   └── main.rs
│   │   ├── Cargo.toml
│   │   └── tauri.conf.json
│   ├── package.json      # Frontend dependencies
│   └── index.html        # HTML entry point
├── docker-compose.yml    # Service orchestration
├── Makefile              # Development commands
├── README.md             # Project documentation
├── LICENSE               # License information
├── INSTALLATION.md       # Installation guide
├── DEPLOYMENT.md         # Deployment guide
├── TESTING.md            # Testing and optimization plan
├── PROJECT_PLAN.md       # Comprehensive project plan
└── SUMMARY.md            # Project summary
```

## 🚀 Quick Start

### Prerequisites
- Docker Desktop
- Node.js 18+
- Rust (for Tauri)
- Python 3.11+

### Development Setup

1. **Clone the repository**:
```bash
git clone https://github.com/bentman/JARVISv2.git
cd JARVISv2/qwenassistant
```

2. **Start backend services**:
```bash
cd backend
docker-compose up -d
```

3. **Install frontend dependencies**:
```bash
cd ../frontend
npm install
```

4. **Start frontend application**:
```bash
npm run tauri dev
```

### Production Build

1. **Build backend Docker image**:
```bash
cd backend
docker build -t local-ai-assistant-backend .
```

2. **Build frontend desktop application**:
```bash
cd frontend
npm run tauri build
```

## 🎯 Core Components

### Hardware Detection Service
Automatically detects CPU, GPU, and NPU capabilities to select the optimal model profile:
- **Light Profile**: CPU-only systems with 3-7B parameter models
- **Medium Profile**: GPU/NPU systems with 7-13B parameter models
- **Heavy Profile**: High-end GPU systems with 13B+ parameter models

### Model Routing System
Intelligently routes requests to the appropriate local AI model based on:
- Hardware profile
- Task type (chat, coding, reasoning)
- Resource availability
- Performance requirements

### Voice Interaction
Complete voice interface with:
- Wake word detection using Porcupine
- Speech-to-text conversion with Whisper
- Text-to-speech synthesis with Piper
- Hands-free operation

### Privacy & Security
- End-to-end encryption for all stored data
- Local processing by default with no cloud dependencies
- Data classification for sensitive information
- Secure communication between components

### Memory Management
- Persistent conversation history with SQLite
- Encrypted storage for sensitive data
- Automatic cleanup based on retention policies
- Efficient database queries and indexing

## 📖 Documentation

- [qwenassistant/INSTALLATION.md](INSTALLATION.md) - Detailed installation instructions
- [qwenassistant/DEPLOYMENT.md](DEPLOYMENT.md) - Deployment and configuration guide
- [qwenassistant/TESTING.md](TESTING.md) - Testing strategies and optimization plan
- [qwenassistant/PROJECT_PLAN.md](PROJECT_PLAN.md) - Comprehensive project plan
- [qwenassistant/SUMMARY.md](SUMMARY.md) - Project summary and implementation details

## 🧪 Testing

The project includes comprehensive testing strategies:

- **Unit Testing**: pytest for backend, Jest for frontend
- **Integration Testing**: End-to-end API and component testing
- **Performance Testing**: Load and stress testing
- **Security Testing**: Vulnerability scanning and penetration testing

### Test Commands
```bash
# Run all tests
make test

# Run backend tests
make test-backend

# Run frontend tests
make test-frontend
```

## 🛠️ Development Commands

```bash
# Install all dependencies
make setup

# Start backend in development mode
make backend-dev

# Start frontend in development mode
make frontend-dev

# Start both backend and frontend
make dev

# Build backend Docker image
make backend-build

# Build frontend desktop application
make frontend-build

# Build both backend and frontend
make build

# Clean build artifacts
make clean

# Show help
make help
```

## 🚀 Future Enhancements

### Short-term Goals
1. Model fine-tuning with LoRA
2. Plugin architecture for extensions
3. Advanced RAG implementation
4. Multi-user support

### Long-term Vision
1. Federated learning capabilities
2. Edge computing extensions
3. Enterprise management features
4. Mobile platform support

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines for details.

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework
- [Tauri](https://tauri.app/) - Build smaller, faster, and more secure desktop applications
- [llama.cpp](https://github.com/ggerganov/llama.cpp) - Inference of LLMs in pure C/C++
- [Whisper](https://github.com/openai/whisper) - Robust speech recognition model
- [Piper](https://github.com/rhasspy/piper) - Fast neural text to speech system
- [Porcupine](https://github.com/Picovoice/porcupine) - Wake word detection engine

## 📞 Support

For support, please open an issue on GitHub or contact us at support@local-ai-assistant.com.