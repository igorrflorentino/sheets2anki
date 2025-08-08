#!/usr/bin/env python3
"""
Script de teste para a nova funcionalidade de nomeação inteligente de decks.
"""

import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.deck_naming import DeckNamer

def test_deck_naming():
    """Testa a nova funcionalidade de nomeação inteligente."""
    
    # URL de teste
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSsNCEFZvBR3UjBwTbyaPPz-B1SKw17I7Jb72XWweS1y75HmzXfgdFJ1TpZX6_S06m9_phJTy5XnCI6/pub?gid=36065074&single=true&output=tsv"
    
    print("=== TESTE DE NOMEAÇÃO INTELIGENTE ===")
    print(f"URL: {url}")
    print()
    
    # Testar cada estratégia individualmente
    print("1. Testando extração de título via HTML...")
    try:
        title = DeckNamer._extract_spreadsheet_title(url)
        print(f"   Resultado: {title}")
    except Exception as e:
        print(f"   Erro: {e}")
    
    print()
    print("2. Testando extração via Content-Disposition...")
    try:
        filename = DeckNamer._extract_filename_from_headers(url)
        print(f"   Resultado: {filename}")
    except Exception as e:
        print(f"   Erro: {e}")
    
    print()
    print("3. Testando extração via primeira célula...")
    try:
        first_cell = DeckNamer._extract_first_cell_content(url)
        print(f"   Resultado: {first_cell}")
    except Exception as e:
        print(f"   Erro: {e}")
    
    print()
    print("4. Testando nome fallback...")
    try:
        fallback = DeckNamer._generate_fallback_name(url)
        print(f"   Resultado: {fallback}")
    except Exception as e:
        print(f"   Erro: {e}")
    
    print()
    print("=== RESULTADO FINAL ===")
    try:
        final_name = DeckNamer.extract_remote_name_from_url(url)
        print(f"Nome remoto extraído: '{final_name}'")
        print(f"Nome anterior era: '0_Sheets2Anki_Template_4_-_Notas'")
    except Exception as e:
        print(f"Erro no resultado final: {e}")

if __name__ == "__main__":
    test_deck_naming()
