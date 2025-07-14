#!/usr/bin/env python3

import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import parseRemoteDeck
    clean_formula_errors = parseRemoteDeck.clean_formula_errors
    print("✅ Using function from parseRemoteDeck module")
    print(f"Function: {clean_formula_errors}")
    print(f"Module: {parseRemoteDeck.__file__}")
except ImportError as e:
    print(f"❌ Failed to import parseRemoteDeck: {e}")
    clean_formula_errors = lambda x: x
    print("Using fallback function")

# Test the function
test_value = '#NAME?'
result = clean_formula_errors(test_value)
print(f"\nTest: clean_formula_errors('{test_value}') = '{result}'")
