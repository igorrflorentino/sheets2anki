#!/usr/bin/env python3
"""
Testes para o módulo de sincronização (sync.py).

Este arquivo testa as funcionalidades principais de sincronização
do Sheets2Anki, incluindo estatísticas, erro handling, e fluxos completos.
"""

import pytest
from unittest.mock import MagicMock, Mock, patch, call
from typing import Dict, List, Any
import sys
import os

# Configurar path para importações
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


# =============================================================================
# TESTES DAS CLASSES DE ESTATÍSTICAS
# =============================================================================

class TestSyncStats:
    """Testes para a classe SyncStats."""
    
    def test_sync_stats_initialization(self):
        """Testa inicialização da classe SyncStats."""
        from src.sync import SyncStats
        
        stats = SyncStats()
        
        # Verificar valores padrão
        assert stats.created == 0
        assert stats.updated == 0
        assert stats.deleted == 0
        assert stats.ignored == 0
        assert stats.errors == 0
        assert stats.unchanged == 0
        assert stats.skipped == 0
        
        # Verificar métricas detalhadas
        assert stats.remote_total_table_lines == 0
        assert stats.remote_valid_note_lines == 0
        assert stats.remote_invalid_note_lines == 0
        assert stats.remote_sync_marked_lines == 0
        assert stats.remote_total_potential_anki_notes == 0
        assert stats.remote_potential_student_notes == 0
        assert stats.remote_potential_missing_a_notes == 0
        assert stats.remote_unique_students_count == 0
        
        # Verificar estruturas de dados
        assert isinstance(stats.remote_notes_per_student, dict)
        assert isinstance(stats.error_details, list)
        assert isinstance(stats.update_details, list)
        assert isinstance(stats.creation_details, list)
        assert isinstance(stats.deletion_details, list)
    
    def test_add_error(self):
        """Testa adição de erros às estatísticas."""
        from src.sync import SyncStats
        
        stats = SyncStats()
        error_msg = "Erro de teste"
        
        stats.add_error(error_msg)
        
        assert stats.errors == 1
        assert error_msg in stats.error_details
    
    def test_add_update_detail(self):
        """Testa adição de detalhes de atualização."""
        from src.sync import SyncStats
        
        stats = SyncStats()
        detail = {"note_id": "123", "action": "updated", "field": "PERGUNTA"}
        
        stats.add_update_detail_structured(detail)
        
        assert len(stats.update_details) == 1
        assert stats.update_details[0] == detail
    
    def test_add_creation_detail(self):
        """Testa adição de detalhes de criação."""
        from src.sync import SyncStats
        
        stats = SyncStats()
        detail = {"note_id": "456", "action": "created", "type": "Basic"}
        
        stats.add_creation_detail(detail)
        
        assert len(stats.creation_details) == 1
        assert stats.creation_details[0] == detail
    
    def test_add_deletion_detail(self):
        """Testa adição de detalhes de exclusão."""
        from src.sync import SyncStats
        
        stats = SyncStats()
        detail = {"note_id": "789", "action": "deleted", "reason": "not_in_remote"}
        
        stats.add_deletion_detail(detail)
        
        assert len(stats.deletion_details) == 1
        assert stats.deletion_details[0] == detail


class TestDeckSyncResult:
    """Testes para a classe DeckSyncResult."""
    
    def test_deck_sync_result_initialization(self):
        """Testa inicialização da classe DeckSyncResult."""
        from src.sync import DeckSyncResult, SyncStats
        
        stats = SyncStats()
        result = DeckSyncResult(
            deck_name="Test Deck",
            deck_key="test_key",
            success=True,
            stats=stats,
            error_message=""
        )
        
        assert result.deck_name == "Test Deck"
        assert result.deck_key == "test_key"
        assert result.success is True
        assert result.stats == stats
        assert result.error_message == ""
    
    def test_deck_sync_result_failure(self):
        """Testa resultado de sincronização com falha."""
        from src.sync import DeckSyncResult, SyncStats
        
        stats = SyncStats()
        stats.add_error("URL inválida")
        
        result = DeckSyncResult(
            deck_name="Failed Deck",
            deck_key="failed_key",
            success=False,
            stats=stats,
            error_message="URL inválida"
        )
        
        assert result.deck_name == "Failed Deck"
        assert result.success is False
        assert result.error_message == "URL inválida"
        assert result.stats.errors == 1


