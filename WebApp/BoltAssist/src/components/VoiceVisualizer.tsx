import React, { useEffect, useState } from 'react';
import { VoiceState } from '../types';

interface VoiceVisualizerProps {
  voiceState: VoiceState;
}

export function VoiceVisualizer({ voiceState }: VoiceVisualizerProps) {
  const [levels, setLevels] = useState<number[]>(new Array(20).fill(0));

  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (voiceState.isListening) {
      interval = setInterval(() => {
        setLevels(prev => prev.map(() => Math.random() * 0.8 + 0.2));
      }, 100);
    } else {
      setLevels(new Array(20).fill(0));
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [voiceState.isListening]);

  if (!voiceState.isListening && !voiceState.isProcessing) {
    return null;
  }

  return (
    <div className="fixed bottom-24 left-1/2 transform -translate-x-1/2 bg-gray-800/90 backdrop-blur-sm p-4 rounded-xl border border-gray-700">
      <div className="flex items-center gap-4">
        <div className="flex items-end gap-1 h-8">
          {levels.map((level, index) => (
            <div
              key={index}
              className="w-1 bg-gradient-to-t from-blue-600 to-blue-400 rounded-full transition-all duration-100"
              style={{
                height: `${level * 100}%`,
                minHeight: '4px'
              }}
            />
          ))}
        </div>
        
        <div className="text-sm">
          {voiceState.isListening && (
            <p className="text-white font-medium">Listening...</p>
          )}
          {voiceState.isProcessing && (
            <p className="text-blue-400 font-medium">Processing speech...</p>
          )}
          {voiceState.isSpeaking && (
            <p className="text-green-400 font-medium">Speaking...</p>
          )}
        </div>
      </div>
    </div>
  );
}