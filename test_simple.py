#!/usr/bin/env python3
"""Simple test to verify API key loading and Gemini API."""

import os
from pathlib import Path

# Step 1: Load .env
print("1. Loading .env file...")
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent / ".env"
    print(f"   Loading from: {env_file}")
    load_dotenv(env_file, override=True)
    print("   ✓ .env loaded")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Step 2: Check API key
print("\n2. Checking API key...")
api_key = os.getenv("GEMINI_API_KEY", "").strip()
print(f"   API Key: {api_key[:20]}..." if api_key else "   ✗ No API key!")
print(f"   Length: {len(api_key)} chars" if api_key else "")

# Step 3: Test Gemini
if api_key:
    print("\n3. Testing Gemini API...")
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)

        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content("Say hello briefly.")

        print(f"   ✓ API Works!")
        print(f"   Response: {response.text[:100]}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
else:
    print("\n3. Skipping API test (no key)")

print("\nDone!")
