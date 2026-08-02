#!/usr/bin/env python3
"""Test Gemini API directly."""

import os
from pathlib import Path

# Load .env
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env", override=True)

api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key: {api_key[:20] if api_key else 'NONE'}...")

if not api_key:
    print("ERROR: No API key!")
    exit(1)

# Test direct Gemini call
print("\nTesting Gemini API directly...")
try:
    import google.generativeai as genai
    print(f"✓ google.generativeai imported")

    genai.configure(api_key=api_key)
    print(f"✓ Configured with API key")

    model = genai.GenerativeModel("gemini-3.5-flash")
    print(f"✓ Model created")

    response = model.generate_content("Say 'Hello from Gemini' in one sentence.")
    print(f"✓ API call successful!")
    print(f"\nResponse: {response.text}")

except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
