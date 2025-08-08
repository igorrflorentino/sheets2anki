#!/usr/bin/env python3
"""
Script de teste básico para verificar sintaxe Python após limpeza.
"""

import sys
import os
sys.path.insert(0, '.')

def test_basic_syntax():
    """Testa sintaxe básica dos módulos sem dependências do Anki."""
    print("🧪 Testando sintaxe Python básica...")
    
    modules_to_test = [
        'src.config_manager',
        'src.student_manager', 
        'src.utils',
        'src.column_definitions',
        'src.constants'
    ]
    
    success_count = 0
    
    for module_name in modules_to_test:
        try:
            # Apenas tentar compilar/importar sem executar
            import importlib.util
            spec = importlib.util.find_spec(module_name)
            if spec is None:
                print(f"❌ {module_name}: Não encontrado")
                continue
                
            # Compilar sem executar
            import py_compile
            py_compile.compile(spec.origin, doraise=True)
            print(f"✅ {module_name}: Sintaxe OK")
            success_count += 1
            
        except Exception as e:
            print(f"❌ {module_name}: {e}")
    
    print(f"\n📊 Resultado: {success_count}/{len(modules_to_test)} módulos com sintaxe válida")
    return success_count == len(modules_to_test)

if __name__ == "__main__":
    success = test_basic_syntax()
    exit(0 if success else 1)
