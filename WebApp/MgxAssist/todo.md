# Hybrid Local-First AI Architecture Prototype - MVP Todo

## Core Files to Create (Max 8 files limit)

### 1. **src/pages/Index.tsx** - Main Dashboard Interface
- Hardware capability detection simulation
- Mode switcher (Assistant/Coding/Search)
- Real-time route visualization
- Privacy controls panel
- Main chat interface with voice/text input

### 2. **src/components/HardwareDetection.tsx** - Capability Detection
- NPU/GPU/CPU profile simulation (heavy/medium/light)
- Hardware status indicators
- Capability registration simulation

### 3. **src/components/RoutingEngine.tsx** - Route Visualization
- Real-time routing decisions (Local → Cloud-Small → Cloud-Large)
- Policy engine simulation
- Route decision factors display

### 4. **src/components/BudgetDashboard.tsx** - Budget Governance
- Monthly/weekly caps tracking
- Cost telemetry visualization
- Soft/hard limit warnings
- Budget burn rate charts

### 5. **src/components/MemoryStore.tsx** - Memory & Retrieval
- Versioned snippets visualization
- Search capabilities simulation
- Memory access controls
- Snippet metadata display

### 6. **src/components/ChatInterface.tsx** - Main Interaction
- Voice-first UX simulation
- Text fallback interface
- Mode-specific interactions
- Response streaming simulation

### 7. **src/lib/systemData.ts** - Data Simulation
- Mock data for all system components
- Routing policies and configurations
- Budget tracking data
- Memory snippets and metadata

### 8. **src/lib/routingLogic.ts** - Core Logic
- Routing decision algorithms
- Budget calculations
- Privacy policy enforcement
- System health monitoring

## Key Features Implementation Priority

1. **Hardware Detection & Profiles** - Simulate device capability detection
2. **Route Visualization** - Show routing decisions in real-time
3. **Budget Tracking** - Interactive budget governance dashboard
4. **Memory System** - Versioned snippet storage and retrieval
5. **Privacy Controls** - Data flow and escalation settings
6. **Chat Interface** - Voice/text interaction simulation
7. **System Health** - Status indicators and warnings
8. **Configuration** - Settings for profiles, policies, and limits

## Design Principles
- Mobile-first responsive design
- Real-time status updates
- Clear visual hierarchy for complex data
- Interactive elements for all major features
- Privacy-first visual indicators
- Configuration-driven interface elements