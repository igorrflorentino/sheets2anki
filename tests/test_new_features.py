"""
Testes para o sistema de configuração e nomeação de decks.

Este módulo contém testes para verificar o funcionamento correto
das novas funcionalidades implementadas.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Adicionar o diretório src ao path para importação
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from config_manager import (
        get_remote_decks, add_remote_deck, disconnect_deck,
        is_deck_disconnected, reconnect_deck, get_deck_naming_mode,
        set_deck_naming_mode, get_parent_deck_name, set_parent_deck_name
    )
    from deck_naming import (
        extract_deck_name_from_url, generate_automatic_deck_name,
        clean_deck_name, check_deck_name_conflict, resolve_deck_name_conflict
    )
    from migration import migrate_config_if_needed, check_data_consistency
except ImportError as e:
    print(f"Erro ao importar módulos: {e}")
    sys.exit(1)


class TestConfigManager(unittest.TestCase):
    """Testes para o gerenciador de configuração."""
    
    def setUp(self):
        """Configuração inicial para cada teste."""
        # Mock do mw (main window do Anki)
        self.mock_mw = Mock()
        self.mock_mw.addonManager.getConfig.return_value = {
            "user_preferences": {
                "deck_naming_mode": "automatic",
                "parent_deck_name": "Sheets2Anki",
                "auto_update_names": True
            },
            "remote_decks": {},
            "disconnected_decks": []
        }
        self.mock_mw.addonManager.writeConfig = Mock()
        
        # Patch do mw global
        self.patcher = patch('config_manager.mw', self.mock_mw)
        self.patcher.start()
    
    def tearDown(self):
        """Limpeza após cada teste."""
        self.patcher.stop()
    
    def test_get_deck_naming_mode(self):
        """Testa obtenção do modo de nomeação."""
        mode = get_deck_naming_mode()
        self.assertEqual(mode, "automatic")
    
    def test_set_deck_naming_mode(self):
        """Testa definição do modo de nomeação."""
        set_deck_naming_mode("manual")
        # Verificar se writeConfig foi chamado
        self.mock_mw.addonManager.writeConfig.assert_called()
    
    def test_get_parent_deck_name(self):
        """Testa obtenção do nome do deck pai."""
        name = get_parent_deck_name()
        self.assertEqual(name, "Sheets2Anki")
    
    def test_add_remote_deck(self):
        """Testa adição de deck remoto."""
        url = "https://example.com/sheet.tsv"
        deck_info = {
            "url": url,
            "deck_id": 12345,
            "deck_name": "Test Deck",
            "naming_mode": "automatic"
        }
        
        add_remote_deck(url, deck_info)
        self.mock_mw.addonManager.writeConfig.assert_called()
    
    def test_disconnect_deck(self):
        """Testa desconexão de deck."""
        url = "https://example.com/sheet.tsv"
        disconnect_deck(url)
        self.mock_mw.addonManager.writeConfig.assert_called()
    
    def test_is_deck_disconnected(self):
        """Testa verificação de deck desconectado."""
        url = "https://example.com/sheet.tsv"
        
        # Inicialmente não deve estar desconectado
        self.assertFalse(is_deck_disconnected(url))
        
        # Após desconectar, deve retornar True
        disconnect_deck(url)
        # Simular que foi adicionado à lista de desconectados
        self.mock_mw.addonManager.getConfig.return_value["disconnected_decks"] = [url]
        self.assertTrue(is_deck_disconnected(url))


class TestDeckNaming(unittest.TestCase):
    """Testes para o sistema de nomeação de decks."""
    
    def test_clean_deck_name(self):
        """Testa limpeza de nomes de deck."""
        # Teste com caracteres especiais
        dirty_name = "Test <Deck> Name: 2024"
        cleaned = clean_deck_name(dirty_name)
        self.assertEqual(cleaned, "Test_Deck_Name_2024")
        
        # Teste com espaços duplos
        dirty_name = "Test  Deck   Name"
        cleaned = clean_deck_name(dirty_name)
        self.assertEqual(cleaned, "Test_Deck_Name")
        
        # Teste com nome vazio
        cleaned = clean_deck_name("")
        self.assertEqual(cleaned, "Unnamed_Deck")
    
    def test_extract_deck_name_from_url(self):
        """Testa extração de nome de deck da URL."""
        # URL básica
        url = "https://docs.google.com/spreadsheets/d/1ABC123/export?format=tsv"
        name = extract_deck_name_from_url(url)
        self.assertTrue(isinstance(name, str))
        self.assertTrue(len(name) > 0)
    
    @patch('deck_naming.get_deck_naming_mode')
    @patch('deck_naming.get_parent_deck_name')
    def test_generate_automatic_deck_name(self, mock_get_parent, mock_get_mode):
        """Testa geração automática de nome de deck."""
        mock_get_mode.return_value = "automatic"
        mock_get_parent.return_value = "Sheets2Anki"
        
        url = "https://docs.google.com/spreadsheets/d/1ABC123/export?format=tsv"
        name = generate_automatic_deck_name(url)
        
        # Deve conter o nome do deck pai
        self.assertIn("Sheets2Anki", name)
        self.assertIn("::", name)
    
    @patch('deck_naming.mw')
    def test_check_deck_name_conflict(self, mock_mw):
        """Testa verificação de conflito de nomes."""
        # Simular que existe um deck com o nome
        mock_mw.col.decks.by_name.return_value = {"name": "Existing Deck"}
        
        result = check_deck_name_conflict("Existing Deck")
        self.assertTrue(result)
        
        # Simular que não existe deck com o nome
        mock_mw.col.decks.by_name.return_value = None
        
        result = check_deck_name_conflict("New Deck")
        self.assertFalse(result)
    
    @patch('deck_naming.check_deck_name_conflict')
    def test_resolve_deck_name_conflict(self, mock_check_conflict):
        """Testa resolução de conflitos de nome."""
        # Simular conflito com nome base, mas não com nome_2
        mock_check_conflict.side_effect = lambda name: name == "Test Deck"
        
        resolved = resolve_deck_name_conflict("Test Deck")
        self.assertEqual(resolved, "Test_Deck_2")


class TestMigration(unittest.TestCase):
    """Testes para o sistema de migração."""
    
    def setUp(self):
        """Configuração inicial para cada teste."""
        self.mock_mw = Mock()
        self.patcher = patch('migration.mw', self.mock_mw)
        self.patcher.start()
    
    def tearDown(self):
        """Limpeza após cada teste."""
        self.patcher.stop()
    
    @patch('migration.get_meta')
    @patch('migration.save_meta')
    def test_migrate_config_if_needed(self, mock_save_meta, mock_get_meta):
        """Testa migração de configuração."""
        # Simular que ainda não foi migrado
        mock_get_meta.return_value = {"migrated": False}
        
        migrate_config_if_needed()
        
        # Verificar se save_meta foi chamado
        mock_save_meta.assert_called()
    
    @patch('migration.get_meta')
    def test_check_data_consistency(self, mock_get_meta):
        """Testa verificação de consistência de dados."""
        # Simular dados consistentes
        mock_get_meta.return_value = {
            "remote_decks": {
                "https://example.com/sheet.tsv": {
                    "deck_id": 12345,
                    "deck_name": "Test Deck"
                }
            }
        }
        
        # Mock do deck existente
        mock_deck = {"name": "Test Deck"}
        self.mock_mw.col.decks.get.return_value = mock_deck
        
        result = check_data_consistency()
        self.assertTrue(result)


def run_tests():
    """Executa todos os testes."""
    # Criar suite de testes
    suite = unittest.TestSuite()
    
    # Adicionar testes
    suite.addTest(unittest.makeSuite(TestConfigManager))
    suite.addTest(unittest.makeSuite(TestDeckNaming))
    suite.addTest(unittest.makeSuite(TestMigration))
    
    # Executar testes
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Retornar resultado
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
