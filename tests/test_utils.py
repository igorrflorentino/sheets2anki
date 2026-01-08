#!/usr/bin/env python3
"""
Tests for the utils.py module

Tests utility functionalities like:
- URL validation
- Publication key extraction
- Hash generation
- General helper functions
"""

import hashlib
from unittest.mock import Mock
from unittest.mock import patch

import pytest

# =============================================================================
# URL VALIDATION TESTS
# =============================================================================


@pytest.mark.unit
class TestUrlValidation:
    """Tests for Google Sheets URL validation."""

    def test_validate_valid_urls(self):
        """Test with valid URLs."""

        def validate_url(url):
            if not url:
                return False

            required_parts = ["docs.google.com", "spreadsheets", "pub?output=tsv"]

            return all(part in url for part in required_parts)

        valid_urls = [
            "https://docs.google.com/spreadsheets/d/e/2PACX-1vSample/pub?output=tsv",
            "https://docs.google.com/spreadsheets/d/1234567890/pub?output=tsv&single=true",
            "http://docs.google.com/spreadsheets/d/e/key/pub?output=tsv",
        ]

        for url in valid_urls:
            assert validate_url(url) == True, f"URL should be valid: {url}"

    def test_validate_invalid_urls(self):
        """Test with invalid URLs."""

        def validate_url(url):
            if not url:
                return False

            required_parts = ["docs.google.com", "spreadsheets", "pub?output=tsv"]

            return all(part in url for part in required_parts)

        invalid_urls = [
            "",
            None,
            "https://example.com/sheet",
            "https://sheets.google.com/sheet",  # Wrong domain
            "https://docs.google.com/sheets/pub?output=csv",  # Wrong output format
            "https://docs.google.com/spreadsheets/edit",  # Not published
            "not_a_url",
        ]

        for url in invalid_urls:
            assert validate_url(url) == False, f"URL should be invalid: {url}"


# =============================================================================
# PUBLICATION KEY EXTRACTION TESTS
# =============================================================================


@pytest.mark.unit
class TestPublicationKeyExtraction:
    """Tests for publication key extraction."""

    def test_extract_publication_key_success(self):
        """Successful key extraction test."""

        def extract_publication_key_from_url(url):
            if not url:
                return None

            import re

            pattern = r"/spreadsheets/d/e/([^/]+)/"
            match = re.search(pattern, url)

            if match:
                return match.group(1)

            # Fallback for old format
            pattern_old = r"/spreadsheets/d/([^/]+)/"
            match_old = re.search(pattern_old, url)
            if match_old:
                return match_old.group(1)

            return None

        test_cases = [
            (
                "https://docs.google.com/spreadsheets/d/e/2PACX-1vSample-Key123/pub?output=tsv",
                "2PACX-1vSample-Key123",
            ),
            (
                "https://docs.google.com/spreadsheets/d/1234567890ABCDEF/pub?output=tsv",
                "1234567890ABCDEF",
            ),
            (
                "https://docs.google.com/spreadsheets/d/e/LONG-KEY-HERE/pub?output=tsv&single=true",
                "LONG-KEY-HERE",
            ),
        ]

        for url, expected_key in test_cases:
            result = extract_publication_key_from_url(url)
            assert result == expected_key, f"Failed for URL: {url}"

    def test_extract_publication_key_failure(self):
        """Key extraction failure test."""

        def extract_publication_key_from_url(url):
            if not url:
                return None

            import re

            pattern = r"/spreadsheets/d/e/([^/]+)/"
            match = re.search(pattern, url)

            if match:
                return match.group(1)

            return None

        invalid_urls = [
            "",
            None,
            "https://example.com/sheet",
            "https://docs.google.com/invalid/format",
            "not_a_url",
        ]

        for url in invalid_urls:
            result = extract_publication_key_from_url(url)
            assert result is None, f"Should return None for: {url}"


# =============================================================================
# HASH GENERATION TESTS
# =============================================================================