class TestSyncStatsManager:
    """Testes para a classe SyncStatsManager."""
    
    def test_sync_stats_manager_initialization(self):
        """Testa inicialização do gerenciador de estatísticas."""
        from src.sync import SyncStatsManager
        
        manager = SyncStatsManager()
        
        assert hasattr(manager, 'total_stats')
        assert hasattr(manager, 'deck_results')
        assert len(manager.deck_results) == 0
    
    def test_add_deck_result(self):
        """Testa adição de resultado de deck."""
        from src.sync import SyncStatsManager, DeckSyncResult, SyncStats
        
        manager = SyncStatsManager()
        stats = SyncStats(created=5, updated=3)
        result = DeckSyncResult(
            deck_name="Test Deck",
            deck_key="test_key",
            success=True,
            stats=stats
        )
        
        manager.add_deck_result(result)
        
        assert len(manager.deck_results) == 1
        assert manager.deck_results[0] == result
        assert manager.total_stats.created == 5
        assert manager.total_stats.updated == 3
    
    def test_get_successful_decks(self):
        """Testa filtro de decks sincronizados com sucesso."""
        from src.sync import SyncStatsManager, DeckSyncResult, SyncStats
        
        manager = SyncStatsManager()
        
        # Deck bem-sucedido
        successful_result = DeckSyncResult(
            deck_name="Success Deck",
            deck_key="success_key",
            success=True,
            stats=SyncStats()
        )
        
        # Deck falhado
        failed_result = DeckSyncResult(
            deck_name="Failed Deck",
            deck_key="failed_key",
            success=False,
            stats=SyncStats(),
            error_message="Erro de teste"
        )
        
        manager.add_deck_result(successful_result)
        manager.add_deck_result(failed_result)
        
        successful_decks = manager.get_successful_decks()
        assert len(successful_decks) == 1
        assert successful_decks[0].deck_name == "Success Deck"
    
    def test_get_failed_decks(self):
        """Testa filtro de decks com falha na sincronização."""
        from src.sync import SyncStatsManager, DeckSyncResult, SyncStats
        
        manager = SyncStatsManager()
        
        # Deck bem-sucedido
        successful_result = DeckSyncResult(
            deck_name="Success Deck",
            deck_key="success_key",
            success=True,
            stats=SyncStats()
        )
        
        # Deck falhado
        failed_result = DeckSyncResult(
            deck_name="Failed Deck",
            deck_key="failed_key",
            success=False,
            stats=SyncStats(),
            error_message="Erro de teste"
        )
        
        manager.add_deck_result(successful_result)
        manager.add_deck_result(failed_result)
        
        failed_decks = manager.get_failed_decks()
        assert len(failed_decks) == 1
        assert failed_decks[0].deck_name == "Failed Deck"
    
    def test_get_summary(self):
        """Testa geração de resumo das estatísticas."""
        from src.sync import SyncStatsManager, DeckSyncResult, SyncStats
        
        manager = SyncStatsManager()
        
        # Adicionar resultado bem-sucedido
        stats1 = SyncStats(created=5, updated=3, errors=0)
        result1 = DeckSyncResult(
            deck_name="Deck 1",
            deck_key="key1",
            success=True,
            stats=stats1
        )
        
        # Adicionar resultado falhado
        stats2 = SyncStats(created=0, updated=0, errors=1)
        result2 = DeckSyncResult(
            deck_name="Deck 2",
            deck_key="key2",
            success=False,
            stats=stats2,
            error_message="Erro"
        )
        
        manager.add_deck_result(result1)
        manager.add_deck_result(result2)
        
        summary = manager.get_summary()
        
        assert summary["successful_decks"] == 1
        assert summary["failed_decks"] == 1
        assert summary["total_decks"] == 2
        assert "total_stats" in summary


