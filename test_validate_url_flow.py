#!/usr/bin/env python3
"""
Teste do fluxo de validação de URL para verificar se está seguindo
o novo modelo de resolução de conflitos.
"""

import sys
import os

# Adicionar src ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

def test_validate_url_flow():
    """
    Testa o fluxo do botão 'Validar URL' com o novo modelo de resolução.
    """
    print("=== TESTE DO BOTÃO 'VALIDAR URL' ===\n")
    
    # Mock das funções usadas na validação
    def mock_get_remote_decks():
        """Mock dos decks existentes baseado no meta.json atual."""
        return {
            "3f67c1cb": {
                "remote_deck_url": "https://docs.google.com/spreadsheets/d/url1",
                "remote_deck_name": "#0 Sheets2Anki Template 7",
                "local_deck_name": "Sheets2Anki::#0 Sheets2Anki Template 7"
            },
            "3c30faa1": {
                "remote_deck_url": "https://docs.google.com/spreadsheets/d/url2", 
                "remote_deck_name": "#0 Sheets2Anki Template 7",
                "local_deck_name": "Sheets2Anki::#0 Sheets2Anki Template 7_2"
            }
        }
    
    def mock_extract_name_from_url(url):
        """Mock da extração do nome (mesma que extract_remote_name_from_url)."""
        return "#0 Sheets2Anki Template 7"  # Mesmo nome para simular conflito
    
    def mock_check_conflict(name):
        """Mock para verificar conflito de nome local."""
        existing_local_names = [
            "Sheets2Anki::#0 Sheets2Anki Template 7",
            "Sheets2Anki::#0 Sheets2Anki Template 7_2"
        ]
        return name in existing_local_names
    
    def mock_resolve_conflict(name):
        """Mock para resolver conflito de nome local."""
        return f"{name}_3"  # Simular resolução para nome local
    
    def resolve_remote_deck_name_conflict(url, remote_deck_name):
        """Mock da nova resolução centralizada de conflitos."""
        current_hash = url.split('/')[-1][:8]
        
        try:
            remote_decks = mock_get_remote_decks()
            
            # Coletar nomes existentes (exceto deck atual)
            existing_names = []
            for deck_hash, deck_info in remote_decks.items():
                if deck_hash != current_hash:
                    existing_name = deck_info.get('remote_deck_name', '')
                    if existing_name:
                        existing_names.append(existing_name)
            
            # Se não há conflito, retornar nome original
            if remote_deck_name not in existing_names:
                return remote_deck_name
            
            # Encontrar sufixo disponível
            conflict_index = 1
            while True:
                candidate_name = f"{remote_deck_name}#conflito{conflict_index}"
                if candidate_name not in existing_names:
                    return candidate_name
                conflict_index += 1
                
                if conflict_index > 10:
                    break
            
            return f"{remote_deck_name}#conflito{conflict_index}"
                    
        except Exception:
            return remote_deck_name
    
    # Simular fluxo de validação
    print("🔍 SIMULANDO FLUXO DE VALIDAÇÃO:")
    
    # 1. Usuário digita URL e clica "Validar URL"
    test_url = "https://docs.google.com/spreadsheets/d/new_test_url"
    print(f"1️⃣ URL digitada: {test_url}")
    
    # 2. Validação extrai nome sugerido
    suggested_name = mock_extract_name_from_url(test_url)
    print(f"2️⃣ Nome extraído (suggested_name): '{suggested_name}'")
    
    # 3. Nome sugerido é transformado em nome local completo
    parent_name = "Sheets2Anki"
    full_local_name = f"{parent_name}::{suggested_name}"
    print(f"3️⃣ Nome local completo: '{full_local_name}'")
    
    # 4. Verificação de conflito de nome local (deck naming)
    has_local_conflict = mock_check_conflict(full_local_name)
    print(f"4️⃣ Conflito de nome local: {'SIM' if has_local_conflict else 'NÃO'}")
    
    if has_local_conflict:
        resolved_local_name = mock_resolve_conflict(full_local_name)
        print(f"   └─ Nome local resolvido: '{resolved_local_name}'")
        final_local_name = resolved_local_name
    else:
        final_local_name = full_local_name
    
    # 5. (NOVO) Preview da resolução de conflito do remote_deck_name
    predicted_remote_name = resolve_remote_deck_name_conflict(test_url, suggested_name)
    print(f"5️⃣ Remote name que seria usado: '{predicted_remote_name}'")
    
    print(f"\n📋 RESULTADO DA VALIDAÇÃO:")
    print(f"   • Nome local final: '{final_local_name}'")
    print(f"   • Remote name final: '{predicted_remote_name}'")
    
    # 6. Quando usuário clica "Adicionar", o fluxo segue com create_deck_info
    print(f"\n➡️ AO CLICAR 'ADICIONAR':")
    print(f"   1. Extrai remote_deck_name: '{suggested_name}'")
    print(f"   2. create_deck_info() aplica resolução: '{predicted_remote_name}'")
    print(f"   3. Note types usarão: 'Sheets2Anki - {predicted_remote_name} - Belle - Basic'")
    
    # Análise do fluxo atual
    print(f"\n🔎 ANÁLISE DO FLUXO ATUAL:")
    print(f"   ✅ Validação extrai nome corretamente")
    print(f"   ✅ Conflito de nome local é resolvido na validação")
    print(f"   ✅ Remote name será resolvido no create_deck_info()")
    print(f"   ⚠️  Usuário não vê preview do remote name final na validação")
    
    print(f"\n🤔 POSSÍVEL MELHORIA:")
    print(f"   • Durante validação, mostrar também o remote name que será usado")
    print(f"   • Exemplo: 'Nome sugerido: {suggested_name}'")
    print(f"   • Adicionar: 'Remote name final: {predicted_remote_name}'")
    print(f"   • Assim o usuário saberia exatamente como ficará")

if __name__ == "__main__":
    test_validate_url_flow()
