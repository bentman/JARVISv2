
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
