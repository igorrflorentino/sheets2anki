"""
Main synchronization functions for the Sheets2Anki addon.

This module contains the core functions for synchronizing
decks with remote sources, using the new configuration system.
It also includes classes for statistics management and finalization.
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
from .compat import AlignRight
from .compat import AlignTop
from .compat import QDialog
from .compat import QGroupBox
from .compat import QLabel

from .compat import QProgressDialog
from .compat import QProgressBar
from .compat import QPushButton
from .compat import QTextEdit
from .compat import QVBoxLayout
from .compat import Qt
from .compat import mw
from .compat import safe_exec_dialog
from .styled_messages import StyledMessageBox
from .config_manager import get_meta
from .config_manager import get_deck_local_name
from .config_manager import get_remote_decks
from .config_manager import save_remote_decks
from .config_manager import sync_note_type_names_robustly
from .config_manager import update_note_type_names_in_meta
from .backup_system import SimplifiedBackupManager
from .data_processor import create_or_update_notes
from .data_processor import getRemoteDeck
from .student_manager import get_selected_students_for_deck
from .templates_and_definitions import update_existing_note_type_templates
from .templates_and_definitions import DEFAULT_STUDENT
from .utils import SyncError
from .compat import MessageBox_Yes, MessageBox_Cancel


class SyncAborted(Exception):
    """Exception raised when user aborts synchronization."""
    pass
from .utils import add_debug_message
from .utils import capture_deck_note_type_ids
from .utils import clear_debug_messages
from .utils import get_spreadsheet_id_from_url
from .utils import remove_empty_subdecks
from .utils import validate_url
from .name_consistency_manager import NameConsistencyManager

# ========================================================================================
# SYNC STATISTICS CLASSES (consolidated from sync_stats.py)
# ========================================================================================


@dataclass
class SyncStats:
    """Statistics of a synchronization."""

    created: int = 0
    updated: int = 0
    deleted: int = 0
    ignored: int = 0
    errors: int = 0
    unchanged: int = 0
    skipped: int = 0

    # Detailed metrics of the remote deck - REFACTORED
    # 1. Total table lines (regardless of content)
    remote_total_table_lines: int = 0

    # 2. Total lines with valid notes (ID filled)
    remote_valid_note_lines: int = 0

    # 3. Total invalid lines (empty ID)
    remote_invalid_note_lines: int = 0

    # 4. Total lines marked for sync (SYNC = true)
    remote_sync_marked_lines: int = 0

    # 5. Potential total notes to be created in Anki (ID × students + [MISSING STUDENTS])
    remote_total_potential_anki_notes: int = 0

    # 6. Potential total notes for specific students
    remote_potential_student_notes: int = 0

    # 7. Potential total notes for [MISSING STUDENTS]
    remote_potential_missing_students_notes: int = 0

    # 8. Total unique students found
    remote_unique_students_count: int = 0

    # 9. Potential total notes per student (detailed)
    remote_notes_per_student: Dict[str, int] = field(default_factory=dict)

    error_details: List[str] = field(default_factory=list)
    # Fields for structured details
    update_details: List[Dict[str, Any]] = field(default_factory=list)
    creation_details: List[Dict[str, Any]] = field(default_factory=list)
    deletion_details: List[Dict[str, Any]] = field(default_factory=list)

    def add_error(self, error_msg: str) -> None:
        """Adds an error to the statistics."""
        self.errors += 1
        self.error_details.append(error_msg)

    def add_update_detail_structured(self, detail: Dict[str, Any]) -> None:
        """Adds a structured update detail."""
        self.update_details.append(detail)

    def add_creation_detail(self, detail: Dict[str, Any]) -> None:
        """Adds a creation detail."""
        self.creation_details.append(detail)

    def add_deletion_detail(self, detail: Dict[str, Any]) -> None:
        """Adds a deletion detail."""
        self.deletion_details.append(detail)

    def merge(self, other: "SyncStats") -> None:
        """Merge with other statistics."""
        self.created += other.created
        self.updated += other.updated
        self.deleted += other.deleted
        self.ignored += other.ignored
        self.errors += other.errors
        self.unchanged += other.unchanged
        self.skipped += other.skipped

        # Aggregate metrics from the remote deck - REFACTORED
        self.remote_total_table_lines += other.remote_total_table_lines
        self.remote_valid_note_lines += other.remote_valid_note_lines
        self.remote_invalid_note_lines += other.remote_invalid_note_lines
        self.remote_sync_marked_lines += other.remote_sync_marked_lines
        self.remote_total_potential_anki_notes += (
            other.remote_total_potential_anki_notes
        )
        self.remote_potential_student_notes += other.remote_potential_student_notes
        self.remote_potential_missing_students_notes += other.remote_potential_missing_students_notes
        self.remote_unique_students_count = max(
            self.remote_unique_students_count, other.remote_unique_students_count
        )

        # Merge student notes dictionaries - SUM values
        for student, count in other.remote_notes_per_student.items():
            if student in self.remote_notes_per_student:
                # Sum instead of taking max to have correct aggregate total
                self.remote_notes_per_student[student] += count
            else:
                self.remote_notes_per_student[student] = count

        self.error_details.extend(other.error_details)
        self.update_details.extend(other.update_details)
        self.creation_details.extend(other.creation_details)
        self.deletion_details.extend(other.deletion_details)

    def get_total_operations(self) -> int:
        """Returns the total number of operations performed."""
        return self.created + self.updated + self.deleted + self.ignored

    def has_changes(self) -> bool:
        """Checks if there were changes."""
        return self.created > 0 or self.updated > 0 or self.deleted > 0

    def has_errors(self) -> bool:
        """Checks if there were errors."""
        return self.errors > 0


@dataclass
class DeckSyncResult:
    """Result of specific deck synchronization."""

    deck_name: str
    deck_key: str
    deck_url: str
    success: bool
    stats: SyncStats
    was_new_deck: bool = False  # If the deck was new (never synced before)
    error_message: Optional[str] = None

    def __post_init__(self):
        """Initialization after creation."""
        if self.stats is None:
            self.stats = SyncStats()


class SyncStatsManager:
    """Sync statistics manager."""

    def __init__(self):
        self.total_stats = SyncStats()
        self.deck_results: List[DeckSyncResult] = []

    def add_deck_result(self, result: DeckSyncResult) -> None:
        """Adds synchronization result of a deck."""
        self.deck_results.append(result)
        self.total_stats.merge(result.stats)

    def create_deck_result(self, deck_name: str, deck_key: str, deck_url: str = "") -> DeckSyncResult:
        """Creates a new deck result."""
        return DeckSyncResult(
            deck_name=deck_name, deck_key=deck_key, deck_url=deck_url, success=False, stats=SyncStats()
        )

    def get_successful_decks(self) -> List[DeckSyncResult]:
        """Returns successfully synchronized decks."""
        return [r for r in self.deck_results if r.success]

    def get_failed_decks(self) -> List[DeckSyncResult]:
        """Returns decks that failed synchronization."""
        return [r for r in self.deck_results if not r.success]

    def get_summary(self) -> Dict[str, Any]:
        """Returns a summary of statistics."""
        successful = len(self.get_successful_decks())
        failed = len(self.get_failed_decks())

        return {
            "total_decks": len(self.deck_results),
            "successful_decks": successful,
            "failed_decks": failed,
            "total_stats": self.total_stats,  # Return SyncStats object directly
            "has_changes": self.total_stats.has_changes(),
            "has_errors": self.total_stats.has_errors(),
        }

    def reset(self) -> None:
        """Resets all statistics."""
        self.total_stats = SyncStats()
        self.deck_results.clear()


# ========================================================================================
# SYNC FINALIZATION FUNCTIONS (consolidated from sync_finalization.py)
# ========================================================================================


def _finalize_sync_cleanup(progress):
    """
    Performs final cleanup operations for synchronization.
    
    Args:
        progress: QProgressDialog instance to update status
        
    Returns:
        int: Number of removed subdecks
    """
    if hasattr(progress, 'appendMessage'):
        progress.appendMessage("🧹 Cleaning up empty subdecks...")
    else:
        progress.setLabelText("🧹 Cleaning up empty subdecks...")
        
    mw.app.processEvents()
    
    from .config_manager import get_remote_decks
    from .utils import apply_automatic_deck_options_system
    
    # Remove empty subdecks
    remote_decks = get_remote_decks()
    removed_subdecks = remove_empty_subdecks(remote_decks)
    
    # Apply automatic deck options system
    if hasattr(progress, 'appendMessage'):
        progress.appendMessage("⚙️ Configuring deck options...")
    else:
        progress.setLabelText("⚙️ Configuring deck options...")
    mw.app.processEvents()

    options_result = apply_automatic_deck_options_system()
    add_debug_message(
        f"✅ apply_automatic_deck_options_system() returned: {options_result}", "SYNC"
    )

    if options_result and options_result.get("success"):
        if options_result.get("root_deck_updated") or options_result.get("remote_decks_updated", 0) > 0:
            count = options_result.get("remote_decks_updated", 0)
            root_txt = "Root + " if options_result.get("root_deck_updated") else ""
            if hasattr(progress, 'appendMessage'):
                progress.appendMessage(f"   ✅ Options applied: {root_txt}{count} decks")
        else:
            if hasattr(progress, 'appendMessage'):
                progress.appendMessage("   ✅ Options verification: OK")

    add_debug_message("🎬 Synchronization cleanup finished", "SYSTEM")

    # Update Anki interface to show changes
    if hasattr(progress, 'appendMessage'):
        progress.appendMessage("🔄 Refreshing interface...")
    else:
        progress.setLabelText("🔄 Refreshing interface...")
    mw.app.processEvents()

    ensure_interface_refresh()
    
    # Wait a moment to show the cleanup message
    time.sleep(0.5)
    
    return removed_subdecks


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
    Shows synchronization summary using scrolled interface.

    Args:
        on_close_callback (callable, optional): Function to be called when the dialogue is closed
        deck_results (list, optional): List of DeckSyncResult for per-deck visualization
    """

    summary = []

    # Main statistics
    if sync_errors or total_stats.errors > 0:
        summary.append("❌ Synchronization completed with problems!")
        summary.append(
            f"📊 Decks: {decks_synced}/{total_decks} successfully synchronized"
        )
    else:
        summary.append("✅ Synchronization completed successfully!")
        summary.append(f"📊 Decks: {decks_synced}/{total_decks} synchronized")

    # Summary statistics in header
    if total_stats.created > 0:
        # Check if any of the decks were new (based on robust detection by last_sync)
        new_decks_detected = False
        if deck_results:
            new_decks_detected = any(result.was_new_deck for result in deck_results if result.success)
        
        if new_decks_detected:
            if total_decks == 1:
                summary.append(f"➕ {total_stats.created} notes created (new deck added)")
            else:
                summary.append(f"➕ {total_stats.created} notes created (includes new decks)")
        else:
            summary.append(f"➕ {total_stats.created} notes created")

    if total_stats.updated > 0:
        summary.append(f"✏️ {total_stats.updated} notes updated")

    if total_stats.deleted > 0:
        summary.append(f"🗑️ {total_stats.deleted} notes deleted")

    if total_stats.ignored > 0:
        summary.append(f"⏭️ {total_stats.ignored} notes ignored")

    # Cleanups
    if removed_subdecks > 0:
        summary.append(f"🧹 {removed_subdecks} empty subdecks removed")

    if cleanup_result and cleanup_result.get("disabled_students_count", 0) > 0:
        summary.append(
            f"🧹 {cleanup_result['disabled_students_count']} disabled students removed"
        )

    if missing_cleanup_result:
        summary.append(f"🧹 {DEFAULT_STUDENT} data removed")

    # AnkiWeb synchronization
    if ankiweb_result is not None:
        if ankiweb_result.get("success", False):
            summary.append(
                "🔄 AnkiWeb: Synchronization started (automatically detecting changes)"
            )
        elif "error" in ankiweb_result:
            summary.append(
                f"❌ AnkiWeb: Synchronization failed - {ankiweb_result['error']}"
            )
    else:
        # Check if configured but not executed
        try:
            from .config_manager import get_ankiweb_sync_mode

            sync_mode = get_ankiweb_sync_mode()
            if sync_mode == "disabled":
                summary.append("⏹️ AnkiWeb: Automatic synchronization disabled")
        except:
            pass

    # Errors
    sync_errors = sync_errors or []
    total_errors = total_stats.errors + len(sync_errors)
    if total_errors > 0:
        summary.append(f"⚠️ {total_errors} errors found")

    # Always use scrolled interface
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
    Generates simplified (aggregated) view of sync statistics.
    
    Args:
        total_stats: Total aggregated statistics
        sync_errors: List of sync errors
        deck_results: List of per-deck results (not used in simplified mode)
    
    Returns:
        list: List of strings for display
    """
    details_content = []

    # NEW: Summary of operations


    # FIRST: Detailed remote deck metrics (aggregated)
    if (
        total_stats.remote_total_table_lines > 0
        or total_stats.remote_valid_note_lines > 0
        or total_stats.remote_sync_marked_lines > 0
        or total_stats.remote_total_potential_anki_notes > 0
    ):
        details_content.append("📊 DETAILED REMOTE DECK METRICS:")
        details_content.append("=" * 60)
        details_content.append(
            f"📋 1. Total table lines: {total_stats.remote_total_table_lines}"
        )
        details_content.append(
            f"✅ 2. Lines with valid notes (ID filled): {total_stats.remote_valid_note_lines}"
        )
        details_content.append(
            f"❌ 3. Invalid lines (empty ID): {total_stats.remote_invalid_note_lines}"
        )
        details_content.append(
            f"🔄 4. Lines marked for sync: {total_stats.remote_sync_marked_lines}"
        )
        details_content.append(
            f"⏸️ 5. Skipped lines (SYNC != yes): {total_stats.skipped}"
        )
        details_content.append(
            f"⏭️ 6. Unchanged notes: {total_stats.unchanged}"
        )
        details_content.append(
            f"➕ 7. Created notes: {total_stats.created}"
        )
        details_content.append(
            f"✏️ 8. Updated notes: {total_stats.updated}"
        )
        details_content.append(
            f"🗑️ 9. Deleted notes: {total_stats.deleted}"
        )
        details_content.append(
            f"⚠️ 10. Ignored notes: {total_stats.ignored}"
        )
        details_content.append(
            f"❌ 11. Errors: {total_stats.errors}"
        )
        details_content.append(
            f"📝 12. Potential total notes in Anki: {total_stats.remote_total_potential_anki_notes}"
        )
        details_content.append(
            f"🎓 13. Potential notes for specific students: {total_stats.remote_potential_student_notes}"
        )
        details_content.append(
            f"❓ 14. Potential notes for {DEFAULT_STUDENT}: {total_stats.remote_potential_missing_students_notes}"
        )
        details_content.append(
            f"👥 15. Total unique students: {total_stats.remote_unique_students_count}"
        )

        # 16. Show notes per individual student
        if total_stats.remote_notes_per_student:
            details_content.append("📊 16. Notes per student (aggregated totals):")
            for student, count in sorted(total_stats.remote_notes_per_student.items()):
                details_content.append(f"   • {student}: {count} notes")

        details_content.append("")

    # SECOND: Detailed errors (if any)
    if sync_errors or total_stats.error_details:
        total_errors = total_stats.errors + len(sync_errors or [])
        if total_errors > 0:
            details_content.append(f"⚠️ DETAILS OF {total_errors} ERRORS:")
            details_content.append("=" * 60)
            error_count = 1
            for error in sync_errors or []:
                details_content.append(f"{error_count:4d}. {error}")
                error_count += 1
            for error in total_stats.error_details:
                details_content.append(f"{error_count:4d}. {error}")
                error_count += 1
            details_content.append("")

    # LAST: Created notes details
    if total_stats.created > 0 and total_stats.creation_details:
        details_content.append(f"➕ DETAILS OF {total_stats.created} CREATED NOTES:")
        details_content.append("=" * 60)
        for i, detail in enumerate(total_stats.creation_details, 1):
            details_content.append(
                f"{i:4d}. {detail['student']}: {detail['note_id']} - {detail.get('pergunta', '(Unknown Question)')}"
            )
        details_content.append("")

    # LAST: Updated notes details
    if total_stats.updated > 0 and total_stats.update_details:
        details_content.append(
            f"✏️ DETAILS OF {total_stats.updated} UPDATED NOTES:"
        )
        details_content.append("=" * 60)
        for i, detail in enumerate(total_stats.update_details, 1):
            details_content.append(f"{i:4d}. {detail['student']}: {detail['note_id']}")
            for j, change in enumerate(detail["changes"], 1):
                details_content.append(f"      {j:2d}. {change}")
            details_content.append("")

    # LAST: Removed notes details
    if total_stats.deleted > 0 and total_stats.deletion_details:
        details_content.append(f"🗑️ DETAILS OF {total_stats.deleted} REMOVED NOTES:")
        details_content.append("=" * 60)
        for i, detail in enumerate(total_stats.deletion_details, 1):
            details_content.append(
                f"{i:4d}. {detail['student']}: {detail['note_id']} - {detail.get('pergunta', '(Unknown Question)')}"
            )
        details_content.append("")

    # If no modification details were recorded, show information message
    if not any(
        [
            total_stats.created > 0 and total_stats.creation_details,
            total_stats.updated > 0 and total_stats.update_details,
            total_stats.deleted > 0 and total_stats.deletion_details,
            sync_errors or total_stats.error_details,
        ]
    ):
        details_content.append(
            "ℹ️ No detailed note modifications were recorded during this sync."
        )
        details_content.append("")
        details_content.append("This can happen when:")
        details_content.append("• Notes were already up to date")
        details_content.append("• Only cleanup operations were performed")
        details_content.append("• No changes were found in spreadsheet data")

    return details_content


def generate_aggregated_summary_only(total_stats, sync_errors=None):
    """
    Generates only aggregated summary without individual note details.
    Used in detailed mode to avoid duplication.
    
    Args:
        total_stats: Total aggregated statistics
        sync_errors: List of sync errors
    
    Returns:
        list: List of strings for display
    """
    details_content = []

    # Detailed errors (if any)
    if sync_errors or total_stats.error_details:
        total_errors = total_stats.errors + len(sync_errors or [])
        if total_errors > 0:
            details_content.append(f"⚠️ DETAILS OF {total_errors} GENERAL ERRORS:")
            details_content.append("=" * 60)
            error_count = 1
            for error in sync_errors or []:
                details_content.append(f"{error_count:4d}. {error}")
                error_count += 1
            for error in total_stats.error_details:
                details_content.append(f"{error_count:4d}. {error}")
                error_count += 1
            details_content.append("")

    # Detailed remote deck metrics (aggregated) - only if not shown per deck
    if (
        total_stats.remote_total_table_lines > 0
        or total_stats.remote_valid_note_lines > 0
        or total_stats.remote_sync_marked_lines > 0
        or total_stats.remote_total_potential_anki_notes > 0
    ):
        details_content.append("📊 AGGREGATED REMOTE METRICS TOTALS:")
        details_content.append("=" * 60)
        details_content.append(
            f"📋 1. Total table lines: {total_stats.remote_total_table_lines}"
        )
        details_content.append(
            f"✅ 2. Lines with valid notes (ID filled): {total_stats.remote_valid_note_lines}"
        )
        details_content.append(
            f"❌ 3. Invalid lines (empty ID): {total_stats.remote_invalid_note_lines}"
        )
        details_content.append(
            f"🔄 4. Lines marked for sync: {total_stats.remote_sync_marked_lines}"
        )
        details_content.append(
            f"⏸️ 5. Skipped lines (SYNC != yes): {total_stats.skipped}"
        )
        details_content.append(
            f"⏭️ 6. Unchanged notes: {total_stats.unchanged}"
        )
        details_content.append(
            f"➕ 7. Created notes: {total_stats.created}"
        )
        details_content.append(
            f"✏️ 8. Updated notes: {total_stats.updated}"
        )
        details_content.append(
            f"🗑️ 9. Deleted notes: {total_stats.deleted}"
        )
        details_content.append(
            f"⚠️ 10. Ignored notes: {total_stats.ignored}"
        )
        details_content.append(
            f"❌ 11. Errors: {total_stats.errors}"
        )
        details_content.append(
            f"📝 12. Potential total notes in Anki: {total_stats.remote_total_potential_anki_notes}"
        )
        details_content.append(
            f"🎓 13. Potential notes for specific students: {total_stats.remote_potential_student_notes}"
        )
        details_content.append(
            f"❓ 14. Potential notes for {DEFAULT_STUDENT}: {total_stats.remote_potential_missing_students_notes}"
        )
        details_content.append(
            f"👥 15. Total unique students: {total_stats.remote_unique_students_count}"
        )

        # 16. Show notes per individual student
        if total_stats.remote_notes_per_student:
            details_content.append("📊 16. Notes per student (aggregated totals):")
            for student, count in sorted(total_stats.remote_notes_per_student.items()):
                details_content.append(f"   • {student}: {count} notes")

        details_content.append("")

    return details_content


def generate_deck_detailed_metrics(stats, deck_name):
    """
    Generates complete detailed metrics for an individual deck.
    
    Args:
        stats: Individual deck statistics (SyncStats)
        deck_name: Deck name
    
    Returns:
        list: List of strings with detailed metrics
    """
    metrics_content = []
    

    # All 9 detailed remote deck metrics (same as simplified mode)
    if (
        stats.remote_total_table_lines > 0
        or stats.remote_valid_note_lines > 0
        or stats.remote_sync_marked_lines > 0
        or stats.remote_total_potential_anki_notes > 0
    ):
        metrics_content.append(f"     📊 Remote Spreadsheet Metrics:")
        metrics_content.append(f"        📋 1. Total table lines: {stats.remote_total_table_lines}")
        metrics_content.append(f"        ✅ 2. Lines with valid notes (ID filled): {stats.remote_valid_note_lines}")
        metrics_content.append(f"        ❌ 3. Invalid lines (empty ID): {stats.remote_invalid_note_lines}")
        metrics_content.append(f"        🔄 4. Lines marked for sync: {stats.remote_sync_marked_lines}")
        metrics_content.append(f"        ⏸️ 5. Skipped lines (SYNC != yes): {stats.skipped}")
        metrics_content.append(f"        ⏭️ 6. Unchanged notes: {stats.unchanged}")
        metrics_content.append(f"        ➕ 7. Created notes: {stats.created}")
        metrics_content.append(f"        ✏️ 8. Updated notes: {stats.updated}")
        metrics_content.append(f"        🗑️ 9. Deleted notes: {stats.deleted}")
        metrics_content.append(f"        ⚠️ 10. Ignored notes: {stats.ignored}")
        metrics_content.append(f"        ❌ 11. Errors: {stats.errors}")
        metrics_content.append(f"        📝 12. Potential total notes in Anki: {stats.remote_total_potential_anki_notes}")
        metrics_content.append(f"        🎓 13. Potential notes for specific students: {stats.remote_potential_student_notes}")
        metrics_content.append(f"        ❓ 14. Potential notes for {DEFAULT_STUDENT}: {stats.remote_potential_missing_students_notes}")
        metrics_content.append(f"        👥 15. Total unique students: {stats.remote_unique_students_count}")
        
        # 16. Show notes per individual student for this deck
        if stats.remote_notes_per_student:
            metrics_content.append(f"        📊 16. Notes per student in this deck:")
            for student, count in sorted(stats.remote_notes_per_student.items()):
                metrics_content.append(f"           • {student}: {count} notes")
    
    # NOTE DETAILS AFTER REMOTE METRICS (individualized per deck)
    
    # Details of created notes in this deck
    if stats.created > 0 and stats.creation_details:
        metrics_content.append(f"     ➕ DETAILS OF {stats.created} CREATED NOTES:")
        for i, detail in enumerate(stats.creation_details, 1):
            metrics_content.append(f"        {i:2d}. {detail['student']}: {detail['note_id']} - {detail.get('pergunta', '(Unknown Question)')}")
    
    # Details of updated notes in this deck
    if stats.updated > 0 and stats.update_details:
        metrics_content.append(f"     ✏️ DETAILS OF {stats.updated} UPDATED NOTES:")
        for i, detail in enumerate(stats.update_details, 1):
            metrics_content.append(f"        {i:2d}. {detail['student']}: {detail['note_id']}")
            for j, change in enumerate(detail["changes"], 1):
                metrics_content.append(f"           {j:2d}. {change}")
    
    # Details of removed notes in this deck
    if stats.deleted > 0 and stats.deletion_details:
        metrics_content.append(f"     🗑️ DETAILS OF {stats.deleted} REMOVED NOTES:")
        for i, detail in enumerate(stats.deletion_details, 1):
            metrics_content.append(f"        {i:2d}. {detail['student']}: {detail['note_id']} - {detail.get('pergunta', '(Unknown Question)')}")
    
    return metrics_content


def generate_detailed_view(total_stats, sync_errors=None, deck_results=None):
    """
    Generates detailed view (per deck) of sync statistics.
    
    Args:
        total_stats: Total aggregated statistics
        sync_errors: List of sync errors
        deck_results: List of individual deck results
    
    Returns:
        list: List of strings for display
    """
    details_content = []

    # FIRST: Show general aggregated summary
    aggregated_summary = generate_aggregated_summary_only(total_stats, sync_errors)
    
    if aggregated_summary:
        details_content.append("📋 AGGREGATED GENERAL SUMMARY:")
        details_content.append("=" * 80)
        details_content.append("\n")
        details_content.extend(aggregated_summary)
        details_content.append("")

    # SECOND: Show summary per individual deck (with individualized note details)
    if deck_results and len(deck_results) >= 1:
        details_content.append("📊 INDIVIDUAL DECK SUMMARY:")
        details_content.append("=" * 80)
        
        for i, deck_result in enumerate(deck_results, 1):
            deck_name = deck_result.deck_name
            stats = deck_result.stats
            success_status = "✅" if deck_result.success else "❌"
            
            # Indicate if the deck was new during this synchronization
            new_deck_indicator = " (NEW DECK)" if deck_result.was_new_deck else ""
            
            details_content.append(f"{i:2d}. {success_status} {deck_name}{new_deck_indicator}")
            
            # Generate all detailed metrics for this deck (includes note details)
            deck_metrics = generate_deck_detailed_metrics(stats, deck_name)
            details_content.extend(deck_metrics)
            
            # If there is a deck-specific error, show it
            if not deck_result.success and hasattr(deck_result, 'error_message') and deck_result.error_message:
                details_content.append(f"     ❌ Error: {deck_result.error_message}")
            
            details_content.append("")
        
        details_content.append("=" * 80)
    
    return details_content


def generate_errors_view(total_stats, sync_errors=None, deck_results=None):
    """
    Generates errors-only view of sync statistics.
    Shows only errors that occurred during synchronization.
    
    Args:
        total_stats: Total aggregated statistics
        sync_errors: List of sync errors
        deck_results: List of per-deck results
    
    Returns:
        list: List of strings for display
    """
    details_content = []
    has_errors = False

    # FIRST: General sync errors
    if sync_errors or total_stats.error_details:
        total_errors = total_stats.errors + len(sync_errors or [])
        if total_errors > 0:
            has_errors = True
            details_content.append(f"⚠️ GENERAL SYNCHRONIZATION ERRORS ({total_errors}):")
            details_content.append("=" * 60)
            error_count = 1
            for error in sync_errors or []:
                details_content.append(f"{error_count:4d}. {error}")
                error_count += 1
            for error in total_stats.error_details:
                details_content.append(f"{error_count:4d}. {error}")
                error_count += 1
            details_content.append("")

    # SECOND: Per-deck errors
    if deck_results:
        deck_errors = []
        for deck_result in deck_results:
            if not deck_result.success:
                deck_errors.append(deck_result)
            elif deck_result.stats.errors > 0 or deck_result.stats.error_details:
                deck_errors.append(deck_result)
        
        if deck_errors:
            has_errors = True
            details_content.append("❌ ERRORS PER DECK:")
            details_content.append("=" * 60)
            
            for i, deck_result in enumerate(deck_errors, 1):
                deck_name = deck_result.deck_name
                stats = deck_result.stats
                success_status = "✅" if deck_result.success else "❌"
                
                details_content.append(f"{i:2d}. {success_status} {deck_name}")
                
                # Show deck-specific error message
                if not deck_result.success and hasattr(deck_result, 'error_message') and deck_result.error_message:
                    details_content.append(f"     ❌ Error: {deck_result.error_message}")
                
                # Show error details from stats
                if stats.errors > 0 or stats.error_details:
                    error_count = 1
                    for error in stats.error_details:
                        details_content.append(f"     {error_count:2d}. {error}")
                        error_count += 1
                
                details_content.append("")
            
            details_content.append("=" * 60)

    # If no errors, show success message
    if not has_errors:
        details_content.append("✅ NO ERRORS OCCURRED DURING SYNCHRONIZATION")
        details_content.append("")
        details_content.append("All decks were synchronized successfully without any errors.")
        details_content.append("")
        details_content.append("If you're experiencing issues, try:")
        details_content.append("• Checking your internet connection")
        details_content.append("• Verifying the spreadsheet URL is accessible")
        details_content.append("• Ensuring the spreadsheet has the correct format")

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
    Shows synchronization summary with a modern, user-friendly scrolled interface.

    Args:
        on_close_callback (callable, optional): Function to be called when the dialogue is closed
        deck_results (list, optional): List of DeckSyncResult for per-deck visualization
    """
    from .compat import Palette_Window
    from .compat import QButtonGroup
    from .compat import QRadioButton
    from .compat import QHBoxLayout
    from .compat import QFrame
    from .compat import QScrollArea
    from .compat import QWidget
    from .compat import QSizePolicy

    # Create custom dialog
    dialog = QDialog()
    dialog.setWindowTitle("Synchronization Summary")
    dialog.setMinimumSize(850, 650)
    dialog.resize(950, 750)

    # Connect callback to closing if provided
    if on_close_callback and callable(on_close_callback):
        dialog.finished.connect(on_close_callback)

    # Detect dark mode based on system default window background color
    palette = dialog.palette()
    bg_color = palette.color(Palette_Window)
    is_dark_mode = bg_color.lightness() < 128

    # Define color scheme based on theme
    if is_dark_mode:
        colors = {
            'bg': '#1e1e1e',
            'card_bg': '#2d2d2d',
            'header_bg': '#363636',
            'text': '#ffffff',
            'text_secondary': '#b0b0b0',
            'border': '#404040',
            'accent_success': '#4CAF50',
            'accent_warning': '#FF9800',
            'accent_error': '#f44336',
            'accent_info': '#2196F3',
            'accent_purple': '#9C27B0',
            'button_bg': '#3d3d3d',
            'button_hover': '#4a4a4a',
            'toggle_active': '#4CAF50',
            'toggle_inactive': '#555555',
        }
    else:
        colors = {
            'bg': '#f5f5f5',
            'card_bg': '#ffffff',
            'header_bg': '#e8e8e8',
            'text': '#1a1a1a',
            'text_secondary': '#666666',
            'border': '#d0d0d0',
            'accent_success': '#4CAF50',
            'accent_warning': '#FF9800',
            'accent_error': '#e53935',
            'accent_info': '#1976D2',
            'accent_purple': '#7B1FA2',
            'button_bg': '#e0e0e0',
            'button_hover': '#d0d0d0',
            'toggle_active': '#4CAF50',
            'toggle_inactive': '#9e9e9e',
        }

    # Determine overall status
    has_errors = (sync_errors and len(sync_errors) > 0) or total_stats.errors > 0
    has_changes = total_stats.created > 0 or total_stats.updated > 0 or total_stats.deleted > 0

    # Apply general dialog style
    dialog.setStyleSheet(f"""
        QDialog {{
            background-color: {colors['bg']};
            color: {colors['text']};
        }}
        QGroupBox {{
            font-weight: bold;
            font-size: 14pt;
            border: 1px solid {colors['border']};
            border-radius: 8px;
            margin-top: 18px;
            padding: 12px;
            padding-top: 12px;
            background-color: {colors['card_bg']};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 12px;
            top: 6px;
            padding: 2px 10px;
            background-color: {colors['card_bg']};
            border-radius: 4px;
            color: {colors['text_secondary']};
        }}
        QRadioButton {{
            font-size: 12pt;
            padding: 8px 15px;
            spacing: 8px;
        }}
        QRadioButton::indicator {{
            width: 18px;
            height: 18px;
        }}
    """)

    main_layout = QVBoxLayout()
    main_layout.setSpacing(15)
    main_layout.setContentsMargins(20, 15, 20, 15)

    # ═══════════════════════════════════════════════════════════════════════════
    # HEADER SECTION - Status banner with icon
    # ═══════════════════════════════════════════════════════════════════════════
    header_frame = QFrame()
    header_frame.setFrameShape(QFrame.Shape.StyledPanel)
    
    # Choose header style based on status
    if has_errors:
        status_icon = "⚠️"
        status_text = "Synchronization Completed with Issues"
        header_color = colors['accent_warning']
        header_bg = f"rgba(255, 152, 0, 0.15)" if not is_dark_mode else "rgba(255, 152, 0, 0.2)"
    else:
        status_icon = "✅"
        status_text = "Synchronization Completed Successfully"
        header_color = colors['accent_success']
        header_bg = f"rgba(76, 175, 80, 0.12)" if not is_dark_mode else "rgba(76, 175, 80, 0.18)"
    
    header_frame.setStyleSheet(f"""
        QFrame {{
            background: {header_bg};
            border: 2px solid {header_color};
            border-radius: 12px;
            padding: 5px;
        }}
    """)
    
    header_layout = QHBoxLayout(header_frame)
    header_layout.setContentsMargins(20, 15, 20, 15)
    
    # Status icon (large)
    icon_label = QLabel(status_icon)
    icon_label.setStyleSheet(f"font-size: 28pt; background: transparent;")
    header_layout.addWidget(icon_label)
    
    # Status text
    status_label = QLabel(status_text)
    status_label.setStyleSheet(f"""
        font-size: 16pt;
        font-weight: bold;
        color: {header_color};
        background: transparent;
        padding-left: 10px;
    """)
    header_layout.addWidget(status_label)
    header_layout.addStretch()
    
    main_layout.addWidget(header_frame)

    # ═══════════════════════════════════════════════════════════════════════════
    # STATISTICS CARDS - Visual summary of key metrics
    # ═══════════════════════════════════════════════════════════════════════════
    stats_frame = QFrame()
    stats_frame.setObjectName("statsContainer")
    stats_frame.setStyleSheet(f"""
        QFrame#statsContainer {{
            background: transparent;
            border: none;
        }}
    """)
    stats_layout = QHBoxLayout(stats_frame)
    stats_layout.setSpacing(10)
    stats_layout.setContentsMargins(0, 8, 0, 8)

    def create_stat_card(value, label, icon, accent_color, card_id):
        """Creates a statistics card widget with unique styling."""
        card = QFrame()
        card.setObjectName(card_id)
        card.setStyleSheet(f"""
            QFrame#{card_id} {{
                background-color: {colors['card_bg']};
                border: 1px solid {colors['border']};
                border-radius: 8px;
                border-left: 4px solid {accent_color};
                padding: 8px;
            }}
            QFrame#{card_id} QLabel {{
                background: transparent;
                border: none;
            }}
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(12, 8, 12, 8)
        card_layout.setSpacing(2)
        
        # Combined icon and value on same line
        value_label = QLabel(f"{icon}  {value}")
        value_label.setStyleSheet(f"""
            font-size: 18pt;
            font-weight: bold;
            color: {accent_color};
        """)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(value_label)
        
        # Label below
        label_lbl = QLabel(label)
        label_lbl.setStyleSheet(f"""
            font-size: 12pt;
            color: {colors['text_secondary']};
        """)
        label_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(label_lbl)
        
        return card

    # Calculate total decks info
    total_decks = len(deck_results) if deck_results else 0
    successful_decks = len([r for r in deck_results if r.success]) if deck_results else 0

    # Add statistic cards with unique IDs
    stats_layout.addWidget(create_stat_card(
        total_stats.created, "Created", "➕", colors['accent_success'], "cardCreated"
    ))
    stats_layout.addWidget(create_stat_card(
        total_stats.updated, "Updated", "✏️", colors['accent_info'], "cardUpdated"
    ))
    stats_layout.addWidget(create_stat_card(
        total_stats.deleted, "Deleted", "🗑️", colors['accent_purple'], "cardDeleted"
    ))
    stats_layout.addWidget(create_stat_card(
        total_stats.skipped, "Skipped", "⏸️", "#888888" if is_dark_mode else "#666666", "cardSkipped"
    ))
    stats_layout.addWidget(create_stat_card(
        total_stats.errors + len(sync_errors or []), "Errors", "⚠️", colors['accent_error'], "cardErrors"
    ))
    if total_decks > 0:
        stats_layout.addWidget(create_stat_card(
            f"{successful_decks}/{total_decks}", "Decks", "📚", colors['accent_info'], "cardDecks"
        ))

    main_layout.addWidget(stats_frame)

    # ═══════════════════════════════════════════════════════════════════════════
    # VIEW MODE TOGGLE - Modern toggle buttons
    # ═══════════════════════════════════════════════════════════════════════════
    view_group = QGroupBox("View Mode")
    view_layout = QHBoxLayout()
    view_layout.setSpacing(8)
    
    # Create styled radio buttons for view modes
    simplified_radio = QRadioButton("📊 Summary")
    detailed_radio = QRadioButton("📑 Full Details")
    errors_radio = QRadioButton("⚠️ Errors Only")
    
    simplified_radio.setChecked(True)
    
    # Style the radio buttons as toggle buttons
    radio_style = f"""
        QRadioButton {{
            background-color: {colors['button_bg']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            padding: 10px 18px;
            font-size: 12pt;
            color: {colors['text']};
        }}
        QRadioButton:hover {{
            background-color: {colors['button_hover']};
        }}
        QRadioButton:checked {{
            background-color: {colors['accent_success']};
            color: white;
            border-color: {colors['accent_success']};
            font-weight: bold;
        }}
        QRadioButton::indicator {{
            width: 0;
            height: 0;
        }}
    """
    
    simplified_radio.setStyleSheet(radio_style)
    detailed_radio.setStyleSheet(radio_style)
    errors_radio.setStyleSheet(radio_style)
    
    # Group radiobuttons
    radio_group = QButtonGroup()
    radio_group.addButton(simplified_radio)
    radio_group.addButton(detailed_radio)
    radio_group.addButton(errors_radio)
    
    view_layout.addWidget(simplified_radio)
    view_layout.addWidget(detailed_radio)
    view_layout.addWidget(errors_radio)
    view_layout.addStretch()
    
    view_group.setLayout(view_layout)
    main_layout.addWidget(view_group)

    # ═══════════════════════════════════════════════════════════════════════════
    # DETAILS TEXT AREA - Scrollable content area
    # ═══════════════════════════════════════════════════════════════════════════
    details_group = QGroupBox("Details")
    details_layout = QVBoxLayout()
    details_layout.setContentsMargins(10, 10, 10, 10)
    
    details_text = QTextEdit()
    details_text.setReadOnly(True)
    details_text.setStyleSheet(f"""
        QTextEdit {{
            font-family: 'SF Mono', 'Monaco', 'Consolas', 'Courier New', monospace;
            font-size: 12pt;
            line-height: 1.5;
            padding: 15px;
            border-radius: 6px;
            border: 1px solid {colors['border']};
            background-color: {colors['card_bg']};
            color: {colors['text']};
            selection-background-color: {colors['accent_info']};
        }}
        QScrollBar:vertical {{
            background: {colors['bg']};
            width: 10px;
            border-radius: 5px;
        }}
        QScrollBar::handle:vertical {{
            background: {colors['border']};
            border-radius: 5px;
            min-height: 20px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {colors['text_secondary']};
        }}
    """)

    def update_details_view():
        """Updates details view based on radiobutton selection."""
        details_content = []
        
        if simplified_radio.isChecked():
            details_content = generate_simplified_view(
                total_stats, sync_errors, deck_results
            )
        elif detailed_radio.isChecked():
            details_content = generate_detailed_view(
                total_stats, sync_errors, deck_results
            )
        else:
            details_content = generate_errors_view(
                total_stats, sync_errors, deck_results
            )
        
        details_text.setPlainText("\n".join(details_content))

    # Connect radiobutton changes to view update
    simplified_radio.toggled.connect(update_details_view)
    detailed_radio.toggled.connect(update_details_view)
    errors_radio.toggled.connect(update_details_view)

    # Set initial content
    update_details_view()
    
    details_layout.addWidget(details_text)
    details_group.setLayout(details_layout)
    main_layout.addWidget(details_group)

    # ═══════════════════════════════════════════════════════════════════════════
    # ACTION BUTTONS - Close and optional actions
    # ═══════════════════════════════════════════════════════════════════════════
    button_layout = QHBoxLayout()
    button_layout.setContentsMargins(0, 10, 0, 0)
    
    # Spacer to push button to the right
    button_layout.addStretch()
    
    # Close button with accent styling
    close_button = QPushButton("✓ Close")
    close_button.setMinimumWidth(140)
    close_button.setStyleSheet(f"""
        QPushButton {{
            background-color: {colors['accent_success']};
            color: white;
            font-size: 12pt;
            font-weight: bold;
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
        }}
        QPushButton:hover {{
            background-color: #45a049;
        }}
        QPushButton:pressed {{
            background-color: #3d8b40;
        }}
    """)
    close_button.clicked.connect(dialog.accept)
    button_layout.addWidget(close_button)
    
    main_layout.addLayout(button_layout)

    dialog.setLayout(main_layout)
    safe_exec_dialog(dialog)


# ========================================================================================
# INTERFACE UPDATE FUNCTIONS (consolidated from interface_updater.py)
# ========================================================================================


def refresh_anki_interface():
    """
    Updates the Anki interface after synchronization.

    Updates:
    - Deck list on main screen
    - Card counters
    - Reviewer interface if active
    - Browser if open
    """
    if not mw:
        add_debug_message(
            "❌ MainWindow not available for update", "INTERFACE_UPDATE"
        )
        return

    try:
        add_debug_message(
            "🔄 Starting Anki interface update", "INTERFACE_UPDATE"
        )

        # 1. Update deck list on main screen
        if hasattr(mw, "deckBrowser") and mw.deckBrowser:
            add_debug_message("📂 Updating deck list", "INTERFACE_UPDATE")
            mw.deckBrowser.refresh()

        # 2. Update reviewer if active
        if hasattr(mw, "reviewer") and mw.reviewer and mw.state == "review":
            add_debug_message("📝 Updating reviewer", "INTERFACE_UPDATE")
            # Force recalculation of card count
            if hasattr(mw.reviewer, "_updateCounts"):
                mw.reviewer._updateCounts()

        # 3. Update browser if open
        if hasattr(mw, "browser") and mw.browser:
            add_debug_message("🔍 Updating browser", "INTERFACE_UPDATE")
            mw.browser.model.reset()
            mw.browser.form.tableView.selectRow(0)

        # 4. Update title bar and general interface
        if hasattr(mw, "setWindowTitle") and mw.col:
            # Keep original title but force internal recalculation
            mw.col.reset()

        # 5. General interface reset trigger
        if hasattr(mw, "reset"):
            add_debug_message(
                "🔄 Running general interface reset", "INTERFACE_UPDATE"
            )
            mw.reset()

        add_debug_message(
            "✅ Anki interface updated successfully", "INTERFACE_UPDATE"
        )

    except Exception as e:
        add_debug_message(f"❌ Error updating interface: {e}", "INTERFACE_UPDATE")


def refresh_deck_list():
    """
    Specifically updates the deck list on the main screen.
    """
    if not mw or not hasattr(mw, "deckBrowser"):
        return

    try:
        add_debug_message("📂 Updating deck list", "INTERFACE_UPDATE")
        mw.deckBrowser.refresh()
    except Exception as e:
        add_debug_message(
            f"❌ Error updating deck list: {e}", "INTERFACE_UPDATE"
        )


def refresh_counts():
    """
    Updates card counters across all interfaces.
    """
    if not mw:
        return

    try:
        add_debug_message("🔢 Updating card counters", "INTERFACE_UPDATE")

        # Force recalculation of counts in collection
        if mw.col:
            mw.col.sched.reset()

        # Update deck browser
        if hasattr(mw, "deckBrowser") and mw.deckBrowser:
            mw.deckBrowser.refresh()

        # Update reviewer if active
        if hasattr(mw, "reviewer") and mw.reviewer and mw.state == "review":
            if hasattr(mw.reviewer, "_updateCounts"):
                mw.reviewer._updateCounts()

    except Exception as e:
        add_debug_message(f"❌ Error updating counters: {e}", "INTERFACE_UPDATE")


def ensure_interface_refresh():
    """
    Ensures the interface is updated, using multiple strategies.

    This function uses different methods to ensure the interface
    is updated regardless of Anki's current state.
    """
    if not mw:
        return

    try:
        add_debug_message(
            "🎯 Running full interface update", "INTERFACE_UPDATE"
        )

        # Method 1: Collection reset (most complete)
        if mw.col:
            mw.col.reset()

        # Method 2: Main interface reset
        if hasattr(mw, "reset"):
            mw.reset()

        # Method 3: Component-specific update
        refresh_deck_list()
        refresh_counts()

        add_debug_message(
            "✅ Full interface update completed", "INTERFACE_UPDATE"
        )

    except Exception as e:
        add_debug_message(f"❌ Error in full update: {e}", "INTERFACE_UPDATE")


# ========================================================================================
# MAIN SYNCHRONIZATION FUNCTIONS
# ========================================================================================


def _is_anki_ready():
    """Checks if Anki is ready for operations."""
    return mw and hasattr(mw, "col") and mw.col


def _is_anki_decks_ready():
    """Checks if Anki is ready for deck operations."""
    return _is_anki_ready() and hasattr(mw.col, "decks")


def syncDecks(selected_deck_names=None, selected_deck_urls=None, new_deck_mode=False):
    """
    Synchronizes all remote decks with their sources.

    This is the main synchronization function that:
    1. Checks if there are disabled students who need to have their data removed
    2. Downloads data from remote decks
    3. Processes and validates data
    4. Updates Anki database
    5. Shows progress to user
    6. Automatically updates names if configured

    Args:
        selected_deck_names: List of deck names to synchronize.
                           If None, synchronizes all decks.
        selected_deck_urls: List of deck URLs to synchronize.
                          If provided, takes precedence over selected_deck_names.
        new_deck_mode: If True, indicates this synchronization is for a newly added deck.
    """
    # Check if mw.col is available
    if not _is_anki_ready():
        StyledMessageBox.warning(None, "Anki Not Ready", "Anki is not ready. Please try again in a few moments.")
        return

    col = mw.col
    
    remote_decks = get_remote_decks()

    # Clear previous debug messages
    clear_debug_messages()

    # Determine which decks to synchronize (needed to setup progress dialog)
    deck_keys = _get_deck_keys_to_sync(
        remote_decks, selected_deck_names, selected_deck_urls
    )
    total_decks = len(deck_keys)

    # Check if there are decks to synchronize
    if total_decks == 0:
        _show_no_decks_message(selected_deck_names)
        return

    # Check if backup is enabled (affects progress steps)
    meta_config = get_meta().get("config", {})
    backup_enabled = meta_config.get("auto_backup_enabled", False)

    # Setup and show progress bar (includes backup step if enabled)
    progress = _setup_progress_dialog(total_decks, include_backup=backup_enabled)
    status_msgs = []
    
    # Step 0: Backup before sync (if enabled)
    if backup_enabled:
        status_msgs.append("💾 Creating backup...")
        _update_progress_text(progress, status_msgs)
        progress.setValue(0)
        mw.app.processEvents()
        
        add_debug_message("💾 Creating automatic backup before synchronization...", "SYNC")
        try:
            backup_manager = SimplifiedBackupManager()
            backup_success = backup_manager.create_auto_backup()
            if backup_success:
                add_debug_message("✅ Automatic backup created", "SYNC")
                status_msgs.append("✅ Automatic backup created")
            else:
                add_debug_message("⚠️ Failed to create automatic backup", "SYNC")
                status_msgs.append("⚠️ Backup skipped")
        except Exception as e:
            add_debug_message(f"⚠️ Error creating automatic backup: {e}", "SYNC")
            status_msgs.append("⚠️ Backup error (continuing...)")
        
        _update_progress_text(progress, status_msgs)
        progress.setValue(1)
        mw.app.processEvents()

    # Update existing note type templates before synchronization
    status_msgs.append("🎨 Updating card templates...")
    _update_progress_text(progress, status_msgs)
    mw.app.processEvents()
    
    try:
        add_debug_message("🔄 Updating existing note type templates...", "SYNC")
        updated_count = update_existing_note_type_templates(col, [])
        add_debug_message(f"✅ {updated_count} note types successfully updated", "SYNC")
        
        status_msgs.append(f"✅ Templates updated ({updated_count} types)")
        _update_progress_text(progress, status_msgs)
        
    except Exception as e:
        add_debug_message(f"⚠️ Error updating templates: {e}", "SYNC")
        
        status_msgs.append("⚠️ Template update failed (continuing...)")
        _update_progress_text(progress, status_msgs)
        # Continue synchronization even if template update failed

    # Manage cleanups in a consolidated way to avoid multiple confirmations
    try:
        missing_cleanup_result, cleanup_result = _handle_consolidated_cleanup(remote_decks)
        
        if missing_cleanup_result:
             status_msgs.append("🧹 Removed [MISSING S.] data")
             _update_progress_text(progress, status_msgs)
             
        if cleanup_result:
             count = cleanup_result.get('disabled_students_count', 0)
             status_msgs.append(f"🧹 Removed data for {count} disabled student(s)")
             _update_progress_text(progress, status_msgs)
             
    except SyncAborted:
        add_debug_message("🛑 SYNC: User aborted synchronization.", "SYNC")
        progress.close()
        return

    # Check if no cleanup was needed and report it (Explicit feedback)
    if not missing_cleanup_result and not cleanup_result:
         status_msgs.append("🧹 Cleanup verification: OK")
         _update_progress_text(progress, status_msgs)

    # Initialize statistics system
    stats_manager = SyncStatsManager()
    sync_errors = []

    # Add initial debug message
    add_debug_message(
        f"🎬 DEBUG SYSTEM ACTIVATED - Total decks: {total_decks}", "SYNC"
    )
    _update_progress_text(progress, status_msgs)

    # Start step counter (1 if backup was done, 0 otherwise)
    step = 1 if backup_enabled else 0
    try:
        # Synchronize each deck
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

                # Create deck result
                deck_name = remote_decks[deckKey].get("local_deck_name", "Unknown")
                deck_url = remote_decks[deckKey].get("remote_deck_url", "")
                
                # Check if the deck was new and update sync status
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

                add_debug_message(f"✅ Deck completed: {deckKey}", "SYNC")

                # Explicitly state deck sync is finished
                status_msgs.append(f"✅ {deck_name}: Synchronization finished")
                _update_progress_text(progress, status_msgs)

            except SyncError as e:
                step, sync_errors = _handle_sync_error(
                    e, deckKey, remote_decks, progress, status_msgs, sync_errors, step
                )

                # Add failure result
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

                # Add unexpected error result
                deck_name = remote_decks[deckKey].get("local_deck_name", "Unknown")
                deck_url = remote_decks[deckKey].get("remote_deck_url", "")
                failed_result = DeckSyncResult(
                    deck_name=deck_name,
                    deck_key=deckKey,
                    deck_url=deck_url,
                    success=False,
                    stats=SyncStats(),
                    error_message=f"Unexpected error: {str(e)}",
                )
                failed_result.stats.add_error(f"Unexpected error: {str(e)}")
                stats_manager.add_deck_result(failed_result)
                continue



        # Get statistics summary
        summary = stats_manager.get_summary()
        successful_decks = len(stats_manager.get_successful_decks())
        deck_results = stats_manager.deck_results  # Get results per deck

        add_debug_message(
            f"🎯 Calling _finalize_sync_cleanup - successful_decks: {successful_decks}, total_decks: {total_decks}",
            "SYNC",
        )
        
        # Finalize cleanup
        removed_subdecks = _finalize_sync_cleanup(progress)

        # Define callback for AnkiWeb sync (to be called after summary window closes)
        def execute_ankiweb_sync_after_close():
            """Callback to execute AnkiWeb synchronization after the user closes the summary window"""
            add_debug_message(
                "🔄 Checking AnkiWeb synchronization configuration...", "SYNC"
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
                            f"❌ AnkiWeb sync failed: {ankiweb_result['error']}", "SYNC"
                        )
                else:
                    add_debug_message("⏹️ AnkiWeb sync disabled", "SYNC")
            except Exception as ankiweb_error:
                add_debug_message(
                    f"❌ AnkiWeb synchronization error: {ankiweb_error}", "SYNC"
                )

        # Define callback to open summary window (to be called after progress bar closes)
        def open_summary_window():
            _show_sync_summary_new(
                sync_errors,
                summary["total_stats"],
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

        # Set the action to perform when progress dialog is closed
        on_close_action = open_summary_window

    finally:
        # Show completion status with Close button (dialog stays open)
        if progress.isVisible():
            _show_sync_completion(
                progress, 
                status_msgs, 
                total_decks, 
                successful_decks if 'successful_decks' in dir() else 0, 
                sync_errors if 'sync_errors' in dir() else None,
                on_close_callback=on_close_action if 'on_close_action' in locals() else None
            )


def _get_deck_keys_to_sync(remote_decks, selected_deck_names, selected_deck_urls=None):
    """
    Determines which deck keys should be synchronized.
    Now works with hash keys from the new structure.

    Args:
        remote_decks: Dictionary of remote decks (hash_key -> deck_info)
        selected_deck_names: Names of selected decks or None
        selected_deck_urls: URLs of selected decks or None

    Returns:
        list: List of hash keys to be synchronized
    """

    # If specific URLs were provided, convert to spreadsheet IDs
    if selected_deck_urls is not None:
        filtered_keys = []
        for url in selected_deck_urls:
            # Extract spreadsheet ID
            spreadsheet_id = get_spreadsheet_id_from_url(url)

            if spreadsheet_id in remote_decks:
                filtered_keys.append(spreadsheet_id)
        return filtered_keys

    # Check if mw.col and mw.col.decks are available
    if not _is_anki_decks_ready():
        return []

    assert mw.col is not None  # Type hint for checker

    # Create name to hash key mapping
    name_to_key = {}
    for hash_key, deck_info in remote_decks.items():
        # Check if deck still exists
        local_deck_id = deck_info.get("local_deck_id")
        deck = mw.col.decks.get(local_deck_id) if local_deck_id is not None else None

        if deck:
            # Use current deck name
            actual_deck_name = deck["name"]
            name_to_key[actual_deck_name] = hash_key

            # Also map config name if different
            config_deck_name = deck_info.get("local_deck_name")
            if config_deck_name and config_deck_name != actual_deck_name:
                name_to_key[config_deck_name] = hash_key

    # If specific names were selected, filter by them
    if selected_deck_names is not None:
        filtered_keys = []
        for deck_name in selected_deck_names:
            if deck_name in name_to_key:
                filtered_keys.append(name_to_key[deck_name])
        return filtered_keys

    # Otherwise, return all hash keys
    return list(remote_decks.keys())


def _show_no_decks_message(selected_deck_names):
    """Shows message when there are no decks to synchronize."""
    if selected_deck_names is not None:
        StyledMessageBox.warning(
            None,
            "Decks Not Found",
            f"None of the selected decks were found in the configuration.",
            detailed_text=f"Selected decks: {', '.join(selected_deck_names)}"
        )
    else:
        StyledMessageBox.information(None, "No Remote Decks", "No remote decks configured for synchronization.")


class LogProgressDialog(QDialog):
    """
    Custom progress dialog with a scrollable log area.
    Mimics QProgressDialog interface used in this module.
    """
    def __init__(self, title, message, min_val, max_val, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📚 Deck Synchronization")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Title/Status label
        self.label = QLabel(title)
        self.label.setWordWrap(True)
        self.label.setStyleSheet("font-weight: bold; font-size: 14pt; color: white;")
        layout.addWidget(self.label)
        
        # Progress bar
        self.bar = QProgressBar()
        self.bar.setRange(min_val, max_val)
        self.bar.setValue(0)
        self.bar.setTextVisible(True)
        layout.addWidget(self.bar)
        
        # Scrollable log area
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)
        
        # Cancel/Close button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        layout.addWidget(self.cancel_btn, 0, AlignRight)
        
        # Initial sizing
        self.resize(600, 450)
        
        # Apply style
        self.setStyleSheet("""
            QDialog {
                background-color: #2d2d2d;
                color: #ffffff;
                font-size: 12pt;
            }
            QLabel {
                color: #ffffff;
                border: none;
            }
            QTextEdit {
                background-color: #1e1e1e;
                color: #e0e0e0;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                font-family: monospace;
                font-size: 11pt;
            }
            QProgressBar {
                border: none;
                border-radius: 4px;
                background-color: #404040;
                height: 24px;
                text-align: center;
                color: white;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:1 #8BC34A);
                border-radius: 4px;
            }
            QPushButton {
                background-color: #505050;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #606060;
            }
        """)

    def setValue(self, val):
        self.bar.setValue(val)
        
    def maximum(self):
        return self.bar.maximum()
        
    def setLabelText(self, text):
        import html
        # Formatting to increase spacing
        lines = text.split('\n')
        html_parts = []
        for line in lines:
            if not line:
                continue
            escaped = html.escape(line)
            # Use div with margin and line-height for spacing
            html_parts.append(f"<div style='margin-bottom: 6px; line-height: 1.45;'>{escaped}</div>")
        
        full_html = "".join(html_parts)
        self.log_area.setHtml(full_html)
        
        # Scroll to bottom
        cursor = self.log_area.textCursor()
        from .compat import QTextCursor
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_area.setTextCursor(cursor)
        
    def setCancelButton(self, btn):
        if btn is None:
            self.cancel_btn.hide()
        else:
            self.layout().replaceWidget(self.cancel_btn, btn)
            self.cancel_btn.deleteLater()
            self.cancel_btn = btn
            self.cancel_btn.show()

    def setCancelButtonText(self, text):
        self.cancel_btn.setText(text)
        
    def setTitle(self, text):
        """Updates the title label."""
        self.label.setText(text)
        
    def appendMessage(self, text):
        """Appends a message to the log area without clearing history."""
        import html
        escaped = html.escape(text)
        # Create styled HTML block
        html_block = f"<div style='margin-bottom: 6px; line-height: 1.45;'>{escaped}</div>"
        self.log_area.append(html_block)
        
        # Scroll to bottom
        cursor = self.log_area.textCursor()
        from .compat import QTextCursor
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_area.setTextCursor(cursor)
        
    def setAutoClose(self, b): pass
    def setAutoReset(self, b): pass
    def setMinimumDuration(self, ms): pass


def _setup_progress_dialog(total_decks, include_backup=False):
    """
    Configures and returns a modern, user-friendly progress dialog with scrollable log.
    
    Args:
        total_decks: Total number of decks to calculate bar maximum
        include_backup: If True, adds 1 step for the backup phase

    Returns:
        LogProgressDialog: Configured progress dialog
    """
    # Calculate total steps: backup (if enabled) + deck steps
    backup_steps = 1 if include_backup else 0
    total_steps = backup_steps + (total_decks * 3)
    
    initial_message = "🔄 Synchronizing..."
    
    progress = LogProgressDialog(initial_message, "", 0, total_steps, mw)
    progress.show()
    mw.app.processEvents()
    return progress


def _show_sync_completion(progress, status_msgs, total_decks, successful_decks, errors=None, on_close_callback=None):
    """
    Shows sync completion status and adds a Close button.
    
    Args:
        progress: The progress dialog
        status_msgs: List of status messages
        total_decks: Total decks attempted
        successful_decks: Number of successful syncs
        errors: List of errors (if any)
        on_close_callback: Optional function to call when dialog is closed
    """
    # Set progress to maximum
    progress.setValue(progress.maximum())
    
    # Build completion status
    if successful_decks == total_decks:
        completion_icon = "✅"
        completion_status = "Synchronization Complete!"
    elif successful_decks > 0:
        completion_icon = "⚠️"
        completion_status = "Synchronization Completed with Issues"
    else:
        completion_icon = "❌"
        completion_status = "Synchronization Failed"

    # Update title to show completion status
    if hasattr(progress, 'setTitle'):
        progress.setTitle(f"{completion_icon} {completion_status}")
    
    # Append simple finish message to log instead of replacing it
    if hasattr(progress, 'appendMessage'):
        progress.appendMessage("-" * 40)
        progress.appendMessage(f"Status: {completion_status}")
        progress.appendMessage(f"Results: {successful_decks}/{total_decks} decks synchronized.")
        progress.appendMessage("-" * 40)
    else:
        # Fallback if somehow using standard dialog
        completion_msg = f"{completion_icon} {completion_status}\n\n"
        completion_msg += f"📊 Results: {successful_decks}/{total_decks} decks synchronized successfully"
        if errors:
            completion_msg += f"\n⚠️ {len(errors)} error(s) occurred"
        progress.setLabelText(completion_msg)
    
    # Add Close button
    from .compat import QPushButton
    close_btn = QPushButton("Close")
    
    def on_close_click():
        progress.close()
        if on_close_callback:
            on_close_callback()
            
    close_btn.clicked.connect(on_close_click)
    
    progress.setCancelButton(close_btn)
    progress.setCancelButtonText("Close")
    
    mw.app.processEvents()


def _update_progress_text(
    progress, status_msgs, max_lines=None, debug_messages=None, show_debug=False
):
    """
    Updates progress bar log with all messages.
    
    Args:
        progress: LogProgressDialog instance
        status_msgs: List of status messages
        max_lines: Ignored (kept for compatibility)
        debug_messages: List of debug messages
        show_debug: If True, shows debug messages in interface
    """
    all_text_lines = []

    # Add all status messages
    if status_msgs:
        all_text_lines.extend(status_msgs)

    # Add debug messages if provided AND requested
    if debug_messages and show_debug:
        all_text_lines.append("")
        all_text_lines.append("=== DEBUG MESSAGES ===")
        all_text_lines.extend(debug_messages)

    # Join all lines
    text = "\n".join(all_text_lines)

    # Update log area (no manual wrapping needed as QTextEdit handles it)
    progress.setLabelText(text)

    # Force interface update
    mw.app.processEvents()


def _sync_single_deck(
    remote_decks, deckKey, progress, status_msgs, step, debug_messages=None
):
    """
    Synchronizes a single deck.

    Args:
        remote_decks: Remote decks dictionary
        deckKey: Deck key to synchronize
        progress: Progress dialog
        status_msgs: List of status messages
        step: Current progress step

    Returns:
        tuple: (step, deck_sync_increment, current_stats)
    """
    from .deck_manager import DeckNameManager
    from .deck_manager import DeckRecreationManager


    # Check if mw.col and mw.col.decks are available
    if not _is_anki_decks_ready():
        raise SyncError("Anki is not ready. Please try again in a few moments.")

    assert mw.col is not None  # Type hint for checker

    currentRemoteInfo = remote_decks[deckKey]
    local_deck_id = currentRemoteInfo["local_deck_id"]
    remote_deck_url = currentRemoteInfo["remote_deck_url"]
    add_debug_message(f"📋 Local Deck ID: {local_deck_id}", "SYNC")
    add_debug_message(f"🔗 Remote URL: {remote_deck_url}", "SYNC")

    # Check if deck exists or needs to be recreated
    was_recreated, current_deck_id, current_deck_name = (
        DeckRecreationManager.recreate_deck_if_missing(currentRemoteInfo)
    )

    if was_recreated and current_deck_id is not None and current_deck_name is not None:
        # Capture old ID before update for correct logging
        old_deck_id = local_deck_id

        # Update info in configuration
        DeckRecreationManager.update_deck_info_after_recreation(
            currentRemoteInfo, current_deck_id, current_deck_name
        )

        # IMPORTANT: Save local_deck_id changes immediately after recreation
        # This ensures the new ID is persisted even if a subsequent error occurs
        save_remote_decks(remote_decks)
        add_debug_message(
            f"[CONFIG_SAVE] local_deck_id updated and saved after recreation: {old_deck_id} -> {current_deck_id}",
            "SYNC",
        )

        # Update local variables
        local_deck_id = current_deck_id

        # Inform about recreation
        msg = f"♻️ Recreating deck: '{current_deck_name}'"
        status_msgs.append(msg)
        _update_progress_text(progress, status_msgs)

        step += 1
        progress.setValue(step)
        mw.app.processEvents()

    # Get current deck (can be original or recreated)
    if local_deck_id is None:
        raise ValueError("Local deck ID is None")

    # Ensure ID is the correct type for Anki
    from anki.decks import DeckId

    deck_id: DeckId = DeckId(local_deck_id)
    deck = mw.col.decks.get(deck_id)
    if not deck:
        raise ValueError(f"Failed to get deck: {deck_id}")

    deckName = deck["name"]
    add_debug_message(f"📋 Current deck: '{deckName}' (ID: {deck_id})", "SYNC")

    # Update info in configuration with actual name used
    currentRemoteInfo["local_deck_name"] = deckName

    # Validate URL before trying to sync and get TSV URL for download
    tsv_url = validate_url(remote_deck_url)

    # 1. Download
    msg = f"📥 {deckName}: Downloading data..."
    status_msgs.append(msg)
    _update_progress_text(progress, status_msgs)

    # Get list of enabled students for this deck
    enabled_students = get_selected_students_for_deck(remote_deck_url)
    add_debug_message(
        f"🎓 Enabled students for this deck: {list(enabled_students)}",
        "STUDENTS",
    )

    remoteDeck = getRemoteDeck(tsv_url, enabled_students=list(enabled_students))

    # NEW: Debug to check loaded notes
    notes_count = (
        len(remoteDeck.notes)
        if hasattr(remoteDeck, "notes") and remoteDeck.notes
        else 0
    )
    add_debug_message(
        f"📊 Notes loaded from remote deck: {notes_count}", "REMOTE_DECK"
    )

    step += 1
    progress.setValue(step)
    mw.app.processEvents()

    # Update remote_deck_name with name extracted from URL
    new_remote_name_from_url = DeckNameManager.extract_remote_name_from_url(
        remote_deck_url
    )
    stored_remote_name = currentRemoteInfo.get("remote_deck_name")
    
    # Check if we could extract a valid name from URL
    if not new_remote_name_from_url:
        add_debug_message(
            f"[NAME_EXTRACT_ERROR] Could not extract name from URL: {remote_deck_url}",
            "SYNC",
        )
        # Use stored name as fallback
        new_remote_name_from_url = stored_remote_name or "Untitled Deck"
    
    # Defensive initialization of current_remote_name
    current_remote_name = stored_remote_name or new_remote_name_from_url

    # IMPORTANT: Improved logic to resolve conflicts dynamically
    # Check if remote name changed and re-evaluate conflict resolution
    should_update = False
    if stored_remote_name != new_remote_name_from_url:
        # Check if stored name has conflict suffix
        if stored_remote_name and " #conflict" in stored_remote_name:
            # Name has conflict suffix - check if still necessary
            add_debug_message(
                f"[CONFLICT_REEVALUATE] Re-evaluating conflict: '{stored_remote_name}' vs new name '{new_remote_name_from_url}'",
                "SYNC",
            )

            # Use centralized DeckNameManager for conflict resolution
            resolved_new_name = DeckNameManager.resolve_remote_name_conflict(
                remote_deck_url, new_remote_name_from_url
            )

            # If resolved name equals original name, there is no more conflict
            if resolved_new_name == new_remote_name_from_url:
                # Conflict was resolved - can use original name
                should_update = True
                current_remote_name = new_remote_name_from_url
                add_debug_message(
                    f"[CONFLICT_RESOLVED] Conflict resolved! '{stored_remote_name}' → '{new_remote_name_from_url}'",
                    "SYNC",
                )

                # Also update local_deck_name to remove suffix
                old_local_name = currentRemoteInfo.get("local_deck_name", "")
                if old_local_name and " #conflict" in old_local_name:
                    # Remove suffix from local name as well
                    new_local_name = old_local_name.split(" #conflict")[0]
                    add_debug_message(
                        f"[CONFLICT_RESOLVED] Updating local_deck_name: '{old_local_name}' → '{new_local_name}'",
                        "SYNC",
                    )

                    # Update deck name in Anki
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
                                    f"[ANKI_UPDATE] Deck renamed in Anki: '{old_anki_name}' → '{new_local_name}'",
                                    "SYNC",
                                )
                    except Exception as e:
                        add_debug_message(
                            f"[ANKI_ERROR] Error renaming deck in Anki: {e}", "SYNC"
                        )

                    # Update in configuration
                    currentRemoteInfo["local_deck_name"] = new_local_name
                    remote_decks[deckKey]["local_deck_name"] = new_local_name

            else:
                # Still dynamic conflict, but suffix might have changed
                if resolved_new_name != stored_remote_name:
                    should_update = True
                    current_remote_name = resolved_new_name
                    add_debug_message(
                        f"[CONFLICT_UPDATE] Updating conflict suffix: '{stored_remote_name}' → '{resolved_new_name}'",
                        "SYNC",
                    )
                else:
                    current_remote_name = stored_remote_name  # Keep existing name
                    add_debug_message(
                        f"[CONFLICT_UNCHANGED] Keeping existing resolution: '{stored_remote_name}'",
                        "SYNC",
                    )

        else:
            # Name doesn't have conflict, apply normal resolution with DeckNameManager
            resolved_remote_name = DeckNameManager.resolve_remote_name_conflict(
                remote_deck_url, new_remote_name_from_url
            )

            if resolved_remote_name != stored_remote_name:
                should_update = True
                current_remote_name = resolved_remote_name
                add_debug_message(
                    f"[CONFLICT_RESOLVE] Applying resolution: '{new_remote_name_from_url}' → '{resolved_remote_name}'",
                    "SYNC",
                )
            else:
                current_remote_name = stored_remote_name  # Keep existing name
                add_debug_message(
                    f"[CONFLICT_KEEP] Keeping resolved name: '{stored_remote_name}'",
                    "SYNC",
                )

    else:
        # Name didn't change, no update needed
        add_debug_message(
            f"[CONFLICT_SKIP] Remote name didn't change, keeping: '{stored_remote_name}'",
            "SYNC",
        )
        current_remote_name = stored_remote_name

    # ROBUST APPROACH: Always recreate local_deck_name and check if it changed
    from .deck_manager import DeckNameManager

    # Recreate local_deck_name based on current remote_deck_name
    expected_local_deck_name = DeckNameManager.generate_local_name(current_remote_name)
    current_local_deck_name = currentRemoteInfo.get("local_deck_name", "")

    add_debug_message("[DECK_NAME_CHECK] Checking name consistency:", "SYNC")
    add_debug_message(f"[DECK_NAME_CHECK] - Remote: '{current_remote_name}'", "SYNC")
    add_debug_message(
        f"[DECK_NAME_CHECK] - Current local: '{current_local_deck_name}'", "SYNC"
    )
    add_debug_message(
        f"[DECK_NAME_CHECK] - Expected local: '{expected_local_deck_name}'", "SYNC"
    )

    # Check if local_deck_name needs update
    local_name_needs_update = current_local_deck_name != expected_local_deck_name

    # Apply necessary updates
    if should_update or local_name_needs_update:
            if should_update:
                add_debug_message("[UPDATE_REASON] remote_deck_name changed", "SYNC")
            if local_name_needs_update:
                add_debug_message("[UPDATE_REASON] local_deck_name inconsistent", "SYNC")

            # Update local_deck_name in meta.json
            if local_name_needs_update:
                DeckNameManager._update_name_in_config(
                    remote_deck_url, expected_local_deck_name
                )
                add_debug_message(
                    f"[LOCAL_NAME_UPDATE] local_deck_name updated: '{current_local_deck_name}' -> '{expected_local_deck_name}'",
                    "SYNC",
                )

            # Sync physical deck name in Anki if necessary
            sync_result = DeckNameManager.sync_deck_with_config(remote_deck_url)
            if sync_result:
                add_debug_message(
                    f"[DECK_SYNC] Physical deck synchronized: ID {sync_result[0]} -> '{sync_result[1]}'",
                    "SYNC",
                )

            # Update configuration if remote_deck_name changed
            if should_update:
                # IMPORTANT: Update note type names BEFORE changing remote_deck_name
                old_remote_name_config = currentRemoteInfo.get("remote_deck_name")
                if old_remote_name_config and old_remote_name_config != current_remote_name:
                    try:
                        from .utils import update_note_type_names_for_deck_rename
                        from .config_manager import get_deck_note_type_ids
                        
                        # Detect actual name present in note types
                        note_types_config = get_deck_note_type_ids(remote_deck_url)
                        actual_old_name = None
                        
                        if note_types_config:
                            # Look for common pattern in note types to extract actual name
                            for note_type_name in note_types_config.values():
                                # Format: "Sheets2Anki - {remote_name} - {student} - {type}"
                                if " - " in note_type_name:
                                    parts = note_type_name.split(" - ")
                                    if len(parts) >= 4 and parts[0] == "Sheets2Anki":
                                        # Reconstruct remote name (can have multiple hyphens)
                                        # Get everything between "Sheets2Anki - " and " - {student}"
                                        start_idx = note_type_name.find("Sheets2Anki - ") + len("Sheets2Anki - ")
                                        # Find last occurrence of " - {student} - {type}"
                                        last_dash_student = note_type_name.rfind(" - " + parts[-2] + " - " + parts[-1])
                                        if last_dash_student > start_idx:
                                            potential_name = note_type_name[start_idx:last_dash_student]
                                            actual_old_name = potential_name
                                            break
                        
                        # If detection failed, use name from configuration
                        old_name_to_use = actual_old_name if actual_old_name else old_remote_name_config
                        
                        add_debug_message(
                            f"[NOTE_TYPE_DETECT] old_remote_name_config: '{old_remote_name_config}'",
                            "SYNC",
                        )
                        add_debug_message(
                            f"[NOTE_TYPE_DETECT] actual_old_name detected: '{actual_old_name}'",
                            "SYNC",
                        )
                        add_debug_message(
                            f"[NOTE_TYPE_DETECT] using for update: '{old_name_to_use}' → '{current_remote_name}'",
                            "SYNC",
                        )
                        
                        updated_count = update_note_type_names_for_deck_rename(
                            remote_deck_url, old_name_to_use, current_remote_name, debug_messages
                        )
                        add_debug_message(
                            f"[NOTE_TYPE_UPDATE] {updated_count} note types updated to new remote_deck_name",
                            "SYNC",
                        )
                        
                        # Sync note types in Anki with updated names
                        if updated_count > 0:
                            try:
                                from .utils import sync_note_type_names_with_config
                                sync_result = sync_note_type_names_with_config(mw.col, remote_deck_url, debug_messages)
                                if sync_result and sync_result.get("renamed_in_anki", 0) > 0:
                                    add_debug_message(
                                        f"[NOTE_TYPE_ANKI_SYNC] {sync_result['renamed_in_anki']} note types renamed in Anki",
                                        "SYNC",
                                    )
                                else:
                                    add_debug_message(
                                        "[NOTE_TYPE_ANKI_SYNC] No note types renamed in Anki",
                                        "SYNC",
                                    )
                            except Exception as anki_sync_error:
                                add_debug_message(
                                    f"[NOTE_TYPE_ANKI_ERROR] Error syncing note types in Anki: {anki_sync_error}",
                                    "SYNC",
                                )
                    except Exception as note_type_error:
                        add_debug_message(
                            f"[NOTE_TYPE_ERROR] Error updating note types: {note_type_error}",
                            "SYNC",
                        )
            
            currentRemoteInfo["remote_deck_name"] = current_remote_name
            remote_decks[deckKey]["remote_deck_name"] = current_remote_name
            add_debug_message(
                f"[REMOTE_NAME_UPDATE] remote_deck_name updated to: '{current_remote_name}'",
                "SYNC",
            )

            # Always update local_deck_name in memory configuration
            if local_name_needs_update:
                currentRemoteInfo["local_deck_name"] = expected_local_deck_name
                remote_decks[deckKey]["local_deck_name"] = expected_local_deck_name
                add_debug_message(
                    "[MEMORY_UPDATE] In-memory configuration updated", "SYNC"
                )

            # Update local_deck_configurations_package_name if in individual mode
            if should_update:
                try:
                    from .config_manager import get_deck_options_mode
                    current_mode = get_deck_options_mode()
                    if current_mode == "individual":
                        expected_package_name = f"Sheets2Anki - {current_remote_name}"
                        currentRemoteInfo["local_deck_configurations_package_name"] = expected_package_name
                        remote_decks[deckKey]["local_deck_configurations_package_name"] = expected_package_name
                        add_debug_message(
                            f"[DECK_OPTIONS_UPDATE] local_deck_configurations_package_name updated to: '{expected_package_name}'",
                            "SYNC",
                        )
                except Exception as opts_error:
                    add_debug_message(
                        f"[DECK_OPTIONS_ERROR] Error updating deck options name: {opts_error}",
                        "SYNC",
                    )

            # IMPORTANT: Do not reload from file here to preserve in-memory updates
            add_debug_message(
                "[CONFIG_PRESERVE] Preserving in-memory updates (remote_deck_name, note_types, and deck_options)", "SYNC"
            )
            
            # Save final configuration (now with updated note_types AND correct remote_deck_name)
            save_remote_decks(remote_decks)
            add_debug_message(
                "[CONFIG_SAVE] Configuration saved after name update (with correct note_types)", "SYNC"
            )    # Update deck name if necessary using DeckNameManager
    current_remote_name = currentRemoteInfo.get("remote_deck_name")
    sync_result = DeckNameManager.sync_deck_with_config(remote_deck_url)
    
    if sync_result:
        sync_deck_id, updated_name = sync_result
        if updated_name != deckName:
            # Update deck info in configuration
            currentRemoteInfo["local_deck_name"] = updated_name
            
            msg = f"🏷️ {deckName} → {updated_name}: Name updated automatically"
            deckName = updated_name
            remoteDeck.deckName = updated_name
            
            status_msgs.append(msg)
            _update_progress_text(progress, status_msgs)
        else:
             # Name verified but no changes needed
             msg = f"🏷️ {deckName}: Name verification OK"
             # Optional: Uncomment if we want this verbose line, but likely too verbose for every sync? 
             # For now, per user request "no step should be silent", we add it.
             status_msgs.append(msg)
             _update_progress_text(progress, status_msgs)

    # 2. Processing and writing to database
    msg = f"⚙️ {deckName}: Processing data..."
    status_msgs.append(msg)
    _update_progress_text(progress, status_msgs)

    remoteDeck.deckName = deckName

    msg = f"💾 {deckName}: Saving changes..."
    status_msgs.append(msg)
    _update_progress_text(progress, status_msgs)

    add_debug_message(
        f"🚀 ABOUT TO CALL create_or_update_notes - remoteDeck has {len(remoteDeck.notes) if hasattr(remoteDeck, 'notes') and remoteDeck.notes else 0} notes",
        "SYNC",
    )

    # Critical debug to verify import
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
        add_debug_message(f"❌ ERROR in create_or_update_notes call: {e}", "SYNC")
        add_debug_message(f"❌ Stack trace: {error_details}", "SYNC")
        # Return default stats with errors
        deck_stats = SyncStats(created=0, updated=0, deleted=0, errors=1, ignored=0)
        deck_stats.add_error(f"Critical synchronization error: {e}")

    add_debug_message(
        f"✅ create_or_update_notes COMPLETED - returned: {deck_stats}", "SYNC"
    )

    step += 1
    progress.setValue(step)
    mw.app.processEvents()

    # 4. Capture and store note type IDs after successful synchronization
    try:

        add_debug_message(
            f"Starting note type ID capture for deck: {deckName}", "SYNC"
        )

        # Capture created/updated note type IDs
        capture_deck_note_type_ids(
            remote_deck_url,  # Use actual URL instead of hash key
            currentRemoteInfo.get("remote_deck_name", "RemoteDeck"),
            None,  # enabled_students is not needed for ID capture
            None,  # enabled_students is not needed for ID capture
        )

        add_debug_message(
            f"✅ Note type IDs captured and stored for deck: {deckName}",
            "SYNC",
        )

        # NEW: Ensure automatic name consistency after synchronization
        add_debug_message(
            f"🔧 Starting name consistency check for: {remote_deck_url}",
            "NAME_CONSISTENCY",
        )
        
        try:
            consistency_result = NameConsistencyManager.ensure_consistency_during_sync(
                deck_url=remote_deck_url,
                remote_decks=remote_decks,
                debug_callback=lambda msg: add_debug_message(msg, "NAME_CONSISTENCY")
            )
            
            if consistency_result and not consistency_result.get('errors'):
                # Success - log what was updated
                updates = []
                if consistency_result.get('deck_updated'):
                    updates.append("deck name")
                if consistency_result.get('note_types_updated'):
                    updates.append(f"{len(consistency_result['note_types_updated'])} note types")
                if consistency_result.get('deck_options_updated'):
                    updates.append("deck options")
                
                if updates:
                    add_debug_message(
                        f"✅ Consistency applied: {', '.join(updates)} updated",
                        "NAME_CONSISTENCY",
                    )
                    status_msgs.append(f"🔧 Consistency applied: {', '.join(updates)}")
                    _update_progress_text(progress, status_msgs)
                else:
                    add_debug_message(
                        "✅ Consistency verified: all names were already correct",
                        "NAME_CONSISTENCY",
                    )
                    status_msgs.append(f"🔧 Name consistency verification: OK")
                    _update_progress_text(progress, status_msgs)
            elif consistency_result and consistency_result.get('errors'):
                # Error - but don't fail synchronization
                for error in consistency_result['errors']:
                    add_debug_message(
                        f"⚠️ Name consistency error: {error}",
                        "NAME_CONSISTENCY",
                    )
        except Exception as consistency_error:
            # Don't fail synchronization due to name consistency
            add_debug_message(
                f"⚠️ Unexpected name consistency error: {consistency_error}",
                "NAME_CONSISTENCY",
            )

    except Exception as e:
        # Don't fail synchronization due to ID capture
        add_debug_message(
            f"❌ ERROR capturing note type IDs for {deckName}: {e}", "SYNC"
        )
        error_details = traceback.format_exc()
        add_debug_message(f"Error details: {error_details}", "SYNC")

    # 5. ROBUST NOTE_TYPE SYNCHRONIZATION after Anki note creation
    add_debug_message(
        "[NOTE_TYPE_SYNC] Starting robust note_type synchronization AFTER note creation...",
        "SYNC",
    )
    try:
        enabled_students = get_selected_students_for_deck(remote_deck_url)
        sync_result = sync_note_type_names_robustly(
            remote_deck_url, current_remote_name, enabled_students
        )

        if sync_result["updated_count"] > 0:
            add_debug_message(
                f"[NOTE_TYPE_SYNC] ✅ {sync_result['updated_count']} note_types successfully synchronized",
                "SYNC",
            )
            add_debug_message(
                f"[NOTE_TYPE_SYNC] - Renamed in Anki: {sync_result['renamed_in_anki']}",
                "SYNC",
            )
            add_debug_message(
                f"[NOTE_TYPE_SYNC] - Updated in meta.json: {sync_result['updated_in_meta']}",
                "SYNC",
            )
            if sync_result.get("notes_migrated", 0) > 0:
                add_debug_message(
                    f"[NOTE_TYPE_SYNC] - Notes migrated: {sync_result['notes_migrated']}",
                    "SYNC",
                )
            
            status_msgs.append(f"🔄 Note Types: {sync_result['updated_count']} synced")
            _update_progress_text(progress, status_msgs)

        else:
            add_debug_message(
                "[NOTE_TYPE_SYNC] ✅ All note_types are already consistent", "SYNC"
            )
            status_msgs.append("🔄 Note Types verification: OK")
            _update_progress_text(progress, status_msgs)

    except Exception as e:
        add_debug_message(
            f"[NOTE_TYPE_SYNC] ❌ Robust synchronization error: {e}", "SYNC"
        )
        # Try fallback with old method
        try:
            enabled_students = get_selected_students_for_deck(remote_deck_url)
            update_note_type_names_in_meta(
                remote_deck_url, current_remote_name, enabled_students
            )
            add_debug_message("[NOTE_TYPE_SYNC] Fallback successfully applied", "SYNC")
        except Exception as fallback_error:
            add_debug_message(
                f"[NOTE_TYPE_SYNC] ❌ Fallback also failed: {fallback_error}", "SYNC"
            )

    # NEW: Update student sync history (ROBUST SOLUTION)
    # This ensures we always know which students were synchronized,
    # regardless of manual note type renames
    try:
        from .config_manager import update_student_sync_history
        
        # Get students who were synchronized in this deck
        students_synced = get_selected_students_for_deck(remote_deck_url)
        
        if students_synced:
            # Update persistent history
            update_student_sync_history(students_synced)
            add_debug_message(
                f"📚 HISTORY: History updated for {len(students_synced)} students",
                "SYNC"
            )
        else:
            add_debug_message("📚 HISTORY: No students synchronized to update history", "SYNC")
            
    except Exception as history_error:
        add_debug_message(f"⚠️ HISTORY: Error updating history: {history_error}", "SYNC")
        # Don't interrupt synchronization due to history error

    # CRITICAL: Save final configurations after name consistency
    # This ensures NameConsistencyManager updates are persisted
    try:
        from .config_manager import save_meta, get_meta
        current_meta = get_meta()
        save_meta(current_meta)
        add_debug_message(
            "💾 FINAL_SAVE: Configurations saved after consistency check",
            "SYNC"
        )
    except Exception as save_error:
        add_debug_message(
            f"⚠️ FINAL_SAVE: Error saving final configurations: {save_error}",
            "SYNC"
        )

    return step, 1, deck_stats


def _handle_sync_error(
    e, deckKey, remote_decks, progress, status_msgs, sync_errors, step
):
    """Handles deck synchronization errors."""
    # Check if mw.col and mw.col.decks are available
    if not _is_anki_decks_ready():
        deckName = "Unknown"
    else:
        assert mw.col is not None  # Type hint for checker
        # Try to get deck name for error message
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

    error_msg = f"❌ {deckName}: Sync failed - {str(e)}"
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
    """Handles unexpected errors during synchronization."""
    # Check if mw.col and mw.col.decks are available
    if not _is_anki_decks_ready():
        deckName = "Unknown"
    else:
        assert mw.col is not None  # Type hint for checker
        # Try to get deck name for error message
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

    error_msg = f"🔥 {deckName}: Unexpected error - {str(e)}"
    sync_errors.append(error_msg)
    status_msgs.append(error_msg)
    _update_progress_text(progress, status_msgs)
    step += 3
    progress.setValue(step)
    mw.app.processEvents()
    return step, sync_errors


def _show_debug_messages_window(debug_messages):
    """
    Shows a scrollable window with all debug messages.
    Adapted for Anki dark and light modes.

    Args:
        debug_messages: List of debug messages to display
    """
    from aqt.qt import QDialog
    from aqt.qt import QLabel
    from aqt.qt import QPushButton
    from aqt.qt import QTextEdit
    from aqt.qt import QVBoxLayout

    dialog = QDialog(mw)
    dialog.setWindowTitle(
        f"Debug Messages - Note Type IDs System ({len(debug_messages)} messages)"
    )
    dialog.setFixedSize(800, 600)

    layout = QVBoxLayout(dialog)

    # Detect dark mode using a more direct method
    is_dark_mode = False
    if hasattr(mw, "pm") and hasattr(mw.pm, "night_mode"):
        is_dark_mode = mw.pm.night_mode()

    # Define theme-based colors
    if is_dark_mode:
        # Dark mode colors - high contrast
        bg_color = "#1e1e1e"  # Very dark background
        text_color = "#f0f0f0"  # Very light text
        border_color = "#555555"  # Medium border
        info_bg_color = "#2d2d2d"  # Slightly lighter info background
        scroll_bg = "#3d3d3d"  # Scrollbar background
        scroll_handle = "#707070"  # Scrollbar handle
        scroll_hover = "#909090"  # Handle hover
        button_bg = "#4a4a4a"  # Button background
        button_hover = "#5a5a5a"  # Button hover
    else:
        # Light mode colors - traditional
        bg_color = "#ffffff"
        text_color = "#000000"
        border_color = "#cccccc"
        info_bg_color = "#f8f8f8"
        scroll_bg = "#f0f0f0"
        scroll_handle = "#c0c0c0"
        scroll_hover = "#a0a0a0"
        button_bg = "#f0f0f0"
        button_hover = "#e0e0e0"

    # Add informative label
    info_label = QLabel(
        f"📋 Total of {len(debug_messages)} debug messages captured during synchronization:"
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

    # Create scrollable text area with high-contrast colors
    text_area = QTextEdit()
    text_area.setReadOnly(True)
    text_area.setPlainText("\n".join(debug_messages))
    text_area.setStyleSheet(
        f"""
        QTextEdit {{
            font-family: 'Courier New', 'Monaco', 'Consolas', 'Liberation Mono', monospace;
            font-size: 12pt;
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

    # Close button with appropriate style
    close_button = QPushButton("Close")
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

    # Apply general style to dialog
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
    Manages data cleanups in a consolidated way to avoid multiple confirmations.

    This function checks if cleanup is needed for:
    1. Disabled students
    2. [MISSING S.] notes (when feature was disabled)

    If both need cleanup, shows a single consolidated confirmation.
    If only one needs cleanup, uses specific confirmation.

    Args:
        remote_decks (dict): Dictionary of configured remote decks

    Returns:
        tuple: (missing_cleanup_result, cleanup_result)
    """
    add_debug_message("🧹 CLEANUP: Starting consolidated cleanup verification...", "CLEANUP")
    
    # Check if [MISSING S.] cleanup is needed
    add_debug_message("📋 CLEANUP: Checking if [MISSING S.] cleanup is needed...", "CLEANUP")
    needs_missing_cleanup = _needs_missing_students_cleanup(remote_decks)
    add_debug_message(f"   ➜ [MISSING S.] cleanup {'REQUIRED' if needs_missing_cleanup else 'NOT required'}", "CLEANUP")

    # Check if disabled students cleanup is needed
    add_debug_message("📋 CLEANUP: Checking if disabled students cleanup is needed...", "CLEANUP")
    needs_disabled_cleanup = _needs_disabled_students_cleanup(remote_decks)
    add_debug_message(f"   ➜ Student cleanup {'REQUIRED' if needs_disabled_cleanup else 'NOT required'}", "CLEANUP")

    if not needs_missing_cleanup and not needs_disabled_cleanup:
        # No cleanup needed
        add_debug_message("✅ CLEANUP: No cleanup needed, continuing synchronization...", "CLEANUP")
        return None, None

    if needs_missing_cleanup and needs_disabled_cleanup:
        # Both cleanups needed - show consolidated confirmation
        return _handle_consolidated_confirmation_cleanup(remote_decks)

    elif needs_missing_cleanup:
        # Only [MISSING S.] cleanup
        missing_result = _handle_missing_students_cleanup(remote_decks)
        return missing_result, None

    else:
        # Only disabled students cleanup
        cleanup_result = _handle_disabled_students_cleanup(remote_decks)
        return None, cleanup_result


def _needs_missing_students_cleanup(remote_decks):
    """
    Checks if missing student data cleanup is necessary.
    
    SIMPLIFIED LOGIC:
    Cleanup is needed ONLY if:
    1. sync_missing_students_notes is disabled (feature turned off)
    2. There's a missing student placeholder in sync_history (data exists)
    
    This correctly detects when a user has disabled the missing students feature
    after it was previously used (and thus has data to be deleted).

    Returns:
        bool: True if cleanup is required
    """
    from .config_manager import is_auto_remove_disabled_students
    from .config_manager import is_sync_missing_students_notes
    from .config_manager import get_students_with_sync_history
    from .templates_and_definitions import DEFAULT_STUDENT

    add_debug_message("📋 CLEANUP: Checking if [MISSING S.] cleanup is needed...", "CLEANUP")

    # All missing student placeholders to check
    missing_placeholders = {
        DEFAULT_STUDENT,  # "[MISSING STUDENT]"
        "[MISSING STUDENTS]",
        "[MISSING S.]"
    }

    # FIRST CHECK: If feature is enabled, no need to clean
    if is_sync_missing_students_notes():
        add_debug_message("🔍 [MISSING S.]: Feature ENABLED, no cleanup needed", "CLEANUP")
        return False  # Feature enabled, no cleanup needed

    # SECOND CHECK: If auto-removal is disabled, don't clean
    if not is_auto_remove_disabled_students():
        add_debug_message(
            "🔍 [MISSING S.]: Feature DISABLED, but automatic removal also DISABLED - not cleaning",
            "CLEANUP"
        )
        return False

    # SIMPLE CHECK: Is there any missing student placeholder in sync_history?
    # This is the ONLY condition that requires cleanup warning
    sync_history_students = get_students_with_sync_history()
    missing_students_with_data = missing_placeholders.intersection(sync_history_students)
    
    add_debug_message(f"   📚 Students in sync_history: {sorted(sync_history_students)}", "CLEANUP")
    add_debug_message(f"   🔍 Missing placeholders with data: {sorted(missing_students_with_data)}", "CLEANUP")
    
    if missing_students_with_data:
        add_debug_message(
            f"⚠️ [MISSING S.]: Found {sorted(missing_students_with_data)} in sync_history, cleanup required",
            "CLEANUP"
        )
        return True
    else:
        add_debug_message("✅ [MISSING S.]: No missing student data found in sync_history, cleanup NOT required", "CLEANUP")
        return False


def _needs_disabled_students_cleanup(remote_decks):
    """
    Checks if disabled students cleanup is necessary.
    
    SIMPLIFIED LOGIC:
    Cleanup is needed ONLY if there are students in sync_history 
    that are NOT in enabled_students.
    
    This correctly detects when a user has disabled a student 
    that was previously synced (and thus has data to be deleted).

    Returns:
        bool: True if cleanup is required
    """
    from .config_manager import get_global_student_config
    from .config_manager import is_auto_remove_disabled_students
    from .config_manager import get_students_with_sync_history
    from .templates_and_definitions import DEFAULT_STUDENT

    add_debug_message("🔍 CLEANUP: Checking if disabled students cleanup is required...", "CLEANUP")

    # FIRST CHECK: Auto-removal must be active
    auto_remove_enabled = is_auto_remove_disabled_students()
    add_debug_message(f"   📋 Auto-removal is {'ENABLED' if auto_remove_enabled else 'DISABLED'}", "CLEANUP")
    
    if not auto_remove_enabled:
        add_debug_message("🚫 CLEANUP: Auto-removal disabled, skipping check", "CLEANUP")
        return False

    config = get_global_student_config()
    
    # Get currently enabled students
    current_enabled = set(config.get("enabled_students", []))
    add_debug_message(f"   👥 Currently enabled students: {sorted(current_enabled)}", "CLEANUP")
    
    # Get students from sync_history (these are students who have data in Anki)
    sync_history_students = get_students_with_sync_history()
    add_debug_message(f"   📚 Students in sync_history: {sorted(sync_history_students)}", "CLEANUP")
    
    # Filter out missing student placeholders (handled separately)
    missing_placeholders = {DEFAULT_STUDENT, "[MISSING STUDENTS]", "[MISSING S.]"}
    real_students_with_data = sync_history_students - missing_placeholders
    add_debug_message(f"   👤 Real students with data: {sorted(real_students_with_data)}", "CLEANUP")
    
    # SIMPLE CHECK: Are there any students with data that are no longer enabled?
    # This is the ONLY condition that requires cleanup warning
    students_to_cleanup = real_students_with_data - current_enabled
    
    if students_to_cleanup:
        add_debug_message("🔍 CLEANUP: Students detected for cleanup:", "CLEANUP")
        add_debug_message(f"  • Students with data (sync_history): {sorted(real_students_with_data)}", "CLEANUP")
        add_debug_message(f"  • Currently enabled: {sorted(current_enabled)}", "CLEANUP")
        add_debug_message(f"  • Students to remove: {sorted(students_to_cleanup)}", "CLEANUP")
        add_debug_message("✅ CLEANUP: Cleanup is REQUIRED", "CLEANUP")
        return True
    else:
        add_debug_message("✅ CLEANUP: No disabled students with data found, cleanup NOT required", "CLEANUP")
        return False


def _handle_consolidated_confirmation_cleanup(remote_decks):
    """
    Shows a single confirmation for both types of cleanup and executes both if confirmed.
    
    SIMPLIFIED LOGIC:
    - Uses sync_history as the ONLY source of truth for students with data
    - Students need cleanup ONLY if they are in sync_history but NOT in enabled_students

    Returns:
        tuple: (missing_cleanup_result, cleanup_result)
    """
    from .config_manager import get_global_student_config
    from .config_manager import get_students_with_sync_history
    from .student_manager import cleanup_disabled_students_data
    from .student_manager import cleanup_missing_students_data
    from .data_removal_confirmation import collect_students_for_removal, show_data_removal_confirmation_dialog
    from .templates_and_definitions import DEFAULT_STUDENT

    # Missing student placeholders
    missing_placeholders = {DEFAULT_STUDENT, "[MISSING STUDENTS]", "[MISSING S.]"}

    # Get configuration
    config = get_global_student_config()
    
    # Currently enabled students
    current_enabled = set(config.get("enabled_students", []))
    add_debug_message(f"   👥 Currently enabled students: {sorted(current_enabled)}", "CLEANUP")

    # SOURCE: sync_history (ONLY source of truth for students with data)
    sync_history_students = get_students_with_sync_history()
    add_debug_message(f"   📚 Students in sync_history: {sorted(sync_history_students)}", "CLEANUP")

    # Filter out missing student placeholders (handled separately)
    real_students_with_data = sync_history_students - missing_placeholders
    add_debug_message(f"   👤 Real students with data: {sorted(real_students_with_data)}", "CLEANUP")

    # SIMPLE CHECK: Students who have data but are no longer enabled
    disabled_students_set = real_students_with_data - current_enabled
    add_debug_message(f"   🎯 Students to cleanup: {sorted(disabled_students_set)}", "CLEANUP")

    deck_names = [
        deck_info.get("remote_deck_name", "") for deck_info in remote_decks.values()
    ]
    deck_names = [name for name in deck_names if name]

    # Check if [MISSING S.] should be cleaned
    from .config_manager import is_sync_missing_students_notes
    missing_functionality_disabled = not is_sync_missing_students_notes()
    
    # Check if there's actually missing student data in sync_history
    missing_students_in_history = missing_placeholders.intersection(sync_history_students)
    should_cleanup_missing = missing_functionality_disabled and bool(missing_students_in_history)
    
    # Collect all students to be removed using centralized function
    students_to_remove = collect_students_for_removal(
        disabled_students=list(disabled_students_set),
        missing_functionality_disabled=should_cleanup_missing  # Only if there's actual data
    )
    
    # If nothing to remove, return without showing dialog
    if not students_to_remove:
        return ({}, {})
    
    # Use centralized dialog for confirmation
    # Use centralized dialog for confirmation (returns int)
    result = show_data_removal_confirmation_dialog(
        students_to_remove=students_to_remove,
        window_title="⚠️ Confirm Data Cleanup"
    )

    if result == MessageBox_Yes:
        add_debug_message("🧹 CLEANUP: User confirmed consolidated cleanup", "CLEANUP")
        add_debug_message(f"🧹 CLEANUP: Disabled students: {sorted(disabled_students_set)}", "CLEANUP")

        # Execute both cleanups
        if should_cleanup_missing:
            cleanup_missing_students_data(deck_names)
        if disabled_students_set:
            cleanup_disabled_students_data(disabled_students_set, deck_names)

        # Return results
        missing_result = {
            "missing_cleanup_count": 1 if should_cleanup_missing else 0,
            "missing_cleanup_message": "[MISSING S.] data removed" if should_cleanup_missing else "",
        }

        cleanup_result = {
            "disabled_students_count": len(disabled_students_set),
            "disabled_students_names": ", ".join(sorted(disabled_students_set)),
        }

        add_debug_message("✅ CLEANUP: Consolidated cleanup completed", "CLEANUP")
        return missing_result, cleanup_result
        
    else:  # MessageBox_Cancel or any other response
        add_debug_message("🛑 CLEANUP: User cancelled consolidated cleanup - ABORTING SYNC", "CLEANUP")
        raise SyncAborted("User cancelled data cleanup")


def _handle_missing_students_cleanup(remote_decks):
    """
    Manages missing student note data cleanup when feature is disabled.
    
    SIMPLIFIED LOGIC:
    - Only checks sync_history for missing student placeholders
    - No Anki scanning needed (sync_history is the source of truth)

    Args:
        remote_decks (dict): Dictionary of configured remote decks

    Returns:
        dict: Cleanup statistics or None if no cleanup occurred
    """
    from .config_manager import is_sync_missing_students_notes
    from .config_manager import get_students_with_sync_history
    from .student_manager import cleanup_missing_students_data
    from .student_manager import show_missing_cleanup_confirmation_dialog
    from .templates_and_definitions import DEFAULT_STUDENT

    # All missing student placeholders to check
    missing_placeholders = {
        DEFAULT_STUDENT,  # "[MISSING STUDENT]"
        "[MISSING STUDENTS]",
        "[MISSING S.]"
    }

    # If feature is enabled, do nothing
    if is_sync_missing_students_notes():
        return None  # Feature enabled, nothing to clean

    # Feature disabled - check if there's missing student data in sync_history
    add_debug_message(
        "🔍 CLEANUP: Sync [MISSING S.] is DISABLED, checking for data to clean...",
        "CLEANUP"
    )

    # Extract deck_names (needed for cleanup later)
    deck_names = [
        deck_info.get("remote_deck_name", "") for deck_info in remote_decks.values()
    ]
    deck_names = [name for name in deck_names if name]  # Filter empty names

    # SIMPLE CHECK: Check sync_history for any missing student placeholders
    sync_history_students = get_students_with_sync_history()
    missing_students_with_data = missing_placeholders.intersection(sync_history_students)
    
    add_debug_message(f"   📚 Students in sync_history: {sorted(sync_history_students)}", "CLEANUP")
    add_debug_message(f"   🔍 Missing placeholders with data: {sorted(missing_students_with_data)}", "CLEANUP")

    if not missing_students_with_data:
        add_debug_message("✅ CLEANUP: No missing student data found in sync_history", "CLEANUP")
        return None

    add_debug_message("⚠️ CLEANUP: [MISSING S.] data found for cleanup", "CLEANUP")

    # Show confirmation dialog
    # Show confirmation dialog
    # Now returns int result
    result = show_missing_cleanup_confirmation_dialog()
    
    if result == MessageBox_Yes:
        # User confirmed - execute cleanup
        add_debug_message(f"🧹 CLEANUP: Starting [MISSING S.] cleanup for decks: {deck_names}", "CLEANUP")

        cleanup_missing_students_data(deck_names)

        # Simple log of completed cleanup
        add_debug_message("✅ CLEANUP: [MISSING S.] cleanup completed", "CLEANUP")
        return {
            "missing_cleanup_count": 1,
            "missing_cleanup_message": "[MISSING S.] data removed",
        }
        
    else:  # MessageBox_Cancel or any other response
        add_debug_message("🛑 CLEANUP: User cancelled [MISSING S.] cleanup - ABORTING SYNC", "CLEANUP")
        raise SyncAborted("User cancelled [MISSING S.] cleanup")


def _handle_disabled_students_cleanup(remote_decks):
    """
    Manages cleanup of data for students who have been disabled.

    This function:
    1. Checks if auto-removal is enabled
    2. Identifies disabled students
    3. Shows security confirmation
    4. Removes data if confirmed

    Args:
        remote_decks (dict): Dictionary of configured remote decks

    Returns:
        dict: Cleanup statistics or None if no cleanup occurred
    """
    from .config_manager import get_global_student_config
    from .config_manager import is_auto_remove_disabled_students
    from .student_manager import cleanup_disabled_students_data
    from .student_manager import get_disabled_students_for_cleanup
    from .student_manager import show_cleanup_confirmation_dialog

    # Check if auto-removal is enabled
    if not is_auto_remove_disabled_students():
        return None  # Auto-removal disabled, nothing to do

    add_debug_message("🔍 CLEANUP: Auto-removal is ENABLED, checking for disabled students...", "CLEANUP")

    # Get current configuration
    config = get_global_student_config()
    current_enabled = set(config.get("enabled_students", []))

    # IMPROVED LOGIC for [MISSING S.]:
    # - If [MISSING S.] functionality is active, include in current list
    # - If functionality was disabled, [MISSING S.] will be detected as "removed"
    #   and its notes will be cleaned
    from .config_manager import is_sync_missing_students_notes

    if is_sync_missing_students_notes():
        current_enabled.add("[MISSING S.]")
        add_debug_message(
            "🔍 CLEANUP: [MISSING S.] included in current list (feature active)", "CLEANUP"
        )
    else:
        add_debug_message(
            "🔍 CLEANUP: [MISSING S.] excluded from current list (feature disabled)", "CLEANUP"
        )
        add_debug_message(
            "          If existing [MISSING S.] notes exist, they will be detected for removal", "CLEANUP"
        )

    # Use get_disabled_students_for_cleanup which uses sync_history as source of truth
    disabled_students = get_disabled_students_for_cleanup(current_enabled)

    if not disabled_students:
        add_debug_message("✅ CLEANUP: No disabled students detected", "CLEANUP")
        return None

    add_debug_message(
        f"⚠️ CLEANUP: Detected {len(disabled_students)} disabled students: {sorted(disabled_students)}", "CLEANUP"
    )

    # Show confirmation dialog
    # Show confirmation dialog (returns int)
    result = show_cleanup_confirmation_dialog(disabled_students)

    if result == MessageBox_Yes:
        # User confirmed - execute cleanup
        deck_names = [
            deck_info.get("remote_deck_name", "") for deck_info in remote_decks.values()
        ]
        deck_names = [name for name in deck_names if name]  # Filter empty names

        add_debug_message(f"🧹 CLEANUP: Starting cleanup for decks: {deck_names}", "CLEANUP")

        cleanup_disabled_students_data(disabled_students, deck_names)

        # Simple log of completed cleanup
        add_debug_message(f"✅ CLEANUP: Cleanup completed for {len(disabled_students)} students", "CLEANUP")
        return {
            "disabled_students_count": len(disabled_students),
            "disabled_students_names": ", ".join(sorted(disabled_students)),
        }
        
    else:  # MessageBox_Cancel or any other response
        add_debug_message("🛑 CLEANUP: User cancelled student cleanup - ABORTING SYNC", "CLEANUP")
        raise SyncAborted("User cancelled student cleanup")
