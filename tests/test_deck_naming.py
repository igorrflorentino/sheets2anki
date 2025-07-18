#!/usr/bin/env python3
"""
Teste da funcionalidade de nomeação automática baseada no nome do arquivo TSV.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Mock do Anki para teste
class MockAnkiMain:
    def __init__(self):
        self.col = MockCollection()

class MockCollection:
    def __init__(self):
        self.decks = MockDecks()

class MockDecks:
    def get(self, deck_id):
        return None
    
    def by_name(self, name):
        return None

# Configurar mock do mw
import src.compat
src.compat.mw = MockAnkiMain()

def test_extract_deck_name_from_url():
    """Testa a extração do nome do deck a partir da URL."""
    try:
        from src.deck_naming import extract_deck_name_from_url
        
        # URLs de teste
        test_urls = [
            "https://docs.google.com/spreadsheets/d/e/2PACX-1vSART0Xw_lDq5bn4bylNox7vxOmU6YkoOjOwqdS3kZ-O1JEBLR8paqDv_bcGTW55yXchaO0jzK2cB8x/pub?gid=334628680&single=true&output=tsv",
            "https://docs.google.com/spreadsheets/d/e/2PACX-1vSART0Xw_lDq5bn4bylNox7vxOmU6YkoOjOwqdS3kZ-O1JEBLR8paqDv_bcGTW55yXchaO0jzK2cB8x/pub?gid=1869088045&single=true&output=tsv"
        ]
        
        print("=== Teste de Extração de Nome do Deck ===")
        
        for i, url in enumerate(test_urls, 1):
            print(f"\nTeste {i}:")
            print(f"URL: {url}")
            
            try:
                deck_name = extract_deck_name_from_url(url)
                print(f"✓ Nome extraído: '{deck_name}'")
            except Exception as e:
                print(f"✗ Erro ao extrair nome: {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ Erro ao testar extração de nome: {e}")
        return False

def test_filename_extraction():
    """Testa especificamente a extração do nome do arquivo TSV."""
    try:
        # Simular uma URL que retorna um arquivo TSV
        import urllib.request
        from unittest.mock import Mock, patch
        
        # Mock da resposta HTTP
        mock_response = Mock()
        mock_response.headers = {'Content-Disposition': 'attachment; filename="Minha_Planilha_de_Teste.tsv"'}
        mock_response.close = Mock()
        
        print("=== Teste de Extração de Nome do Arquivo TSV ===")
        
        with patch('urllib.request.urlopen', return_value=mock_response):
            from src.deck_naming import extract_deck_name_from_url
            
            url = "https://docs.google.com/spreadsheets/d/test/export?format=tsv"
            deck_name = extract_deck_name_from_url(url)
            
            print(f"URL: {url}")
            print(f"✓ Nome extraído: '{deck_name}'")
            print(f"✓ Esperado: 'Minha_Planilha_de_Teste'")
            
            if deck_name == "Minha_Planilha_de_Teste":
                print("✓ Teste passou!")
                return True
            else:
                print("✗ Teste falhou - nome não confere")
                return False
        
    except Exception as e:
        print(f"✗ Erro ao testar extração de nome do arquivo: {e}")
        return False

def test_generate_automatic_deck_name():
    """Testa a geração de nomes automáticos com hierarquia."""
    try:
        from src.deck_naming import generate_automatic_deck_name
        
        print("=== Teste de Geração de Nome Automático ===")
        
        # Mock das configurações
        import src.config_manager
        
        # Mock das funções de configuração
        original_get_mode = src.config_manager.get_deck_naming_mode
        original_get_parent = src.config_manager.get_parent_deck_name
        
        def mock_get_mode():
            return "automatic"
        
        def mock_get_parent():
            return "Sheets2Anki"
        
        src.config_manager.get_deck_naming_mode = mock_get_mode
        src.config_manager.get_parent_deck_name = mock_get_parent
        
        url = "https://docs.google.com/spreadsheets/d/test/export?format=tsv"
        deck_name = generate_automatic_deck_name(url)
        
        print(f"URL: {url}")
        print(f"✓ Nome gerado: '{deck_name}'")
        print(f"✓ Deve incluir hierarquia: 'Sheets2Anki::'")
        
        # Restaurar funções originais
        src.config_manager.get_deck_naming_mode = original_get_mode
        src.config_manager.get_parent_deck_name = original_get_parent
        
        if "Sheets2Anki::" in deck_name:
            print("✓ Teste passou!")
            return True
        else:
            print("✗ Teste falhou - hierarquia não encontrada")
            return False
        
    except Exception as e:
        print(f"✗ Erro ao testar geração de nome automático: {e}")
        return False

def main():
    """Executa todos os testes."""
    print("=== Teste da Funcionalidade de Nomeação Automática ===")
    
    tests = [
        test_extract_deck_name_from_url,
        test_filename_extraction,
        test_generate_automatic_deck_name
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Erro no teste: {e}")
    
    print(f"\n=== Resultado: {passed}/{total} testes passaram ===")
    
    if passed == total:
        print("✓ Todos os testes passaram! A funcionalidade está funcionando.")
    else:
        print("✗ Alguns testes falharam.")

if __name__ == "__main__":
    main()
