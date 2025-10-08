#!/usr/bin/env python3
"""
Minimal always-on voice loop client for Local AI Assistant.
- Continuously records short audio windows from the system microphone
- Sends each window to /api/v1/voice/session (wake->STT->chat->TTS)
- If wake word is detected by the backend, plays assistant audio
- Supports simple barge-in: stops playback if a new wake word is detected

Requirements (host environment):
  pip install sounddevice soundfile simpleaudio requests

Usage:
  python scripts/voice_loop.py --host http://localhost:8000 --window-sec 1.5 --rate 16000 --device none

Notes:
- Uses backend-side wake word detection (openwakeword if available). If not detected, the server returns detected=false.
- Maintains a conversation_id so each detected turn stays in the same thread.
- For best results, set PRIVACY and SEARCH settings as desired.
"""
import argparse
import base64
import io
import json
import sys
import threading
import time
import wave
from typing import Optional

import requests

try:
    import sounddevice as sd
    import numpy as np
except Exception as e:
    print("[voice_loop] Missing dependency: sounddevice (pip install sounddevice). Error:", e)
    sys.exit(1)

try:
    import simpleaudio as sa
except Exception as e:
    print("[voice_loop] Missing dependency: simpleaudio (pip install simpleaudio). Error:", e)
    sys.exit(1)


def float_to_wav_bytes(audio: np.ndarray, samplerate: int) -> bytes:
    """Convert float32 mono audio (-1..1) to 16-bit PCM WAV bytes."""
    # Ensure mono
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    # clip and scale
    audio = np.clip(audio, -1.0, 1.0)
    pcm = (audio * 32767.0).astype(np.int16)
    with io.BytesIO() as buf:
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(samplerate)
            wf.writeframes(pcm.tobytes())
        return buf.getvalue()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="http://localhost:8000", help="Backend host URL")
    ap.add_argument("--window-sec", type=float, default=1.5, help="Recording window in seconds for detection")
    ap.add_argument("--rate", type=int, default=16000, help="Sample rate (Hz)")
    ap.add_argument("--device", default=None, help="Input device name or index (default system)")
    ap.add_argument("--mode", default="chat", help="Chat mode: chat|coding|reasoning")
    ap.add_argument("--include-web", action="store_true", help="Include unified web search if privacy allows")
    ap.add_argument("--escalate-llm", action="store_true", help="Use remote LLM summarization for web (if configured)")
    args = ap.parse_args()

    session_url = f"{args.host.rstrip('/')}/api/v1/voice/session"

    # Track conversation across turns
    conversation_id: Optional[str] = None

    # Playback controller
    play_lock = threading.Lock()
    current_play: Optional[sa.PlayObject] = None

    def stop_playback():
        nonlocal current_play
        with play_lock:
            try:
                if current_play is not None and current_play.is_playing():
                    current_play.stop()
            except Exception:
                pass
            current_play = None

    def play_wav_bytes(wav_bytes: bytes):
        nonlocal current_play
        try:
            with play_lock:
                # Stop any existing playback (barge-in)
                if current_play is not None and current_play.is_playing():
                    current_play.stop()
                wave_obj = sa.WaveObject.from_wave_read(wave.open(io.BytesIO(wav_bytes)))
                current_play = wave_obj.play()
        except Exception as e:
            print("[voice_loop] Playback error:", e)

    # Configure input stream
    samplerate = args.rate
    channels = 1
    blocksize = int(args.window_sec * samplerate)

    print("[voice_loop] Starting. Press Ctrl+C to stop.")
    try:
        while True:
            # Record a short window
            audio = sd.rec(frames=blocksize, samplerate=samplerate, channels=channels, dtype="float32", device=args.device)
            sd.wait()
            wav_bytes = float_to_wav_bytes(audio.flatten(), samplerate)
            payload = {
                "audio_data": base64.b64encode(wav_bytes).decode("utf-8"),
                "conversation_id": conversation_id,
                "mode": args.mode,
                "include_web": bool(args.include_web),
                "escalate_llm": bool(args.escalate_llm),
            }
            try:
                r = requests.post(session_url, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=60)
                if r.status_code != 200:
                    # Budget or other errors are non-fatal to loop
                    print("[voice_loop] Session error:", r.status_code, r.text[:200])
                    # Backoff a bit to avoid hammering
                    time.sleep(0.2)
                    continue
                resp = r.json()
            except Exception as e:
                print("[voice_loop] Request failed:", e)
                time.sleep(0.5)
                continue

            if not isinstance(resp, dict):
                continue
            if not resp.get("detected"):
                # No wake word; continue listening
                continue

            # Stop any current playback (barge-in)
            stop_playback()

            # Update conversation; play assistant audio
            conversation_id = resp.get("conversation_id") or conversation_id
            audio_b64 = resp.get("audio_data")
            if isinstance(audio_b64, str) and audio_b64:
                try:
                    audio_bytes = base64.b64decode(audio_b64)
                    play_wav_bytes(audio_bytes)
                except Exception as e:
                    print("[voice_loop] Could not play audio:", e)
            else:
                print("[voice_loop] No audio returned from server.")

            # Small delay to avoid immediate re-trigger while assistant responds
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n[voice_loop] Stopping...")
        stop_playback()
        return


if __name__ == "__main__":
    main()
