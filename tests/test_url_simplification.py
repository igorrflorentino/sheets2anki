"""
Tests for the new simplified URL functionalities.
"""

import pytest


@pytest.mark.unit
class TestSpreadsheetIdExtraction:
    """Tests for spreadsheet ID extraction from edit URLs."""

    def test_extract_from_edit_url(self):
        """Test spreadsheet ID extraction from edit URL."""
        from src.utils import extract_spreadsheet_id_from_url

        url = "https://docs.google.com/spreadsheets/d/1N-Va4ZzLUJBsD6wBaOkoeFTE6EnbZdaP/edit?usp=sharing"
        expected_id = "1N-Va4ZzLUJBsD6wBaOkoeFTE6EnbZdaP"
        
        result = extract_spreadsheet_id_from_url(url)
        assert result == expected_id

    def test_extract_from_edit_url_different_params(self):
        """Test extraction with different parameters."""
        from src.utils import extract_spreadsheet_id_from_url

        url = "https://docs.google.com/spreadsheets/d/1abc123xyz/edit#gid=0"
        expected_id = "1abc123xyz"
        
        result = extract_spreadsheet_id_from_url(url)
        assert result == expected_id

    def test_extract_from_empty_url(self):
        """Test with empty URL."""
        from src.utils import extract_spreadsheet_id_from_url

        result = extract_spreadsheet_id_from_url("")
        assert result is None

    def test_extract_from_none_url(self):
        """Test with None URL."""
        from src.utils import extract_spreadsheet_id_from_url

        result = extract_spreadsheet_id_from_url(None)
        assert result is None

    def test_extract_from_invalid_url(self):
        """Test with a non-Google Sheets URL."""
        from src.utils import extract_spreadsheet_id_from_url

        url = "https://example.com/not-google-sheets"
        
        result = extract_spreadsheet_id_from_url(url)
        assert result is None

    def test_extract_from_non_edit_google_url(self):
        """Test with Google Sheets URL but not an edit one."""
        from src.utils import extract_spreadsheet_id_from_url

        url = "https://docs.google.com/spreadsheets/d/1abc123/view"
        
        result = extract_spreadsheet_id_from_url(url)
        assert result is None


@pytest.mark.unit  
class TestSpreadsheetIdFromUrl:
    """Tests for getting spreadsheet ID with validation."""

    def test_get_id_success(self):
        """Test that gets ID successfully."""
        from src.utils import get_spreadsheet_id_from_url

        url = "https://docs.google.com/spreadsheets/d/1abc123/edit?usp=sharing"
        
        result = get_spreadsheet_id_from_url(url)
        assert result == "1abc123"

    def test_get_id_success_long_id(self):
        """Test with a real long ID."""
        from src.utils import get_spreadsheet_id_from_url

        url = "https://docs.google.com/spreadsheets/d/1N-Va4ZzLUJBsD6wBaOkoeFTE6EnbZdaP/edit?usp=sharing"
        
        result = get_spreadsheet_id_from_url(url)
        assert result == "1N-Va4ZzLUJBsD6wBaOkoeFTE6EnbZdaP"

    def test_get_id_invalid_url(self):
        """Test that fails for invalid URL."""
        from src.utils import get_spreadsheet_id_from_url
        import pytest

        url = "https://example.com/invalid"
        
        with pytest.raises(ValueError) as exc_info:
            get_spreadsheet_id_from_url(url)
        
        assert "valid Google Sheets edit URL" in str(exc_info.value)

    def test_get_id_empty_url(self):
        """Test that fails for empty URL."""
        from src.utils import get_spreadsheet_id_from_url
        import pytest

        with pytest.raises(ValueError) as exc_info:
            get_spreadsheet_id_from_url("")
        
        assert "valid Google Sheets edit URL" in str(exc_info.value)


@pytest.mark.unit
class TestEditUrlToTsv:
    """Tests for converting edit URL to TSV."""

    def test_convert_edit_url_success(self):
        """Successful conversion test."""
        from src.utils import convert_edit_url_to_tsv

        url = "https://docs.google.com/spreadsheets/d/1abc123/edit?usp=sharing"
        expected = "https://docs.google.com/spreadsheets/d/1abc123/export?format=tsv"
        
        result = convert_edit_url_to_tsv(url)
        assert result == expected

    def test_convert_edit_url_long_id(self):
        """Test with a real long ID."""
        from src.utils import convert_edit_url_to_tsv

        url = "https://docs.google.com/spreadsheets/d/1N-Va4ZzLUJBsD6wBaOkoeFTE6EnbZdaP/edit?usp=sharing"
        expected = "https://docs.google.com/spreadsheets/d/1N-Va4ZzLUJBsD6wBaOkoeFTE6EnbZdaP/export?format=tsv"
        
        result = convert_edit_url_to_tsv(url)
        assert result == expected

    def test_convert_invalid_url(self):
        """Test with invalid URL."""
        from src.utils import convert_edit_url_to_tsv
        import pytest

        url = "https://example.com/not-google"
        
        with pytest.raises(ValueError) as exc_info:
            convert_edit_url_to_tsv(url)
        
        assert "URL must be from Google Sheets" in str(exc_info.value)

    def test_convert_empty_url(self):
        """Test with empty URL."""
        from src.utils import convert_edit_url_to_tsv
        import pytest

        with pytest.raises(ValueError) as exc_info:
            convert_edit_url_to_tsv("")
        
        assert "URL must be a non-empty string" in str(exc_info.value)

    def test_convert_non_edit_google_url(self):
        """Test with Google Sheets URL but not an edit one."""
        from src.utils import convert_edit_url_to_tsv
        import pytest

        url = "https://docs.google.com/spreadsheets/d/1abc123/view"
        
        with pytest.raises(ValueError) as exc_info:
            convert_edit_url_to_tsv(url)
        
        assert "URL must be a Google Sheets edit URL" in str(exc_info.value)


@pytest.mark.unit
class TestValidateUrl:
    """Tests for URL validation (requires network connection)."""

    def test_validate_url_format_check(self):
        """Format validation test without connectivity."""
        from src.utils import validate_url
        import pytest

        # Non-Google Sheets URL
        url = "https://example.com/invalid"
        
        with pytest.raises(ValueError) as exc_info:
            validate_url(url)
        
        assert "Invalid URL" in str(exc_info.value)

    def test_validate_empty_url(self):
        """Empty URL validation test."""
        from src.utils import validate_url
        import pytest

        with pytest.raises(ValueError) as exc_info:
            validate_url("")
        
        assert "URL must be a non-empty string" in str(exc_info.value)

    def test_validate_invalid_protocol(self):
        """Invalid protocol validation test."""
        from src.utils import validate_url
        import pytest

        url = "ftp://docs.google.com/spreadsheets/d/1abc123/edit"
        
        with pytest.raises(ValueError) as exc_info:
            validate_url(url)
        
        assert "Must start with http:// or https://" in str(exc_info.value)