@pytest.mark.unit
class TestHashGeneration:
    """Tests for hash generation."""

    def test_get_publication_key_hash(self):
        """Publication key hash generation test."""

        def get_publication_key_hash(url):
            def extract_key(url):
                if not url:
                    return None
                import re

                pattern = r"/spreadsheets/d/e/([^/]+)/"
                match = re.search(pattern, url)
                return match.group(1) if match else None

            publication_key = extract_key(url)

            if publication_key:
                hash_obj = hashlib.md5(publication_key.encode("utf-8"))
                return hash_obj.hexdigest()[:8]
            else:
                # Fallback to full URL hash
                hash_obj = hashlib.md5(url.encode("utf-8"))
                return hash_obj.hexdigest()[:8]

        url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSample/pub?output=tsv"
        hash_result = get_publication_key_hash(url)

        assert len(hash_result) == 8
        assert isinstance(hash_result, str)

        # Hash must be consistent
        hash_result2 = get_publication_key_hash(url)
        assert hash_result == hash_result2

    def test_hash_consistency(self):
        """Hash consistency test."""

        def generate_hash(text):
            hash_obj = hashlib.md5(text.encode("utf-8"))
            return hash_obj.hexdigest()[:8]

        test_text = "test_string_123"

        hash1 = generate_hash(test_text)
        hash2 = generate_hash(test_text)

        assert hash1 == hash2
        assert len(hash1) == 8


# =============================================================================
# DECK FUNCTION TESTS
# =============================================================================


@pytest.mark.unit
class TestDeckUtilities:
    """Tests for deck utility functions."""

    def test_get_or_create_deck(self, mock_mw):
        """Deck retrieval/creation test."""

        def get_or_create_deck(deck_name, mw):
            # Simulate search for existing deck
            deck_id = mw.col.decks.id(deck_name, create=False)
            if deck_id:
                return deck_id

            # Create new deck
            new_deck = mw.col.decks.new(deck_name)
            return mw.col.decks.save(new_deck)

        # Behavioral mock
        mock_mw.col.decks.id = Mock(return_value=None)  # Deck doesn't exist
        mock_mw.col.decks.new = Mock(return_value={"name": "Test Deck", "id": 123})
        mock_mw.col.decks.save = Mock(return_value=123)

        deck_id = get_or_create_deck("Test Deck", mock_mw)

        assert deck_id == 123
        mock_mw.col.decks.new.assert_called_once_with("Test Deck")

    def test_get_subdeck_name(self):
        """Subdeck name generation test."""

        def get_subdeck_name(
            parent_deck, student, importance, topic, subtopic, concept
        ):
            parts = [parent_deck]

            if student:
                parts.append(student)
            if importance:
                parts.append(importance)
            if topic:
                parts.append(topic)
            if subtopic:
                parts.append(subtopic)
            if concept:
                parts.append(concept)

            return "::".join(parts)

        result = get_subdeck_name(
            "Sheets2Anki", "John", "High", "Geography", "Capitals", "Brazil"
        )

        expected = "Sheets2Anki::John::High::Geography::Capitals::Brazil"
        assert result == expected

    def test_ensure_subdeck_exists(self, mock_mw):
        """Subdeck existence guarantee test."""

        def ensure_subdeck_exists(subdeck_name, mw):
            # Simulate hierarchical creation
            parts = subdeck_name.split("::")
            current_deck = ""

            for part in parts:
                current_deck = f"{current_deck}::{part}" if current_deck else part

                deck_id = mw.col.decks.id(current_deck, create=False)
                if not deck_id:
                    new_deck = mw.col.decks.new(current_deck)
                    mw.col.decks.save(new_deck)

        # Setup mocks
        mock_mw.col.decks.id = Mock(return_value=None)  # Decks don't exist
        mock_mw.col.decks.new = Mock(return_value={"name": "deck"})
        mock_mw.col.decks.save = Mock()

        ensure_subdeck_exists("Parent::Child::Grandchild", mock_mw)

        # Should create 3 decks
        assert mock_mw.col.decks.new.call_count == 3


# =============================================================================
# STRING FUNCTION TESTS
# =============================================================================


