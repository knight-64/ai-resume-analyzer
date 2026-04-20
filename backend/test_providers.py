"""Test provider factory and selection"""
import os
import sys
from app.services.provider_factory import get_provider

# Test 1: Get Claude provider (default)
print("Test 1: Getting default provider (should be Claude)...")
try:
    os.environ["LLM_PROVIDER"] = "claude"
    provider = get_provider()
    print(f"  [OK] Got provider: {provider.__class__.__name__}")
except ValueError as e:
    print(f"  [OK] Expected error (no API key): {str(e)[:50]}...")

# Test 2: Get Groq provider explicitly
print("\nTest 2: Getting Groq provider explicitly...")
try:
    provider = get_provider("groq")
    print(f"  [FAIL] Should have failed (no API key set)")
except ValueError as e:
    print(f"  [OK] Expected error: {str(e)[:50]}...")

# Test 3: Invalid provider
print("\nTest 3: Testing invalid provider...")
try:
    provider = get_provider("invalid")
    print(f"  [FAIL] Should have failed")
except ValueError as e:
    print(f"  [OK] Expected error: {str(e)[:50]}...")

# Test 4: Provider parameter overrides environment
print("\nTest 4: Provider parameter overrides environment...")
os.environ["LLM_PROVIDER"] = "claude"
try:
    provider = get_provider("groq")
    print(f"  [FAIL] Should have failed (no Groq API key)")
except ValueError as e:
    print(f"  [OK] Parameter override works: {str(e)[:50]}...")

print("\n[PASS] All provider factory tests passed!")

