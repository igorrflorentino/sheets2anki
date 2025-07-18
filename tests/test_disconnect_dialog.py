#!/usr/bin/env python3
"""
Teste básico para verificar se o disconnect_dialog funciona corretamente.
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
        # Simula alguns decks para teste
        mock_decks = {
            1: {"name": "Deck de Teste 1"},
            2: {"name": "Deck de Teste 2"},
            3: {"name": "Deck de Teste 3"}
        }
        return mock_decks.get(deck_id)

def test_disconnect_dialog_import():
    """Testa se o disconnect_dialog pode ser importado."""
    try:
        from src.disconnect_dialog import show_disconnect_dialog
        print("✓ Importação do disconnect_dialog bem-sucedida")
        return True
    except Exception as e:
        print(f"✗ Erro ao importar disconnect_dialog: {e}")
        return False

def test_deck_manager_import():
    """Testa se o deck_manager pode ser importado."""
    try:
        from src.deck_manager import removeRemoteDeck
        print("✓ Importação do deck_manager bem-sucedida")
        return True
    except Exception as e:
        print(f"✗ Erro ao importar deck_manager: {e}")
        return False

def test_mock_dialog():
    """Testa se o diálogo pode ser instanciado com dados mock."""
    try:
        # Mock básico do config_manager
        import src.config_manager
        
        # Mock da função get_remote_decks
        original_get_remote_decks = src.config_manager.get_remote_decks
        
        def mock_get_remote_decks():
            return {
                "https://test1.com": {
                    "deck_id": 1,
                    "deck_name": "Deck de Teste 1"
                },
                "https://test2.com": {
                    "deck_id": 2,
                    "deck_name": "Deck de Teste 2"
                }
            }
        
        src.config_manager.get_remote_decks = mock_get_remote_decks
        
        from src.disconnect_dialog import DisconnectDialog
        
        # Criar instância do dialog (não vamos executar para não abrir janela)
        mock_mw = MockAnkiMain()
        dialog = DisconnectDialog(mock_mw)
        
        # Restaurar função original
        src.config_manager.get_remote_decks = original_get_remote_decks
        
        print("✓ Diálogo pode ser instanciado com dados mock")
        return True
    except Exception as e:
        print(f"✗ Erro ao testar diálogo: {e}")
        return False

def main():
    """Executa todos os testes."""
    print("=== Teste do Sistema de Desconexão ===")
    
    tests = [
        test_disconnect_dialog_import,
        test_deck_manager_import,
        test_mock_dialog
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n=== Resultado: {passed}/{total} testes passaram ===")
    
    if passed == total:
        print("✓ Todos os testes passaram! O sistema está funcionando corretamente.")
    else:
        print("✗ Alguns testes falharam. Verifique os erros acima.")

if __name__ == "__main__":
    main()
