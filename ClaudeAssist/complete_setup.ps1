# complete_setup.ps1 - Complete your Jarvis repository structure
param(
    [switch]$CreateFiles,
    [switch]$All
)

function Write-Step($message) {
    Write-Host "🔧 $message" -ForegroundColor Green
}

# Create missing directories
function Create-MissingDirectories {
    Write-Step "Creating missing directories..."
    
    $directories = @(
        "frontend",
        "frontend/public",
        "frontend/src",
        "frontend/src/components",
        "frontend/src/services", 
        "backend/api",
        "backend/services",
        "backend/core",
        "backend/utils", 
        "backend/tests",
        "configs/development",
        "configs/production",
        "configs/local",
        "docs",
        "mobile",
        ".github/workflows",
        ".github/ISSUE_TEMPLATE"
    )
    
    foreach ($dir in $directories) {
        if (!(Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Host "  Created: $dir" -ForegroundColor DarkGreen
        }
    }
}

# Create .gitignore
function Create-GitIgnore {
    Write-Step "Creating .gitignore file..."
    
    $gitignore = @"
# Python
__pycache__/
*.py[cod]
*`$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/
env.bak/
venv.bak/
jarvis_env/
.venv/

# Environment Variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Docker
docker-compose.override.yml

# Logs
*.log
logs/

# Database
*.db
*.sqlite3

# AI Models (large files)
models/
*.bin
*.gguf
*.ggml
*.pt
*.pth
*.safetensors

# Audio/Video files
*.wav
*.mp3
*.mp4
*.avi

# Temporary files
tmp/
temp/
*.tmp
*.temp

# Azure
.azure/

# Terraform
*.tfstate
*.tfstate.*
.terraform/
.terraform.lock.hcl

# Secrets
secrets/
certificates/
*.pem
*.key
*.crt

# Conversation history
conversations/
chat_history/
user_data/
"@
    
    Set-Content -Path ".gitignore" -Value $gitignore
    Write-Host "✅ .gitignore created" -ForegroundColor Green
}

# Create backend requirements.txt
function Create-BackendRequirements {
    Write-Step "Creating backend requirements.txt..."
    
    $requirements = @"
fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0
python-multipart==0.0.6
openai-whisper==20231117
TTS==0.21.3
torch==2.1.0
torchvision==0.16.0
torchaudio==2.1.0
opencv-python==4.8.1.78
Pillow==10.1.0
requests==2.31.0
python-dotenv==1.0.0
azure-storage-blob==12.19.0
azure-cognitiveservices-speech==1.34.0
redis==5.0.1
celery==5.3.4
sqlalchemy==2.0.23
aiosqlite==0.19.0
httpx==0.25.2
numpy==1.24.3
pydantic==2.5.0
pydantic-settings==2.1.0
pytest==7.4.3
pytest-asyncio==0.21.1
black==23.11.0
flake8==6.1.0
alembic==1.13.1
psycopg2-binary==2.9.9
"@
    
    Set-Content -Path "backend/requirements.txt" -Value $requirements
    Write-Host "✅ Backend requirements.txt created" -ForegroundColor Green
}

# Create basic FastAPI main.py
function Create-BackendMain {
    Write-Step "Creating backend main API file..."
    
    $mainPy = @"
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Jarvis AI Assistant", 
    version="1.0.0",
    description="Personal AI Assistant with multimodal capabilities"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Jarvis AI Assistant API", "status": "running"}

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "jarvis-backend",
        "version": "1.0.0"
    }

@app.post("/api/chat")
async def chat_endpoint(message: dict):
    # Placeholder for chat functionality
    return {
        "response": f"Echo: {message.get('content', 'No message')}",
        "timestamp": "2025-07-02"
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
"@
    
    New-Item -ItemType Directory -Path "backend/api" -Force | Out-Null
    Set-Content -Path "backend/api/main.py" -Value $mainPy
    Set-Content -Path "backend/api/__init__.py" -Value ""
    Write-Host "✅ Backend API main.py created" -ForegroundColor Green
}

# Create frontend package.json
function Create-FrontendPackage {
    Write-Step "Creating frontend package.json..."
    
    $packageJson = @'
{
  "name": "jarvis-ai-frontend",
  "version": "1.0.0",
  "description": "Frontend for Jarvis AI Assistant",
  "main": "src/index.js",
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "axios": "^1.6.0",
    "socket.io-client": "^4.7.0",
    "styled-components": "^6.1.0",
    "lucide-react": "^0.300.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "typescript": "^5.3.0"
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
'@
    
    Set-Content -Path "frontend/package.json" -Value $packageJson
    Write-Host "✅ Frontend package.json created" -ForegroundColor Green
}

# Create basic React App.js
function Create-FrontendApp {
    Write-Step "Creating frontend React app..."
    
    $appJs = @"
import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [message, setMessage] = useState('');
  const [chat, setChat] = useState([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    // Test backend connection
    fetch('/api/health')
      .then(res => res.json())
      .then(data => {
        setConnected(data.status === 'healthy');
      })
      .catch(() => setConnected(false));
  }, []);

  const sendMessage = async () => {
    if (!message.trim()) return;

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content: message }),
      });
      
      const data = await response.json();
      setChat(prev => [...prev, 
        { type: 'user', content: message },
        { type: 'assistant', content: data.response }
      ]);
      setMessage('');
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🤖 Jarvis AI Assistant</h1>
        <div className="status">
          Status: {connected ? '✅ Connected' : '❌ Disconnected'}
        </div>
      </header>
      
      <main className="chat-container">
        <div className="chat-messages">
          {chat.map((msg, index) => (
            <div key={index} className={`message ${msg.type}`}>
              <strong>{msg.type === 'user' ? 'You' : 'Jarvis'}:</strong> {msg.content}
            </div>
          ))}
        </div>
        
        <div className="chat-input">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Type your message..."
          />
          <button onClick={sendMessage}>Send</button>
        </div>
      </main>
    </div>
  );
}

export default App;
"@
    
    $appCss = @"
.App {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

.App-header {
  text-align: center;
  margin-bottom: 30px;
}

.App-header h1 {
  color: #333;
  margin-bottom: 10px;
}

.status {
  font-size: 14px;
  margin-bottom: 20px;
}

.chat-container {
  border: 1px solid #ddd;
  border-radius: 8px;
  height: 500px;
  display: flex;
  flex-direction: column;
}

.chat-messages {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background-color: #f9f9f9;
}

.message {
  margin-bottom: 15px;
  padding: 10px;
  border-radius: 5px;
}

.message.user {
  background-color: #e3f2fd;
  text-align: right;
}

.message.assistant {
  background-color: #fff;
  text-align: left;
}

.chat-input {
  display: flex;
  padding: 20px;
  border-top: 1px solid #ddd;
}

.chat-input input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-right: 10px;
}

.chat-input button {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.chat-input button:hover {
  background-color: #0056b3;
}
"@
    
    $indexJs = @"
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
"@
    
    $indexHtml = @"
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="Jarvis AI Assistant" />
    <title>Jarvis AI Assistant</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
"@
    
    Set-Content -Path "frontend/src/App.js" -Value $appJs
    Set-Content -Path "frontend/src/App.css" -Value $appCss
    Set-Content -Path "frontend/src/index.js" -Value $indexJs
    Set-Content -Path "frontend/public/index.html" -Value $indexHtml
    Write-Host "✅ Frontend React app created" -ForegroundColor Green
}

# Create GitHub workflows
function Create-GitHubWorkflows {
    Write-Step "Creating GitHub Actions workflows..."
    
    $ciWorkflow = @'
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
    
    - name: Test backend
      run: |
        cd backend
        python -m pytest tests/ -v || echo "No tests yet"
  
  test-frontend:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '20'
    
    - name: Install dependencies
      run: |
        cd frontend
        npm install
    
    - name: Build frontend
      run: |
        cd frontend
        npm run build
'@
    
    Set-Content -Path ".github/workflows/ci.yml" -Value $ciWorkflow
    Write-Host "✅ GitHub Actions CI workflow created" -ForegroundColor Green
}

# Create proper Docker files
function Create-DockerFiles {
    Write-Step "Creating Docker files..."
    
    # Move existing backend dockerfile to proper location
    if (Test-Path "backend/dockerfile/backend.dockerfile") {
        Move-Item "backend/dockerfile/backend.dockerfile" "backend/Dockerfile" -Force
        Remove-Item "backend/dockerfile" -Recurse -Force
    }
    
    # Create frontend Dockerfile
    $frontendDockerfile = @"
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
"@
    
    Set-Content -Path "frontend/Dockerfile" -Value $frontendDockerfile
    
    # Create nginx.conf for frontend
    $nginxConf = @"
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    server {
        listen       80;
        server_name  localhost;

        location / {
            root   /usr/share/nginx/html;
            index  index.html index.htm;
            try_files `$uri `$uri/ /index.html;
        }

        location /api {
            proxy_pass http://backend:8000;
            proxy_set_header Host `$host;
            proxy_set_header X-Real-IP `$remote_addr;
        }
    }
}
"@
    
    Set-Content -Path "frontend/nginx.conf" -Value $nginxConf
    Write-Host "✅ Docker files created" -ForegroundColor Green
}

# Create updated README
function Create-UpdatedReadme {
    Write-Step "Creating updated README.md..."
    
    $readme = @"
# 🤖 Jarvis AI Assistant

A personal AI assistant inspired by Tony Stark's JARVIS, featuring self-programming capabilities and multimodal interaction.

## 🚀 Features

- 🧠 **Local LLM Processing** - Privacy-first AI with Ollama
- 🗣️ **Voice Interaction** - Speech-to-text and text-to-speech
- 👁️ **Computer Vision** - Image analysis and camera integration
- 🏠 **Smart Home Integration** - Control IoT devices
- ☁️ **Cloud Sync** - OneDrive and Azure integration
- 📱 **Cross-Platform** - Web, mobile, and desktop access
- 🔄 **Self-Improvement** - Learning from interactions

## 🏗️ Architecture

- **Backend**: FastAPI + Python
- **Frontend**: React + TypeScript
- **AI**: Ollama (local) + OpenAI/Claude (fallback)
- **Voice**: Whisper + TTS
- **Vision**: LLaVA + Azure Vision
- **Storage**: OneDrive + Azure Storage
- **Deployment**: Docker + Azure Container Instances

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker
- Azure CLI (for cloud deployment)

### Local Development

1. **Clone the repository**
   ``````bash
   git clone https://github.com/yourusername/jarvis-ai-assistant.git
   cd jarvis-ai-assistant
   ``````

2. **Set up environment**
   ``````powershell
   # Copy environment template
   cp .env.example .env
   # Edit .env with your API keys
   ``````

3. **Start with Docker Compose**
   ``````bash
   docker-compose up -d
   ``````

4. **Or run manually**
   ``````bash
   # Backend
   cd backend
   pip install -r requirements.txt
   python -m uvicorn api.main:app --reload
   
   # Frontend (new terminal)
   cd frontend
   npm install
   npm start
   ``````

5. **Install Ollama and models**
   ``````bash
   # Install Ollama
   ollama serve
   
   # Pull models
   ollama pull llama3.1:8b
   ``````

### Cloud Deployment

1. **Set up Azure resources**
   ``````powershell
   # Login to Azure
   az login
   
   # Run setup script
   python scripts/setup/azure_setup.py
   ``````

2. **Deploy infrastructure**
   ``````powershell
   # Deploy with script
   .\scripts\deployment\deploy.ps1 -Environment production -Force
   ``````

## 📁 Project Structure

``````
jarvis-ai-assistant/
├── backend/                 # FastAPI backend
│   ├── api/                # API endpoints
│   ├── services/           # Business logic
│   └── core/               # Core functionality
├── frontend/               # React frontend
├── infrastructure/         # Docker & Terraform
├── scripts/               # Setup & deployment scripts
├── configs/               # Environment configurations
└── docs/                  # Documentation
``````

## 🔧 Development

### Backend
- FastAPI with async support
- Pydantic models for data validation
- SQLAlchemy for database ORM
- Pytest for testing

### Frontend
- React 18 with hooks
- Styled components for UI
- Axios for API calls
- WebSocket for real-time communication

## 📚 Documentation

- [Setup Guide](docs/SETUP.md)
- [API Documentation](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Architecture Overview](docs/architecture/overview.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by Tony Stark's JARVIS from Marvel
- Built with modern AI and web technologies
- Community-driven development

---

**Note**: This is a personal AI assistant project. Ensure you comply with all applicable laws and service terms when using AI APIs and services.
"@
    
    Set-Content -Path "README.md" -Value $readme -Force
    Write-Host "✅ README.md updated" -ForegroundColor Green
}

# Main execution
if ($CreateFiles -or $All) {
    Write-Host "🚀 Completing Jarvis AI repository setup..." -ForegroundColor Cyan
    
    Create-MissingDirectories
    Create-GitIgnore
    Create-BackendRequirements
    Create-BackendMain
    Create-FrontendPackage
    Create-FrontendApp
    Create-GitHubWorkflows
    Create-DockerFiles
    Create-UpdatedReadme
    
    Write-Host "`n🎉 Repository setup completed!" -ForegroundColor Green
    Write-Host "`nNext steps:" -ForegroundColor Yellow
    Write-Host "1. Copy .env.example to .env and add your API keys" -ForegroundColor White
    Write-Host "2. Run: docker-compose up -d" -ForegroundColor White
    Write-Host "3. Install Ollama: ollama pull llama3.1:8b" -ForegroundColor White
    Write-Host "4. Visit: http://localhost:3000" -ForegroundColor White
}

if ($All) {
    Write-Host "`n🔧 Installing dependencies..." -ForegroundColor Cyan
    
    # Install backend dependencies
    if (Test-Path "backend/requirements.txt") {
        Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
        Set-Location backend
        pip install -r requirements.txt
        Set-Location ..
    }
    
    # Install frontend dependencies
    if (Test-Path "frontend/package.json") {
        Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
        Set-Location frontend
        npm install
        Set-Location ..
    }
    
    Write-Host "✅ Dependencies installed!" -ForegroundColor Green
}