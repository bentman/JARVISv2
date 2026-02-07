# QwenAssistant Services Startup Guide

Complete guide to download models and start the QwenAssistant services.

## Overview

QwenAssistant consists of:
- **Backend:** FastAPI server with AI models (port 8000)
- **Frontend:** React web interface (port 5173)
- **Models:** Local AI models for inference
- **Cache:** Optional Redis for performance
- **Database:** SQLite for persistence

## Prerequisites Checklist

Before starting, verify you have:

- [ ] Python 3.9+ (`python3 --version`)
- [ ] Node.js 16+ (`node --version`)
- [ ] npm 8+ (`npm --version`)
- [ ] 30GB free disk space (`df -h`)
- [ ] 8GB+ RAM (`free -h` or system info)
- [ ] Internet connection for model download

## Step 1: Download AI Models

### Why Models Are Needed

Models provide:
- **LLM (Large Language Model):** For chat and reasoning
- **Whisper (STT):** For speech-to-text voice input
- **Piper (TTS):** For text-to-speech voice output
- **Embeddings:** For semantic search

### Model Profiles

Choose based on your hardware:

| Profile | LLM Size | Speed | Quality | Disk | RAM |
|---------|----------|-------|---------|------|-----|
| **Light** | 3B | Fastest | Basic | 4GB | 8GB |
| **Medium** | 7B | Balanced | Good | 6GB | 16GB |
| **Heavy** | 13B | Slower | Best | 9GB | 32GB |

### Download Models

**Option 1: Automatic (Recommended)**

```bash
# Light profile (fast, 8GB systems)
PROFILE=light bash backend/setup_models.sh

# Medium profile (balanced, 16GB systems) - RECOMMENDED
PROFILE=medium bash backend/setup_models.sh

# Heavy profile (best quality, 32GB systems)
PROFILE=heavy bash backend/setup_models.sh
```

**Option 2: Manual

```bash
mkdir -p backend/../models
cd backend/../models

# Download chat model (choose one)
# Light (3B):
wget https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf

# Medium (7B):
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_K_M.gguf

# Download speech models
wget https://huggingface.co/ggerganov/whisper.cpp/resolve/main/models/ggml-base.bin
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/kathleen/medium/en_US-kathleen-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/kathleen/medium/en_US-kathleen-medium.onnx.json
```

**Download Times:**
- Light: 15-20 minutes
- Medium: 20-30 minutes
- Heavy: 30-40 minutes

(Depends on internet speed)

### Verify Models

```bash
# Check models exist
ls -lh models/

# Expected output:
# llama-*-chat.gguf (3-7GB)
# whisper-*.bin (100-700MB)
# piper-tts.onnx (400MB)
# piper-tts.onnx.json (1KB)
```

---

## Step 2: Configure Environment

### Create .env File

```bash
# Copy example
cp .env.example .env

# Edit configuration
nano .env  # or vim, or your editor
```

### Essential Settings

```ini
# Database
DATABASE_URL=sqlite:///./data/local_ai.db

# Models
MODEL_PATH=../models
HARDWARE_PROFILE=medium  # or light/heavy

# Optional: Cloud features
OPENAI_API_KEY=
GROQ_API_KEY=

# Logging
LOG_LEVEL=INFO
DEBUG=false
```

---

## Step 3: Start Services

### Option A: Native (Development)

Recommended for development and testing.

**Start Backend:**

```bash
cd backend

# Create virtual environment (first time only)
python3 -m venv .venv

# Activate
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows PowerShell

# Install dependencies
pip install -r requirements.txt

# Start backend
uvicorn app.main:app --reload
```

Backend starts on: `http://localhost:8000`

**In another terminal, start Frontend:**

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Start frontend
npm run dev
```

Frontend starts on: `http://localhost:5173`

### Option B: Automated (All-in-One)

Use the startup script:

```bash
# Make script executable (one time)
chmod +x start_services.sh

# Start everything
bash start_services.sh

# Stop everything (Ctrl+C)
```

The script:
1. Checks prerequisites
2. Sets up both backend and frontend
3. Starts services automatically
4. Shows status and logs

### Option C: Docker (Production)

For containerized deployment:

```bash
# Start services
docker compose -f backend/docker-compose.yml up -d

# View logs
docker compose -f backend/docker-compose.yml logs -f

# Stop services
docker compose -f backend/docker-compose.yml down
```

Backend starts on: `http://localhost:8000`
Redis starts on: `localhost:6379`

---

## Step 4: Verify Services

### Backend Health Check

```bash
# Check API is responding
curl http://localhost:8000/api/v1/health/services

# Expected response:
# {"status": "healthy", "services": {...}}
```

### Database Check

```bash
cd backend
python3 -c "from app.models.database import db; conv = db.create_conversation('test'); print('✓ Database working')"
```

### Frontend Check

Open browser: `http://localhost:5173`

You should see the chat interface.

---

## Step 5: First Run

### Test the Chat

1. Open http://localhost:5173 in browser
2. Type a message: "Hello, what is your name?"
3. Click send or press Enter
4. Wait for response (first response is slower)

### Expected Behavior

- **First message:** 5-15 seconds (model loading)
- **Subsequent messages:** 2-10 seconds (depends on complexity)
- **Voice input:** Click microphone, speak, get transcribed text
- **Conversation history:** Messages saved automatically

---

## Monitoring & Troubleshooting

### Check Service Status

```bash
# Backend running?
curl http://localhost:8000/health

# Redis running? (if using Docker)
redis-cli ping

# Frontend accessible?
curl http://localhost:5173
```

### View Logs

```bash
# Backend logs
tail -f /tmp/backend.log

# Frontend logs
tail -f /tmp/frontend.log

# Or use Docker
docker compose -f backend/docker-compose.yml logs -f
```

