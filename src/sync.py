"""
Funções de sincronização principal para o addon Sheets2Anki.

Este módulo contém as funções centrais para sincronização
de decks com fontes remotas, usando o novo sistema de configuração.
Inclui também classes para gerenciamento de estatísticas e finalização.
"""

import time
import traceback
from typing import Optional, Dict, List, Any, Tuple, Union, cast
from dataclasses import dataclass, field
from .compat import (
    mw, showInfo, QProgressDialog, QPushButton, QLabel, QDialog, QVBoxLayout,
    QTextEdit, QDialogButtonBox, AlignTop, AlignLeft, ButtonBox_Ok, safe_exec_dialog,
    QSpinBox, QHBoxLayout, QFrame, QTabWidget, QWidget, QFont, QSizePolicy,
    QMessageBox, MessageBox_Yes, MessageBox_No
)
from .config_manager import get_remote_decks, save_remote_decks, disconnect_deck, verify_and_update_deck_info
from .utils import remove_empty_subdecks
from .utils import validate_url
from .data_processor import getRemoteDeck
from .data_processor import create_or_update_notes
from .utils import SyncError
from .utils import add_debug_message, get_debug_messages, clear_debug_messages

# ========================================================================================
# CLASSES DE ESTATÍSTICAS DE SINCRONIZAÇÃO (consolidado de sync_stats.py)
# ========================================================================================

