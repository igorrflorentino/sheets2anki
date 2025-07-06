import unittest
from unittest.mock import patch, MagicMock
from .parseRemoteDeck import (
    parse_tags, parse_tsv_data, validate_tsv_headers, 
    has_cloze_deletion, getRemoteDeck, RemoteDeck,
    build_remote_deck_from_tsv
)
from . import column_definitions as cols

class TestParseRemoteDeck(unittest.TestCase):
    def test_parse_tags_empty(self):
        """Test parsing empty tag strings"""
        self.assertEqual(parse_tags(""), [])
        self.assertEqual(parse_tags(" "), [])
        self.assertEqual(parse_tags(None), [])

    def test_parse_tags_single(self):
        """Test parsing a single tag"""
        self.assertEqual(
            parse_tags("type1: name1"),
            ["type1::name1"]
        )

    def test_parse_tags_multiple(self):
        """Test parsing multiple tags"""
        self.assertEqual(
            parse_tags("type1: name1, type1: name2, type2: name1"),
            ["type1::name1", "type1::name2", "type2::name1"]
        )

    def test_parse_tags_spaces(self):
        """Test parsing tags with extra spaces"""
        self.assertEqual(
            parse_tags("  type1  :  name1  ,  type2  :  name2  "),
            ["type1::name1", "type2::name2"]
        )

    def test_parse_tags_invalid(self):
        """Test parsing invalid tag formats"""
        # Missing colon
        self.assertEqual(parse_tags("type1 name1"), [])
        # Empty type
        self.assertEqual(parse_tags(": name1"), [])
        # Empty name
        self.assertEqual(parse_tags("type1:"), [])
        # Mixed valid and invalid
        self.assertEqual(
            parse_tags("type1: name1, invalid_tag, type2: name2"),
            ["type1::name1", "type2::name2"]
        )

    def test_parse_tags_special_chars(self):
        """Test parsing tags with special characters and spaces"""
        self.assertEqual(
            parse_tags("type one: name 1!, type-two: name@2"),
            ["type_one::name_1", "type_two::name_2"]
        )

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

    def test_build_remote_deck_missing_required(self):
        """Test building remote deck with missing required fields"""
        data = [cols.REQUIRED_COLUMNS]  # Headers
        row = [""] * len(cols.REQUIRED_COLUMNS)  # Empty row
        data.append(row)
        
        deck = build_remote_deck_from_tsv(data)
        self.assertEqual(len(deck.questions), 0)  # Should skip invalid row

if __name__ == '__main__':
    unittest.main()