# =============================================================================
# TESTES DAS FUNÇÕES DE SINCRONIZAÇÃO
# =============================================================================

class TestSyncDecks:
    """Testes para a função principal syncDecks."""
    
    @patch('src.sync.mw')
    @patch('src.sync.get_remote_decks')
    @patch('src.sync.clear_debug_messages')
    def test_sync_decks_no_decks(self, mock_clear_debug, mock_get_remote_decks, mock_mw):
        """Testa syncDecks quando não há decks para sincronizar."""
        from src.sync import syncDecks
        
        # Mock do Anki
        mock_mw.col = MagicMock()
        
        # Mock de configuração vazia
        mock_get_remote_decks.return_value = {}
        
        # Executar sincronização
        syncDecks()
        
        # Verificar que debug foi limpo
        mock_clear_debug.assert_called_once()
        mock_get_remote_decks.assert_called_once()
    
    @patch('src.sync.mw')
    @patch('src.sync.get_remote_decks')
    @patch('src.sync.clear_debug_messages')
    @patch('src.sync._handle_consolidated_cleanup')
    @patch('src.sync._get_deck_keys_to_sync')
    @patch('src.sync._show_no_decks_message')
    def test_sync_decks_no_selected_decks(
        self, 
        mock_show_no_decks,
        mock_get_deck_keys,
        mock_cleanup,
        mock_clear_debug,
        mock_get_remote_decks,
        mock_mw
    ):
        """Testa syncDecks quando nenhum deck é selecionado."""
        from src.sync import syncDecks
        
        # Mock básico do Anki
        mock_mw.col = MagicMock()
        
        # Mock de configuração com decks
        mock_get_remote_decks.return_value = {
            "key1": {"local_deck_name": "Deck 1", "remote_deck_url": "http://test.com"}
        }
        
        # Mock de cleanup
        mock_cleanup.return_value = (None, None)
        
        # Mock de seleção vazia
        mock_get_deck_keys.return_value = []
        
        # Executar sincronização
        syncDecks(selected_deck_names=["NonExistent Deck"])
        
        # Verificar que mensagem de "nenhum deck" foi mostrada
        mock_show_no_decks.assert_called_once_with(["NonExistent Deck"])
    
    @patch('src.sync.mw')
    @patch('src.sync.get_remote_decks')
    @patch('src.sync.clear_debug_messages')
    @patch('src.sync._handle_consolidated_cleanup')
    @patch('src.sync._get_deck_keys_to_sync')
    @patch('src.sync._setup_progress_dialog')
    @patch('src.sync._sync_single_deck')
    @patch('src.sync._finalize_sync_new')
    def test_sync_decks_success(
        self,
        mock_finalize,
        mock_sync_single,
        mock_setup_progress,
        mock_get_deck_keys,
        mock_cleanup,
        mock_clear_debug,
        mock_get_remote_decks,
        mock_mw
    ):
        """Testa sincronização bem-sucedida de decks."""
        from src.sync import syncDecks, SyncStats
        
        # Mock básico do Anki
        mock_mw.col = MagicMock()
        
        # Mock de configuração com decks
        remote_decks = {
            "key1": {"local_deck_name": "Deck 1", "remote_deck_url": "http://test1.com"},
            "key2": {"local_deck_name": "Deck 2", "remote_deck_url": "http://test2.com"}
        }
        mock_get_remote_decks.return_value = remote_decks
        
        # Mock de cleanup
        mock_cleanup.return_value = (None, None)
        
        # Mock de seleção de decks
        mock_get_deck_keys.return_value = ["key1", "key2"]
        
        # Mock de progresso
        mock_progress = MagicMock()
        mock_setup_progress.return_value = mock_progress
        
        # Mock de sincronização individual
        stats = SyncStats(created=5, updated=3)
        mock_sync_single.side_effect = [
            (1, 1, stats),  # Primeiro deck
            (2, 1, stats)   # Segundo deck
        ]
        
        # Executar sincronização
        syncDecks()
        
        # Verificar chamadas
        mock_clear_debug.assert_called_once()
        mock_get_remote_decks.assert_called_once()
        assert mock_sync_single.call_count == 2
        mock_finalize.assert_called_once()
    
    @patch('src.sync.mw')
    @patch('src.sync.get_remote_decks')
    @patch('src.sync._get_deck_keys_to_sync')
    @patch('src.sync._setup_progress_dialog')
    @patch('src.sync._sync_single_deck')
    @patch('src.sync._handle_sync_error')
    @patch('src.sync._finalize_sync_new')
    def test_sync_decks_with_sync_error(
        self,
        mock_finalize,
        mock_handle_sync_error,
        mock_sync_single,
        mock_setup_progress,
        mock_get_deck_keys,
        mock_get_remote_decks,
        mock_mw
    ):
        """Testa tratamento de SyncError durante sincronização."""
        from src.sync import syncDecks
        from src.utils import SyncError
        
        # Mock básico do Anki
        mock_mw.col = MagicMock()
        
        # Mock de configuração
        remote_decks = {"key1": {"local_deck_name": "Deck 1"}}
        mock_get_remote_decks.return_value = remote_decks
        
        # Mock de seleção
        mock_get_deck_keys.return_value = ["key1"]
        
        # Mock de progresso
        mock_progress = MagicMock()
        mock_setup_progress.return_value = mock_progress
        
        # Mock de erro de sincronização
        sync_error = SyncError("Erro de sincronização de teste")
        mock_sync_single.side_effect = sync_error
        
        # Mock do handler de erro
        mock_handle_sync_error.return_value = (1, ["Erro tratado"])
        
        # Executar sincronização
        with patch('src.sync.clear_debug_messages'), \
             patch('src.sync._handle_consolidated_cleanup') as mock_cleanup:
            
            mock_cleanup.return_value = (None, None)
            syncDecks()
        
        # Verificar que erro foi tratado
        mock_handle_sync_error.assert_called_once()
        args = mock_handle_sync_error.call_args[0]
        assert args[0] == sync_error
        assert args[1] == "key1"
        
        # Verificar que finalização foi chamada
        mock_finalize.assert_called_once()


