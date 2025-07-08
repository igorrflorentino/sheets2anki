import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Adicionar o diretório pai ao path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from remote_decks.parseRemoteDeck import (
    create_tags_from_fields, parse_tsv_data, validate_tsv_headers, 
    has_cloze_deletion, getRemoteDeck, RemoteDeck,
    build_remote_deck_from_tsv, clean_tag_text
)
from remote_decks import column_definitions as cols

class TestParseRemoteDeck(unittest.TestCase):
    def test_clean_tag_text(self):
        """Test cleaning text for tag use"""
        self.assertEqual(clean_tag_text(""), "")
        self.assertEqual(clean_tag_text(" "), "")
        self.assertEqual(clean_tag_text(None), "")
        self.assertEqual(clean_tag_text("tag name!@#"), "tag_name")
        self.assertEqual(clean_tag_text(" tag  name "), "tag_name")

    def test_create_tags_from_fields_empty(self):
        """Test creating tags from empty fields"""
        fields = {
            cols.TOPICO: "",
            cols.SUBTOPICO: "",
            cols.BANCAS: "",
            cols.ANO: "",
            cols.MORE_TAGS: ""
        }
        self.assertEqual(create_tags_from_fields(fields), [])

    def test_create_tags_from_fields_full(self):
        """Test creating tags from complete fields"""
        fields = {
            cols.TOPICO: "Direito Civil",
            cols.SUBTOPICO: "Contratos, Obrigações",
            cols.BANCAS: "CESPE, FGV",
            cols.ANO: "2023",
            cols.MORE_TAGS: "importante, revisao"
        }
        expected_tags = [
            "topicos::Direito_Civil::Contratos",
            "topicos::Direito_Civil::Obrigacoes",
            "bancas::CESPE",
            "bancas::FGV",
            "provas::2023",
            "variado::importante",
            "variado::revisao"
        ]
        self.assertEqual(create_tags_from_fields(fields), expected_tags)

    def test_create_tags_from_fields_multiple_subtopics(self):
        """Test creating tags with multiple subtopics for the same topic"""
        fields = {
            cols.TOPICO: "Direito Penal",
            cols.SUBTOPICO: "Crimes contra a pessoa, Crimes contra o patrimônio, Crimes contra a honra",
            cols.BANCAS: "",
            cols.ANO: "",
            cols.MORE_TAGS: ""
        }
        expected_tags = [
            "topicos::Direito_Penal::Crimes_contra_a_pessoa",
            "topicos::Direito_Penal::Crimes_contra_o_patrimonio",
            "topicos::Direito_Penal::Crimes_contra_a_honra"
        ]
        self.assertEqual(create_tags_from_fields(fields), expected_tags)

    def test_create_tags_from_fields_partial(self):
        """Test creating tags from partial fields"""
        fields = {
            cols.TOPICO: "Direito Civil",
            cols.SUBTOPICO: "",  # Empty subtopic
            cols.BANCAS: "CESPE",
            cols.ANO: "2023",
            cols.MORE_TAGS: ""  # Empty additional tags
        }
        expected_tags = [
            "topicos::Direito_Civil",
            "bancas::CESPE",
            "provas::2023"
        ]
        self.assertEqual(create_tags_from_fields(fields), expected_tags)

    def test_parse_tsv_data_valid(self):
        """Test parsing valid TSV data"""
        tsv_data = "col1\tcol2\nval1\tval2\nval3\tval4"
        result = parse_tsv_data(tsv_data)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], ["col1", "col2"])
        self.assertEqual(result[1], ["val1", "val2"])
        self.assertEqual(result[2], ["val3", "val4"])

    def test_parse_tsv_data_empty(self):
        """Test parsing empty TSV data"""
        with self.assertRaises(ValueError) as context:
            parse_tsv_data("")
        self.assertEqual(str(context.exception), "TSV file is empty")

    def test_parse_tsv_data_headers_only(self):
        """Test parsing TSV with only headers"""
        with self.assertRaises(ValueError) as context:
            parse_tsv_data("col1\tcol2")
        self.assertEqual(str(context.exception), "TSV file must contain headers and at least one card")

    def test_validate_tsv_headers_valid(self):
        """Test validating TSV headers with all required columns"""
        headers = cols.REQUIRED_COLUMNS
        result = validate_tsv_headers(headers)
        self.assertEqual(result, headers)

    def test_validate_tsv_headers_missing(self):
        """Test validating TSV headers with missing required columns"""
        headers = [cols.ID, cols.PERGUNTA]  # Missing other required columns
        with self.assertRaises(ValueError) as context:
            validate_tsv_headers(headers)
        self.assertTrue("Missing required columns:" in str(context.exception))

    def test_has_cloze_deletion(self):
        """Test cloze deletion detection"""
        self.assertTrue(has_cloze_deletion("This is a {{c1::test}} question"))
        self.assertTrue(has_cloze_deletion("Multiple {{c1::cloze}} {{c2::deletions}}"))
        self.assertFalse(has_cloze_deletion("No cloze here"))
        self.assertFalse(has_cloze_deletion("Invalid {{c1:cloze}}"))  # Missing second colon
        self.assertFalse(has_cloze_deletion(""))
        self.assertFalse(has_cloze_deletion(None))

    @patch('requests.get')
    def test_get_remote_deck_success(self, mock_get):
        """Test successful remote deck retrieval"""
        mock_response = MagicMock()
        mock_response.content = "ID\tPERGUNTA\tINFO_1\nid1\tq1\ta1".encode('utf-8')
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        deck = getRemoteDeck("http://example.com/test.tsv")
        self.assertIsInstance(deck, RemoteDeck)
        self.assertEqual(len(deck.questions), 1)

    @patch('requests.get')
    def test_get_remote_deck_network_error(self, mock_get):
        """Test remote deck retrieval with network error"""
        mock_get.side_effect = Exception("Network error")
        with self.assertRaises(Exception) as context:
            getRemoteDeck("http://example.com/test.tsv")
        self.assertTrue("Error downloading or reading the TSV" in str(context.exception))

    def test_build_remote_deck_valid(self):
        """Test building remote deck from valid TSV data"""
        data = [cols.REQUIRED_COLUMNS]  # Headers
        row = ["1"] * len(cols.REQUIRED_COLUMNS)  # Sample data row
        data.append(row)
        
        deck = build_remote_deck_from_tsv(data)
        self.assertIsInstance(deck, RemoteDeck)
        self.assertEqual(len(deck.questions), 1)
        self.assertIn('tags', deck.questions[0])  # Verify tags are included
        self.assertIsInstance(deck.questions[0]['tags'], list)  # Verify tags is a list

    def test_build_remote_deck_missing_required(self):
        """Test building remote deck with missing required fields"""
        data = [cols.REQUIRED_COLUMNS]  # Headers
        row = [""] * len(cols.REQUIRED_COLUMNS)  # Empty row
        data.append(row)
        
        deck = build_remote_deck_from_tsv(data)
        self.assertEqual(len(deck.questions), 0)  # Should skip invalid row

if __name__ == '__main__':
    unittest.main()