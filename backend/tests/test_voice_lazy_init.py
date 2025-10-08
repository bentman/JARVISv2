import io
import wave
import pytest

from app.services.voice_service import VoiceService


def make_silence_wav_bytes(duration_sec=0.1, sample_rate=16000):
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        nframes = int(duration_sec * sample_rate)
        wf.writeframes(b"\x00\x00" * nframes)
    return buf.getvalue()


def test_voice_service_lazy_stt_not_available(monkeypatch):
    # Create a new instance (don't use global) to control behavior
    vs = VoiceService()

    # Force _find_whisper_model to raise, simulating absence
    monkeypatch.setattr(vs, "_find_whisper_model", lambda: (_ for _ in ()).throw(Exception("no whisper")))

    audio_bytes = make_silence_wav_bytes()

    with pytest.raises(Exception) as exc:
        vs.speech_to_text(audio_bytes)
    msg = str(exc.value).lower()
    assert "whisper stt not available" in msg or "not found" in msg
