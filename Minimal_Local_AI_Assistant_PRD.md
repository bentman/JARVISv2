# Product Requirements Document (PRD)
# Minimal Marketable Local-First AI Assistant

**Version:** 1.0
**Date:** September 18, 2025
**Project Name:** LocalAI Assistant

## 1. Product Overview

### 1.1 Purpose
Deliver a minimal marketable local-first AI assistant that runs entirely on user hardware with automatic capability detection, voice interaction, and privacy-first principles. The product must support chat, reasoning, and coding tasks while maintaining all data processing locally by default.

### 1.2 Vision
Create the simplest possible local AI assistant that provides immediate value to users while establishing a foundation for future enhancements. The assistant should work seamlessly across different hardware configurations (CPU, GPU, NPU) with zero setup complexity.

### 1.3 Goals
1. **Local-First Privacy**: All data processing occurs locally by default with no cloud dependencies
2. **Hardware Adaptive**: Automatically detects and optimizes for available hardware capabilities
3. **Voice Enabled**: Full voice interaction with wake word detection
4. **Cross-Platform**: Works on Windows, macOS, and Linux desktops
5. **Minimal Setup**: One-command installation and deployment
6. **Resource Efficient**: Optimized for consumer hardware with intelligent resource management

## 2. Key Features

### 2.1 Core Features (MMP - Minimal Marketable Product)
- **Hardware Detection**: Automatic CPU/GPU/NPU capability detection
- **Model Selection**: Dynamic model loading based on hardware profile
- **Voice Interface**: Wake word detection, STT, TTS
- **Chat Interface**: Text-based interaction with streaming responses
- **Local Backend**: Containerized services for coordination
- **Memory Persistence**: Conversation history storage
- **Privacy Controls**: Data classification and local processing enforcement

### 2.2 Hardware Profiles
- **Light (CPU Only)**: 3-7B parameter models for basic tasks
- **Medium (GPU/NPU)**: 7-13B parameter models for reasoning/coding
- **Heavy (High-end GPU)**: 13B+ parameter models for complex tasks

### 2.3 Interaction Modes
- **Voice Mode**: Hands-free interaction with wake word activation
- **Text Mode**: Traditional chat interface with markdown support
- **Hybrid Mode**: Seamless switching between voice and text

## 3. Technical Architecture

### 3.1 Overall Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    Desktop Application                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Voice     │  │   Chat UI   │  │  Hardware Detection │  │
│  │ Interface   │  │             │  │                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    Backend Services                         │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Model     │  │  Memory     │  │   Privacy &         │  │
│  │  Routing    │  │  Storage    │  │  Security           │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                   AI Model Execution                        │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   LLM       │  │   Voice     │  │  Hardware-          │  │
│  │  Inference  │  │  Models     │  │  Optimized          │  │
│  └─────────────┘  └─────────────┘  │  Execution          │  │
│                                   └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Backend Services (Docker Container Stack)
1. **Core Assistant Service** (FastAPI)
   - REST API for frontend communication
   - Request routing and orchestration
   - Conversation management

2. **Model Router Service**
   - Hardware capability detection
   - Model selection based on profile
   - Resource allocation management

3. **Memory Service**
   - SQLite-based conversation storage
   - Vector embedding for semantic search
   - Data encryption at rest

4. **Voice Service**
   - Wake word detection (Porcupine)
   - Speech-to-text (Whisper.cpp)
   - Text-to-speech (Piper)

5. **Privacy Service**
   - Data classification and redaction
   - Local processing enforcement
   - Access control management

### 3.3 Frontend Application (Tauri + React)
- **Framework**: Tauri v2.0+ with React 18+
- **UI Library**: Tailwind CSS with Radix UI components
- **State Management**: Zustand for lightweight state management
- **Voice Integration**: Web Audio API with native microphone access
- **Cross-Platform**: Windows, macOS, Linux native applications

## 4. Technology Stack

### 4.1 Backend Technologies
- **Primary Framework**: FastAPI (Python 3.11+)
- **Containerization**: Docker Compose v2.20+
- **Database**: SQLite 3.42+ with SQLModel
- **AI Inference**: ONNX Runtime 1.16+ / llama.cpp
- **Vector Storage**: LanceDB 0.5+
- **Task Queue**: None (synchronous for MVP)

### 4.2 Frontend Technologies
- **Desktop Framework**: Tauri 2.0+
- **UI Framework**: React 18.2+
- **Styling**: Tailwind CSS 3.3+
- **Components**: Radix UI 1.0+
- **State Management**: Zustand 4.4+

### 4.3 AI Models
- **Small Models** (CPU): Llama 3.2 (3B) - GGUF Q4_K_M quantized
- **Medium Models** (GPU): Mistral 7B Instruct - GGUF Q5_K_M quantized
- **Large Models** (High-end GPU): Mixtral 8x7B - GGUF Q4_K_M quantized
- **Voice Models**: 
  - STT: Whisper Small (GGML quantized)
  - TTS: Piper TTS voices
  - Wake Word: Porcupine 3.0+

