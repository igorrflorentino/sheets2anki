"""
Funções de sincronização principal para o addon Sheets2Anki.

Este módulo contém as funções centrais para sincronização
de decks com fontes remotas, usando o novo sistema de configuração.
Inclui também classes para gerenciamento de estatísticas e finalização.
"""

import time
import traceback
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from .compat import AlignLeft
from .compat import AlignTop
from .compat import MessageBox_No
from .compat import MessageBox_Yes
from .compat import QDialog
from .compat import QGroupBox
from .compat import QLabel
from .compat import QMessageBox
from .compat import QProgressDialog
from .compat import QPushButton
from .compat import QTextEdit
from .compat import QVBoxLayout
from .compat import mw
from .compat import safe_exec_dialog
from .compat import showInfo
from .config_manager import get_deck_local_name
from .config_manager import get_remote_decks
from .config_manager import save_remote_decks
from .config_manager import sync_note_type_names_robustly
from .config_manager import update_note_type_names_in_meta
from .data_processor import create_or_update_notes
from .data_processor import getRemoteDeck
from .student_manager import get_selected_students_for_deck
from .templates_and_definitions import update_existing_note_type_templates
from .utils import SyncError
from .utils import add_debug_message
from .utils import capture_deck_note_type_ids
from .utils import clear_debug_messages
from .utils import get_publication_key_hash
from .utils import remove_empty_subdecks
from .utils import validate_url
from .name_consistency_manager import NameConsistencyManager

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
    unchanged: int = 0
    skipped: int = 0

    # Métricas detalhadas do deck remoto - REFATORADAS
    # 1. Total de linhas da tabela (independente de preenchimento)
    remote_total_table_lines: int = 0

    # 2. Total de linhas com notas válidas (ID preenchido)
    remote_valid_note_lines: int = 0

    # 3. Total de linhas inválidas (ID vazio)
    remote_invalid_note_lines: int = 0

    # 4. Total de linhas marcadas para sincronizar (SYNC? = true)
    remote_sync_marked_lines: int = 0

    # 5. Total potencial de notas que serão criadas no Anki (ID × alunos + [MISSING A.])
    remote_total_potential_anki_notes: int = 0

    # 6. Total potencial de notas para alunos específicos
    remote_potential_student_notes: int = 0

    # 7. Total potencial de notas para [MISSING A.]
    remote_potential_missing_a_notes: int = 0

    # 8. Total de alunos únicos encontrados
    remote_unique_students_count: int = 0

    # 9. Total potencial de notas por aluno (detalhado)
    remote_notes_per_student: Dict[str, int] = field(default_factory=dict)

    error_details: List[str] = field(default_factory=list)
    # Campos para detalhes estruturados
    update_details: List[Dict[str, Any]] = field(default_factory=list)
    creation_details: List[Dict[str, Any]] = field(default_factory=list)
    deletion_details: List[Dict[str, Any]] = field(default_factory=list)

    def add_error(self, error_msg: str) -> None:
        """Adiciona um erro às estatísticas."""
        self.errors += 1
        self.error_details.append(error_msg)

    def add_update_detail_structured(self, detail: Dict[str, Any]) -> None:
        """Adiciona um detalhe estruturado de atualização."""
        self.update_details.append(detail)

    def add_creation_detail(self, detail: Dict[str, Any]) -> None:
        """Adiciona um detalhe de criação."""
        self.creation_details.append(detail)

    def add_deletion_detail(self, detail: Dict[str, Any]) -> None:
        """Adiciona um detalhe de exclusão."""
        self.deletion_details.append(detail)

    def merge(self, other: "SyncStats") -> None:
        """Merge com outras estatísticas."""
        self.created += other.created
        self.updated += other.updated
        self.deleted += other.deleted
        self.ignored += other.ignored
        self.errors += other.errors
        self.unchanged += other.unchanged
        self.skipped += other.skipped

        # Agregar métricas do deck remoto - REFATORADAS
        self.remote_total_table_lines += other.remote_total_table_lines
        self.remote_valid_note_lines += other.remote_valid_note_lines
        self.remote_invalid_note_lines += other.remote_invalid_note_lines
        self.remote_sync_marked_lines += other.remote_sync_marked_lines
        self.remote_total_potential_anki_notes += (
            other.remote_total_potential_anki_notes
        )
        self.remote_potential_student_notes += other.remote_potential_student_notes
        self.remote_potential_missing_a_notes += other.remote_potential_missing_a_notes
        self.remote_unique_students_count = max(
            self.remote_unique_students_count, other.remote_unique_students_count
        )

        # Merge dos dicionários de notas por aluno - SOMAR os valores
        for student, count in other.remote_notes_per_student.items():
            if student in self.remote_notes_per_student:
                # CORRIGI: Somar em vez de pegar o máximo para ter total agregado correto
                self.remote_notes_per_student[student] += count
            else:
                self.remote_notes_per_student[student] = count

        self.error_details.extend(other.error_details)
        self.update_details.extend(other.update_details)
        self.creation_details.extend(other.creation_details)
        self.deletion_details.extend(other.deletion_details)

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
@dataclass
class DeckSyncResult:
    """Resultado da sincronização de um deck específico."""

    deck_name: str
    deck_key: str
    deck_url: str
    success: bool
    stats: SyncStats
    was_new_deck: bool = False  # Se o deck era novo (nunca sincronizado)
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

    def create_deck_result(self, deck_name: str, deck_key: str, deck_url: str = "") -> DeckSyncResult:
        """Cria um novo resultado de deck."""
        return DeckSyncResult(
            deck_name=deck_name, deck_key=deck_key, deck_url=deck_url, success=False, stats=SyncStats()
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
            "total_decks": len(self.deck_results),
            "successful_decks": successful,
            "failed_decks": failed,
            "total_stats": self.total_stats,  # Retornar diretamente o objeto SyncStats
            "has_changes": self.total_stats.has_changes(),
            "has_errors": self.total_stats.has_errors(),
        }

    def reset(self) -> None:
        """Reseta todas as estatísticas."""
        self.total_stats = SyncStats()
        self.deck_results.clear()


# ========================================================================================
# FUNÇÕES DE FINALIZAÇÃO DE SINCRONIZAÇÃO (consolidado de sync_finalization.py)
# ========================================================================================


