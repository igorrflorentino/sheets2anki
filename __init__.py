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


def configure_image_processor():
    """
    Opens the Image Processor configuration dialog.
    
    This function allows the user to configure:
    1. Enable/disable automatic image processing
    2. ImgBB API key for image hosting
    3. Google OAuth credentials for Sheets API
    4. Auto-process setting for syncs
    """
    try:
        from .src.image_processor_config_dialog import show_image_processor_config
        show_image_processor_config()
    except Exception as e:
        error_msg = errorTemplate.format(str(e))
        showInfo(error_msg)


def verify_repair_images():
    """
    Verifies and repairs broken image URLs in remote decks.
    
    This function:
    1. Shows styled deck selection dialog
    2. Verifies all image URLs in the selected deck
    3. Attempts to repair broken URLs using local backups
    4. Shows results to the user
    """
    try:
        from .src.config_manager import get_remote_decks
        from .src.image_processor import verify_and_repair_images
        from .src.compat import (
            QDialog, QVBoxLayout, QLabel, QListWidget, 
            QPushButton, QHBoxLayout, QFrame, QGroupBox,
            Palette_Window, WINDOW_MODAL, QProgressDialog
        )
        
        # Get remote decks
        remote_decks = get_remote_decks()
        
        if not remote_decks:
            showInfo("No remote decks configured.\n\nPlease add a remote deck first.")
            return
        
        # Create dialog
        dialog = QDialog(mw)
        dialog.setWindowTitle("Verify & Repair Images")
        dialog.setMinimumSize(650, 550)
        dialog.resize(700, 600)
        
        # Detect dark mode
        palette = dialog.palette()
        bg_color = palette.color(Palette_Window)
        is_dark = bg_color.lightness() < 128
        
        # Setup colors (addon standard)
        if is_dark:
            colors = {
                'bg': '#1e1e1e',
                'card_bg': '#2d2d2d',
                'text': '#ffffff',
                'text_secondary': '#b0b0b0',
                'border': '#404040',
                'accent_primary': '#2196F3',
                'accent_success': '#4CAF50',
                'button_bg': '#3d3d3d',
                'button_hover': '#4a4a4a',
                'list_bg': '#252525',
            }
        else:
            colors = {
                'bg': '#f5f5f5',
                'card_bg': '#ffffff',
                'text': '#1a1a1a',
                'text_secondary': '#666666',
                'border': '#d0d0d0',
                'accent_primary': '#1976D2',
                'accent_success': '#4CAF50',
                'button_bg': '#e0e0e0',
                'button_hover': '#d0d0d0',
                'list_bg': '#fafafa',
            }
        
        # Apply base stylesheet
        dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {colors['bg']};
                color: {colors['text']};
            }}
            QGroupBox {{
                font-weight: bold;
                font-size: 12pt;
                border: 1px solid {colors['border']};
                border-radius: 8px;
                margin-top: 16px;
                padding: 12px;
                padding-top: 28px;
                background-color: {colors['card_bg']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 12px;
                top: 4px;
                padding: 2px 10px;
                background-color: {colors['card_bg']};
                border-radius: 4px;
                color: {colors['text_secondary']};
                font-size: 12pt;
            }}
            QListWidget {{
                background-color: {colors['list_bg']};
                border: 1px solid {colors['border']};
                border-radius: 6px;
                padding: 5px;
                font-size: 12pt;
            }}
            QListWidget::item {{
                padding: 8px;
                border-radius: 4px;
            }}
            QListWidget::item:selected {{
                background-color: {colors['accent_primary']};
                color: white;
            }}
            QListWidget::item:hover {{
                background-color: {colors['button_hover']};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header section (addon standard)
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_frame.setStyleSheet(f"""
            QFrame#headerFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {colors['accent_primary']}, 
                    stop:1 {colors['accent_success']});
                border-radius: 12px;
                padding: 5px;
            }}
            QFrame#headerFrame QLabel {{
                background: transparent;
                color: white;
                border: none;
            }}
        """)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        title_label = QLabel("🔍 Verify & Repair Images")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        desc_label = QLabel(
            "Check all image URLs and automatically repair broken ones using local backups."
        )
        desc_label.setStyleSheet("font-size: 12pt; opacity: 0.9;")
        desc_label.setWordWrap(True)
        header_layout.addWidget(desc_label)
        
        layout.addWidget(header_frame)
        
        # Info section (addon standard)
        info_label = QLabel(
            "📋 <b>What this does:</b><br>"
            "• Checks all image URLs in the spreadsheet<br>"
            "• Identifies broken or inaccessible images<br>"
            "• Re-uploads from local backups if available"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet(f"""
            background-color: rgba(33, 150, 243, 0.15);
            border: 1px solid {colors['accent_primary']};
            border-radius: 6px;
            padding: 12px 16px;
            font-size: 12pt;
            color: {colors['text']};
        """)
        layout.addWidget(info_label)
        
        # Deck selection section (using GroupBox)
        deck_group = QGroupBox("Select Deck to Verify")
        deck_layout = QVBoxLayout()
        deck_layout.setSpacing(10)
        
        deck_list = QListWidget()
        for deck_url, deck_info in remote_decks.items():
            deck_name = deck_info.get("remote_deck_name", "Unknown")
            deck_list.addItem(f"📊 {deck_name}")
            deck_list.item(deck_list.count() - 1).setData(256, deck_url)
        
        deck_list.setCurrentRow(0)
        deck_layout.addWidget(deck_list)
        
        deck_group.setLayout(deck_layout)
        layout.addWidget(deck_group, 1)  # Give stretch factor
        
        # Buttons (addon standard)
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 10, 0, 0)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['button_bg']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                border-radius: 8px;
                padding: 12px 25px;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: {colors['button_hover']};
            }}
        """)
        
        verify_btn = QPushButton("✓ Verify & Repair")
        verify_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['accent_success']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 25px;
                font-size: 12pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #45a049;
            }}
        """)
        verify_btn.setDefault(True)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(verify_btn)
        
        layout.addLayout(buttons_layout)
        dialog.setLayout(layout)
        
        # Button handlers
        def on_verify():
            selected_item = deck_list.currentItem()
            if not selected_item:
                return
            
            deck_url = selected_item.data(256)
            deck_name = selected_item.text().replace("📊 ", "")
            dialog.accept()
            
            # Show styled progress
            progress = QProgressDialog(f"Verifying images for '{deck_name}'...", None, 0, 0, mw)
            progress.setWindowTitle("🔍 Image Verification")
            progress.setWindowModality(WINDOW_MODAL)
            progress.setMinimumWidth(400)
            progress.setStyleSheet(f"""
                QProgressDialog {{
                    background-color: {colors['bg']};
                }}
                QLabel {{
                    color: {colors['text']};
                    font-size: 12pt;
                    padding: 10px;
                }}
            """)
            progress.show()
            mw.app.processEvents()
            
            # Verify and repair
            success, message = verify_and_repair_images(deck_url)
            
            progress.close()
            
            # Show styled results
            if success:
                if "All" in message and "accessible" in message:
                    result_icon = "✅"
                    result_title = "All Images OK!"
                elif "Repaired:" in message:
                    result_icon = "🔧"
                    result_title = "Repairs Completed"
                else:
                    result_icon = "ℹ️"
                    result_title = "Verification Complete"
            else:
                result_icon = "⚠️"
                result_title = "Verification Issues"
            
            showInfo(f"{result_icon} {result_title}\n\n{message}")
        
        def on_cancel():
            dialog.reject()
        
        verify_btn.clicked.connect(on_verify)
        cancel_btn.clicked.connect(on_cancel)
        
        dialog.exec()
        
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
        language = config.get("language", "english")
        
        if not api_key:
            send_ai_error_to_card("No API key configured. Please configure AI Help first.")
            return
        
        if not model:
            send_ai_error_to_card("No model selected. Please configure AI Help first.")
            return
            
        # Add language instruction
        language_instruction = ""
        if language == "portuguese_br":
            language_instruction = "Por favor, responda em Português do Brasil.\n\n"
        elif language == "spanish_latam":
            language_instruction = "Por favor, responda en Español Latinoamericano.\n\n"
        else:
            language_instruction = "Please answer in English (American).\n\n"
            
        final_prompt = language_instruction + prompt
        
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
        
        call_ai_api_async(service, model, api_key, final_prompt, decoded_content, on_ai_response)
        
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

    # Action: Configure Image Processor
    imageProcessorConfigAction = QAction("Configure Image Processor", mw)
    imageProcessorConfigAction.setShortcut(QKeySequence("Ctrl+Shift+P"))
    qconnect(imageProcessorConfigAction.triggered, configure_image_processor)
    remoteDecksSubMenu.addAction(imageProcessorConfigAction)

    # Separator
    remoteDecksSubMenu.addSeparator()

    # Action: Verify & Repair Images
    verifyRepairImagesAction = QAction("Verify & Repair Images", mw)
    verifyRepairImagesAction.setShortcut(QKeySequence("Ctrl+Shift+V"))
    qconnect(verifyRepairImagesAction.triggered, verify_repair_images)
    remoteDecksSubMenu.addAction(verifyRepairImagesAction)

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