"""
Sheets2Anki Add-on - Main Anki Integration Module

This module serves as the entry point for the Sheets2Anki Anki add-on,
integrating remote deck synchronization features with Google Sheets.

Main features:
- Python environment configuration for dependencies
- Integration with Anki user interface
- Menu creation and actions for remote deck management
- Error handling and user feedback
- Bridge between Anki interface and synchronization logic

Add-on structure:
- __init__.py: Main module (this file)
- src/: Synchronization and processing logic
- libs/: External libraries and dependencies

Author: Igor Florentino
Email: igorlopesc@gmail.com
"""

# =============================================================================
# PYTHON ENVIRONMENT CONFIGURATION
# =============================================================================

import sys
import os

# Configure paths for external dependencies
addon_path = os.path.dirname(__file__)
libs_path = os.path.join(addon_path, 'libs')

# Add libraries to Python path if not already present
if libs_path not in sys.path:
    sys.path.insert(0, libs_path)

# =============================================================================
# ANKI AND INTERNAL MODULE IMPORTS
# =============================================================================

# Main Anki imports with compatibility
try:
    from .src.compat import mw, showInfo, QAction, QMenu, QKeySequence, safe_qconnect as qconnect
    from aqt.importing import ImportDialog
except ImportError as e:
    # Fallback for development
    print(f"Error importing compatibility modules: {e}")
    from aqt import mw
    from aqt.utils import showInfo
    from aqt.qt import QAction, QMenu, QKeySequence, qconnect
    from aqt.importing import ImportDialog

# Internal module imports with robust error handling
try:
    from .src.deck_manager import import_test_deck
    from .src.deck_manager import addNewDeck
    from .src.deck_manager import syncDecksWithSelection as sDecks
    from .src.deck_manager import removeRemoteDeck as rDecks
    from .src.backup_dialog import show_backup_dialog
    from .src.templates_and_definitions import DEFAULT_PARENT_DECK_NAME
    from .libs.org_to_anki.utils import getAnkiPluginConnector as getConnector
    
except Exception as e:
    showInfo(f"Error importing Sheets2Anki plugin modules:\n{e}")
    raise

# =============================================================================
# TEMPLATES AND CONFIGURATIONS
# =============================================================================

# Error message template for the user
errorTemplate = """
Hello! It seems an error occurred during execution.

The error was: {}.

If you'd like me to fix it, please report here: https://github.com/igorrflorentino/sheets2anki

Please provide as much information as possible, especially the file that caused the error.
"""

# =============================================================================
# USER INTERFACE FUNCTIONS
# =============================================================================

def addDeck():
    """
    Adds a new remote deck connected to a Google Sheets spreadsheet.
    
    This function:
    1. Initializes the Anki bridge
    2. Calls the interface to add a new deck
    3. Handles errors and displays appropriate feedback
    4. Ensures resource cleanup even in case of error
    """
    ankiBridge = None
    try:
        ankiBridge = getConnector()
        ankiBridge.startEditing()
        addNewDeck()
    except Exception as e:
        errorMessage = str(e)
        showInfo(errorTemplate.format(errorMessage))
        if ankiBridge and ankiBridge.getConfig().get("debug", False):
            import traceback
            trace = traceback.format_exc()
            showInfo(str(trace))
    finally:
        if ankiBridge:
            ankiBridge.stopEditing()

def backup_decks():
    """
    Opens the remote decks backup dialog.
    
    This function allows the user to:
    1. Create a complete backup of their configurations
    2. Restore previous backups
    3. Export/import specific configurations
    """
    try:
        show_backup_dialog()
    except Exception as e:
        error_msg = errorTemplate.format(str(e))
        showInfo(error_msg)

def syncDecks():
    """
    Synchronizes all configured remote decks.
    
    This function starts the synchronization process for all decks
    registered in the system, downloading updated data from
    Google Sheets spreadsheets.
    """
    try:
        sDecks()
    except Exception as e:
        error_msg = errorTemplate.format(str(e))
        showInfo(error_msg)

