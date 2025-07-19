import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Adicionar o diretório pai ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.subdeck_manager import remove_empty_subdecks

class TestEmptySubdeckRemoval(unittest.TestCase):
    
    @patch('src.subdeck_manager.mw')
    def test_remove_empty_subdecks(self, mock_mw):
        # Configurar mocks
        mock_col = MagicMock()
        mock_mw.col = mock_col
        
        # Configurar decks
        main_deck = {"name": "TestDeck", "id": 1}
        subdeck1 = {"name": "TestDeck::Topic1", "id": 2}
        subdeck2 = {"name": "TestDeck::Topic1::Subtopic1", "id": 3}
        subdeck3 = {"name": "TestDeck::Topic2", "id": 4}
        
        # Configurar mock para decks.get
        def mock_get_deck(deck_id):
            if deck_id == 1:
                return main_deck
            elif deck_id == 2:
                return subdeck1
            elif deck_id == 3:
                return subdeck2
            elif deck_id == 4:
                return subdeck3
            return None
        
        mock_col.decks.get.side_effect = mock_get_deck
        
        # Configurar mock para all_names_and_ids
        class MockDeckInfo:
            def __init__(self, name, id):
                self.name = name
                self.id = id
        
        mock_col.decks.all_names_and_ids.return_value = [
            MockDeckInfo("TestDeck", 1),
            MockDeckInfo("TestDeck::Topic1", 2),
            MockDeckInfo("TestDeck::Topic1::Subtopic1", 3),
            MockDeckInfo("TestDeck::Topic2", 4)
        ]
        
        # Configurar mock para find_cards
        def mock_find_cards(query):
            if "TestDeck::Topic1::Subtopic1" in query:
                return []  # Subdeck vazio
            elif "TestDeck::Topic1" in query:
                return [101, 102]  # Subdeck com cards
            elif "TestDeck::Topic2" in query:
                return []  # Subdeck vazio
            return [100, 101, 102]  # Deck principal com cards
        
        mock_col.find_cards.side_effect = mock_find_cards
        
        # Configurar remote_decks
        remote_decks = {
            "url1": {"deck_id": 1, "deck_name": "TestDeck"}
        }
        
        # Executar a função
        removed_count = remove_empty_subdecks(remote_decks)
        
        # Verificar resultados
        self.assertEqual(removed_count, 2)  # Dois subdecks vazios devem ser removidos
        
        # Verificar que os decks vazios foram removidos
        mock_col.decks.remove.assert_any_call([3])  # TestDeck::Topic1::Subtopic1
        mock_col.decks.remove.assert_any_call([4])  # TestDeck::Topic2
        
        # Verificar que a interface foi atualizada
        mock_mw.reset.assert_called_once()

if __name__ == "__main__":
    unittest.main()