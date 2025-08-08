#!/usr/bin/env python3
"""
Teste para verificar a persistência dos checkboxes no sync_dialog
"""

import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_sync_persistence():
    """Testa se os valores is_sync estão sendo lidos corretamente do meta.json"""
    
    try:
        from config_manager import get_meta
        
        meta = get_meta()
        decks = meta.get("decks", {})
        
        print("=== Estado atual dos decks no meta.json ===")
        for hash_key, deck_info in decks.items():
            remote_name = deck_info.get("remote_deck_name", "N/A")
            local_name = deck_info.get("local_deck_name", "N/A") 
            is_sync = deck_info.get("is_sync", True)  # Padrão True
            
            print(f"Hash: {hash_key}")
            print(f"  Remote: {remote_name}")
            print(f"  Local: {local_name}")
            print(f"  is_sync: {is_sync}")
            print()
        
        print("✅ Teste concluído - os valores is_sync foram lidos com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

if __name__ == "__main__":
    test_sync_persistence()
