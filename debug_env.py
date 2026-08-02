#!/usr/bin/env python3
"""Debug .env loading issues."""

import os
from pathlib import Path

print("="*70)
print("DEBUGGING .ENV LOADING")
print("="*70)

# Check 1: File exists
env_file = Path(__file__).parent / ".env"
print(f"\n1. Checking .env file:")
print(f"   Path: {env_file}")
print(f"   Exists: {env_file.exists()}")

if env_file.exists():
    # Check 2: Read file directly
    print(f"\n2. Reading .env file directly:")
    with open(env_file, "r") as f:
        content = f.read()
        print(f"   File size: {len(content)} bytes")
        for line in content.split('\n'):
            if line and not line.startswith('#'):
                if 'GEMINI' in line:
                    print(f"   Found: {line[:60]}")

    # Check 3: Load with dotenv
    print(f"\n3. Loading with python-dotenv:")
    try:
        from dotenv import load_dotenv
        print(f"   python-dotenv available: YES")

        result = load_dotenv(env_file, override=True, verbose=True)
        print(f"   load_dotenv returned: {result}")

        # Check 4: Get from environment
        print(f"\n4. Checking os.getenv:")
        api_key = os.getenv("GEMINI_API_KEY")
        print(f"   GEMINI_API_KEY: {api_key[:20] if api_key else 'NOT FOUND'}...")

        # Check 5: Get all env vars starting with GEMINI
        print(f"\n5. All GEMINI_* variables:")
        for key, value in os.environ.items():
            if 'GEMINI' in key:
                print(f"   {key}: {value[:20]}...")

    except ImportError:
        print(f"   python-dotenv available: NO")
else:
    print("   ERROR: .env file not found!")

print("\n" + "="*70)
