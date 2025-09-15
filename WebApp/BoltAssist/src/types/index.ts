export interface DeviceProfile {
  id: 'light' | 'medium' | 'heavy';
  name: string;
  description: string;
  capabilities: string[];
  hardware: string;
  modelSize: string;
  icon: string;
}

export interface Message {
  id: string;
  content: string;
  timestamp: Date;
  isUser: boolean;
  profile?: string;
}

export interface MemorySnippet {
  id: string;
  content: string;
  timestamp: Date;
  context: string;
}

export interface BackendStatus {
  connected: boolean;
  latency: number;
  activeModel: string;
  memoryCount: number;
}

export interface VoiceState {
  isListening: boolean;
  isProcessing: boolean;
  isSpeaking: boolean;
  isEnabled: boolean;
}