### 4.4 Security Technologies
- **Encryption**: libsodium via PyNaCl 1.5+
- **Authentication**: None for MVP (local only)
- **Data Protection**: AES-256 for data at rest
- **Communication**: TLS 1.3 for container communication

## 5. Implementation Requirements

### 5.1 Hardware Detection
```python
interface HardwareCapability {
  cpu: {
    cores: number;
    architecture: "x64" | "arm64";
    features: string[];
  };
  gpu: {
    vendor: "nvidia" | "amd" | "intel" | "apple";
    memory_gb: number;
    compute_capability?: string;
  };
  memory_gb: number;
  profile: "light" | "medium" | "heavy";
}
```

### 5.2 API Specifications

#### Core Assistant API
```
POST /api/chat
{
  "message": string,
  "mode": "chat" | "coding" | "reasoning",
  "stream": boolean
}

Response (streaming):
data: {"type": "text", "content": "Hello"}
data: {"type": "thinking", "content": "Processing your request"}
data: {"type": "response", "content": "How can I help you today?"}
data: {"type": "done"}

GET /api/conversations
Response:
{
  "conversations": [
    {
      "id": "conv_123",
      "title": "Project Discussion",
      "created_at": "2025-09-18T10:30:00Z",
      "updated_at": "2025-09-18T10:35:00Z"
    }
  ]
}
```

#### Hardware Detection API
```
GET /api/hardware
Response:
{
  "profile": "medium",
  "capabilities": {
    "cpu_cores": 8,
    "gpu_memory_gb": 12,
    "total_memory_gb": 32,
    "detected_hardware": ["nvidia_gpu"]
  },
  "selected_model": "mistral-7b-instruct"
}
```

### 5.3 Data Models

#### Conversation Model
```json
{
  "id": "conv_abc123",
  "title": "Meeting Notes",
  "created_at": "2025-09-18T10:30:00Z",
  "updated_at": "2025-09-18T10:35:00Z",
  "messages": [
    {
      "id": "msg_xyz789",
      "role": "user" | "assistant",
      "content": "Hello, how can you help me?",
      "timestamp": "2025-09-18T10:30:01Z",
      "tokens": 8,
      "mode": "chat"
    }
  ]
}
```

#### System Configuration
```json
{
  "privacy_level": "local_only",
  "voice_enabled": true,
  "wake_word": "assistant",
  "hardware_profile": "auto",
  "model_preference": "balanced",
  "auto_delete_days": 30
}
```

## 6. User Experience

### 6.1 Installation Process
1. **Download**: Single installer for target platform
2. **Hardware Detection**: Automatic profile selection
3. **Model Download**: Background download of appropriate models
4. **First Launch**: Quick tutorial and settings configuration

