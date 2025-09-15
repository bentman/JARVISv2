import { DeviceProfile, Message, MemorySnippet, BackendStatus } from '../types';

// Simulate backend API responses
export class MockApiService {
  private static instance: MockApiService;
  private messages: Message[] = [];
  private memorySnippets: MemorySnippet[] = [];
  private backendStatus: BackendStatus = {
    connected: true,
    latency: 45,
    activeModel: 'llama-3.1-8b',
    memoryCount: 0
  };

  static getInstance(): MockApiService {
    if (!MockApiService.instance) {
      MockApiService.instance = new MockApiService();
    }
    return MockApiService.instance;
  }

  async sendMessage(content: string, profile: DeviceProfile): Promise<Message> {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 800 + Math.random() * 1200));

    const userMessage: Message = {
      id: `user_${Date.now()}`,
      content,
      timestamp: new Date(),
      isUser: true,
      profile: profile.id
    };

    // Generate response based on profile capabilities
    const response = this.generateResponse(content, profile);
    
    const assistantMessage: Message = {
      id: `assistant_${Date.now()}`,
      content: response,
      timestamp: new Date(),
      isUser: false,
      profile: profile.id
    };

    this.messages.push(userMessage, assistantMessage);
    
    // Create memory snippet
    const memorySnippet: MemorySnippet = {
      id: `memory_${Date.now()}`,
      content: `User: ${content}\nAssistant: ${response}`,
      timestamp: new Date(),
      context: `${profile.name} Profile`
    };
    
    this.memorySnippets.push(memorySnippet);
    this.backendStatus.memoryCount = this.memorySnippets.length;

    return assistantMessage;
  }

  private generateResponse(input: string, profile: DeviceProfile): string {
    const lower = input.toLowerCase();
    
    // Profile-specific responses
    if (lower.includes('hello') || lower.includes('hi')) {
      return `Hello! I'm your ${profile.name.toLowerCase()} AI assistant running locally on your device. How can I help you today?`;
    }
    
    if (lower.includes('code') || lower.includes('programming')) {
      if (profile.id === 'light') {
        return "I can provide basic coding guidance, but for more complex programming tasks, consider switching to a medium or heavy profile for better capabilities.";
      } else if (profile.id === 'medium') {
        return "I can help with coding! I can write functions, debug code, and explain programming concepts. What would you like to work on?";
      } else {
        return "I'm ready for complex coding tasks! I can architect solutions, write full applications, optimize code, and handle advanced programming challenges.";
      }
    }
    
    if (lower.includes('reasoning') || lower.includes('think')) {
      if (profile.id === 'light') {
        return "I can handle basic reasoning tasks efficiently on your CPU. What would you like me to think through?";
      } else if (profile.id === 'medium') {
        return "With my medium-capacity profile, I can perform solid reasoning and analysis. Let me know what complex problem you'd like to explore.";
      } else {
        return "I'm operating at full capacity for complex reasoning, logical analysis, and multi-step problem solving. What challenging question can I help you with?";
      }
    }
    
    if (lower.includes('capability') || lower.includes('what can you do')) {
      return `Running in ${profile.name} mode, I can: ${profile.capabilities.join(', ')}. My current model size is ${profile.modelSize} optimized for ${profile.hardware}.`;
    }

    // Default responses based on profile
    const responses = {
      light: [
        "I'm processing your request using my lightweight CPU-optimized model. Here's what I can tell you:",
        "Running efficiently on CPU, I can provide you with a concise answer:",
        "Using my compact model, here's my response:"
      ],
      medium: [
        "With my medium-capacity GPU acceleration, I can provide a more detailed analysis:",
        "Leveraging my enhanced reasoning capabilities, here's what I think:",
        "Using my mid-tier model with coding support, I can help you with:"
      ],
      heavy: [
        "Drawing on my full reasoning capabilities and large model, I can provide comprehensive insight:",
        "With access to my complete knowledge base and advanced processing, here's my analysis:",
        "Using my heavy-capacity profile for maximum performance, I can tell you:"
      ]
    };

    const profileResponses = responses[profile.id];
    const randomResponse = profileResponses[Math.floor(Math.random() * profileResponses.length)];
    
    return `${randomResponse}\n\nRegarding "${input}" - This is a simulated response demonstrating the ${profile.name} profile capabilities. In a real implementation, this would connect to your local LLM running ${profile.modelSize} on ${profile.hardware}.`;
  }

  async getMemorySnippets(): Promise<MemorySnippet[]> {
    return this.memorySnippets;
  }

  async getBackendStatus(): Promise<BackendStatus> {
    // Simulate some variation in latency
    this.backendStatus.latency = 35 + Math.floor(Math.random() * 30);
    return this.backendStatus;
  }

  getMessages(): Message[] {
    return this.messages;
  }
}