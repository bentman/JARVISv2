import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  MessageSquare, 
  Mic, 
  MicOff, 
  Send, 
  Zap, 
  Cloud, 
  Server, 
  User, 
  Bot, 
  Volume2,
  AlertTriangle,
  CheckCircle,
  Clock,
  DollarSign,
  Shield
} from 'lucide-react';
import { HardwareProfile } from '@/lib/systemData';
import { Route, formatCurrency, formatLatency } from '@/lib/routingLogic';
import { mockBackend, MockResponse } from '@/lib/mockBackend';

interface Message {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  route?: Route;
  cost?: number;
  latency?: number;
  mode: 'assistant' | 'coding' | 'search';
  provider?: string;
  model?: string;
  tokensUsed?: number;
  processingSteps?: string[];
}

interface EnhancedChatInterfaceProps {
  currentMode: 'assistant' | 'coding' | 'search';
  hardwareProfile: HardwareProfile;
  privacyLevel: 'local-only' | 'cloud-allowed' | 'external-ok';
  onModeChange: (mode: 'assistant' | 'coding' | 'search') => void;
  onBudgetUpdate: (budget: any) => void;
}

export default function EnhancedChatInterface({ 
  currentMode, 
  hardwareProfile, 
  privacyLevel,
  onModeChange,
  onBudgetUpdate 
}: EnhancedChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'system',
      content: 'Hybrid AI Assistant initialized. Hardware profile detected and routing engine ready. How can I help you today?',
      timestamp: new Date(),
      mode: 'assistant'
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingSteps, setProcessingSteps] = useState<string[]>([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [voiceEnabled, setVoiceEnabled] = useState(false);
  const [error, setError] = useState<string | null>(null);
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
      setTimeout(() => {
        const sampleInputs = {
          assistant: "What's the best way to optimize my daily workflow?",
          coding: "Help me refactor this React component for better performance",
          search: "Find the latest information about TypeScript 5.0 features"
        };
        setInputText(sampleInputs[currentMode]);
        setIsListening(false);
      }, 2000);
    }
  };

  const processWithBackend = async (userMessage: string): Promise<void> => {
    setIsProcessing(true);
    setProcessingSteps([]);
    setCurrentStep(0);
    setError(null);

    try {
      const steps = [
        'Analyzing query intent and complexity',
        'Checking privacy and budget constraints',
        'Selecting optimal routing tier',
        'Initializing AI model',
        'Processing query',
        'Generating response',
        'Updating memory and telemetry'
      ];

      setProcessingSteps(steps);

      for (let i = 0; i < steps.length - 1; i++) {
        setCurrentStep(i);
        await new Promise(resolve => setTimeout(resolve, 300 + Math.random() * 200));
      }

      const response: MockResponse = await mockBackend.processQuery(
        userMessage,
        currentMode,
        hardwareProfile,
        privacyLevel
      );

      setCurrentStep(steps.length - 1);
      await new Promise(resolve => setTimeout(resolve, 200));

      const assistantMessage: Message = {
        id: Date.now().toString(),
        type: 'assistant',
        content: response.content,
        timestamp: new Date(),
        route: response.route,
        cost: response.cost,
        latency: response.latency,
        mode: currentMode,
        provider: response.provider,
        model: response.model,
        tokensUsed: response.tokensUsed,
        processingSteps: response.processingSteps
      };

      setMessages(prev => [...prev, assistantMessage]);
      onBudgetUpdate(mockBackend.getBudgetData());

    } catch (error: any) {
      setError(error.message);
      
      const errorMessage: Message = {
        id: Date.now().toString(),
        type: 'system',
        content: `Error: ${error.message}`,
        timestamp: new Date(),
        mode: currentMode
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsProcessing(false);
      setProcessingSteps([]);
      setCurrentStep(0);
    }
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
    const messageToProcess = inputText;
    setInputText('');

    await processWithBackend(messageToProcess);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleQuickAction = (action: string) => {
    setInputText(action);
  };

  const getModeIcon = (mode: string) => {
    switch (mode) {
      case 'assistant': return <MessageSquare className="h-4 w-4" />;
      case 'coding': return <Zap className="h-4 w-4" />;
      case 'search': return <Cloud className="h-4 w-4" />;
      default: return <MessageSquare className="h-4 w-4" />;
    }
  };

  const getRouteIcon = (route?: Route) => {
    if (!route) return null;
    switch (route) {
      case 'local': return <Zap className="h-3 w-3" />;
      case 'cloud-small': return <Cloud className="h-3 w-3" />;
      case 'cloud-large': return <Server className="h-3 w-3" />;
    }
  };

  const getRouteColor = (route?: Route) => {
    if (!route) return '';
    switch (route) {
      case 'local': return 'text-green-600 bg-green-50';
      case 'cloud-small': return 'text-blue-600 bg-blue-50';
      case 'cloud-large': return 'text-purple-600 bg-purple-50';
    }
  };

  const getPrivacyLevelColor = (level: string) => {
    switch (level) {
      case 'local-only': return 'text-red-600 bg-red-50';
      case 'cloud-allowed': return 'text-yellow-600 bg-yellow-50';
      case 'external-ok': return 'text-green-600 bg-green-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const quickActions = {
    assistant: [
      "What's the weather like today?",
      "Help me plan my daily schedule",
      "Explain quantum computing in simple terms"
    ],
    coding: [
      "Review this React component for performance issues",
      "Help me optimize this database query",
      "Explain the SOLID principles with examples"
    ],
    search: [
      "Find the latest AI research papers",
      "Search for TypeScript best practices",
      "Look up current market trends in tech"
    ]
  };

  return (
    <Card className="w-full h-[700px] flex flex-col">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5" />
              Enhanced AI Chat Interface
            </CardTitle>
            <CardDescription>
              Real-time routing with budget tracking and privacy controls
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Badge className={getPrivacyLevelColor(privacyLevel)}>
              <Shield className="h-3 w-3 mr-1" />
              {privacyLevel.replace('-', ' ')}
            </Badge>
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

        <div className="flex items-center gap-4 text-sm">
          <div className="flex items-center gap-2">
            <span className="text-muted-foreground">Hardware:</span>
            <Badge variant="outline">{hardwareProfile.type.toUpperCase()}</Badge>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-muted-foreground">Profile:</span>
            <span className="font-medium">{hardwareProfile.name}</span>
          </div>
        </div>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col p-4">
        <div className="flex-1 overflow-y-auto space-y-4 mb-4">
          {messages.map((message) => (
            <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] ${
                message.type === 'user' 
                  ? 'bg-primary text-primary-foreground' 
                  : message.type === 'system'
                  ? 'bg-muted border-l-4 border-blue-500'
                  : 'bg-muted'
              } rounded-lg p-3`}>
                <div className="flex items-center gap-2 mb-2">
                  {message.type === 'user' ? (
                    <User className="h-4 w-4" />
                  ) : message.type === 'system' ? (
                    <AlertTriangle className="h-4 w-4" />
                  ) : (
                    <Bot className="h-4 w-4" />
                  )}
                  
                  <Badge variant="secondary" className="text-xs">
                    {message.mode}
                  </Badge>
                  
                  {message.route && (
                    <Badge className={`${getRouteColor(message.route)} text-xs`}>
                      {getRouteIcon(message.route)}
                      <span className="ml-1">{message.route}</span>
                    </Badge>
                  )}
                  
                  {message.provider && (
                    <Badge variant="outline" className="text-xs">
                      {message.model}
                    </Badge>
                  )}
                </div>
                
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                
                {message.type === 'assistant' && message.cost !== undefined && (
                  <div className="mt-3 pt-2 border-t border-border/50">
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div className="flex items-center gap-1">
                        <DollarSign className="h-3 w-3" />
                        <span>Cost: {formatCurrency(message.cost)}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        <span>Latency: {formatLatency(message.latency || 0)}</span>
                      </div>
                      {message.tokensUsed && (
                        <div className="col-span-2 flex items-center gap-1">
                          <span>Tokens: {message.tokensUsed}</span>
                          <span className="text-muted-foreground">•</span>
                          <span>{message.timestamp.toLocaleTimeString()}</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {isProcessing && (
            <div className="flex justify-start">
              <div className="bg-muted rounded-lg p-3 max-w-[80%]">
                <div className="flex items-center gap-2 mb-2">
                  <Bot className="h-4 w-4" />
                  <Badge variant="secondary" className="text-xs">Processing</Badge>
                </div>
                
                {processingSteps.length > 0 && (
                  <div className="space-y-2">
                    <Progress value={(currentStep / processingSteps.length) * 100} className="h-2" />
                    <div className="space-y-1">
                      {processingSteps.map((step, index) => (
                        <div key={index} className={`flex items-center gap-2 text-xs ${
                          index < currentStep ? 'text-green-600' : 
                          index === currentStep ? 'text-blue-600' : 
                          'text-muted-foreground'
                        }`}>
                          {index < currentStep ? (
                            <CheckCircle className="h-3 w-3" />
                          ) : index === currentStep ? (
                            <div className="w-3 h-3 border-2 border-current border-t-transparent rounded-full animate-spin" />
                          ) : (
                            <div className="w-3 h-3 rounded-full border border-current" />
                          )}
                          <span>{step}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {error && (
          <Alert className="mb-4 border-red-200 bg-red-50">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Quick Actions */}
        <div className="mb-3">
          <div className="text-xs text-muted-foreground mb-2">Quick actions for {currentMode} mode:</div>
          <div className="flex flex-wrap gap-1">
            {quickActions[currentMode].map((action, index) => (
              <Button
                key={index}
                variant="outline"
                size="sm"
                onClick={() => handleQuickAction(action)}
                className="text-xs h-7"
                disabled={isProcessing}
              >
                {action}
              </Button>
            ))}
          </div>
        </div>

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