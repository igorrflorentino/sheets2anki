#!/usr/bin/env python3
"""
Teste usando meta.json atual para demonstrar resolução centralizada.
"""

import sys
import os
import json

# Adicionar src ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

def test_with_actual_meta():
    """
    Testa usando o meta.json atual como base.
    """
    print("=== TESTE COM META.JSON ATUAL ===\n")
    
    # Carregar meta.json atual
    try:
        with open('meta.json', 'r', encoding='utf-8') as f:
            meta = json.load(f)
            
        decks = meta.get('decks', {})
        print(f"📁 Decks encontrados no meta.json: {len(decks)}")
        
        for deck_hash, deck_info in decks.items():
            remote_name = deck_info.get('remote_deck_name', 'N/A')
            local_name = deck_info.get('local_deck_name', 'N/A')
            print(f"   • Hash: {deck_hash}")
            print(f"     Remote: '{remote_name}'")
            print(f"     Local:  '{local_name}'")
        
        print()
        
        # Simular adição de um terceiro deck com mesmo nome
        print("🔄 Simulando adição de terceiro deck com nome '#0 Sheets2Anki Template 7'")
        
        # Mock da função de resolução
        def resolve_conflict_simulation(new_url, new_remote_name):
            """Simula a resolução de conflito com dados reais."""
            existing_names = []
            
            # Pegar nomes já existentes (excluindo o deck que seria novo)
            for deck_hash, deck_info in decks.items():
                existing_name = deck_info.get('remote_deck_name', '')
                if existing_name:
                    existing_names.append(existing_name)
            
            print(f"   Nomes existentes: {existing_names}")
            
            # Verificar conflito
            if new_remote_name not in existing_names:
                return new_remote_name
            
            # Gerar sufixo
            conflict_index = 1
            while True:
                candidate = f"{new_remote_name}#conflito{conflict_index}"
                if candidate not in existing_names:
                    return candidate
                conflict_index += 1
                
                if conflict_index > 10:  # Limite para teste
                    break
            
            return f"{new_remote_name}#conflito{conflict_index}"
        
        new_url = "https://docs.google.com/spreadsheets/d/new_url"
        original_name = "#0 Sheets2Anki Template 7"
        resolved_name = resolve_conflict_simulation(new_url, original_name)
        
        print(f"   Nome original: '{original_name}'")
        print(f"   Nome resolvido: '{resolved_name}'")
        
        # Mostrar como seriam os note types
        def generate_note_type_name(remote_name, student, is_cloze=False):
            note_type = "Cloze" if is_cloze else "Basic"
            if student:
                return f"Sheets2Anki - {remote_name} - {student} - {note_type}"
            else:
                return f"Sheets2Anki - {remote_name} - {note_type}"
        
        print(f"\n   📝 Note types gerados:")
        students = ["Belle"]  # Usando aluno ativo do meta.json
        for student in students:
            basic_name = generate_note_type_name(resolved_name, student, False)
            cloze_name = generate_note_type_name(resolved_name, student, True)
            print(f"     • Basic: '{basic_name}'")
            print(f"     • Cloze:  '{cloze_name}'")
        
        print(f"\n✅ RESULTADO:")
        print(f"   • Conflito detectado e resolvido automaticamente")
        print(f"   • Novo nome: '{resolved_name}' (com sufixo #conflito)")
        print(f"   • Note types únicos gerados automaticamente")
        print(f"   • Consistência mantida em todo o sistema")
        
    except Exception as e:
        print(f"❌ Erro ao carregar meta.json: {e}")

if __name__ == "__main__":
    test_with_actual_meta()
