"""
Sheets2Anki - Add-on for synchronizing Anki decks with Google Sheets spreadsheets

This module implements the main functionality for synchronizing Anki decks
with Google Sheets spreadsheets in TSV format.
"""

# Import compatibility module that now contains all compatibility functions
from . import compat

# Initialize debug system when the addon is loaded
try:
    from .utils import add_debug_message
    from .utils import initialize_debug_log

    initialize_debug_log()
    add_debug_message("🚀 Sheets2Anki addon loaded", "SYSTEM")
except Exception as e:
    print(f"[SHEETS2ANKI] Error initializing debug: {e}")

# =============================================================================
# MAIN EXPOSED FUNCTIONS (consolidated from main.py)
# =============================================================================

# Project module imports
from .backup_dialog import show_backup_dialog
from .debug_dialog import show_debug_mode_dialog
from .deck_manager import addNewDeck
from .deck_manager import import_test_deck
from .deck_manager import manage_deck_students
from .deck_manager import removeRemoteDeck
from .deck_manager import reset_student_selection
from .deck_manager import syncDecksWithSelection
from .sync import syncDecks
from .sync_dialog import show_sync_dialog

# These functions are the main entry points of the addon
# and are used by Anki's menu system
__all__ = [
    "syncDecks",
    "syncDecksWithSelection",
    "import_test_deck",
    "addNewDeck",
    "removeRemoteDeck",
    "manage_deck_students",
    "reset_student_selection",
    "show_backup_dialog",
    "show_debug_mode_dialog",
]

