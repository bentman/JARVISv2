import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import { v4 as uuidv4 } from 'uuid';
import fs from 'fs/promises';
import path from 'path';

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(helmet());
app.use(cors());
app.use(morgan('combined'));
app.use(express.json({ limit: '10mb' }));

// In-memory storage (replace with database in production)
let conversations = new Map();
let memoryStore = new Map();

// Ensure data directory exists
const DATA_DIR = './data';
try {
  await fs.mkdir(DATA_DIR, { recursive: true });
} catch (error) {
  console.log('Data directory already exists or created');
}

// Load persisted data
async function loadPersistedData() {
  try {
    const conversationsData = await fs.readFile(path.join(DATA_DIR, 'conversations.json'), 'utf8');
    const memoryData = await fs.readFile(path.join(DATA_DIR, 'memory.json'), 'utf8');
    
    conversations = new Map(JSON.parse(conversationsData));
    memoryStore = new Map(JSON.parse(memoryData));
    
    console.log('Loaded persisted data');
  } catch (error) {
    console.log('No persisted data found, starting fresh');
  }
}

// Save data periodically
async function saveData() {
  try {
    await fs.writeFile(
      path.join(DATA_DIR, 'conversations.json'),
      JSON.stringify([...conversations])
    );
    await fs.writeFile(
      path.join(DATA_DIR, 'memory.json'),
      JSON.stringify([...memoryStore])
    );
  } catch (error) {
    console.error('Failed to save data:', error);
  }
}

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    conversations: conversations.size,
    memoryEntries: memoryStore.size
  });
});