@dataclass
class SyncStats:
    """Estatísticas de uma sincronização."""
    created: int = 0
    updated: int = 0
    deleted: int = 0
    ignored: int = 0
    errors: int = 0
    error_details: List[str] = field(default_factory=list)
    updated_details: List[str] = field(default_factory=list)
    
    def add_error(self, error_msg: str) -> None:
        """Adiciona um erro às estatísticas."""
        self.errors += 1
        self.error_details.append(error_msg)
    
    def add_update_detail(self, detail: str) -> None:
        """Adiciona um detalhe de atualização."""
        self.updated_details.append(detail)
    
    def merge(self, other: 'SyncStats') -> None:
        """Merge com outras estatísticas."""
        self.created += other.created
        self.updated += other.updated
        self.deleted += other.deleted
        self.ignored += other.ignored
        self.errors += other.errors
        self.error_details.extend(other.error_details)
        self.updated_details.extend(other.updated_details)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário (compatibilidade com código antigo)."""
        return {
            'created': self.created,
            'updated': self.updated,
            'deleted': self.deleted,
            'ignored': self.ignored,
            'errors': self.errors,
            'error_details': self.error_details,
            'updated_details': self.updated_details
        }
    
    def get_total_operations(self) -> int:
        """Retorna o total de operações realizadas."""
        return self.created + self.updated + self.deleted + self.ignored
    
    def has_changes(self) -> bool:
        """Verifica se houve mudanças."""
        return self.created > 0 or self.updated > 0 or self.deleted > 0
    
    def has_errors(self) -> bool:
        """Verifica se houve erros."""
        return self.errors > 0

@dataclass 
class DeckSyncResult:
    """Resultado da sincronização de um deck específico."""
    deck_name: str
    deck_key: str
    success: bool
    stats: SyncStats
    error_message: Optional[str] = None
    
    def __post_init__(self):
        """Inicialização após criação."""
        if self.stats is None:
            self.stats = SyncStats()

class SyncStatsManager:
    """Gerenciador de estatísticas de sincronização."""
    
    def __init__(self):
        self.total_stats = SyncStats()
        self.deck_results: List[DeckSyncResult] = []
    
    def add_deck_result(self, result: DeckSyncResult) -> None:
        """Adiciona resultado de sincronização de um deck."""
        self.deck_results.append(result)
        self.total_stats.merge(result.stats)
    
    def create_deck_result(self, deck_name: str, deck_key: str) -> DeckSyncResult:
        """Cria um novo resultado de deck."""
        return DeckSyncResult(
            deck_name=deck_name,
            deck_key=deck_key,
            success=False,
            stats=SyncStats()
        )
    
    def get_successful_decks(self) -> List[DeckSyncResult]:
        """Retorna decks sincronizados com sucesso."""
        return [r for r in self.deck_results if r.success]
    
    def get_failed_decks(self) -> List[DeckSyncResult]:
        """Retorna decks que falharam na sincronização."""
        return [r for r in self.deck_results if not r.success]
    
    def get_summary(self) -> Dict[str, Any]:
        """Retorna um resumo das estatísticas."""
        successful = len(self.get_successful_decks())
        failed = len(self.get_failed_decks())
        
        return {
            'total_decks': len(self.deck_results),
            'successful_decks': successful,
            'failed_decks': failed,
            'total_stats': self.total_stats.to_dict(),
            'has_changes': self.total_stats.has_changes(),
            'has_errors': self.total_stats.has_errors()
        }
    
    def reset(self) -> None:
        """Reseta todas as estatísticas."""
        self.total_stats = SyncStats()
        self.deck_results.clear()

# ========================================================================================
# FUNÇÕES DE FINALIZAÇÃO DE SINCRONIZAÇÃO (consolidado de sync_finalization.py)
# ========================================================================================

def _finalize_sync_new(progress, total_decks, successful_decks, total_stats, sync_errors, cleanup_result=None, missing_cleanup_result=None):
    """
    Finaliza o processo de sincronização usando o novo sistema de estatísticas.
    
    Args:
        progress: QProgressDialog instance
        total_decks: Total de decks para sync
        successful_decks: Número de decks sincronizados com sucesso
        total_stats: Estatísticas totais da sincronização
        sync_errors: Lista de erros de sincronização
        cleanup_result: Resultado da limpeza (opcional) 
        missing_cleanup_result: Resultado da limpeza de decks ausentes (opcional)
        
    Returns:
        Resultado consolidado da sincronização
    """
    
    progress.setLabelText("Limpando subdecks vazios...")
    from .config_manager import get_remote_decks
    
    # Remover subdecks vazios
    remote_decks = get_remote_decks()
    removed_subdecks = remove_empty_subdecks(remote_decks)
    
    # Preparar mensagem final para exibir na barra de progresso
    cleanup_info = ""
    if cleanup_result:
        cleanup_info = f", {cleanup_result['disabled_students_count']} alunos removidos"
    
    if missing_cleanup_result:
        if cleanup_info:
            cleanup_info += f", dados [MISSING A.] removidos"
        else:
            cleanup_info = f", dados [MISSING A.] removidos"
    
    # Gerar mensagem final baseada nas estatísticas
    if sync_errors or total_stats.get('errors', 0) > 0:
        final_msg = f"Concluído com problemas: {successful_decks}/{total_decks} decks sincronizados"
        if total_stats.get('created', 0) > 0:
            final_msg += f", {total_stats['created']} notas criadas"
        if total_stats.get('updated', 0) > 0:
            final_msg += f", {total_stats['updated']} atualizadas"
        if total_stats.get('deleted', 0) > 0:
            final_msg += f", {total_stats['deleted']} deletadas"
        if total_stats.get('ignored', 0) > 0:
            final_msg += f", {total_stats['ignored']} ignoradas"
        if removed_subdecks > 0:
            final_msg += f", {removed_subdecks} subdecks vazios removidos"
        if cleanup_info:
            final_msg += cleanup_info
        final_msg += f", {total_stats.get('errors', 0) + len(sync_errors)} erros"
    else:
        final_msg = f"Sincronização concluída com sucesso!"
        if total_stats.get('created', 0) > 0:
            final_msg += f" {total_stats['created']} notas criadas"
        if total_stats.get('updated', 0) > 0:
            final_msg += f", {total_stats['updated']} atualizadas"
        if total_stats.get('deleted', 0) > 0:
            final_msg += f", {total_stats['deleted']} deletadas"
        if total_stats.get('ignored', 0) > 0:
            final_msg += f", {total_stats['ignored']} ignoradas"
        if removed_subdecks > 0:
            final_msg += f", {removed_subdecks} subdecks vazios removidos"
        if cleanup_info:
            final_msg += cleanup_info
    
    # Adicionar mensagem final de debug
    add_debug_message("🎬 Sincronização finalizada", "SYSTEM")
    
    # Atualizar a interface do Anki para mostrar as mudanças
    ensure_interface_refresh()
    
    # Atualizar progresso final
    progress.setValue(total_decks)
    progress.setLabelText(final_msg)
    
    # Aguardar um momento para mostrar a mensagem final
    import time
    time.sleep(1)
    
    # Mostrar resumo detalhado
    _show_sync_summary_new(sync_errors, total_stats, successful_decks, total_decks, removed_subdecks, cleanup_result, missing_cleanup_result)

def _show_sync_summary_new(sync_errors, total_stats, decks_synced, total_decks, removed_subdecks=0, cleanup_result=None, missing_cleanup_result=None):
    """
    Mostra resumo da sincronização usando o novo sistema.
    """
    from .compat import showInfo
    from .utils import get_debug_messages, is_debug_enabled
    
    summary = []
    
    # Estatísticas principais
    if sync_errors or total_stats.get('errors', 0) > 0:
        summary.append("❌ Sincronização concluída com problemas!")
        summary.append(f"📊 Decks: {decks_synced}/{total_decks} sincronizados com sucesso")
    else:
        summary.append("✅ Sincronização concluída com sucesso!")
        summary.append(f"📊 Decks: {decks_synced}/{total_decks} sincronizados")
    
    # Estatísticas de notas
    if total_stats.get('created', 0) > 0:
        summary.append(f"➕ {total_stats['created']} notas criadas")
    if total_stats.get('updated', 0) > 0:
        summary.append(f"✏️ {total_stats['updated']} notas atualizadas")
    if total_stats.get('deleted', 0) > 0:
        summary.append(f"🗑️ {total_stats['deleted']} notas deletadas")
    if total_stats.get('ignored', 0) > 0:
        summary.append(f"⏭️ {total_stats['ignored']} notas ignoradas")
    
    # Limpezas
    if removed_subdecks > 0:
        summary.append(f"🧹 {removed_subdecks} subdecks vazios removidos")
    
    if cleanup_result and cleanup_result.get('disabled_students_count', 0) > 0:
        summary.append(f"🧹 {cleanup_result['disabled_students_count']} alunos desabilitados removidos")
    
    if missing_cleanup_result:
        summary.append("🧹 Dados [MISSING A.] removidos")
    
    # Erros
    total_errors = total_stats.get('errors', 0) + len(sync_errors)
    if total_errors > 0:
        summary.append(f"⚠️ {total_errors} erros encontrados")
        
        # Mostrar detalhes dos erros se debug estiver habilitado
        if is_debug_enabled() and (sync_errors or total_stats.get('error_details')):
            summary.append("\nDetalhes dos erros:")
            for error in sync_errors:
                summary.append(f"  • {error}")
            for error in total_stats.get('error_details', []):
                summary.append(f"  • {error}")
    
    # Informações de debug se habilitado
    if is_debug_enabled():
        debug_messages = get_debug_messages()
        summary.append(f"\n🐛 Debug: {len(debug_messages)} mensagens capturadas")
        summary.append("(Verificar console para detalhes)")
    
    showInfo("\n".join(summary))

# ========================================================================================
# FUNÇÕES DE ATUALIZAÇÃO DA INTERFACE (consolidado de interface_updater.py) 
# ========================================================================================

def refresh_anki_interface():
    """
    Atualiza a interface do Anki após a sincronização.
    
    Atualiza:
    - Lista de decks na tela principal
    - Contador de cards
    - Interface do reviewer se estiver ativo
    - Browser se estiver aberto
    """
    if not mw:
        add_debug_message("❌ MainWindow não disponível para atualização", "INTERFACE_UPDATE")
        return
    
    try:
        add_debug_message("🔄 Iniciando atualização da interface do Anki", "INTERFACE_UPDATE")
        
        # 1. Atualizar a lista de decks na tela principal
        if hasattr(mw, 'deckBrowser') and mw.deckBrowser:
            add_debug_message("📂 Atualizando lista de decks", "INTERFACE_UPDATE")
            mw.deckBrowser.refresh()
        
        # 2. Atualizar o reviewer se estiver ativo
        if hasattr(mw, 'reviewer') and mw.reviewer and mw.state == "review":
            add_debug_message("📝 Atualizando reviewer", "INTERFACE_UPDATE")
            # Forçar recalculo do número de cards
            if hasattr(mw.reviewer, '_updateCounts'):
                mw.reviewer._updateCounts()
        
        # 3. Atualizar o browser se estiver aberto
        if hasattr(mw, 'browser') and mw.browser:
            add_debug_message("🔍 Atualizando browser", "INTERFACE_UPDATE")
            mw.browser.model.reset()
            mw.browser.form.tableView.selectRow(0)
        
        # 4. Atualizar a barra de título e interface geral
        if hasattr(mw, 'setWindowTitle') and mw.col:
            # Manter o título original mas forçar recalculo interno
            mw.col.reset()
        
        # 5. Trigger geral de reset da interface
        if hasattr(mw, 'reset'):
            add_debug_message("🔄 Executando reset geral da interface", "INTERFACE_UPDATE")
            mw.reset()
        
        add_debug_message("✅ Interface do Anki atualizada com sucesso", "INTERFACE_UPDATE")
        
    except Exception as e:
        add_debug_message(f"❌ Erro ao atualizar interface: {e}", "INTERFACE_UPDATE")

def refresh_deck_list():
    """
    Atualiza especificamente a lista de decks na tela principal.
    """
    if not mw or not hasattr(mw, 'deckBrowser'):
        return
    
    try:
        add_debug_message("📂 Atualizando lista de decks", "INTERFACE_UPDATE")
        mw.deckBrowser.refresh()
    except Exception as e:
        add_debug_message(f"❌ Erro ao atualizar lista de decks: {e}", "INTERFACE_UPDATE")

def refresh_counts():
    """
    Atualiza os contadores de cards em todas as interfaces.
    """
    if not mw:
        return
        
    try:
        add_debug_message("🔢 Atualizando contadores de cards", "INTERFACE_UPDATE")
        
        # Forçar recálculo dos counts na collection
        if mw.col:
            mw.col.sched.reset()
        
        # Atualizar deck browser
        if hasattr(mw, 'deckBrowser') and mw.deckBrowser:
            mw.deckBrowser.refresh()
            
        # Atualizar reviewer se ativo
        if hasattr(mw, 'reviewer') and mw.reviewer and mw.state == "review":
            if hasattr(mw.reviewer, '_updateCounts'):
                mw.reviewer._updateCounts()
                
    except Exception as e:
        add_debug_message(f"❌ Erro ao atualizar contadores: {e}", "INTERFACE_UPDATE")

def ensure_interface_refresh():
    """
    Garante que a interface seja atualizada, usando múltiplas estratégias.
    
    Esta função usa diferentes métodos para garantir que a interface
    seja atualizada independente do estado atual do Anki.
    """
    if not mw:
        return
        
    try:
        add_debug_message("🎯 Executando atualização completa da interface", "INTERFACE_UPDATE")
        
        # Método 1: Reset da collection (mais completo)
        if mw.col:
            mw.col.reset()
        
        # Método 2: Reset da interface principal
        if hasattr(mw, 'reset'):
            mw.reset()
        
        # Método 3: Atualização específica dos componentes
        refresh_deck_list()
        refresh_counts()
        
        add_debug_message("✅ Atualização completa da interface concluída", "INTERFACE_UPDATE")
        
    except Exception as e:
        add_debug_message(f"❌ Erro na atualização completa: {e}", "INTERFACE_UPDATE")

# ========================================================================================
# FUNÇÕES PRINCIPAIS DE SINCRONIZAÇÃO
# ========================================================================================

def _is_anki_ready():
    """Verifica se o Anki está pronto para operações."""
    return mw and hasattr(mw, 'col') and mw.col

def _is_anki_decks_ready():
    """Verifica se o Anki está pronto para operações com decks."""
    return _is_anki_ready() and hasattr(mw.col, 'decks')

def syncDecks(selected_deck_names=None, selected_deck_urls=None):
    """
    Sincroniza todos os decks remotos com suas fontes.
    
    Esta é a função principal de sincronização que:
    1. Verifica se há alunos desabilitados que precisam ter dados removidos
    2. Baixa dados dos decks remotos
    3. Processa e valida os dados
    4. Atualiza o banco de dados do Anki
    5. Mostra progresso ao usuário
    6. Atualiza nomes automaticamente se configurado
    
    Args:
        selected_deck_names: Lista de nomes de decks para sincronizar. 
                           Se None, sincroniza todos os decks.
        selected_deck_urls: Lista de URLs de decks para sincronizar.
                          Se fornecida, tem precedência sobre selected_deck_names.
    """
    # Verificar se mw.col está disponível
    if not _is_anki_ready():
        showInfo("Anki não está pronto. Tente novamente em alguns instantes.")
        return
        
    col = mw.col
    remote_decks = get_remote_decks()
    
    # Limpar mensagens de debug anteriores
    clear_debug_messages()
    
    # **NOVO**: Gerenciar limpezas de forma consolidada para evitar múltiplas confirmações
    missing_cleanup_result, cleanup_result = _handle_consolidated_cleanup(remote_decks)

    # Inicializar sistema de estatísticas
    stats_manager = SyncStatsManager()
    sync_errors = []
    status_msgs = []
    
    # Determinar quais decks sincronizar
    deck_keys = _get_deck_keys_to_sync(remote_decks, selected_deck_names, selected_deck_urls)
    total_decks = len(deck_keys)
    
    # Verificar se há decks para sincronizar
    if total_decks == 0:
        _show_no_decks_message(selected_deck_names)
        return
    
    # Configurar e mostrar barra de progresso
    progress = _setup_progress_dialog(total_decks)
    
    # Adicionar mensagem de debug inicial
    add_debug_message(f"🎬 SISTEMA DE DEBUG ATIVADO - Total de decks: {total_decks}", "SYNC")
    _update_progress_text(progress, status_msgs)
    
    step = 0
    try:
        # Sincronizar cada deck
        for deckKey in deck_keys:
            try:
                step, deck_sync_increment, current_stats = _sync_single_deck(
                    remote_decks, deckKey, progress, status_msgs, step
                )
                
                # Criar resultado do deck
                deck_name = remote_decks[deckKey].get("local_deck_name", "Unknown")
                deck_result = DeckSyncResult(
                    deck_name=deck_name,
                    deck_key=deckKey,
                    success=True,
                    stats=current_stats
                )
                stats_manager.add_deck_result(deck_result)
                
                add_debug_message(f"✅ Deck concluído: {deckKey}", "SYNC")

            except SyncError as e:
                step, sync_errors = _handle_sync_error(
                    e, deckKey, remote_decks, progress, status_msgs, sync_errors, step
                )
                
                # Adicionar resultado de falha
                deck_name = remote_decks[deckKey].get("local_deck_name", "Unknown")
                failed_result = DeckSyncResult(
                    deck_name=deck_name,
                    deck_key=deckKey,
                    success=False,
                    stats=SyncStats(),
                    error_message=str(e)
                )
                failed_result.stats.add_error(str(e))
                stats_manager.add_deck_result(failed_result)
                continue
                
            except Exception as e:
                step, sync_errors = _handle_unexpected_error(
                    e, deckKey, remote_decks, progress, status_msgs, sync_errors, step
                )
                
                # Adicionar resultado de erro inesperado
                deck_name = remote_decks[deckKey].get("local_deck_name", "Unknown")
                failed_result = DeckSyncResult(
                    deck_name=deck_name,
                    deck_key=deckKey,
                    success=False,
                    stats=SyncStats(),
                    error_message=f"Erro inesperado: {str(e)}"
                )
                failed_result.stats.add_error(f"Erro inesperado: {str(e)}")
                stats_manager.add_deck_result(failed_result)
                continue
        
        # Não precisamos salvar remote_decks aqui porque add_note_type_id_to_deck já salva individualmente
        # e essa chamada sobrescreveria os note_type_ids que foram adicionados
        
        # Mas precisamos salvar as atualizações de local_deck_name que foram feitas durante a sincronização
        from .config_manager import save_meta, get_meta
        try:
            current_meta = get_meta()
            save_meta(current_meta)
        except Exception as e:
            print(f"[WARNING] Erro ao salvar configurações após sincronização: {e}")
        
        # Obter resumo das estatísticas
        summary = stats_manager.get_summary()
        successful_decks = len(stats_manager.get_successful_decks())
        
        # Finalizar progresso e mostrar resultados
        _finalize_sync_new(progress, total_decks, successful_decks, summary['total_stats'], sync_errors, cleanup_result, missing_cleanup_result)
    
    finally:
        # Garantir que o dialog de progresso seja fechado
        if progress.isVisible():
            progress.close()

def _get_deck_keys_to_sync(remote_decks, selected_deck_names, selected_deck_urls=None):
    """
    Determina quais chaves de deck devem ser sincronizadas.
    Agora trabalha com hash keys da nova estrutura.
    
    Args:
        remote_decks: Dicionário de decks remotos (hash_key -> deck_info)
        selected_deck_names: Nomes dos decks selecionados ou None
        selected_deck_urls: URLs dos decks selecionados ou None
        
    Returns:
        list: Lista de hash keys a serem sincronizadas
    """
    from .utils import get_publication_key_hash
    
    # Se URLs específicas foram fornecidas, converter para hash keys
    if selected_deck_urls is not None:
        filtered_keys = []
        for url in selected_deck_urls:
            # Gerar hash da chave de publicação
            url_hash = get_publication_key_hash(url)
            
            if url_hash in remote_decks:
                filtered_keys.append(url_hash)
        return filtered_keys
    
    # Verificar se mw.col e mw.col.decks estão disponíveis
    if not _is_anki_decks_ready():
        return []
    
    assert mw.col is not None  # Type hint para o checker
        
    # Criar mapeamento de nomes para hash keys
    name_to_key = {}
    for hash_key, deck_info in remote_decks.items():
        # Verificar se o deck ainda existe
        local_deck_id = deck_info.get("local_deck_id")
        deck = mw.col.decks.get(local_deck_id) if local_deck_id is not None else None
        
        if deck:
            # Usar nome atual do deck
            actual_deck_name = deck["name"]
            name_to_key[actual_deck_name] = hash_key
            
            # Também mapear nome da configuração se diferente
            config_deck_name = deck_info.get("local_deck_name")
            if config_deck_name and config_deck_name != actual_deck_name:
                name_to_key[config_deck_name] = hash_key
    
    # Se nomes específicos foram selecionados, filtrar por eles
    if selected_deck_names is not None:
        filtered_keys = []
        for deck_name in selected_deck_names:
            if deck_name in name_to_key:
                filtered_keys.append(name_to_key[deck_name])
        return filtered_keys
    
    # Caso contrário, retornar todas as hash keys
    return list(remote_decks.keys())

def _build_name_to_key_mapping(config):
    """
    Constrói mapeamento de nomes de deck para hash keys de configuração.
    
    Args:
        config: Configuração do addon
        
    Returns:
        dict: Mapeamento de nomes para hash keys
    """
    # Verificar se mw.col e mw.col.decks estão disponíveis
    if not _is_anki_decks_ready():
        return {}
    
    assert mw.col is not None  # Type hint para o checker
        
    name_to_key = {}
    for hash_key, deck_info in get_remote_decks().items():
        # Obter o nome real do deck no Anki, não o nome salvo na config
        local_deck_id = deck_info.get("local_deck_id")
        if local_deck_id:
            deck = mw.col.decks.get(local_deck_id) if local_deck_id is not None else None
            if deck:
                actual_deck_name = deck["name"]
                name_to_key[actual_deck_name] = hash_key
            else:
                # Usar o nome salvo na config se o deck não existir
                config_deck_name = deck_info.get("local_deck_name")
                if config_deck_name:
                    name_to_key[config_deck_name] = hash_key
    
    return name_to_key

def _show_no_decks_message(selected_deck_names):
    """Mostra mensagem quando não há decks para sincronizar."""
    if selected_deck_names is not None:
        showInfo(f"Nenhum dos decks selecionados foi encontrado na configuração.\n\nDecks selecionados: {', '.join(selected_deck_names)}")
    else:
        showInfo("Nenhum deck remoto configurado para sincronização.")

def _setup_progress_dialog(total_decks):
    """
    Configura e retorna o dialog de progresso com tamanho ampliado.
    
    Esta função configura uma barra de progresso com:
    - Largura ampliada para 600px para acomodar debug messages
    - Altura ampliada para 450px para mostrar mais conteúdo
    - Quebra automática de linha para textos longos
    - Alinhamento adequado do texto
    
    Args:
        total_decks: Número total de decks para calcular o máximo da barra
        
    Returns:
        QProgressDialog: Dialog de progresso configurado
    """
    progress = QProgressDialog("Sincronizando decks...", "", 0, total_decks * 3, mw)
    progress.setWindowTitle("Sincronização de Decks")
    progress.setMinimumDuration(0)
    progress.setValue(0)
    progress.setCancelButton(None)
    progress.setAutoClose(False)  # Não fechar automaticamente
    progress.setAutoReset(False)  # Não resetar automaticamente
    
    # Configurar tamanho normal (interface limpa sem debug messages)
    progress.setFixedWidth(500)  # Largura normal de 500 pixels
    progress.setFixedHeight(200)  # Altura reduzida para 200 pixels
    
    # Configurar o label para quebrar linha automaticamente
    label = progress.findChild(QLabel)
    if label:
        label.setWordWrap(True)  # Permitir quebra de linha
        label.setAlignment(AlignTop | AlignLeft)  # Alinhar ao topo e à esquerda
        label.setMinimumSize(480, 180)  # Tamanho ajustado para interface limpa
    
    progress.show()
    mw.app.processEvents()  # Força a exibição da barra
    return progress

def _update_progress_text(progress, status_msgs, max_lines=3, debug_messages=None, show_debug=False):
    """
    Atualiza o texto da barra de progresso com formatação adequada.
    
    Args:
        progress: QProgressDialog instance
        status_msgs: Lista de mensagens de status
        max_lines: Número máximo de linhas a mostrar para status
        debug_messages: Lista de mensagens de debug (apenas armazenadas, não exibidas por padrão)
        show_debug: Se True, mostra as mensagens de debug na interface (padrão: False)
    """
    all_text_lines = []
    
    # Adicionar mensagens de status recentes
    recent_msgs = status_msgs[-max_lines:] if len(status_msgs) > max_lines else status_msgs
    if recent_msgs:
        all_text_lines.extend(recent_msgs)
    
    # Adicionar mensagens de debug se fornecidas E se solicitado
    if debug_messages and show_debug:
        all_text_lines.append("")  # Linha em branco para separar
        all_text_lines.append("=== DEBUG MESSAGES ===")
        
        # Mostrar as últimas mensagens de debug (máximo 15 para janela ampliada)
        recent_debug = debug_messages[-15:] if len(debug_messages) > 15 else debug_messages
        all_text_lines.extend(recent_debug)
        
        if len(debug_messages) > 15:
            all_text_lines.append(f"... e mais {len(debug_messages) - 15} mensagens de debug")
    
    # Juntar todas as linhas
    text = "\n".join(all_text_lines)
    
    # Limitar o comprimento de cada linha para evitar texto muito longo
    lines = text.split('\n')
    formatted_lines = []
    
    for line in lines:
        # Se a linha for muito longa, quebrar em palavras
        if len(line) > 80:  # Aumentar para 80 caracteres para debug messages
            words = line.split(' ')
            current_line = ""
            
            for word in words:
                if len(current_line) + len(word) + 1 <= 80:
                    if current_line:
                        current_line += " " + word
                    else:
                        current_line = word
                else:
                    if current_line:
                        formatted_lines.append(current_line)
                    current_line = word
            
            if current_line:
                formatted_lines.append(current_line)
        else:
            formatted_lines.append(line)
    
    # Atualizar o texto na barra de progresso
    final_text = "\n".join(formatted_lines)
    progress.setLabelText(final_text)
    
    # Forçar atualização da interface
    mw.app.processEvents()

def _sync_single_deck(remote_decks, deckKey, progress, status_msgs, step):
    """
    Sincroniza um único deck.
    
    Args:
        remote_decks: Dicionário de decks remotos
        deckKey: Chave do deck para sincronizar
        progress: Dialog de progresso
        status_msgs: Lista de mensagens de status
        step: Passo atual do progresso
        
    Returns:
        tuple: (step, deck_sync_increment, current_stats)
    """
    from .utils import add_debug_message
    from .deck_manager import DeckRecreationManager, DeckNameManager
    
    # Início da lógica de sincronização
    add_debug_message(f"🚀 INICIANDO sincronização para deck hash: {deckKey}", "SYNC")
    
    # Verificar se mw.col e mw.col.decks estão disponíveis
    if not _is_anki_decks_ready():
        raise SyncError("Anki não está pronto. Tente novamente em alguns instantes.")
    
    assert mw.col is not None  # Type hint para o checker
        
    currentRemoteInfo = remote_decks[deckKey]
    local_deck_id = currentRemoteInfo["local_deck_id"]
    remote_deck_url = currentRemoteInfo["remote_deck_url"]
    add_debug_message(f"📋 Local Deck ID: {local_deck_id}", "SYNC")
    add_debug_message(f"🔗 Remote URL: {remote_deck_url}", "SYNC")

    # Verificar se o deck existe ou precisa ser recriado
    was_recreated, current_deck_id, current_deck_name = DeckRecreationManager.recreate_deck_if_missing(currentRemoteInfo)
    
    if was_recreated and current_deck_id is not None and current_deck_name is not None:
        # Capturar o ID antigo antes da atualização para log correto
        old_deck_id = local_deck_id
        
        # Atualizar informações na configuração
        DeckRecreationManager.update_deck_info_after_recreation(currentRemoteInfo, current_deck_id, current_deck_name)
        
        # IMPORTANTE: Salvar imediatamente as mudanças de local_deck_id após recriação
        # Isso garante que o novo ID seja persistido mesmo se houver erro posterior
        save_remote_decks(remote_decks)
        add_debug_message(f"[CONFIG_SAVE] local_deck_id atualizado e salvo após recriação: {old_deck_id} -> {current_deck_id}", "SYNC")
        
        # Atualizar variáveis locais
        local_deck_id = current_deck_id
        
        # Informar sobre a recriação
        msg = f"Deck recriado: '{current_deck_name}'"
        status_msgs.append(msg)
        _update_progress_text(progress, status_msgs)
        
        step += 1
        progress.setValue(step)
        mw.app.processEvents()
    
    # Obter o deck atual (pode ser o original ou o recriado)
    if local_deck_id is None:
        raise ValueError("ID do deck local é None")
    
    # Garantir que o ID seja do tipo correto para o Anki
    from anki.decks import DeckId
    deck_id: DeckId = DeckId(local_deck_id)
    deck = mw.col.decks.get(deck_id)
    if not deck:
        raise ValueError(f"Falha ao obter deck: {deck_id}")
        
    deckName = deck["name"]
    add_debug_message(f"📋 Deck atual: '{deckName}' (ID: {deck_id})", "SYNC")

    # Atualizar informações na configuração com o nome real usado
    currentRemoteInfo["local_deck_name"] = deckName

    # Validar URL antes de tentar sincronizar
    validate_url(remote_deck_url)

    # 1. Download
    msg = f"{deckName}: baixando arquivo..."
    status_msgs.append(msg)
    _update_progress_text(progress, status_msgs)
    
    # Obter lista de estudantes habilitados para este deck
    from .student_manager import get_selected_students_for_deck
    enabled_students = get_selected_students_for_deck(remote_deck_url)
    add_debug_message(f"🎓 Estudantes habilitados para este deck: {list(enabled_students)}", "STUDENTS")
    
    remoteDeck = getRemoteDeck(remote_deck_url, enabled_students=list(enabled_students))
    
    # NOVO: Debug para verificar questões carregadas
    questions_count = len(remoteDeck.questions) if hasattr(remoteDeck, 'questions') and remoteDeck.questions else 0
    add_debug_message(f"📊 Questões carregadas do deck remoto: {questions_count}", "REMOTE_DECK")
    
    step += 1
    progress.setValue(step)
    mw.app.processEvents()

    # Atualizar remote_deck_name com o nome extraído da URL
    new_remote_name_from_url = DeckNameManager.extract_remote_name_from_url(remote_deck_url)
    stored_remote_name = currentRemoteInfo.get("remote_deck_name")
    
    # IMPORTANTE: Lógica aprimorada para resolver conflitos dinâmicamente
    # Verificar se o nome remoto mudou e reavaliar resolução de conflitos
    should_update = False
    if stored_remote_name != new_remote_name_from_url:
        # Verificar se o nome armazenado tem sufixo de conflito
        if stored_remote_name and ' #conflito' in stored_remote_name:
            # Nome tem sufixo de conflito - verificar se ainda é necessário
            add_debug_message(f"[CONFLICT_REEVALUATE] Reavaliando conflito: '{stored_remote_name}' vs novo nome '{new_remote_name_from_url}'", "SYNC")
            
            # Usar DeckNameManager centralizado para resolução de conflitos
            resolved_new_name = DeckNameManager.resolve_remote_name_conflict(remote_deck_url, new_remote_name_from_url)
            
            # Se o nome resolvido é igual ao nome original, não há mais conflito
            if resolved_new_name == new_remote_name_from_url:
                # Conflito foi resolvido - pode usar nome original
                should_update = True
                current_remote_name = new_remote_name_from_url
                add_debug_message(f"[CONFLICT_RESOLVED] Conflito resolvido! '{stored_remote_name}' → '{new_remote_name_from_url}'", "SYNC")
                
                # Também atualizar local_deck_name para remover o sufixo
                old_local_name = currentRemoteInfo.get("local_deck_name", "")
                if old_local_name and ' #conflito' in old_local_name:
                    # Remover sufixo do nome local também
                    new_local_name = old_local_name.split(' #conflito')[0]
                    add_debug_message(f"[CONFLICT_RESOLVED] Atualizando local_deck_name: '{old_local_name}' → '{new_local_name}'", "SYNC")
                    
                    # Atualizar nome do deck no Anki
                    try:
                        deck_id = currentRemoteInfo.get("local_deck_id")
                        if deck_id and mw and mw.col:
                            from anki.decks import DeckId
                            deck = mw.col.decks.get(DeckId(deck_id))
                            if deck:
                                old_anki_name = deck.get('name', '')
                                deck['name'] = new_local_name
                                mw.col.decks.save(deck)
                                add_debug_message(f"[ANKI_UPDATE] Deck renomeado no Anki: '{old_anki_name}' → '{new_local_name}'", "SYNC")
                    except Exception as e:
                        add_debug_message(f"[ANKI_ERROR] Erro ao renomear deck no Anki: {e}", "SYNC")
                    
                    # Atualizar na configuração
                    currentRemoteInfo["local_deck_name"] = new_local_name
                    remote_decks[deckKey]["local_deck_name"] = new_local_name
                    
            else:
                # Ainda há conflito, mas pode ter mudado o sufixo
                if resolved_new_name != stored_remote_name:
                    should_update = True
                    current_remote_name = resolved_new_name
                    add_debug_message(f"[CONFLICT_UPDATE] Atualizando sufixo de conflito: '{stored_remote_name}' → '{resolved_new_name}'", "SYNC")
                else:
                    add_debug_message(f"[CONFLICT_UNCHANGED] Mantendo resolução existente: '{stored_remote_name}'", "SYNC")
                    
        else:
            # Nome não tem conflito, aplicar resolução normal com DeckNameManager
            resolved_remote_name = DeckNameManager.resolve_remote_name_conflict(remote_deck_url, new_remote_name_from_url)
            
            if resolved_remote_name != stored_remote_name:
                should_update = True
                current_remote_name = resolved_remote_name
                add_debug_message(f"[CONFLICT_RESOLVE] Aplicando resolução: '{new_remote_name_from_url}' → '{resolved_remote_name}'", "SYNC")
    
    else:
        # Nome não mudou, não precisa atualizar
        add_debug_message(f"[CONFLICT_SKIP] Nome remoto não mudou, mantendo: '{stored_remote_name}'", "SYNC")
        current_remote_name = stored_remote_name
        
    # Aplicar atualização se necessário
    if should_update:
            # Usar DeckNameManager para sincronizar
            sync_result = DeckNameManager.sync_deck_with_config(remote_deck_url)
            
            # Atualizar configuração
            currentRemoteInfo["remote_deck_name"] = current_remote_name
            remote_decks[deckKey]["remote_deck_name"] = current_remote_name
            
            add_debug_message(f"[CONFIG_UPDATE] Configuração atualizada - remote: '{current_remote_name}'", "SYNC")
            
            # Salvar configuração usando o método existente
            save_remote_decks(remote_decks)
            add_debug_message(f"[CONFIG_SAVE] Configuração salva após atualização de nomes", "SYNC")
            
            # Atualizar os nomes dos note types no meta.json para refletir o novo remote_deck_name
            try:
                from .config_manager import update_note_type_names_in_meta
                from .student_manager import get_selected_students_for_deck
                from .utils import update_note_type_names_for_deck_rename
                
                enabled_students = get_selected_students_for_deck(remote_deck_url)
                update_note_type_names_in_meta(remote_deck_url, current_remote_name, enabled_students)
                
                # Atualizar nomes dos note types na configuração para o novo remote_deck_name
                updated_count = update_note_type_names_for_deck_rename(
                    remote_deck_url, 
                    stored_remote_name, 
                    current_remote_name, 
                    None,  # enabled_students não é necessário para a captura de IDs
                )
                if updated_count > 0:
                    add_debug_message(f"[NOTE_TYPE_RENAME] {updated_count} note types atualizados para novo remote_deck_name", "SYNC")
                    
                    # Garantir que as mudanças sejam persistidas no meta.json antes da sincronização
                    time.sleep(0.1)  # Pequeno delay para garantir que o arquivo seja salvo
                    
                    # Sincronizar imediatamente os nomes no Anki após atualização na config
                    from .utils import sync_note_type_names_with_config
                    try:
                        add_debug_message(f"[NOTE_TYPE_SYNC] Iniciando sincronização imediata após rename...", "SYNC")
                        sync_stats = sync_note_type_names_with_config(mw.col, remote_deck_url)
                        if sync_stats['synced_note_types'] > 0:
                            add_debug_message(f"[NOTE_TYPE_SYNC] {sync_stats['synced_note_types']} note types sincronizados no Anki imediatamente", "SYNC")
                        else:
                            add_debug_message(f"[NOTE_TYPE_SYNC] Nenhuma mudança necessária na sincronização imediata", "SYNC")
                    except Exception as sync_error:
                        add_debug_message(f"[NOTE_TYPE_SYNC] Erro na sincronização imediata: {sync_error}", "SYNC")
                        add_debug_message(f"[NOTE_TYPE_SYNC] Traceback: {traceback.format_exc()}", "SYNC")
                
            except Exception as e:
                print(f"[Sheets2Anki] Erro ao atualizar nomes de note types no meta.json: {e}")
                add_debug_message(f"[NOTE_TYPE_RENAME] Erro ao atualizar note types: {e}", "SYNC")

    # 2. Processamento (já incluído no getRemoteDeck)
    msg = f"{deckName}: processando dados..."
    status_msgs.append(msg)
    _update_progress_text(progress, status_msgs)
    
    remoteDeck.deckName = deckName
    
    # Atualizar nome do deck se necessário usando DeckNameManager
    current_remote_name = currentRemoteInfo.get("remote_deck_name")
    sync_result = DeckNameManager.sync_deck_with_config(remote_deck_url)
    if sync_result:
        sync_deck_id, updated_name = sync_result
        if updated_name != deckName:
            # Atualizar informações do deck na configuração
            currentRemoteInfo["local_deck_name"] = updated_name
            deckName = updated_name
            remoteDeck.deckName = updated_name
        
        msg = f"{deckName}: nome do deck atualizado automaticamente..."
        status_msgs.append(msg)
        _update_progress_text(progress, status_msgs)
    
    # Sincronizar nome do deck no Anki com a configuração usando DeckNameManager
    from .utils import sync_note_type_names_with_config
    sync_result = DeckNameManager.sync_deck_with_config(remote_deck_url)
    if sync_result:
        synced_deck_id, synced_name = sync_result
        if synced_name != deckName:
            msg = f"{deckName}: nome sincronizado no Anki para '{synced_name}'"
            status_msgs.append(msg)
            add_debug_message(f"[DECK_SYNC] Deck renomeado no Anki: {deckName} → {synced_name}", "SYNC")
    
    # Sincronizar nomes dos note types no Anki com a configuração (source of truth) - FINAL
    add_debug_message(f"[NOTE_TYPE_SYNC] Executando sincronização FINAL dos note types...", "SYNC")
    note_sync_stats = sync_note_type_names_with_config(mw.col, remote_deck_url)
    if note_sync_stats:
        if note_sync_stats['synced_note_types'] > 0:
            msg = f"{deckName}: {note_sync_stats['synced_note_types']} note types sincronizados"
            status_msgs.append(msg)
            add_debug_message(f"[NOTE_TYPE_SYNC] FINAL: {note_sync_stats['synced_note_types']} note types atualizados no Anki", "SYNC")
        else:
            add_debug_message(f"[NOTE_TYPE_SYNC] FINAL: Todos os note types já estavam sincronizados", "SYNC")
            
        if note_sync_stats['error_note_types'] > 0:
            add_debug_message(f"[NOTE_TYPE_SYNC] FINAL: {note_sync_stats['error_note_types']} erros durante sincronização", "SYNC")
            for error in note_sync_stats.get('errors', []):
                add_debug_message(f"[NOTE_TYPE_SYNC] ERRO: {error}", "SYNC")
    else:
        add_debug_message(f"[NOTE_TYPE_SYNC] FINAL: Nenhuma estatística retornada", "SYNC")
        add_debug_message(f"[NOTE_TYPE_SYNC] {note_sync_stats['synced_note_types']} note types atualizados no Anki", "SYNC")
    
    step += 1
    progress.setValue(step)
    mw.app.processEvents()

    # 3. Escrita no banco
    msg = f"{deckName}: escrevendo no banco de dados..."
    status_msgs.append(msg)
    _update_progress_text(progress, status_msgs)
    
    add_debug_message(f"🚀 ABOUT TO CALL create_or_update_notes - remoteDeck has {len(remoteDeck.questions) if hasattr(remoteDeck, 'questions') and remoteDeck.questions else 0} questions", "SYNC")
    
    deck_stats_dict = create_or_update_notes(mw.col, remoteDeck, local_deck_id, deck_url=remote_deck_url)
    
    add_debug_message(f"✅ create_or_update_notes COMPLETED - returned: {deck_stats_dict}", "SYNC")
    
    # Converter para o novo formato SyncStats
    deck_stats = SyncStats(
        created=deck_stats_dict.get('created', 0),
        updated=deck_stats_dict.get('updated', 0),
        deleted=deck_stats_dict.get('deleted', 0),
        ignored=deck_stats_dict.get('ignored', 0),
        errors=deck_stats_dict.get('errors', 0)
    )
    
    # Adicionar detalhes de erros se existirem
    for error in deck_stats_dict.get('error_details', []):
        deck_stats.add_error(error)
    
    # Adicionar detalhes de atualizações se existirem
    for detail in deck_stats_dict.get('updated_details', []):
        deck_stats.add_update_detail(detail)
    
    step += 1
    progress.setValue(step)
    mw.app.processEvents()

    # 4. Capturar e armazenar IDs dos note types após sincronização bem-sucedida
    try:
        from .utils import capture_deck_note_type_ids
        
        add_debug_message(f"Iniciando captura de note type IDs para deck: {deckName}", "SYNC")
        
        # Capturar IDs dos note types criados/atualizados
        capture_deck_note_type_ids(
            remote_deck_url,  # Usar a URL real em vez da hash key
            currentRemoteInfo.get("remote_deck_name", "RemoteDeck"),
            None,  # enabled_students não é necessário para a captura de IDs
            None  # enabled_students não é necessário para a captura de IDs
        )
        
        add_debug_message(f"✅ IDs de note types capturados e armazenados para deck: {deckName}", "SYNC")
        
    except Exception as e:
        # Não falhar a sincronização por causa da captura de IDs
        add_debug_message(f"❌ ERRO na captura de note type IDs para {deckName}: {e}", "SYNC")
        error_details = traceback.format_exc()
        add_debug_message(f"Detalhes do erro: {error_details}", "SYNC")

    return step, 1, deck_stats

def _accumulate_stats(total_stats, deck_stats):
    """Acumula estatísticas de um deck nas estatísticas totais."""
    total_stats['created'] += deck_stats['created']
    total_stats['updated'] += deck_stats['updated']
    total_stats['deleted'] += deck_stats['deleted']
    total_stats['ignored'] += deck_stats.get('ignored', 0)
    total_stats['errors'] += deck_stats['errors']
    total_stats['error_details'].extend(deck_stats['error_details'])
    
    # Adicionar todos os detalhes das atualizações (sem limite)
    if 'updated_details' in deck_stats:
        if 'updated_details' not in total_stats:
            total_stats['updated_details'] = []
        total_stats['updated_details'].extend(deck_stats['updated_details'])

def _handle_sync_error(e, deckKey, remote_decks, progress, status_msgs, sync_errors, step):
    """Trata erros de sincronização de deck."""
    # Verificar se mw.col e mw.col.decks estão disponíveis
    if not _is_anki_decks_ready():
        deckName = "Unknown"
    else:
        assert mw.col is not None  # Type hint para o checker
        # Tentar obter o nome do deck para a mensagem de erro
        try:
            deck_info = remote_decks[deckKey]
            local_deck_id = deck_info["local_deck_id"]
            deck = mw.col.decks.get(local_deck_id) if local_deck_id is not None else None
            deckName = deck["name"] if deck else (deck_info.get("local_deck_name") or str(local_deck_id) if local_deck_id is not None else "Unknown")
        except:
            deckName = "Unknown"
    
    error_msg = f"Failed to sync deck '{deckName}': {str(e)}"
    sync_errors.append(error_msg)
    status_msgs.append(error_msg)
    _update_progress_text(progress, status_msgs)
    step += 3
    progress.setValue(step)
    mw.app.processEvents()
    return step, sync_errors

def _handle_unexpected_error(e, deckKey, remote_decks, progress, status_msgs, sync_errors, step):
    """Trata erros inesperados durante sincronização."""
    # Verificar se mw.col e mw.col.decks estão disponíveis
    if not _is_anki_decks_ready():
        deckName = "Unknown"
    else:
        assert mw.col is not None  # Type hint para o checker
        # Tentar obter o nome do deck para a mensagem de erro
        try:
            deck_info = remote_decks[deckKey]
            local_deck_id = deck_info["local_deck_id"]
            deck = mw.col.decks.get(local_deck_id) if local_deck_id is not None else None
            from .config_manager import get_deck_local_name
            deckName = deck["name"] if deck else (get_deck_local_name(deckKey) or str(local_deck_id) if local_deck_id is not None else "Unknown")
        except:
            deckName = "Unknown"
    
    error_msg = f"Unexpected error syncing deck '{deckName}': {str(e)}"
    sync_errors.append(error_msg)
    status_msgs.append(error_msg)
    _update_progress_text(progress, status_msgs)
    step += 3
    progress.setValue(step)
    mw.app.processEvents()
    return step, sync_errors

def _finalize_sync(progress, total_decks, decks_synced, total_stats, sync_errors, debug_messages=None, cleanup_result=None, missing_cleanup_result=None):
    """Finaliza a sincronização mostrando resultados."""
    progress.setValue(total_decks * 3)
    mw.app.processEvents()
    
    # Aplicar opções compartilhadas automaticamente após sincronização
    try:
        if mw and mw.col:  # Verificar se Anki está disponível
            from .utils import apply_sheets2anki_options_to_all_remote_decks, ensure_parent_deck_has_shared_options
            
            # 1. Aplicar ao deck raiz "Sheets2Anki" (sempre)
            ensure_parent_deck_has_shared_options()
            
            # 2. Aplicar a todos os decks remotos sincronizados
            options_stats = apply_sheets2anki_options_to_all_remote_decks()
            if options_stats['success'] and options_stats['updated_decks'] > 0:
                print(f"[SYNC_OPTIONS] Opções aplicadas a {options_stats['updated_decks']} decks remotos")
                
    except Exception as e:
        print(f"[SYNC_OPTIONS] Aviso: Erro ao aplicar opções compartilhadas: {e}")
    
    # Remover subdecks vazios após a sincronização
    remote_decks = get_remote_decks()
    removed_subdecks = remove_empty_subdecks(remote_decks)
    
    # Preparar mensagem final para exibir na barra de progresso
    cleanup_info = ""
    if cleanup_result:
        cleanup_info = f", {cleanup_result['disabled_students_count']} alunos removidos"
    
    if missing_cleanup_result:
        if cleanup_info:
            cleanup_info += f", dados [MISSING A.] removidos"
        else:
            cleanup_info = f", dados [MISSING A.] removidos"
    
    if sync_errors or total_stats['errors'] > 0:
        final_msg = f"Concluído com problemas: {decks_synced}/{total_decks} decks sincronizados"
        if total_stats['created'] > 0:
            final_msg += f", {total_stats['created']} notas criadas"
        if total_stats['updated'] > 0:
            final_msg += f", {total_stats['updated']} atualizadas"
        if total_stats['deleted'] > 0:
            final_msg += f", {total_stats['deleted']} deletadas"
        if total_stats['ignored'] > 0:
            final_msg += f", {total_stats['ignored']} ignoradas"
        if removed_subdecks > 0:
            final_msg += f", {removed_subdecks} subdecks vazios removidos"
        if cleanup_info:
            final_msg += cleanup_info
        final_msg += f", {total_stats['errors'] + len(sync_errors)} erros"
    else:
        final_msg = f"Sincronização concluída com sucesso!"
        if total_stats['created'] > 0:
            final_msg += f" {total_stats['created']} notas criadas"
        if total_stats['updated'] > 0:
            final_msg += f", {total_stats['updated']} atualizadas"
        if total_stats['deleted'] > 0:
            final_msg += f", {total_stats['deleted']} deletadas"
        if total_stats['ignored'] > 0:
            final_msg += f", {total_stats['ignored']} ignoradas"
        if removed_subdecks > 0:
            final_msg += f", {removed_subdecks} subdecks vazios removidos"
        if cleanup_info:
            final_msg += cleanup_info
    
    # Remover informação sobre debug messages do final_msg (interface limpa)
    
    # Adicionar mensagem final de debug
    if debug_messages is not None:
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        add_debug_message("🎬 FIM - Sincronização finalizada", "SYSTEM")
    
    # Exibir mensagem final na barra SEM debug messages (interface limpa)
    final_status_msgs = [final_msg]
    _update_progress_text(progress, final_status_msgs, max_lines=5, debug_messages=None, show_debug=False)
    
    # Fechar o progress dialog antes de mostrar o resumo detalhado
    progress.close()
    
    # Mostrar resumo abrangente dos resultados da sincronização com botão de debug integrado
    _show_sync_summary(sync_errors, total_stats, decks_synced, total_decks, removed_subdecks, cleanup_result, debug_messages, missing_cleanup_result)
    
    # Atualizar a interface do Anki após mostrar o resumo
    ensure_interface_refresh()

def _show_debug_messages_window(debug_messages):
    """
    Mostra uma janela scrollable com todas as mensagens de debug.
    Adaptada para dark mode e light mode do Anki.
    
    Args:
        debug_messages: Lista de mensagens de debug para exibir
    """
    from aqt.qt import QDialog, QVBoxLayout, QTextEdit, QPushButton, QLabel
    
    dialog = QDialog(mw)
    dialog.setWindowTitle(f"Debug Messages - Sistema de Note Type IDs ({len(debug_messages)} mensagens)")
    dialog.setFixedSize(800, 600)
    
    layout = QVBoxLayout(dialog)
    
    # Detectar dark mode usando método mais direto
    is_dark_mode = False
    if hasattr(mw, 'pm') and hasattr(mw.pm, 'night_mode'):
        is_dark_mode = mw.pm.night_mode()
    
    # Definir cores baseadas no tema
    if is_dark_mode:
        # Dark mode colors - cores com alto contraste
        bg_color = "#1e1e1e"        # Fundo muito escuro
        text_color = "#f0f0f0"      # Texto muito claro
        border_color = "#555555"     # Borda média
        info_bg_color = "#2d2d2d"   # Fundo do info um pouco mais claro
        scroll_bg = "#3d3d3d"       # Fundo da scrollbar
        scroll_handle = "#707070"    # Handle da scrollbar
        scroll_hover = "#909090"     # Handle hover
        button_bg = "#4a4a4a"       # Fundo do botão
        button_hover = "#5a5a5a"    # Hover do botão
    else:
        # Light mode colors - cores tradicionais
        bg_color = "#ffffff"
        text_color = "#000000"
        border_color = "#cccccc"
        info_bg_color = "#f8f8f8"
        scroll_bg = "#f0f0f0"
        scroll_handle = "#c0c0c0"
        scroll_hover = "#a0a0a0"
        button_bg = "#f0f0f0"
        button_hover = "#e0e0e0"
    
    # Adicionar label informativo
    info_label = QLabel(f"📋 Total de {len(debug_messages)} mensagens de debug capturadas durante a sincronização:")
    info_label.setStyleSheet(f"""
        QLabel {{
            font-weight: bold; 
            margin-bottom: 5px;
            color: {text_color};
            background-color: {info_bg_color};
            padding: 8px;
            border-radius: 4px;
            border: 1px solid {border_color};
        }}
    """)
    layout.addWidget(info_label)
    
    # Criar área de texto scrollable com cores de alto contraste
    text_area = QTextEdit()
    text_area.setReadOnly(True)
    text_area.setPlainText("\n".join(debug_messages))
    text_area.setStyleSheet(f"""
        QTextEdit {{
            font-family: 'Courier New', 'Monaco', 'Consolas', 'Liberation Mono', monospace;
            font-size: 10pt;
            background-color: {bg_color};
            color: {text_color};
            border: 2px solid {border_color};
            line-height: 1.4;
            padding: 10px;
            selection-background-color: {"#4a4a4a" if is_dark_mode else "#3390ff"};
            selection-color: {text_color};
        }}
        QScrollBar:vertical {{
            background-color: {scroll_bg};
            width: 14px;
            border: 1px solid {border_color};
        }}
        QScrollBar::handle:vertical {{
            background-color: {scroll_handle};
            border-radius: 6px;
            margin: 2px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {scroll_hover};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            background: none;
            border: none;
        }}
    """)
    
    layout.addWidget(text_area)
    
    # Botão para fechar com estilo apropriado
    close_button = QPushButton("Fechar")
    close_button.clicked.connect(dialog.accept)
    close_button.setDefault(True)
    close_button.setStyleSheet(f"""
        QPushButton {{
            background-color: {button_bg};
            color: {text_color};
            border: 1px solid {border_color};
            padding: 10px 20px;
            border-radius: 6px;
            font-weight: bold;
            min-width: 80px;
        }}
        QPushButton:hover {{
            background-color: {button_hover};
        }}
        QPushButton:pressed {{
            background-color: {border_color};
        }}
    """)
    layout.addWidget(close_button)
    
    # Aplicar estilo geral ao dialog
    dialog.setStyleSheet(f"""
        QDialog {{
            background-color: {info_bg_color};
            color: {text_color};
        }}
    """)
    
    from .compat import safe_exec_dialog
    safe_exec_dialog(dialog)

def _show_sync_summary(sync_errors, total_stats, decks_synced, total_decks, removed_subdecks=0, cleanup_result=None, debug_messages=None, missing_cleanup_result=None):
    """Mostra resumo detalhado da sincronização com controles de visualização para detalhes."""
    # Preparar o resumo básico
    if sync_errors or total_stats['errors'] > 0:
        summary = f"Sincronização concluída com alguns problemas:\n\n"
        summary += f"Decks sincronizados: {decks_synced}/{total_decks}\n"
        summary += f"Notas criadas: {total_stats['created']}\n"
        summary += f"Notas atualizadas: {total_stats['updated']}\n"
        summary += f"Notas deletadas: {total_stats['deleted']}\n"
        summary += f"Notas ignoradas: {total_stats['ignored']}\n"
        if removed_subdecks > 0:
            summary += f"Subdecks vazios removidos: {removed_subdecks}\n"
        
        # Incluir informações de limpeza de alunos removidos
        if cleanup_result and cleanup_result['disabled_students_count'] > 0:
            summary += f"Alunos removidos: {cleanup_result['disabled_students_count']} ({cleanup_result['disabled_students_names']})\n"
        
        # Incluir informações de limpeza [MISSING A.]
        if missing_cleanup_result:
            summary += f"Dados [MISSING A.] removidos\n"
        
        summary += f"Erros encontrados: {total_stats['errors'] + len(sync_errors)}\n\n"
        
        # Adicionar erros de nível de deck
        if sync_errors:
            summary += "Erros de sincronização de decks:\n"
            summary += "\n".join(sync_errors) + "\n\n"
        
        # Adicionar erros de nível de note (sem limite)
        if total_stats['error_details']:
            summary += "Erros de processamento de notas:\n"
            summary += "\n".join(total_stats['error_details'])
    else:
        summary = f"Sincronização concluída com sucesso!\n\n"
        summary += f"Decks sincronizados: {decks_synced}\n"
        summary += f"Notas criadas: {total_stats['created']}\n"
        summary += f"Notas atualizadas: {total_stats['updated']}\n"
        summary += f"Notas deletadas: {total_stats['deleted']}\n"
        summary += f"Notas ignoradas: {total_stats['ignored']}\n"
        if removed_subdecks > 0:
            summary += f"Subdecks vazios removidos: {removed_subdecks}\n"
        
        # Incluir informações de limpeza de alunos removidos
        if cleanup_result and cleanup_result['disabled_students_count'] > 0:
            summary += f"Alunos removidos: {cleanup_result['disabled_students_count']} ({cleanup_result['disabled_students_names']})\n"
        
        # Incluir informações de limpeza [MISSING A.]
        if missing_cleanup_result:
            summary += f"Dados [MISSING A.] removidos\n"
        
        summary += "Nenhum erro encontrado."
    
    # Se há detalhes de atualizações, mostrar em um diálogo com controles
    if total_stats.get('updated_details'):
        # Verificar se mw está disponível
        if not mw:
            showInfo(summary)
            return
            
        _show_detailed_summary_dialog(summary, total_stats, removed_subdecks, cleanup_result, debug_messages, missing_cleanup_result)
    else:
        # Se não há detalhes de atualizações, mostrar apenas o resumo
        # Mas ainda incluir botão de debug se disponível
        if debug_messages and len(debug_messages) > 0:
            # Criar um diálogo simples com botão de debug
            dialog = QDialog(mw)
            dialog.setWindowTitle("Sincronização Finalizada")
            dialog.setMinimumSize(400, 300)
            
            layout = QVBoxLayout()
            
            # Resumo
            summary_label = QLabel(summary)
            summary_label.setWordWrap(True)
            layout.addWidget(summary_label)
            
            # Botões
            button_box = QDialogButtonBox(ButtonBox_Ok)
            
            # Adicionar botão de debug
            debug_button = QPushButton("Mostrar Debug")
            debug_button.clicked.connect(lambda: _show_debug_messages_window(debug_messages))
            button_box.addButton(debug_button, QDialogButtonBox.ButtonRole.ActionRole)
            
            button_box.accepted.connect(dialog.accept)
            layout.addWidget(button_box)
            
            dialog.setLayout(layout)
            safe_exec_dialog(dialog)
        else:
            # ShowInfo padrão se não há debug
            showInfo(summary)


def _show_detailed_summary_dialog(summary, total_stats, removed_subdecks, cleanup_result=None, debug_messages=None, missing_cleanup_result=None):
    """Mostra diálogo detalhado com controles de visualização."""
    
    # Criar diálogo personalizado
    dialog = QDialog(mw)
    dialog.setWindowTitle("Resumo da Sincronização")
    dialog.setMinimumSize(700, 600)
    
    layout = QVBoxLayout()
    
    # Resumo geral no topo
    summary_label = QLabel(summary)
    summary_label.setWordWrap(True)
    layout.addWidget(summary_label)
    
    debug_messages = total_stats.get('debug_messages', [])
    
    # Sempre usar abas quando há debug messages ou detalhes de atualizações
    if debug_messages or total_stats.get('updated_details'):
        # Criar widget de abas
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # ABA 1: DETALHES DAS ATUALIZAÇÕES (se houver)
        if total_stats.get('updated_details'):
            updates_tab = QWidget()
            updates_layout = QVBoxLayout()
            
            # Controles
            total_updates = len(total_stats['updated_details'])
            controls_frame = QFrame()
            controls_layout = QHBoxLayout()
            controls_frame.setLayout(controls_layout)
            
            controls_layout.addWidget(QLabel(f"Mostrar detalhes (total: {total_updates}):"))
            
            quantity_spinner = QSpinBox()
            quantity_spinner.setMinimum(1)
            quantity_spinner.setMaximum(max(1, total_updates))
            quantity_spinner.setValue(min(20, total_updates))
            quantity_spinner.setSuffix(f" de {total_updates}")
            controls_layout.addWidget(quantity_spinner)
            
            show_all_button = QPushButton("Mostrar Todos")
            controls_layout.addWidget(show_all_button)
            controls_layout.addStretch()
            
            updates_layout.addWidget(controls_frame)
            
            # Área de texto para detalhes
            details_text = QTextEdit()
            details_text.setReadOnly(True)
            updates_layout.addWidget(details_text)
            
            def update_details_display():
                quantity = quantity_spinner.value()
                details = f"Detalhes das atualizações realizadas (mostrando {quantity} de {total_updates}):\n\n"
                
                for i, update in enumerate(total_stats['updated_details'][:quantity], 1):
                    details += f"{i}. ID: {update['id']}\n"
                    details += f"   Pergunta: {update['pergunta']}\n"
                    details += f"   Mudanças:\n"
                    for change in update['changes']:
                        details += f"     • {change}\n"
                    details += "\n"
                
                if removed_subdecks > 0:
                    details += f"\n\nSubdecks vazios removidos: {removed_subdecks}\n"
                
                details_text.setPlainText(details)
            
            def show_all_details():
                quantity_spinner.setValue(total_updates)
            
            quantity_spinner.valueChanged.connect(update_details_display)
            show_all_button.clicked.connect(show_all_details)
            update_details_display()
            
            updates_tab.setLayout(updates_layout)
            tab_widget.addTab(updates_tab, f"Atualizações ({total_updates})")
        
        # ABA 2: MENSAGENS DE DEBUG
        if debug_messages:
            debug_tab = QWidget()
            debug_layout = QVBoxLayout()
            
            debug_header = QLabel(f"Mensagens de Debug ({len(debug_messages)} mensagens)")
            debug_header.setStyleSheet("font-weight: bold; color: #0066cc;")
            debug_layout.addWidget(debug_header)
            
            debug_text = QTextEdit()
            debug_text.setReadOnly(True)
            debug_text.setFont(QFont("Courier", 9))
            
            debug_content = "\n".join(debug_messages)
            debug_text.setPlainText(debug_content)
            
            debug_layout.addWidget(debug_text)
            debug_tab.setLayout(debug_layout)
            tab_widget.addTab(debug_tab, f"Debug ({len(debug_messages)})")
        
        # Se não há abas, criar uma aba padrão
        if tab_widget.count() == 0:
            default_tab = QWidget()
            default_layout = QVBoxLayout()
            default_layout.addWidget(QLabel("Nenhum detalhe adicional disponível."))
            default_tab.setLayout(default_layout)
            tab_widget.addTab(default_tab, "Resumo")
    else:
        # Caso simples: apenas o resumo básico  
        layout.addWidget(QLabel("Nenhum detalhe adicional disponível."))
    total_updates = len(total_stats['updated_details'])
    controls_layout.addWidget(QLabel(f"Mostrar detalhes (total: {total_updates}):"))
    
    # Spinner para quantidade
    quantity_spinner = QSpinBox()
    quantity_spinner.setMinimum(1)
    quantity_spinner.setMaximum(max(1, total_updates))
    quantity_spinner.setValue(min(20, total_updates))  # Padrão: 20 ou total se menor
    quantity_spinner.setSuffix(f" de {total_updates}")
    controls_layout.addWidget(quantity_spinner)
    
    # Botão para mostrar todos
    show_all_button = QPushButton("Mostrar Todos")
    controls_layout.addWidget(show_all_button)
    
    # Espaçador
    controls_layout.addStretch()
    
    layout.addWidget(controls_frame)
    
    # Área de texto com scroll para os detalhes das atualizações
    details_text = QTextEdit()
    details_text.setReadOnly(True)
    layout.addWidget(details_text)
    
    # Função para atualizar os detalhes mostrados
    def update_details_display():
        quantity = quantity_spinner.value()
        
        # Preparar texto detalhado das atualizações
        details = f"Detalhes das atualizações realizadas (mostrando {quantity} de {total_updates}):\n\n"
        
        for i, update in enumerate(total_stats['updated_details'][:quantity], 1):
            details += f"{i}. ID: {update['id']}\n"
            details += f"   Pergunta: {update['pergunta']}\n"
            details += f"   Mudanças:\n"
            # Separar cada mudança em uma nova linha com indentação
            for change in update['changes']:
                details += f"     • {change}\n"
            details += "\n"
        
        # Adicionar informação sobre subdecks vazios removidos, se houver
        if removed_subdecks > 0:
            details += f"\n\nSubdecks vazios removidos: {removed_subdecks}\n"
            details += "Subdecks sem cards foram automaticamente removidos para manter a organização."
        
        details_text.setPlainText(details)
    
    # Função para mostrar todos os detalhes
    def show_all_details():
        quantity_spinner.setValue(total_updates)
    
    # Conectar sinais
    quantity_spinner.valueChanged.connect(update_details_display)
    show_all_button.clicked.connect(show_all_details)
    
    # Atualizar display inicial
    update_details_display()
    
    # Botões
    button_box = QDialogButtonBox(ButtonBox_Ok)
    
    # Adicionar botão de debug se há mensagens de debug
    if debug_messages and len(debug_messages) > 0:
        debug_button = QPushButton("Mostrar Debug")
        debug_button.clicked.connect(lambda: _show_debug_messages_window(debug_messages))
        button_box.addButton(debug_button, QDialogButtonBox.ButtonRole.ActionRole)
    
    button_box.accepted.connect(dialog.accept)
    layout.addWidget(button_box)
    
    dialog.setLayout(layout)
    safe_exec_dialog(dialog)


def _handle_consolidated_cleanup(remote_decks):
    """
    Gerencia limpezas de dados de forma consolidada para evitar múltiplas confirmações.
    
    Esta função verifica se há necessidade de limpeza de:
    1. Alunos desabilitados
    2. Notas [MISSING A.] (quando funcionalidade foi desabilitada)
    
    Se ambos precisam de limpeza, mostra uma única confirmação consolidada.
    Se apenas um precisa, usa a confirmação específica.
    
    Args:
        remote_decks (dict): Dicionário de decks remotos configurados
        
    Returns:
        tuple: (missing_cleanup_result, cleanup_result)
    """
    # Verificar se precisa de limpeza [MISSING A.]
    needs_missing_cleanup = _needs_missing_students_cleanup(remote_decks)
    
    # Verificar se precisa de limpeza de alunos desabilitados
    needs_disabled_cleanup = _needs_disabled_students_cleanup(remote_decks)
    
    if not needs_missing_cleanup and not needs_disabled_cleanup:
        # Nenhuma limpeza necessária
        return None, None
    
    if needs_missing_cleanup and needs_disabled_cleanup:
        # Ambas as limpezas são necessárias - mostrar confirmação consolidada
        return _handle_consolidated_confirmation_cleanup(remote_decks)
    
    elif needs_missing_cleanup:
        # Apenas limpeza [MISSING A.]
        missing_result = _handle_missing_students_cleanup(remote_decks)
        return missing_result, None
    
    else:
        # Apenas limpeza de alunos desabilitados
        cleanup_result = _handle_disabled_students_cleanup(remote_decks)
        return None, cleanup_result


def _needs_missing_students_cleanup(remote_decks):
    """
    Verifica se é necessário fazer limpeza de dados [MISSING A.] sem mostrar diálogos.
    
    Returns:
        bool: True se limpeza é necessária
    """
    from .config_manager import is_sync_missing_students_notes, is_auto_remove_disabled_students
    
    # PRIMEIRA VERIFICAÇÃO: Se funcionalidade está ativada, não precisa limpar
    if is_sync_missing_students_notes():
        print(f"🔍 [MISSING A.]: Funcionalidade ATIVADA, nenhuma limpeza necessária")
        return False  # Funcionalidade ativada, não precisa limpar
    
    # SEGUNDA VERIFICAÇÃO: Se remoção automática está desabilitada, não limpar
    if not is_auto_remove_disabled_students():
        print(f"🔍 [MISSING A.]: Funcionalidade DESATIVADA, mas remoção automática também DESABILITADA - não limpar")
        return False
    
    print(f"🔍 [MISSING A.]: Funcionalidade DESATIVADA e remoção automática ATIVADA, verificando se há dados para limpar...")
    
    # Verificar se há dados [MISSING A.] para limpar
    deck_names = [deck_info.get('remote_deck_name', '') for deck_info in remote_decks.values()]
    deck_names = [name for name in deck_names if name]
    
    if not deck_names or not _is_anki_ready():
        print(f"🔍 [MISSING A.]: Sem decks ou sem conexão com Anki")
        return False
    
    assert mw.col is not None  # Type hint para o checker
    col = mw.col
    has_missing_data = False
    
    for deck_name in deck_names:
        print(f"🔍 [MISSING A.]: Verificando deck '{deck_name}'...")
        
        # Verificar se há decks [MISSING A.]
        missing_deck_pattern = f"{deck_name}::[MISSING A.]::"
        all_decks = col.decks.all_names_and_ids()
        
        missing_decks_found = [deck.name for deck in all_decks if deck.name.startswith(missing_deck_pattern)]
        if missing_decks_found:
            has_missing_data = True
            print(f"  📁 Encontrados {len(missing_decks_found)} decks [MISSING A.]")
        
        # Verificar se há note types [MISSING A.]
        all_models = col.models.all()
        missing_pattern = f"Sheets2Anki - {deck_name} - [MISSING A.] -"
        
        missing_models_found = [model['name'] for model in all_models if missing_pattern in model['name']]
        if missing_models_found:
            has_missing_data = True
            print(f"  🏷️ Encontrados {len(missing_models_found)} note types [MISSING A.]")
            
        if has_missing_data:
            break  # Já encontrou dados, não precisa continuar
    
    if has_missing_data:
        print(f"⚠️ [MISSING A.]: Dados encontrados, limpeza necessária")
    else:
        print(f"✅ [MISSING A.]: Nenhum dado encontrado, limpeza desnecessária")
    
    return has_missing_data


def _needs_disabled_students_cleanup(remote_decks):
    """
    Verifica se é necessário fazer limpeza de alunos desabilitados.
    
    NOVA VERSÃO: Usa normalização consistente de nomes.
    
    ROBUSTEZ: Usa múltiplas fontes para detectar alunos anteriormente habilitados:
    1. Note types existentes no Anki
    2. Configuração global de estudantes disponíveis  
    3. Dados dos decks remotos
    
    Returns:
        bool: True se limpeza é necessária
    """
    from .config_manager import is_auto_remove_disabled_students, get_global_student_config
    
    # PRIMEIRA VERIFICAÇÃO: Auto-remoção deve estar ativa
    if not is_auto_remove_disabled_students():
        return False
    
    config = get_global_student_config()
    current_enabled_raw = config.get("enabled_students", [])
    
    # Estudantes atualmente habilitados (case-sensitive)
    current_enabled_set = {student for student in current_enabled_raw if student and student.strip()}
    
    # MÚLTIPLAS FONTES para detectar alunos anteriormente habilitados (ROBUSTEZ)
    previous_enabled_raw = set()
    
    # Fonte 1: Note types existentes no Anki
    note_types_students = _get_students_from_existing_note_types(remote_decks)
    previous_enabled_raw.update(note_types_students)
    
    # Fonte 2: Todos os estudantes disponíveis
    available_students = config.get("available_students", [])
    previous_enabled_raw.update(available_students)
    
    # Fonte 3: Verificar se há decks/notas de alunos no Anki (scan direto)
    if mw and hasattr(mw, 'col') and mw.col:
        anki_students = _get_students_from_anki_data()
        previous_enabled_raw.update(anki_students)
    
    # Processar previous_enabled (case-sensitive)
    previous_enabled_set = {student for student in previous_enabled_raw if student and student.strip()}
    
    # CALCULAR alunos desabilitados (case-sensitive)
    disabled_students_set = previous_enabled_set - current_enabled_set
    
    if disabled_students_set:
        print(f"🔍 CLEANUP: Detectados alunos para limpeza:")
        print(f"  • Atualmente habilitados: {sorted(current_enabled_raw)}")
        print(f"  • Anteriormente habilitados: {sorted(previous_enabled_set)}")  
        print(f"  • Alunos a remover: {sorted(disabled_students_set)}")
    
    return bool(disabled_students_set)


def _get_students_from_anki_data():
    """
    NOVA FUNÇÃO: Escaneia dados do Anki para encontrar estudantes com dados existentes.
    Agora usa normalização consistente de nomes.
    
    Returns:
        set: Conjunto de alunos encontrados no Anki (nomes normalizados)
    """
    students_found = set()
    
    if not _is_anki_ready():
        return students_found
    
    assert mw.col is not None  # Type hint para o checker
    col = mw.col
    
    try:
        # Escanear decks por padrões de alunos "DeckName::StudentName::"
        all_decks = col.decks.all_names_and_ids()
        for deck in all_decks:
            deck_parts = deck.name.split("::")
            if len(deck_parts) >= 2 and "Sheets2Anki" in deck_parts[0]:
                # Possível aluno na segunda posição
                potential_student = deck_parts[1].strip()
                if potential_student and potential_student != "[MISSING A.]":
                    students_found.add(potential_student)
        
        # Escanear note types buscando nomes de estudantes
        all_models = col.models.all()
        for model in all_models:
            model_name = model['name']
            if "Sheets2Anki -" in model_name:
                # Extrair nome do estudante do formato: "Sheets2Anki - Deck - StudentName - Type"
                parts = model_name.split(" - ")
                if len(parts) >= 4:
                    student_name = parts[2].strip()  # Third part is student name
                    if student_name:
                        students_found.add(student_name)
        
        print(f"🔍 SCAN: Encontrados estudantes com dados no Anki: {sorted(students_found)}")
        
    except Exception as e:
        print(f"⚠️ SCAN: Erro ao escanear dados do Anki: {e}")
    
    return students_found


def _handle_consolidated_confirmation_cleanup(remote_decks):
    """
    Mostra uma única confirmação para ambos os tipos de limpeza e executa ambos se confirmado.
    NOVA VERSÃO: Usa normalização consistente de nomes.
    
    Returns:
        tuple: (missing_cleanup_result, cleanup_result)
    """
    from .config_manager import get_global_student_config
    from .student_manager import (
        cleanup_missing_students_data,
        cleanup_disabled_students_data
    )
    
    # OBTER ALUNOS DESABILITADOS usando normalização consistente
    config = get_global_student_config()
    current_enabled_raw = config.get("enabled_students", [])
    available_students = config.get("available_students", [])
    
    # Estudantes atualmente habilitados (case-sensitive)
    current_enabled_set = {student for student in current_enabled_raw if student and student.strip()}
    
    # MÚLTIPLAS FONTES para detectar alunos anteriormente habilitados
    previous_enabled_raw = set()
    previous_enabled_raw.update(_get_students_from_existing_note_types(remote_decks))
    previous_enabled_raw.update(available_students)
    
    # Adicionar dados do Anki
    if mw and hasattr(mw, 'col') and mw.col:
        anki_students = _get_students_from_anki_data()
        previous_enabled_raw.update(anki_students)
    
    # Processar previous_enabled (case-sensitive)
    previous_enabled_set = {student for student in previous_enabled_raw if student and student.strip()}
    
    # CALCULAR desabilitados (case-sensitive)
    disabled_students_set = previous_enabled_set - current_enabled_set
    
    deck_names = [deck_info.get('remote_deck_name', '') for deck_info in remote_decks.values()]
    deck_names = [name for name in deck_names if name]
    
    # Criar mensagem consolidada
    students_list = '\n'.join([f"• {student}" for student in sorted(disabled_students_set)])
    
    message = (
        f"⚠️ ATENÇÃO: REMOÇÃO PERMANENTE DE DADOS ⚠️\n\n"
        f"Foram detectadas alterações que requerem limpeza de dados:\n\n"
        f"🗑️ DADOS QUE SERÃO DELETADOS PERMANENTEMENTE:\n\n"
        f"📚 ALUNOS DESABILITADOS ({len(disabled_students_set)}):\n{students_list}\n"
        f"• Todas as notas dos alunos\n"
        f"• Todos os cards dos alunos\n"
        f"• Todos os decks dos alunos\n"
        f"• Todos os note types dos alunos\n\n"
        f"📝 NOTAS SEM ALUNOS ESPECÍFICOS ([MISSING A.]):\n"
        f"• Todas as notas em subdecks [MISSING A.]\n"
        f"• Todos os subdecks [MISSING A.] e seus conteúdos\n"
        f"• Note types específicos para [MISSING A.]\n\n"
        f"❌ ESTA AÇÃO É IRREVERSÍVEL!\n\n"
        f"Deseja continuar com a remoção de todos os dados?"
    )
    
    # Criar MessageBox consolidado
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Warning)
    msg_box.setWindowTitle("Confirmar Remoção Permanente - Múltiplas Limpezas")
    msg_box.setText(message)
    msg_box.setStandardButtons(MessageBox_Yes | MessageBox_No)
    msg_box.setDefaultButton(MessageBox_No)  # Default é NOT remover
    
    # Customizar botões
    yes_btn = msg_box.button(MessageBox_Yes)
    no_btn = msg_box.button(MessageBox_No)
    
    if yes_btn:
        yes_btn.setText("🗑️ SIM, DELETAR TODOS OS DADOS")
        yes_btn.setStyleSheet("QPushButton { background-color: #d73027; color: white; font-weight: bold; }")
    
    if no_btn:
        no_btn.setText("🛡️ NÃO, MANTER DADOS")
        no_btn.setStyleSheet("QPushButton { background-color: #4575b4; color: white; font-weight: bold; }")
    
    # Executar diálogo
    from .compat import safe_exec_dialog
    result = safe_exec_dialog(msg_box)
    confirmed = result == MessageBox_Yes
    
    if confirmed:
        print(f"🧹 CLEANUP: Usuário confirmou limpeza consolidada")
        print(f"🧹 CLEANUP: Alunos desabilitados: {sorted(disabled_students_set)}")
        
        # Executar ambas as limpezas
        cleanup_missing_students_data(deck_names)
        cleanup_disabled_students_data(disabled_students_set, deck_names)
        
        # Retornar resultados
        missing_result = {
            'missing_cleanup_count': 1,
            'missing_cleanup_message': 'Dados [MISSING A.] removidos'
        }
        
        cleanup_result = {
            'disabled_students_count': len(disabled_students_set),
            'disabled_students_names': ', '.join(sorted(disabled_students_set))
        }
        
        print(f"✅ CLEANUP: Limpeza consolidada concluída")
        return missing_result, cleanup_result
    else:
        print(f"🛡️ CLEANUP: Usuário cancelou limpeza consolidada, dados preservados")
        return None, None


def _handle_missing_students_cleanup(remote_decks):
    """
    Gerencia a limpeza de dados de notas [MISSING A.] quando a funcionalidade for desativada.
    
    Esta função:
    1. Verifica se a sincronização de notas sem alunos foi desativada
    2. Mostra confirmação de segurança
    3. Remove dados [MISSING A.] se confirmado
    
    Args:
        remote_decks (dict): Dicionário de decks remotos configurados
        
    Returns:
        dict: Estatísticas de limpeza ou None se não houve limpeza
    """
    from .config_manager import is_sync_missing_students_notes
    from .student_manager import (
        cleanup_missing_students_data,
        show_missing_cleanup_confirmation_dialog
    )
    
    # Se a funcionalidade está ativada, não fazer nada
    if is_sync_missing_students_notes():
        return None  # Funcionalidade ativada, nada a limpar
    
    # Funcionalidade desativada - verificar se há dados [MISSING A.] para remover
    print(f"🔍 CLEANUP: Sync [MISSING A.] está DESATIVADA, verificando dados para limpeza...")
    
    # Verificar se existem decks ou note types [MISSING A.]
    if not _is_anki_ready():
        return None
    
    assert mw.col is not None  # Type hint para o checker
    col = mw.col
    deck_names = [deck_info.get('remote_deck_name', '') for deck_info in remote_decks.values()]
    deck_names = [name for name in deck_names if name]  # Filtrar nomes vazios
    
    # Verificar se há dados [MISSING A.] existentes
    has_missing_data = False
    
    try:
        for deck_name in deck_names:
            # Verificar se há decks [MISSING A.]
            missing_deck_pattern = f"{deck_name}::[MISSING A.]::"
            all_decks = col.decks.all()
            for deck in all_decks:
                if deck.get("name", "").startswith(missing_deck_pattern):
                    has_missing_data = True
                    break
            
            if has_missing_data:
                break
            
            # Verificar se há note types [MISSING A.]
            note_types = col.models.all()
            for note_type in note_types:
                note_type_name = note_type.get('name', '')
                missing_pattern = f"Sheets2Anki - {deck_name} - [MISSING A.] -"
                if note_type_name.startswith(missing_pattern):
                    has_missing_data = True
                    break
            
            if has_missing_data:
                break
    
    except Exception as e:
        print(f"❌ CLEANUP: Erro ao verificar dados [MISSING A.]: {e}")
        return None
    
    if not has_missing_data:
        print(f"✅ CLEANUP: Nenhum dado [MISSING A.] encontrado para limpeza")
        return None
    
    print(f"⚠️ CLEANUP: Encontrados dados [MISSING A.] para limpeza")
    
    # Mostrar diálogo de confirmação
    if show_missing_cleanup_confirmation_dialog():
        # Usuário confirmou - executar limpeza
        print(f"🧹 CLEANUP: Iniciando limpeza [MISSING A.] para decks: {deck_names}")
        
        cleanup_missing_students_data(deck_names)
        
        # Log simples da limpeza concluída
        print(f"✅ CLEANUP: Limpeza [MISSING A.] concluída")
        return {
            'missing_cleanup_count': 1,
            'missing_cleanup_message': 'Dados [MISSING A.] removidos'
        }
    else:
        print(f"🛡️ CLEANUP: Usuário cancelou a limpeza [MISSING A.], dados preservados")
        return None


def _handle_disabled_students_cleanup(remote_decks):
    """
    Gerencia a limpeza de dados de alunos que foram desabilitados.
    
    Esta função:
    1. Verifica se a auto-remoção está ativada
    2. Identifica alunos que foram desabilitados
    3. Mostra confirmação de segurança
    4. Remove dados se confirmado
    
    Args:
        remote_decks (dict): Dicionário de decks remotos configurados
        
    Returns:
        dict: Estatísticas de limpeza ou None se não houve limpeza
    """
    from .config_manager import is_auto_remove_disabled_students, get_global_student_config
    from .student_manager import (
        get_disabled_students_for_cleanup,
        show_cleanup_confirmation_dialog,
        cleanup_disabled_students_data
    )
    
    # Verificar se a auto-remoção está ativada
    if not is_auto_remove_disabled_students():
        return None  # Auto-remoção desativada, nada a fazer
    
    print(f"🔍 CLEANUP: Auto-remoção está ATIVADA, verificando alunos desabilitados...")
    
    # Obter configuração atual
    config = get_global_student_config()
    current_enabled = set(config.get("enabled_students", []))
    
    # Incluir [MISSING A.] na lista se a funcionalidade estiver ativa
    # (isso evita que seja considerado como "removido" quando está apenas controlado por configuração)
    from .config_manager import is_sync_missing_students_notes
    if is_sync_missing_students_notes():
        current_enabled.add("[MISSING A.]")
        print(f"🔍 CLEANUP: [MISSING A.] incluído na lista atual (funcionalidade ativa)")
    else:
        print(f"🔍 CLEANUP: [MISSING A.] não incluído na lista atual (funcionalidade inativa)")
    
    # Para detectar alunos desabilitados, precisamos comparar com uma versão anterior
    # Como não temos histórico, vamos usar os note types existentes como referência
    previous_enabled = _get_students_from_existing_note_types(remote_decks)
    
    # Identificar alunos desabilitados
    disabled_students = get_disabled_students_for_cleanup(current_enabled, previous_enabled)
    
    if not disabled_students:
        print(f"✅ CLEANUP: Nenhum aluno desabilitado detectado")
        return None
    
    print(f"⚠️ CLEANUP: Detectados {len(disabled_students)} alunos desabilitados: {sorted(disabled_students)}")
    
    # Mostrar diálogo de confirmação
    if show_cleanup_confirmation_dialog(disabled_students):
        # Usuário confirmou - executar limpeza
        deck_names = [deck_info.get('remote_deck_name', '') for deck_info in remote_decks.values()]
        deck_names = [name for name in deck_names if name]  # Filtrar nomes vazios
        
        print(f"🧹 CLEANUP: Iniciando limpeza para decks: {deck_names}")
        
        cleanup_disabled_students_data(disabled_students, deck_names)
        
        # Log simples da limpeza concluída
        print(f"✅ CLEANUP: Limpeza concluída para {len(disabled_students)} alunos")
        return {
            'disabled_students_count': len(disabled_students),
            'disabled_students_names': ', '.join(sorted(disabled_students))
        }
    else:
        print(f"🛡️ CLEANUP: Usuário cancelou a limpeza, dados preservados")
        return None


def _get_students_from_existing_note_types(remote_decks):
    """
    Extrai lista de alunos a partir dos note types existentes.
    
    Usado para detectar alunos que existiam anteriormente mas foram desabilitados.
    
    Args:
        remote_decks (dict): Dicionário de decks remotos
        
    Returns:
        Set[str]: Conjunto de alunos encontrados nos note types existentes
    """
    if not _is_anki_ready():
        return set()
    
    assert mw.col is not None  # Type hint para o checker
    students = set()
    col = mw.col
    
    try:
        # Obter todos os note types
        note_types = col.models.all()
        
        # Extrair nomes de decks remotos para filtrar
        remote_deck_names = {deck_info.get('remote_deck_name', '') for deck_info in remote_decks.values()}
        remote_deck_names = {name for name in remote_deck_names if name}
        
        for note_type in note_types:
            note_type_name = note_type.get('name', '')
            
            # Verificar se é um note type do Sheets2Anki
            # Formato: "Sheets2Anki - {remote_deck_name} - {student} - {Basic|Cloze}"
            if note_type_name.startswith('Sheets2Anki - '):
                parts = note_type_name.split(' - ')
                if len(parts) >= 4:  # ['Sheets2Anki', '{deck_name}', '{student}', '{Basic|Cloze}']
                    deck_name = parts[1]
                    student = parts[2]
                    note_type_suffix = parts[3]
                    
                    # Verificar se é de um deck remoto conhecido e tem formato correto
                    if deck_name in remote_deck_names and note_type_suffix in ['Basic', 'Cloze']:
                        students.add(student)
                        print(f"🔍 CLEANUP: Encontrado aluno '{student}' no note type '{note_type_name}'")
        
        print(f"📋 CLEANUP: Alunos encontrados nos note types existentes: {sorted(students)}")
        return students
        
    except Exception as e:
        print(f"❌ CLEANUP: Erro ao extrair alunos dos note types: {e}")
        return set()