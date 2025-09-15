# Hybrid Assistant Client PRD

### AI Agent Instruction: Environment Isolation
- **Terminal**: Use -noprofile for Windows PowerShell (`powershell -noprofile`), `-c` for PowerShell or disable shell initialization (`bash +l` or `zsh -f`) on Linux/macOS to prevent profile interference and ensure project-specific paths are used.
- **Environment Isolation**: Create and activate a .venv in project root for all Python dependencies:
  ```bash
  python -m venv .venv
  .venv\Scripts\activate  # Windows (or source .venv/bin/activate on POSIX)
  ```
  Must activate .venv for all Python operations (installing dependencies, running scripts) to avoid overwriting global Python requirements and ensure project isolation.
- **Python**: Use separate .venv for \backend, \frontend, etc - but ensure consistency of apps and dependancies. Always activate in appropriate .venv for work and update pip to avoid errors. Maintain appropriate requirements.txt for all python .venv environments. Check if available, update/modify as required, install and add if needed.
- **Cargo/Rust**: Use latest stable TOOLCHAIN in rust-toolchain.toml to ensure consistency across machines.
- **Project Tracking**: Maintain a dedicated `project_progress.md` file to track implementation phases, with checklists for completed tasks and course corrections. Update after each session to ensure traction across conversations. This tracking ensures consistent progress and reduces handbook-off errors.

- Review project_progress.md for current status before starting work
- Check off completed items and note any unexpected requirements
- Document blockers, decisions, and pivot points for future reference

## Product Overview
A privacy-first, offline-capable desktop AI assistant that automatically selects and runs optimized models based on device hardware. Supports text chat, voice conversation, cloud hybrid routing, and intelligent memory management. Cross-platform (Windows, macOS, Linux) with sub-2s response times.

## Core Objectives
- Zero-config local AI assistant across hardware tiers
- Privacy-focused (local-first, opt-in telemetry)
- End-to-end multimodal (text, voice, hybrid memory)
- Scalable to 70%+ daily active usage

## Target Users
- Developers seeking local coding assistance
- Power users needing offline analysis tools
- Privacy-conscious individuals wanting control over data

## Technical Architecture

### Platform Stack
- **Desktop Framework**: Tauri >=2.0 (Rust >=1.70 backend + React >=18 + TypeScript + Tailwind CSS frontend)
- **AI Stack**: llama.cpp >=0.3 (GGUF models), ONNX Runtime >=1.18 (NPU/GPU acceleration)
- **Speech Stack**: Kokoro >=v0.19 TTS (ONNX), faster-whisper STT (C++ implementation)
- **Data Layer**: SQLite (conversations), RocksDB (embeddings/vectors), Qdrant-lite (vector retrieval), Redis (short-term cache)

### Hardware Profiles & Model Selection
Hardware auto-detection assigns optimal models:

| Tier | Req. Specs | Text Model | Speech Support | Use Case |
|------|------------|------------|---------------|----------|
| Heavy | ≥32GB RAM, 8GB+ VRAM | llama-3.3-70b-instruct-q4_K_M | Full (Kokoro + Whisper) | Complex analysis, coding |
| Medium | ≥16GB RAM, 4GB+ VRAM | qwen2.5-32b-instruct-q5_K_M | Full | Chat, light coding |
| Light | ≥8GB RAM | phi-3.5-mini-instruct-q4_K_M | Voice-only (Kokoro) | Basic conversation |
| NPU Opt | ≥8GB RAM + NPU | ONNX phi-3.5-mini + QNN Kokoro | Full accelerated | Efficient on mobile/ARM |
| API Only | ≥4GB RAM | Cloud models | N/A | Fallback mode |

### Voice Capabilities
- **TTS**: Kokoro (50MB ONNX model, natural speech, cross-platform)
- **STT**: faster-whisper (quantized Whisper, low-latency transcription)
- **Conversation Mode**: Voice input/output for hands-free interaction
- **Hardware Support**: DirectML (Intel/AMD NPU), CoreML (Apple ANE), QNN (Qualcomm Hexagon ARM64)

## Core Features

