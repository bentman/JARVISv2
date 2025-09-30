# Qwen Code Instructions

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
- **QWEN.md**: This file - for AI coding assistant instructions

## Current Implementation Status
The project has made significant progress with working implementations of:
- Backend services (hardware detection, chat API, voice processing, privacy controls)
- Frontend chat interface with voice capabilities
- Model routing system based on hardware profiles
- Memory and privacy services
- Basic database integration with SQLite

## Next Steps & Implementation Requirements

### Immediate Priorities
1. **Complete Semantic Search**: Implement vector embeddings functionality in memory_service.py
2. **Database Implementation**: Complete the database models with actual SQLite implementation
3. **Wake Word Detection**: Replace placeholder implementation in voice_service.py with actual wake word detection
4. **Model Integration**: Ensure GGUF model files are properly integrated and accessible
5. **Testing**: Create comprehensive unit and integration tests

### Critical Missing Elements
1. **Redis Integration**: For short-term caching as mentioned in the architecture
2. **Vector Database**: For semantic search capabilities (consider FAISS or similar)
3. **NPU Detection**: Complete hardware detector with NPU-specific APIs
4. **Budget Monitoring**: Cost analysis and budget governance features
5. **Cross-platform Desktop App**: Complete Tauri configuration for desktop distribution

### Implementation Guidelines
- **Reference Existing Implementations**: When implementing features, research similar open-source projects on GitHub for proven approaches
- **Model Integration**: Look for examples of GGUF model integration with ONNX Runtime or llama.cpp
- **Voice Processing**: Research Whisper for STT and Piper TTS implementations
- **Wake Word Detection**: Implement local-first wake word detection solutions (avoid cloud-dependent services like Porcupine)
- **Vector Embeddings**: Implement semantic search using vector databases like FAISS, HNSW, or similar

### Requirements Reference
- All implementation should align with requirements in `Project.md`
- Do not implement features without understanding the complete requirements first
- Focus on local-first processing as defined in the requirements
- Ensure all data processing occurs locally by default with no cloud dependencies
- Maintain proper dependency isolation using the virtual environment at `backend/.venv`
