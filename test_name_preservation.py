#!/usr/bin/env python3
"""
Teste de depuração para verificar a preservação de espaços no nome do deck remoto.
"""

import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from deck_naming import DeckNamer

def test_name_extraction():
    """Testa a extração de nome da URL do Google Sheets."""
    
    # URL real do usuário (baseada no meta.json)
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSsNCEFZvBR3UjBwTbyaPPz-B1SKw17I7Jb72XWweS1y75HmzXfgdFJ1TpZX6_S06m9_phJTy5XnCI6/pub?gid=36065074&single=true&output=tsv"
    
    print(f"[TEST] URL de entrada: {url}")
    print("=" * 80)
    
    # Testar extração de nome remoto
    remote_name = DeckNamer.extract_name_from_url(url)
    print(f"[TEST] Nome remoto extraído: '{remote_name}'")
    
    # Testar geração de nome local
    local_name = DeckNamer.generate_local_deck_name(remote_name)
    print(f"[TEST] Nome local gerado: '{local_name}'")
    
    print("=" * 80)
    
    # Verificar se contém espaços
    has_spaces = ' ' in remote_name
    print(f"[TEST] Nome remoto contém espaços? {has_spaces}")
    
    if has_spaces:
        print("✅ SUCESSO: Espaços estão sendo preservados!")
    else:
        print("❌ PROBLEMA: Espaços estão sendo removidos!")
        
    return remote_name, local_name

if __name__ == "__main__":
    test_name_extraction()