### Conversation Modes
```rust
enum ConversationMode {
  Assistant = "assistant",  // General queries
  Coding = "coding",       // Code assistance
  Creative = "creative",   // Ideation/writing
  Analyzer = "analyzer"    // Document analysis
}
```
Modes trigger model selection, temperature adjustments, and routing preferences.

### Intelligent Assistant Modes
- **Chat**: Markdown-rendered conversations with syntax highlighting
- **Coding**: Code generation, refactoring, debugging assistance
- **Creative**: Writing, ideation support
- **Analyzer**: Document Q&A, summarization
- **Conversation**: Voice-driven continuous dialogue

### Aggregate Search (Research Mode)
Unified query across:
- Local conversation memory (SQLite)
- Vector embeddings (Qdrant-lite, semantic retrieval)
- Search providers (Bing, Google, Tavily)
- Cloud AI providers (if enabled)
Results ranked by relevance with citations, summaries, export to Markdown.

### Memory & Knowledge System
- **Short-term Cache**: Redis for frequent queries and context
- **Vector Storage**: Embeddings in RocksDB/Qdrant for semantic retrieval
- **Long-term History**: SQLite with tagging and filtering
- **Memory Sync**: Future-ready stubs for cross-device synchronization
- **Export**: Markdown conversation histories with tagging/search

### Intelligent Routing
- **Local-First Logic**: Escalate to cloud only when necessary (context limits, capabilities)
- **Routing Function**:
  ```rust
  fn should_escalate(context: &Context) -> bool {
    context.tokens > local_model.context_limit ||
    context.requires_capability_not_supported_by_local
  }
  ```
- **Budget Management**: Token tracking and provider failover
- **Provider Support**: Primary support for OpenAI, Anthropic, GoogleAI, xAI (Grok). Extensible to additional optimized alternates such as Hugging Face Inference API, Replicate, Together AI, and Cohere. Users can configure up to 4 active providers per conversation mode, with fallback priority and budget constraints.

### Multimodal UI/UX
- **Chat Interface**: Streaming responses, message threading, code blocks
- **Settings Panel**: Model overrides, temperature, privacy toggles
- **Status Indicators**: Hardware tier badges, NPU icons, routing state, Redis memory usage
- **System Tray**: Quick access, model loading notifications
- **Research Panel**: Aggregate search interface with source indicators

## Implementation Details

### Hardware Detection Module
Detects and profiles:
- **CPU/GPU**: Cores, RAM via sysinfo/wmi crates
- **Accelerators**: Vulkan/CLBlast for GPU, NPU via vendor SDKs (DirectML, CoreML, QNN including Qualcomm Hexagon ARM64)
- **Benchmarking**: Automatic scoring for tier assignment

### Model Management System
- **Download Priority**: Essential models cached locally per profile
- **Runtime Selection**: GGUF for heavy CPU/GPU, ONNX for NPU acceleration
- **Validation**: Runtime capability checks before model selection
- **Storage**: `~/.hybrid-assistant/models/cache/` with metadata

### Model Profiles & Defaults
Hardware auto-detection assigns models (updated versions shown below):

profiles:
  heavy:
    min_ram: 32GB+
    gpu_vram: 8GB+
    model: "llama-3.3-70b-instruct-q4_K_M.gguf"
    context_limit: 8192
    capabilities: ["reasoning", "coding", "analysis"]

  medium:
    min_ram: 16GB+
    gpu_vram: 4GB+
    model: "qwen2.5-32b-instruct-q5_K_M.gguf"
    context_limit: 4096
    capabilities: ["conversation", "light_coding"]

  light:
    min_ram: 8GB+
    model: "phi-3.5-mini-instruct-q4_K_M.gguf"
    context_limit: 2048
    capabilities: ["basic_conversation"]

  npu_optimized:
    min_ram: 8GB+
    npu_required: true
    model: "onnx://phi-3.5-mini-npu.onnx"
    context_limit: 2048
    capabilities: ["basic_conversation", "low-power"]

  api_only:
    min_ram: 4GB
    model: null
    backend_required: true

