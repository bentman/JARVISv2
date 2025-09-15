# Local-First AI Assistant

A complete local-first AI assistant that runs entirely offline with chat, voice interaction, reasoning, and coding capabilities. Built with Docker backend, Tauri desktop frontend, and automatic hardware detection for optimal model selection.

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** - For running the AI backend
- **Node.js 18+** - For the frontend development
- **Rust** - For building the Tauri application  
- **Git** - For cloning the repository

### One-Command Startup

**Linux/macOS:**
```bash
chmod +x start.sh
./start.sh
```

**Windows:**
```cmd
start.bat
```

This will:
1. Detect your hardware tier (CPU/GPU/NPU)
2. Start the Docker backend with appropriate models
3. Provide instructions for running the frontend

### Manual Startup

1. **Start Backend Services:**
```bash
# For GPU systems
docker-compose --profile gpu up -d

# For CPU-only systems  
docker-compose --profile cpu-only up -d
```

2. **Install Frontend Dependencies:**
```bash
cd frontend
npm install
```

3. **Run Frontend:**
```bash
# Development mode
npm run dev

# Build production app
npm run tauri build
```

## 🏗️ Architecture

### Backend (Docker)
- **Ollama**: Local model runtime for LLM inference
- **AI Assistant Backend**: Rust service for routing, memory, and hardware detection
- **SQLite**: Local conversation storage

### Frontend (Tauri + React)
- **Tauri**: Cross-platform desktop framework
- **React + TypeScript**: Modern web UI
- **Voice Controls**: Speech-to-text and text-to-speech
- **Hardware Detection**: Automatic model selection

## 🧠 Hardware Tiers & Models

The system automatically detects your hardware and selects appropriate models:

| Tier | Hardware Requirements | Chat Model | Code Model | Reasoning Model |
|------|----------------------|------------|------------|-----------------|
| **Light** | CPU only, <16GB RAM | Phi-3 3.8B | Phi-3 3.8B | Phi-3 3.8B |
| **Medium** | 4-8GB VRAM or 16-32GB RAM | Gemma2 9B | DeepSeek Coder 6.7B | Gemma2 9B |
| **Heavy** | >8GB VRAM or >32GB RAM | Llama 3.1 8B | DeepSeek Coder 33B | Llama 3.1 8B |
| **NPU** | Neural Processing Unit | Gemma2 2B | Phi-3 3.8B | Phi-3 3.8B |

## 📱 Features

### Chat Interface
- **Multi-mode Chat**: General conversation, code assistance, reasoning tasks
- **Message History**: Persistent conversation storage
- **Real-time Responses**: Streaming model inference

### Voice Interaction
- **Speech-to-Text**: Voice input for hands-free interaction
- **Text-to-Speech**: Audio responses for accessibility
- **Voice Commands**: Wake word activation (planned)

### Memory System
- **Conversation Search**: Find previous discussions
- **Context Awareness**: Models understand conversation history
- **Export/Import**: Backup and restore conversations

### Hardware Optimization
- **Auto-Detection**: Identifies CPU, GPU, NPU capabilities  
- **Dynamic Routing**: Selects best model for each request type
- **Resource Monitoring**: Tracks usage and performance

## 🛠️ Development

### Project Structure
```
├── backend/                 # Rust backend service
│   ├── src/                # Source code
│   ├── Dockerfile          # Container definition
│   └── config.yaml         # Configuration
├── frontend/               # Tauri + React frontend
│   ├── src/                # React UI source  
│   ├── src-tauri/          # Rust Tauri backend
│   └── package.json        # Node.js dependencies
├── docker-compose.yml      # Service orchestration
├── start.sh               # Linux/macOS startup
└── start.bat              # Windows startup
```

### Backend Development
```bash
cd backend
cargo run
```

### Frontend Development  
```bash
cd frontend
npm run dev          # Web development server
npm run tauri dev    # Desktop app development
```

### Building for Production
```bash
# Backend
docker build -t ai-assistant-backend backend/

# Frontend
cd frontend
npm run tauri build  # Creates platform-specific installers
```

## 🔧 Configuration

### Backend Configuration (`backend/config.yaml`)
```yaml
database:
  path: "data/assistant.db"

ollama:
  base_url: "http://localhost:11434"
  timeout_seconds: 300

models:
  light_tier: ["phi3:3.8b"]
  medium_tier: ["gemma2:9b", "deepseek-coder:6.7b"]
  heavy_tier: ["llama3.1:8b", "gemma2:27b", "deepseek-coder:33b"]
  npu_tier: ["phi3:3.8b", "gemma2:2b"]
```

### Environment Variables
- `OLLAMA_BASE_URL`: Ollama service endpoint
- `DATABASE_PATH`: SQLite database location  
- `RUST_LOG`: Logging level (debug, info, warn, error)

## 🔒 Privacy & Security

- **100% Local**: No data leaves your machine
- **No Telemetry**: No usage tracking or analytics
- **Open Source**: Transparent, auditable code
- **Offline Capable**: Works without internet connection

## 📊 System Requirements

### Minimum (Light Tier)
- 16GB RAM
- 4 CPU cores
- 50GB disk space

### Recommended (Medium Tier)  
- 32GB RAM
- 8 CPU cores
- GPU with 4-8GB VRAM
- 100GB disk space

### Optimal (Heavy Tier)
- 64GB RAM
- 16+ CPU cores  
- GPU with 16+ GB VRAM
- 200GB disk space

## 🐛 Troubleshooting

### Backend Won't Start
```bash
# Check Docker status
docker ps
docker-compose logs backend

# Reset services
docker-compose down -v
docker-compose up -d
```

### Model Download Issues
```bash
# Manual model pull
docker exec -it ai_assistant_ollama ollama pull phi3:3.8b

# Check available space
df -h
```

### Frontend Build Errors
```bash
# Clean and reinstall
cd frontend
rm -rf node_modules dist
npm install
npm run tauri build
```

### Voice Recognition Not Working
- Check microphone permissions
- Verify audio device in system settings
- Test with `npm run tauri dev` for debugging

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Ollama** - Local LLM runtime
- **Tauri** - Cross-platform app framework
- **React** - UI framework
- **Rust** - System programming language

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/ai-assistant/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/ai-assistant/discussions)
- **Documentation**: [Project Wiki](https://github.com/your-repo/ai-assistant/wiki)