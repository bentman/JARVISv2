import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { ChatInterface } from './components/ChatInterface';
import { StatusPanel } from './components/StatusPanel';
import { ProfileSelection } from './components/ProfileSelection';
import { LoadingScreen } from './components/LoadingScreen';
import { VoiceVisualizer } from './components/VoiceVisualizer';
import { useDeviceDetection } from './hooks/useDeviceDetection';
import { useVoiceInterface } from './hooks/useVoiceInterface';
import { ApiService } from './services/apiService';
import { Message, MemorySnippet, BackendStatus } from './types';

function App() {
  const { detectedProfile, activeProfile, isDetecting, changeProfile } = useDeviceDetection();
  const { voiceState, permissionGranted, initializeVoice, toggleListening, toggleSpeech, speak } = useVoiceInterface();
  
  const [messages, setMessages] = useState<Message[]>([]);
  const [memorySnippets, setMemorySnippets] = useState<MemorySnippet[]>([]);
  const [backendStatus, setBackendStatus] = useState<BackendStatus>({
    connected: false,
    latency: 0,
    activeModel: 'offline',
    memoryCount: 0
  });
  const [currentView, setCurrentView] = useState<'chat' | 'profile'>('chat');
  const [isLoading, setIsLoading] = useState(false);

  const apiService = ApiService.getInstance();

  useEffect(() => {
    initializeVoice();
    loadConversationHistory();
    
    // Update backend status periodically
    const statusInterval = setInterval(updateBackendStatus, 5000);
    
    // Initial status check
    updateBackendStatus();

    return () => clearInterval(statusInterval);
  }, [initializeVoice]);

  const updateBackendStatus = async () => {
    try {
      const status = await apiService.getBackendStatus();
      setBackendStatus(status);
    } catch (error) {
      console.error('Failed to update backend status:', error);
      setBackendStatus(prev => ({ ...prev, connected: false }));
    }
  };

  const loadConversationHistory = async () => {
    try {
      const history = await apiService.getConversationHistory();
      setMessages(history);
      
      const memory = await apiService.getMemorySnippets();
      setMemorySnippets(memory);
    } catch (error) {
      console.error('Failed to load conversation history:', error);
    }
  };

  const handleSendMessage = async (content: string) => {
    if (!activeProfile || !backendStatus.connected) {
      console.error('Cannot send message: no active profile or backend disconnected');
      return;
    }

    setIsLoading(true);

    try {
      // Add user message immediately
      const userMessage: Message = {
        id: `user_${Date.now()}`,
        content,
        timestamp: new Date(),
        isUser: true,
        profile: activeProfile.id
      };
      
      setMessages(prev => [...prev, userMessage]);

      // Send to backend
      const response = await apiService.sendMessage(content, activeProfile);
      
      // Add assistant response
      setMessages(prev => [...prev, response]);
      
      // Update memory
      const memory = await apiService.getMemorySnippets();
      setMemorySnippets(memory);
      
      // Speak response if voice is enabled
      if (voiceState.isEnabled && permissionGranted && !voiceState.isSpeaking) {
        await speak(response.content);
      }
      
    } catch (error) {
      console.error('Failed to send message:', error);
      
      // Add error message
      const errorMessage: Message = {
        id: `error_${Date.now()}`,
        content: 'Sorry, I encountered an error processing your message. Please check that the backend is running.',
        timestamp: new Date(),
        isUser: false,
        profile: activeProfile.id
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleVoiceInput = async () => {
    try {
      const transcript = await toggleListening();
      if (transcript) {
        await handleSendMessage(transcript);
      }
    } catch (error) {
      console.error('Voice input failed:', error);
    }
  };

  const handleProfileChange = (profileId: 'light' | 'medium' | 'heavy') => {
    changeProfile(profileId);
  };

  if (isDetecting) {
    return <LoadingScreen />;
  }

  if (!activeProfile || !detectedProfile) {
    return <LoadingScreen />;
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <Header 
        activeProfile={activeProfile}
        backendStatus={backendStatus}
        onProfileChange={handleProfileChange}
      />
      
      <div className="flex h-[calc(100vh-80px)]">
        {/* Main Content */}
        <div className="flex-1 flex flex-col">
          {/* Navigation */}
          <div className="bg-gray-800 border-b border-gray-700 px-6 py-3">
            <nav className="flex gap-4">
              <button
                onClick={() => setCurrentView('chat')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  currentView === 'chat'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
              >
                Chat Interface
              </button>
              <button
                onClick={() => setCurrentView('profile')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  currentView === 'profile'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
              >
                Profile Settings
              </button>
            </nav>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-hidden">
            {currentView === 'chat' ? (
              <ChatInterface
                messages={messages}
                onSendMessage={handleSendMessage}
                onVoiceInput={handleVoiceInput}
                activeProfile={activeProfile}
                voiceState={voiceState}
                onToggleListening={handleVoiceInput}
                onToggleSpeech={toggleSpeech}
                isLoading={isLoading}
                backendConnected={backendStatus.connected}
              />
            ) : (
              <ProfileSelection
                detectedProfile={detectedProfile}
                activeProfile={activeProfile}
                onProfileChange={handleProfileChange}
              />
            )}
          </div>
        </div>

        {/* Status Panel */}
        <div className="w-80 border-l border-gray-800">
          <StatusPanel
            backendStatus={backendStatus}
            memorySnippets={memorySnippets}
            messageCount={messages.length}
          />
        </div>
      </div>

      {/* Voice Visualizer */}
      <VoiceVisualizer voiceState={voiceState} />
    </div>
  );
}

export default App;