def _finalize_sync_new(
    progress,
    total_decks,
    successful_decks,
    total_stats,
    sync_errors,
    cleanup_result=None,
    missing_cleanup_result=None,
    deck_results=None,
    new_deck_mode=False,
):
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
        deck_results: Lista de DeckSyncResult para visualização por deck (opcional)

    Returns:
        Resultado consolidado da sincronização
    """

    add_debug_message("🎯 _finalize_sync_new INICIADO", "SYNC")

    progress.setLabelText("Limpando subdecks vazios...")
    from .config_manager import get_remote_decks

    # Remover subdecks vazios
    remote_decks = get_remote_decks()
    removed_subdecks = remove_empty_subdecks(remote_decks)

    add_debug_message(
        "🔧 Prestes a chamar apply_automatic_deck_options_system()", "SYNC"
    )
    # Aplicar sistema automático de opções de deck
    from .utils import apply_automatic_deck_options_system

    options_result = apply_automatic_deck_options_system()
    add_debug_message(
        f"✅ apply_automatic_deck_options_system() retornou: {options_result}", "SYNC"
    )

    # Preparar mensagem final para exibir na barra de progresso
    cleanup_info = ""
    if cleanup_result:
        cleanup_info = f", {cleanup_result['disabled_students_count']} alunos removidos"

    if missing_cleanup_result:
        if cleanup_info:
            cleanup_info += ", dados [MISSING A.] removidos"
        else:
            cleanup_info = ", dados [MISSING A.] removidos"

    # Gerar mensagem final baseada nas estatísticas
    if sync_errors or total_stats.errors > 0:
        final_msg = f"Concluído com problemas: {successful_decks}/{total_decks} decks sincronizados"
        if total_stats.created > 0:
            final_msg += f", {total_stats.created} notas criadas"
        if total_stats.updated > 0:
            final_msg += f", {total_stats.updated} atualizadas"
        if total_stats.deleted > 0:
            final_msg += f", {total_stats.deleted} deletadas"
        if total_stats.ignored > 0:
            final_msg += f", {total_stats.ignored} ignoradas"
        if removed_subdecks > 0:
            final_msg += f", {removed_subdecks} subdecks vazios removidos"
        if cleanup_info:
            final_msg += cleanup_info
        final_msg += f", {total_stats.errors + len(sync_errors)} erros"
    else:
        final_msg = "Sincronização concluída com sucesso!"
        if total_stats.created > 0:
            final_msg += f" {total_stats.created} notas criadas"
        if total_stats.updated > 0:
            final_msg += f", {total_stats.updated} atualizadas"
        if total_stats.deleted > 0:
            final_msg += f", {total_stats.deleted} deletadas"
        if total_stats.ignored > 0:
            final_msg += f", {total_stats.ignored} ignoradas"
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
    time.sleep(1)

    # Mostrar resumo detalhado PRIMEIRO (sem resultado AnkiWeb ainda)
    def execute_ankiweb_sync_after_close():
        """Callback para executar sincronização AnkiWeb após o usuário fechar a janela de resumo"""
        # APÓS o usuário fechar a janela, executar sincronização AnkiWeb se configurada
        add_debug_message(
            "🔄 Verificando configuração de sincronização AnkiWeb...", "SYNC"
        )
        try:
            from .ankiweb_sync import execute_ankiweb_sync_if_configured

            ankiweb_result = execute_ankiweb_sync_if_configured()

            if ankiweb_result:
                if ankiweb_result["success"]:
                    add_debug_message(
                        f"✅ AnkiWeb sync: {ankiweb_result['message']}", "SYNC"
                    )
                else:
                    add_debug_message(
                        f"❌ AnkiWeb sync falhou: {ankiweb_result['error']}", "SYNC"
                    )
            else:
                add_debug_message("⏹️ AnkiWeb sync desabilitado", "SYNC")
        except Exception as ankiweb_error:
            add_debug_message(
                f"❌ Erro na sincronização AnkiWeb: {ankiweb_error}", "SYNC"
            )

    _show_sync_summary_new(
        sync_errors,
        total_stats,
        successful_decks,
        total_decks,
        removed_subdecks,
        cleanup_result,
        missing_cleanup_result,
        ankiweb_result=None,
        on_close_callback=execute_ankiweb_sync_after_close,
        deck_results=deck_results,
        new_deck_mode=new_deck_mode,
    )


def _show_sync_summary_new(
    sync_errors,
    total_stats,
    decks_synced,
    total_decks,
    removed_subdecks=0,
    cleanup_result=None,
    missing_cleanup_result=None,
    ankiweb_result=None,
    on_close_callback=None,
    deck_results=None,
    new_deck_mode=False,
):
    """
    Mostra resumo da sincronização usando interface com scroll.

    Args:
        on_close_callback (callable, optional): Função a ser chamada quando o diálogo for fechado
        deck_results (list, optional): Lista de DeckSyncResult para visualização por deck
    """

    summary = []

    # Estatísticas principais
    if sync_errors or total_stats.errors > 0:
        summary.append("❌ Sincronização concluída com problemas!")
        summary.append(
            f"📊 Decks: {decks_synced}/{total_decks} sincronizados com sucesso"
        )
    else:
        summary.append("✅ Sincronização concluída com sucesso!")
        summary.append(f"📊 Decks: {decks_synced}/{total_decks} sincronizados")

    # Estatísticas resumidas no cabeçalho
    if total_stats.created > 0:
        # Verificar se algum dos decks era novo (baseado na detecção robusta por last_sync)
        new_decks_detected = False
        if deck_results:
            new_decks_detected = any(result.was_new_deck for result in deck_results if result.success)
        
        if new_decks_detected:
            if total_decks == 1:
                summary.append(f"➕ {total_stats.created} notas criadas (novo deck adicionado)")
            else:
                summary.append(f"➕ {total_stats.created} notas criadas (inclui novos decks)")
        else:
            summary.append(f"➕ {total_stats.created} notas criadas")

    if total_stats.updated > 0:
        summary.append(f"✏️ {total_stats.updated} notas atualizadas")

    if total_stats.deleted > 0:
        summary.append(f"🗑️ {total_stats.deleted} notas deletadas")

    if total_stats.ignored > 0:
        summary.append(f"⏭️ {total_stats.ignored} notas ignoradas")

    # Limpezas
    if removed_subdecks > 0:
        summary.append(f"🧹 {removed_subdecks} subdecks vazios removidos")

    if cleanup_result and cleanup_result.get("disabled_students_count", 0) > 0:
        summary.append(
            f"🧹 {cleanup_result['disabled_students_count']} alunos desabilitados removidos"
        )

    if missing_cleanup_result:
        summary.append("🧹 Dados [MISSING A.] removidos")

    # Sincronização AnkiWeb
    if ankiweb_result is not None:
        if ankiweb_result.get("success", False):
            summary.append(
                "🔄 AnkiWeb: Sincronização iniciada (detectando mudanças automaticamente)"
            )
        elif "error" in ankiweb_result:
            summary.append(
                f"❌ AnkiWeb: Falha na sincronização - {ankiweb_result['error']}"
            )
    else:
        # Verificar se está configurado mas não executou
        try:
            from .config_manager import get_ankiweb_sync_mode

            sync_mode = get_ankiweb_sync_mode()
            if sync_mode == "disabled":
                summary.append("⏹️ AnkiWeb: Sincronização automática desabilitada")
        except:
            pass

    # Erros
    sync_errors = sync_errors or []
    total_errors = total_stats.errors + len(sync_errors)
    if total_errors > 0:
        summary.append(f"⚠️ {total_errors} erros encontrados")

    # Sempre usar interface com scroll
    _show_sync_summary_with_scroll(
        summary,
        total_stats,
        removed_subdecks,
        cleanup_result,
        missing_cleanup_result,
        sync_errors,
        ankiweb_result,
        on_close_callback,
        deck_results,
    )


def generate_simplified_view(total_stats, sync_errors=None, deck_results=None):
    """
    Gera visualização simplificada (agregada) das estatísticas de sincronização.
    
    Args:
        total_stats: Estatísticas totais agregadas
        sync_errors: Lista de erros de sincronização
        deck_results: Lista de resultados por deck (não usado no modo simplificado)
    
    Returns:
        list: Lista de strings para exibição
    """
    details_content = []

    # PRIMEIRO: Métricas detalhadas do deck remoto (agregadas)
    if (
        total_stats.remote_total_table_lines > 0
        or total_stats.remote_valid_note_lines > 0
        or total_stats.remote_sync_marked_lines > 0
        or total_stats.remote_total_potential_anki_notes > 0
    ):
        details_content.append("📊 MÉTRICAS DETALHADAS DOS DECKS REMOTOS:")
        details_content.append("=" * 60)
        details_content.append(
            f"📋 1. Total de linhas na tabela: {total_stats.remote_total_table_lines}"
        )
        details_content.append(
            f"✅ 2. Linhas com notas válidas (ID preenchido): {total_stats.remote_valid_note_lines}"
        )
        details_content.append(
            f"❌ 3. Linhas inválidas (ID vazio): {total_stats.remote_invalid_note_lines}"
        )
        details_content.append(
            f"🔄 4. Linhas marcadas para sincronização: {total_stats.remote_sync_marked_lines}"
        )
        details_content.append(
            f"📝 5. Total potencial de notas no Anki: {total_stats.remote_total_potential_anki_notes}"
        )
        details_content.append(
            f"🎓 6. Potencial de notas para alunos específicos: {total_stats.remote_potential_student_notes}"
        )
        details_content.append(
            f"❓ 7. Potencial de notas para [MISSING A.]: {total_stats.remote_potential_missing_a_notes}"
        )
        details_content.append(
            f"👥 8. Total de alunos únicos: {total_stats.remote_unique_students_count}"
        )

        # 9. Mostrar notas por aluno individual
        if total_stats.remote_notes_per_student:
            details_content.append("📊 9. Notas por aluno (totais agregados):")
            for student, count in sorted(total_stats.remote_notes_per_student.items()):
                details_content.append(f"   • {student}: {count} notas")

        details_content.append("")

    # SEGUNDO: Erros detalhados (se houver)
    if sync_errors or total_stats.error_details:
        total_errors = total_stats.errors + len(sync_errors or [])
        if total_errors > 0:
            details_content.append(f"⚠️ DETALHES DOS {total_errors} ERROS:")
            details_content.append("=" * 60)
            error_count = 1
            for error in sync_errors or []:
                details_content.append(f"{error_count:4d}. {error}")
                error_count += 1
            for error in total_stats.error_details:
                details_content.append(f"{error_count:4d}. {error}")
                error_count += 1
            details_content.append("")

    # POR ÚLTIMO: Detalhes das notas criadas
    if total_stats.created > 0 and total_stats.creation_details:
        details_content.append(f"➕ DETALHES DAS {total_stats.created} NOTAS CRIADAS:")
        details_content.append("=" * 60)
        for i, detail in enumerate(total_stats.creation_details, 1):
            details_content.append(
                f"{i:4d}. {detail['student']}: {detail['note_id']} - {detail['pergunta']}"
            )
        details_content.append("")

    # POR ÚLTIMO: Detalhes das notas atualizadas
    if total_stats.updated > 0 and total_stats.update_details:
        details_content.append(
            f"✏️ DETALHES DAS {total_stats.updated} NOTAS ATUALIZADAS:"
        )
        details_content.append("=" * 60)
        for i, detail in enumerate(total_stats.update_details, 1):
            details_content.append(f"{i:4d}. {detail['student']}: {detail['note_id']}")
            for j, change in enumerate(detail["changes"], 1):
                details_content.append(f"      {j:2d}. {change}")
            details_content.append("")

    # POR ÚLTIMO: Detalhes das notas removidas
    if total_stats.deleted > 0 and total_stats.deletion_details:
        details_content.append(f"🗑️ DETALHES DAS {total_stats.deleted} NOTAS REMOVIDAS:")
        details_content.append("=" * 60)
        for i, detail in enumerate(total_stats.deletion_details, 1):
            details_content.append(
                f"{i:4d}. {detail['student']}: {detail['note_id']} - {detail['pergunta']}"
            )
        details_content.append("")

    # Se não há detalhes de modificações, mostrar mensagem informativa
    if not any(
        [
            total_stats.created > 0 and total_stats.creation_details,
            total_stats.updated > 0 and total_stats.update_details,
            total_stats.deleted > 0 and total_stats.deletion_details,
            sync_errors or total_stats.error_details,
        ]
    ):
        details_content.append(
            "ℹ️ Nenhuma modificação detalhada de notas foi registrada nesta sincronização."
        )
        details_content.append("")
        details_content.append("Isso pode acontecer quando:")
        details_content.append("• As notas já estavam atualizadas")
        details_content.append("• Apenas operações de limpeza foram realizadas")
        details_content.append("• Não houve alterações nos dados das planilhas")

    return details_content


def generate_aggregated_summary_only(total_stats, sync_errors=None):
    """
    Gera apenas o resumo agregado sem detalhes de notas individuais.
    Usado no modo detalhado para evitar duplicação.
    
    Args:
        total_stats: Estatísticas totais agregadas
        sync_errors: Lista de erros de sincronização
    
    Returns:
        list: Lista de strings para exibição
    """
    details_content = []

    # Erros detalhados (se houver)
    if sync_errors or total_stats.error_details:
        total_errors = total_stats.errors + len(sync_errors or [])
        if total_errors > 0:
            details_content.append(f"⚠️ DETALHES DOS {total_errors} ERROS GERAIS:")
            details_content.append("=" * 60)
            error_count = 1
            for error in sync_errors or []:
                details_content.append(f"{error_count:4d}. {error}")
                error_count += 1
            for error in total_stats.error_details:
                details_content.append(f"{error_count:4d}. {error}")
                error_count += 1
            details_content.append("")

    # Métricas detalhadas do deck remoto (agregadas) - apenas se não foram mostradas por deck
    if (
        total_stats.remote_total_table_lines > 0
        or total_stats.remote_valid_note_lines > 0
        or total_stats.remote_sync_marked_lines > 0
        or total_stats.remote_total_potential_anki_notes > 0
    ):
        details_content.append("📊 TOTAIS AGREGADOS DE MÉTRICAS REMOTAS:")
        details_content.append("=" * 60)
        details_content.append(
            f"📋 1. Total de linhas na tabela: {total_stats.remote_total_table_lines}"
        )
        details_content.append(
            f"✅ 2. Linhas com notas válidas (ID preenchido): {total_stats.remote_valid_note_lines}"
        )
        details_content.append(
            f"❌ 3. Linhas inválidas (ID vazio): {total_stats.remote_invalid_note_lines}"
        )
        details_content.append(
            f"🔄 4. Linhas marcadas para sincronização: {total_stats.remote_sync_marked_lines}"
        )
        details_content.append(
            f"📝 5. Total potencial de notas no Anki: {total_stats.remote_total_potential_anki_notes}"
        )
        details_content.append(
            f"🎓 6. Potencial de notas para alunos específicos: {total_stats.remote_potential_student_notes}"
        )
        details_content.append(
            f"❓ 7. Potencial de notas para [MISSING A.]: {total_stats.remote_potential_missing_a_notes}"
        )
        details_content.append(
            f"👥 8. Total de alunos únicos: {total_stats.remote_unique_students_count}"
        )

        # 9. Mostrar notas por aluno individual
        if total_stats.remote_notes_per_student:
            details_content.append("📊 9. Notas por aluno (totais agregados):")
            for student, count in sorted(total_stats.remote_notes_per_student.items()):
                details_content.append(f"   • {student}: {count} notas")

        details_content.append("")

    return details_content


def generate_deck_detailed_metrics(stats, deck_name):
    """
    Gera métricas detalhadas completas para um deck individual.
    
    Args:
        stats: Estatísticas do deck individual (SyncStats)
        deck_name: Nome do deck
    
    Returns:
        list: Lista de strings com as métricas detalhadas
    """
    metrics_content = []
    
    # Estatísticas básicas de modificações
    modifications = []
    if stats.created > 0:
        modifications.append(f"{stats.created} criadas")
    if stats.updated > 0:
        modifications.append(f"{stats.updated} atualizadas")
    if stats.deleted > 0:
        modifications.append(f"{stats.deleted} deletadas")
    if stats.ignored > 0:
        modifications.append(f"{stats.ignored} ignoradas")
    if stats.unchanged > 0:
        modifications.append(f"{stats.unchanged} inalteradas")
    if stats.skipped > 0:
        modifications.append(f"{stats.skipped} puladas")
    if stats.errors > 0:
        modifications.append(f"{stats.errors} erros")
    
    if modifications:
        metrics_content.append(f"     📝 Notas: {', '.join(modifications)}")
    
    # Todas as 9 métricas detalhadas do deck remoto (igual ao modo simplificado)
    if (
        stats.remote_total_table_lines > 0
        or stats.remote_valid_note_lines > 0
        or stats.remote_sync_marked_lines > 0
        or stats.remote_total_potential_anki_notes > 0
    ):
        metrics_content.append(f"     📊 Métricas da Planilha Remota:")
        metrics_content.append(f"        📋 1. Total de linhas na tabela: {stats.remote_total_table_lines}")
        metrics_content.append(f"        ✅ 2. Linhas com notas válidas (ID preenchido): {stats.remote_valid_note_lines}")
        metrics_content.append(f"        ❌ 3. Linhas inválidas (ID vazio): {stats.remote_invalid_note_lines}")
        metrics_content.append(f"        🔄 4. Linhas marcadas para sincronização: {stats.remote_sync_marked_lines}")
        metrics_content.append(f"        📝 5. Total potencial de notas no Anki: {stats.remote_total_potential_anki_notes}")
        metrics_content.append(f"        🎓 6. Potencial de notas para alunos específicos: {stats.remote_potential_student_notes}")
        metrics_content.append(f"        ❓ 7. Potencial de notas para [MISSING A.]: {stats.remote_potential_missing_a_notes}")
        metrics_content.append(f"        👥 8. Total de alunos únicos: {stats.remote_unique_students_count}")
        
        # 9. Mostrar notas por aluno individual para este deck
        if stats.remote_notes_per_student:
            metrics_content.append(f"        📊 9. Notas por aluno neste deck:")
            for student, count in sorted(stats.remote_notes_per_student.items()):
                metrics_content.append(f"           • {student}: {count} notas")
    
    # DETALHES DAS NOTAS APÓS AS MÉTRICAS REMOTAS (individualizado por deck)
    
    # Detalhes das notas criadas neste deck
    if stats.created > 0 and stats.creation_details:
        metrics_content.append(f"     ➕ DETALHES DAS {stats.created} NOTAS CRIADAS:")
        for i, detail in enumerate(stats.creation_details, 1):
            metrics_content.append(f"        {i:2d}. {detail['student']}: {detail['note_id']} - {detail['pergunta']}")
    
    # Detalhes das notas atualizadas neste deck
    if stats.updated > 0 and stats.update_details:
        metrics_content.append(f"     ✏️ DETALHES DAS {stats.updated} NOTAS ATUALIZADAS:")
        for i, detail in enumerate(stats.update_details, 1):
            metrics_content.append(f"        {i:2d}. {detail['student']}: {detail['note_id']}")
            for j, change in enumerate(detail["changes"], 1):
                metrics_content.append(f"           {j:2d}. {change}")
    
    # Detalhes das notas removidas neste deck
    if stats.deleted > 0 and stats.deletion_details:
        metrics_content.append(f"     🗑️ DETALHES DAS {stats.deleted} NOTAS REMOVIDAS:")
        for i, detail in enumerate(stats.deletion_details, 1):
            metrics_content.append(f"        {i:2d}. {detail['student']}: {detail['note_id']} - {detail['pergunta']}")
    
    return metrics_content


def generate_detailed_view(total_stats, sync_errors=None, deck_results=None):
    """
    Gera visualização detalhada (por deck) das estatísticas de sincronização.
    
    Args:
        total_stats: Estatísticas totais agregadas
        sync_errors: Lista de erros de sincronização
        deck_results: Lista de resultados por deck individual
    
    Returns:
        list: Lista de strings para exibição
    """
    details_content = []

    # PRIMEIRO: Mostrar resumo geral agregado
    aggregated_summary = generate_aggregated_summary_only(total_stats, sync_errors)
    
    if aggregated_summary:
        details_content.append("📋 RESUMO GERAL AGREGADO:")
        details_content.append("=" * 80)
        details_content.append("\n")
        details_content.extend(aggregated_summary)
        details_content.append("")

    # SEGUNDO: Mostrar resumo por deck individual (com detalhes das notas individualizados)
    if deck_results and len(deck_results) >= 1:
        details_content.append("📊 RESUMO POR DECK INDIVIDUAL:")
        details_content.append("=" * 80)
        
        for i, deck_result in enumerate(deck_results, 1):
            deck_name = deck_result.deck_name
            stats = deck_result.stats
            success_status = "✅" if deck_result.success else "❌"
            
            # Indicar se o deck era novo durante esta sincronização
            new_deck_indicator = " (NOVO DECK)" if deck_result.was_new_deck else ""
            
            details_content.append(f"{i:2d}. {success_status} {deck_name}{new_deck_indicator}")
            
            # Gerar todas as métricas detalhadas para este deck (inclui detalhes das notas)
            deck_metrics = generate_deck_detailed_metrics(stats, deck_name)
            details_content.extend(deck_metrics)
            
            # Se houver erro específico do deck, mostrar
            if not deck_result.success and hasattr(deck_result, 'error_message') and deck_result.error_message:
                details_content.append(f"     ❌ Erro: {deck_result.error_message}")
            
            details_content.append("")
        
        details_content.append("=" * 80)
    
    return details_content


def _show_sync_summary_with_scroll(
    base_summary,
    total_stats,
    removed_subdecks=0,
    cleanup_result=None,
    missing_cleanup_result=None,
    sync_errors=None,
    ankiweb_result=None,
    on_close_callback=None,
    deck_results=None,
):
    """
    Mostra resumo da sincronização com interface scrollável.

    Args:
        on_close_callback (callable, optional): Função a ser chamada quando o diálogo for fechado
        deck_results (list, optional): Lista de DeckSyncResult para visualização por deck
    """
    from .compat import Palette_Window
    from .compat import QButtonGroup
    from .compat import QRadioButton
    from .compat import QHBoxLayout

    # Criar dialog customizado
    dialog = QDialog()
    dialog.setWindowTitle("Resumo da Sincronização")
    dialog.setMinimumSize(800, 600)
    dialog.resize(1000, 700)

    # Conectar callback ao fechamento se fornecido
    if on_close_callback and callable(on_close_callback):
        dialog.finished.connect(on_close_callback)

    # Detectar dark mode baseado na cor de fundo padrão do sistema
    palette = dialog.palette()
    bg_color = palette.color(Palette_Window)
    is_dark_mode = bg_color.lightness() < 128

    # Aplicar estilo geral do dialog baseado no tema
    if is_dark_mode:
        dialog.setStyleSheet(
            """
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }
        """
        )
    else:
        dialog.setStyleSheet(
            """
            QDialog {
                background-color: #ffffff;
                color: #000000;
            }
        """
        )

    layout = QVBoxLayout()

    # Cabeçalho com informações principais
    header_text = "\n".join(base_summary)
    header_label = QLabel(header_text)

    # Estilos adaptáveis para dark mode
    header_style = """
        QLabel {
            font-weight: bold; 
            padding: 15px; 
            border-radius: 8px;
            margin-bottom: 5px;
        }
    """

    if is_dark_mode:
        header_style += """
            background-color: #3a3a3a;
            color: #ffffff;
            border: 1px solid #555555;
        """
    else:
        header_style += """
            background-color: #f0f0f0;
            color: #000000;
            border: 1px solid #cccccc;
        """

    header_label.setStyleSheet(header_style)
    layout.addWidget(header_label)

    # Seção de radiobuttons para escolher o formato de exibição
    view_group_box = QGroupBox("Formato de Exibição")
    view_layout = QHBoxLayout()
    
    # Radiobuttons
    simplified_radio = QRadioButton("Simplificado")
    detailed_radio = QRadioButton("Completo")
    
    # Sempre mostrar simplificado por padrão (como solicitado pelo usuário)
    simplified_radio.setChecked(True)
    
    # Agrupar radiobuttons
    radio_group = QButtonGroup()
    radio_group.addButton(simplified_radio)
    radio_group.addButton(detailed_radio)
    
    view_layout.addWidget(simplified_radio)
    view_layout.addWidget(detailed_radio)
    view_group_box.setLayout(view_layout)
    layout.addWidget(view_group_box)

    # Área de texto com scroll para detalhes
    details_text = QTextEdit()
    details_text.setReadOnly(True)

    def update_details_view():
        """Atualiza a visualização dos detalhes baseado na seleção do radiobutton."""
        details_content = []
        
        if simplified_radio.isChecked():
            # Modo Simplificado - mostra dados agregados
            details_content = generate_simplified_view(
                total_stats, sync_errors, deck_results
            )
        else:
            # Modo Completo - mostra dados por deck individual
            details_content = generate_detailed_view(
                total_stats, sync_errors, deck_results
            )
        
        details_text.setPlainText("\n".join(details_content))

    # Conectar mudanças de radiobutton à atualização da view
    simplified_radio.toggled.connect(update_details_view)
    detailed_radio.toggled.connect(update_details_view)

    # Definir conteúdo inicial (simplificado)
    update_details_view()

    # Estilos adaptáveis para a área de texto
    text_style = """
        QTextEdit {
            font-family: 'Monaco', 'Consolas', 'Courier New', monospace; 
            font-size: 11pt; 
            padding: 15px;
            border-radius: 5px;
            border: 1px solid;
        }
    """

    if is_dark_mode:
        text_style += """
            background-color: #2b2b2b;
            color: #ffffff;
            border-color: #555555;
            selection-background-color: #404040;
        """
    else:
        text_style += """
            background-color: #ffffff;
            color: #000000;
            border-color: #cccccc;
            selection-background-color: #b3d7ff;
        """

    details_text.setStyleSheet(text_style)
    layout.addWidget(details_text)

    # Botão para fechar adaptável ao dark mode
    close_button = QPushButton("Fechar")

    button_style = """
        QPushButton {
            padding: 12px 25px; 
            font-size: 12pt; 
            font-weight: bold;
            border-radius: 6px;
            border: 2px solid;
            margin-top: 10px;
        }
        QPushButton:hover {
            border-width: 3px;
        }
        QPushButton:pressed {
            padding: 13px 24px 11px 26px;
        }
    """

    if is_dark_mode:
        button_style += """
            background-color: #4a4a4a;
            color: #ffffff;
            border-color: #666666;
        }
        QPushButton:hover {
            background-color: #5a5a5a;
            border-color: #777777;
        }
        QPushButton:pressed {
            background-color: #3a3a3a;
        """
    else:
        button_style += """
            background-color: #f0f0f0;
            color: #000000;
            border-color: #cccccc;
        }
        QPushButton:hover {
            background-color: #e0e0e0;
            border-color: #999999;
        }
        QPushButton:pressed {
            background-color: #d0d0d0;
        """

    close_button.setStyleSheet(button_style)
    close_button.clicked.connect(dialog.accept)
    layout.addWidget(close_button)

    dialog.setLayout(layout)
    safe_exec_dialog(dialog)


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
        add_debug_message(
            "❌ MainWindow não disponível para atualização", "INTERFACE_UPDATE"
        )
        return

    try:
        add_debug_message(
            "🔄 Iniciando atualização da interface do Anki", "INTERFACE_UPDATE"
        )

        # 1. Atualizar a lista de decks na tela principal
        if hasattr(mw, "deckBrowser") and mw.deckBrowser:
            add_debug_message("📂 Atualizando lista de decks", "INTERFACE_UPDATE")
            mw.deckBrowser.refresh()

        # 2. Atualizar o reviewer se estiver ativo
        if hasattr(mw, "reviewer") and mw.reviewer and mw.state == "review":
            add_debug_message("📝 Atualizando reviewer", "INTERFACE_UPDATE")
            # Forçar recalculo do número de cards
            if hasattr(mw.reviewer, "_updateCounts"):
                mw.reviewer._updateCounts()

        # 3. Atualizar o browser se estiver aberto
        if hasattr(mw, "browser") and mw.browser:
            add_debug_message("🔍 Atualizando browser", "INTERFACE_UPDATE")
            mw.browser.model.reset()
            mw.browser.form.tableView.selectRow(0)

        # 4. Atualizar a barra de título e interface geral
        if hasattr(mw, "setWindowTitle") and mw.col:
            # Manter o título original mas forçar recalculo interno
            mw.col.reset()

        # 5. Trigger geral de reset da interface
        if hasattr(mw, "reset"):
            add_debug_message(
                "🔄 Executando reset geral da interface", "INTERFACE_UPDATE"
            )
            mw.reset()

        add_debug_message(
            "✅ Interface do Anki atualizada com sucesso", "INTERFACE_UPDATE"
        )

    except Exception as e:
        add_debug_message(f"❌ Erro ao atualizar interface: {e}", "INTERFACE_UPDATE")


def refresh_deck_list():
    """
    Atualiza especificamente a lista de decks na tela principal.
    """
    if not mw or not hasattr(mw, "deckBrowser"):
        return

    try:
        add_debug_message("📂 Atualizando lista de decks", "INTERFACE_UPDATE")
        mw.deckBrowser.refresh()
    except Exception as e:
        add_debug_message(
            f"❌ Erro ao atualizar lista de decks: {e}", "INTERFACE_UPDATE"
        )


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
        if hasattr(mw, "deckBrowser") and mw.deckBrowser:
            mw.deckBrowser.refresh()

        # Atualizar reviewer se ativo
        if hasattr(mw, "reviewer") and mw.reviewer and mw.state == "review":
            if hasattr(mw.reviewer, "_updateCounts"):
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
        add_debug_message(
            "🎯 Executando atualização completa da interface", "INTERFACE_UPDATE"
        )

        # Método 1: Reset da collection (mais completo)
        if mw.col:
            mw.col.reset()

        # Método 2: Reset da interface principal
        if hasattr(mw, "reset"):
            mw.reset()

        # Método 3: Atualização específica dos componentes
        refresh_deck_list()
        refresh_counts()

        add_debug_message(
            "✅ Atualização completa da interface concluída", "INTERFACE_UPDATE"
        )

    except Exception as e:
        add_debug_message(f"❌ Erro na atualização completa: {e}", "INTERFACE_UPDATE")


# ========================================================================================
# FUNÇÕES PRINCIPAIS DE SINCRONIZAÇÃO
# ========================================================================================


def _is_anki_ready():
    """Verifica se o Anki está pronto para operações."""
    return mw and hasattr(mw, "col") and mw.col


def _is_anki_decks_ready():
    """Verifica se o Anki está pronto para operações com decks."""
    return _is_anki_ready() and hasattr(mw.col, "decks")


def syncDecks(selected_deck_names=None, selected_deck_urls=None, new_deck_mode=False):
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
        new_deck_mode: Se True, indica que esta sincronização é para um deck recém-adicionado.
    """
    # Verificar se mw.col está disponível
    if not _is_anki_ready():
        showInfo("Anki não está pronto. Tente novamente em alguns instantes.")
        return

    col = mw.col
    remote_decks = get_remote_decks()

    # Limpar mensagens de debug anteriores
    clear_debug_messages()

    # **NOVO**: Atualizar templates de note types existentes antes da sincronização
    try:
        add_debug_message("🔄 Atualizando templates de note types existentes...", "SYNC")
        updated_count = update_existing_note_type_templates(col, [])
        add_debug_message(f"✅ {updated_count} note types atualizados com sucesso", "SYNC")
    except Exception as e:
        add_debug_message(f"⚠️ Erro ao atualizar templates: {e}", "SYNC")
        # Continuar a sincronização mesmo se houver erro na atualização dos templates

    # **NOVO**: Gerenciar limpezas de forma consolidada para evitar múltiplas confirmações
    missing_cleanup_result, cleanup_result = _handle_consolidated_cleanup(remote_decks)

    # Inicializar sistema de estatísticas
    stats_manager = SyncStatsManager()
    sync_errors = []
    status_msgs = []

    # Determinar quais decks sincronizar
    deck_keys = _get_deck_keys_to_sync(
        remote_decks, selected_deck_names, selected_deck_urls
    )
    total_decks = len(deck_keys)

    # Verificar se há decks para sincronizar
    if total_decks == 0:
        _show_no_decks_message(selected_deck_names)
        return

    # Configurar e mostrar barra de progresso
    progress = _setup_progress_dialog(total_decks)

    # Adicionar mensagem de debug inicial
    add_debug_message(
        f"🎬 SISTEMA DE DEBUG ATIVADO - Total de decks: {total_decks}", "SYNC"
    )
    _update_progress_text(progress, status_msgs)

    step = 0
    try:
        # Sincronizar cada deck
        for deckKey in deck_keys:
            try:
                step, deck_sync_increment, current_stats = _sync_single_deck(
                    remote_decks,
                    deckKey,
                    progress,
                    status_msgs,
                    step,
                    debug_messages=[],
                )

                # Criar resultado do deck
                deck_name = remote_decks[deckKey].get("local_deck_name", "Unknown")
                deck_url = remote_decks[deckKey].get("remote_deck_url", "")
                
                # Verificar se o deck era novo e atualizar status de sincronização
                from .config_manager import update_deck_sync_status
                was_new_deck = update_deck_sync_status(deck_url, success=True)
                
                deck_result = DeckSyncResult(
                    deck_name=deck_name,
                    deck_key=deckKey,
                    deck_url=deck_url,
                    success=True,
                    stats=current_stats,
                    was_new_deck=was_new_deck,
                )
                stats_manager.add_deck_result(deck_result)

                add_debug_message(f"✅ Deck concluído: {deckKey}", "SYNC")

            except SyncError as e:
                step, sync_errors = _handle_sync_error(
                    e, deckKey, remote_decks, progress, status_msgs, sync_errors, step
                )

                # Adicionar resultado de falha
                deck_name = remote_decks[deckKey].get("local_deck_name", "Unknown")
                deck_url = remote_decks[deckKey].get("remote_deck_url", "")
                failed_result = DeckSyncResult(
                    deck_name=deck_name,
                    deck_key=deckKey,
                    deck_url=deck_url,
                    success=False,
                    stats=SyncStats(),
                    error_message=str(e),
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
                deck_url = remote_decks[deckKey].get("remote_deck_url", "")
                failed_result = DeckSyncResult(
                    deck_name=deck_name,
                    deck_key=deckKey,
                    deck_url=deck_url,
                    success=False,
                    stats=SyncStats(),
                    error_message=f"Erro inesperado: {str(e)}",
                )
                failed_result.stats.add_error(f"Erro inesperado: {str(e)}")
                stats_manager.add_deck_result(failed_result)
                continue

        # Não precisamos salvar remote_decks aqui porque add_note_type_id_to_deck já salva individualmente
        # e essa chamada sobrescreveria os note_type_ids que foram adicionados

        # Mas precisamos salvar as atualizações de local_deck_name que foram feitas durante a sincronização
        from .config_manager import get_meta
        from .config_manager import save_meta

        try:
            current_meta = get_meta()
            save_meta(current_meta)
        except Exception as e:
            print(f"[WARNING] Erro ao salvar configurações após sincronização: {e}")

        # Obter resumo das estatísticas
        summary = stats_manager.get_summary()
        successful_decks = len(stats_manager.get_successful_decks())
        deck_results = stats_manager.deck_results  # Obter resultados por deck

        add_debug_message(
            f"🎯 Chamando _finalize_sync_new - successful_decks: {successful_decks}, total_decks: {total_decks}",
            "SYNC",
        )
        # Finalizar progresso e mostrar resultados
        _finalize_sync_new(
            progress,
            total_decks,
            successful_decks,
            summary["total_stats"],
            sync_errors,
            cleanup_result,
            missing_cleanup_result,
            deck_results,
            new_deck_mode=new_deck_mode,
        )

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


def _show_no_decks_message(selected_deck_names):
    """Mostra mensagem quando não há decks para sincronizar."""
    if selected_deck_names is not None:
        showInfo(
            f"Nenhum dos decks selecionados foi encontrado na configuração.\n\nDecks selecionados: {', '.join(selected_deck_names)}"
        )
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


def _update_progress_text(
    progress, status_msgs, max_lines=3, debug_messages=None, show_debug=False
):
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
    recent_msgs = (
        status_msgs[-max_lines:] if len(status_msgs) > max_lines else status_msgs
    )
    if recent_msgs:
        all_text_lines.extend(recent_msgs)

    # Adicionar mensagens de debug se fornecidas E se solicitado
    if debug_messages and show_debug:
        all_text_lines.append("")  # Linha em branco para separar
        all_text_lines.append("=== DEBUG MESSAGES ===")

        # Mostrar as últimas mensagens de debug (máximo 15 para janela ampliada)
        recent_debug = (
            debug_messages[-15:] if len(debug_messages) > 15 else debug_messages
        )
        all_text_lines.extend(recent_debug)

        if len(debug_messages) > 15:
            all_text_lines.append(
                f"... e mais {len(debug_messages) - 15} mensagens de debug"
            )

    # Juntar todas as linhas
    text = "\n".join(all_text_lines)

    # Limitar o comprimento de cada linha para evitar texto muito longo
    lines = text.split("\n")
    formatted_lines = []

    for line in lines:
        # Se a linha for muito longa, quebrar em palavras
        if len(line) > 80:  # Aumentar para 80 caracteres para debug messages
            words = line.split(" ")
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


def _sync_single_deck(
    remote_decks, deckKey, progress, status_msgs, step, debug_messages=None
):
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
    from .deck_manager import DeckNameManager
    from .deck_manager import DeckRecreationManager

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
    was_recreated, current_deck_id, current_deck_name = (
        DeckRecreationManager.recreate_deck_if_missing(currentRemoteInfo)
    )

    if was_recreated and current_deck_id is not None and current_deck_name is not None:
        # Capturar o ID antigo antes da atualização para log correto
        old_deck_id = local_deck_id

        # Atualizar informações na configuração
        DeckRecreationManager.update_deck_info_after_recreation(
            currentRemoteInfo, current_deck_id, current_deck_name
        )

        # IMPORTANTE: Salvar imediatamente as mudanças de local_deck_id após recriação
        # Isso garante que o novo ID seja persistido mesmo se houver erro posterior
        save_remote_decks(remote_decks)
        add_debug_message(
            f"[CONFIG_SAVE] local_deck_id atualizado e salvo após recriação: {old_deck_id} -> {current_deck_id}",
            "SYNC",
        )

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

    # Validar URL antes de tentar sincronizar e obter URL TSV para download
    tsv_url = validate_url(remote_deck_url)

    # 1. Download
    msg = f"{deckName}: baixando arquivo..."
    status_msgs.append(msg)
    _update_progress_text(progress, status_msgs)

    # Obter lista de estudantes habilitados para este deck
    enabled_students = get_selected_students_for_deck(remote_deck_url)
    add_debug_message(
        f"🎓 Estudantes habilitados para este deck: {list(enabled_students)}",
        "STUDENTS",
    )

    remoteDeck = getRemoteDeck(tsv_url, enabled_students=list(enabled_students))

    # NOVO: Debug para verificar notas carregadas
    notes_count = (
        len(remoteDeck.notes)
        if hasattr(remoteDeck, "notes") and remoteDeck.notes
        else 0
    )
    add_debug_message(
        f"📊 Notas carregadas do deck remoto: {notes_count}", "REMOTE_DECK"
    )

    step += 1
    progress.setValue(step)
    mw.app.processEvents()

    # Atualizar remote_deck_name com o nome extraído da URL
    new_remote_name_from_url = DeckNameManager.extract_remote_name_from_url(
        remote_deck_url
    )
    stored_remote_name = currentRemoteInfo.get("remote_deck_name")

    # IMPORTANTE: Lógica aprimorada para resolver conflitos dinâmicamente
    # Verificar se o nome remoto mudou e reavaliar resolução de conflitos
    should_update = False
    if stored_remote_name != new_remote_name_from_url:
        # Verificar se o nome armazenado tem sufixo de conflito
        if stored_remote_name and " #conflito" in stored_remote_name:
            # Nome tem sufixo de conflito - verificar se ainda é necessário
            add_debug_message(
                f"[CONFLICT_REEVALUATE] Reavaliando conflito: '{stored_remote_name}' vs novo nome '{new_remote_name_from_url}'",
                "SYNC",
            )

            # Usar DeckNameManager centralizado para resolução de conflitos
            resolved_new_name = DeckNameManager.resolve_remote_name_conflict(
                remote_deck_url, new_remote_name_from_url
            )

            # Se o nome resolvido é igual ao nome original, não há mais conflito
            if resolved_new_name == new_remote_name_from_url:
                # Conflito foi resolvido - pode usar nome original
                should_update = True
                current_remote_name = new_remote_name_from_url
                add_debug_message(
                    f"[CONFLICT_RESOLVED] Conflito resolvido! '{stored_remote_name}' → '{new_remote_name_from_url}'",
                    "SYNC",
                )

                # Também atualizar local_deck_name para remover o sufixo
                old_local_name = currentRemoteInfo.get("local_deck_name", "")
                if old_local_name and " #conflito" in old_local_name:
                    # Remover sufixo do nome local também
                    new_local_name = old_local_name.split(" #conflito")[0]
                    add_debug_message(
                        f"[CONFLICT_RESOLVED] Atualizando local_deck_name: '{old_local_name}' → '{new_local_name}'",
                        "SYNC",
                    )

                    # Atualizar nome do deck no Anki
                    try:
                        deck_id = currentRemoteInfo.get("local_deck_id")
                        if deck_id and mw and mw.col:
                            from anki.decks import DeckId

                            deck = mw.col.decks.get(DeckId(deck_id))
                            if deck:
                                old_anki_name = deck.get("name", "")
                                deck["name"] = new_local_name
                                mw.col.decks.save(deck)
                                add_debug_message(
                                    f"[ANKI_UPDATE] Deck renomeado no Anki: '{old_anki_name}' → '{new_local_name}'",
                                    "SYNC",
                                )
                    except Exception as e:
                        add_debug_message(
                            f"[ANKI_ERROR] Erro ao renomear deck no Anki: {e}", "SYNC"
                        )

                    # Atualizar na configuração
                    currentRemoteInfo["local_deck_name"] = new_local_name
                    remote_decks[deckKey]["local_deck_name"] = new_local_name

            else:
                # Ainda há conflito, mas pode ter mudado o sufixo
                if resolved_new_name != stored_remote_name:
                    should_update = True
                    current_remote_name = resolved_new_name
                    add_debug_message(
                        f"[CONFLICT_UPDATE] Atualizando sufixo de conflito: '{stored_remote_name}' → '{resolved_new_name}'",
                        "SYNC",
                    )
                else:
                    add_debug_message(
                        f"[CONFLICT_UNCHANGED] Mantendo resolução existente: '{stored_remote_name}'",
                        "SYNC",
                    )

        else:
            # Nome não tem conflito, aplicar resolução normal com DeckNameManager
            resolved_remote_name = DeckNameManager.resolve_remote_name_conflict(
                remote_deck_url, new_remote_name_from_url
            )

            if resolved_remote_name != stored_remote_name:
                should_update = True
                current_remote_name = resolved_remote_name
                add_debug_message(
                    f"[CONFLICT_RESOLVE] Aplicando resolução: '{new_remote_name_from_url}' → '{resolved_remote_name}'",
                    "SYNC",
                )

    else:
        # Nome não mudou, não precisa atualizar
        add_debug_message(
            f"[CONFLICT_SKIP] Nome remoto não mudou, mantendo: '{stored_remote_name}'",
            "SYNC",
        )
        current_remote_name = stored_remote_name

    # ABORDAGEM ROBUSTA: Sempre recriar local_deck_name e verificar se mudou
    from .deck_manager import DeckNameManager

    # Recriar local_deck_name baseado no remote_deck_name atual
    expected_local_deck_name = DeckNameManager.generate_local_name(current_remote_name)
    current_local_deck_name = currentRemoteInfo.get("local_deck_name", "")

    add_debug_message("[DECK_NAME_CHECK] Verificando consistência de nomes:", "SYNC")
    add_debug_message(f"[DECK_NAME_CHECK] - Remote: '{current_remote_name}'", "SYNC")
    add_debug_message(
        f"[DECK_NAME_CHECK] - Local atual: '{current_local_deck_name}'", "SYNC"
    )
    add_debug_message(
        f"[DECK_NAME_CHECK] - Local esperado: '{expected_local_deck_name}'", "SYNC"
    )

    # Verificar se local_deck_name precisa ser atualizado
    local_name_needs_update = current_local_deck_name != expected_local_deck_name

    # Aplicar atualizações necessárias
    if should_update or local_name_needs_update:
            if should_update:
                add_debug_message("[UPDATE_REASON] remote_deck_name mudou", "SYNC")
            if local_name_needs_update:
                add_debug_message("[UPDATE_REASON] local_deck_name inconsistente", "SYNC")

            # Atualizar local_deck_name no meta.json
            if local_name_needs_update:
                DeckNameManager._update_name_in_config(
                    remote_deck_url, expected_local_deck_name
                )
                add_debug_message(
                    f"[LOCAL_NAME_UPDATE] local_deck_name atualizado: '{current_local_deck_name}' -> '{expected_local_deck_name}'",
                    "SYNC",
                )

            # Sincronizar nome físico no Anki se necessário
            sync_result = DeckNameManager.sync_deck_with_config(remote_deck_url)
            if sync_result:
                add_debug_message(
                    f"[DECK_SYNC] Deck físico sincronizado: ID {sync_result[0]} -> '{sync_result[1]}'",
                    "SYNC",
                )

            # Atualizar configuração se houve mudança no remote_deck_name
            if should_update:
                # IMPORTANTE: Atualizar nomes dos note types ANTES de mudar o remote_deck_name
                old_remote_name_config = currentRemoteInfo.get("remote_deck_name")
                if old_remote_name_config and old_remote_name_config != current_remote_name:
                    try:
                        from .utils import update_note_type_names_for_deck_rename
                        from .config_manager import get_deck_note_type_ids
                        
                        # Detectar o nome real presente nos note types
                        note_types_config = get_deck_note_type_ids(remote_deck_url)
                        actual_old_name = None
                        
                        if note_types_config:
                            # Procurar por padrão comum nos note types para extrair o nome real
                            for note_type_name in note_types_config.values():
                                # Formato: "Sheets2Anki - {remote_name} - {student} - {type}"
                                if " - " in note_type_name:
                                    parts = note_type_name.split(" - ")
                                    if len(parts) >= 4 and parts[0] == "Sheets2Anki":
                                        # Reconstruir o nome remoto (pode ter múltiplos hífens)
                                        # Pegar tudo entre "Sheets2Anki - " e " - {student}"
                                        start_idx = note_type_name.find("Sheets2Anki - ") + len("Sheets2Anki - ")
                                        # Encontrar a última ocorrência de " - " seguida de aluno
                                        last_dash_student = note_type_name.rfind(" - " + parts[-2] + " - " + parts[-1])
                                        if last_dash_student > start_idx:
                                            potential_name = note_type_name[start_idx:last_dash_student]
                                            actual_old_name = potential_name
                                            break
                        
                        # Se não conseguiu detectar, usar o nome da configuração
                        old_name_to_use = actual_old_name if actual_old_name else old_remote_name_config
                        
                        add_debug_message(
                            f"[NOTE_TYPE_DETECT] old_remote_name_config: '{old_remote_name_config}'",
                            "SYNC",
                        )
                        add_debug_message(
                            f"[NOTE_TYPE_DETECT] actual_old_name detectado: '{actual_old_name}'",
                            "SYNC",
                        )
                        add_debug_message(
                            f"[NOTE_TYPE_DETECT] usando para atualização: '{old_name_to_use}' → '{current_remote_name}'",
                            "SYNC",
                        )
                        
                        updated_count = update_note_type_names_for_deck_rename(
                            remote_deck_url, old_name_to_use, current_remote_name, debug_messages
                        )
                        add_debug_message(
                            f"[NOTE_TYPE_UPDATE] {updated_count} note types atualizados para novo remote_deck_name",
                            "SYNC",
                        )
                        
                        # Sincronizar os note types no Anki com os nomes atualizados
                        if updated_count > 0:
                            try:
                                from .utils import sync_note_type_names_with_config
                                sync_result = sync_note_type_names_with_config(mw.col, remote_deck_url, debug_messages)
                                if sync_result and sync_result.get("renamed_in_anki", 0) > 0:
                                    add_debug_message(
                                        f"[NOTE_TYPE_ANKI_SYNC] {sync_result['renamed_in_anki']} note types renomeados no Anki",
                                        "SYNC",
                                    )
                                else:
                                    add_debug_message(
                                        "[NOTE_TYPE_ANKI_SYNC] Nenhum note type renomeado no Anki",
                                        "SYNC",
                                    )
                            except Exception as anki_sync_error:
                                add_debug_message(
                                    f"[NOTE_TYPE_ANKI_ERROR] Erro ao sincronizar note types no Anki: {anki_sync_error}",
                                    "SYNC",
                                )
                    except Exception as note_type_error:
                        add_debug_message(
                            f"[NOTE_TYPE_ERROR] Erro ao atualizar note types: {note_type_error}",
                            "SYNC",
                        )
            
            currentRemoteInfo["remote_deck_name"] = current_remote_name
            remote_decks[deckKey]["remote_deck_name"] = current_remote_name
            add_debug_message(
                f"[REMOTE_NAME_UPDATE] remote_deck_name atualizado para: '{current_remote_name}'",
                "SYNC",
            )

            # Sempre atualizar local_deck_name na configuração em memória
            if local_name_needs_update:
                currentRemoteInfo["local_deck_name"] = expected_local_deck_name
                remote_decks[deckKey]["local_deck_name"] = expected_local_deck_name
                add_debug_message(
                    "[MEMORY_UPDATE] Configuração em memória atualizada", "SYNC"
                )

            # IMPORTANTE: Não recarregar do arquivo aqui para preservar atualizações em memória
            add_debug_message(
                "[CONFIG_PRESERVE] Preservando atualizações em memória (remote_deck_name e note_types)", "SYNC"
            )
            
            # Salvar configuração final (agora com note_types atualizados E remote_deck_name correto)
            save_remote_decks(remote_decks)
            add_debug_message(
                "[CONFIG_SAVE] Configuração salva após atualização de nomes (com note_types corretos)", "SYNC"
            )    # Atualizar nome do deck se necessário usando DeckNameManager
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

    # 2. Processamento e escrita no banco de dados
    msg = f"{deckName}: processando dados..."
    status_msgs.append(msg)
    _update_progress_text(progress, status_msgs)

    remoteDeck.deckName = deckName

    msg = f"{deckName}: escrevendo no banco de dados..."
    status_msgs.append(msg)
    _update_progress_text(progress, status_msgs)

    add_debug_message(
        f"🚀 ABOUT TO CALL create_or_update_notes - remoteDeck has {len(remoteDeck.notes) if hasattr(remoteDeck, 'notes') and remoteDeck.notes else 0} notes",
        "SYNC",
    )

    # Debug crítico para verificar importação
    add_debug_message(
        f"🔧 create_or_update_notes function: {create_or_update_notes}", "SYNC"
    )
    add_debug_message(
        f"🔧 mw.col: {mw.col}, remoteDeck: {remoteDeck}, local_deck_id: {local_deck_id}",
        "SYNC",
    )

    try:
        add_debug_message("🔧 CALLING create_or_update_notes NOW...", "SYNC")
        deck_stats = create_or_update_notes(
            mw.col,
            remoteDeck,
            local_deck_id,
            deck_url=remote_deck_url,
            debug_messages=debug_messages,
        )
        add_debug_message(f"🔧 create_or_update_notes RETURNED: {deck_stats}", "SYNC")
    except Exception as e:
        error_details = traceback.format_exc()
        add_debug_message(f"❌ ERRO na chamada create_or_update_notes: {e}", "SYNC")
        add_debug_message(f"❌ Stack trace: {error_details}", "SYNC")
        # Retornar stats padrão com erros
        deck_stats = SyncStats(created=0, updated=0, deleted=0, errors=1, ignored=0)
        deck_stats.add_error(f"Erro crítico na sincronização: {e}")

    add_debug_message(
        f"✅ create_or_update_notes COMPLETED - returned: {deck_stats}", "SYNC"
    )

    step += 1
    progress.setValue(step)
    mw.app.processEvents()

    # 4. Capturar e armazenar IDs dos note types após sincronização bem-sucedida
    try:

        add_debug_message(
            f"Iniciando captura de note type IDs para deck: {deckName}", "SYNC"
        )

        # Capturar IDs dos note types criados/atualizados
        capture_deck_note_type_ids(
            remote_deck_url,  # Usar a URL real em vez da hash key
            currentRemoteInfo.get("remote_deck_name", "RemoteDeck"),
            None,  # enabled_students não é necessário para a captura de IDs
            None,  # enabled_students não é necessário para a captura de IDs
        )

        add_debug_message(
            f"✅ IDs de note types capturados e armazenados para deck: {deckName}",
            "SYNC",
        )

        # NOVO: Garantir consistência automática de nomes após sincronização
        add_debug_message(
            f"🔧 Iniciando verificação de consistência de nomes para: {remote_deck_url}",
            "NAME_CONSISTENCY",
        )
        
        try:
            consistency_result = NameConsistencyManager.ensure_consistency_during_sync(
                deck_url=remote_deck_url,
                remote_decks=remote_decks,
                debug_callback=lambda msg: add_debug_message(msg, "NAME_CONSISTENCY")
            )
            
            if consistency_result and not consistency_result.get('errors'):
                # Sucesso - logar o que foi atualizado
                updates = []
                if consistency_result.get('deck_updated'):
                    updates.append("deck name")
                if consistency_result.get('note_types_updated'):
                    updates.append(f"{len(consistency_result['note_types_updated'])} note types")
                if consistency_result.get('deck_options_updated'):
                    updates.append("deck options")
                
                if updates:
                    add_debug_message(
                        f"✅ Consistência aplicada: {', '.join(updates)} atualizados",
                        "NAME_CONSISTENCY",
                    )
                else:
                    add_debug_message(
                        "✅ Consistência verificada: todos os nomes já estavam corretos",
                        "NAME_CONSISTENCY",
                    )
            elif consistency_result and consistency_result.get('errors'):
                # Erro - mas não falhar a sincronização
                for error in consistency_result['errors']:
                    add_debug_message(
                        f"⚠️ Erro na consistência de nomes: {error}",
                        "NAME_CONSISTENCY",
                    )
        except Exception as consistency_error:
            # Não falhar a sincronização por causa da consistência de nomes
            add_debug_message(
                f"⚠️ Erro inesperado na consistência de nomes: {consistency_error}",
                "NAME_CONSISTENCY",
            )

    except Exception as e:
        # Não falhar a sincronização por causa da captura de IDs
        add_debug_message(
            f"❌ ERRO na captura de note type IDs para {deckName}: {e}", "SYNC"
        )
        error_details = traceback.format_exc()
        add_debug_message(f"Detalhes do erro: {error_details}", "SYNC")

    # 5. SINCRONIZAÇÃO ROBUSTA DOS NOTE_TYPES após criação das notas no Anki
    add_debug_message(
        "[NOTE_TYPE_SYNC] Iniciando sincronização robusta dos note_types APÓS criação das notas...",
        "SYNC",
    )
    try:
        enabled_students = get_selected_students_for_deck(remote_deck_url)
        sync_result = sync_note_type_names_robustly(
            remote_deck_url, current_remote_name, enabled_students
        )

        if sync_result["updated_count"] > 0:
            add_debug_message(
                f"[NOTE_TYPE_SYNC] ✅ {sync_result['updated_count']} note_types sincronizados com sucesso",
                "SYNC",
            )
            add_debug_message(
                f"[NOTE_TYPE_SYNC] - Renomeados no Anki: {sync_result['renamed_in_anki']}",
                "SYNC",
            )
            add_debug_message(
                f"[NOTE_TYPE_SYNC] - Atualizados no meta.json: {sync_result['updated_in_meta']}",
                "SYNC",
            )
            if sync_result.get("notes_migrated", 0) > 0:
                add_debug_message(
                    f"[NOTE_TYPE_SYNC] - Notas migradas: {sync_result['notes_migrated']}",
                    "SYNC",
                )
        else:
            add_debug_message(
                "[NOTE_TYPE_SYNC] ✅ Todos os note_types já estão consistentes", "SYNC"
            )

    except Exception as e:
        add_debug_message(
            f"[NOTE_TYPE_SYNC] ❌ Erro na sincronização robusta: {e}", "SYNC"
        )
        # Tentar fallback com método antigo
        try:
            enabled_students = get_selected_students_for_deck(remote_deck_url)
            update_note_type_names_in_meta(
                remote_deck_url, current_remote_name, enabled_students
            )
            add_debug_message("[NOTE_TYPE_SYNC] Fallback aplicado com sucesso", "SYNC")
        except Exception as fallback_error:
            add_debug_message(
                f"[NOTE_TYPE_SYNC] ❌ Fallback também falhou: {fallback_error}", "SYNC"
            )

    # NOVO: Atualizar histórico de sincronização de alunos (SOLUÇÃO ROBUSTA)
    # Isso garante que sempre saibamos quais alunos foram sincronizados,
    # independentemente de renomeações manuais de note types
    try:
        from .config_manager import update_student_sync_history
        
        # Obter alunos que foram sincronizados neste deck
        students_synced = get_selected_students_for_deck(remote_deck_url)
        
        if students_synced:
            # Atualizar histórico persistente
            update_student_sync_history(students_synced)
            add_debug_message(
                f"📚 HISTORY: Histórico atualizado para {len(students_synced)} alunos",
                "SYNC"
            )
        else:
            add_debug_message("📚 HISTORY: Nenhum aluno sincronizado para atualizar histórico", "SYNC")
            
    except Exception as history_error:
        add_debug_message(f"⚠️ HISTORY: Erro ao atualizar histórico: {history_error}", "SYNC")
        # Não interromper sincronização por erro no histórico

    # CRÍTICO: Salvar configurações finais após consistência de nomes
    # Isso garante que as atualizações do NameConsistencyManager sejam persistidas
    try:
        from .config_manager import save_meta, get_meta
        current_meta = get_meta()
        save_meta(current_meta)
        add_debug_message(
            "💾 FINAL_SAVE: Configurações salvas após verificação de consistência",
            "SYNC"
        )
    except Exception as save_error:
        add_debug_message(
            f"⚠️ FINAL_SAVE: Erro ao salvar configurações finais: {save_error}",
            "SYNC"
        )

    return step, 1, deck_stats


def _handle_sync_error(
    e, deckKey, remote_decks, progress, status_msgs, sync_errors, step
):
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
            deck = (
                mw.col.decks.get(local_deck_id) if local_deck_id is not None else None
            )
            deckName = (
                deck["name"]
                if deck
                else (
                    deck_info.get("local_deck_name") or str(local_deck_id)
                    if local_deck_id is not None
                    else "Unknown"
                )
            )
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


def _handle_unexpected_error(
    e, deckKey, remote_decks, progress, status_msgs, sync_errors, step
):
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
            deck = (
                mw.col.decks.get(local_deck_id) if local_deck_id is not None else None
            )
            deckName = (
                deck["name"]
                if deck
                else (
                    get_deck_local_name(deckKey) or str(local_deck_id)
                    if local_deck_id is not None
                    else "Unknown"
                )
            )
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


def _show_debug_messages_window(debug_messages):
    """
    Mostra uma janela scrollable com todas as mensagens de debug.
    Adaptada para dark mode e light mode do Anki.

    Args:
        debug_messages: Lista de mensagens de debug para exibir
    """
    from aqt.qt import QDialog
    from aqt.qt import QLabel
    from aqt.qt import QPushButton
    from aqt.qt import QTextEdit
    from aqt.qt import QVBoxLayout

    dialog = QDialog(mw)
    dialog.setWindowTitle(
        f"Debug Messages - Sistema de Note Type IDs ({len(debug_messages)} mensagens)"
    )
    dialog.setFixedSize(800, 600)

    layout = QVBoxLayout(dialog)

    # Detectar dark mode usando método mais direto
    is_dark_mode = False
    if hasattr(mw, "pm") and hasattr(mw.pm, "night_mode"):
        is_dark_mode = mw.pm.night_mode()

    # Definir cores baseadas no tema
    if is_dark_mode:
        # Dark mode colors - cores com alto contraste
        bg_color = "#1e1e1e"  # Fundo muito escuro
        text_color = "#f0f0f0"  # Texto muito claro
        border_color = "#555555"  # Borda média
        info_bg_color = "#2d2d2d"  # Fundo do info um pouco mais claro
        scroll_bg = "#3d3d3d"  # Fundo da scrollbar
        scroll_handle = "#707070"  # Handle da scrollbar
        scroll_hover = "#909090"  # Handle hover
        button_bg = "#4a4a4a"  # Fundo do botão
        button_hover = "#5a5a5a"  # Hover do botão
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
    info_label = QLabel(
        f"📋 Total de {len(debug_messages)} mensagens de debug capturadas durante a sincronização:"
    )
    info_label.setStyleSheet(
        f"""
        QLabel {{
            font-weight: bold; 
            margin-bottom: 5px;
            color: {text_color};
            background-color: {info_bg_color};
            padding: 8px;
            border-radius: 4px;
            border: 1px solid {border_color};
        }}
    """
    )
    layout.addWidget(info_label)

    # Criar área de texto scrollable com cores de alto contraste
    text_area = QTextEdit()
    text_area.setReadOnly(True)
    text_area.setPlainText("\n".join(debug_messages))
    text_area.setStyleSheet(
        f"""
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
    """
    )

    layout.addWidget(text_area)

    # Botão para fechar com estilo apropriado
    close_button = QPushButton("Fechar")
    close_button.clicked.connect(dialog.accept)
    close_button.setDefault(True)
    close_button.setStyleSheet(
        f"""
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
    """
    )
    layout.addWidget(close_button)

    # Aplicar estilo geral ao dialog
    dialog.setStyleSheet(
        f"""
        QDialog {{
            background-color: {info_bg_color};
            color: {text_color};
        }}
    """
    )

    from .compat import safe_exec_dialog

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
    from .config_manager import is_auto_remove_disabled_students
    from .config_manager import is_sync_missing_students_notes

    # PRIMEIRA VERIFICAÇÃO: Se funcionalidade está ativada, não precisa limpar
    if is_sync_missing_students_notes():
        print("🔍 [MISSING A.]: Funcionalidade ATIVADA, nenhuma limpeza necessária")
        return False  # Funcionalidade ativada, não precisa limpar

    # SEGUNDA VERIFICAÇÃO: Se remoção automática está desabilitada, não limpar
    if not is_auto_remove_disabled_students():
        print(
            "🔍 [MISSING A.]: Funcionalidade DESATIVADA, mas remoção automática também DESABILITADA - não limpar"
        )
        return False

    print(
        "🔍 [MISSING A.]: Funcionalidade DESATIVADA e remoção automática ATIVADA, verificando se há dados para limpar..."
    )

    # Verificar se há dados [MISSING A.] para limpar
    deck_names = [
        deck_info.get("remote_deck_name", "") for deck_info in remote_decks.values()
    ]
    deck_names = [name for name in deck_names if name]

    if not deck_names or not _is_anki_ready():
        print("🔍 [MISSING A.]: Sem decks ou sem conexão com Anki")
        return False

    assert mw.col is not None  # Type hint para o checker
    col = mw.col
    has_missing_data = False

    for deck_name in deck_names:
        print(f"🔍 [MISSING A.]: Verificando deck '{deck_name}'...")

        # Verificar se há decks [MISSING A.]
        missing_deck_pattern = f"{deck_name}::[MISSING A.]::"
        all_decks = col.decks.all_names_and_ids()

        missing_decks_found = [
            deck.name
            for deck in all_decks
            if deck.name.startswith(missing_deck_pattern)
        ]
        if missing_decks_found:
            has_missing_data = True
            print(f"  📁 Encontrados {len(missing_decks_found)} decks [MISSING A.]")

        # Verificar se há note types [MISSING A.]
        all_models = col.models.all()
        missing_pattern = f"Sheets2Anki - {deck_name} - [MISSING A.] -"

        missing_models_found = [
            model["name"] for model in all_models if missing_pattern in model["name"]
        ]
        if missing_models_found:
            has_missing_data = True
            print(
                f"  🏷️ Encontrados {len(missing_models_found)} note types [MISSING A.]"
            )

        if has_missing_data:
            break  # Já encontrou dados, não precisa continuar

    if has_missing_data:
        print("⚠️ [MISSING A.]: Dados encontrados, limpeza necessária")
    else:
        print("✅ [MISSING A.]: Nenhum dado encontrado, limpeza desnecessária")

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
    from .config_manager import get_global_student_config
    from .config_manager import is_auto_remove_disabled_students

    # PRIMEIRA VERIFICAÇÃO: Auto-remoção deve estar ativa
    if not is_auto_remove_disabled_students():
        return False

    config = get_global_student_config()
    current_enabled_raw = config.get("enabled_students", [])

    # Estudantes atualmente habilitados (case-sensitive)
    current_enabled_set = {
        student for student in current_enabled_raw if student and student.strip()
    }

    # MÚLTIPLAS FONTES para detectar alunos anteriormente habilitados (ROBUSTEZ)
    previous_enabled_raw = set()

    # Fonte 1: Todos os estudantes disponíveis
    available_students = config.get("available_students", [])
    previous_enabled_raw.update(available_students)

    # Fonte 3: Verificar se há decks/notas de alunos no Anki (scan direto)
    if mw and hasattr(mw, "col") and mw.col:
        anki_students = _get_students_from_anki_data()
        previous_enabled_raw.update(anki_students)

    # Processar previous_enabled (case-sensitive)
    previous_enabled_set = {
        student for student in previous_enabled_raw if student and student.strip()
    }

    # CALCULAR alunos desabilitados (case-sensitive)
    disabled_students_set = previous_enabled_set - current_enabled_set

    if disabled_students_set:
        print("🔍 CLEANUP: Detectados alunos para limpeza:")
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
        # Escanear decks por padrões de alunos "Sheets2Anki::DeckRemoto::StudentName::"
        all_decks = col.decks.all_names_and_ids()
        for deck in all_decks:
            deck_parts = deck.name.split("::")
            if len(deck_parts) >= 3 and "Sheets2Anki" in deck_parts[0]:
                # Estrutura: ["Sheets2Anki", "DeckRemoto", "StudentName", ...]
                potential_student = deck_parts[2].strip()  # Terceira posição é o aluno
                if potential_student and potential_student != "[MISSING A.]":
                    students_found.add(potential_student)

        # Escanear note types buscando nomes de estudantes
        all_models = col.models.all()
        for model in all_models:
            model_name = model["name"]
            if "Sheets2Anki -" in model_name:
                # Extrair nome do estudante do formato: "Sheets2Anki - Deck - StudentName - Type"
                parts = model_name.split(" - ")
                if len(parts) >= 4:
                    student_name = parts[2].strip()  # Third part is student name
                    if student_name:
                        students_found.add(student_name)

        print(
            f"🔍 SCAN: Encontrados estudantes com dados no Anki: {sorted(students_found)}"
        )

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
    from .student_manager import cleanup_disabled_students_data
    from .student_manager import cleanup_missing_students_data

    # OBTER ALUNOS DESABILITADOS usando normalização consistente
    config = get_global_student_config()
    current_enabled_raw = config.get("enabled_students", [])
    available_students = config.get("available_students", [])

    # Estudantes atualmente habilitados (case-sensitive)
    current_enabled_set = {
        student for student in current_enabled_raw if student and student.strip()
    }

    # MÚLTIPLAS FONTES para detectar alunos anteriormente habilitados
    previous_enabled_raw = set()
    previous_enabled_raw.update(available_students)

    # Adicionar dados do Anki
    if mw and hasattr(mw, "col") and mw.col:
        anki_students = _get_students_from_anki_data()
        previous_enabled_raw.update(anki_students)

    # Processar previous_enabled (case-sensitive)
    previous_enabled_set = {
        student for student in previous_enabled_raw if student and student.strip()
    }

    # CALCULAR desabilitados (case-sensitive)
    disabled_students_set = previous_enabled_set - current_enabled_set

    deck_names = [
        deck_info.get("remote_deck_name", "") for deck_info in remote_decks.values()
    ]
    deck_names = [name for name in deck_names if name]

    # Criar mensagem consolidada mais clara
    message_parts = [
        "⚠️ ATENÇÃO: REMOÇÃO PERMANENTE DE DADOS ⚠️\n",
        "O sistema detectou dados que precisam ser removidos.\n",
    ]

    # Só mostrar seção de alunos desabilitados se houver alunos
    if disabled_students_set:
        students_list = "\n".join(
            [f"• {student}" for student in sorted(disabled_students_set)]
        )
        message_parts.extend(
            [
                "\n📚 ALUNOS DESABILITADOS:\n",
                "Os seguintes alunos foram removidos da sincronização:\n",
                f"{students_list}\n",
                "\n🗑️ SERÁ REMOVIDO DE CADA ALUNO:\n",
                "• Todas as notas individuais do aluno\n",
                "• Todos os cards do aluno\n",
                "• Todos os subdecks do aluno\n",
                "• Note types específicos do aluno\n",
            ]
        )

    # Verificar se [MISSING A.] deve ser limpo
    from .config_manager import is_sync_missing_students_notes

    if not is_sync_missing_students_notes():
        # [MISSING A.] foi desabilitado
        message_parts.extend(
            [
                "\n📝 FUNCIONALIDADE [MISSING A.] DESABILITADA:\n",
                "• Todas as notas sem alunos específicos serão removidas\n",
                "• Todos os subdecks [MISSING A.] serão removidos\n",
                "• Note types [MISSING A.] serão removidos\n",
            ]
        )

    message_parts.extend(
        [
            "\n❌ ESTA AÇÃO É IRREVERSÍVEL!\n",
            "Os dados removidos não podem ser recuperados.\n\n",
            "Deseja continuar com a remoção?",
        ]
    )

    message = "".join(message_parts)

    # Criar MessageBox consolidado
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Warning)
    msg_box.setWindowTitle("⚠️ Confirmar Limpeza de Dados")
    msg_box.setText(message)
    msg_box.setStandardButtons(MessageBox_Yes | MessageBox_No)
    msg_box.setDefaultButton(MessageBox_No)  # Default é NOT remover

    # Customizar botões
    yes_btn = msg_box.button(MessageBox_Yes)
    no_btn = msg_box.button(MessageBox_No)

    if yes_btn:
        yes_btn.setText("🗑️ SIM, DELETAR TODOS OS DADOS")
        yes_btn.setStyleSheet(
            "QPushButton { background-color: #d73027; color: white; font-weight: bold; }"
        )

    if no_btn:
        no_btn.setText("🛡️ NÃO, MANTER DADOS")
        no_btn.setStyleSheet(
            "QPushButton { background-color: #4575b4; color: white; font-weight: bold; }"
        )

    # Executar diálogo
    from .compat import safe_exec_dialog

    result = safe_exec_dialog(msg_box)
    confirmed = result == MessageBox_Yes

    if confirmed:
        print("🧹 CLEANUP: Usuário confirmou limpeza consolidada")
        print(f"🧹 CLEANUP: Alunos desabilitados: {sorted(disabled_students_set)}")

        # Executar ambas as limpezas
        cleanup_missing_students_data(deck_names)
        cleanup_disabled_students_data(disabled_students_set, deck_names)

        # Retornar resultados
        missing_result = {
            "missing_cleanup_count": 1,
            "missing_cleanup_message": "Dados [MISSING A.] removidos",
        }

        cleanup_result = {
            "disabled_students_count": len(disabled_students_set),
            "disabled_students_names": ", ".join(sorted(disabled_students_set)),
        }

        print("✅ CLEANUP: Limpeza consolidada concluída")
        return missing_result, cleanup_result
    else:
        print("🛡️ CLEANUP: Usuário cancelou limpeza consolidada, dados preservados")
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
    from .student_manager import cleanup_missing_students_data
    from .student_manager import show_missing_cleanup_confirmation_dialog

    # Se a funcionalidade está ativada, não fazer nada
    if is_sync_missing_students_notes():
        return None  # Funcionalidade ativada, nada a limpar

    # Funcionalidade desativada - verificar se há dados [MISSING A.] para remover
    print(
        "🔍 CLEANUP: Sync [MISSING A.] está DESATIVADA, verificando dados para limpeza..."
    )

    # Verificar se existem decks ou note types [MISSING A.]
    if not _is_anki_ready():
        return None

    assert mw.col is not None  # Type hint para o checker
    col = mw.col
    deck_names = [
        deck_info.get("remote_deck_name", "") for deck_info in remote_decks.values()
    ]
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
                note_type_name = note_type.get("name", "")
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
        print("✅ CLEANUP: Nenhum dado [MISSING A.] encontrado para limpeza")
        return None

    print("⚠️ CLEANUP: Encontrados dados [MISSING A.] para limpeza")

    # Mostrar diálogo de confirmação
    if show_missing_cleanup_confirmation_dialog():
        # Usuário confirmou - executar limpeza
        print(f"🧹 CLEANUP: Iniciando limpeza [MISSING A.] para decks: {deck_names}")

        cleanup_missing_students_data(deck_names)

        # Log simples da limpeza concluída
        print("✅ CLEANUP: Limpeza [MISSING A.] concluída")
        return {
            "missing_cleanup_count": 1,
            "missing_cleanup_message": "Dados [MISSING A.] removidos",
        }
    else:
        print("🛡️ CLEANUP: Usuário cancelou a limpeza [MISSING A.], dados preservados")
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
    from .config_manager import get_global_student_config
    from .config_manager import is_auto_remove_disabled_students
    from .student_manager import cleanup_disabled_students_data
    from .student_manager import get_disabled_students_for_cleanup
    from .student_manager import show_cleanup_confirmation_dialog

    # Verificar se a auto-remoção está ativada
    if not is_auto_remove_disabled_students():
        return None  # Auto-remoção desativada, nada a fazer

    print("🔍 CLEANUP: Auto-remoção está ATIVADA, verificando alunos desabilitados...")

    # Obter configuração atual
    config = get_global_student_config()
    current_enabled = set(config.get("enabled_students", []))

    # LÓGICA MELHORADA para [MISSING A.]:
    # - Se a funcionalidade de [MISSING A.] está ativa, incluir na lista atual
    # - Se a funcionalidade foi desativada, [MISSING A.] será detectado como "removido"
    #   e suas notas serão limpas
    from .config_manager import is_sync_missing_students_notes

    if is_sync_missing_students_notes():
        current_enabled.add("[MISSING A.]")
        print(
            "🔍 CLEANUP: [MISSING A.] incluído na lista atual (funcionalidade ativa)"
        )
    else:
        print(
            "🔍 CLEANUP: [MISSING A.] excluído da lista atual (funcionalidade desativada)"
        )
        print(
            "          Se houver notas [MISSING A.] existentes, serão detectadas para remoção"
        )

    # Para detectar alunos desabilitados, usar histórico persistente ao invés de note types
    # A função obsoleta foi removida - usando sistema robusto baseado em histórico
    previous_enabled = set()  # Simplificado - usar outras fontes de dados

    # Identificar alunos desabilitados
    disabled_students = get_disabled_students_for_cleanup(
        current_enabled, previous_enabled
    )

    if not disabled_students:
        print("✅ CLEANUP: Nenhum aluno desabilitado detectado")
        return None

    print(
        f"⚠️ CLEANUP: Detectados {len(disabled_students)} alunos desabilitados: {sorted(disabled_students)}"
    )

    # Mostrar diálogo de confirmação
    if show_cleanup_confirmation_dialog(disabled_students):
        # Usuário confirmou - executar limpeza
        deck_names = [
            deck_info.get("remote_deck_name", "") for deck_info in remote_decks.values()
        ]
        deck_names = [name for name in deck_names if name]  # Filtrar nomes vazios

        print(f"🧹 CLEANUP: Iniciando limpeza para decks: {deck_names}")

        cleanup_disabled_students_data(disabled_students, deck_names)

        # Log simples da limpeza concluída
        print(f"✅ CLEANUP: Limpeza concluída para {len(disabled_students)} alunos")
        return {
            "disabled_students_count": len(disabled_students),
            "disabled_students_names": ", ".join(sorted(disabled_students)),
        }
    else:
        print("🛡️ CLEANUP: Usuário cancelou a limpeza, dados preservados")
        return None
