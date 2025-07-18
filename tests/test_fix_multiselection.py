#!/usr/bin/env python3
"""
Teste para verificar se a solução de compatibilidade para MultiSelection está funcionando
"""

# Adiciona o diretório atual ao path para importar os módulos
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Importa o módulo de correção
    from src.fix_multiselection import (
        MULTI_SELECTION, SINGLE_SELECTION, NO_SELECTION, 
        EXTENDED_SELECTION, CONTIGUOUS_SELECTION
    )
    
    print("Testando constantes de seleção...")
    
    # Testa os valores
    print(f"MULTI_SELECTION: {MULTI_SELECTION}")
    print(f"SINGLE_SELECTION: {SINGLE_SELECTION}")
    print(f"NO_SELECTION: {NO_SELECTION}")
    print(f"EXTENDED_SELECTION: {EXTENDED_SELECTION}")
    print(f"CONTIGUOUS_SELECTION: {CONTIGUOUS_SELECTION}")
    
    # Importa QListWidget para teste
    from aqt.qt import QListWidget
    
    # Testa criação da instância
    list_widget = QListWidget()
    list_widget.setSelectionMode(MULTI_SELECTION)
    
    print("✅ Teste passou! As constantes de seleção estão funcionando.")
    
except Exception as e:
    print(f"❌ Erro no teste: {e}")
    sys.exit(1)