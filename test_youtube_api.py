#!/usr/bin/env python3
"""
Test script to verify YouTube Data API key
"""
import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

def test_youtube_api():
    """Test YouTube Data API key"""
    api_key = os.getenv('YOUTUBE_DATA_API_KEY')
    
    if not api_key:
        print("❌ YOUTUBE_DATA_API_KEY not found in environment variables")
        return False
    
    print(f"🔑 YouTube API Key found: {api_key[:10]}...")
    
    # Test API call with a simple search
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
            print("✅ YouTube Data API key is valid!")
            return True
        elif response.status_code == 403:
            print("❌ YouTube Data API key is invalid or quota exceeded (403 Forbidden)")
            return False
        else:
            print(f"❌ API call failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing YouTube API: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing YouTube Data API Key...")
    test_youtube_api()
