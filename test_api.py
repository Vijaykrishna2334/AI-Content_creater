#!/usr/bin/env python3
"""
Test script to verify GROQ API key
"""
import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

def test_groq_api():
    """Test GROQ API key"""
    api_key = os.getenv('GROQ_API_KEY')
    
    if not api_key:
        print("❌ GROQ_API_KEY not found in environment variables")
        return False
    
    print(f"🔑 API Key found: {api_key[:10]}...")
    
    # Test API call
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "user", "content": "Hello, this is a test message."}
        ],
        "max_tokens": 10,
        "temperature": 0.1
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            print("✅ GROQ API key is valid!")
            return True
        elif response.status_code == 401:
            print("❌ GROQ API key is invalid (401 Unauthorized)")
            print("   Please get a new API key from console.groq.com")
            return False
        else:
            print(f"❌ API call failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing GROQ API Key...")
    test_groq_api()
