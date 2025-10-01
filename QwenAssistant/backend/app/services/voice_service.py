import base64
import io
import tempfile
import os
import subprocess
from pathlib import Path
from typing import Tuple
from app.core.config import settings

class VoiceService:
    """
    Voice service for speech-to-text and text-to-speech conversion
    Uses Whisper for STT and Piper for TTS
    Includes local wake word detection (prefers openwakeword if available; falls back to STT-based keyword check).
    """
    
    def __init__(self):
        self.wake_word_model = self._init_wake_word()
        self.stt_model = self._find_whisper_model()
        self.tts_model = self._find_piper_model()
        self.piper_voice = self._find_piper_voice()
        self._initialize_models()
        
    def _init_wake_word(self):
        """Initialize openwakeword model if available; return None otherwise."""
        try:
            from openwakeword.model import Model as OWWModel
            # Load default prepackaged wake words; allow external models via env if provided
            return OWWModel()
        except Exception:
            return None
        
    def _find_whisper_model(self) -> str:
        """
        Find Whisper model for speech-to-text
        """
        # Common locations for Whisper models
        possible_paths = [
            "/usr/local/bin/whisper",
            "/opt/whisper/bin/whisper",
            "./whisper.cpp/whisper",  # Local build
            settings.MODEL_PATH + "/whisper.cpp/whisper",  # Model directory
            "whisper",
            "whisper-cpp"
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                return path
        
        # If not found, try to install Whisper.cpp
        self._install_whisper()
        return "whisper"
    
    def _find_piper_model(self) -> str:
        """
        Find Piper TTS model
        """
        # Common locations for Piper TTS
        possible_paths = [
            "/usr/local/bin/piper",
            "/opt/piper/bin/piper",
            "./piper/src/piper",  # Local build
            settings.MODEL_PATH + "/piper/src/piper",  # Model directory
            "piper"
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                return path
        
        # If not found, try to install Piper
        self._install_piper()
        return "piper"
    
    def _find_piper_voice(self) -> str:
        """
        Find a suitable voice model for Piper
        """
        # Look for voice files in the models directory
        model_path = Path(settings.MODEL_PATH)
        voice_files = list(model_path.glob("*piper*voice*"))
        
        if voice_files:
            return str(voice_files[0])
        
        # Default English voice if found
        en_voice = model_path / "en-us-kathleen-low.onnx"
        if en_voice.exists():
            return str(en_voice)
        
        # If no voice model is found, return None and handle in text_to_speech
        return None
    
    def _install_whisper(self):
        """
        Install Whisper.cpp if not found
        """
        print("Installing Whisper.cpp...")
        try:
            # Clone the repository
            subprocess.run(["git", "clone", "https://github.com/ggerganov/whisper.cpp.git"], check=True)
            os.chdir("whisper.cpp")
            # Build whisper.cpp
            subprocess.run(["make"], check=True)
            os.chdir("..")
            print("Whisper.cpp installed successfully")
        except subprocess.CalledProcessError:
            print("Failed to install Whisper.cpp automatically. Please install manually.")
            raise
    
    def _install_piper(self):
        """
        Install Piper TTS if not found
        """
        print("Installing Piper TTS...")
        try:
            # Clone the repository
            subprocess.run(["git", "clone", "https://github.com/rhasspy/piper.git"], check=True)
            os.chdir("piper")
            # Build Piper TTS
            subprocess.run(["cargo", "build", "--release"], check=True)
            os.chdir("..")
            print("Piper TTS installed successfully")
        except subprocess.CalledProcessError:
            print("Failed to install Piper TTS. Make sure you have Rust installed.")
            raise
    
    def _initialize_models(self):
        """Initialize voice models"""
        # In a real implementation, this would load the models
        # For now, we'll just verify the executables exist
        if not Path(self.stt_model).exists():
            raise FileNotFoundError(f"Whisper STT model not found at {self.stt_model}")
        
        if not Path(self.tts_model).exists():
            raise FileNotFoundError(f"Piper TTS model not found at {self.tts_model}")
        
        print("Voice models initialized successfully")
        
    def detect_wake_word(self, audio_data: bytes) -> bool:
        """
        Detect wake word in audio stream
        Returns True if wake word is detected
        """
        # Preferred: use openwakeword if available
        if self.wake_word_model is not None:
            try:
                # Decode WAV bytes to float32 mono 16kHz numpy array
                import io
                import wave
                import numpy as np
                with wave.open(io.BytesIO(audio_data), "rb") as wf:
                    n_channels = wf.getnchannels()
                    sampwidth = wf.getsampwidth()
                    framerate = wf.getframerate()
                    frames = wf.getnframes()
                    pcm_bytes = wf.readframes(frames)
                # Convert bytes to int16 assuming 16-bit PCM
                if sampwidth != 2:
                    return False  # unsupported format for now
                pcm = np.frombuffer(pcm_bytes, dtype=np.int16)
                if n_channels > 1:
                    pcm = pcm.reshape(-1, n_channels).mean(axis=1).astype(np.int16)
                # Resample if needed to 16000 Hz
                target_sr = 16000
                if framerate != target_sr:
                    # Simple linear resample
                    import numpy as np
                    x_old = np.linspace(0, 1, num=len(pcm), endpoint=False)
                    x_new = np.linspace(0, 1, num=int(len(pcm) * target_sr / framerate), endpoint=False)
                    pcm = np.interp(x_new, x_old, pcm).astype(np.int16)
                audio = (pcm.astype(np.float32) / 32768.0).reshape(1, -1)
                scores = self.wake_word_model.predict(audio)
                # scores is a dict of wakeword -> score; trigger if any exceeds threshold
                for _kw, score in scores.items():
                    if isinstance(score, (list, tuple, np.ndarray)):
                        val = float(np.max(score))
                    else:
                        val = float(score)
                    if val >= 0.5:
                        return True
            except Exception:
                # Fall back to STT-based approach below
                pass

        # Fallback: STT + keyword spotting
        try:
            transcription, _confidence = self.speech_to_text(audio_data)
            wake_words = ["hello assistant", "hey assistant", "assistant", "qwen", "wake up"]
            for word in wake_words:
                if word.lower() in transcription.lower():
                    return True
        except Exception:
            pass
        return False
        
    def speech_to_text(self, audio_data: bytes) -> Tuple[str, float]:
        """
        Convert speech to text using Whisper
        Returns (transcribed_text, confidence)
        """
        import time
        start_time = time.time()
        
        try:
            # Write audio data to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
                temp_audio.write(audio_data)
                temp_audio_path = temp_audio.name
            
            # Create temporary file for output
            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_output:
                temp_output_path = temp_output.name
            
            try:
                # Prepare the whisper command
                cmd = [
                    self.stt_model,
                    "-m", f"{settings.MODEL_PATH}/ggml-large.bin",  # Whisper model path
                    "-f", temp_audio_path,
                    "-otxt", temp_output_path
                ]
                
                # Run the whisper command
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=120  # 2 minute timeout for transcription
                )
                
                if result.returncode != 0:
                    raise Exception(f"Whisper failed with error: {result.stderr}")
                
                # Read the transcribed text
                with open(temp_output_path, 'r') as f:
                    transcribed_text = f.read().strip()
                
                # Calculate confidence (placeholder - in real implementation, 
                # this would come from the model output)
                execution_time = time.time() - start_time
                confidence = min(0.95, max(0.6, 1.0 - (execution_time / 10.0)))  # Basic confidence estimation
                
                return transcribed_text, confidence
                
            finally:
                # Clean up temporary files
                os.unlink(temp_audio_path)
                os.unlink(temp_output_path)
                
        except subprocess.TimeoutExpired:
            raise Exception("Speech-to-text conversion timed out")
        except Exception as e:
            raise Exception(f"Error during speech-to-text conversion: {str(e)}")
        
    def text_to_speech(self, text: str) -> bytes:
        """
        Convert text to speech using Piper TTS
        Returns audio data as bytes
        """
        import time
        start_time = time.time()
        
        try:
            # Ensure we have a voice model
            if not self.piper_voice:
                raise Exception("No voice model found for Piper TTS")
            
            # Create temporary files
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".txt") as temp_input:
                temp_input.write(text)
                temp_input_path = temp_input.name
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_output:
                temp_output_path = temp_output.name
            
            try:
                # Prepare the Piper command
                cmd = [
                    self.tts_model,
                    "--model", self.piper_voice,
                    "--output_file", temp_output_path
                ]
                
                # Run the Piper command with text input
                with open(temp_input_path, 'r') as input_file:
                    result = subprocess.run(
                        cmd,
                        stdin=input_file,
                        capture_output=True,
                        text=True,
                        timeout=120  # 2 minute timeout for TTS
                    )
                
                if result.returncode != 0:
                    raise Exception(f"Piper TTS failed with error: {result.stderr}")
                
                # Read the generated audio
                with open(temp_output_path, 'rb') as audio_file:
                    audio_bytes = audio_file.read()
                
                return audio_bytes
                
            finally:
                # Clean up temporary files
                os.unlink(temp_input_path)
                os.unlink(temp_output_path)
                
        except subprocess.TimeoutExpired:
            raise Exception("Text-to-speech conversion timed out")
        except Exception as e:
            raise Exception(f"Error during text-to-speech conversion: {str(e)}")


# Global voice service instance
voice_service = VoiceService()