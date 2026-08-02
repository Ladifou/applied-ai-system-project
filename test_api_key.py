#!/usr/bin/env python3
"""
Debug script to verify Gemini API key is loaded correctly.

Run this to troubleshoot API key issues:
    python test_api_key.py
"""

from pathlib import Path
import sys

print("\n" + "="*70)
print("GEMINI API KEY VERIFICATION")
print("="*70)

# Step 1: Check .env file exists
print("\n1. Checking .env file...")
env_path = Path(__file__).parent / ".env"

if env_path.exists():
    print(f"   ✓ .env file found at: {env_path}")
else:
    print(f"   ✗ .env file NOT found at: {env_path}")
    print("   Create it with: cp .env.example .env")
    sys.exit(1)

# Step 2: Check python-dotenv is installed
print("\n2. Checking python-dotenv installation...")
try:
    import dotenv
    print("   ✓ python-dotenv is installed")
except ImportError:
    print("   ✗ python-dotenv is NOT installed")
    print("   Install with: pip install python-dotenv")
    sys.exit(1)

# Step 3: Load .env file
print("\n3. Loading .env file...")
from dotenv import load_dotenv
import os

load_dotenv(env_path)
print(f"   ✓ Loaded environment from: {env_path}")

# Step 4: Check API key
print("\n4. Checking GEMINI_API_KEY...")
api_key = os.getenv("GEMINI_API_KEY", "").strip()

if api_key:
    print(f"   ✓ API key found: {api_key[:15]}...{api_key[-4:]}")
    print(f"   ✓ Key length: {len(api_key)} characters")

    if api_key.startswith("AIzaSy"):
        print("   ✓ Key format looks correct (starts with AIzaSy)")
    else:
        print(f"   ⚠️ Key format unexpected (starts with {api_key[:5]})")
else:
    print("   ✗ GEMINI_API_KEY is empty or not set")
    print("   Edit .env file and add your API key:")
    print("   GEMINI_API_KEY=your-key-here")
    sys.exit(1)

# Step 5: Check google-generativeai
print("\n5. Checking google-generativeai installation...")
try:
    import google.generativeai as genai
    print("   ✓ google-generativeai is installed")
except ImportError:
    print("   ✗ google-generativeai is NOT installed")
    print("   Install with: pip install google-generativeai")
    sys.exit(1)

# Step 6: Try to configure Gemini
print("\n6. Testing Gemini API connection...")
try:
    genai.configure(api_key=api_key)
    print("   ✓ Successfully configured Gemini API")
except Exception as e:
    print(f"   ✗ Failed to configure Gemini API: {str(e)}")
    sys.exit(1)

# Step 7: Try to list available models
print("\n7. Listing available Gemini models...")
try:
    models = genai.list_models()
    model_count = 0
    for model in models:
        if "generateContent" in model.supported_generation_methods:
            print(f"   • {model.name}")
            model_count += 1
    print(f"   ✓ Found {model_count} available models")
except Exception as e:
    print(f"   ✗ Failed to list models: {str(e)}")
    print("   This might indicate an invalid API key")
    sys.exit(1)

# Step 8: Test a simple generation
print("\n8. Testing a simple API call...")
try:
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content("Say 'Hello' in one word only.")

    if response.text:
        print(f"   ✓ API call successful!")
        print(f"   ✓ Response: {response.text}")
    else:
        print("   ✗ API call returned empty response")
        sys.exit(1)
except Exception as e:
    print(f"   ✗ API call failed: {str(e)}")
    sys.exit(1)

print("\n" + "="*70)
print("✓ ALL CHECKS PASSED!")
print("="*70)
print("\nYour Gemini API setup is working correctly.")
print("You can now run: python example_llm_usage.py\n")
