#!/usr/bin/env python3

import sys
import os

# Adicionar o diretório raiz do projeto ao path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

# Tentar importar com diferentes estratégias
print("🔍 Testando estratégias de importação:")

strategy_worked = False

# Estratégia 1: Importar de src/
try:
    from src.parseRemoteDeck import clean_formula_errors
    print("✅ Estratégia 1: from src.parseRemoteDeck import clean_formula_errors")
    strategy_worked = True
except ImportError as e:
    print(f"❌ Estratégia 1 falhou: {e}")

# Estratégia 2: Importar src como módulo
if not strategy_worked:
    try:
        import src.parseRemoteDeck as parseRemoteDeck
        clean_formula_errors = parseRemoteDeck.clean_formula_errors
        print("✅ Estratégia 2: import src.parseRemoteDeck")
        strategy_worked = True
    except ImportError as e:
        print(f"❌ Estratégia 2 falhou: {e}")

# Test the function
if strategy_worked:
    test_value = '#NAME?'
    result = clean_formula_errors(test_value)
    print(f"\nTest: clean_formula_errors('{test_value}') = '{result}'")
    
    # Test with a few more values
    test_values = ['#REF!', 'normal text', '#VALUE!', '#CUSTOM!']
    for val in test_values:
        result = clean_formula_errors(val)
        print(f"clean_formula_errors('{val}') = '{result}'")
else:
    print("❌ Todas as estratégias de importação falharam")
