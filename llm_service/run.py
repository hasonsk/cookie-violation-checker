# Cell 1: Install dependencies
#!pip install fastapi uvicorn transformers accelerate bitsandbytes pyngrok torch sentencepiece

# Cell 2: Setup ngrok authentication
# Replace 'YOUR_NGROK_TOKEN' with your actual ngrok token from https://ngrok.com/
from pyngrok import ngrok, conf
import os

# Set ngrok auth token
NGROK_TOKEN = "xxx"  # Get this from https://dashboard.ngrok.com/get-started/your-authtoken
ngrok.set_auth_token(NGROK_TOKEN)

# Cell 3: Clone repository and setup
#!git clone https://github.com/YOUR_USERNAME/llm-fastapi-server.git
#%cd llm-fastapi-server

# Cell 4: Start the server with ngrok tunnel
import subprocess
import threading
import time
from pyngrok import ngrok

def start_server():
    """Start the FastAPI server"""
    subprocess.run(["python", "main.py"])

# Start server in background thread
server_thread = threading.Thread(target=start_server)
server_thread.daemon = True
server_thread.start()

# Wait for server to start
time.sleep(10)

# Create ngrok tunnel
public_url = ngrok.connect(8000)
print(f"🚀 Server is running!")
print(f"📡 Public URL: {public_url}")
print(f"📋 API Documentation: {public_url}/docs")
print(f"💊 Health Check: {public_url}/health")

# Keep the tunnel alive
try:
    # Keep running
    ngrok_process = ngrok.get_ngrok_process()
    ngrok_process.proc.wait()
except KeyboardInterrupt:
    print("Shutting down...")
    ngrok.kill()

# Cell 5: Test the API (run this in a separate cell after server starts)
import requests
import json

# Replace with your ngrok URL
API_URL = "YOUR_NGROK_URL_HERE"  # e.g., "https://abc123.ngrok.io"

# Test health endpoint
response = requests.get(f"{API_URL}/health")
print("Health Check:", response.json())

# Test generation endpoint
test_prompt = "What is artificial intelligence?"
payload = {
    "prompt": test_prompt,
    "max_length": 200,
    "temperature": 0.7
}

response = requests.post(f"{API_URL}/generate", json=payload)
if response.status_code == 200:
    result = response.json()
    print(f"Prompt: {result['prompt']}")
    print(f"Generated: {result['generated_text']}")
else:
    print(f"Error: {response.status_code} - {response.text}")

# Cell 6: Alternative - Run server and get URL in one cell
import subprocess
import threading
import time
from pyngrok import ngrok
import requests

def run_server_with_ngrok():
    # Start server in background
    def start_server():
        subprocess.run(["python", "main.py"])

    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()

    # Wait for server to start
    print("⏳ Starting server...")
    time.sleep(15)

    # Create ngrok tunnel
    public_url = ngrok.connect(8000)
    print(f"🚀 Server is running!")
    print(f"📡 Public URL: {public_url}")
    print(f"📋 API Documentation: {public_url}/docs")

    # Test connection
    try:
        response = requests.get(f"{public_url}/health", timeout=30)
        if response.status_code == 200:
            print("✅ Server is healthy!")
            health_data = response.json()
            print(f"Model loaded: {health_data['model_loaded']}")
            print(f"GPU available: {health_data['gpu_available']}")
        else:
            print(f"⚠️ Server responded with status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing server: {e}")

    return public_url

# Run the server
url = run_server_with_ngrok()