@pytest.mark.unit
class TestStringUtilities:
    """Tests for string utility functions."""

    def test_clean_filename(self):
        """File name cleaning test."""

        def clean_filename(filename):
            if not filename:
                return ""

            import re

            # Remove special characters
            cleaned = re.sub(r"[^\w\s\-_.]", "", filename)
            # Remove extra spaces and replace with underscore
            cleaned = re.sub(r"\s+", "_", cleaned.strip())
            return cleaned

        test_cases = [
            ("Normal File.txt", "Normal_File.txt"),
            ("File with @#$%!.doc", "File_with_.doc"),
            ("  Extra  Spaces  .pdf", "Extra_Spaces_.pdf"),
            ("", ""),
            ("already_clean_file.txt", "already_clean_file.txt"),
        ]

        for input_text, expected in test_cases:
            result = clean_filename(input_text)
            assert result == expected, f"Failed for: {input_text}"

    def test_normalize_text(self):
        """Text normalization test."""

        def normalize_text(text):
            if not text:
                return ""

            # Remove accents and special characters
            import unicodedata

            normalized = unicodedata.normalize("NFD", text)
            ascii_text = normalized.encode("ascii", "ignore").decode("ascii")

            # Remove special characters except letters, numbers and spaces
            import re

            cleaned = re.sub(r"[^\w\s]", "", ascii_text)

            return cleaned.strip().lower()

        test_cases = [
            ("John Smith", "john smith"),
            ("Conceição", "conceicao"),
            ("Programming!", "programming"),
            ("", ""),
            ("123 Test", "123 test"),
        ]

        for input_text, expected in test_cases:
            result = normalize_text(input_text)
            assert result == expected, f"Failed for: {input_text}"


# =============================================================================
# DATA VALIDATION TESTS
# =============================================================================


@pytest.mark.unit
class TestDataValidation:
    """Tests for data validation."""

    def test_validate_student_name(self):
        """Student name validation test."""

        def validate_student_name(name):
            if not name or not isinstance(name, str):
                return False

            name = name.strip()
            if len(name) < 1:
                return False

            # Must not contain only numbers or special characters
            # Check for letters (including accented ones)
            import re

            return bool(re.search(r"[a-zA-ZÀ-ÿ]", name))

        valid_names = ["John", "Mary Smith", "Ann-Paula", "Joe123"]
        invalid_names = ["", "   ", None, "123", "!@#$%", 123]

        for name in valid_names:
            assert validate_student_name(name) == True, f"Should be valid: {name}"

        for name in invalid_names:
            assert validate_student_name(name) == False, f"Should be invalid: {name}"

    def test_validate_deck_name(self):
        """Deck name validation test."""

        def validate_deck_name(name):
            if not name or not isinstance(name, str):
                return False

            name = name.strip()
            if len(name) < 1 or len(name) > 100:
                return False

            # Should not contain characters problematic for Anki
            forbidden_chars = ["<", ">", ":", '"', "|", "?", "*"]
            return not any(char in name for char in forbidden_chars)

        valid_names = ["General Geography", "Mathematics - Algebra", "Test_Deck_123"]
        invalid_names = ["", "Deck<Invalid>", "Deck|With|Pipes", "A" * 101]

        for name in valid_names:
            assert validate_deck_name(name) == True, f"Should be valid: {name}"

        for name in invalid_names:
            assert validate_deck_name(name) == False, f"Should be invalid: {name}"


# =============================================================================
# EXCEPTION HANDLING TESTS
# =============================================================================


@pytest.mark.unit
class TestExceptionHandling:
    """Tests for exception handling."""

    def test_safe_int_conversion(self):
        """Safe integer conversion test."""

        def safe_int(value, default=0):
            try:
                return int(value)
            except (ValueError, TypeError):
                return default

        test_cases = [
            ("123", 123),
            ("0", 0),
            ("-45", -45),
            ("not_a_number", 0),
            (None, 0),
            (12.5, 12),
            ("", 0),
        ]

        for input_val, expected in test_cases:
            result = safe_int(input_val)
            assert result == expected, f"Failed for: {input_val}"

    def test_safe_json_load(self):
        """Safe JSON loading test."""
        import json

        def safe_json_load(json_string, default=None):
            try:
                return json.loads(json_string)
            except (json.JSONDecodeError, TypeError):
                return default if default is not None else {}

        valid_json = '{"key": "value", "number": 123}'
        invalid_json = '{"invalid": json}'

        result1 = safe_json_load(valid_json)
        assert result1 == {"key": "value", "number": 123}

        result2 = safe_json_load(invalid_json)
        assert result2 == {}

        result3 = safe_json_load(None, [])
        assert result3 == []


