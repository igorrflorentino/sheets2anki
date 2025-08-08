#!/usr/bin/env python3
"""
Teste da resolução centralizada de conflitos no remote_deck_name.
Demonstra como a nova lógica funciona.
"""

import sys
import os

# Adicionar src ao path para importar módulos
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

def simulate_conflict_resolution():
    """
    Simula o processo de resolução de conflitos centralizada.
    """
    print("=== TESTE DE RESOLUÇÃO CENTRALIZADA DE CONFLITOS ===\n")
    
    # Mock das funções que seriam usadas
    def mock_get_remote_decks():
        return {
            "3f67c1cb": {
                "remote_deck_url": "https://docs.google.com/spreadsheets/d/url1",
                "remote_deck_name": "#0 Sheets2Anki Template 7",
                "local_deck_name": "Sheets2Anki::#0 Sheets2Anki Template 7"
            }
        }
    
    def mock_get_deck_hash(url):
        if url == "https://docs.google.com/spreadsheets/d/url1":
            return "3f67c1cb"
        elif url == "https://docs.google.com/spreadsheets/d/url2":
            return "3c30faa1"
        elif url == "https://docs.google.com/spreadsheets/d/url3":
            return "4d41fab2"
        return "new_hash"
    
    def resolve_remote_deck_name_conflict(url, remote_deck_name):
        """
        Versão mock da função de resolução centralizada.
        """
        if not remote_deck_name:
            return "RemoteDeck"
        
        clean_name = remote_deck_name.strip()
        current_hash = mock_get_deck_hash(url)
        
        try:
            remote_decks = mock_get_remote_decks()
            if not remote_decks:
                return clean_name
            
            # Coletar todos os remote_deck_names existentes (exceto o deck atual)
            existing_names = []
            for deck_hash, deck_info in remote_decks.items():
                if deck_hash != current_hash:
                    deck_remote_name = deck_info.get('remote_deck_name', '')
                    if deck_remote_name:
                        existing_names.append(deck_remote_name)
            
            # Se não há conflito, retornar nome original
            if clean_name not in existing_names:
                return clean_name
            
            # Encontrar sufixo disponível
            conflict_index = 1
            while True:
                candidate_name = f"{clean_name}#conflito{conflict_index}"
                if candidate_name not in existing_names:
                    return candidate_name
                conflict_index += 1
                
                if conflict_index > 100:
                    return f"{clean_name}#conflito{conflict_index}"
                    
        except Exception:
            return clean_name
        
        return clean_name
    
    def mock_get_note_type_name(url, remote_deck_name, student=None, is_cloze=False):
        """
        Mock da função get_note_type_name que agora usa o remote_deck_name já resolvido.
        """
        note_type = "Cloze" if is_cloze else "Basic"
        clean_remote_name = remote_deck_name.strip() if remote_deck_name else "RemoteDeck"
        
        if student:
            clean_student_name = student.strip()
            if clean_student_name:
                return f"Sheets2Anki - {clean_remote_name} - {clean_student_name} - {note_type}"
        else:
            return f"Sheets2Anki - {clean_remote_name} - {note_type}"
    
    # Teste 1: Primeiro deck com nome novo (sem conflito)
    print("📝 Teste 1: Primeiro deck '#0 Sheets2Anki Template 7'")
    url1 = "https://docs.google.com/spreadsheets/d/url1"
    original_name = "#0 Sheets2Anki Template 7"
    resolved_name1 = resolve_remote_deck_name_conflict(url1, original_name)
    print(f"   Nome original: {original_name}")
    print(f"   Nome resolvido: {resolved_name1}")
    print(f"   Note type para Belle: {mock_get_note_type_name(url1, resolved_name1, 'Belle', False)}")
    print()
    
    # Atualizar mock para incluir o primeiro deck
    def mock_get_remote_decks_with_first():
        return {
            "3f67c1cb": {
                "remote_deck_url": "https://docs.google.com/spreadsheets/d/url1",
                "remote_deck_name": "#0 Sheets2Anki Template 7",
                "local_deck_name": "Sheets2Anki::#0 Sheets2Anki Template 7"
            }
        }
    
    # Substituir a função mock
    original_mock = resolve_remote_deck_name_conflict.__code__
    
    def resolve_remote_deck_name_conflict_updated(url, remote_deck_name):
        if not remote_deck_name:
            return "RemoteDeck"
        
        clean_name = remote_deck_name.strip()
        current_hash = mock_get_deck_hash(url)
        
        try:
            remote_decks = mock_get_remote_decks_with_first()
            if not remote_decks:
                return clean_name
            
            existing_names = []
            for deck_hash, deck_info in remote_decks.items():
                if deck_hash != current_hash:
                    deck_remote_name = deck_info.get('remote_deck_name', '')
                    if deck_remote_name:
                        existing_names.append(deck_remote_name)
            
            if clean_name not in existing_names:
                return clean_name
            
            conflict_index = 1
            while True:
                candidate_name = f"{clean_name}#conflito{conflict_index}"
                if candidate_name not in existing_names:
                    return candidate_name
                conflict_index += 1
                
                if conflict_index > 100:
                    return f"{clean_name}#conflito{conflict_index}"
                    
        except Exception:
            return clean_name
        
        return clean_name
    
    # Teste 2: Segundo deck com mesmo nome (deve gerar conflito)
    print("🔄 Teste 2: Segundo deck com mesmo nome '#0 Sheets2Anki Template 7'")
    url2 = "https://docs.google.com/spreadsheets/d/url2"
    resolved_name2 = resolve_remote_deck_name_conflict_updated(url2, original_name)
    print(f"   Nome original: {original_name}")
    print(f"   Nome resolvido: {resolved_name2}")
    print(f"   Note type para Belle: {mock_get_note_type_name(url2, resolved_name2, 'Belle', False)}")
    print()
    
    # Teste 3: Terceiro deck com mesmo nome (deve gerar #conflito2)
    print("🔄 Teste 3: Terceiro deck com mesmo nome '#0 Sheets2Anki Template 7'")
    
    def mock_get_remote_decks_with_two():
        return {
            "3f67c1cb": {
                "remote_deck_url": "https://docs.google.com/spreadsheets/d/url1",
                "remote_deck_name": "#0 Sheets2Anki Template 7",
                "local_deck_name": "Sheets2Anki::#0 Sheets2Anki Template 7"
            },
            "3c30faa1": {
                "remote_deck_url": "https://docs.google.com/spreadsheets/d/url2",
                "remote_deck_name": "#0 Sheets2Anki Template 7#conflito1",
                "local_deck_name": "Sheets2Anki::#0 Sheets2Anki Template 7#conflito1"
            }
        }
    
    def resolve_remote_deck_name_conflict_final(url, remote_deck_name):
        if not remote_deck_name:
            return "RemoteDeck"
        
        clean_name = remote_deck_name.strip()
        current_hash = mock_get_deck_hash(url)
        
        try:
            remote_decks = mock_get_remote_decks_with_two()
            if not remote_decks:
                return clean_name
            
            existing_names = []
            for deck_hash, deck_info in remote_decks.items():
                if deck_hash != current_hash:
                    deck_remote_name = deck_info.get('remote_deck_name', '')
                    if deck_remote_name:
                        existing_names.append(deck_remote_name)
            
            if clean_name not in existing_names:
                return clean_name
            
            conflict_index = 1
            while True:
                candidate_name = f"{clean_name}#conflito{conflict_index}"
                if candidate_name not in existing_names:
                    return candidate_name
                conflict_index += 1
                
                if conflict_index > 100:
                    return f"{clean_name}#conflito{conflict_index}"
                    
        except Exception:
            return clean_name
        
        return clean_name
    
    url3 = "https://docs.google.com/spreadsheets/d/url3"
    resolved_name3 = resolve_remote_deck_name_conflict_final(url3, original_name)
    print(f"   Nome original: {original_name}")
    print(f"   Nome resolvido: {resolved_name3}")
    print(f"   Note type para Belle: {mock_get_note_type_name(url3, resolved_name3, 'Belle', False)}")
    print()
    
    # Resumo das vantagens
    print("✅ VANTAGENS DA CENTRALIZAÇÃO:")
    print("   1. Resolução de conflitos em um só lugar (config_manager.py)")
    print("   2. Nomes de deck e note type consistentes automaticamente")
    print("   3. Sufixo '#conflito' mais claro que '_2', '_3'")
    print("   4. Menos código duplicado e mais fácil manutenção")
    print("   5. Lógica aplicada em todos os pontos onde remote_deck_name é definido")

if __name__ == "__main__":
    simulate_conflict_resolution()
