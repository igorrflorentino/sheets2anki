#!/usr/bin/env python3
"""
Teste simples para verificar o conteúdo de meta.json.
"""

import json
import os

def test_meta_config():
    """Testa a leitura da configuração meta.json."""
    print("=== VERIFICAÇÃO DE CONFIGURAÇÃO ===")
    
    try:
        with open('meta.json', 'r', encoding='utf-8') as f:
            meta = json.load(f)
        
        decks = meta.get('decks', {})
        print(f"Decks encontrados no meta.json: {len(decks)}")
        
        if len(decks) == 0:
            print("❌ PROBLEMA: Nenhum deck remoto configurado!")
            print("A descoberta de estudantes precisa de decks remotos configurados.")
            return False
        
        for i, (hash_key, deck_info) in enumerate(decks.items(), 1):
            print(f"\nDeck {i}:")
            print(f"  Hash: {hash_key}")
            print(f"  Nome remoto: {deck_info.get('remote_deck_name', 'N/A')}")
            url = deck_info.get('remote_deck_url', 'N/A')
            print(f"  URL remota: {url}")
            
            if url == 'N/A' or not url:
                print("  ❌ PROBLEMA: URL não configurada!")
                return False
            else:
                print("  ✅ URL configurada corretamente")
        
        return True
    
    except FileNotFoundError:
        print("❌ Arquivo meta.json não encontrado")
        return False
    except Exception as e:
        print(f"❌ Erro ao ler meta.json: {e}")
        return False

def test_column_definition():
    """Verifica a definição da coluna ALUNOS."""
    print("\n=== VERIFICAÇÃO DA COLUNA ALUNOS ===")
    
    # Ler diretamente o arquivo column_definitions.py
    try:
        with open('src/column_definitions.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'ALUNOS = ' in content:
            # Extrair a definição
            lines = content.split('\n')
            for line in lines:
                if line.strip().startswith('ALUNOS = '):
                    alunos_def = line.strip()
                    print(f"Definição encontrada: {alunos_def}")
                    return True
        
        print("❌ PROBLEMA: Definição ALUNOS não encontrada!")
        return False
        
    except Exception as e:
        print(f"❌ Erro ao ler column_definitions.py: {e}")
        return False

if __name__ == "__main__":
    config_ok = test_meta_config()
    column_ok = test_column_definition()
    
    if config_ok and column_ok:
        print("\n✅ CONFIGURAÇÃO BÁSICA OK - O problema deve estar no parsing do TSV")
    else:
        print("\n❌ PROBLEMA NA CONFIGURAÇÃO BÁSICA - Corrija antes de continuar")