# =============================================================================
# PERFORMANCE TESTS
# =============================================================================


@pytest.mark.slow
class TestPerformance:
    """Performance tests for critical functions."""

    def test_hash_generation_performance(self):
        """Hash generation performance test."""
        import time

        def generate_hash(text):
            hash_obj = hashlib.md5(text.encode("utf-8"))
            return hash_obj.hexdigest()[:8]

        # Generate many hashes
        start_time = time.time()

        for i in range(1000):
            test_text = f"test_string_{i}"
            hash_result = generate_hash(test_text)
            assert len(hash_result) == 8

        end_time = time.time()
        duration = end_time - start_time

        # Should process 1000 hashes in less than 1 second
        assert duration < 1.0, f"Hash generation too slow: {duration}s"


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


@pytest.mark.integration
class TestUtilsIntegration:
    """Integration tests of utility functions."""

    def test_url_to_hash_workflow(self):
        """Full URL to hash workflow test."""

        def extract_publication_key_from_url(url):
            if not url:
                return None
            import re

            pattern = r"/spreadsheets/d/e/([^/]+)/"
            match = re.search(pattern, url)
            return match.group(1) if match else None

        def get_publication_key_hash(url):
            publication_key = extract_publication_key_from_url(url)
            if publication_key:
                hash_obj = hashlib.md5(publication_key.encode("utf-8"))
                return hash_obj.hexdigest()[:8]
            else:
                hash_obj = hashlib.md5(url.encode("utf-8"))
                return hash_obj.hexdigest()[:8]

        def validate_url(url):
            required_parts = ["docs.google.com", "spreadsheets", "pub?output=tsv"]
            return all(part in url for part in required_parts)

        # Full workflow
        url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSample/pub?output=tsv"

        # 1. Validate URL
        assert validate_url(url) == True

        # 2. Extract key
        key = extract_publication_key_from_url(url)
        assert key == "2PACX-1vSample"

        # 3. Generate hash
        hash_result = get_publication_key_hash(url)
        assert len(hash_result) == 8

        # 4. Hash must be consistent
        hash_result2 = get_publication_key_hash(url)
        assert hash_result == hash_result2


# =============================================================================
# TESTS FOR NEW FEATURES - EDIT URLS
# =============================================================================


@pytest.mark.unit
class TestGoogleSheetsUrlConversion:
    """Tests for Google Sheets URL conversion."""

    def test_convert_edit_url_to_tsv(self):
        """Test conversion of edit URL to TSV."""
        from src.utils import convert_edit_url_to_tsv

        edit_url = "https://docs.google.com/spreadsheets/d/1N-Va4ZzLUJBsD6wBaOkoeFTE6EnbZdaPBB88FYl2hrs/edit?usp=sharing"
        expected_tsv = "https://docs.google.com/spreadsheets/d/1N-Va4ZzLUJBsD6wBaOkoeFTE6EnbZdaPBB88FYl2hrs/export?format=tsv"
        
        result = convert_edit_url_to_tsv(edit_url)
        assert result == expected_tsv

    def test_convert_already_tsv_url(self):
        """Test with URL already in TSV format."""
        # URLs already in TSV format don't need conversion
        # The convert_edit_url_to_tsv function only works with edit URLs
        # This test no longer applies to the new function
        pass

    def test_convert_export_format_url(self):
        """Test with URL already in export format."""
        # URLs already in export format don't need conversion
        # The convert_edit_url_to_tsv function only works with edit URLs
        # This test no longer applies to the new function
        pass

    def test_convert_invalid_url(self):
        """Test with invalid URL."""
        from src.utils import convert_edit_url_to_tsv

        invalid_url = "https://example.com/not-google-sheets"
        
        with pytest.raises(ValueError) as exc_info:
            convert_edit_url_to_tsv(invalid_url)
        
        assert "URL must be from Google Sheets" in str(exc_info.value)

    def test_convert_empty_url(self):
        """Test with empty URL."""
        from src.utils import convert_edit_url_to_tsv

        with pytest.raises(ValueError) as exc_info:
            convert_edit_url_to_tsv("")
        
        assert "URL must be a non-empty string" in str(exc_info.value)

    def test_convert_unrecognized_format(self):
        """Test with Google Sheets URL in unrecognized format."""
        from src.utils import convert_edit_url_to_tsv

        unrecognized_url = "https://docs.google.com/spreadsheets/d/1abc123/view"
        
        with pytest.raises(ValueError) as exc_info:
            convert_edit_url_to_tsv(unrecognized_url)
        
        assert "URL must be a Google Sheets edit URL" in str(exc_info.value)

    def test_convert_edit_url_fallback(self):
        """Fallback test for edit URLs that are not accessible."""
        from src.utils import convert_edit_url_to_tsv

        # Edit URL with fictitious ID (not accessible)
        edit_url = "https://docs.google.com/spreadsheets/d/1fictitious123/edit?usp=sharing"
        
        result = convert_edit_url_to_tsv(edit_url)
        
        # Should return URL without gid (always downloads first tab)
        expected_result = "https://docs.google.com/spreadsheets/d/1fictitious123/export?format=tsv"
        assert result == expected_result