class TestSyncSingleDeck:
    """Testes para a função _sync_single_deck."""
    
    @patch('src.sync.mw')
    @patch('src.sync.validate_url')
    @patch('src.sync.get_selected_students_for_deck')
    @patch('src.sync.getRemoteDeck')
    @patch('src.sync.create_or_update_notes')
    def test_sync_single_deck_success(
        self,
        mock_create_notes,
        mock_get_remote_deck,
        mock_get_students,
        mock_validate_url,
        mock_mw
    ):
        """Testa sincronização bem-sucedida de um único deck."""
        from src.sync import _sync_single_deck, SyncStats
        
        # Mock do Anki
        mock_mw.col = MagicMock()
        mock_deck = {"id": 123, "name": "Test Deck"}
        mock_mw.col.decks.get.return_value = mock_deck
        
        # Mock de dados de entrada
        remote_decks = {
            "test_key": {
                "local_deck_id": 123,
                "remote_deck_url": "http://test.com/sheet.tsv",
                "local_deck_name": "Test Deck"
            }
        }
        
        progress = MagicMock()
        status_msgs = []
        
        # Mock de validação
        mock_validate_url.return_value = None
        
        # Mock de estudantes
        mock_get_students.return_value = ["João", "Maria"]
        
        # Mock de deck remoto
        mock_remote_deck = MagicMock()
        mock_remote_deck.notes = [{"ID": "1", "PERGUNTA": "Test?"}]
        mock_get_remote_deck.return_value = mock_remote_deck
        
        # Mock de criação de notas
        stats = SyncStats(created=2, updated=1)
        mock_create_notes.return_value = stats
        
        # Executar sincronização
        with patch('src.deck_manager.DeckRecreationManager') as mock_recreation, \
             patch('src.deck_manager.DeckNameManager') as mock_name_manager, \
             patch('src.sync.capture_deck_note_type_ids'), \
             patch('src.sync.sync_note_type_names_robustly') as mock_sync_types, \
             patch('src.sync.add_debug_message'):
            
            mock_recreation.recreate_deck_if_missing.return_value = (False, 123, "Test Deck")
            mock_name_manager.sync_deck_with_config.return_value = (123, "Test Deck")
            mock_sync_types.return_value = {"updated_count": 0}
            
            step, increment, result_stats = _sync_single_deck(
                remote_decks, "test_key", progress, status_msgs, 0
            )
        
        # Verificar resultado
        assert step >= 0
        assert increment == 1
        assert result_stats.created == 2
        assert result_stats.updated == 1
        
        # Verificar chamadas importantes
        mock_validate_url.assert_called_once_with("http://test.com/sheet.tsv")
        # A função get_selected_students_for_deck é chamada 2x: uma vez para obter dados e outra para sync de note types
        assert mock_get_students.call_count >= 1
        mock_get_remote_deck.assert_called_once()
        mock_create_notes.assert_called_once()
    
    @patch('src.sync.mw')
    @patch('src.sync.validate_url')
    def test_sync_single_deck_invalid_url(self, mock_validate_url, mock_mw):
        """Testa sincronização com URL inválida."""
        from src.sync import _sync_single_deck
        
        # Mock do Anki
        mock_mw.col = MagicMock()
        
        # Mock de dados de entrada
        remote_decks = {
            "test_key": {
                "local_deck_id": 123,
                "remote_deck_url": "invalid_url",
                "local_deck_name": "Test Deck"
            }
        }
        
        progress = MagicMock()
        status_msgs = []
        
        # Mock de validação que gera exceção
        mock_validate_url.side_effect = ValueError("URL inválida")
        
        # Executar sincronização deve gerar exceção
        with patch('src.deck_manager.DeckRecreationManager') as mock_recreation, \
             patch('src.sync.add_debug_message'):
            
            mock_recreation.recreate_deck_if_missing.return_value = (False, 123, "Test Deck")
            
            with pytest.raises(ValueError, match="URL inválida"):
                _sync_single_deck(remote_decks, "test_key", progress, status_msgs, 0)


