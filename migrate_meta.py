#!/usr/bin/env python3
"""
Script para migrar meta.json existente aplicando resolução de conflitos.
"""

import json
import sys
import os

# Adicionar src ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

def migrate_existing_meta():
    """
    Migra o meta.json atual aplicando resolução de conflitos nos decks existentes.
    """
    print("=== MIGRAÇÃO DE META.JSON EXISTENTE ===\n")
    
    # Carregar meta.json atual
    try:
        with open('meta.json', 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except Exception as e:
        print(f"❌ Erro ao carregar meta.json: {e}")
        return
    
    decks = meta.get('decks', {})
    print(f"📁 Decks encontrados: {len(decks)}")
    
    # Mostrar estado atual
    print(f"\n📋 ESTADO ATUAL (problemático):")
    for deck_hash, deck_info in decks.items():
        remote_name = deck_info.get('remote_deck_name', 'N/A')
        print(f"   • {deck_hash[:8]}: '{remote_name}'")
    
    # Aplicar resolução de conflitos
    def apply_conflict_resolution(decks_data):
        """Aplica resolução de conflitos aos decks existentes."""
        # Agrupar por remote_deck_name
        name_groups = {}
        for deck_hash, deck_info in decks_data.items():
            remote_name = deck_info.get('remote_deck_name', '')
            if remote_name not in name_groups:
                name_groups[remote_name] = []
            name_groups[remote_name].append((deck_hash, deck_info))
        
        updated_decks = {}
        
        for remote_name, deck_list in name_groups.items():
            if len(deck_list) == 1:
                # Sem conflito
                deck_hash, deck_info = deck_list[0]
                updated_decks[deck_hash] = deck_info
            else:
                # Conflito detectado - aplicar sufixos
                print(f"\n🔄 Resolvendo conflito para nome: '{remote_name}'")
                print(f"   Decks com mesmo nome: {len(deck_list)}")
                
                # Ordenar por hash para ordem consistente
                deck_list.sort(key=lambda x: x[0])
                
                for index, (deck_hash, deck_info) in enumerate(deck_list):
                    new_deck_info = deck_info.copy()
                    
                    if index == 0:
                        # Primeiro deck mantém nome original
                        resolved_name = remote_name
                        print(f"   • {deck_hash[:8]}: '{remote_name}' (mantém original)")
                    else:
                        # Demais decks recebem sufixo
                        resolved_name = f"{remote_name}#conflito{index}"
                        print(f"   • {deck_hash[:8]}: '{remote_name}' → '{resolved_name}'")
                    
                    # Atualizar remote_deck_name
                    new_deck_info['remote_deck_name'] = resolved_name
                    
                    # Atualizar note types se necessário
                    if resolved_name != remote_name:
                        old_note_types = deck_info.get('note_types', {})
                        new_note_types = {}
                        
                        for nt_id, old_name in old_note_types.items():
                            # Substituir remote_deck_name no nome do note type
                            new_name = old_name.replace(
                                f"Sheets2Anki - {remote_name} -",
                                f"Sheets2Anki - {resolved_name} -"
                            )
                            new_note_types[nt_id] = new_name
                            if new_name != old_name:
                                print(f"     Note type: '{old_name}' → '{new_name}'")
                        
                        new_deck_info['note_types'] = new_note_types
                    
                    updated_decks[deck_hash] = new_deck_info
        
        return updated_decks
    
    # Aplicar resolução
    print(f"\n🔧 APLICANDO RESOLUÇÃO DE CONFLITOS...")
    updated_decks = apply_conflict_resolution(decks)
    
    # Mostrar resultado
    print(f"\n📋 ESTADO APÓS MIGRAÇÃO:")
    for deck_hash, deck_info in updated_decks.items():
        remote_name = deck_info.get('remote_deck_name', 'N/A')
        print(f"   • {deck_hash[:8]}: '{remote_name}'")
    
    # Criar novo meta.json
    new_meta = meta.copy()
    new_meta['decks'] = updated_decks
    
    # Criar backup
    backup_filename = 'meta.json.backup'
    try:
        with open(backup_filename, 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=4, ensure_ascii=False)
        print(f"\n💾 Backup criado: {backup_filename}")
    except Exception as e:
        print(f"⚠️ Erro ao criar backup: {e}")
    
    # Salvar novo meta.json
    try:
        with open('meta.json', 'w', encoding='utf-8') as f:
            json.dump(new_meta, f, indent=4, ensure_ascii=False)
        print(f"✅ Meta.json atualizado com resolução de conflitos!")
    except Exception as e:
        print(f"❌ Erro ao salvar meta.json: {e}")
        return
    
    print(f"\n🎯 MIGRAÇÃO CONCLUÍDA:")
    print(f"   ✅ Conflitos resolvidos automaticamente")
    print(f"   ✅ Note types atualizados com novos nomes")
    print(f"   ✅ Sistema pronto para funcionar corretamente")
    print(f"   ✅ Próximas sincronizações preservarão os conflitos resolvidos")

if __name__ == "__main__":
    migrate_existing_meta()
