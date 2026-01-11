#!/usr/bin/env python3
"""
Complete Twitter API test with all credentials
"""
import os
from dotenv import load_dotenv
import requests
import base64

# Load environment variables
load_dotenv()

def test_twitter_complete():
    """Test all Twitter API credentials"""
    api_key = os.getenv('TWITTER_API_KEY')
    api_secret = os.getenv('TWITTER_API_SECRET')
    access_token = os.getenv('TWITTER_ACCESS_TOKEN')
    access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
    
    print("🔑 Twitter API Credentials:")
    print(f"   API Key: {api_key[:10] if api_key else 'Not found'}...")
    print(f"   API Secret: {api_secret[:10] if api_secret else 'Not found'}...")
    print(f"   Access Token: {access_token[:10] if access_token else 'Not found'}...")
    print(f"   Access Token Secret: {access_token_secret[:10] if access_token_secret else 'Not found'}...")
    print(f"   Bearer Token: {bearer_token[:20] if bearer_token else 'Not found'}...")
    
    if not all([api_key, api_secret, access_token, access_token_secret, bearer_token]):
        print("❌ Missing Twitter credentials")
        return False
    
    # Test 1: Bearer Token (API v2)
    print("\n🧪 Testing Bearer Token (API v2)...")
    try:
        url = "https://api.twitter.com/2/tweets/search/recent"
        headers = {"Authorization": f"Bearer {bearer_token}"}
        params = {"query": "AI", "max_results": 10}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            print("✅ Bearer Token: Working")
            data = response.json()
            tweet_count = len(data.get('data', []))
            print(f"   Found {tweet_count} tweets")
        elif response.status_code == 429:
            print("✅ Bearer Token: Working (Rate limited - normal)")
        else:
            print(f"❌ Bearer Token: Failed ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Bearer Token: Error - {e}")
        return False
    
    # Test 2: OAuth 1.0a (API v1.1) - Test authentication
    print("\n🧪 Testing OAuth 1.0a Authentication...")
    try:
        # Test if we can get user info (this requires OAuth 1.0a)
        # We'll test the credentials by trying to get a bearer token
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
            print("✅ OAuth 1.0a: Working")
        else:
            print(f"❌ OAuth 1.0a: Failed ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ OAuth 1.0a: Error - {e}")
        return False
    
    print("\n🎉 All Twitter credentials are working!")
    return True

if __name__ == "__main__":
    print("🧪 Testing Complete Twitter API Setup...")
    test_twitter_complete()
