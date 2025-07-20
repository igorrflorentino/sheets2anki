"""
Testes de integração para a criação de decks a partir de dados TSV.
"""
import pytest
from src.parseRemoteDeck import build_remote_deck_from_tsv
from src.column_definitions import REQUIRED_COLUMNS

class TestDeckCreation:
    """Testes de integração para a criação de decks."""
    
    def test_build_deck_from_tsv(self, sample_tsv_data):
        """Testa a criação de um deck a partir de dados TSV."""
        remote_deck = build_remote_deck_from_tsv(sample_tsv_data)
        
        # Verificar se o deck foi criado corretamente
        assert remote_deck is not None
        
        # Verificar se as questões foram processadas corretamente
        # Apenas questões com SYNC? = true devem ser incluídas
        assert len(remote_deck.questions) == 2  # Duas questões com SYNC? = true
        
        # Verificar IDs das questões incluídas
        # As questões agora são dicionários com 'fields' e 'tags'
        question_ids = [q['fields']['ID'] for q in remote_deck.questions]
        assert '001' in question_ids
        assert '003' in question_ids
        assert '002' not in question_ids  # Esta tem SYNC? = false
    
    def test_column_validation(self):
        """Testa a validação de colunas obrigatórias."""
        # Teste com colunas incompletas
        incomplete_headers = REQUIRED_COLUMNS[:10]  # Apenas 10 primeiros
        incomplete_data = [
            incomplete_headers,
            ['001', 'Pergunta teste', 'Resposta teste', 'true'] + [''] * (len(incomplete_headers) - 4)
        ]
        
        # Deve lançar uma exceção quando faltam colunas obrigatórias
        with pytest.raises(Exception):
            build_remote_deck_from_tsv(incomplete_data)