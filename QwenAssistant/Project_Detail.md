# Local AI Assistant - System Design & Implementation

## Project Overview

The Local AI Assistant is a privacy-focused, local-first AI assistant that runs entirely on user hardware. It provides chat, voice interaction, and reasoning capabilities while ensuring all data processing occurs locally by default. The system is designed with privacy, hardware adaptability, and cross-platform compatibility as core principles.

## Key Features

### Privacy First
- **Local Processing**: All AI inference happens on your device by default
- **End-to-End Encryption**: Conversation data encrypted at rest
- **No Cloud Dependencies**: Zero external data transmission by default
- **Data Classification**: Automatic sensitive data detection and handling

### Hardware Adaptive
- **Automatic Detection**: CPU/GPU/NPU capability detection
- **Dynamic Model Selection**: Optimizes for your hardware configuration
- **Performance Profiles**:
  - **Light**: Basic tasks for lower-end hardware
  - **Medium**: Enhanced capabilities for mid-range systems
  - **Heavy**: Full feature set for high-performance devices
  - **NPU Optimized**: Accelerated performance on neural processing hardware
  - **API Integration**: Optional cloud fallback for unsupported tasks

The system automatically selects the appropriate performance profile based on your hardware:
- **Light Profile**: For systems with limited resources (e.g., 3-7B parameter models)
- **Medium Profile**: For mid-range systems with moderate GPU/NPU capabilities (e.g., 7-13B parameter models)
- **Heavy Profile**: For high-performance devices with sufficient memory to run large models (e.g., 13B+ parameter models)
- **NPU Optimized**: For neural processing units with specialized optimizations

### Voice Interaction
- **Wake Word Detection**: Hands-free activation with local processing
- **Speech-to-Text**: Accurate voice recognition
- **Text-to-Speech**: Natural voice responses
- **Real-time Processing**: Low-latency voice interaction

### Rich Chat Interface
- **Streaming Responses**: Real-time message updates
- **Conversation History**: Persistent chat storage
- **Multi-modal Input**: Voice and text support
- **Responsive Design**: Works on all screen sizes

## Technology Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Database**: [SQLite](https://www.sqlite.org/) with [SQLModel](https://sqlmodel.tiangolo.com/)
- **AI Inference**: [ONNX Runtime](https://onnxruntime.ai/), [llama.cpp](https://github.com/ggerganov/llama.cpp)
- **Containerization**: [Docker](https://www.docker.com/)
- **Dependency Management**: Python virtual environment (`.venv`) for isolation

### Frontend
- **Desktop Framework**: [Tauri](https://tauri.app/) (Rust + React)
- **UI Library**: [React](https://reactjs.org/) with [Tailwind CSS](https://tailwindcss.com/)
- **State Management**: [Zustand](https://github.com/pmndrs/zustand)
- **Voice Processing**: Web Audio API

### AI Models
- **Chat Models**: Llama 3.2, Mistral 7B, Llama 3.3
- **Voice Models**: Whisper (STT), Piper (TS)
- **Wake Word**: Local implementation for privacy-focused activation
- **Model Format**: GGUF for optimal local performance

## Development Workflow

The project uses a Python virtual environment in the backend to ensure dependency isolation and consistency across different development environments.

To set up the development environment:

```bash
make setup
```

This creates a virtual environment in `backend/.venv` and installs all required dependencies.

For development:

```bash
make dev  # Runs both backend and frontend in development mode
```

## Design Principles

### Privacy & Security
- Local-first processing with no default external data transmission
- Data encryption for conversation storage
- Classification system for sensitive information handling
- User controls for data retention and sharing
- End-to-end encryption for data protection
- Model integrity verification
- Secure inter-component communication
- Isolation of AI models and data processing

### Performance Requirements
- Real-time conversation with sub-3 second responses
- Voice processing with low latency and minimal delay
- Interface responsiveness regardless of model size
- Efficient resource utilization across hardware tiers
- High system uptime and availability
- Graceful degradation under resource constraints
- Automatic error recovery and user feedback
- Consistent performance across supported platforms

## Current Implementation Status

The project has made significant progress with working implementations of:
- Backend services (hardware detection, chat API, voice processing, privacy controls)
- Frontend chat interface with voice capabilities
- Model routing system based on hardware profiles with GGUF model discovery
- Memory and privacy services
- Database implementation with SQLModel and SQLite
- Semantic search functionality using vector embeddings and FAISS (with Redis-backed caching)
- Actual wake word detection using openwakeword library
- Vector store for persistent semantic search
- Intelligent routing system prioritizing local-first processing
- Redis cache service for chat and semantic search
- Budget monitoring service and endpoints
- Model discovery and selection endpoints
- Minimal Tauri configuration for desktop app launch

### Remaining Components
- Enhanced NPU detection with vendor SDKs (optional OpenVINO support)
- Cross-platform desktop app distribution and installers
- Comprehensive testing suite
- Memory synchronization across devices
- Unified search aggregation with external providers
