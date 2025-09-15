import React from 'react';
import { Mic, MicOff, Square } from 'lucide-react';

interface VoiceControlsProps {
  isRecording: boolean;
  onStartRecording: () => void;
  onStopRecording: () => void;
}

const VoiceControls: React.FC<VoiceControlsProps> = ({
  isRecording,
  onStartRecording,
  onStopRecording,
}) => {
  return (
    <div className="flex items-center">
      {!isRecording ? (
        <button
          onClick={onStartRecording}
          className="p-2 text-gray-600 hover:text-primary-600 hover:bg-primary-50 rounded-full transition-colors"
          title="Start voice recording"
        >
          <Mic className="w-5 h-5" />
        </button>
      ) : (
        <button
          onClick={onStopRecording}
          className="p-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-full transition-colors animate-pulse"
          title="Stop voice recording"
        >
          <Square className="w-5 h-5 fill-current" />
        </button>
      )}
    </div>
  );
};

export default VoiceControls;