### Common Issues

**Issue:** "Address already in use"
```bash
# Find what's using the port
lsof -i :8000

# Stop the service and restart
```

**Issue:** "Module not found" errors
```bash
# Ensure virtual environment is activated
source .venv/bin/activate
pip install -r requirements.txt
```

**Issue:** "Connection refused"
```bash
# Backend might be crashing
# Check logs: tail -f /tmp/backend.log
# Verify models exist: ls -la models/
# Check database: python3 verify_structure.py
```

**Issue:** Slow responses
```bash
# Check if using right profile
# Light profile fastest, medium balanced, heavy best quality

# Monitor resources
docker stats  # if using Docker
htop          # if native
```

---

## Performance Optimization

### For Faster Responses

1. **Use Light Profile:**
   ```bash
   PROFILE=light bash backend/setup_models.sh
   HARDWARE_PROFILE=light
   ```

2. **Enable GPU Acceleration:**
   - NVIDIA: Install CUDA
   - macOS: Metal is auto-enabled
   - Others: Use CPU (sufficient for most use cases)

3. **Close Other Applications:**
   - Free up RAM
   - Reduce CPU contention

4. **Use SSD Storage:**
   - Faster model loading
   - Better database performance

### Monitoring Performance

```bash
# Monitor real-time resource usage
watch -n 1 'ps aux | grep -E "python|node" | grep -v grep'

# Check GPU usage (NVIDIA)
watch -n 1 nvidia-smi

# Profile backend performance
docker stats qwen_backend  # if using Docker
```

---

## Stop Services

### Native

```bash
# Press Ctrl+C in backend terminal
# Press Ctrl+C in frontend terminal

# Or kill processes
pkill -f uvicorn
pkill -f "node.*dev"
```

### Docker

```bash
docker compose -f backend/docker-compose.yml down

# Clean up volumes (optional - deletes data)
docker compose -f backend/docker-compose.yml down -v
```

---

## Advanced Configuration

### Change Ports

Edit `.env`:
```ini
API_PORT=8001          # Backend port
FRONTEND_PORT=5174     # Frontend port
```

### Enable Redis Caching

Docker: Already included in docker-compose.yml

Native:
```bash
# Install Redis
brew install redis      # macOS
sudo apt install redis  # Ubuntu/Debian

# Run Redis
redis-server
```

### Enable Cloud Features

Edit `.env`:
```ini
CLOUD_ENABLED=true
OPENAI_API_KEY=sk-...  # Add your key
```

### Change Model

Edit backend/app/core/config.py or environment:
```bash
HARDWARE_PROFILE=heavy
```

---

## Backup & Restore

### Backup Conversations

```bash
# SQLite database stored at:
backend/data/local_ai.db

# Backup:
cp backend/data/local_ai.db backup-$(date +%s).db
```

### Export Conversations

Via API (when implemented):
```bash
curl http://localhost:8000/api/v1/memory/export > conversations.json
```

---

## Resetting Everything

### Reset Database

```bash
# Stop services first
rm backend/data/local_ai.db
# Restart backend - database recreates automatically
```

### Reset All Models

```bash
# Delete models
rm -rf models/
# Re-download: PROFILE=medium bash backend/setup_models.sh
```

### Full Clean Reinstall

```bash
# Remove virtual environments
rm -rf backend/.venv
rm -rf frontend/node_modules

# Remove data
rm -rf backend/data
rm -rf models

# Re-setup
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt

cd frontend
npm install

# Download models again
PROFILE=medium bash ../backend/setup_models.sh
```

---

## Getting Help

### Documentation

- **Quick Start:** See QUICK_START.md
- **Technical Details:** See OPTION_A_COMPLETION_REPORT.md
- **Docker Guide:** See DOCKER_DEPLOYMENT.md
- **Project Overview:** See README.md in parent directory

### Verification Scripts

```bash
# Verify backend structure
cd backend && python3 verify_structure.py

# Run comprehensive tests
cd backend && python3 test_qwen_backend.py
```

### Check Logs

```bash
# Backend
tail -f /tmp/backend.log

# Frontend
tail -f /tmp/frontend.log

# Docker
docker compose -f backend/docker-compose.yml logs
```

---

## System Requirements

### Minimum

- Python 3.9+
- Node.js 16+
- 8GB RAM
- 30GB disk
- CPU 4 cores

### Recommended

- Python 3.11+
- Node.js 18+
- 16GB RAM
- 50GB SSD
- CPU 8+ cores
- GPU (NVIDIA/AMD/Intel)

### Supported Platforms

- Linux (Ubuntu 20.04+)
- macOS (10.15+)
- Windows 10/11
- Docker compatible systems

---

## What's Next

After starting services:

1. **Explore Features:**
   - Chat with AI
   - Use voice input/output
   - Search through conversations
   - View conversation history

2. **Customize:**
   - Change models/profile
   - Adjust settings
   - Enable cloud features
   - Configure privacy

3. **Integrate:**
   - Connect to external APIs
   - Add custom tools
   - Build plugins
   - Create workflows

4. **Deploy:**
   - Production setup
   - Multi-server deployment
   - Cloud hosting
   - Monitoring/alerting

---

## Success Indicators

✅ Backend running:
```bash
curl http://localhost:8000/api/v1/health/services
# Returns: {"status": "healthy", ...}
```

✅ Frontend accessible:
```
http://localhost:5173 shows chat interface
```

✅ Database working:
```bash
cd backend && python3 verify_structure.py
# Returns: 4/4 checks passed
```

✅ AI responding:
Type message and get response in chat interface

---

**You're ready! Start chatting with your local AI. 🚀**
