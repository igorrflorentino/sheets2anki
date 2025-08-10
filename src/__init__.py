"""
Sheets2Anki - Add-on para sincronizar decks do Anki com planilhas do Google Sheets

Este módulo implementa a funcionalidade principal para sincronização de decks do Anki
com planilhas do Google Sheets em formato TSV.
"""

# Importar módulo de compatibilidade que agora contém todas as funções de compatibilidade
from . import compat

# Inicializar sistema de debug quando o addon é carregado
try:
    from .utils import add_debug_message
    from .utils import initialize_debug_log

    initialize_debug_log()
    add_debug_message("🚀 Sheets2Anki addon carregado", "SYSTEM")
except Exception as e:
    print(f"[SHEETS2ANKI] Erro ao inicializar debug: {e}")

# =============================================================================
# FUNÇÕES PRINCIPAIS EXPOSTAS (consolidado de main.py)
# =============================================================================

# Imports dos módulos do projeto
from .backup_system import show_backup_dialog
from .deck_manager import addNewDeck
from .deck_manager import import_test_deck
from .deck_manager import manage_deck_students
from .deck_manager import removeRemoteDeck
from .deck_manager import reset_student_selection
from .deck_manager import syncDecksWithSelection
from .sync import syncDecks
from .sync_dialog import show_sync_dialog

# Estas funções são os pontos de entrada principais do addon
# e são usadas pelo sistema de menus do Anki
__all__ = [
    "syncDecks",
    "syncDecksWithSelection",
    "import_test_deck",
    "addNewDeck",
    "removeRemoteDeck",
    "manage_deck_students",
    "reset_student_selection",
    "show_backup_dialog",
]
