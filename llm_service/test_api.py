import requests
import json
import time
import sys

# Configuration
API_URL = "https://c9c8-35-226-153-152.ngrok-free.app/"  # Change this to your ngrok URL if using ngrok

def test_connection():
    """Test if server is running and accessible"""
    try:
        print("🔍 Testing server connection...")
        response = requests.get(API_URL, timeout=10)
        print(f"✅ Server is running! Status: {response.status_code}")
        print(f"Response: {response.text}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Connection refused - Server is not running")
        return False
    except requests.exceptions.Timeout:
        print("❌ Connection timeout - Server is slow to respond")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_health():
    """Test health endpoint"""
    try:
        print("\n🏥 Testing health endpoint...")
        response = requests.get(f"{API_URL}/health", timeout=30)

        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Raw Response: {response.text}")

        if response.status_code == 200:
            try:
                health_data = response.json()
                print("✅ Health check successful!")
                print(json.dumps(health_data, indent=2))
                return health_data
            except json.JSONDecodeError:
                print("❌ Invalid JSON response from health endpoint")
                return None
        else:
            print(f"❌ Health check failed with status: {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ Health check error: {e}")
        return None

def test_generation():
    """Test text generation"""
    try:
        print("\n🤖 Testing text generation...")

        payload = {
            "prompt": "Hello, how are you?",
            "max_length": 100,
            "temperature": 0.7
        }

        response = requests.post(
            f"{API_URL}/generate",
            json=payload,
            timeout=120,
            headers={"Content-Type": "application/json"}
        )

        print(f"Status Code: {response.status_code}")
        print(f"Raw Response: {response.text}")

        if response.status_code == 200:
            try:
                result = response.json()
                print("✅ Generation successful!")
                print(f"Generated: {result.get('generated_text', 'No text found')}")
                return True
            except json.JSONDecodeError:
                print("❌ Invalid JSON response from generation endpoint")
                return False
        else:
            print(f"❌ Generation failed with status: {response.status_code}")
            print(f"Error response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Generation test error: {e}")
        return False

def check_server_logs():
    """Instructions for checking server logs"""
    print("\n📋 Server Debugging Steps:")
    print("1. Check if the server is running:")
    print("   - Look for 'python main.py' process")
    print("   - Check terminal where you started the server")
    print()
    print("2. Check server logs for errors:")
    print("   - Model loading errors")
    print("   - CUDA/GPU memory issues")
    print("   - Missing dependencies")
    print()
    print("3. Common issues:")
    print("   - Model not loaded (503 Service Unavailable)")
    print("   - CUDA out of memory")
    print("   - Missing Hugging Face token")
    print("   - Network/firewall issues")

def main():
    print("🧪 API Server Debug Test")
    print("=" * 50)

    # Test 1: Basic connection
    if not test_connection():
        print("\n❌ Server is not accessible. Please check:")
        print("1. Is the server running? (python main.py)")
        print("2. Is the URL correct?")
        print("3. Are you using the right port (8000)?")
        check_server_logs()
        return

    # Test 2: Health check
    health_data = test_health()
    if not health_data:
        print("\n❌ Health endpoint failed")
        check_server_logs()
        return

    # Check if model is loaded
    if not health_data.get("model_loaded", False):
        print("\n⚠️ Model is not loaded yet!")
        print("This is normal - model loading can take 2-10 minutes")
        print("Please wait and try again...")

        # Wait and retry
        print("Waiting 30 seconds and retrying...")
        time.sleep(30)
        health_data = test_health()

        if not health_data or not health_data.get("model_loaded", False):
            print("❌ Model still not loaded. Check server logs for errors.")
            return

    # Test 3: Text generation
    if health_data.get("model_loaded", False):
        print(f"\n✅ Model loaded: {health_data.get('model_name', 'Unknown')}")
        test_generation()

    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    # Check if URL was provided as argument
    if len(sys.argv) > 1:
        API_URL = sys.argv[1].rstrip('/')
        print(f"Using custom API URL: {API_URL}")

    main()
