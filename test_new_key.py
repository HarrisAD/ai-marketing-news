#!/usr/bin/env python3
"""
Test a new OpenAI API key to see if it resolves the rate limit issue
"""

import os
from openai import OpenAI

def test_new_key(api_key):
    print(f"🔑 Testing new API key: {api_key[:20]}...")
    
    try:
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Say 'New key test successful'"}
            ],
            max_tokens=10
        )
        
        print("✅ New API key works!")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ New key test failed: {e}")
        if "rate_limit" in str(e).lower():
            print("Still hitting rate limits - this is definitely an OpenAI platform issue")
        return False

if __name__ == "__main__":
    new_key = input("Enter your new API key: ")
    if test_new_key(new_key):
        print("\n✅ New key works! Update your .env file:")
        print(f"OPENAI_API_KEY={new_key}")
    else:
        print("\n❌ Same issue persists - contact OpenAI support")