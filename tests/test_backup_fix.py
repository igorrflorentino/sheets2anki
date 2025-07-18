#!/usr/bin/env python3
"""
Teste para verificar se o erro do QAbstractItemView.MultiSelection foi corrigido
"""

import sys
import os

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from stubs.aqt.qt import QAbstractItemView, QListWidget
    
    print("Testando QAbstractItemView.MultiSelection...")
    
    # Testar se os atributos estão disponíveis
    print(f"MultiSelection: {QAbstractItemView.MultiSelection}")
    print(f"SingleSelection: {QAbstractItemView.SingleSelection}")
    print(f"NoSelection: {QAbstractItemView.NoSelection}")
    print(f"ExtendedSelection: {QAbstractItemView.ExtendedSelection}")
    print(f"ContiguousSelection: {QAbstractItemView.ContiguousSelection}")
    
    # Testar se pode criar instâncias
    view = QAbstractItemView()
    list_widget = QListWidget()
    
    # Testar se pode usar setSelectionMode
    view.setSelectionMode(QAbstractItemView.MultiSelection)
    list_widget.setSelectionMode(QAbstractItemView.MultiSelection)
    
    print("✅ Teste passou! O erro do QAbstractItemView.MultiSelection foi corrigido.")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    sys.exit(1)
