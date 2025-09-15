import React, { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import { Volume2, User, Bot, Code, Brain, MessageSquare } from 'lucide-react';
import 'highlight.js/styles/github.css';

interface ChatMessage {
  id: string;
  message: string;
  response: string;
  messageType?: 'chat' | 'code' | 'reasoning';
  timestamp: string;
}

interface ChatInterfaceProps {
  messages: ChatMessage[];
  isLoading: boolean;
  onSpeakResponse: (text: string) => void;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  isLoading,
  onSpeakResponse,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const getMessageTypeIcon = (type?: string) => {
    switch (type) {
      case 'code':
        return <Code className="w-4 h-4 text-green-600" />;
      case 'reasoning':
        return <Brain className="w-4 h-4 text-purple-600" />;
      default:
        return <MessageSquare className="w-4 h-4 text-blue-600" />;
    }
  };

  const getMessageTypeColor = (type?: string) => {
    switch (type) {
      case 'code':
        return 'border-l-4 border-green-500';
      case 'reasoning':
        return 'border-l-4 border-purple-500';
      default:
        return 'border-l-4 border-blue-500';
    }
  };

  return (
    <div className="flex-1 overflow-hidden bg-gray-50">
      <div className="h-full overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && !isLoading && (
          <div className="flex items-center justify-center h-full text-gray-500">
            <div className="text-center">
              <Bot className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <h3 className="text-lg font-medium mb-2">Welcome to AI Assistant</h3>
              <p className="text-sm">
                Start a conversation, ask for help with code, or request detailed reasoning.
              </p>
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div key={message.id} className="space-y-4">
            {/* User Message */}
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
                  <User className="w-4 h-4 text-white" />
                </div>
              </div>
              <div className={`flex-1 bg-white rounded-lg p-4 shadow-sm ${getMessageTypeColor(message.messageType)}`}>
                <div className="flex items-center space-x-2 mb-2">
                  {getMessageTypeIcon(message.messageType)}
                  <span className="text-sm font-medium text-gray-700 capitalize">
                    {message.messageType || 'chat'}
                  </span>
                  <span className="text-xs text-gray-500">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <div className="text-gray-800 whitespace-pre-wrap">
                  {message.message}
                </div>
              </div>
            </div>

            {/* Assistant Response */}
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
                  <Bot className="w-4 h-4 text-white" />
                </div>
              </div>
              <div className="flex-1 bg-white rounded-lg p-4 shadow-sm">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">
                    Assistant
                  </span>
                  <button
                    onClick={() => onSpeakResponse(message.response)}
                    className="p-1 text-gray-400 hover:text-gray-600 rounded"
                    title="Speak response"
                  >
                    <Volume2 className="w-4 h-4" />
                  </button>
                </div>
                <div className="prose prose-sm max-w-none">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    rehypePlugins={[rehypeHighlight]}
                    components={{
                      code: ({ node, inline, className, children, ...props }) => {
                        const match = /language-(\w+)/.exec(className || '');
                        return !inline && match ? (
                          <div className="relative">
                            <div className="absolute top-2 right-2 text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                              {match[1]}
                            </div>
                            <pre className={className} {...props}>
                              <code>{children}</code>
                            </pre>
                          </div>
                        ) : (
                          <code className="bg-gray-100 px-1 py-0.5 rounded text-sm" {...props}>
                            {children}
                          </code>
                        );
                      },
                    }}
                  >
                    {message.response}
                  </ReactMarkdown>
                </div>
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
                <Bot className="w-4 h-4 text-white" />
              </div>
            </div>
            <div className="flex-1 bg-white rounded-lg p-4 shadow-sm">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                <span className="text-sm text-gray-500 ml-2">Thinking...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default ChatInterface;