def removeRemote():
    """
    Removes a remote deck connection from the system.
    
    This function:
    1. Initializes the Anki bridge
    2. Allows the user to disconnect a remote deck
    3. Handles errors and displays appropriate feedback
    4. Ensures resource cleanup
    """
    ankiBridge = None
    try:
        ankiBridge = getConnector()
        ankiBridge.startEditing()
        rDecks()
    except Exception as e:
        errorMessage = str(e)
        showInfo(errorTemplate.format(errorMessage))
        if ankiBridge and ankiBridge.getConfig().get("debug", False):
            import traceback
            trace = traceback.format_exc()
            showInfo(str(trace))
    finally:
        if ankiBridge:
            ankiBridge.stopEditing()

def configure_global_students():
    """
    Opens the global student configuration dialog.
    
    This function allows the user to globally configure which students
    should be synchronized across all remote decks.
    """
    try:
        from .src.global_student_config_dialog import show_global_student_config_dialog
        show_global_student_config_dialog(mw)
    except Exception as e:
        error_msg = errorTemplate.format(str(e))
        showInfo(error_msg)

def configure_deck_options_mode():
    """
    Opens the deck options mode configuration dialog.
    
    This function allows the user to choose between three modes:
    1. Shared - All decks use "Sheets2Anki - Default"
    2. Individual - Each deck has its own group "Sheets2Anki - [Name]"
    3. Manual - No automatic options application
    """
    try:
        from .src.deck_options_config_dialog import show_deck_options_config_dialog
        show_deck_options_config_dialog(mw)
    except Exception as e:
        error_msg = errorTemplate.format(str(e))
        showInfo(error_msg)

def configure_ankiweb_sync():
    """
    Opens the AnkiWeb automatic synchronization configuration dialog.
    
    This function allows the user to choose between two modes:
    1. Disabled - No automatic synchronization
    2. Sync - Execute sync after deck synchronization
    """
    try:
        from .src.ankiweb_sync_config_dialog import show_ankiweb_sync_config
        show_ankiweb_sync_config()
    except Exception as e:
        error_msg = errorTemplate.format(str(e))
        showInfo(error_msg)

def open_debug_mode():
    """Opens the debug mode configuration dialog."""
    try:
        from .src.debug_dialog import show_debug_mode_dialog
        show_debug_mode_dialog()
    except Exception as e:
        error_msg = errorTemplate.format(str(e))
        showInfo(error_msg)

def configure_timer():
    """
    Opens the timer position configuration dialog.
    
    This function allows the user to choose between three timer positions:
    1. Top Middle - Timer at top center
    2. Between Sections - Timer between CONTEXT and CARD
    3. Hidden - Timer disabled
    """
    try:
        from .src.timer_config_dialog import show_timer_config_dialog
        show_timer_config_dialog(mw)
    except Exception as e:
        error_msg = errorTemplate.format(str(e))
        showInfo(error_msg)

def configure_ai_help():
    """
    Opens the AI Help configuration dialog.
    
    This function allows the user to configure:
    1. AI Service (Gemini, Claude, OpenAI)
    2. API Key
    3. Model selection
    4. Custom prompt template
    """
    try:
        from .src.ai_help_config_dialog import show_ai_help_config_dialog
        show_ai_help_config_dialog(mw)
    except Exception as e:
        error_msg = errorTemplate.format(str(e))
        showInfo(error_msg)


# =============================================================================
# AI HELP PYCMD HANDLER
# =============================================================================

