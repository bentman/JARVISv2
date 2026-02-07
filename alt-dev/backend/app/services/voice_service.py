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
    Lazy-initializes external executables to avoid startup failures if absent.
    """
    
    def __init__(self):
        # Wake word model is lightweight to try at startup; ignore failures.
        self.wake_word_model = self._init_wake_word()
        # Defer heavy executable discovery until first use
        self.stt_model = None
        self.tts_model = None
        self.piper_voice = None
        # No _initialize_models at import-time
        
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
    
    def _find_piper_model(self) -> str | None:
        """
        Find Piper TTS executable if present; do not attempt installation here.
        Returns absolute path or None if not found.
        """
        from shutil import which as _which
        # Common locations and PATH
        possible_paths = [
            "/usr/local/bin/piper",
            "/opt/piper/bin/piper",
            "./piper/src/piper",
            settings.MODEL_PATH + "/piper/src/piper",
        ]
        for path in possible_paths:
            if Path(path).exists():
                return path
        resolved = _which("piper")
        return resolved
    
    def _find_piper_voice(self) -> str:
        """
        Find a suitable voice model for Piper.
        Preference order:
        - en_AU*.onnx (Australian English)
        - en_*.onnx (any English)
        - any *.onnx in the models directory
        """
        model_path = Path(settings.MODEL_PATH)
        # Gather all .onnx candidates
        onnx_files = list(model_path.glob("*.onnx"))
        if not onnx_files:
            return None
        # Prefer en_AU first
        au = [p for p in onnx_files if p.name.lower().startswith("en_au")]
        if au:
            return str(au[0])
        # Then any English
        en = [p for p in onnx_files if p.name.lower().startswith("en_")]
        if en:
            return str(en[0])
        # Fallback to any .onnx
        return str(onnx_files[0])
    
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
        """Deprecated: initialization happens lazily in ensure_* methods."""
        pass
        
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
        
    def _find_whisper_weights(self) -> str:
        """Find a suitable Whisper model weights file under MODEL_PATH."""
        candidates = [
            "ggml-base.en.bin",
            "ggml-base.bin",
            "ggml-small.en.bin",
            "ggml-small.bin",
            "ggml-medium.en.bin",
            "ggml-medium.bin",
            "ggml-large-v3.bin",
            "ggml-large.bin",
        ]
        base = Path(settings.MODEL_PATH)
        for name in candidates:
            p = base / name
            if p.exists():
                return str(p)
        # Fallback to any ggml-*.bin
        for p in base.glob("ggml-*.bin"):
            return str(p)
        raise FileNotFoundError("No Whisper model weights found under MODEL_PATH")

    def speech_to_text(self, audio_data: bytes) -> Tuple[str, float]:
        """
        Convert speech to text using Whisper
        Returns (transcribed_text, confidence)
        """
        import time
        from shutil import which
        start_time = time.time()

        # Ensure STT executable is available lazily
        if self.stt_model is None:
            try:
                self.stt_model = self._find_whisper_model()
            except Exception:
                raise Exception("Whisper STT not available")
        # Resolve executable path (PATH or absolute)
        stt_exec = self.stt_model
        if not Path(stt_exec).exists():
            resolved = which(stt_exec)
            if not resolved:
                raise Exception("Whisper STT executable not found in PATH")
            stt_exec = resolved
        # Resolve model weights
        try:
            whisper_weights = self._find_whisper_weights()
        except Exception as e:
            raise Exception(f"Whisper model weights not found: {str(e)}")
        
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
                    stt_exec,
                    "-m", whisper_weights,
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
        from shutil import which
        start_time = time.time()
        
        try:
            # Prefer Piper if available
            tts_exec = None
            if self.tts_model is None:
                try:
                    self.tts_model = self._find_piper_model()
                except Exception:
                    self.tts_model = None
            if self.tts_model:
                tts_exec = self.tts_model
                if not Path(tts_exec).exists():
                    resolved = which(tts_exec)
                    if resolved:
                        tts_exec = resolved
                    else:
                        tts_exec = None
            # Debug log which engine will be used
            try:
                engine_hint = "piper" if tts_exec else "espeak-ng"
                print(f"[voice] TTS engine selected: {engine_hint}")
            except Exception:
                pass
            # Fallback to espeak-ng if Piper unavailable
            if tts_exec is None:
                espeak = which("espeak-ng") or which("espeak")
                if not espeak:
                    raise Exception("No TTS engine available (piper/espeak-ng)")
                # Use espeak-ng to generate WAV directly
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_output:
                    temp_output_path = temp_output.name
                try:
                    v = getattr(settings, "TTS_PREFERRED_VOICE", None)
                    cmd = [espeak] + (["-v", v] if v else []) + ["-w", temp_output_path, text]
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                    try:
                        if v:
                            print(f"[voice] Using espeak-ng voice: {v}")
                    except Exception:
                        pass
                    if result.returncode != 0:
                        raise Exception(f"espeak-ng failed: {result.stderr}")
                    with open(temp_output_path, 'rb') as audio_file:
                        return audio_file.read()
                finally:
                    try:
                        os.unlink(temp_output_path)
                    except Exception:
                        pass
            # Piper path: ensure voice model
            if self.piper_voice is None:
                self.piper_voice = self._find_piper_voice()
            if not self.piper_voice:
                # If no Piper voice but we have espeak, fallback
                espeak = which("espeak-ng") or which("espeak")
                if espeak:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_output:
                        temp_output_path = temp_output.name
                    try:
                        cmd = [espeak, "-w", temp_output_path, text]
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                        if result.returncode != 0:
                            raise Exception(f"espeak-ng failed: {result.stderr}")
                        with open(temp_output_path, 'rb') as audio_file:
                            return audio_file.read()
                    finally:
                        try:
                            os.unlink(temp_output_path)
                        except Exception:
                            pass
                raise Exception("No voice model found for Piper TTS")

            # Use Piper
            tts_exec_final = tts_exec
            # Create temporary files
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".txt") as temp_input:
                temp_input.write(text)
                temp_input_path = temp_input.name
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_output:
                temp_output_path = temp_output.name
            try:
                cmd = [
                    tts_exec_final,
                    "--model", self.piper_voice,
                    "--output_file", temp_output_path
                ]
                with open(temp_input_path, 'r') as input_file:
                    result = subprocess.run(
                        cmd,
                        stdin=input_file,
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                if result.returncode != 0:
                    # Piper failed (possibly due to invalid/placeholder voice); fallback to espeak-ng if available
                    from shutil import which as _which
                    espeak = _which("espeak-ng") or _which("espeak")
                    if espeak:
                        # Generate WAV via espeak-ng
                        try:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_es_wav:
                                temp_es_wav_path = temp_es_wav.name
                            v = getattr(settings, "TTS_PREFERRED_VOICE", None)
                            es_cmd = [espeak, "-w", temp_es_wav_path] + (["-v", v] if v else []) + [text]
                            es_res = subprocess.run(es_cmd, capture_output=True, text=True, timeout=60)
                            if es_res.returncode == 0:
                                try:
                                    print("[voice] Piper failed, fell back to espeak-ng")
                                except Exception:
                                    pass
                                with open(temp_es_wav_path, 'rb') as audio_file:
                                    return audio_file.read()
                        finally:
                            try:
                                os.unlink(temp_es_wav_path)
                            except Exception:
                                pass
                    # No fallback available, raise
                    raise Exception(f"Piper TTS failed with error: {result.stderr}")
                with open(temp_output_path, 'rb') as audio_file:
                    audio_bytes = audio_file.read()
                return audio_bytes
            finally:
                try:
                    os.unlink(temp_input_path)
                except Exception:
                    pass
                try:
                    os.unlink(temp_output_path)
                except Exception:
                    pass
                try:
                    os.unlink(temp_output_path)
                except Exception:
                    pass
        except subprocess.TimeoutExpired:
            raise Exception("Text-to-speech conversion timed out")
        except Exception as e:
            raise Exception(f"Error during text-to-speech conversion: {str(e)}")
        


# Global voice service instance
voice_service = VoiceService()
