import { DeviceProfile, Message, MemorySnippet, BackendStatus } from '../types';

const API_BASE_URL = 'http://localhost:3001';

export class ApiService {
  private static instance: ApiService;
  private sessionId: string;

  constructor() {
    this.sessionId = this.getOrCreateSessionId();
  }

  static getInstance(): ApiService {
    if (!ApiService.instance) {
      ApiService.instance = new ApiService();
    }
    return ApiService.instance;
  }

  private getOrCreateSessionId(): string {
    let sessionId = localStorage.getItem('ai-session-id');
    if (!sessionId) {
      sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('ai-session-id', sessionId);
    }
    return sessionId;
  }

  async sendMessage(content: string, profile: DeviceProfile): Promise<Message> {
    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: content,
          profile: profile.id,
          sessionId: this.sessionId
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return {
        id: data.message.id,
        content: data.message.content,
        timestamp: new Date(data.message.timestamp),
        isUser: false,
        profile: data.message.profile
      };
    } catch (error) {
      console.error('Failed to send message:', error);
      throw new Error('Failed to communicate with backend');
    }
  }

  async getConversationHistory(): Promise<Message[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/conversations/${this.sessionId}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.messages.map((msg: any) => ({
        ...msg,
        timestamp: new Date(msg.timestamp)
      }));
    } catch (error) {
      console.error('Failed to get conversation history:', error);
      return [];
    }
  }

  async getMemorySnippets(): Promise<MemorySnippet[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/memory/${this.sessionId}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.memories.map((memory: any) => ({
        ...memory,
        timestamp: new Date(memory.timestamp)
      }));
    } catch (error) {
      console.error('Failed to get memory snippets:', error);
      return [];
    }
  }

  async searchMemory(query: string): Promise<MemorySnippet[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          sessionId: this.sessionId
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.results.map((memory: any) => ({
        ...memory,
        timestamp: new Date(memory.timestamp)
      }));
    } catch (error) {
      console.error('Failed to search memory:', error);
      return [];
    }
  }

  async getBackendStatus(): Promise<BackendStatus> {
    try {
      const startTime = Date.now();
      const response = await fetch(`${API_BASE_URL}/health`);
      const latency = Date.now() - startTime;
      
      if (!response.ok) {
        return {
          connected: false,
          latency: 0,
          activeModel: 'offline',
          memoryCount: 0
        };
      }

      const data = await response.json();
      
      return {
        connected: true,
        latency,
        activeModel: this.getModelForProfile(),
        memoryCount: data.memoryEntries || 0
      };
    } catch (error) {
      return {
        connected: false,
        latency: 0,
        activeModel: 'offline',
        memoryCount: 0
      };
    }
  }

  private getModelForProfile(): string {
    const profile = localStorage.getItem('active-profile') || 'light';
    const modelMap = {
      light: 'phi-3-mini',
      medium: 'llama-3.1-8b',
      heavy: 'llama-3.1-70b'
    };
    return modelMap[profile as keyof typeof modelMap] || 'phi-3-mini';
  }
}