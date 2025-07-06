import unittest
from .parseRemoteDeck import parse_tags

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

if __name__ == '__main__':
    unittest.main()