# Agentic Coding Environment - Quick Start Guide

## Overview

Zero-configuration AI coding environment with local Ollama models and Aider web interface.

**Architecture:**
- 3 Ollama AI models (codeqwen:7b, codestral:latest, deepseek-r1:7b)
- Aider AI coding assistant with web interface
- FastAPI orchestrator for model routing
- Docker Desktop on Windows 11

## Prerequisites

- **Windows 11** with Docker Desktop
- **16GB+ RAM** (32GB+ recommended)
- **PowerShell** (built-in)

## Quick Start

### 1. Start Everything
```powershell
cd D:\ProgramData\docker\AGENTIC
docker-compose up -d
```

### 2. Access Services
- **Aider Web Interface:** http://localhost:8501
- **Orchestrator API:** http://localhost:7000
- **Ollama Models:** localhost:11001-11003

**That's it!** Everything starts automatically including model downloads.

## Usage

### Aider AI Coding Assistant

**Web Interface (Recommended):**
- Open http://localhost:8501 in your browser
- Drag & drop files or use the interface
- Chat with AI about your code

**Command Line:**
```powershell
docker exec -it agentic-aider-1 aider --model openai/codeqwen:7b --no-show-model-warnings
```

### API Access

**Test orchestrator:**
```powershell
curl http://localhost:7000
```

**Generate code via API:**
```powershell
curl -X POST http://localhost:7000/generate -H "Content-Type: application/json" -d '{\"model\": \"codeqwen\", \"prompt\": \"Write a Python hello world function\"}'
```

### Direct Ollama Access
```powershell
curl http://localhost:11001/api/tags  # codeqwen:7b
curl http://localhost:11002/api/tags  # codestral:latest  
curl http://localhost:11003/api/tags  # deepseek-r1:7b
```

## Service Management

### Check Status
```powershell
docker-compose ps
```

### View Logs
```powershell
docker-compose logs aider        # Aider logs
docker-compose logs orchestrator # API logs
docker-compose logs codeqwen1.5  # Model logs
```

### Stop Everything
```powershell
docker-compose down
```

### Clean Restart
```powershell
docker-compose down
docker-compose up -d
```

## Troubleshooting

### Services Won't Start
```powershell
# Check Docker Desktop is running
docker version

# Check for port conflicts
netstat -an | findstr ":8501 :7000 :11001 :11002 :11003"

# Force rebuild
docker-compose down
docker-compose up -d --force-recreate
```

### Web Interface Not Loading
```powershell
# Wait for models to download (first time takes 5-10 minutes)
docker-compose logs aider

# Check if port 8501 is accessible
curl http://localhost:8501
```

### Models Not Available
```powershell
# Check model downloads
docker exec agentic-codeqwen1.5-1 ollama list
docker exec agentic-codestral-1 ollama list
docker exec agentic-deepseek-coder-1 ollama list

# Wait for init containers to complete
docker-compose ps -a | findstr init
```

### High Memory Usage
```powershell
# Check resource usage
docker stats

# Run only essential services
docker-compose up -d codeqwen1.5 aider orchestrator
```

### Complete Reset
```powershell
# WARNING: Deletes all models and data
docker-compose down -v
docker system prune -f
docker-compose up -d
```

## Configuration

### Available Models
- **codeqwen:7b** - Best for code understanding (default)
- **codestral:latest** - Optimized for code completion
- **deepseek-r1:7b** - Strong reasoning capabilities

### Additional Coding Assistants
The platform can be extended with complementary open-source AI coding tools:

- **[OpenHands](https://github.com/All-Hands-AI/OpenHands)** - Autonomous AI agents for complex multi-step development tasks
- **[Tabby](https://github.com/TabbyML/tabby)** - Self-hosted code completion engine (GitHub Copilot alternative)  
- **[SWE-agent](https://github.com/SWE-agent/SWE-agent)** - Specialized autonomous GitHub issue resolution

*All support local LLMs and Docker deployment for seamless integration.*

### Ports Used
- **8501** - Aider Web Interface
- **7000** - Orchestrator API
- **11001** - CodeQwen Ollama
- **11002** - Codestral Ollama  
- **11003** - DeepSeek Ollama

### Environment Variables
Located in `.env` file:
```env
CODEQWEN_ENDPOINT=http://codeqwen1.5:11434
CODESTRAL_ENDPOINT=http://codestral:11434
DEEPSEEK_ENDPOINT=http://deepseek-coder:11434
```

## Performance Tips

### For Lower-End Systems
```powershell
# Start only one model
docker-compose up -d codeqwen1.5 aider orchestrator
```

### For High Performance
```powershell
# All models (requires 16GB+ RAM)
docker-compose up -d
```

### Extending with Additional Tools
Add complementary coding assistants to your environment:

**[OpenHands](https://github.com/All-Hands-AI/OpenHands)** (Autonomous Development):
```yaml
openhands:
  image: ghcr.io/all-hands-ai/openhands:latest
  ports:
    - "3000:3000"
  environment:
    - LLM_API_KEY=ollama
    - LLM_BASE_URL=http://codeqwen1.5:11434/v1
```

**[Tabby](https://github.com/TabbyML/tabby)** (Code Completion):
```yaml
tabby:
  image: tabbyml/tabby:latest
  ports:
    - "8080:8080"
  volumes:
    - tabby_data:/data
  command: serve --model StarCoder-1B --host 0.0.0.0
```

**[SWE-agent](https://github.com/SWE-agent/SWE-agent)** (Issue Resolution):
```yaml
swe-agent:
  image: sweagent/swe-agent:latest
  volumes:
    - ./:/workspace
  environment:
    - SWE_AGENT_CONFIG_FILE=/workspace/config.yaml
```

## File Structure
```
D:\PROGRAMDATA\DOCKER\AGENTIC\
├── docker-compose.yaml    # Main configuration
├── .env                   # Environment settings
├── claude.md             # Claude instructions
├── runbook.md            # This guide
└── orchestrator/
    ├── Dockerfile
    └── orchestrator.py    # API router
```

## Maintenance

### Updates
```powershell
docker-compose pull
docker-compose up -d --force-recreate
```

### Cleanup
```powershell
docker image prune -f
docker system df  # Check disk usage
```

### Backup
Models and data are stored in Docker volumes. To backup:
```powershell
docker volume ls | findstr agentic
```

---

**Need Help?** Check container logs: `docker-compose logs [service-name]`

**First Run?** Initial model downloads take 5-10 minutes. Web interface available at http://localhost:8501 when ready.