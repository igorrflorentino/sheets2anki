"""
Testes para a funcionalidade de sincronização seletiva com a coluna SYNC?.
"""
import pytest
from src.column_definitions import should_sync_question, SYNC, REQUIRED_COLUMNS

class TestSyncSelective:
    """Testes para a funcionalidade de sincronização seletiva."""
    
    @pytest.mark.parametrize("value,expected", [
        ('true', True),
        ('1', True),
        ('sim', True),
        ('yes', True),
        ('verdadeiro', True),
        ('v', True),
        ('TRUE', True),  # Case insensitive
        ('SIM', True),   # Case insensitive
        ('', True),      # Valor vazio deve sincronizar (compatibilidade)
        ('valor_nao_reconhecido', True)  # Valor não reconhecido sincroniza
    ])
    def test_should_sync_positive(self, value, expected):
        """Testa valores que devem resultar em sincronização."""
        fields = {SYNC: value}
        result = should_sync_question(fields)
        assert result == expected
    
    @pytest.mark.parametrize("value,expected", [
        ('false', False),
        ('0', False),
        ('não', False),
        ('nao', False),
        ('no', False),
        ('falso', False),
        ('f', False),
        ('FALSE', False),  # Case insensitive
        ('NÃO', False),    # Case insensitive
    ])
    def test_should_sync_negative(self, value, expected):
        """Testa valores que devem resultar em não sincronização."""
        fields = {SYNC: value}
        result = should_sync_question(fields)
        assert result == expected
    
    def test_sync_in_required_columns(self):
        """Verifica se SYNC? está nas colunas obrigatórias."""
        assert SYNC in REQUIRED_COLUMNS