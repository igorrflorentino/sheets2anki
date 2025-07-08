# Sheets2Anki Add-on
# Author: Dr. Basti
# Email: drbasti.co@gmail.com

#import sys os
import sys
import os

# Obtener la ruta absoluta del directorio actual (donde está __init__.py)
addon_path = os.path.dirname(__file__)

# Agregar la carpeta 'libs' al sys.path
libs_path = os.path.join(addon_path, 'remote_decks', 'libs')
if libs_path not in sys.path:
    sys.path.insert(0, libs_path)
    
# Anki integration class

from aqt import mw
from aqt.utils import showInfo, qconnect
from aqt.qt import QAction, QMenu, QKeySequence
from aqt.importing import ImportDialog

try:
    from .remote_decks.main import import_test_deck
    from .remote_decks.main import addNewDeck
    from .remote_decks.main import syncDecks as sDecks
    from .remote_decks.main import removeRemoteDeck as rDecks
    from .remote_decks.libs.org_to_anki.utils import getAnkiPluginConnector as getConnector
except Exception as e:
    showInfo(f"Error importing modules from the sheets2anki plugin:\n{e}")
    raise

errorTemplate = """
Hello! It seems an error occurred during execution.

The error was: {}.

If you want me to fix it, please report it here: https://github.com/sebastianpaez/sheets2anki

Make sure to provide as much information as possible, especially the file that caused the error.
"""

def addDeck():
    try:
        ankiBridge = getConnector()
        ankiBridge.startEditing()
        addNewDeck()
    except Exception as e:
        errorMessage = str(e)
        showInfo(errorTemplate.format(errorMessage))
        if ankiBridge.getConfig().get("debug", False):
            import traceback
            trace = traceback.format_exc()
            showInfo(str(trace))
    finally:
        ankiBridge.stopEditing()

def syncDecks():
    try:
        ankiBridge = getConnector()
        ankiBridge.startEditing()
        sDecks()
    except Exception as e:
        errorMessage = str(e)
        showInfo(errorTemplate.format(errorMessage))
        if ankiBridge.getConfig().get("debug", False):
            import traceback
            trace = traceback.format_exc()
            showInfo(str(trace))
    finally:
        showInfo("Synchronization complete")
        ankiBridge.stopEditing()

def removeRemote():
    try:
        ankiBridge = getConnector()
        ankiBridge.startEditing()
        rDecks()
    except Exception as e:
        errorMessage = str(e)
        showInfo(errorTemplate.format(errorMessage))
        if ankiBridge.getConfig().get("debug", False):
            import traceback
            trace = traceback.format_exc()
            showInfo(str(trace))
    finally:
        ankiBridge.stopEditing()

# Verificar que mw no sea None antes de agregar acciones al menú
if mw is not None:
    remoteDecksSubMenu = QMenu("Manage sheets2anki Decks", mw)
    mw.form.menuTools.addMenu(remoteDecksSubMenu)

    # Añadir acción para "Agregar nuevo mazo remoto"
    remoteDeckAction = QAction("Add New sheets2anki Remote Deck", mw)
    remoteDeckAction.setShortcut(QKeySequence("Ctrl+Shift+A"))
    qconnect(remoteDeckAction.triggered, addDeck)
    remoteDecksSubMenu.addAction(remoteDeckAction)

    # Acción para "Sincronizar mazos remotos"
    syncDecksAction = QAction("Sync Decks", mw)
    syncDecksAction.setShortcut(QKeySequence("Ctrl+Shift+S"))
    qconnect(syncDecksAction.triggered, syncDecks)
    remoteDecksSubMenu.addAction(syncDecksAction)

    # Acción para "Eliminar mazo remoto"
    removeRemoteDeck = QAction("Disconnect a remote Deck", mw)
    removeRemoteDeck.setShortcut(QKeySequence("Ctrl+Shift+D"))
    qconnect(removeRemoteDeck.triggered, removeRemote)
    remoteDecksSubMenu.addAction(removeRemoteDeck)

    # Adicionar ação para importar deck de teste
    importTestDeckAction = QAction("Import Test Deck", mw)
    importTestDeckAction.setShortcut(QKeySequence("Ctrl+Shift+T"))
    qconnect(importTestDeckAction.triggered, import_test_deck)
    remoteDecksSubMenu.addAction(importTestDeckAction)
    
