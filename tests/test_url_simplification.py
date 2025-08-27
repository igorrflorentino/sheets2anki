"""
Testes para as novas funcionalidades simplificadas de URL.
"""

import pytest


@pytest.mark.unit
class TestSpreadsheetIdExtraction:
    """Testes para extração de ID de planilha de URLs de edição."""

    def test_extract_from_edit_url(self):
        """Teste extração de ID de planilha de URL de edição."""
        from src.utils import extract_spreadsheet_id_from_url

        url = "https://docs.google.com/spreadsheets/d/1N-Va4ZzLUJBsD6wBaOkoeFTE6EnbZdaP/edit?usp=sharing"
        expected_id = "1N-Va4ZzLUJBsD6wBaOkoeFTE6EnbZdaP"
        
        result = extract_spreadsheet_id_from_url(url)
        assert result == expected_id

    def test_extract_from_edit_url_different_params(self):
        """Teste extração com diferentes parâmetros."""
        from src.utils import extract_spreadsheet_id_from_url

        url = "https://docs.google.com/spreadsheets/d/1abc123xyz/edit#gid=0"
        expected_id = "1abc123xyz"
        
        result = extract_spreadsheet_id_from_url(url)
        assert result == expected_id

    def test_extract_from_empty_url(self):
        """Teste com URL vazia."""
        from src.utils import extract_spreadsheet_id_from_url

        result = extract_spreadsheet_id_from_url("")
        assert result is None

    def test_extract_from_none_url(self):
        """Teste com URL None."""
        from src.utils import extract_spreadsheet_id_from_url

        result = extract_spreadsheet_id_from_url(None)
        assert result is None

    def test_extract_from_invalid_url(self):
        """Teste com URL que não é do Google Sheets."""
        from src.utils import extract_spreadsheet_id_from_url

        url = "https://example.com/not-google-sheets"
        
        result = extract_spreadsheet_id_from_url(url)
        assert result is None

    def test_extract_from_non_edit_google_url(self):
        """Teste com URL do Google Sheets mas não de edição."""
        from src.utils import extract_spreadsheet_id_from_url

        url = "https://docs.google.com/spreadsheets/d/1abc123/view"
        
        result = extract_spreadsheet_id_from_url(url)
        assert result is None


@pytest.mark.unit  
class TestSpreadsheetIdFromUrl:
    """Testes para obtenção de ID de planilha com validação."""

    def test_get_id_success(self):
        """Teste que obtém ID com sucesso."""
        from src.utils import get_spreadsheet_id_from_url

        url = "https://docs.google.com/spreadsheets/d/1abc123/edit?usp=sharing"
        
        result = get_spreadsheet_id_from_url(url)
        assert result == "1abc123"

    def test_get_id_success_long_id(self):
        """Teste com ID longo real."""
        from src.utils import get_spreadsheet_id_from_url

        url = "https://docs.google.com/spreadsheets/d/1N-Va4ZzLUJBsD6wBaOkoeFTE6EnbZdaP/edit?usp=sharing"
        
        result = get_spreadsheet_id_from_url(url)
        assert result == "1N-Va4ZzLUJBsD6wBaOkoeFTE6EnbZdaP"

    def test_get_id_invalid_url(self):
        """Teste que falha para URL inválida."""
        from src.utils import get_spreadsheet_id_from_url
        import pytest

        url = "https://example.com/invalid"
        
        with pytest.raises(ValueError) as exc_info:
            get_spreadsheet_id_from_url(url)
        
        assert "URL deve ser uma URL de edição válida" in str(exc_info.value)

    def test_get_id_empty_url(self):
        """Teste que falha para URL vazia."""
        from src.utils import get_spreadsheet_id_from_url
        import pytest

        with pytest.raises(ValueError) as exc_info:
            get_spreadsheet_id_from_url("")
        
        assert "URL deve ser uma URL de edição válida" in str(exc_info.value)


@pytest.mark.unit
class TestEditUrlToTsv:
    """Testes para conversão de URL de edição para TSV."""

    def test_convert_edit_url_success(self):
        """Teste conversão bem-sucedida."""
        from src.utils import convert_edit_url_to_tsv

        url = "https://docs.google.com/spreadsheets/d/1abc123/edit?usp=sharing"
        expected = "https://docs.google.com/spreadsheets/d/1abc123/export?format=tsv"
        
        result = convert_edit_url_to_tsv(url)
        assert result == expected

    def test_convert_edit_url_long_id(self):
        """Teste com ID longo real."""
        from src.utils import convert_edit_url_to_tsv

        url = "https://docs.google.com/spreadsheets/d/1N-Va4ZzLUJBsD6wBaOkoeFTE6EnbZdaP/edit?usp=sharing"
        expected = "https://docs.google.com/spreadsheets/d/1N-Va4ZzLUJBsD6wBaOkoeFTE6EnbZdaP/export?format=tsv"
        
        result = convert_edit_url_to_tsv(url)
        assert result == expected

    def test_convert_invalid_url(self):
        """Teste com URL inválida."""
        from src.utils import convert_edit_url_to_tsv
        import pytest

        url = "https://example.com/not-google"
        
        with pytest.raises(ValueError) as exc_info:
            convert_edit_url_to_tsv(url)
        
        assert "URL deve ser do Google Sheets" in str(exc_info.value)

    def test_convert_empty_url(self):
        """Teste com URL vazia."""
        from src.utils import convert_edit_url_to_tsv
        import pytest

        with pytest.raises(ValueError) as exc_info:
            convert_edit_url_to_tsv("")
        
        assert "URL deve ser uma string não vazia" in str(exc_info.value)

    def test_convert_non_edit_google_url(self):
        """Teste com URL do Google mas não de edição."""
        from src.utils import convert_edit_url_to_tsv
        import pytest

        url = "https://docs.google.com/spreadsheets/d/1abc123/view"
        
        with pytest.raises(ValueError) as exc_info:
            convert_edit_url_to_tsv(url)
        
        assert "URL deve ser uma URL de edição do Google Sheets" in str(exc_info.value)


@pytest.mark.unit
class TestValidateUrl:
    """Testes para validação de URLs (requer conexão de rede)."""

    def test_validate_url_format_check(self):
        """Teste validação de formato sem conectividade."""
        from src.utils import validate_url
        import pytest

        # URL que não é do Google Sheets
        url = "https://example.com/invalid"
        
        with pytest.raises(ValueError) as exc_info:
            validate_url(url)
        
        assert "URL inválida" in str(exc_info.value)

    def test_validate_empty_url(self):
        """Teste validação de URL vazia."""
        from src.utils import validate_url
        import pytest

        with pytest.raises(ValueError) as exc_info:
            validate_url("")
        
        assert "URL deve ser uma string não vazia" in str(exc_info.value)

    def test_validate_invalid_protocol(self):
        """Teste validação de protocolo inválido."""
        from src.utils import validate_url
        import pytest

        url = "ftp://docs.google.com/spreadsheets/d/1abc123/edit"
        
        with pytest.raises(ValueError) as exc_info:
            validate_url(url)
        
        assert "Deve começar com http:// ou https://" in str(exc_info.value)
