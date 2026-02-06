#!/usr/bin/env python3
"""Test Groq API key"""
import os
from groq import Groq

# Load from environment
api_key = os.getenv("GROQ_API_KEY", "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")

print(f"Testing Groq API key: {api_key[:20]}...")

try:
    client = Groq(api_key=api_key)
    
    # Test a simple completion
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": "Say 'API key is working!' if you can read this."}
        ],
        temperature=0.7,
        max_tokens=50
    )
    
    result = response.choices[0].message.content
    print(f"\n✅ SUCCESS! Groq API Response:")
    print(result)
    print("\nThe Groq API key is valid and working!")
    
except Exception as e:
    print(f"\n❌ ERROR! Groq API test failed:")
    print(f"Error: {str(e)}")
    print("\nThe API key may be invalid or there's a connection issue.")
