# Local AI Assistant - System Components

## Architecture Overview

The Local AI Assistant follows a modular architecture with distinct backend services and a cross-platform desktop frontend:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Desktop Application                          │
│  ┌─────────────────┐   ┌─────────────────┐   ┌────────────────────┐ │
│  │ Voice Interface │   │ Chat UI         │   │ Hardware Detection │ │
│  └─────────────────┘   └─────────────────┘   └────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────────┐
│                        Backend Services                             │
│  ┌─────────────────┐   ┌─────────────────┐   ┌────────────────────┐ │
│  │ Model Routing   │   │ Memory Storage  │   │ Privacy & Security │ │
│  └─────────────────┘   └─────────────────┘   └────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────────┐
│                        AI Model Execution                           │
│  ┌─────────────────┐   ┌─────────────────┐   ┌────────────────────┐ │
│  │ LLM Inference   │   │ Voice Models    │   │ Hardware-Optimized │ │
│  └─────────────────┘   └─────────────────┘   └────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

## Core Components

### Backend Services

1. **Core Assistant Service**: REST API for frontend communication, request routing, and orchestration
2. **Model Router Service**: Hardware detection, model selection, and resource management
3. **Memory Service**: Conversation storage, vector embedding, and semantic search
4. **Voice Service**: Wake word detection, speech-to-text, text-to-speech
5. **Privacy Service**: Data classification, encryption, and local processing enforcement

### Frontend Components

- **Desktop Application**: Cross-platform desktop application using web technologies
- **Chat Interface**: Modern UI with rich, responsive interfaces
- **Voice Interface**: Audio integration for voice input/output

### Development Environment

The backend uses a Python virtual environment (`.venv`) for dependency isolation:

- **Virtual Environment**: Automatically created at `backend/.venv`
- **Dependency Management**: Managed through `requirements.txt`
- **Setup Command**: `make setup` creates the environment and installs dependencies
- **Development Commands**: All backend commands automatically use the virtual environment