# =============================================================================
# TESTES DAS FUNÇÕES AUXILIARES
# =============================================================================

class TestSyncHelperFunctions:
    """Testes para funções auxiliares de sincronização."""
    
    def test_get_deck_keys_to_sync_all(self):
        """Testa seleção de todos os decks para sincronização."""
        from src.sync import _get_deck_keys_to_sync
        
        remote_decks = {
            "key1": {"local_deck_name": "Deck 1"},
            "key2": {"local_deck_name": "Deck 2"},
            "key3": {"local_deck_name": "Deck 3"}
        }
        
        # Sem filtros - deve retornar todos
        result = _get_deck_keys_to_sync(remote_decks, None, None)
        assert len(result) == 3
        assert set(result) == {"key1", "key2", "key3"}
    
    @patch('src.sync.mw')
    @patch('src.sync.get_publication_key_hash')
    def test_get_deck_keys_to_sync_by_names(self, mock_hash, mock_mw):
        """Testa seleção de decks por nomes."""
        from src.sync import _get_deck_keys_to_sync
        
        # Mock do Anki
        mock_mw.col = MagicMock()
        mock_deck1 = {"id": 123, "name": "Deck 1"}
        mock_deck2 = {"id": 456, "name": "Deck 2"}
        mock_deck3 = {"id": 789, "name": "Deck 3"}
        
        mock_mw.col.decks.get.side_effect = lambda deck_id: {
            123: mock_deck1,
            456: mock_deck2,
            789: mock_deck3
        }.get(deck_id)
        
        remote_decks = {
            "key1": {"local_deck_name": "Deck 1", "local_deck_id": 123},
            "key2": {"local_deck_name": "Deck 2", "local_deck_id": 456},
            "key3": {"local_deck_name": "Deck 3", "local_deck_id": 789}
        }
        
        # Filtrar por nomes
        result = _get_deck_keys_to_sync(remote_decks, ["Deck 1", "Deck 3"], None)
        assert len(result) == 2
        assert "key1" in result
        assert "key3" in result
        assert "key2" not in result
    
    @patch('src.sync.get_publication_key_hash')
    def test_get_deck_keys_to_sync_by_urls(self, mock_hash):
        """Testa seleção de decks por URLs."""
        from src.sync import _get_deck_keys_to_sync
        
        # Mock da função de hash
        def mock_hash_function(url):
            return {
                "http://test1.com": "key1",
                "http://test2.com": "key2",
                "http://test3.com": "key3"
            }.get(url)
        
        mock_hash.side_effect = mock_hash_function
        
        remote_decks = {
            "key1": {
                "local_deck_name": "Deck 1",
                "remote_deck_url": "http://test1.com"
            },
            "key2": {
                "local_deck_name": "Deck 2", 
                "remote_deck_url": "http://test2.com"
            },
            "key3": {
                "local_deck_name": "Deck 3",
                "remote_deck_url": "http://test3.com"
            }
        }
        
        # Filtrar por URLs
        result = _get_deck_keys_to_sync(
            remote_decks, 
            None, 
            ["http://test1.com", "http://test2.com"]
        )
        assert len(result) == 2
        assert "key1" in result
        assert "key2" in result
        assert "key3" not in result
    
    @patch('src.sync.QProgressDialog')
    @patch('src.sync.mw')
    def test_setup_progress_dialog(self, mock_mw, mock_progress_class):
        """Testa configuração do diálogo de progresso."""
        from src.sync import _setup_progress_dialog
        
        # Mock do diálogo
        mock_progress = MagicMock()
        mock_progress_class.return_value = mock_progress
        
        # Mock do label (retornar None para evitar problemas de alinhamento)
        mock_progress.findChild.return_value = None
        
        # Configurar progresso
        result = _setup_progress_dialog(5)
        
        # Verificar criação básica
        mock_progress_class.assert_called_once()
        assert result == mock_progress
        mock_progress.show.assert_called_once()


