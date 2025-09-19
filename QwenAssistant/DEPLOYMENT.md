# Local AI Assistant Build and Deployment Guide

## Prerequisites

1. Docker Desktop (for backend services)
2. Node.js 18+ (for frontend)
3. Rust (for Tauri desktop app)
4. Python 3.11+ (for backend)

## Development Setup

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the backend:
```bash
uvicorn app.main:app --reload
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run in development mode:
```bash
npm run tauri dev
```

## Production Build

### Backend Docker Build

1. Build the Docker image:
```bash
cd backend
docker build -t local-ai-assistant-backend .
```

2. Run with Docker Compose:
```bash
cd ..
docker-compose up -d
```

### Frontend Desktop Build

1. Build the Tauri application:
```bash
cd frontend
npm run tauri build
```

This will create platform-specific installers in the `src-tauri/target/release/bundle/` directory.

## Model Installation

The application requires local AI models to function. Models should be placed in the `models/` directory.

### Required Models

1. **Chat Models**:
   - Llama 3.2 (3B) for light profile
   - Mistral 7B Instruct for medium profile
   - Llama 3.3 (70B) for heavy profile

2. **Voice Models**:
   - Whisper Small for speech-to-text
   - Piper voices for text-to-speech

### Model Format

Models should be in GGUF format for optimal performance with llama.cpp.

## Configuration

### Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
# Database
DATABASE_URL=sqlite:///./data/local_ai.db

# Model paths
MODEL_PATH=/models

# Security
SECRET_KEY=your-secret-key-here
```

### Hardware Profiles

The application automatically detects hardware capabilities and selects the appropriate profile:

- **Light**: CPU-only operation with 3-7B parameter models
- **Medium**: GPU/NPU operation with 7-13B parameter models
- **Heavy**: High-end GPU operation with 13B+ parameter models

## Deployment Options

### Local Installation

1. Install Docker Desktop
2. Download and install the desktop application
3. Place models in the models directory
4. Launch the application

### Enterprise Deployment

For enterprise deployments, consider:

1. Centralized model management
2. User management and authentication
3. Usage monitoring and analytics
4. Compliance reporting

## Troubleshooting

### Common Issues

1. **Models not loading**: Ensure models are in the correct format and location
2. **Voice not working**: Check microphone permissions
3. **Slow responses**: Verify hardware profile matches system capabilities
4. **Database errors**: Ensure write permissions for the data directory

### Logs

Backend logs can be accessed through Docker:
```bash
docker-compose logs backend
```

Frontend logs are available in the application's data directory.