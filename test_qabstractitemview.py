#!/usr/bin/env python3
"""
Teste para verificar se QAbstractItemView.MultiSelection está funcionando
"""

# Adiciona o diretório atual ao path para importar os stubs
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Importa usando os stubs
    from stubs.aqt.qt import QAbstractItemView
    
    print("Testando QAbstractItemView.MultiSelection...")
    
    # Testa os atributos
    print(f"MultiSelection: {QAbstractItemView.MultiSelection}")
    print(f"SingleSelection: {QAbstractItemView.SingleSelection}")
    print(f"NoSelection: {QAbstractItemView.NoSelection}")
    print(f"ExtendedSelection: {QAbstractItemView.ExtendedSelection}")
    print(f"ContiguousSelection: {QAbstractItemView.ContiguousSelection}")
    
    # Testa criação da instância
    view = QAbstractItemView()
    view.setSelectionMode(QAbstractItemView.MultiSelection)
    
    print("✅ Teste passou! QAbstractItemView.MultiSelection está funcionando.")
    
except Exception as e:
    print(f"❌ Erro no teste: {e}")
    sys.exit(1)
