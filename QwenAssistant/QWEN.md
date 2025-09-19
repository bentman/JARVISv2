# Local AI Assistant - Project Context

## Project Overview

The Local AI Assistant is a privacy-focused, local-first AI assistant that runs entirely on user hardware with no cloud dependencies. It provides chat, voice interaction, and reasoning capabilities while ensuring all data processing occurs locally on the user's device.

### Key Features

1. **Privacy First**
   - Local Processing: All AI inference happens on your device
   - End-to-End Encryption: Conversation data encrypted at rest
   - No Cloud Dependencies: Zero external data transmission
   - Data Classification: Automatic sensitive data detection

2. **Hardware Adaptive**
   - Automatic Detection: CPU/GPU/NPU capability detection
   - Dynamic Model Selection: Optimizes for your hardware
   - Three Performance Tiers:
     - Light (CPU-only): 3-7B parameter models
     - Medium (GPU/NPU): 7-13B parameter models
     - Heavy (High-end GPU): 13B+ parameter models

3. **Voice Interaction**
   - Wake Word Detection: Hands-free activation
   - Speech-to-Text: Accurate voice recognition
   - Text-to-Speech: Natural voice responses
   - Real-time Processing: Low-latency voice interaction

4. **Rich Chat Interface**
   - Streaming Responses: Real-time message updates
   - Conversation History: Persistent chat storage
   - Multi-modal Input: Voice and text support
   - Responsive Design: Works on all screen sizes

5. **Cross-Platform**
   - Windows, macOS, and Linux support
   - Consistent experience across platforms

## Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: SQLite with SQLModel
- **AI Inference**: ONNX Runtime, llama.cpp
- **Containerization**: Docker

### Frontend
- **Desktop Framework**: Tauri (Rust + React)
- **UI Library**: React with Tailwind CSS
- **State Management**: Zustand
- **Voice Processing**: Web Audio API

### AI Models
- **Chat Models**: Llama 3.2, Mistral 7B, Llama 3.3
- **Voice Models**: Whisper (STT), Piper (TTS)
- **Wake Word**: Planned for local implementation (currently in development)
- **Model Format**: GGUF for optimal local performance

## Project Structure

```
local-ai-assistant/
├── backend/              # FastAPI backend services
│   ├── app/              # Main application code
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Core application logic
│   │   ├── models/       # Data models
│   │   ├── services/     # Business logic services
│   │   └── main.py       # Application entry point
│   ├── tests/            # Unit and integration tests
│   ├── Dockerfile        # Backend Docker image
│   └── requirements.txt  # Python dependencies
├── frontend/             # Tauri desktop application
│   ├── src/              # React application source
│   ├── src-tauri/        # Tauri backend code (Rust)
│   └── package.json      # Frontend dependencies
├── models/               # AI models and related files
├── docker-compose.yml    # Service orchestration
├── README.md             # Project documentation
├── INSTALLATION.md       # Installation guide
├── DEPLOYMENT.md         # Deployment guide
└── TESTING.md            # Testing and optimization plan
```

## Development Workflow

### Prerequisites
- Docker Desktop
- Node.js 18+
- Rust (for Tauri)
- Python 3.11+

### Quick Start Commands

Using the Makefile (recommended):
```bash
# Install all dependencies
make setup

# Start backend in development mode
make backend-dev

# Start frontend in development mode
make frontend-dev

# Start both backend and frontend in development mode
make dev

# Run all tests
make test

# Build both backend and frontend
make build
```

Manual commands:
```bash
# Start backend services
cd backend
docker-compose up -d

# Install frontend dependencies and start development server
cd frontend
npm install
npm run tauri dev
```

### Backend Development
- Entry point: `backend/app/main.py`
- API endpoints: `backend/app/api/v1/endpoints/`
- Core logic: `backend/app/core/`
- Data models: `backend/app/models/`
- Services: `backend/app/services/`

### Frontend Development
- Main application: `frontend/src/App.tsx`
- Components: `frontend/src/components/`
- Services: `frontend/src/services/`
- Tauri backend: `frontend/src-tauri/`

## Building and Deployment

### Development Build
1. Backend: `make backend-dev` or `cd backend && uvicorn app.main:app --reload`
2. Frontend: `make frontend-dev` or `cd frontend && npm run tauri dev`

### Production Build
1. Backend: `make backend-build` or `cd backend && docker build -t local-ai-assistant-backend .`
2. Frontend: `make frontend-build` or `cd frontend && npm run tauri build`

## Testing

The project includes comprehensive testing strategies:
- Unit Testing: pytest for backend, Jest for frontend
- Integration Testing: End-to-end API and component testing
- Performance Testing: Load and stress testing
- Security Testing: Vulnerability scanning and penetration testing

Run tests with: `make test` or individually with `make test-backend` and `make test-frontend`

## Development Conventions

### Backend
- FastAPI for REST API implementation
- SQLModel for database models and operations
- Pydantic for data validation
- Environment-based configuration

### Frontend
- React with TypeScript
- Tailwind CSS for styling
- Zustand for state management
- Tauri for desktop application functionality

### AI/ML
- GGUF format models for optimal local performance
- ONNX Runtime and llama.cpp for inference
- Hardware-adaptive model selection

## Key Documentation Files

1. `README.md` - Project overview and quick start
2. `INSTALLATION.md` - Detailed installation guide
3. `DEPLOYMENT.md` - Deployment and configuration
4. `TESTING.md` - Testing strategies and optimization
5. `PROJECT_PLAN.md` - Complete project plan and timeline
6. `SUMMARY.md` - Project summary and implementation status

## Future Enhancements

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