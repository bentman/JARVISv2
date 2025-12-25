// API service for connecting to the backend
const API_BASE_URL = 'http://localhost:8000/api/v1';

// --- Types ---

export interface ChatRequest {
  message: string;
  mode?: string;
  stream?: boolean;
}

export interface ChatResponse {
  type: string;
  content: string;
  tokens_used?: number;
}

export interface HardwareInfo {
  profile: string;
  capabilities: {
    cpu: {
      cores: number;
      threads: number;
      architecture: string;
    };
    gpu: {
      name: string;
      memory_gb: number;
      vendor: string;
    } | null;
    memory: {
      total_gb: number;
      available_gb: number;
    };
    profile: string;
  };
  selected_model: string;
}

export interface VoiceResponse {
  text: string;
  confidence: number;
}

export interface VoiceSessionRequest {
  audio_data: string; // Base64 encoded audio data
  conversation_id?: string;
  mode?: string;
  include_web?: boolean;
  escalate_llm?: boolean;
}

export interface VoiceSessionResponse {
  detected: boolean;
  conversation_id: string;
  transcript: string;
  response_text: string;
  audio_data: string; // Base64 encoded WAV
}

export interface PrivacySettings {
  privacy_level: string;
  data_retention_days: number;
  redact_aggressiveness: string;
}

export interface BudgetStatus {
  daily_cost_usd: number;
  daily_limit_usd: number;
  monthly_cost_usd: number;
  monthly_limit_usd: number;
  enforce: boolean;
  cost_per_token_local_usd: number;
  cost_per_token_remote_llm_usd: number;
}

export interface BudgetConfigRequest {
  daily_limit_usd?: number | null;
  monthly_limit_usd?: number | null;
  enforce?: boolean | null;
}

// --- API Service Class ---

export class ApiService {
  // Chat API
  static async sendMessage(request: ChatRequest): Promise<ChatResponse[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      });
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  }

  // Hardware API
  static async getHardwareInfo(): Promise<HardwareInfo> {
    try {
      const response = await fetch(`${API_BASE_URL}/hardware/detect`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Error getting hardware info:', error);
      throw error;
    }
  }

  // Voice API (Legacy components)
  static async speechToText(audioData: string): Promise<VoiceResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/voice/stt`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ audio_data: audioData }),
      });
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Error in speech-to-text:', error);
      throw error;
    }
  }

  static async textToSpeech(text: string): Promise<string> {
    try {
      const response = await fetch(`${API_BASE_URL}/voice/tts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      return data.audio_data;
    } catch (error) {
      console.error('Error in text-to-speech:', error);
      throw error;
    }
  }

  // Unified Voice Session
  static async voiceSession(request: VoiceSessionRequest): Promise<VoiceSessionResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/voice/session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      });
      // 429 Budget exceeded is special
      if (response.status === 429) {
         throw new Error("Budget Limit Exceeded");
      }
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Error in voice session:', error);
      throw error;
    }
  }

  // Memory API
  static async getConversations() {
    try {
      const response = await fetch(`${API_BASE_URL}/memory/conversations`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Error getting conversations:', error);
      throw error;
    }
  }

  // Settings: Privacy
  static async getPrivacySettings(): Promise<PrivacySettings> {
    const response = await fetch(`${API_BASE_URL}/privacy/settings`);
    if (!response.ok) throw new Error("Failed to fetch privacy settings");
    return await response.json();
  }

  static async updatePrivacySettings(settings: PrivacySettings): Promise<PrivacySettings> {
    const response = await fetch(`${API_BASE_URL}/privacy/settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings)
    });
    if (!response.ok) throw new Error("Failed to update privacy settings");
    return await response.json();
  }

  // Settings: Budget
  static async getBudgetStatus(): Promise<BudgetStatus> {
      const response = await fetch(`${API_BASE_URL}/budget/status`);
      if (!response.ok) throw new Error("Failed to fetch budget status");
      return await response.json();
  }

  static async updateBudgetConfig(config: BudgetConfigRequest): Promise<void> {
      const response = await fetch(`${API_BASE_URL}/budget/config`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(config)
      });
      if (!response.ok) throw new Error("Failed to update budget config");
  }
}

export default new ApiService();
