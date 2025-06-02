#!/usr/bin/env python3
"""
Test script to verify OpenAI API key configuration
"""
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from translate import traduire, OPENAI_API_KEY

    print("✅ Translation module loaded successfully")
    print(f"📡 API Key configured: {'Yes' if OPENAI_API_KEY and OPENAI_API_KEY != 'sk-test-key-for-development' else 'No (using test key)'}")

    # Test a simple translation
    print("\n🔍 Testing translation functionality...")
    test_text = "Bonjour"
    try:
        result = traduire(test_text, "en")
        print(f"✅ Translation test successful: '{test_text}' -> '{result}'")
    except Exception as e:
        print(f"❌ Translation test failed: {e}")

except ImportError as e:
    print(f"❌ Failed to import translation module: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
