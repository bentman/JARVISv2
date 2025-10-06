# Local AI Assistant Code Instructions

## Style & Conventions
- **Backend**: Use Python with PEP 8 style guidelines
- **Frontend**: Use TypeScript with React functional components and hooks
- **Naming**: Use snake_case for Python variables/functions, camelCase for TypeScript
- **API Routes**: Follow RESTful conventions with versioning (e.g., `/api/v1/chat`)
- **Type Hints**: Always include type hints in Python functions and TypeScript interfaces
- **Async/Await**: Use async/await for I/O operations in Python
- **Pydantic Models**: Use Pydantic for request/response validation in FastAPI

## Project Structure
- **Backend Services**: Located in `backend/app/services/` (hardware_detector.py, model_router.py, etc.)
- **API Endpoints**: Located in `backend/app/api/v1/endpoints/` (chat.py, hardware.py, etc.)
- **Frontend Components**: Located in `frontend/src/components/`
- **Frontend Services**: Located in `frontend/src/services/`
- **Configuration**: Backend settings in `backend/app/core/config.py`
- **Database Models**: Located in `backend/app/models/`
- **Tauri Backend**: Located in `frontend/src-tauri/src/main.rs`

## Common Tasks
- **Adding New API Endpoint**: Create new file in `backend/app/api/v1/endpoints/`, add to router in `backend/app/api/v1/__init__.py`
- **Adding New Service**: Create new file in `backend/app/services/`, implement as class with focused responsibility
- **Adding Frontend Component**: Create new file in `frontend/src/components/` using React functional component pattern
- **Hardware Profile Implementation**: Update model configurations in `backend/app/services/model_router.py`
- **Environment Setup**: Use `make setup` to initialize virtual environment and dependencies
- **Development Mode**: Use `make dev` to run both backend and frontend in development mode

## Other Documentation Files
- **Project.md**: Requirements document - do not modify without specific confirmation!
- **README.md**: Main project overview for humans
- **Project_Components.md**: System architecture and components for humans
- **Project_Detail.md**: System design and vision for humans
- **WARP.md**: This file - for AI coding assistant instructions

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
- Redis cache service for short-term caching (chat and semantic search)
- Budget monitoring service and API endpoints (status/config)
- Model discovery and selection endpoints (/api/v1/models)
- Minimal Tauri configuration (src-tauri) for desktop app launch during development

## Next Steps & Implementation Requirements

### Immediate Priorities
1. **Redis Integration**: For short-term caching as mentioned in the architecture
2. **NPU Detection**: Complete hardware detector with NPU-specific APIs
3. **Budget Monitoring**: Cost analysis and budget governance features
4. **Cross-platform Desktop App**: Complete Tauri configuration for desktop distribution
5. **Testing**: Create comprehensive unit and integration tests

### Critical Missing Elements
1. **Memory Synchronization**: Framework for syncing memory across devices, with versioning and conflict resolution
2. **Unified Search Aggregation**: Integration with search providers (web APIs like Bing/Google/Tavily) and cloud AI providers
3. **Advanced Privacy Controls**: Enhanced data classification and selective redaction for memory snippets
4. **Enhanced Hardware Detection**: Specialized processor detection including NPUs
5. **Model Fine-tuning**: LoRA implementation for task-specific customization

### Implementation Guidelines
- **Reference Existing Implementations**: When implementing features, research similar open-source projects on GitHub for proven approaches
- **Model Integration**: Look for examples of GGUF model integration with ONNX Runtime or llama.cpp
- **Voice Processing**: Research Whisper for STT and Piper TTS implementations
- **Wake Word Detection**: Leverage the existing openwakeword integration in voice_service.py
- **Vector Embeddings**: Use the existing FAISS-based vector store implementation in vector_store.py

### Requirements Reference
- All implementation should align with requirements in `Project.md`
- Do not implement features without understanding the complete requirements first
- Focus on local-first processing as defined in the requirements
- Ensure all data processing occurs locally by default with no cloud dependencies
- Maintain proper dependency isolation using the virtual environment at `backend/.venv`

prepare a short “follow-up issues” list (no code changes) to track the two flagged items

Here’s a concise follow-up issues list to track the two flagged items (no code changes):

1) ModelRouter: duplicate get_model_path definitions
- Location: backend/app/services/model_router.py
- Problem: There are two get_model_path methods; the later definition overrides the earlier one that consults self.model_paths. This can cause the code to ignore discovered absolute paths for GGUF files and fallback to MODEL_PATH join logic.
- Impact: Model file resolution may be incorrect when models are discovered recursively under subfolders; potential FileNotFoundError or use of wrong file.
- Proposed resolution:
  - Deduplicate into a single get_model_path that:
    - Returns self.model_paths[model_name] if present.
    - Falls back to os.path.join(settings.MODEL_PATH, f"{model_name}.gguf") otherwise.
  - Add a unit test to ensure when model_paths contains an entry, that path is used exclusively.
- Acceptance criteria:
  - No duplicate method definitions.
  - When a model is discovered via recursive scan, its absolute path is used in inference.
  - Tests cover both discovered-path and fallback-path scenarios.

2) VoiceService: import-time initialization and external binary/toolchain dependency
- Location: backend/app/services/voice_service.py
- Problem: VoiceService initializes at import time, verifying Whisper/Piper executables immediately. If binaries aren’t installed (or toolchains like cargo aren’t present for auto-build), app startup can fail.
- Impact: Backend may crash on startup in environments where whisper/piper aren’t preinstalled, especially inside Docker where Rust/Cargo isn’t included. This reduces robustness and blocks unrelated endpoints.
- Proposed resolution:
  - Convert to lazy initialization (initialize Whisper/Piper only on first use of STT/TTS/wake-word endpoints).
  - Soft-fail behavior: if not available, return a structured error (e.g., 503 with reason) instead of raising at import.
  - Optional feature flag: VOICE_ENABLED to disable voice endpoints without code removal.
  - Documentation note: If voice features are required in container, either:
    - Provide prebuilt whisper/piper executables in the image, or
    - Extend Dockerfile with the necessary toolchains (Rust/Cargo) and build steps.
- Acceptance criteria:
  - Backend starts successfully without whisper/piper present.
  - Voice endpoints respond gracefully with a clear error when executables are unavailable.
  - When executables are present, STT/TTS/wake-word calls succeed in a basic smoke test.