#!/usr/bin/env python3
"""
Test script to verify Twitter API keys
"""
import os
from dotenv import load_dotenv
import requests
import base64

# Load environment variables
load_dotenv()

def test_twitter_api():
    """Test Twitter API keys"""
    api_key = os.getenv('TWITTER_API_KEY')
    api_secret = os.getenv('TWITTER_API_SECRET')
    
    if not api_key or not api_secret:
        print("❌ Twitter API keys not found in environment variables")
        print(f"   TWITTER_API_KEY: {bool(api_key)}")
        print(f"   TWITTER_API_SECRET: {bool(api_secret)}")
        return False
    
    print(f"🔑 Twitter API Key found: {api_key[:10]}...")
    print(f"🔑 Twitter API Secret found: {api_secret[:10]}...")
    
    # Test API authentication by getting bearer token
    try:
        # Encode credentials
        credentials = f"{api_key}:{api_secret}"
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        
        # Request bearer token
        url = "https://api.twitter.com/oauth2/token"
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
        }
        data = "grant_type=client_credentials"
        
        response = requests.post(url, headers=headers, data=data, timeout=10)
        
        if response.status_code == 200:
            token_data = response.json()
            bearer_token = token_data.get('access_token')
            print("✅ Twitter API authentication successful!")
            print(f"   Bearer token: {bearer_token[:20]}...")
            
            # Test API call with bearer token
            test_url = "https://api.twitter.com/2/tweets/search/recent"
            test_headers = {
                "Authorization": f"Bearer {bearer_token}"
            }
            test_params = {
                "query": "AI",
                "max_results": 10
            }
            
            test_response = requests.get(test_url, headers=test_headers, params=test_params, timeout=10)
            
            if test_response.status_code == 200:
                print("✅ Twitter API search test successful!")
                data = test_response.json()
                tweet_count = len(data.get('data', []))
                print(f"   Found {tweet_count} recent tweets about AI")
                return True
            else:
                print(f"❌ Twitter API search failed with status {test_response.status_code}")
                print(f"   Response: {test_response.text}")
                return False
                
        elif response.status_code == 401:
            print("❌ Twitter API keys are invalid (401 Unauthorized)")
            print("   Please check your API key and secret")
            return False
        else:
            print(f"❌ Twitter API authentication failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Twitter API: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Twitter API Keys...")
    test_twitter_api()
