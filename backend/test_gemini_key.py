#!/usr/bin/env python3
"""Simple test to verify Gemini API key works."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment from secrets/.env (override any existing env vars)
secrets_env = Path(__file__).resolve().parents[1] / "secrets" / ".env"
if secrets_env.exists():
    load_dotenv(dotenv_path=secrets_env, override=True)
    print(f"✅ Loaded environment from {secrets_env} (with override)")
else:
    print(f"❌ secrets/.env not found at {secrets_env}")
    exit(1)

# Check API key
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ No GEMINI_API_KEY or GOOGLE_API_KEY found in environment")
    exit(1)

print(f"✅ API key found: {api_key[:20]}...{api_key[-4:]}")

# Test with google-generativeai
try:
    import google.generativeai as genai

    genai.configure(api_key=api_key)

    # Test with gemini-2.0-flash
    model = genai.GenerativeModel('gemini-2.0-flash')

    print("\n🧪 Testing Gemini API...")
    response = model.generate_content("Say 'Hello, API test successful!' in a friendly way.")

    print("\n✅ API Response:")
    print(response.text)
    print("\n✅ Gemini API key is working correctly!")

except Exception as e:
    print(f"\n❌ Error testing Gemini API: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
