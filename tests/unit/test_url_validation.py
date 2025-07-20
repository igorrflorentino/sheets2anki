"""
Testes para a funcionalidade de validação de URLs.
"""
import pytest
from src.validation import validate_url

class TestUrlValidation:
    """Testes para a funcionalidade de validação de URLs."""
    
    @pytest.mark.parametrize("url,should_raise", [
        ('https://docs.google.com/spreadsheets/d/1abc/export?format=tsv', False),
        ('https://docs.google.com/spreadsheets/d/e/1abc/pub?output=tsv', False),
        ('https://example.com', True),
        ('https://docs.google.com/spreadsheets/d/1abc/edit', True),  # Sem formato TSV
        ('', True),
    ])
    def test_validate_url(self, url, should_raise, mocker):
        """Testa a validação de URLs."""
        # Mock para urllib.request.urlopen
        mock_response = mocker.MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.headers.get.return_value = 'text/tab-separated-values'
        
        mock_urlopen = mocker.patch('urllib.request.urlopen', return_value=mock_response)
        
        if should_raise:
            with pytest.raises(ValueError):
                validate_url(url)
        else:
            # Não deve levantar exceção
            validate_url(url)