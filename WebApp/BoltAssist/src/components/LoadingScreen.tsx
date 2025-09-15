import React from 'react';
import { Cpu, Loader } from 'lucide-react';

export function LoadingScreen() {
  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center">
      <div className="text-center space-y-6">
        <div className="flex justify-center">
          <div className="relative">
            <Cpu className="w-16 h-16 text-blue-400" />
            <Loader className="w-6 h-6 text-blue-400 absolute -bottom-2 -right-2 animate-spin" />
          </div>
        </div>
        
        <div className="space-y-2">
          <h1 className="text-2xl font-bold text-white">Local AI Assistant</h1>
          <p className="text-gray-400">Detecting hardware capabilities...</p>
        </div>
        
        <div className="flex items-center justify-center gap-2">
          <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
          <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
          <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
        </div>
        
        <div className="text-xs text-gray-500 max-w-md">
          <p>Analyzing CPU cores, memory, GPU availability...</p>
          <p>Selecting optimal model profile for your device</p>
        </div>
      </div>
    </div>
  );
}