def handle_ai_help_request(card_content):
    """
    Handles AI Help requests from card JavaScript.
    
    This function:
    1. Gets AI configuration
    2. Calls the AI API with card content
    3. Returns response to the card via JavaScript
    
    Args:
        card_content: The card content sent from JavaScript (URL encoded)
    """
    import urllib.parse
    
    try:
        # Decode the card content
        decoded_content = urllib.parse.unquote(card_content)
        
        # Get AI configuration
        from .src.config_manager import get_ai_help_config
        config = get_ai_help_config()
        
        if not config.get("enabled"):
            send_ai_response_to_card("AI Help is not enabled. Go to Tools → Sheets2Anki → Configure AI Help to set it up.", None)
            return
        
        service = config.get("service", "gemini")
        model = config.get("model", "")
        api_key = config.get("api_key", "")
        prompt = config.get("prompt", "")
        
        if not api_key:
            send_ai_error_to_card("No API key configured. Please configure AI Help first.")
            return
        
        if not model:
            send_ai_error_to_card("No model selected. Please configure AI Help first.")
            return
        
        # Call AI API asynchronously
        from .src.ai_service import call_ai_api_async
        
        def on_ai_response(result, error):
            if error:
                send_ai_error_to_card(str(error))
            else:
                # result is a dict with 'text', 'input_tokens', 'output_tokens', 'cost'
                usage_info = {
                    "input_tokens": result.get("input_tokens", 0),
                    "output_tokens": result.get("output_tokens", 0),
                    "cost": result.get("cost", 0)
                }
                send_ai_response_to_card(result.get("text", ""), usage_info)
        
        call_ai_api_async(service, model, api_key, prompt, decoded_content, on_ai_response)
        
    except Exception as e:
        send_ai_error_to_card(f"Error processing AI Help request: {str(e)}")


def send_ai_response_to_card(response, usage_info):
    """Sends AI response back to the card via JavaScript."""
    try:
        import json
        from aqt import mw
        if mw and mw.reviewer and mw.reviewer.web:
            # Escape the response for JavaScript
            escaped_response = response.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n').replace('\r', '')
            
            # Serialize usage info
            usage_json = json.dumps(usage_info) if usage_info else "null"
            
            # Must run on main thread - Qt requires UI operations on main thread
            def run_on_main():
                if mw.reviewer and mw.reviewer.web:
                    mw.reviewer.web.eval(f"sheets2ankiAIResponse('{escaped_response}', {usage_json})")
            
            mw.taskman.run_on_main(run_on_main)
    except Exception as e:
        print(f"Error sending AI response to card: {e}")


def send_ai_error_to_card(error):
    """Sends error message back to the card via JavaScript."""
    try:
        from aqt import mw
        if mw and mw.reviewer and mw.reviewer.web:
            # Escape the error for JavaScript
            escaped_error = str(error).replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n').replace('\r', '')
            
            # Must run on main thread - Qt requires UI operations on main thread
            def run_on_main():
                if mw.reviewer and mw.reviewer.web:
                    mw.reviewer.web.eval(f"sheets2ankiAIError('{escaped_error}')")
            
            mw.taskman.run_on_main(run_on_main)
    except Exception as e:
        print(f"Error sending AI error to card: {e}")

# =============================================================================
# ANKI INTERFACE CONFIGURATION
# =============================================================================

