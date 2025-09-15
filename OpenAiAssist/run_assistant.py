#!/usr/bin/env python3
import os
import sys
import subprocess
import venv
import shutil
import platform
from pathlib import Path

# -------------------------
# CONFIG
# -------------------------
VENV_DIR = Path(".venv")
PYTHON_BIN = VENV_DIR / "bin" / "python" if platform.system() != "Windows" else VENV_DIR / "Scripts" / "python.exe"
PIP_BIN = VENV_DIR / "bin" / "pip" if platform.system() != "Windows" else VENV_DIR / "Scripts" / "pip.exe"

REQUIREMENTS = [
    "flask",
    "flask-socketio",
    "eventlet",
    "transformers",
    "torch",
    "sounddevice",
    "soundfile",
    "speechrecognition",
    "gtts",
]

DOCKER_COMPOSE_YML = """\
services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    volumes:
      - ./backend:/app
"""

BACKEND_DOCKERFILE = """\
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "server.py"]
"""

BACKEND_REQUIREMENTS = """\
flask
flask-socketio
eventlet
transformers
torch
sounddevice
soundfile
speechrecognition
gtts
"""

BACKEND_SERVER = """\
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import speech_recognition as sr
from gtts import gTTS
import os
import io

app = Flask(__name__, template_folder="templates", static_folder="static")
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("speech_in")
def handle_speech(data):
    text = data.get("text", "")
    print(f"[CLIENT] {text}")
    response = f"Echo: {text}"
    # Generate voice output
    tts = gTTS(response)
    tts.save("static/response.mp3")
    emit("speech_out", {"text": response, "audio": "/static/response.mp3"})

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
"""

FRONTEND_HTML = """\
<!DOCTYPE html>
<html>
<head>
  <title>Assistant</title>
  <meta charset="utf-8"/>
  <style>
    body { font-family: sans-serif; background: #f9f9f9; margin: 2em; }
    #log { border: 1px solid #ccc; padding: 1em; background: white; height: 200px; overflow-y: auto; }
    button { margin: 0.5em; padding: 0.5em 1em; }
  </style>
</head>
<body>
  <h1>Voice Assistant</h1>
  <div id="log"></div>
  <button onclick="startRec()">🎙️ Start</button>
  <audio id="player" controls></audio>

  <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
  <script>
    const socket = io();

    function log(msg) {
      const logEl = document.getElementById("log");
      logEl.innerHTML += "<div>" + msg + "</div>";
      logEl.scrollTop = logEl.scrollHeight;
    }

    function startRec() {
      const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
      recognition.lang = "en-US";
      recognition.onresult = (event) => {
        const text = event.results[0][0].transcript;
        log("You: " + text);
        socket.emit("speech_in", { text: text });
      };
      recognition.start();
    }

    socket.on("speech_out", (data) => {
      log("AI: " + data.text);
      const player = document.getElementById("player");
      player.src = data.audio;
      player.play();
    });
  </script>
</body>
</html>
"""

# -------------------------
# HELPERS
# -------------------------
def run(cmd, check=True):
    print(f"[RUN] {cmd}")
    subprocess.run(cmd, shell=True, check=check)

def ensure_venv():
    if not VENV_DIR.exists():
        print("[INFO] Creating venv...")
        venv.create(VENV_DIR, with_pip=True)
    # Update pip correctly (no direct pip call)
    run(f"{PYTHON_BIN} -m pip install --upgrade pip")
    run(f"{PYTHON_BIN} -m pip install " + " ".join(REQUIREMENTS))

def prepare_backend():
    backend_dir = Path("backend")
    backend_dir.mkdir(exist_ok=True)
    (backend_dir / "templates").mkdir(exist_ok=True)
    (backend_dir / "static").mkdir(exist_ok=True)

    (backend_dir / "requirements.txt").write_text(BACKEND_REQUIREMENTS, encoding="utf-8")
    (backend_dir / "server.py").write_text(BACKEND_SERVER, encoding="utf-8")
    (backend_dir / "templates" / "index.html").write_text(FRONTEND_HTML, encoding="utf-8")
    (backend_dir / "Dockerfile").write_text(BACKEND_DOCKERFILE, encoding="utf-8")

    Path("docker-compose.yml").write_text(DOCKER_COMPOSE_YML, encoding="utf-8")

def launch_docker():
    run("docker compose up --build")

# -------------------------
# MAIN
# -------------------------
if __name__ == "__main__":
    ensure_venv()
    prepare_backend()
    launch_docker()