### 6.2 Main Interface
```
┌─────────────────────────────────────────────────────────────┐
│ [Logo] Local AI Assistant       [Settings] [Help]          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ┌─────────────────┐  ┌──────────────────┐  ┌─────────────┐ │
│ │ Hardware Status │  │ Current Model    │  │ Privacy     │ │
│ │ ● GPU: 12GB     │  │ 🧠 Mistral 7B   │  │ 🔒 Local    │ │
│ │ ● Profile: Med  │  │ ⚡ 245ms latency │  │ Only        │ │
│ └─────────────────┘  └──────────────────┘  └─────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 🎤 Voice Active           [Chat|Code|Reason] [Settings] │ │
│ │                                                         │ │
│ │ > "Help me write a Python function..."                  │ │
│ │                                                         │ │
│ │ ✓ Processing with Mistral 7B (privacy mode)             │ │
│ │ ⏱️ Estimated completion: 8 seconds                       │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Assistant:                                              │ │
│ │ I'll help you write a Python function. Could you tell   │ │
│ │ me what functionality you need?                         │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ [📎] [😊] [🎤] Type your message...  [Send]             │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 6.3 Voice Interaction Flow
1. **Wake Word**: "Hey assistant" activates voice mode
2. **Listening**: Microphone input captured and processed
3. **STT**: Speech converted to text using Whisper
4. **Processing**: Request processed by selected model
5. **TTS**: Response converted to speech using Piper
6. **Output**: Audio response played through speakers

## 7. Privacy & Security

### 7.1 Data Handling Principles
- **Local by Default**: All data processed locally unless explicitly permitted
- **No Telemetry**: Zero data collection or usage tracking
- **Encrypted Storage**: All conversation data encrypted at rest
- **Minimal Permissions**: Only necessary system permissions requested

### 7.2 Data Classification
- **Never Leave Device**: Financial, medical, personal identification
- **Local Processing Only**: Work documents, private conversations
- **Allow Cloud (Optional)**: Public information, non-sensitive data

### 7.3 Security Implementation
- **End-to-End Encryption**: Conversation data encrypted with AES-256
- **Model Integrity**: Cryptographic verification of AI models
- **Secure Communication**: TLS 1.3 between all components
- **Access Controls**: File system permissions for sensitive data

## 8. Performance Requirements

### 8.1 Response Times
- **Light Profile**: < 5 seconds for typical queries
- **Medium Profile**: < 3 seconds for typical queries
- **Heavy Profile**: < 2 seconds for typical queries

### 8.2 Resource Usage
- **CPU Usage**: < 80% during active processing
- **Memory Usage**: < 8GB for medium profile
- **Disk Space**: < 20GB for all models and data
- **Battery Impact**: < 10% additional drain on mobile devices

### 8.3 Scalability
- **Concurrent Users**: 1 user per installation (local only)
- **Conversation History**: 10,000+ messages per user
- **Model Switching**: < 2 seconds context switching

## 9. Deployment & Distribution

### 9.1 Installation Methods
- **Windows**: NSIS installer with bundled Docker
- **macOS**: DMG package with bundled Docker
- **Linux**: AppImage with system Docker dependency

### 9.2 System Requirements
**Minimum (Light Profile)**:
- CPU: Modern dual-core processor
- RAM: 8GB
- Disk: 10GB available space
- OS: Windows 10+, macOS 12+, Ubuntu 20.04+

**Recommended (Medium Profile)**:
- CPU: 4+ cores
- GPU: 4GB+ VRAM (NVIDIA/AMD/Intel)
- RAM: 16GB
- Disk: 20GB available space

**Optimal (Heavy Profile)**:
- CPU: 8+ cores
- GPU: 8GB+ VRAM (NVIDIA RTX 3070+/AMD RX 6700+/Intel Arc)
- RAM: 32GB
- Disk: 50GB available space

### 9.3 Update Strategy
- **Model Updates**: Background downloading with version management
- **Application Updates**: Tauri built-in updater with delta updates
- **Security Patches**: Automatic notification for critical updates

## 10. Success Metrics

### 10.1 Technical Metrics
- **Installation Success**: > 95% successful installations
- **First Interaction**: < 30 seconds to first assistant response
- **Voice Recognition**: > 90% accuracy in quiet environments
- **System Availability**: 99.5% uptime after installation

### 10.2 User Experience Metrics
- **Task Completion**: > 80% of basic tasks completed successfully
- **User Satisfaction**: > 4.0/5.0 rating in user surveys
- **Privacy Confidence**: > 90% of users report high privacy confidence
- **Retention**: > 70% weekly active users

### 10.3 Performance Benchmarks
- **Model Load Time**: < 10 seconds for profile-appropriate models
- **Response Latency**: Meets profile-specific targets
- **Resource Efficiency**: < 20% battery drain during 1-hour session

## 11. Implementation Roadmap

### Phase 1: Core Foundation (Weeks 1-4)
- [ ] Backend service containerization with FastAPI
- [ ] Hardware detection and model selection logic
- [ ] Basic chat interface with Tauri/React
- [ ] SQLite conversation storage implementation
- [ ] Docker Compose deployment configuration

### Phase 2: Voice Integration (Weeks 5-8)
- [ ] Wake word detection with Porcupine
- [ ] Whisper STT integration
- [ ] Piper TTS implementation
- [ ] Voice interface in desktop application
- [ ] Streaming response handling

### Phase 3: Privacy & polish (Weeks 9-12)
- [ ] Data encryption implementation
- [ ] Privacy controls and settings
- [ ] Cross-platform packaging and distribution
- [ ] Performance optimization and testing
- [ ] Documentation and user guides

## 12. Risk Assessment

### 12.1 Technical Risks
- **Model Performance**: Variability in local inference performance
  - *Mitigation*: Comprehensive benchmarking and profile optimization
- **Hardware Compatibility**: Issues with diverse GPU configurations
  - *Mitigation*: Extensive testing on common hardware combinations
- **Voice Recognition**: Accuracy issues in noisy environments
  - *Mitigation*: Clear user expectations and environment guidance

### 12.2 Market Risks
- **Competition**: Established cloud-based assistants
  - *Mitigation*: Emphasize privacy and local control differentiation
- **User Adoption**: Resistance to local-only model
  - *Mitigation*: Clear value proposition and transparent benefits

## 13. Conclusion

This PRD defines a minimal marketable product for a local-first AI assistant that prioritizes user privacy while delivering core AI capabilities. The product focuses on essential features that provide immediate value:
- Zero-setup local AI processing
- Automatic hardware optimization
- Voice and text interaction
- Persistent conversation memory
- Strong privacy guarantees

By focusing on these core capabilities, the product establishes a foundation that can be enhanced with additional features in future releases while immediately addressing the growing demand for privacy-conscious AI tools.