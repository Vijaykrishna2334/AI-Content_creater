#!/usr/bin/env python3
"""
Comprehensive test script for all API keys
"""
import os
from dotenv import load_dotenv
import requests
import base64

# Load environment variables
load_dotenv()

def test_groq_api():
    """Test GROQ API key"""
    api_key = os.getenv('GROQ_API_KEY')
    
    if not api_key:
        print("❌ GROQ_API_KEY not found")
        return False
    
    print(f"🔑 GROQ API Key: {api_key[:10]}...")
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 10
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            print("✅ GROQ API: Working")
            return True
        else:
            print(f"❌ GROQ API: Failed ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ GROQ API: Error - {e}")
        return False

def test_resend_api():
    """Test Resend API key"""
    api_key = os.getenv('RESEND_API_KEY')
    
    if not api_key:
        print("❌ RESEND_API_KEY not found")
        return False
    
    print(f"🔑 Resend API Key: {api_key[:10]}...")
    
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "from": "test@example.com",
        "to": ["test@example.com"],
        "subject": "Test",
        "html": "<p>Test</p>"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code in [200, 201, 400]:  # 400 is expected for invalid email
            print("✅ Resend API: Working")
            return True
        else:
            print(f"❌ Resend API: Failed ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Resend API: Error - {e}")
        return False

def test_youtube_api():
    """Test YouTube Data API key"""
    api_key = os.getenv('YOUTUBE_DATA_API_KEY')
    
    if not api_key:
        print("❌ YOUTUBE_DATA_API_KEY not found")
        return False
    
    print(f"🔑 YouTube API Key: {api_key[:10]}...")
    
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        'part': 'snippet',
        'q': 'test',
        'maxResults': 1,
        'key': api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            print("✅ YouTube API: Working")
            return True
        else:
            print(f"❌ YouTube API: Failed ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ YouTube API: Error - {e}")
        return False

def test_twitter_api():
    """Test Twitter API keys"""
    api_key = os.getenv('TWITTER_API_KEY')
    api_secret = os.getenv('TWITTER_API_SECRET')
    
    if not api_key or not api_secret:
        print("❌ Twitter API keys not found")
        return False
    
    print(f"🔑 Twitter API Key: {api_key[:10]}...")
    print(f"🔑 Twitter API Secret: {api_secret[:10]}...")
    
    try:
        # Test authentication
        credentials = f"{api_key}:{api_secret}"
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        
        url = "https://api.twitter.com/oauth2/token"
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
        }
        data = "grant_type=client_credentials"
        
        response = requests.post(url, headers=headers, data=data, timeout=10)
        if response.status_code == 200:
            print("✅ Twitter API: Working")
            return True
        else:
            print(f"❌ Twitter API: Failed ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Twitter API: Error - {e}")
        return False

def main():
    print("🧪 Testing All API Keys...")
    print("=" * 50)
    
    results = []
    results.append(("GROQ API", test_groq_api()))
    results.append(("Resend API", test_resend_api()))
    results.append(("YouTube API", test_youtube_api()))
    results.append(("Twitter API", test_twitter_api()))
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY:")
    
    working = 0
    total = len(results)
    
    for name, status in results:
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {name}: {'Working' if status else 'Failed'}")
        if status:
            working += 1
    
    print(f"\n🎯 Result: {working}/{total} APIs working")
    
    if working == total:
        print("🎉 All APIs are working perfectly!")
    elif working >= 3:
        print("✅ Most APIs are working - your application should work well!")
    else:
        print("⚠️ Some APIs need attention - check the failed ones above")

if __name__ == "__main__":
    main()
