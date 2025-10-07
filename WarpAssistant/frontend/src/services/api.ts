// API service for connecting to the backend
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Types
interface ChatRequest {
  message: string;
  mode?: string;
  stream?: boolean;
}

interface ChatResponse {
  type: string;
  content: string;
  tokens_used?: number;
}

interface HardwareInfo {
  profile: string;
  capabilities: {
    cpu_cores: number;
    cpu_architecture: string;
    gpu_vendor: string | null;
    gpu_memory_gb: number | null;
    total_memory_gb: number;
    profile: string;
  };
  selected_model: string;
}

interface VoiceRequest {
  audio_data: string; // Base64 encoded audio data
}

interface VoiceResponse {
  text: string;
  confidence: number;
}

// API Service Class
export class ApiService {
  // Chat API
  static async sendMessage(request: ChatRequest): Promise<ChatResponse[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/send`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
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
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error getting hardware info:', error);
      throw error;
    }
  }

  // Voice API
  static async speechToText(audioData: string): Promise<VoiceResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/voice/stt`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          audio_data: audioData
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error in speech-to-text:', error);
      throw error;
    }
  }

  static async textToSpeech(text: string): Promise<string> {
    try {
      const response = await fetch(`${API_BASE_URL}/voice/tts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: text
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.audio_data;
    } catch (error) {
      console.error('Error in text-to-speech:', error);
      throw error;
    }
  }

  // Memory API
  static async getConversations() {
    try {
      const response = await fetch(`${API_BASE_URL}/memory/conversations`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error getting conversations:', error);
      throw error;
    }
  }
}

// Export default instance
export default new ApiService();