### Backend Interfaces (Rust Traits)
```rust
trait AIService {
    fn infer_text(&self, prompt: &str) -> Result<String>;
    fn infer_voice(&self, audio: &[f32]) -> Result<String>;  // STT
}

trait SpeechService {
    fn synthesize(&self, text: &str) -> Result<Vec<f32>>;  // TTS
    fn transcribe(&self, audio: &[f32]) -> Result<String>; // STT
}

trait MemoryManager {
    async fn store_vector(&self, embedding: Vec<f32>, content: String);
    async fn search_vectors(&self, query: Vec<f32>) -> Vec<Snippet>;
}

trait RoutingEngine {
    fn should_escalate(&self, context: &Context) -> bool;
    fn select_backend(&self, task: &Task) -> Backend;
}

trait MemorySync {
    async fn push_snippets(&self, snippets: Vec<Snippet>);
    async fn pull_updates(&self) -> Vec<Snippet>;
}

trait BudgetManager {
    fn check_allowance(&self) -> Credits;
    fn track_usage(&self, tokens: u32, route: Route);
}

trait ModelRuntime {
    fn load(&self, path: &Path) -> Result<Model>;
    fn infer(&self, input: &Tensor) -> Result<Output>;
}
```

### Configuration & Feature Flags
```json
{
  "hardware": { "auto_detect": true, "npu_preference": ["directml", "coreml", "qnn"] },
  "models": { "directory": "~/.hybrid-assistant", "auto_download": true },
  "features": { "voice_mode": true, "aggregate_search": true, "memory_sync": false },
  "routing": { "fallback": "local_first", "providers": [] },
  "redis": { "enabled": true, "max_memory": "256mb" }
}
```

### Quick Start & Onboarding
1. Hardware detection + tier assignment
2. Download essential model (~2-5GB)
3. Voice calibration for STT/TTS (if enabled)
4. First text/voice query within 30s

## Operational Requirements

### Performance Targets
- **Startup**: <3s with cached models
- **Inference**: <500ms first token, <2s full response (medium tier)
- **Memory**: <8GB working set for light models
- **Cache**: Redis hit rate >80% for repeat queries
- **Stability**: 99.9% uptime, graceful degradation

### Testing Strategy
- **Unit**: Hardware detection, model loading, routing logic, speech integration
- **Integration**: End-to-end chats, voice conversations, aggregate search, provider failover
- **Performance**: Latency benchmarks, memory/caching pressure tests
- **Compatibility**: Across supported OS/hardware combinations

### Security & Privacy
- **Local Only**: All data stays device-local by default
- **Encryption**: Optional for exported conversations and Redis cache
- **Telemetry**: Anonymous usage stats (opt-in only)
- **Sandboxing**: Models run in isolated processes

### Build & Deployment
- **Commands**: `npm run tauri dev`, `cargo test`, `npm run tauri build`
- **Distribution**: Single binary with embedded models/cache
- **Updates**: Auto-update framework for model definitions

### Risks & Mitigations
- **Quantization Compatibility**: Vendor SDK testing, fallback chains
- **Hardware Diversity**: Extensive profiling, OpenGL/Vulkan abstraction
- **Memory Pressure**: Swap detection, model unloading, cache limits, warning thresholds
- **Speech Accuracy**: Quality validation, user correction UI

### Success Metrics
- **Adoption**: 70% daily usage retention
- **Performance**: >90% queries under 2s
- **Completion**: 95% successful model downloads
- **Satisfaction**: High feedback on hardware utilization and privacy

## Development Environment Setup
This project maintains a consistent, reproducible development environment to ensure quick setup for contributors and smooth CI/CD processes.

### Prerequisites
- **Rust**: >=1.70 (install via [rustup](https://rustup.rs/))
- **Node.js**: >=18 (install via [nvm](https://github.com/nvm-sh/nvm) or official installer)
- **Python**: >=3.8 (for tooling/scripts, installed via venv)
- **System**: 16GB RAM minimum, SSD storage

### End Goal is to give end users a 'One-Time Setup'
1. Clone the repository: `git clone https://github.com/bentman/JARVISv2.git && cd JARVISv2`
2. Activate virtual environment (see above)
3. Install Rust: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh` (Linux/macOS) or run rustup-init.exe (Windows)
4. Install Node.js dependencies: `npm install`
5. Install Tauri CLI: `cargo install tauri-cli`
6. Build and run: `npm run tauri dev`

### Quick Start Workflow
Clone → Activate venv → Rustup → npm install → npm run tauri dev (target: <5 min setup time).
