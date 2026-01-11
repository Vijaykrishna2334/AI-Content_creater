#!/usr/bin/env python3
"""
Test script to verify Twitter Bearer Token
"""
import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

def test_twitter_bearer():
    """Test Twitter Bearer Token"""
    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
    
    if not bearer_token:
        print("❌ TWITTER_BEARER_TOKEN not found in environment variables")
        return False
    
    print(f"🔑 Twitter Bearer Token found: {bearer_token[:20]}...")
    
    # Test API call with bearer token
    url = "https://api.twitter.com/2/tweets/search/recent"
    headers = {
        "Authorization": f"Bearer {bearer_token}"
    }
    params = {
        "query": "AI",
        "max_results": 10
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            print("✅ Twitter Bearer Token is valid!")
            data = response.json()
            tweet_count = len(data.get('data', []))
            print(f"   Found {tweet_count} recent tweets about AI")
            
            # Show sample tweet
            if data.get('data'):
                sample_tweet = data['data'][0]
                print(f"   Sample tweet: {sample_tweet.get('text', '')[:100]}...")
            
            return True
        elif response.status_code == 429:
            print("✅ Twitter Bearer Token is valid! (Rate limited - this is normal)")
            return True
        else:
            print(f"❌ Twitter API call failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Twitter Bearer Token: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Twitter Bearer Token...")
    test_twitter_bearer()
