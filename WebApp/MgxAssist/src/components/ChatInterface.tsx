import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { MessageSquare, Mic, MicOff, Send, Zap, Cloud, Server, User, Bot, Volume2 } from 'lucide-react';
import { HardwareProfile } from '@/lib/systemData';
import { Route, getRouteIcon, formatCurrency, formatLatency } from '@/lib/routingLogic';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  route?: Route;
  cost?: number;
  latency?: number;
  mode: 'assistant' | 'coding' | 'search';
}

interface ChatInterfaceProps {
  currentMode: 'assistant' | 'coding' | 'search';
  hardwareProfile: HardwareProfile;
  onModeChange: (mode: 'assistant' | 'coding' | 'search') => void;
}

export default function ChatInterface({ currentMode, hardwareProfile, onModeChange }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'assistant',
      content: 'Hello! I\'m your hybrid local-first AI assistant. I can help with general questions, coding tasks, and search queries. How can I assist you today?',
      timestamp: new Date(),
      route: 'local',
      cost: 0,
      latency: 120,
      mode: 'assistant'
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const simulateVoiceRecognition = () => {
    if (!voiceEnabled) {
      alert('Voice recognition is simulated in this demo. In a real implementation, this would use the Web Speech API.');
      return;
    }

    setIsListening(!isListening);
    
    if (!isListening) {
      // Simulate voice input after 2 seconds
      setTimeout(() => {
        const sampleInputs = {
          assistant: "What's the weather like today?",
          coding: "Help me optimize this React component",
          search: "Find information about TypeScript best practices"
        };
        setInputText(sampleInputs[currentMode]);
        setIsListening(false);
      }, 2000);
    }
  };

  const simulateResponse = async (userMessage: string): Promise<Message> => {
    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 1500 + Math.random() * 1000));

    const responses = {
      assistant: [
        "I'd be happy to help with that! Based on your hardware profile, I can process this locally for better privacy.",
        "That's an interesting question. Let me route this to our cloud-small tier for a comprehensive answer.",
        "I understand what you're looking for. Processing this locally to keep your data private."
      ],
      coding: [
        "I'll analyze your code and provide optimization suggestions. Using cloud-large for advanced code analysis.",
        "Let me help you with that coding task. Processing locally with your high-performance setup.",
        "I can assist with code optimization. Routing to cloud-small for balanced performance and cost."
      ],
      search: [
        "I'll search for that information across multiple sources and provide you with the most relevant results.",
        "Searching for comprehensive information on that topic. Using cloud aggregation for best results.",
        "Let me find the latest information on that for you. Processing search query locally first."
      ]
    };

    const routes: Route[] = ['local', 'cloud-small', 'cloud-large'];
    const selectedRoute = routes[Math.floor(Math.random() * routes.length)];
    const costs = { local: 0, 'cloud-small': 0.01 + Math.random() * 0.02, 'cloud-large': 0.05 + Math.random() * 0.10 };
    const latencies = { local: 100 + Math.random() * 100, 'cloud-small': 300 + Math.random() * 200, 'cloud-large': 800 + Math.random() * 400 };

    return {
      id: Date.now().toString(),
      type: 'assistant',
      content: responses[currentMode][Math.floor(Math.random() * responses[currentMode].length)],
      timestamp: new Date(),
      route: selectedRoute,
      cost: costs[selectedRoute],
      latency: latencies[selectedRoute],
      mode: currentMode
    };
  };

  const handleSendMessage = async () => {
    if (!inputText.trim() || isProcessing) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputText,
      timestamp: new Date(),
      mode: currentMode
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsProcessing(true);

    try {
      const assistantMessage = await simulateResponse(inputText);
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error generating response:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const getModeIcon = (mode: string) => {
    switch (mode) {
      case 'assistant': return <MessageSquare className="h-4 w-4" />;
      case 'coding': return <Zap className="h-4 w-4" />;
      case 'search': return <Cloud className="h-4 w-4" />;
      default: return <MessageSquare className="h-4 w-4" />;
    }
  };

  const getModeColor = (mode: string) => {
    switch (mode) {
      case 'assistant': return 'text-blue-600 bg-blue-50';
      case 'coding': return 'text-purple-600 bg-purple-50';
      case 'search': return 'text-green-600 bg-green-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <Card className="w-full h-[600px] flex flex-col">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5" />
              AI Chat Interface
            </CardTitle>
            <CardDescription>
              Voice-first interaction with intelligent routing
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setVoiceEnabled(!voiceEnabled)}
              className={voiceEnabled ? 'bg-green-50 text-green-600' : ''}
            >
              <Volume2 className="h-4 w-4 mr-2" />
              {voiceEnabled ? 'Voice On' : 'Voice Off'}
            </Button>
          </div>
        </div>
        
        {/* Mode Selector */}
        <div className="flex gap-2">
          {(['assistant', 'coding', 'search'] as const).map((mode) => (
            <Button
              key={mode}
              variant={currentMode === mode ? 'default' : 'outline'}
              size="sm"
              onClick={() => onModeChange(mode)}
              className="gap-2"
            >
              {getModeIcon(mode)}
              {mode.charAt(0).toUpperCase() + mode.slice(1)}
            </Button>
          ))}
        </div>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col p-4">
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto space-y-4 mb-4">
          {messages.map((message) => (
            <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] ${message.type === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted'} rounded-lg p-3`}>
                <div className="flex items-center gap-2 mb-1">
                  {message.type === 'user' ? (
                    <User className="h-4 w-4" />
                  ) : (
                    <Bot className="h-4 w-4" />
                  )}
                  <Badge className={getModeColor(message.mode)} variant="secondary">
                    {message.mode}
                  </Badge>
                  {message.route && (
                    <Badge variant="outline" className="text-xs">
                      {getRouteIcon(message.route)} {message.route}
                    </Badge>
                  )}
                </div>
                <p className="text-sm">{message.content}</p>
                {message.type === 'assistant' && message.cost !== undefined && (
                  <div className="flex items-center gap-3 mt-2 text-xs opacity-70">
                    <span>Cost: {formatCurrency(message.cost)}</span>
                    <span>Latency: {formatLatency(message.latency || 0)}</span>
                    <span>{message.timestamp.toLocaleTimeString()}</span>
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {isProcessing && (
            <div className="flex justify-start">
              <div className="bg-muted rounded-lg p-3 max-w-[80%]">
                <div className="flex items-center gap-2">
                  <Bot className="h-4 w-4" />
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-current rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-current rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-current rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                  <span className="text-sm text-muted-foreground">Processing...</span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="icon"
            onClick={simulateVoiceRecognition}
            className={isListening ? 'bg-red-50 text-red-600' : ''}
            disabled={isProcessing}
          >
            {isListening ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
          </Button>
          <Textarea
            placeholder={`Ask me anything in ${currentMode} mode...`}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={handleKeyPress}
            className="flex-1 min-h-[40px] max-h-[120px] resize-none"
            disabled={isProcessing}
          />
          <Button
            onClick={handleSendMessage}
            disabled={!inputText.trim() || isProcessing}
            size="icon"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
        
        {isListening && (
          <Alert className="mt-2">
            <Mic className="h-4 w-4" />
            <AlertDescription>
              Listening... Speak your message now.
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
}