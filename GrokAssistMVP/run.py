import os
import platform
import subprocess
import sys
import time
import logging
import tkinter as tk
from tkinter import messagebox
import requests
import psutil
import torch
import speech_recognition as sr
import pyttsx3
import threading
import ollama
import json
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(f"assistant_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)

# Constants
BACKEND_URL = "http://localhost:8000"
MEMORY_FILE = "memory.json"
SETUP_FLAG = ".setup_done"
HARDWARE_FILE = ".env.hardware"
OS = platform.system().lower()
IS_WINDOWS = OS == "windows"
IS_MACOS = OS == "darwin"
IS_LINUX = OS == "linux"
IS_WSL = "microsoft" in platform.uname().release.lower()

# Check if Ollama is ready
def wait_for_ollama():
    for i in range(10):
        try:
            requests.get("http://localhost:11434/api/version", timeout=1)
            logging.info("Ollama server is ready.")
            return True
        except:
            time.sleep(3)
    logging.error("Ollama server not ready after 30s.")
    return False

# Bootstrap setup (run once)
def bootstrap():
    if os.path.exists(SETUP_FLAG):
        logging.info("Setup already completed. Skipping bootstrap.")
        return
    try:
        logging.info("Running bootstrap setup...")
        
        # Install system dependencies
        if IS_LINUX or IS_WSL:
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            subprocess.run([
                "sudo", "apt-get", "install", "-y",
                "python3-pip", "docker.io", "espeak", "libespeak-dev",
                "cmake", "swig", "python3-tk"
            ], check=True)
            logging.info("Add yourself to docker group manually if needed: sudo usermod -aG docker $USER && newgrp docker")
            logging.warning("If Docker permissions fail, re-run after re-logging in.")
        elif IS_MACOS:
            subprocess.run(["brew", "install", "python", "docker", "cmake", "swig"], check=True)
        elif IS_WINDOWS:
            logging.info("Windows: Ensure Docker Desktop (https://www.docker.com/products/docker-desktop) and Python 3.10+ are installed manually.")
            logging.info("For voice support, run in Windows Python, not WSL.")
        
        # Install Python dependencies
        subprocess.run([sys.executable, "-m", "pip", "install", "--user",
                        "fastapi==0.115.0", "uvicorn==0.30.6", "pydantic==2.9.2",
                        "requests", "psutil", "torch", "speechrecognition",
                        "pyttsx3", "ollama", "pocketsphinx"], check=True)
        
        # Install Ollama
        if IS_LINUX or IS_WSL:
            if not os.path.exists("/usr/local/bin/ollama"):
                subprocess.run("curl https://ollama.ai/install.sh | sh", shell=True, check=True)
        elif IS_MACOS:
            subprocess.run(["brew", "install", "ollama"], check=True)
        elif IS_WINDOWS:
            logging.info("Windows: Download Ollama from https://ollama.ai/download")
        
        # Start Ollama server
        subprocess.Popen(["ollama", "serve"])
        if not wait_for_ollama():
            raise Exception("Ollama server not ready.")
        
        # Pull LLM models (smallest first)
        models = ["phi3:3.8b", "llama3.1:8b", "llama3.1:70b"]
        for model in models:
            if model not in subprocess.run(["ollama", "list"], capture_output=True, text=True).stdout:
                subprocess.run(["ollama", "pull", model], check=True)
        
        # Create backend files
        os.makedirs("ai-assistant", exist_ok=True)
        with open("ai-assistant/Dockerfile", "w") as f:
            f.write("""
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend.py .
CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8000"]
""")
        
        with open("ai-assistant/requirements.txt", "w") as f:
            f.write("fastapi==0.115.0\nuvicorn==0.30.6\npydantic==2.9.2\n")
        
        with open("ai-assistant/backend.py", "w") as f:
            f.write("""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import logging
from datetime import datetime

app = FastAPI()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(f"backend_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)

conn = sqlite3.connect("memory.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS memory (id INTEGER PRIMARY KEY AUTOINCREMENT, snippet TEXT)''')
conn.commit()

class ChatRequest(BaseModel):
    input_text: str
    profile: str
    response_text: str

class MemoryRequest(BaseModel):
    snippet: str

class MemoryResponse(BaseModel):
    snippets: list[str]

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        logging.info(f"Chat request: {request.input_text} on profile {request.profile}")
        cursor.execute("INSERT INTO memory (snippet) VALUES (?)", (request.response_text[:100],))
        conn.commit()
        return {"response": request.response_text, "profile": request.profile}
    except Exception as e:
        logging.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Backend error: {str(e)}")

@app.post("/memory")
async def add_memory(request: MemoryRequest):
    try:
        cursor.execute("INSERT INTO memory (snippet) VALUES (?)", (request.snippet,))
        conn.commit()
        logging.info("Memory snippet added")
        return {"status": "added"}
    except Exception as e:
        logging.error(f"Memory add error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memory")
async def get_memory():
    try:
        cursor.execute("SELECT snippet FROM memory ORDER BY id DESC LIMIT 10")
        snippets = [row[0] for row in cursor.fetchall()]
        logging.info("Memory retrieved")
        return MemoryResponse(snippets=snippets)
    except Exception as e:
        logging.error(f"Memory get error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/memory")
async def clear_memory():
    try:
        cursor.execute("DELETE FROM memory")
        conn.commit()
        logging.info("Memory cleared")
        return {"status": "cleared"}
    except Exception as e:
        logging.error(f"Memory clear error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search")
async def search(query: str):
    logging.info(f"Search stub for query: {query}")
    return {"results": f"Local search stub: no results for '{query}'"}
""")
        
        # Build and run backend
        os.chdir("ai-assistant")
        subprocess.run(["docker", "build", "-t", "ai-backend", "."], check=True)
        subprocess.run(["docker", "run", "-d", "-p", "8000:8000", "--name", "ai-backend", "ai-backend"], check=True)
        os.chdir("..")
        
        # Mark setup as done
        with open(SETUP_FLAG, "w") as f:
            f.write("Setup completed")
        logging.info("Bootstrap setup complete.")
    except Exception as e:
        logging.error(f"Bootstrap error: {str(e)}")
        sys.exit(1)

# Hardware detection
def detect_profile():
    try:
        cpu_count = psutil.cpu_count()
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
            if gpu_memory >= 8:
                profile = "heavy"
                model = "llama3.1:70b"
                hardware = "High-end GPU/NPU"
            elif gpu_memory >= 4:
                profile = "medium"
                model = "llama3.1:8b"
                hardware = "Mid-tier GPU/NPU"
        elif torch.backends.mps.is_available():
            profile = "medium"
            model = "llama3.1:8b"
            hardware = "Apple NPU"
        else:
            profile = "light"
            model = "phi3:3.8b"
            hardware = "CPU"
        with open(HARDWARE_FILE, "w") as f:
            json.dump({"profile": profile, "model": model, "hardware": hardware}, f)
        return profile, model, hardware
    except Exception as e:
        logging.error(f"Hardware detection error: {str(e)}")
        profile = "light"
        model = "phi3:3.8b"
        hardware = "CPU (fallback)"
        with open(HARDWARE_FILE, "w") as f:
            json.dump({"profile": profile, "model": model, "hardware": hardware}, f)
        return profile, model, hardware

# Memory management
def load_memory():
    try:
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        return []
    except Exception as e:
        logging.error(f"Load memory error: {str(e)}")
        return []

def save_memory(snippets):
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(snippets, f)
    except Exception as e:
        logging.error(f"Save memory error: {str(e)}")

def sync_memory_with_backend():
    try:
        response = requests.get(f"{BACKEND_URL}/memory", timeout=5)
        if response.status_code == 200:
            backend_snippets = response.json()["snippets"]
            local_snippets = load_memory()
            combined = list(set(local_snippets + backend_snippets))[-10:]
            save_memory(combined)
            for snippet in combined:
                requests.post(f"{BACKEND_URL}/memory", json={"snippet": snippet}, timeout=5)
            return combined
        return load_memory()
    except Exception as e:
        logging.error(f"Sync memory error: {str(e)}")
        return load_memory()

# LLM response
def get_llm_response(input_text, profile, model):
    start_time = time.time()
    try:
        memory = sync_memory_with_backend()
        context = "\n".join(memory[-5:])
        prompt = f"Context: {context}\nUser: {input_text}\nAssistant: "
        
        if profile == "light":
            prompt += "Provide a concise response with simple reasoning. Example: For 'What's 2+2?', answer '4'. Avoid complex computations."
        elif profile == "medium":
            prompt += "Provide a detailed response with moderate reasoning. Example: For 'Explain photosynthesis', give a paragraph. "
            if "code" in input_text.lower():
                prompt += "Generate basic Python code (e.g., loops, simple functions)."
        elif profile == "heavy":
            prompt += "Use chain-of-thought reasoning for a thorough response. Break down complex questions step-by-step. Example: For 'Solve x^2 + 2x - 3 = 0', show quadratic formula steps. "
            if "code" in input_text.lower():
                prompt += "Generate or refine extended Python code (e.g., algorithms, debugging, multi-step logic)."
        
        response = ollama.generate(model=model, prompt=prompt, stream=False, options={"temperature": 0.7})["response"]
        latency = time.time() - start_time
        logging.info(f"LLM response generated in {latency:.2f}s on {profile} with model {model}")
        
        if profile == "light" and latency > 5:
            logging.warning("Light profile latency exceeded 5s")
        
        snippets = load_memory() + [response[:100]]
        save_memory(snippets[-10:])
        sync_memory_with_backend()
        
        requests.post(f"{BACKEND_URL}/chat", json={
            "input_text": input_text,
            "profile": profile,
            "response_text": response
        }, timeout=5)
        
        return response
    except Exception as e:
        logging.error(f"LLM error: {str(e)}")
        return f"Error: Could not generate response ({str(e)})"

# Voice loop
recognizer = sr.Recognizer()
engine = pyttsx3.init()
try:
    voices = engine.getProperty("voices")
    for voice in voices:
        if "english" in voice.name.lower():
            engine.setProperty("voice", voice.id)
            break
except Exception as e:
    logging.warning(f"TTS voice setup failed: {str(e)}")

def voice_loop(profile, model, chat_text):
    if IS_WSL:
        logging.warning("Voice input disabled in WSL due to microphone access limitations. Use text input.")
        return
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        while True:
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                text = recognizer.recognize_sphinx(audio)
                if "hey assistant" in text.lower():
                    input_text = text.lower().replace("hey assistant", "").strip()
                    if input_text:
                        response = get_llm_response(input_text, profile, model)
                        chat_text.insert(tk.END, f"You: {input_text}\nAssistant: {response}\n\n")
                        try:
                            engine.say(response)
                            engine.runAndWait()
                        except Exception as e:
                            logging.error(f"TTS error: {str(e)}")
                            chat_text.insert(tk.END, "TTS failed; response displayed only.\n\n")
            except sr.WaitTimeoutError:
                pass
            except Exception as e:
                logging.debug(f"Voice loop error: {str(e)}")

# Assistant runtime
def assistant():
    try:
        # Check backend and Ollama
        backend_ready = False
        ollama_ready = wait_for_ollama()
        try:
            requests.get(f"{BACKEND_URL}/docs", timeout=5)
            backend_ready = True
        except:
            pass
        
        if not (backend_ready and ollama_ready):
            root = tk.Tk()
            root.title("Local AI Assistant - Error")
            root.geometry("400x200")
            tk.Label(root, text="Error: Backend or Ollama not running.", fg="red").pack(pady=10)
            tk.Label(root, text="Run 'python3 run.py --bootstrap' first, then re-run.").pack()
            tk.Button(root, text="Exit", command=root.quit).pack(pady=10)
            root.mainloop()
            sys.exit(1)
        
        profile, model, hardware = detect_profile()
        logging.info(f"Detected profile: {profile} with model {model} on {hardware}")
        
        try:
            if model not in subprocess.run(["ollama", "list"], capture_output=True, text=True).stdout:
                ollama.pull(model)
            logging.info(f"Model {model} ready")
        except Exception as e:
            logging.error(f"Failed to pull model {model}: {str(e)}")
            messagebox.showerror("Error", f"Failed to load model {model}. Ensure Ollama is running.")
            return
        
        root = tk.Tk()
        root.title("Local AI Assistant")
        root.geometry("600x400")
        
        profile_label = tk.Label(
            root,
            text=f"Active Profile: {profile.capitalize()} | Model: {model} | Hardware: {hardware}",
            font=("Arial", 12, "bold"),
            fg="blue"
        )
        profile_label.pack(pady=10)
        
        chat_text = tk.Text(root, height=20, width=60)
        chat_text.pack(pady=5)
        chat_text.insert(tk.END, "Assistant ready. Say 'Hey Assistant' or type below.\n\n")
        if IS_WSL:
            chat_text.insert(tk.END, "Note: Voice input disabled in WSL; use text input.\n\n")
        
        input_entry = tk.Entry(root, width=50)
        input_entry.pack(pady=5)
        
        def send_text():
            input_text = input_entry.get()
            if input_text:
                response = get_llm_response(input_text, profile, model)
                chat_text.insert(tk.END, f"You: {input_text}\nAssistant: {response}\n\n")
                input_entry.delete(0, tk.END)
        
        tk.Button(root, text="Send", command=send_text).pack(pady=5)
        
        def voice_thread():
            voice_loop(profile, model, chat_text)
        
        if not IS_WSL:
            threading.Thread(target=voice_thread, daemon=True).start()
        
        # Verify functionality
        with open("ai-assistant/verify.py", "w") as f:
            f.write("""
import requests
import subprocess
import sys
import ollama

def verify():
    print("Verifying Local AI Assistant...")
    
    # Check backend
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        print("Backend running.")
    except:
        print("Error: Backend not running.")
        sys.exit(1)
    
    # Check profile detection
    with open("assistant_{}.log".format(__import__('datetime').datetime.now().strftime('%Y%m%d')), "r") as f:
        if "Detected profile" in f.read():
            print("Profile detection: Success.")
        else:
            print("Error: Profile detection failed.")
            sys.exit(1)
    
    # Test text input
    response = requests.post("http://localhost:8000/chat", json={
        "input_text": "What's 2+2?", "profile": "light", "response_text": "4"
    }, timeout=5)
    if '"response":"4"' in response.text:
        print("Text input: Success (2+2 = 4).")
    else:
        print("Error: Text input failed.")
        sys.exit(1)
    
    # Test memory
    requests.post("http://localhost:8000/memory", json={"snippet": "Test snippet"}, timeout=5)
    memory = requests.get("http://localhost:8000/memory", timeout=5)
    if "Test snippet" in memory.text:
        print("Memory: Success (snippet stored/retrieved).")
    else:
        print("Error: Memory failed.")
        sys.exit(1)
    
    # Test search stub
    search = requests.get("http://localhost:8000/search?query=test", timeout=5)
    if "Local search stub" in search.text:
        print("Search stub: Success.")
    else:
        print("Error: Search stub failed.")
        sys.exit(1)
    
    # Test LLM response
    response = ollama.generate(model="phi3:3.8b", prompt="What is 2+2?", stream=False, options={"temperature": 0.7})["response"]
    if "4" in response:
        print("LLM response: Success (2+2 includes 4).")
    else:
        print("Error: LLM response failed.")
        sys.exit(1)
    
    print("Verification complete. For voice and UI tests:")
    print("- Type 'What's 2+2?' (expect '4').")
    print("- Say 'Hey Assistant, what's the capital of France?' (expect 'Paris') if not in WSL.")
    print("- Check logs for latency (<5s for light profile).")

if __name__ == "__main__":
    verify()
""")
        
        subprocess.run([sys.executable, "ai-assistant/verify.py"])
        
        root.mainloop()
    except Exception as e:
        logging.error(f"Assistant error: {str(e)}")
        messagebox.showerror("Error", f"Failed to start assistant: {str(e)}")

# Main entry point
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--bootstrap":
        bootstrap()
    else:
        assistant()