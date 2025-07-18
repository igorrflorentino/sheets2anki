#!/usr/bin/env python3
"""
Teste para verificar se a solução de compatibilidade para exec_/exec está funcionando
"""

# Adiciona o diretório atual ao path para importar os módulos
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Importa o módulo de correção
    from src.fix_exec import safe_exec
    
    print("Testando função safe_exec...")
    
    # Importa QDialog para teste
    from stubs.aqt.qt import QDialog
    
    # Cria um diálogo de teste
    dialog = QDialog()
    
    # Testa a função safe_exec
    print("Executando safe_exec(dialog)...")
    result = safe_exec(dialog)
    print(f"Resultado: {result}")
    
    print("✅ Teste passou! A função safe_exec está funcionando.")
    
except Exception as e:
    print(f"❌ Erro no teste: {e}")
    sys.exit(1)