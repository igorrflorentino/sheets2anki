import unittest
from unittest.mock import patch, MagicMock
import urllib.error
from . import main
from .main import (
    validate_url, get_model_suffix_from_url, create_card_template,
    create_model, ensure_custom_models, SyncError, NoteProcessingError,
    CollectionSaveError, syncDecks, addNewDeck, removeRemoteDeck
)

class TestMain(unittest.TestCase):
    def test_validate_url_valid(self):
        """Test URL validation with valid URLs"""
        # Valid URLs should not raise exceptions
        valid_urls = [
            "https://docs.google.com/spreadsheets/d/xxx/pub?output=tsv",
            "http://example.com/sheet.tsv?format=tsv",
            "https://example.com/data.tsv?output=tsv&other=param"
        ]
        for url in valid_urls:
            with patch('urllib.request.urlopen') as mock_urlopen:
                mock_response = MagicMock()
                mock_response.getcode.return_value = 200
                mock_response.headers = {'Content-Type': 'text/tab-separated-values'}
                mock_urlopen.return_value = mock_response
                try:
                    validate_url(url)
                except Exception as e:
                    self.fail(f"validate_url() raised {type(e).__name__} unexpectedly!")

    def test_validate_url_invalid(self):
        """Test URL validation with invalid URLs"""
        invalid_urls = [
            "",  # Empty URL
            None,  # None URL
            "not_a_url",  # Invalid format
            "ftp://example.com/data.tsv",  # Wrong protocol
            "https://example.com/data.csv"  # Wrong format
        ]
        for url in invalid_urls:
            with self.assertRaises(ValueError):
                validate_url(url)

    def test_validate_url_network_errors(self):
        """Test URL validation with network errors"""
        url = "https://example.com/data.tsv?output=tsv"
        
        # Test connection timeout
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_urlopen.side_effect = TimeoutError()
            with self.assertRaises(ValueError) as context:
                validate_url(url)
            self.assertTrue("Connection timed out" in str(context.exception))
        
        # Test HTTP error
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_urlopen.side_effect = urllib.error.HTTPError(
                url, 404, "Not Found", None, None
            )
            with self.assertRaises(ValueError) as context:
                validate_url(url)
            self.assertTrue("HTTP Error 404" in str(context.exception))

    def test_get_model_suffix_from_url(self):
        """Test model suffix generation from URLs"""
        url1 = "https://example.com/data1.tsv"
        url2 = "https://example.com/data2.tsv"
        
        # Test that different URLs produce different suffixes
        suffix1 = get_model_suffix_from_url(url1)
        suffix2 = get_model_suffix_from_url(url2)
        self.assertNotEqual(suffix1, suffix2)
        
        # Test that same URL produces same suffix
        self.assertEqual(suffix1, get_model_suffix_from_url(url1))
        
        # Test suffix length
        self.assertEqual(len(suffix1), 8)

    def test_create_card_template_basic(self):
        """Test creation of basic card template"""
        template = create_card_template(is_cloze=False)
        
        # Check template structure
        self.assertIn('qfmt', template)
        self.assertIn('afmt', template)
        
        # Check template content
        self.assertIn('{{FrontSide}}', template['afmt'])
        self.assertNotIn('{{cloze:', template['qfmt'])

    def test_create_card_template_cloze(self):
        """Test creation of cloze card template"""
        template = create_card_template(is_cloze=True)
        
        # Check template content
        self.assertIn('{{cloze:', template['qfmt'])
        self.assertNotIn('{{FrontSide}}', template['afmt'])

    @patch('aqt.mw')
    def test_create_model(self, mock_mw):
        """Test model creation"""
        # Mock Anki collection
        mock_col = MagicMock()
        mock_col.models.new.return_value = {'type': 0}
        
        # Test basic model creation
        model = create_model(mock_col, "Test Model", is_cloze=False)
        self.assertEqual(model['type'], 0)
        
        # Test cloze model creation
        model = create_model(mock_col, "Test Cloze Model", is_cloze=True)
        self.assertEqual(model['type'], 1)

    @patch('aqt.mw')
    def test_ensure_custom_models(self, mock_mw):
        """Test custom model creation and caching"""
        # Mock Anki collection
        mock_col = MagicMock()
        mock_col.models.by_name.return_value = None
        mock_col.models.new.return_value = {'type': 0}
        
        url = "https://example.com/test.tsv"
        models = ensure_custom_models(mock_col, url)
        
        # Check that both model types are created
        self.assertIn('standard', models)
        self.assertIn('cloze', models)
        
        # Check model names contain URL suffix
        suffix = get_model_suffix_from_url(url)
        self.assertTrue(any(suffix in str(m) for m in models.values()))

    @patch('aqt.mw')
    def test_sync_decks_with_id(self, mock_mw):
        """Test deck synchronization using deck IDs"""
        # Mock configuration
        mock_config = {
            "remote-decks": {
                "https://example.com/test.tsv": {
                    "url": "https://example.com/test.tsv",
                    "deck_id": 1234567890
                }
            }
        }
        
        # Mock collection and deck
        mock_deck = {"id": 1234567890, "name": "Test Deck"}
        mock_col = MagicMock()
        mock_col.decks.get.return_value = mock_deck
        
        # Set up mocks
        mock_mw.col = mock_col
        mock_mw.addonManager.getConfig.return_value = mock_config
        
        # Mock getRemoteDeck
        with patch('remote_decks.main.getRemoteDeck') as mock_get_remote:
            mock_deck = MagicMock()
            mock_get_remote.return_value = mock_deck
            
            # Mock validate_url
            with patch('remote_decks.main.validate_url'):
                # Mock create_or_update_notes
                with patch('remote_decks.main.create_or_update_notes'):
                    # Run sync
                    syncDecks()
                    
                    # Verify deck was looked up by ID
                    mock_col.decks.get.assert_called_with(1234567890)
                    
                    # Verify deck name was set from collection
                    self.assertEqual(mock_deck.deckName, "Test Deck")

    @patch('aqt.mw')
    @patch('aqt.qt.QInputDialog')
    def test_add_new_deck_with_id(self, mock_dialog, mock_mw):
        """Test adding a new deck with ID-based configuration"""
        # Mock user input
        mock_dialog.getText.side_effect = [
            ("https://example.com/test.tsv", True),  # URL input
            ("Test Deck", True)  # Deck name input
        ]
        
        # Mock collection and deck
        mock_deck = {"id": 1234567890, "name": "Test Deck"}
        mock_col = MagicMock()
        mock_col.decks.by_name.return_value = mock_deck
        
        # Set up mocks
        mock_mw.col = mock_col
        mock_mw.addonManager.getConfig.return_value = {"remote-decks": {}}
        
        # Mock validate_url and getRemoteDeck
        with patch('remote_decks.main.validate_url'), \
             patch('remote_decks.main.getRemoteDeck') as mock_get_remote, \
             patch('remote_decks.main.syncDecks'):
            
            mock_get_remote.return_value = MagicMock()
            
            # Run add new deck
            addNewDeck()
            
            # Verify configuration was saved with deck ID
            mock_mw.addonManager.writeConfig.assert_called_once()
            config = mock_mw.addonManager.writeConfig.call_args[0][1]
            self.assertIn("remote-decks", config)
            self.assertIn("https://example.com/test.tsv", config["remote-decks"])
            self.assertEqual(
                config["remote-decks"]["https://example.com/test.tsv"]["deck_id"],
                1234567890
            )

if __name__ == '__main__':
    unittest.main()