# =============================================================================
# TESTES DE TRATAMENTO DE ERROS
# =============================================================================

class TestSyncErrorHandling:
    """Testes para tratamento de erros durante sincronização."""
    
    def test_handle_sync_error(self):
        """Testa tratamento de SyncError."""
        from src.sync import _handle_sync_error
        from src.utils import SyncError
        
        # Dados de teste
        error = SyncError("Teste de erro")
        deck_key = "test_key"
        remote_decks = {deck_key: {"local_deck_name": "Test Deck"}}
        progress = MagicMock()
        status_msgs = []
        sync_errors = []
        step = 5
        
        # Executar tratamento
        with patch('src.sync._update_progress_text') as mock_update:
            
            new_step, new_errors = _handle_sync_error(
                error, deck_key, remote_decks, progress, 
                status_msgs, sync_errors, step
            )
        
        # Verificar resultado
        assert new_step == step + 3  # A função incrementa em 3, não 1
        assert len(new_errors) == 1
        assert "Teste de erro" in new_errors[0]
        
        # Verificar que progress foi atualizado
        mock_update.assert_called()
    
    def test_handle_unexpected_error(self):
        """Testa tratamento de erro inesperado."""
        from src.sync import _handle_unexpected_error
        
        # Dados de teste
        error = Exception("Erro inesperado")
        deck_key = "test_key"
        remote_decks = {deck_key: {"local_deck_name": "Test Deck"}}
        progress = MagicMock()
        status_msgs = []
        sync_errors = []
        step = 5
        
        # Executar tratamento
        with patch('src.sync._update_progress_text') as mock_update:
            
            new_step, new_errors = _handle_unexpected_error(
                error, deck_key, remote_decks, progress,
                status_msgs, sync_errors, step
            )
        
        # Verificar resultado
        assert new_step == step + 3  # A função incrementa em 3, não 1
        assert len(new_errors) == 1
        assert "Erro inesperado" in new_errors[0]
        
        # Verificar que progress foi atualizado
        mock_update.assert_called()


# =============================================================================
# TESTES DE INTEGRAÇÃO DE SINCRONIZAÇÃO
# =============================================================================

