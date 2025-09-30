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

### Development Environment

The backend uses a Python virtual environment (`.venv`) for dependency isolation:

- **Virtual Environment**: Automatically created at `backend/.venv`
- **Dependency Management**: Managed through `requirements.txt`
- **Setup Command**: `make setup` creates the environment and installs dependencies
- **Development Commands**: All backend commands automatically use the virtual environment

### Desktop Application

- Cross-platform desktop application using web technologies
- Modern UI with rich, responsive interfaces
- Audio integration for voice input/output
- Hardware abstraction for consistent behavior across platforms

### Memory Management System

- **Short-term Cache**: Redis cache for frequent queries and context maintenance
- **Vector Storage**: Embeddings in searchable backend for semantic retrieval
- **Long-term Persistence**: Structured storage for conversation history
- **Memory Synchronization**: Framework for syncing memory across devices
- **Privacy Controls**: Data classification and selective redaction

### Intelligent Routing System

Policy-driven logic prioritizing local-first processing with tiered escalation:
- Local (priority) for standard tasks
- Cloud-lite (small models) for capability gaps in reasoning/coding
- Cloud-heavy (large models) for complex analysis

### Unified Search Aggregation

System for integrated queries across multiple sources:
- Local memory (conversation history)
- Vector embeddings (semantic retrieval)
- Search providers (web APIs like Bing/Google/Tavily)
- Cloud AI providers

Results are aggregated, ranked by relevance, with citations, summaries, and configurable source preferences.

## Current Implementation Status

The project has made significant progress with working implementations of:
- Backend services (hardware detection, chat API, voice processing, privacy controls)
- Frontend chat interface with voice capabilities
- Model routing system based on hardware profiles
- Memory and privacy services
- Basic database integration with SQLite

### Remaining Components
- Semantic search functionality (vector embeddings)
- Redis integration for caching
- Complete NPU detection
- Wake word detection implementation
- Cross-platform desktop app distribution
- Comprehensive testing suite
```
