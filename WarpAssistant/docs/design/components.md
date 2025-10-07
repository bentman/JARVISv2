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
2. **Model Router Service**: Hardware detection, model selection, and resource management with GGUF model discovery
3. **Memory Service**: Conversation storage, vector embedding, and semantic search
4. **Voice Service**: Wake word detection, speech-to-text, text-to-speech
5. **Privacy Service**: Data classification, encryption, and local processing enforcement
6. **Embedding Service**: Lightweight, local-first embedding service using feature hashing
7. **Vector Store**: FAISS-based vector store for semantic search with persistent storage
8. **Cache Service**: Redis-backed short-term caching for chat and semantic search
9. **Budget Service**: Cost tracking with configuration and reporting endpoints

### Memory Management System

- **Short-term Cache**: Redis cache for frequent queries, context maintenance, and quick access to recent snippets
- **Vector Storage**: Embeddings in searchable backend for semantic retrieval and semantic similarity
- **Long-term Persistence**: Structured storage for conversation history with tagging, filtering, and export capabilities
- **Memory Synchronization**: Framework for syncing memory across devices, with versioning and conflict resolution
- **Privacy Controls**: Data classification and selective redaction for memory snippets, ensuring only approved content is retained

### Desktop Application

- Cross-platform desktop application using web technologies
- Modern UI with rich, responsive interfaces
- Audio integration for voice input/output
- Hardware abstraction for consistent behavior across platforms

### Development Environment

The backend uses a Python virtual environment (`.venv`) for dependency isolation:

- **Virtual Environment**: Automatically created at `backend/.venv`
- **Dependency Management**: Managed through `requirements.txt`
- **Setup Command**: `make setup` creates the environment and installs dependencies
- **Development Commands**: All backend commands automatically use the virtual environment