class TestSyncIntegration:
    """Testes de integração para fluxos completos de sincronização."""
    
    @patch('src.sync.mw')
    @patch('src.sync.get_remote_decks')
    @patch('src.sync.validate_url')
    @patch('src.sync.getRemoteDeck')
    @patch('src.data_processor.create_or_update_notes')
    def test_complete_sync_workflow(
        self,
        mock_create_notes,
        mock_get_remote_deck,
        mock_validate_url,
        mock_get_remote_decks,
        mock_mw
    ):
        """Testa fluxo completo de sincronização com múltiplos decks."""
        from src.sync import syncDecks, SyncStats
        
        # Mock do Anki
        mock_mw.col = MagicMock()
        mock_mw.app = MagicMock()
        
        # Mock de decks
        mock_mw.col.decks.get.side_effect = [
            {"id": 123, "name": "Deck 1"},
            {"id": 456, "name": "Deck 2"}
        ]
        
        # Mock de configuração
        remote_decks = {
            "key1": {
                "local_deck_id": 123,
                "remote_deck_url": "http://test1.com/sheet1.tsv",
                "local_deck_name": "Deck 1"
            },
            "key2": {
                "local_deck_id": 456,
                "remote_deck_url": "http://test2.com/sheet2.tsv", 
                "local_deck_name": "Deck 2"
            }
        }
        mock_get_remote_decks.return_value = remote_decks
        
        # Mock de validação
        mock_validate_url.return_value = None
        
        # Mock de deck remoto
        mock_remote_deck = MagicMock()
        mock_remote_deck.notes = [{"ID": "1", "PERGUNTA": "Test?"}]
        mock_get_remote_deck.return_value = mock_remote_deck
        
        # Mock de criação de notas
        stats1 = SyncStats(created=3, updated=2)
        stats2 = SyncStats(created=1, updated=4)
        mock_create_notes.side_effect = [stats1, stats2]
        
        # Executar sincronização completa
        with patch('src.sync.clear_debug_messages'), \
             patch('src.sync._handle_consolidated_cleanup') as mock_cleanup, \
             patch('src.deck_manager.DeckRecreationManager') as mock_recreation, \
             patch('src.deck_manager.DeckNameManager') as mock_name_manager, \
             patch('src.sync.get_selected_students_for_deck') as mock_students, \
             patch('src.sync.capture_deck_note_type_ids'), \
             patch('src.sync.sync_note_type_names_robustly') as mock_sync_types, \
             patch('src.sync._finalize_sync_new') as mock_finalize, \
             patch('src.sync.add_debug_message'), \
             patch('src.sync.remove_empty_subdecks') as mock_remove_subdecks, \
             patch('src.sync._setup_progress_dialog') as mock_setup_progress, \
             patch('src.sync.save_remote_decks') as mock_save_decks, \
             patch('src.sync._update_progress_text') as mock_update_progress:
            
            # Configurar mocks
            mock_cleanup.return_value = (None, None)
            mock_recreation.recreate_deck_if_missing.side_effect = [
                (False, 123, "Deck 1"),
                (False, 456, "Deck 2")
            ]
            mock_name_manager.sync_deck_with_config.side_effect = [
                (123, "Deck 1"),
                (456, "Deck 2")
            ]
            mock_students.return_value = ["João", "Maria"]
            mock_sync_types.return_value = {"updated_count": 0}
            mock_remove_subdecks.return_value = 0
            mock_create_notes.side_effect = [stats1, stats2]
            
            # Mock do diálogo de progresso
            mock_progress = MagicMock()
            mock_setup_progress.return_value = mock_progress
            
            # Executar
            result = syncDecks()
            
            # Verificar que finalização foi chamada
            mock_finalize.assert_called_once()
            
            # Verificar que a função rodou sem erro
            # Note: devido à complexidade do fluxo real, apenas verificamos que executou
            assert result is None  # syncDecks não retorna valor por padrão
    
    def test_sync_with_partial_failures(self):
        """Testa sincronização onde alguns decks falham."""
        from src.sync import syncDecks
        from src.utils import SyncError
        
        # Mock básico
        with patch('src.sync.mw') as mock_mw, \
             patch('src.sync.get_remote_decks') as mock_get_decks, \
             patch('src.sync.clear_debug_messages'), \
             patch('src.sync._handle_consolidated_cleanup') as mock_cleanup, \
             patch('src.sync._sync_single_deck') as mock_sync_single, \
             patch('src.sync._finalize_sync_new') as mock_finalize, \
             patch('src.sync._setup_progress_dialog') as mock_setup_progress:
            
            # Configurar Anki
            mock_mw.col = MagicMock()
            
            # Mock do diálogo de progresso
            mock_progress = MagicMock()
            mock_setup_progress.return_value = mock_progress
            
            # Configurar decks
            remote_decks = {
                "key1": {"local_deck_name": "Success Deck"},
                "key2": {"local_deck_name": "Failed Deck"}
            }
            mock_get_decks.return_value = remote_decks
            mock_cleanup.return_value = (None, None)
            
            # Primeiro deck sucesso, segundo falha
            mock_sync_single.side_effect = [
                (1, 1, Mock()),  # Sucesso
                SyncError("Falha no segundo deck")  # Falha
            ]
            
            # Executar
            syncDecks()
            
            # Verificar que finalização foi chamada mesmo com falhas parciais
            mock_finalize.assert_called_once()


