# QwenAssistant Quick Start Guide

Get the QwenAssistant AI assistant up and running in minutes.

## Prerequisites

### System Requirements
- **RAM:** Minimum 8GB (16GB recommended)
- **Storage:** 30GB free disk space
- **CPU:** 4+ cores recommended
- **OS:** Windows, macOS, or Linux

### Software Requirements
- Python 3.9+
- Node.js 16+
- npm 8+
- (Optional) Docker & Docker Compose

### Internet Connection
Required for downloading AI models (one-time, ~10-20GB depending on profile)

---

## Quick Start (3 Steps)

### Step 1: Download Models

Models are required for local AI inference. Choose a profile based on your hardware:

```bash
# Light profile (for 8GB+ RAM, fastest)
PROFILE=light bash backend/setup_models.sh

# Medium profile (for 16GB+ RAM, balanced)
PROFILE=medium bash backend/setup_models.sh

# Heavy profile (for 32GB+ RAM, most capable)
PROFILE=heavy bash backend/setup_models.sh
```

**Download Sizes:**
- Light: ~3.5GB LLM + ~0.5GB speech models = ~4GB total
- Medium: ~5GB LLM + ~1GB speech models = ~6GB total
- Heavy: ~7.5GB LLM + ~1.5GB speech models = ~9GB total

**Time Estimate:** 10-30 minutes (depends on internet speed)

### Step 2: Start Backend & Frontend

```bash
# Option A: Native (recommended for development)
bash start_services.sh

# Option B: Docker (for production)
docker compose -f backend/docker-compose.yml up -d
```

**What Happens:**
- Backend starts on `http://localhost:8000`
- Frontend starts on `http://localhost:5173`
- API documentation available at `http://localhost:8000/docs`

### Step 3: Open in Browser

```
http://localhost:5173
```

You're ready to chat with your local AI!

---

## Detailed Setup

### Manual Setup (if scripts don't work)

#### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Start backend
uvicorn app.main:app --reload
# Backend runs on http://localhost:8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
# Frontend runs on http://localhost:5173
```

---

## Configuration

### Environment Variables

Create `.env` file in `backend/` directory:

```bash
# Database
DATABASE_URL=sqlite:///./data/local_ai.db

# Model paths
MODEL_PATH=../models

# Privacy
PRIVACY_ENCRYPT_AT_REST=true

# Logging
LOG_LEVEL=INFO

# Optional: API keys for cloud features
# OPENAI_API_KEY=sk-...
# GROQ_API_KEY=gsk-...
```

### Hardware Profile Selection

The backend automatically detects your hardware and selects an appropriate profile:

- **Light (3B LLM):** Fast responses, basic understanding
- **Medium (7B LLM):** Balanced speed and capability
- **Heavy (13B+ LLM):** Best accuracy, slower responses

Override with environment variable:

```bash
HARDWARE_PROFILE=medium uvicorn app.main:app --reload
```

---

## Verification

### Backend Health Check

```bash
curl http://localhost:8000/api/v1/health/services
```

Expected response:
```json
{"status": "healthy", "services": {...}}
```

### Frontend Check

Open http://localhost:5173 and verify you can see the chat interface.

### Database Verification

```bash
cd backend
python3 -c "from app.models.database import db; print('✓ Database ready')"
```

---

## Troubleshooting

### Backend Won't Start

**Error:** `ModuleNotFoundError: No module named 'app'`
- Solution: Activate virtual environment: `source .venv/bin/activate`

**Error:** `Address already in use`
- Solution: Change port: `uvicorn app.main:app --port 8001`

**Error:** `Database locked`
- Solution: Close other instances, remove `data/local_ai.db` and restart

### Frontend Won't Start

**Error:** `npm: command not found`
- Solution: Install Node.js from https://nodejs.org/

**Error:** `port 5173 already in use`
- Solution: `npm run dev -- --port 5174`

### Models Not Downloading

**Error:** `Network error` or `Permission denied`
- Check internet connection: `ping huggingface.co`
- Ensure write permission in models directory
- Try using Docker instead

### Slow Responses

**Cause:** Using Heavy profile on underpowered hardware
- Solution: Switch to Light or Medium profile
- Use GPU acceleration if available

---

## Usage Tips

### Chat Features

1. **Text Input:** Type messages and press Enter
2. **Voice Input:** Click microphone icon to speak
3. **Mode Selection:** Choose chat, coding, or reasoning mode
4. **History:** All conversations saved locally

### Performance Tips

- Close other applications to free RAM
- Use Light profile on 8GB systems
- Enable GPU acceleration if available
- Use SSD for faster database access

### Privacy

- All data stays on your computer
- No data sent to cloud by default
- Optional cloud integration available
- Automatic data encryption supported

---

## Advanced Features

### Memory & Search

- Conversations automatically searchable
- Vector embeddings for semantic search
- Up to 5 recent relevant messages retrieved
- Full conversation history available

### Privacy Controls

- Sensitive data automatic detection
- Optional encryption at rest
- Data classification (public/personal/sensitive)
- Selective cloud synchronization

### Budget Tracking

- Token usage per conversation
- Optional cost estimation for cloud features
- Real-time budget monitoring
- Spending alerts

---

## Docker Deployment

### Start with Docker

```bash
# Build and start services
docker compose -f backend/docker-compose.yml up -d