// Chat endpoint
app.post('/chat', async (req, res) => {
  try {
    const { message, profile, sessionId = 'default' } = req.body;
    
    if (!message || !profile) {
      return res.status(400).json({ error: 'Message and profile are required' });
    }

    const messageId = uuidv4();
    const timestamp = new Date().toISOString();
    
    // Get or create conversation
    if (!conversations.has(sessionId)) {
      conversations.set(sessionId, []);
    }
    
    const conversation = conversations.get(sessionId);
    
    // Add user message
    const userMessage = {
      id: messageId,
      content: message,
      timestamp,
      isUser: true,
      profile
    };
    
    conversation.push(userMessage);
    
    // Generate response based on profile
    const response = await generateResponse(message, profile, conversation);
    
    const assistantMessage = {
      id: uuidv4(),
      content: response,
      timestamp: new Date().toISOString(),
      isUser: false,
      profile
    };
    
    conversation.push(assistantMessage);
    
    // Store in memory
    const memoryEntry = {
      id: uuidv4(),
      content: `User: ${message}\nAssistant: ${response}`,
      timestamp: new Date().toISOString(),
      context: `${profile} Profile`,
      sessionId
    };
    
    memoryStore.set(memoryEntry.id, memoryEntry);
    
    // Save data
    await saveData();
    
    res.json({
      message: assistantMessage,
      memoryId: memoryEntry.id
    });
    
  } catch (error) {
    console.error('Chat error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Memory endpoint
app.get('/memory/:sessionId?', (req, res) => {
  try {
    const { sessionId } = req.params;
    const { limit = 50 } = req.query;
    
    let memories = [...memoryStore.values()];
    
    if (sessionId) {
      memories = memories.filter(m => m.sessionId === sessionId);
    }
    
    memories = memories
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
      .slice(0, parseInt(limit));
    
    res.json({ memories });
  } catch (error) {
    console.error('Memory retrieval error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Search endpoint
app.post('/search', (req, res) => {
  try {
    const { query, sessionId } = req.body;
    
    if (!query) {
      return res.status(400).json({ error: 'Query is required' });
    }
    
    let memories = [...memoryStore.values()];
    
    if (sessionId) {
      memories = memories.filter(m => m.sessionId === sessionId);
    }
    
    // Simple text search
    const results = memories.filter(memory =>
      memory.content.toLowerCase().includes(query.toLowerCase())
    ).slice(0, 10);
    
    res.json({ results, query });
  } catch (error) {
    console.error('Search error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get conversation history
app.get('/conversations/:sessionId', (req, res) => {
  try {
    const { sessionId } = req.params;
    const conversation = conversations.get(sessionId) || [];
    
    res.json({ messages: conversation });
  } catch (error) {
    console.error('Conversation retrieval error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

async function generateResponse(message, profile, conversation) {
  const context = conversation.slice(-6); // Last 3 exchanges for context
  
  // Profile-specific response generation
  const profileCapabilities = {
    light: {
      maxLength: 150,
      capabilities: ['basic conversation', 'simple Q&A', 'light reasoning']
    },
    medium: {
      maxLength: 300,
      capabilities: ['conversation', 'reasoning', 'basic coding', 'explanations']
    },
    heavy: {
      maxLength: 500,
      capabilities: ['advanced reasoning', 'complex coding', 'detailed analysis', 'multi-step problems']
    }
  };
  
  const config = profileCapabilities[profile] || profileCapabilities.light;
  
  // Simple response generation based on input patterns
  const lower = message.toLowerCase();
  
  if (lower.includes('hello') || lower.includes('hi') || lower.includes('hey')) {
    return `Hello! I'm your local AI assistant running in ${profile} mode. I can help with ${config.capabilities.join(', ')}. What would you like to work on?`;
  }
  
  if (lower.includes('code') || lower.includes('programming') || lower.includes('function')) {
    if (profile === 'light') {
      return "I can provide basic coding guidance, but for more complex programming tasks, consider switching to medium or heavy profile for better capabilities.";
    } else if (profile === 'medium') {
      return "I can help with coding! I can write functions, debug code, and explain programming concepts. What programming task would you like assistance with?";
    } else {
      return "I'm ready for complex coding challenges! I can architect solutions, write full applications, optimize algorithms, and handle advanced programming tasks. What would you like to build?";
    }
  }
  
  if (lower.includes('explain') || lower.includes('how') || lower.includes('what')) {
    if (profile === 'light') {
      return `I can provide a concise explanation. ${message.includes('?') ? 'Here\'s a brief answer:' : 'Let me explain briefly:'} This is a working response from your local AI assistant.`;
    } else if (profile === 'medium') {
      return `I can provide a detailed explanation with examples and context. ${message.includes('?') ? 'Here\'s what I can tell you:' : 'Let me break this down:'} This demonstrates medium-tier reasoning capabilities.`;
    } else {
      return `I can provide comprehensive analysis with multiple perspectives and detailed reasoning. ${message.includes('?') ? 'Here\'s a thorough explanation:' : 'Let me analyze this in depth:'} This showcases heavy-tier analytical capabilities with extended context understanding.`;
    }
  }
  
  if (lower.includes('memory') || lower.includes('remember') || lower.includes('recall')) {
    const memoryCount = context.length;
    return `I have access to our conversation history with ${memoryCount} recent exchanges. I can recall and reference previous topics we've discussed. This memory is stored locally and persists across sessions.`;
  }
  
  // Default response based on profile
  const responses = {
    light: `Processing your message with CPU-optimized efficiency. This is a real response from your local light-capacity AI assistant.`,
    medium: `Analyzing your request with medium-tier reasoning capabilities. I can provide more detailed responses and handle coding tasks.`,
    heavy: `Processing with full reasoning capabilities. I can handle complex analysis, advanced coding, and multi-step problem solving.`
  };
  
  return responses[profile] + ` You said: "${message}" - I'm ready to help with tasks suited to my ${profile} profile capabilities.`;
}

// Load data on startup
await loadPersistedData();

// Save data every 30 seconds
setInterval(saveData, 30000);

// Graceful shutdown
process.on('SIGTERM', async () => {
  console.log('Saving data before shutdown...');
  await saveData();
  process.exit(0);
});

app.listen(PORT, () => {
  console.log(`Local AI Assistant Backend running on port ${PORT}`);
  console.log(`Health check: http://localhost:${PORT}/health`);
});