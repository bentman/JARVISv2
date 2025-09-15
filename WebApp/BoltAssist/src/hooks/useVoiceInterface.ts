import { useState, useCallback, useRef, useEffect } from 'react';
import { VoiceState } from '../types';
import { VoiceService } from '../services/voiceService';

export function useVoiceInterface() {
  const [voiceState, setVoiceState] = useState<VoiceState>({
    isListening: false,
    isProcessing: false,
    isSpeaking: false,
    isEnabled: false
  });
  
  const voiceServiceRef = useRef<VoiceService>();
  const [permissionGranted, setPermissionGranted] = useState(false);

  // Initialize voice service
  const initializeVoice = useCallback(async () => {
    if (!voiceServiceRef.current) {
      voiceServiceRef.current = new VoiceService();
      
      const isSupported = voiceServiceRef.current.isSupported();
      setVoiceState(prev => ({ ...prev, isEnabled: isSupported }));
      
      if (isSupported) {
        // Request permissions
        const hasPermission = await voiceServiceRef.current.requestPermissions();
        setPermissionGranted(hasPermission);
        
        if (!hasPermission) {
          setVoiceState(prev => ({ ...prev, isEnabled: false }));
        }
      }
    }
  }, []);

  const startListening = useCallback(async (): Promise<string | null> => {
    if (!voiceServiceRef.current || !voiceState.isEnabled || !permissionGranted) {
      return null;
    }

    try {
      setVoiceState(prev => ({ ...prev, isListening: true, isProcessing: false }));
      
      const transcript = await voiceServiceRef.current.startListening();
      
      setVoiceState(prev => ({ ...prev, isListening: false, isProcessing: false }));
      
      return transcript;
    } catch (error) {
      console.error('Speech recognition failed:', error);
      setVoiceState(prev => ({ ...prev, isListening: false, isProcessing: false }));
      return null;
    }
  }, [voiceState.isEnabled, permissionGranted]);

  const stopListening = useCallback(() => {
    if (voiceServiceRef.current) {
      voiceServiceRef.current.stopListening();
      setVoiceState(prev => ({ ...prev, isListening: false }));
    }
  }, []);

  const speak = useCallback(async (text: string): Promise<void> => {
    if (!voiceServiceRef.current || !voiceState.isEnabled) {
      return;
    }

    try {
      setVoiceState(prev => ({ ...prev, isSpeaking: true }));
      await voiceServiceRef.current.speak(text);
    } catch (error) {
      console.error('Speech synthesis failed:', error);
    } finally {
      setVoiceState(prev => ({ ...prev, isSpeaking: false }));
    }
  }, [voiceState.isEnabled]);

  const toggleListening = useCallback(async () => {
    if (voiceState.isListening) {
      stopListening();
      return null;
    } else {
      return await startListening();
    }
  }, [voiceState.isListening, startListening, stopListening]);

  const toggleSpeech = useCallback(() => {
    if (voiceState.isSpeaking) {
      voiceServiceRef.current?.stopSpeaking();
      setVoiceState(prev => ({ ...prev, isSpeaking: false }));
    }
  }, [voiceState.isSpeaking]);

  return {
    voiceState,
    permissionGranted,
    initializeVoice,
    startListening,
    stopListening,
    speak,
    toggleListening,
    toggleSpeech
  };
}