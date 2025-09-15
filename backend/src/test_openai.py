#!/usr/bin/env python3
"""
Test OpenAI API key and check rate limits
"""

import os
from openai import OpenAI
from services.config import settings

def test_api_key():
    print("🔑 Testing OpenAI API Key...")
    print(f"API Key: {settings.openai_api_key[:20]}...")
    print(f"Model: {settings.openai_model}")
    
    try:
        client = OpenAI(api_key=settings.openai_api_key)
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'API test successful' in JSON format"}
            ],
            max_tokens=50
        )
        
        print("✅ API Key works!")
        print(f"Response: {response.choices[0].message.content}")
        
        # Try to get usage info (this might not work for all accounts)
        try:
            # Check if we can make another call to see current limits
            response2 = client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "user", "content": "What is 2+2?"}
                ],
                max_tokens=10
            )
            print("✅ Second call successful - rate limits seem OK")
            
        except Exception as e:
            if "rate_limit" in str(e).lower() or "429" in str(e):
                print(f"❌ Rate limit hit: {e}")
                print("\n💡 Possible issues:")
                print("1. Project-based API key may have different limits")
                print("2. Organization rate limits may be different")
                print("3. Check your OpenAI dashboard for actual usage")
            else:
                print(f"⚠️  Other API error: {e}")
                
    except Exception as e:
        print(f"❌ API Key test failed: {e}")
        if "authentication" in str(e).lower():
            print("🔧 Check that your API key is correct and active")
        elif "rate_limit" in str(e).lower():
            print("🔧 Rate limit issue detected")

if __name__ == "__main__":
    test_api_key()