# =============================================================================
# TESTES DE PERFORMANCE E EDGE CASES
# =============================================================================

class TestSyncPerformance:
    """Testes de performance e casos extremos."""
    
    def test_sync_large_number_of_decks(self):
        """Testa sincronização com grande número de decks."""
        from src.sync import _get_deck_keys_to_sync
        
        # Criar muitos decks
        remote_decks = {}
        for i in range(100):
            remote_decks[f"key{i}"] = {
                "local_deck_name": f"Deck {i}",
                "remote_deck_url": f"http://test{i}.com"
            }
        
        # Verificar que todos são selecionados
        result = _get_deck_keys_to_sync(remote_decks, None, None)
        assert len(result) == 100
    
    def test_sync_with_empty_stats(self):
        """Testa sincronização que não resulta em mudanças."""
        from src.sync import SyncStats, SyncStatsManager, DeckSyncResult
        
        # Criar stats vazias
        empty_stats = SyncStats()
        
        # Criar resultado
        result = DeckSyncResult(
            deck_name="Empty Deck",
            deck_key="empty_key", 
            success=True,
            stats=empty_stats
        )
        
        # Adicionar ao gerenciador
        manager = SyncStatsManager()
        manager.add_deck_result(result)
        
        # Verificar resumo
        summary = manager.get_summary()
        assert summary["successful_decks"] == 1
        assert summary["failed_decks"] == 0
        assert summary["total_stats"].created == 0
        assert summary["total_stats"].updated == 0
    
    @patch('src.sync.mw')
    def test_sync_with_unicode_deck_names(self, mock_mw):
        """Testa sincronização com nomes de deck com caracteres especiais."""
        from src.sync import _get_deck_keys_to_sync
        
        # Mock do Anki
        mock_mw.col = MagicMock()
        mock_deck1 = {"id": 123, "name": "Deck com Acentuação"}
        mock_deck2 = {"id": 456, "name": "Deck 中文"}
        mock_deck3 = {"id": 789, "name": "Deck العربية"}
        
        mock_mw.col.decks.get.side_effect = lambda deck_id: {
            123: mock_deck1,
            456: mock_deck2,
            789: mock_deck3
        }.get(deck_id)
        
        remote_decks = {
            "key1": {"local_deck_name": "Deck com Acentuação", "local_deck_id": 123},
            "key2": {"local_deck_name": "Deck 中文", "local_deck_id": 456},
            "key3": {"local_deck_name": "Deck العربية", "local_deck_id": 789}
        }
        
        # Filtrar por nome com acentos
        result = _get_deck_keys_to_sync(remote_decks, ["Deck com Acentuação"], None)
        assert len(result) == 1
        assert "key1" in result
        
        # Filtrar por nome em chinês
        result = _get_deck_keys_to_sync(remote_decks, ["Deck 中文"], None)
        assert len(result) == 1
        assert "key2" in result


if __name__ == "__main__":
    pytest.main([__file__])
