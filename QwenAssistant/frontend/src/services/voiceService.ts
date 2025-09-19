import { invoke } from '@tauri-apps/api/tauri';

export class VoiceService {
  private isListening = false;
  private audioContext: AudioContext | null = null;
  private mediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];

  async startListening(): Promise<void> {
    if (this.isListening) return;

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.audioContext = new AudioContext();
      this.mediaRecorder = new MediaRecorder(stream);
      this.audioChunks = [];

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data);
        }
      };

      this.mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
        await this.processAudio(audioBlob);
        this.audioChunks = [];
      };

      this.mediaRecorder.start();
      this.isListening = true;
    } catch (error) {
      console.error('Error accessing microphone:', error);
      throw new Error('Could not access microphone. Please check permissions.');
    }
  }

  stopListening(): void {
    if (!this.isListening || !this.mediaRecorder) return;

    this.mediaRecorder.stop();
    this.isListening = false;

    // Stop all tracks
    if (this.mediaRecorder.stream) {
      this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
    }
  }

  private async processAudio(audioBlob: Blob): Promise<void> {
    try {
      // Convert blob to base64
      const base64Data = await this.blobToBase64(audioBlob);
      
      // Send to backend for processing
      const result = await invoke('process_voice_input', { audioData: base64Data });
      
      // Handle the result (this would depend on your backend response)
      console.log('Voice processing result:', result);
    } catch (error) {
      console.error('Error processing audio:', error);
    }
  }

  private blobToBase64(blob: Blob): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        if (typeof reader.result === 'string') {
          // Remove the data URL prefix
          const base64Data = reader.result.split(',')[1];
          resolve(base64Data);
        } else {
          reject(new Error('Failed to convert blob to base64'));
        }
      };
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  }

  async speak(text: string): Promise<void> {
    try {
      // Send text to backend for TTS conversion
      const base64Audio = await invoke('text_to_speech', { text });
      
      // Play the audio (this would require additional implementation)
      console.log('TTS result received:', base64Audio);
    } catch (error) {
      console.error('Error with text-to-speech:', error);
    }
  }

  isVoiceActive(): boolean {
    return this.isListening;
  }
}