# View logs
docker compose -f backend/docker-compose.yml logs -f backend

# Stop services
docker compose -f backend/docker-compose.yml down
```

### Docker Compose Configuration

Services include:
- **Backend:** FastAPI on port 8000
- **Redis:** Caching on port 6379
- **Data Volume:** SQLite database persistence

---

## Performance Benchmarks

### Response Times (Medium Profile)

| Task | Time | Notes |
|------|------|-------|
| Simple question | 2-5s | With CUDA GPU: <2s |
| Complex reasoning | 10-30s | Depends on answer length |
| Search query | 1-3s | Uses vector search + cache |
| Message retrieval | <100ms | Local database access |

### Resource Usage

| Component | Memory | CPU | Storage |
|-----------|--------|-----|---------|
| Backend | 2-4GB | 20-50% | 100MB code |
| Models (Medium) | 5-7GB loaded | 60-80% | 5GB on disk |
| Frontend | 300-500MB | 10-20% | 100MB code |
| Database | Variable | <1% | <500MB |

---

## Upgrades & Scaling

### Adding Models

Download additional models:
```bash
cd backend
bash setup_models.sh heavy  # Switch to heavy profile
```

### Switching Profiles

Change `PROFILE` environment variable and restart.

### Cloud Integration (Optional)

Enable cloud features in `backend/app/core/config.py`:
- Web search integration
- Cloud model fallback
- Cross-device sync

---

## Getting Help

### Common Issues

1. **Backend crashes on startup**
   - Check logs: `tail -f /tmp/backend.log`
   - Verify database: `python3 verify_structure.py`

2. **Models not working**
   - Verify models downloaded: `ls backend/../models/`
   - Check model format: Must be GGUF for LLMs

3. **Slow performance**
   - Monitor CPU/RAM usage
   - Check if using right profile
   - Enable GPU acceleration

### Verification Scripts

```bash
# Verify backend structure
cd backend && python3 verify_structure.py

# Run comprehensive tests
cd backend && python3 test_qwen_backend.py
```

---

## Next Steps

### Development

1. Review API documentation: http://localhost:8000/docs
2. Check code: `backend/app/services/` for service details
3. Customize: Edit `backend/app/core/config.py` for settings

### Production Deployment

1. Build Docker image: `docker build -f backend/Dockerfile -t qwen-ai:latest`
2. Configure environment: Set production environment variables
3. Deploy: Use docker-compose or Kubernetes
4. Monitor: Set up health checks and logging

### Extensions

- Add custom tools/plugins
- Integrate with external APIs
- Build mobile companion app
- Create conversational UI themes

---

## Resources

- **Documentation:** See `IMPLEMENTATION_SUMMARY.md`
- **Technical Details:** See `OPTION_A_COMPLETION_REPORT.md`
- **Architecture:** See `Project.md` and `Project_Components.md`
- **API Reference:** http://localhost:8000/docs (when running)

---

## Support

For issues:
1. Check troubleshooting section above
2. Review logs: `/tmp/backend.log` and `/tmp/frontend.log`
3. Run verification scripts
4. Check GitHub issues if applicable

---

**Happy chatting! 🚀**

Your local AI assistant is ready to help with any task while keeping your data private and under your control.