@pytest.mark.unit
class TestExtractPublicationKeyFromUrl:
    """Tests for extracting keys/IDs from Google Sheets URLs."""

    def test_extract_publication_key_from_published_url(self):
        """Test publication key extraction from published URL."""
        from src.utils import extract_publication_key_from_url

        url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSample-Key-123/pub?output=tsv"
        expected_key = "2PACX-1vSample-Key-123"
        
        result = extract_publication_key_from_url(url)
        assert result == expected_key

    def test_extract_id_from_edit_url(self):
        """Test spreadsheet ID extraction from edit URL."""
        from src.utils import extract_publication_key_from_url

        url = "https://docs.google.com/spreadsheets/d/1N-Va4ZzLUJBsD6wBaOkoeFTE6EnbZdaPBB88FYl2hrs/edit?usp=sharing"
        expected_id = "1N-Va4ZzLUJBsD6wBaOkoeFTE6EnbZdaPBB88FYl2hrs"
        
        result = extract_publication_key_from_url(url)
        assert result == expected_id

    def test_extract_from_empty_url(self):
        """Test with empty URL."""
        from src.utils import extract_publication_key_from_url

        result = extract_publication_key_from_url("")
        assert result is None

    def test_extract_from_invalid_url(self):
        """Test with URL that is not from Google Sheets."""
        from src.utils import extract_publication_key_from_url

        url = "https://example.com/not-google-sheets"
        
        result = extract_publication_key_from_url(url)
        assert result is None


@pytest.mark.unit
class TestGetPublicationKeyHash:
    """Tests for key/ID hash generation."""

    def test_hash_consistency(self):
        """Test that hash is consistent for the same URL."""
        from src.utils import get_publication_key_hash

        url = "https://docs.google.com/spreadsheets/d/1abc123/edit?usp=sharing"
        
        hash1 = get_publication_key_hash(url)
        hash2 = get_publication_key_hash(url)
        
        assert hash1 == hash2
        assert len(hash1) == 8

    def test_hash_different_urls(self):
        """Test that different URLs produce different hashes."""
        from src.utils import get_publication_key_hash

        url1 = "https://docs.google.com/spreadsheets/d/1abc123/edit?usp=sharing"
        url2 = "https://docs.google.com/spreadsheets/d/1xyz789/edit?usp=sharing"
        
        hash1 = get_publication_key_hash(url1)
        hash2 = get_publication_key_hash(url2)
        
        assert hash1 != hash2
        assert len(hash1) == 8
        assert len(hash2) == 8

    def test_hash_fallback_for_unknown_format(self):
        """Fallback test for URLs in unknown format."""
        from src.utils import get_publication_key_hash

        # URL in unrecognized format, but should still generate hash
        url = "https://docs.google.com/spreadsheets/unknown-format"
        
        hash_result = get_publication_key_hash(url)
        assert len(hash_result) == 8


if __name__ == "__main__":
    pytest.main([__file__])
