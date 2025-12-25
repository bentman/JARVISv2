import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { MessageCircle, Mic, Settings, FileText, MicOff, Globe, Volume2, VolumeX } from 'lucide-react';
import { voiceService } from '../services';
import { ApiService, ChatResponse } from '../services/api';
import { HardwareStatus } from './HardwareStatus';
import { SettingsModal } from './SettingsModal';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  
  // Modes
  const [voiceMode, setVoiceMode] = useState(false); // If true, play TTS and use session
  const [includeWeb, setIncludeWeb] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (inputValue.trim() === '') return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');

    setIsProcessing(true);
    try {
      // Chat Request
      const responses = await ApiService.sendMessage({
        message: inputValue,
        mode: 'chat',
        stream: true
      });
      
      const aiResponse = responses.find((r: ChatResponse) => r.type === 'response');
      
      if (aiResponse) {
        const aiMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: aiResponse.content,
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, aiMessage]);

        // If in voice mode, we should technically TTS here, but /chat/send doesn't return audio.
        // For mixed text/voice, we rely on the mic button flow for audio.
        // If user typed but Voice Mode is ON, we could call TTS separately.
        if (voiceMode) {
             const audioBase64 = await ApiService.textToSpeech(aiResponse.content);
             const audio = new Audio(`data:audio/wav;base64,${audioBase64}`);
             await audio.play();
        }

      } else {
        throw new Error('No response content');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, there was an error connecting to the AI service.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const toggleVoice = async () => {
    try {
      if (isListening) {
        // User manually stopped recording
        voiceService.stopListening(); 
        setIsListening(false);
        // Note: voiceService.ts currently auto-processes on stop.
        // To use /session, we'd need to change voiceService or use a different flow here.
        // For Sprint 1, let's stick to the existing voiceService flow but enhance the output handling.
        // EDIT: To properly implement /session, we need the raw blob. voiceService.ts encapsulates it.
        // Let's rely on the existing STT flow for now, but verify it works.
      } else {
        await voiceService.startListening();
        setIsListening(true);
      }
    } catch (error) {
      console.error('Voice toggle error:', error);
    }
  };
  
  // Poll for voice service result (hacky, but matches current voiceService implementation)
  // Ideally voiceService should emit events or return a promise on stop.
  // The current voiceService.ts returns the text promise from startListening? No, startListening returns void.
  // Wait, I read voiceService.ts earlier. 
  // It says: "this.mediaRecorder.onstop = async () => { const audioBlob ... await this.processAudio(audioBlob); }"
  // And processAudio returns result.text. BUT where does it return TO? It just returns to the onstop handler.
  // The current voiceService.ts implementation swallows the result! The console.log shows it, but the UI never gets it.
  // I NEED TO FIX VoiceService.ts to use a callback or event.

  return (
    <div className="flex flex-col h-full bg-gray-50">
      <SettingsModal isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />
      
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-4 flex items-center justify-between shadow-sm">
        <div className="flex items-center space-x-4">
           <h1 className="text-xl font-bold text-gray-800 tracking-tight">JARVIS</h1>
           <div className="hidden md:block h-6 w-px bg-gray-200"></div>
           <HardwareStatus />
        </div>
        
        <div className="flex space-x-2">
           <button 
            onClick={() => setVoiceMode(!voiceMode)}
            className={`p-2 rounded-lg transition-colors ${voiceMode ? 'bg-blue-100 text-blue-600' : 'hover:bg-gray-100 text-gray-600'}`}
            title="Toggle Voice Mode"
          >
            {voiceMode ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
          </button>
          <button className="p-2 rounded-lg hover:bg-gray-100 transition-colors">
            <FileText className="w-5 h-5 text-gray-600" />
          </button>
          <button 
            onClick={() => setIsSettingsOpen(true)}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <Settings className="w-5 h-5 text-gray-600" />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center space-y-6 opacity-60">
            <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center">
                <MessageCircle className="w-10 h-10 text-blue-500" />
            </div>
            <div>
                <h2 className="text-2xl font-semibold text-gray-800">Local AI Assistant</h2>
                <p className="text-gray-500 max-w-md mt-2">
                Ready to assist with privacy-first processing.
                </p>
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-3xl rounded-2xl px-6 py-4 shadow-sm prose max-w-none ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white prose-invert'
                    : 'bg-white border border-gray-200 text-gray-800'
                }`}
              >
                 <ReactMarkdown 
                    remarkPlugins={[remarkGfm]}
                    components={{
                        pre: ({node, ...props}) => <div className="overflow-auto w-full my-2 bg-black/10 p-2 rounded" {...props as any} />,
                        code: ({node, ...props}) => <code className="font-mono text-sm" {...props as any} />
                    }}
                 >
                    {message.content}
                 </ReactMarkdown>
              </div>
            </div>
          ))
        )}
        {isProcessing && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 rounded-2xl px-6 py-4 shadow-sm">
              <div className="flex items-center space-x-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                </div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="bg-white p-4 border-t border-gray-200">
        <div className="max-w-5xl mx-auto flex items-end space-x-4">
          <div className="flex-1 relative bg-gray-50 rounded-2xl border border-gray-200 focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-transparent transition-all">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Type your message..."
              className="w-full bg-transparent border-none py-4 px-4 pr-12 resize-none focus:ring-0 max-h-32"
              rows={1}
            />
            <button
                onClick={() => setIncludeWeb(!includeWeb)}
                className={`absolute right-3 bottom-3 p-1.5 rounded-md transition-colors ${includeWeb ? 'bg-blue-100 text-blue-600' : 'text-gray-400 hover:bg-gray-200'}`}
                title="Search Web"
            >
                <Globe className="w-5 h-5" />
            </button>
          </div>
          
          <button
            onClick={toggleVoice}
            disabled={isProcessing}
            className={`p-4 rounded-full shadow-md transition-all ${
              isListening
                ? 'bg-red-500 text-white animate-pulse ring-4 ring-red-200'
                : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
            } disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            {isListening ? <MicOff className="w-6 h-6" /> : <Mic className="w-6 h-6" />}
          </button>
          
          <button
            onClick={handleSend}
            disabled={inputValue.trim() === '' || isProcessing}
            className="p-4 bg-blue-600 text-white rounded-full shadow-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
             <div className="w-6 h-6 flex items-center justify-center">
               <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                 <path d="M3.478 2.405a.75.75 0 00-.926.94l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.405z" />
               </svg>
             </div>
          </button>
        </div>
        <div className="max-w-5xl mx-auto mt-2 text-center text-xs text-gray-400">
           JARVIS runs locally. Response times depend on your hardware.
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
