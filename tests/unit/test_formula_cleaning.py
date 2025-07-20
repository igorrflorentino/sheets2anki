"""
Testes para a funcionalidade de limpeza automática de fórmulas.
"""
import pytest
from src.parseRemoteDeck import clean_formula_errors

class TestFormulaCleaning:
    """Testes para a funcionalidade de limpeza de fórmulas."""
    
    @pytest.mark.parametrize("input_val,expected", [
        ('#NAME?', ''),
        ('#REF!', ''),
        ('#VALUE!', ''),
        ('#DIV/0!', ''),
        ('#N/A', ''),
        ('#NULL!', ''),
        ('#NUM!', ''),
        ('Texto com #REF! no meio', 'Texto com  no meio'),
        ('Múltiplos #REF! #NAME? erros', 'Múltiplos   erros'),
    ])
    def test_clean_formula_errors(self, input_val, expected):
        """Testa a limpeza de erros de fórmula."""
        result = clean_formula_errors(input_val)
        assert result == expected
    
    @pytest.mark.parametrize("input_val,expected", [
        ('=SUM(A1:A10)', ''),
        ('=VLOOKUP(A1, B1:C10, 2, FALSE)', ''),
        ('=IF(A1>10, "Alto", "Baixo")', ''),
        ('Texto com =SUM(A1) no meio', 'Texto com  no meio'),
        ('Múltiplas =SUM(A1) =AVG(B1:B10) fórmulas', 'Múltiplas   fórmulas'),
    ])
    def test_clean_formula_expressions(self, input_val, expected):
        """Testa a limpeza de expressões de fórmula."""
        result = clean_formula_errors(input_val)
        assert result == expected
    
    @pytest.mark.parametrize("input_val,expected", [
        ('Texto normal', 'Texto normal'),
        ('123', '123'),
        ('', ''),
        ('Texto com = sinal', 'Texto com = sinal'),
        ('Texto com # hashtag', 'Texto com # hashtag'),
    ])
    def test_preserve_normal_text(self, input_val, expected):
        """Testa que texto normal é preservado."""
        result = clean_formula_errors(input_val)
        assert result == expected