# Check if Anki is available before configuring the interface
if mw is not None:
    # Create main submenu for Sheets2Anki features
    remoteDecksSubMenu = QMenu(DEFAULT_PARENT_DECK_NAME, mw)
    mw.form.menuTools.addMenu(remoteDecksSubMenu)

    # =========================================================================
    # MENU ACTIONS
    # =========================================================================

    # Action: Add new remote deck
    remoteDeckAction = QAction("Add New Remote Deck", mw)
    remoteDeckAction.setShortcut(QKeySequence("Ctrl+Shift+A"))
    qconnect(remoteDeckAction.triggered, addDeck)
    remoteDecksSubMenu.addAction(remoteDeckAction)

    # Action: Synchronize remote decks
    syncDecksAction = QAction("Synchronize Remote Decks", mw)
    syncDecksAction.setShortcut(QKeySequence("Ctrl+Shift+S"))
    qconnect(syncDecksAction.triggered, syncDecks)
    remoteDecksSubMenu.addAction(syncDecksAction)

    # Action: Disconnect remote deck
    removeRemoteDeck = QAction("Disconnect a Remote Deck", mw)
    removeRemoteDeck.setShortcut(QKeySequence("Ctrl+Shift+D"))
    qconnect(removeRemoteDeck.triggered, removeRemote)
    remoteDecksSubMenu.addAction(removeRemoteDeck)

    # Separator
    remoteDecksSubMenu.addSeparator()

    # Action: Global Student Configuration
    studentConfigAction = QAction("Configure Students Globally", mw)
    studentConfigAction.setShortcut(QKeySequence("Ctrl+Shift+G"))
    qconnect(studentConfigAction.triggered, configure_global_students)
    remoteDecksSubMenu.addAction(studentConfigAction)

    # Action: Configure deck options mode
    deckOptionsConfigAction = QAction("Configure Deck Options", mw)
    deckOptionsConfigAction.setShortcut(QKeySequence("Ctrl+Shift+O"))
    qconnect(deckOptionsConfigAction.triggered, configure_deck_options_mode)
    remoteDecksSubMenu.addAction(deckOptionsConfigAction)

    # Action: Configure AnkiWeb synchronization
    ankiWebSyncConfigAction = QAction("Configure AnkiWeb Sync", mw)
    ankiWebSyncConfigAction.setShortcut(QKeySequence("Ctrl+Shift+W"))
    qconnect(ankiWebSyncConfigAction.triggered, configure_ankiweb_sync)
    remoteDecksSubMenu.addAction(ankiWebSyncConfigAction)

    # Action: Configure timer position
    timerConfigAction = QAction("Configure Timer", mw)
    timerConfigAction.setShortcut(QKeySequence("Ctrl+Shift+I"))
    qconnect(timerConfigAction.triggered, configure_timer)
    remoteDecksSubMenu.addAction(timerConfigAction)

    # Action: Configure AI Help
    aiHelpConfigAction = QAction("Configure AI Help", mw)
    aiHelpConfigAction.setShortcut(QKeySequence("Ctrl+Shift+H"))
    qconnect(aiHelpConfigAction.triggered, configure_ai_help)
    remoteDecksSubMenu.addAction(aiHelpConfigAction)

    # Separator
    remoteDecksSubMenu.addSeparator()

    # Action: Remote decks backup
    backupDecksAction = QAction("Remote Decks Backup", mw)
    backupDecksAction.setShortcut(QKeySequence("Ctrl+Shift+B"))
    qconnect(backupDecksAction.triggered, backup_decks)
    remoteDecksSubMenu.addAction(backupDecksAction)

    debugModeAction = QAction("Debug Mode", mw)
    debugModeAction.setShortcut(QKeySequence("Ctrl+Shift+L"))
    qconnect(debugModeAction.triggered, open_debug_mode)
    remoteDecksSubMenu.addAction(debugModeAction)

    # Action: Import test deck (development/debug only)
    try:
        from .src.templates_and_definitions import IS_DEVELOPMENT_MODE
        if IS_DEVELOPMENT_MODE:
            importTestDeckAction = QAction("Import Test Deck", mw)
            importTestDeckAction.setShortcut(QKeySequence("Ctrl+Shift+T"))
            qconnect(importTestDeckAction.triggered, import_test_deck)
            remoteDecksSubMenu.addAction(importTestDeckAction)
    except ImportError:
        pass  # If import fails, don't show the menu

    # =========================================================================
    # PYCMD HANDLER REGISTRATION
    # =========================================================================
    
    from aqt import gui_hooks
    
    def on_webview_did_receive_js_message(handled, message, context):
        """Handler for JavaScript pycmd messages from review cards."""
        if message.startswith("sheets2anki_ai_help:"):
            card_content = message[len("sheets2anki_ai_help:"):]
            handle_ai_help_request(card_content)
            return True, None
        return handled
    
    gui_hooks.webview_did_receive_js_message.append(on_webview_did_receive_js_message)