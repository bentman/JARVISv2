# Local-First AI Assistant MVP

A privacy-focused AI assistant that runs entirely on your local hardware with automatic capability detection and voice interaction.

## Features

- **Hardware Detection**: Automatically detects CPU, GPU, and NPU capabilities
- **Three Capability Profiles**: Light (CPU), Medium (GPU/NPU), Heavy (High-end GPU/NPU)
- **Voice Interface**: Speech-to-text and text-to-speech with real-time feedback
- **Local Backend**: Lightweight Express.js server for coordination and persistence
- **Memory Management**: Persistent conversation history and context
- **Cross-Platform**: Works on Windows, Mac, Linux via web browser

## Quick Start

### 1. Start the Backend

```bash
# Using Docker (recommended)
docker-compose up -d

# Or run locally
cd backend
npm install
npm start
```

### 2. Start the Client

```bash
npm run dev
```

### 3. Open in Browser

Navigate to `http://localhost:5173` and start chatting!

## Architecture

### Backend (Port 3001)
- **Express.js server** with REST API
- **Local file persistence** for conversations and memory
- **Health monitoring** and status endpoints
- **CORS enabled** for client communication

### Client (Port 5173)
- **React + TypeScript** with Tailwind CSS
- **Real hardware detection** using WebGL, WebGPU, and system APIs
- **Speech Recognition API** for voice input
- **Speech Synthesis API** for voice output
- **Local storage** for preferences and session management

## API Endpoints

- `GET /health` - Backend health and status
- `POST /chat` - Send message and get response
- `GET /memory/:sessionId` - Retrieve conversation memory
- `POST /search` - Search through conversation history
- `GET /conversations/:sessionId` - Get full conversation history

## Hardware Profiles

### Light Capacity (CPU Only)
- **Model**: 1-3B parameters
- **Capabilities**: Basic conversation, light reasoning, Q&A
- **Hardware**: Any modern CPU

### Medium Capacity (GPU/NPU Mid-tier)
- **Model**: 7-13B parameters  
- **Capabilities**: Reasoning, basic coding, code review
- **Hardware**: Dedicated GPU or NPU

### Heavy Capacity (High-end GPU/NPU)
- **Model**: 30-70B parameters
- **Capabilities**: Advanced reasoning, complex coding, architecture design
- **Hardware**: High-end GPU (RTX 4080+) or advanced NPU

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Start backend in development mode
cd backend
npm run dev

# Build for production
npm run build
```

## Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build manually
docker build -t local-ai-assistant .
docker run -p 3001:3001 -v $(pwd)/data:/app/data local-ai-assistant
```

## Privacy & Security

- **100% Local Processing**: No external API calls or cloud services
- **Data Persistence**: All data stored locally in files or browser storage
- **No Telemetry**: No usage tracking or analytics
- **Secure by Default**: CORS configured, Helmet security headers enabled

## Browser Compatibility

- **Chrome/Edge**: Full support including voice features
- **Firefox**: Full support including voice features  
- **Safari**: Full support including voice features
- **Mobile Browsers**: Text chat supported, voice may be limited

## Troubleshooting

### Backend Connection Issues
1. Ensure backend is running on port 3001
2. Check `docker-compose logs` for errors
3. Verify no firewall blocking localhost:3001

### Voice Not Working
1. Grant microphone permissions when prompted
2. Ensure HTTPS or localhost (required for speech APIs)
3. Check browser console for speech API errors

### Performance Issues
1. Switch to a lighter profile if responses are slow
2. Clear browser cache and local storage
3. Restart backend if memory usage is high

## License

MIT License - See LICENSE file for details