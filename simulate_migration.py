#!/usr/bin/env python3
"""
Demonstração da migração do meta.json atual para a nova lógica centralizada.
Este script simula como os conflitos seriam resolvidos automaticamente.
"""

import json
import sys
import os

# Adicionar src ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

def simulate_migration():
    """
    Simula a migração do meta.json atual para resolver conflitos centralizadamente.
    """
    print("=== DEMONSTRAÇÃO DE MIGRAÇÃO PARA LÓGICA CENTRALIZADA ===\n")
    
    # Carregar meta.json atual
    try:
        with open('meta.json', 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except Exception as e:
        print(f"❌ Erro ao carregar meta.json: {e}")
        return
    
    decks = meta.get('decks', {})
    print("📋 ESTADO ATUAL:")
    
    for deck_hash, deck_info in decks.items():
        remote_name = deck_info.get('remote_deck_name', 'N/A')
        local_name = deck_info.get('local_deck_name', 'N/A')
        note_types = deck_info.get('note_types', {})
        print(f"   Deck {deck_hash[:8]}:")
        print(f"     Remote name: '{remote_name}'")
        print(f"     Local name:  '{local_name}'")
        for nt_id, nt_name in note_types.items():
            print(f"     Note type:   '{nt_name}'")
        print()
    
    print("🔄 APLICANDO RESOLUÇÃO CENTRALIZADA:\n")
    
    # Simular a lógica de resolução centralizada
    def resolve_conflicts_for_migration(decks_data):
        """
        Resolve conflitos aplicando sufixos baseados na ordem dos hashes.
        """
        # Agrupar decks por remote_deck_name
        name_groups = {}
        for deck_hash, deck_info in decks_data.items():
            remote_name = deck_info.get('remote_deck_name', '')
            if remote_name not in name_groups:
                name_groups[remote_name] = []
            name_groups[remote_name].append((deck_hash, deck_info))
        
        # Resolver conflitos
        updated_decks = {}
        for remote_name, deck_list in name_groups.items():
            if len(deck_list) == 1:
                # Sem conflito, manter nome original
                deck_hash, deck_info = deck_list[0]
                updated_decks[deck_hash] = deck_info.copy()
            else:
                # Há conflito, aplicar sufixos
                # Ordenar por hash para consistência
                deck_list.sort(key=lambda x: x[0])
                
                for index, (deck_hash, deck_info) in enumerate(deck_list):
                    new_deck_info = deck_info.copy()
                    
                    if index == 0:
                        # Primeiro deck mantém nome original
                        resolved_name = remote_name
                    else:
                        # Demais decks recebem sufixo
                        resolved_name = f"{remote_name}#conflito{index}"
                    
                    # Atualizar remote_deck_name
                    new_deck_info['remote_deck_name'] = resolved_name
                    
                    # Atualizar note types
                    old_note_types = deck_info.get('note_types', {})
                    new_note_types = {}
                    
                    for nt_id, old_nt_name in old_note_types.items():
                        # Substituir o remote_deck_name no nome do note type
                        if remote_name in old_nt_name:
                            new_nt_name = old_nt_name.replace(
                                f"Sheets2Anki - {remote_name} -",
                                f"Sheets2Anki - {resolved_name} -"
                            )
                        else:
                            new_nt_name = old_nt_name
                        
                        new_note_types[nt_id] = new_nt_name
                    
                    new_deck_info['note_types'] = new_note_types
                    updated_decks[deck_hash] = new_deck_info
        
        return updated_decks
    
    # Aplicar resolução
    updated_decks = resolve_conflicts_for_migration(decks)
    
    print("📋 ESTADO APÓS MIGRAÇÃO:")
    
    for deck_hash, deck_info in updated_decks.items():
        remote_name = deck_info.get('remote_deck_name', 'N/A')
        local_name = deck_info.get('local_deck_name', 'N/A')
        note_types = deck_info.get('note_types', {})
        print(f"   Deck {deck_hash[:8]}:")
        print(f"     Remote name: '{remote_name}' 🔄")
        print(f"     Local name:  '{local_name}'")
        for nt_id, nt_name in note_types.items():
            print(f"     Note type:   '{nt_name}' 🔄")
        print()
    
    # Mostrar diferenças
    print("🎯 RESUMO DAS MUDANÇAS:")
    for deck_hash in decks.keys():
        old_remote = decks[deck_hash].get('remote_deck_name', '')
        new_remote = updated_decks[deck_hash].get('remote_deck_name', '')
        
        if old_remote != new_remote:
            print(f"   • Deck {deck_hash[:8]}: '{old_remote}' → '{new_remote}'")
            
            old_note_types = decks[deck_hash].get('note_types', {})
            new_note_types = updated_decks[deck_hash].get('note_types', {})
            
            for nt_id in old_note_types.keys():
                old_nt = old_note_types.get(nt_id, '')
                new_nt = new_note_types.get(nt_id, '')
                if old_nt != new_nt:
                    print(f"     Note type: '{old_nt}' → '{new_nt}'")
        else:
            print(f"   • Deck {deck_hash[:8]}: Sem alterações (primeiro com nome único)")
    
    print("\n✅ VANTAGENS OBTIDAS:")
    print("   1. ✅ Conflitos resolvidos automaticamente")
    print("   2. ✅ Nomes únicos para remote_deck_name")
    print("   3. ✅ Note types consistentes com novos nomes")
    print("   4. ✅ Lógica centralizada em config_manager.py")
    print("   5. ✅ Futuras adições de decks respeitarão automaticamente os conflitos")

if __name__ == "__main__":
    simulate_migration()
