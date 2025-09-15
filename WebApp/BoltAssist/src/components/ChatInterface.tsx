import React, { useState, useRef, useEffect } from 'react';
import { Send, Mic, MicOff, Volume2, VolumeX, AlertCircle } from 'lucide-react';
import { Message, VoiceState, DeviceProfile } from '../types';

interface ChatInterfaceProps {
  messages: Message[];
  onSendMessage: (content: string) => void;
  onVoiceInput: () => void;
  activeProfile: DeviceProfile;
  voiceState: VoiceState;
  onToggleListening: () => void;
  onToggleSpeech: () => void;
  isLoading: boolean;
  backendConnected: boolean;
}

export function ChatInterface({ 
  messages, 
  onSendMessage,
  onVoiceInput,
  activeProfile,
  voiceState,
  onToggleListening,
  onToggleSpeech,
  isLoading,
  backendConnected
}: ChatInterfaceProps) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading || !backendConnected) return;

    const message = input.trim();
    setInput('');
    onSendMessage(message);
  };

  const handleVoiceClick = async () => {
    if (!backendConnected) return;
    onVoiceInput();
  };

  return (
    <div className="flex flex-col h-full bg-gray-900">
      {/* Chat Header */}
      <div className="p-4 border-b border-gray-800 bg-gray-800/50">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-white">
              Chat • {activeProfile.name} Profile
            </h2>
            <p className="text-sm text-gray-400">{activeProfile.modelSize}</p>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={handleVoiceClick}
              disabled={!voiceState.isEnabled || !backendConnected}
              className={`
                p-2 rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed
                ${voiceState.isListening 
                  ? 'bg-red-500 hover:bg-red-600' 
                  : 'bg-gray-700 hover:bg-gray-600'
                }
              `}
              title={!voiceState.isEnabled ? 'Voice not available' : !backendConnected ? 'Backend disconnected' : 'Toggle voice input'}
            >
              {voiceState.isListening ? (
                <MicOff className="w-5 h-5 text-white" />
              ) : (
                <Mic className="w-5 h-5 text-white" />
              )}
            </button>
            
            <button
              onClick={onToggleSpeech}
              disabled={!voiceState.isEnabled}
              className={`
                p-2 rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed
                ${voiceState.isSpeaking 
                  ? 'bg-blue-500 hover:bg-blue-600' 
                  : 'bg-gray-700 hover:bg-gray-600'
                }
              `}
              title={!voiceState.isEnabled ? 'Voice not available' : 'Toggle speech output'}
            >
              {voiceState.isSpeaking ? (
                <Volume2 className="w-5 h-5 text-white" />
              ) : (
                <VolumeX className="w-5 h-5 text-white" />
              )}
            </button>
          </div>
        </div>
        
        {!backendConnected && (
          <div className="mt-3 p-3 bg-red-900/20 border border-red-800 rounded-lg flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-red-400" />
            <span className="text-sm text-red-300">
              Backend disconnected. Start the backend server to enable chat.
            </span>
          </div>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 mt-8">
            <p>Start a conversation with your local AI assistant</p>
            <p className="text-sm mt-2">
              {backendConnected 
                ? `Try saying "Hello" or ask a question using ${activeProfile.name.toLowerCase()} capabilities`
                : 'Start the backend server to begin chatting'
              }
            </p>
          </div>
        )}
        
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`
                max-w-xs lg:max-w-md xl:max-w-lg px-4 py-3 rounded-lg
                ${message.isUser
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-100'
                }
              `}
            >
              <p className="whitespace-pre-wrap">{message.content}</p>
              <div className="flex items-center justify-between mt-2">
                <span className="text-xs opacity-70">
                  {message.timestamp.toLocaleTimeString()}
                </span>
                {message.profile && (
                  <span className="text-xs opacity-70 capitalize">
                    {message.profile}
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-800 px-4 py-3 rounded-lg">
              <div className="flex items-center gap-2">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
                <span className="text-sm text-gray-400">Processing...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Voice Status */}
      {(voiceState.isListening || voiceState.isProcessing) && (
        <div className="px-4 py-2 bg-gray-800/50 border-t border-gray-800">
          <div className="flex items-center gap-2">
            {voiceState.isListening && (
              <>
                <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-gray-300">Listening for speech...</span>
              </>
            )}
            {voiceState.isProcessing && (
              <>
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-gray-300">Processing speech...</span>
              </>
            )}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="p-4 border-t border-gray-800">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={
              !backendConnected 
                ? 'Backend disconnected...'
                : `Ask your ${activeProfile.name.toLowerCase()} AI assistant...`
            }
            disabled={isLoading || !backendConnected}
            className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading || !backendConnected}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed px-4 py-2 rounded-lg transition-colors duration-200"
          >
            <Send className="w-5 h-5 text-white" />
          </button>
        </form>
        
        {!voiceState.isEnabled && (
          <p className="text-xs text-gray-500 mt-2">
            Voice input not available in this browser
          </p>
        )}
      </div>
    </div>
  );
}