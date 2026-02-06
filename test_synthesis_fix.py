#!/usr/bin/env python3
"""
Test script to verify Groq API synthesis generation is working
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, '/app/backend')

from seo_engine.multi_llm_client import MultiLLMClient

async def test_synthesis():
    """Test synthesis generation with the new API key"""
    print("=" * 60)
    print("TESTING GROQ API SYNTHESIS GENERATION")
    print("=" * 60)
    
    # Get API key from environment
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ ERROR: GROQ_API_KEY not found in environment")
        return False
    
    print(f"\n✓ API Key loaded: {api_key[:30]}...")
    
    try:
        # Initialize MultiLLMClient
        client = MultiLLMClient(
            provider="groq",
            model="llama-3.3-70b-versatile",
            api_key=api_key,
            temperature=0.7,
            max_tokens=700
        )
        print("✓ MultiLLMClient initialized")
        
        # Test synthesis prompt (similar to what the orchestrator uses)
        test_prompt = """You are the Master SEO Strategist synthesizing insights for a test website.

Based on analysis, create:

1. **Executive Summary** (3 sentences max)
2. **Top 5 Priority Actions** (ranked by impact)
3. **Quick Wins** (can be done in < 1 day)

Keep total response under 200 words."""
        
        print("\n✓ Generating synthesis...")
        synthesis = client.generate(test_prompt, max_tokens=700)
        
        print("\n" + "=" * 60)
        print("SYNTHESIS RESULT:")
        print("=" * 60)
        print(synthesis)
        print("=" * 60)
        
        # Check if it's an error
        if synthesis.startswith("Error generating"):
            print("\n❌ ERROR: Synthesis generation failed!")
            return False
        else:
            print("\n✅ SUCCESS! Synthesis generation is working correctly!")
            return True
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv('/app/backend/.env')
    
    # Run test
    result = asyncio.run(test_synthesis())
    sys.exit(0 if result else 1)
