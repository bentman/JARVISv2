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
