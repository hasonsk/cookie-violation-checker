# Llama-3.1-8B FastAPI Server

A FastAPI-based REST API server for serving Meta's Llama-3.1-8B model with 4-bit quantization, designed to run on Google Colab with ngrok tunneling.

## Features

- ✅ **4-bit Quantization**: Efficient memory usage with BitsAndBytesConfig
- ✅ **FastAPI Framework**: Modern, fast web framework with automatic API documentation
- ✅ **Google Colab Compatible**: Optimized for Colab's free GPU resources
- ✅ **Ngrok Integration**: Public API access through secure tunneling
- ✅ **Health Monitoring**: Built-in health checks and GPU monitoring
- ✅ **Memory Management**: Automatic cache clearing and memory optimization

## Quick Start on Google Colab

### 1. Setup Ngrok Account
1. Go to [ngrok.com](https://ngrok.com) and create a free account
2. Get your authentication token from the [dashboard](https://dashboard.ngrok.com/get-started/your-authtoken)

### 2. Clone and Setup Repository
```bash
# In Google Colab
!git clone https://github.com/YOUR_USERNAME/llm-fastapi-server.git
%cd llm-fastapi-server
```

### 3. Install Dependencies
```bash
!pip install -r requirements.txt
```

### 4. Run the Server
```python
# Set your ngrok token
from pyngrok import ngrok
ngrok.set_auth_token("YOUR_NGROK_TOKEN")

# Start server (this will take a few minutes to load the model)
!python main.py &

# Create public tunnel
public_url = ngrok.connect(8000)
print(f"🚀 API is live at: {public_url}")
print(f"📋 Documentation: {public_url}/docs")
```

## API Endpoints

### Health Check
```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "gpu_available": true,
  "gpu_memory_used": "3.2GB / 15.0GB"
}
```

### Text Generation
```
POST /generate
```

**Request Body:**
```json
{
  "prompt": "What is artificial intelligence?",
  "max_length": 512,
  "temperature": 0.7,
  "top_p": 0.9,
  "do_sample": true
}
```

**Response:**
```json
{
  "generated_text": "Artificial intelligence (AI) refers to...",
  "prompt": "What is artificial intelligence?",
  "model_info": "meta-llama/Meta-Llama-3.1-8B-Instruct (4-bit quantized)"
}
```

### Clear GPU Cache
```
POST /clear-cache
```

## Usage Examples

### Python Client
```python
import requests

# Replace with your ngrok URL
API_URL = "https://abc123.ngrok.io"

# Health check
response = requests.get(f"{API_URL}/health")
print(response.json())

# Generate text
payload = {
    "prompt": "Explain quantum computing:",
    "max_length": 300,
    "temperature": 0.7
}

response = requests.post(f"{API_URL}/generate", json=payload)
result = response.json()
print(result["generated_text"])
```

### cURL
```bash
# Health check
curl -X GET "https://your-ngrok-url.ngrok.io/health"

# Generate text
curl -X POST "https://your-ngrok-url.ngrok.io/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "Write a poem about space:",
       "max_length": 200,
       "temperature": 0.8
     }'
```

### JavaScript/Node.js
```javascript
const axios = require('axios');

const API_URL = 'https://your-ngrok-url.ngrok.io';

async function generateText(pr
