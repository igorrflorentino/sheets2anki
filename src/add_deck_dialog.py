"""
Enhanced dialog for adding new remote decks.

This module provides a modern, user-friendly interface for adding decks
with support for automatic naming and conflict resolution.
"""

from .compat import AlignCenter
from .compat import DialogAccepted
from .compat import QDialog
from .compat import QFrame
from .compat import QGroupBox
from .compat import QHBoxLayout
from .compat import QLabel
from .compat import QLineEdit
from .compat import QMessageBox
from .compat import QProgressBar
from .compat import QPushButton
from .compat import QTimer
from .compat import QVBoxLayout
from .compat import QWidget
from .compat import mw
from .compat import safe_exec
from .config_manager import add_remote_deck
from .config_manager import get_remote_decks
from .config_manager import is_deck_disconnected
from .data_processor import RemoteDeckError
from .data_processor import getRemoteDeck
from .templates_and_definitions import DEFAULT_PARENT_DECK_NAME
from .styled_messages import StyledMessageBox
from .utils import get_or_create_deck, validate_url, get_spreadsheet_id_from_url, add_debug_message


def is_dark_mode():
    """Detects if Anki is running in dark mode."""
    try:
        from aqt import theme
        if hasattr(theme, 'theme_manager'):
            return theme.theme_manager.night_mode
        # Fallback for older Anki versions
        from aqt import mw as main_window
        if main_window and hasattr(main_window, 'pm'):
            return main_window.pm.night_mode()
    except Exception:
        pass
    return False


def get_colors():
    """Returns color palette based on current theme."""
    if is_dark_mode():
        # Dark mode colors
        return {
            "primary": "#5BA3E0",
            "primary_dark": "#4A90D9",
            "primary_light": "#2A3F50",
            "success": "#3CB371",
            "success_light": "#1E3A2A",
            "warning": "#E6A817",
            "warning_light": "#3D3520",
            "error": "#E05555",
            "error_light": "#3D2020",
            "text_primary": "#E0E0E0",
            "text_secondary": "#A0A0A0",
            "text_muted": "#707070",
            "background": "#2D2D2D",
            "background_secondary": "#383838",
            "border": "#505050",
            "border_light": "#454545",
        }
    else:
        # Light mode colors
        return {
            "primary": "#4A90D9",
            "primary_dark": "#357ABD",
            "primary_light": "#E8F4FC",
            "success": "#28A745",
            "success_light": "#D4EDDA",
            "warning": "#FFC107",
            "warning_light": "#FFF3CD",
            "error": "#DC3545",
            "error_light": "#F8D7DA",
            "text_primary": "#2C3E50",
            "text_secondary": "#6C757D",
            "text_muted": "#ADB5BD",
            "background": "#FFFFFF",
            "background_secondary": "#F8F9FA",
            "border": "#DEE2E6",
            "border_light": "#E9ECEF",
        }


class AddDeckDialog(QDialog):
    """
    Modern, user-friendly dialog for adding new remote decks.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Remote Deck")
        self.setModal(True)
        self.setMinimumWidth(520)
        self.setMaximumWidth(600)

        self.remote_deck = None
        self.suggested_name = ""
        self.validation_timer = QTimer()
        self.current_step = 1
        
        # Get colors based on current theme
        self.colors = get_colors()

        self._setup_styles()
        self._setup_ui()
        self._connect_signals()
        self._adjust_dialog_size()

    def _setup_styles(self):
        """Sets up the dialog's stylesheet."""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.colors['background']};
            }}
            QGroupBox {{
                font-weight: bold;
                font-size: 13px;
                color: {self.colors['text_primary']};
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: {self.colors['background']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                background-color: {self.colors['background']};
            }}
            QLineEdit {{
                padding: 12px 16px;
                font-size: 13px;
                border: 2px solid {self.colors['border']};
                border-radius: 8px;
                background-color: {self.colors['background']};
                color: {self.colors['text_primary']};
            }}
            QLineEdit:focus {{
                border-color: {self.colors['primary']};
                background-color: {self.colors['primary_light']};
            }}
            QLineEdit:disabled {{
                background-color: {self.colors['background_secondary']};
                color: {self.colors['text_muted']};
            }}
            QLabel {{
                color: {self.colors['text_primary']};
            }}
        """)

    def _setup_ui(self):
        """Sets up the modern user interface."""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(24, 20, 24, 20)

        # ===== HEADER SECTION =====
        header_widget = self._create_header()
        main_layout.addWidget(header_widget)

        # ===== STEP 1: URL INPUT =====
        step1_group = self._create_step1_section()
        main_layout.addWidget(step1_group)

        # ===== STEP 2: PREVIEW (Initially hidden) =====
        self.step2_group = self._create_step2_section()
        self.step2_group.setVisible(False)
        main_layout.addWidget(self.step2_group)

        # ===== PROGRESS BAR =====
        self.progress_bar = self._create_progress_bar()
        main_layout.addWidget(self.progress_bar)

        # ===== SPACER =====
        main_layout.addStretch()

        # ===== BUTTONS =====
        buttons_layout = self._create_buttons()
        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)

    def _create_header(self):
        """Creates the header section with title and description."""
        header = QWidget()
        layout = QVBoxLayout(header)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 8)

        # Title with icon
        title = QLabel("📊 Add Remote Deck")
        title.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {self.colors['text_primary']};
            padding-bottom: 4px;
        """)
        layout.addWidget(title)

        # Subtitle/description
        subtitle = QLabel(
            "Connect a Google Sheets spreadsheet to sync flashcards automatically."
        )
        subtitle.setStyleSheet(f"""
            font-size: 12px;
            color: {self.colors['text_secondary']};
            line-height: 1.4;
        """)
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        # Separator line
        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet(f"background-color: {self.colors['border_light']};")
        layout.addWidget(separator)

        return header

    def _create_step1_section(self):
        """Creates Step 1: URL input section."""
        group = QGroupBox("Step 1: Paste Spreadsheet URL")
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 20, 16, 16)

        # Help text
        help_text = QLabel(
            "💡 <b>How to get the URL:</b> Open your Google Sheets spreadsheet, "
            "click <b>Share</b>, set access to <b>\"Anyone with the link\"</b>, "
            "then copy the URL from your browser."
        )
        help_text.setStyleSheet(f"""
            font-size: 11px;
            color: {self.colors['text_secondary']};
            background-color: {self.colors['background_secondary']};
            padding: 10px 12px;
            border-radius: 6px;
            line-height: 1.5;
        """)
        help_text.setWordWrap(True)
        layout.addWidget(help_text)

        # URL input container
        input_container = QWidget()
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(8)

        # URL input field
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("https://docs.google.com/spreadsheets/d/...")
        self.url_edit.setMinimumHeight(44)
        input_layout.addWidget(self.url_edit)

        # Status indicator button (visual only)
        self.status_indicator = QLabel("⚪")
        self.status_indicator.setFixedSize(32, 32)
        self.status_indicator.setAlignment(AlignCenter)
        self.status_indicator.setStyleSheet(f"""
            font-size: 16px;
            background-color: {self.colors['background_secondary']};
            border-radius: 16px;
        """)
        input_layout.addWidget(self.status_indicator)

        layout.addWidget(input_container)

        # Status message area
        self.status_container = QWidget()
        status_layout = QHBoxLayout(self.status_container)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(8)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet(f"""
            font-size: 12px;
            color: {self.colors['text_secondary']};
            padding: 4px 0;
        """)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()

        layout.addWidget(self.status_container)

        group.setLayout(layout)
        return group

    def _create_step2_section(self):
        """Creates Step 2: Preview section."""
        group = QGroupBox("Step 2: Review Deck Details")
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 20, 16, 16)

        # Statistics container
        self.stats_widget = QWidget()
        stats_layout = QHBoxLayout(self.stats_widget)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(12)

        # We'll add stat cards dynamically
        self.stats_layout = stats_layout
        layout.addWidget(self.stats_widget)

        # Conflict warning (initially hidden)
        self.conflict_warning = QLabel("")
        self.conflict_warning.setVisible(False)
        self.conflict_warning.setStyleSheet(f"""
            font-size: 12px;
            color: {self.colors['warning']};
            background-color: {self.colors['warning_light']};
            border: 1px solid {self.colors['warning']};
            border-radius: 6px;
            padding: 10px 14px;
        """)
        self.conflict_warning.setWordWrap(True)
        layout.addWidget(self.conflict_warning)

        # Deck name preview section
        name_section = QWidget()
        name_layout = QVBoxLayout(name_section)
        name_layout.setContentsMargins(0, 8, 0, 0)
        name_layout.setSpacing(6)

        name_label = QLabel("📁 Deck will be created as:")
        name_label.setStyleSheet(f"""
            font-size: 11px;
            color: {self.colors['text_secondary']};
            font-weight: bold;
        """)
        name_layout.addWidget(name_label)

        self.name_preview = QLabel("")
        self.name_preview.setStyleSheet(f"""
            font-size: 14px;
            font-weight: bold;
            color: {self.colors['primary']};
            background-color: {self.colors['primary_light']};
            padding: 12px 16px;
            border-radius: 6px;
            border: 1px solid {self.colors['primary']};
        """)
        self.name_preview.setWordWrap(True)
        name_layout.addWidget(self.name_preview)

        layout.addWidget(name_section)

        group.setLayout(layout)
        return group

    def _create_stat_card(self, icon, value, label):
        """Creates a statistics card widget."""
        card = QWidget()
        card.setStyleSheet(f"""
            QWidget {{
                background-color: {self.colors['background_secondary']};
                border-radius: 8px;
                padding: 8px;
            }}
        """)
        card.setMinimumWidth(90)
        card.setMaximumWidth(120)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        # Icon and value
        value_label = QLabel(f"{icon} {value}")
        value_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {self.colors['text_primary']};
        """)
        value_label.setAlignment(AlignCenter)
        layout.addWidget(value_label)

        # Label
        text_label = QLabel(label)
        text_label.setStyleSheet(f"""
            font-size: 10px;
            color: {self.colors['text_secondary']};
        """)
        text_label.setAlignment(AlignCenter)
        layout.addWidget(text_label)

        return card

    def _create_progress_bar(self):
        """Creates a modern progress bar."""
        progress = QProgressBar()
        progress.setVisible(False)
        progress.setMaximumHeight(4)
        progress.setTextVisible(False)
        progress.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                background-color: {self.colors['border_light']};
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background-color: {self.colors['primary']};
                border-radius: 2px;
            }}
        """)
        return progress

    def _create_buttons(self):
        """Creates the button section."""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(12)

        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setMinimumHeight(40)
        self.cancel_button.setMinimumWidth(100)
        self.cancel_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['background']};
                color: {self.colors['text_secondary']};
                border: 2px solid {self.colors['border']};
                border-radius: 8px;
                font-size: 13px;
                font-weight: 500;
                padding: 8px 20px;
            }}
            QPushButton:hover {{
                background-color: {self.colors['background_secondary']};
                border-color: {self.colors['text_secondary']};
            }}
            QPushButton:pressed {{
                background-color: {self.colors['border']};
            }}
        """)

        # Add button
        self.add_button = QPushButton("✓ Add Deck")
        self.add_button.setEnabled(False)
        self.add_button.setMinimumHeight(40)
        self.add_button.setMinimumWidth(140)
        self.add_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['success']};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
                padding: 8px 24px;
            }}
            QPushButton:hover {{
                background-color: #218838;
            }}
            QPushButton:pressed {{
                background-color: #1E7E34;
            }}
            QPushButton:disabled {{
                background-color: {self.colors['border']};
                color: {self.colors['text_muted']};
            }}
        """)

        layout.addStretch()
        layout.addWidget(self.cancel_button)
        layout.addWidget(self.add_button)

        return layout

    def _connect_signals(self):
        """Connects interface signals."""
        self.validation_timer.setSingleShot(True)
        self.validation_timer.timeout.connect(self._validate_url_auto)

        self.url_edit.textChanged.connect(self._on_url_changed)
        self.add_button.clicked.connect(self._add_deck)
        self.cancel_button.clicked.connect(self.reject)

    def _adjust_dialog_size(self):
        """Adjusts window size based on visible content."""
        QTimer.singleShot(10, self._do_adjust_size)

    def _do_adjust_size(self):
        """Executes window size adjustment."""
        layout = self.layout()
        if not layout:
            return

        layout.activate()
        size_hint = self.sizeHint()
        ideal_width = max(size_hint.width(), 520)
        ideal_height = max(size_hint.height(), 300)
        self.resize(ideal_width, ideal_height)
        self.updateGeometry()

    def _check_duplicate_spreadsheet(self, url):
        """
        Checks if a spreadsheet is already registered.

        Args:
            url (str): URL to check

        Returns:
            tuple: (is_duplicate, deck_info, is_disconnected)
        """
        try:
            spreadsheet_id = get_spreadsheet_id_from_url(url)
            remote_decks = get_remote_decks()
            if spreadsheet_id in remote_decks:
                deck_info = remote_decks[spreadsheet_id]
                is_disconnected = False
                return True, deck_info, is_disconnected
            return False, None, False
        except ValueError:
            return False, None, False

    def _on_url_changed(self):
        """Called when URL is changed - starts automatic validation."""
        self.add_button.setEnabled(False)
        self.step2_group.setVisible(False)
        self.remote_deck = None
        self.suggested_name = ""
        self._adjust_dialog_size()

        url = self.url_edit.text().strip()

        if not url:
            self._show_status("Waiting for URL...", "waiting")
            self.validation_timer.stop()
            return

        # Immediate feedback for obviously invalid URLs
        if not url.startswith(("http://", "https://")):
            self._show_status("URL must start with http:// or https://", "error")
            self.validation_timer.stop()
            return

        if "docs.google.com/spreadsheets" not in url:
            self._show_status("Please enter a valid Google Sheets URL", "error")
            self.validation_timer.stop()
            return

        # Start timer for automatic validation
        self._show_status("Validating URL...", "validating")
        self.validation_timer.stop()
        self.validation_timer.start(1200)

    def _validate_url_auto(self):
        """Validates URL automatically (called by timer)."""
        from .deck_manager import DeckNameManager

        url = self.url_edit.text().strip()

        if not url:
            return

        # Check if URL is already in use
        is_duplicate, deck_info, is_disconnected = self._check_duplicate_spreadsheet(url)
        if is_duplicate:
            if is_disconnected:
                self._show_status("This spreadsheet will reconnect an existing deck", "warning")
            else:
                deck_name = deck_info.get('remote_deck_name', 'Unknown') if deck_info else 'Unknown'
                self._show_status(f"Already registered as: {deck_name}", "error")
                self.add_button.setEnabled(False)
                return

        self._show_progress(True)

        try:
            # Validate URL format and get TSV URL
            self.tsv_url = validate_url(url)

            # Try to load deck
            self.remote_deck = getRemoteDeck(self.tsv_url)

            # Extract suggested name
            self.suggested_name = DeckNameManager.extract_remote_name_from_url(url)

            # Show preview
            self._show_deck_preview()

            self._show_status("URL validated successfully!", "success")
            self.add_button.setEnabled(True)

        except RemoteDeckError as e:
            self._show_status(f"Error: {str(e)}", "error")
        except Exception as e:
            self._show_status(f"Validation error: {str(e)}", "error")
        finally:
            self._show_progress(False)

    def _show_progress(self, show):
        """Shows/hides progress bar."""
        if show:
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)
        else:
            self.progress_bar.setVisible(False)
        self._adjust_dialog_size()

    def _show_status(self, message, status_type="info"):
        """Shows status message with visual indicator."""
        indicators = {
            "waiting": ("⚪", self.colors['text_muted'], self.colors['background_secondary']),
            "validating": ("🔄", self.colors['primary'], self.colors['primary_light']),
            "success": ("✅", self.colors['success'], self.colors['success_light']),
            "warning": ("⚠️", self.colors['warning'], self.colors['warning_light']),
            "error": ("❌", self.colors['error'], self.colors['error_light']),
        }

        icon, color, bg = indicators.get(status_type, ("ℹ️", self.colors['text_secondary'], self.colors['background_secondary']))

        self.status_indicator.setText(icon)
        self.status_indicator.setStyleSheet(f"""
            font-size: 16px;
            background-color: {bg};
            border-radius: 16px;
        """)

        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"""
            font-size: 12px;
            color: {color};
            padding: 4px 0;
            font-weight: {'bold' if status_type in ['success', 'error'] else 'normal'};
        """)

    def _show_deck_preview(self):
        """Shows preview of validated deck with statistics."""
        if not self.remote_deck:
            return

        # Clear existing stat cards
        while self.stats_layout.count():
            item = self.stats_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Get statistics
        deck_stats = self.remote_deck.get_statistics()

        # Create stat cards
        valid_lines = deck_stats.get("valid_note_lines", 0)
        self.stats_layout.addWidget(self._create_stat_card("📝", str(valid_lines), "Questions"))

        unique_students = deck_stats.get("unique_students_count", 0)
        if unique_students > 0:
            self.stats_layout.addWidget(self._create_stat_card("👥", str(unique_students), "Students"))

        potential_notes = deck_stats.get("total_potential_anki_notes", 0)
        if potential_notes > 0 and potential_notes != valid_lines:
            self.stats_layout.addWidget(self._create_stat_card("🎯", str(potential_notes), "Anki Notes"))

        invalid_lines = deck_stats.get("invalid_note_lines", 0)
        if invalid_lines > 0:
            self.stats_layout.addWidget(self._create_stat_card("⚠️", str(invalid_lines), "Skipped"))

        self.stats_layout.addStretch()

        # Update deck name preview
        self._update_deck_name_preview()

        self.step2_group.setVisible(True)
        self._adjust_dialog_size()

    def _update_deck_name_preview(self):
        """Updates deck name preview with conflict detection."""
        from .deck_manager import DeckNameManager

        if not self.suggested_name:
            return

        current_url = self.url_edit.text().strip()
        final_remote_name = DeckNameManager.resolve_remote_name_conflict(
            current_url, self.suggested_name
        )

        parent_name = DEFAULT_PARENT_DECK_NAME
        full_name = f"{parent_name}::{final_remote_name}"

        if final_remote_name != self.suggested_name:
            # CONFLICT - Show warning
            self.conflict_warning.setText(
                f"⚠️ Name conflict detected! Original: '{self.suggested_name}' → "
                f"Renamed to: '{final_remote_name}'"
            )
            self.conflict_warning.setVisible(True)

            self.name_preview.setText(full_name)
            self.name_preview.setStyleSheet(f"""
                font-size: 14px;
                font-weight: bold;
                color: {self.colors['warning']};
                background-color: {self.colors['warning_light']};
                padding: 12px 16px;
                border-radius: 6px;
                border: 1px solid {self.colors['warning']};
            """)
        else:
            # No conflict
            self.conflict_warning.setVisible(False)
            self.name_preview.setText(full_name)
            self.name_preview.setStyleSheet(f"""
                font-size: 14px;
                font-weight: bold;
                color: {self.colors['primary']};
                background-color: {self.colors['primary_light']};
                padding: 12px 16px;
                border-radius: 6px;
                border: 1px solid {self.colors['primary']};
            """)

        self._adjust_dialog_size()

    def _add_deck(self):
        """Adds the remote deck."""
        from .deck_manager import DeckNameManager

        url = self.url_edit.text().strip()

        if not url or not self.remote_deck:
            StyledMessageBox.warning(self, "Validation Required", "Please validate the URL before proceeding.", detailed_text="The URL needs to be checked to ensure it points to a valid Google Sheet.")
            return

        # Final validation
        is_duplicate, deck_info, is_disconnected = self._check_duplicate_spreadsheet(url)
        if is_duplicate and not is_disconnected:
            deck_name = deck_info.get('remote_deck_name', 'Unknown') if deck_info else 'Unknown'
            StyledMessageBox.warning(
                self,
                "Already Registered",
                "This spreadsheet is already connected.",
                detailed_text=f"It is currently registered as: {deck_name}\n\nYou don't need to add it again."
            )
            return

        # Generate deck name
        parent_name = DEFAULT_PARENT_DECK_NAME
        final_remote_name = DeckNameManager.resolve_remote_name_conflict(
            url, self.suggested_name
        )
        full_name = f"{parent_name}::{final_remote_name}"

        self._show_progress(True)
        self.add_button.setEnabled(False)
        self.add_button.setText("Adding...")

        try:
            # Create deck in Anki
            deck_id, actual_name = get_or_create_deck(mw.col, full_name)

            # Add to configuration
            from .config_manager import create_deck_info

            deck_info = create_deck_info(
                url=url,
                local_deck_id=deck_id,
                local_deck_name=actual_name,
                remote_deck_name=final_remote_name,
            )

            add_remote_deck(url, deck_info)

            # Sync deck name
            sync_result = DeckNameManager.sync_deck_with_config(url)
            if sync_result:
                synced_deck_id, synced_name = sync_result
                add_debug_message(f"Deck synchronized: {actual_name} → {synced_name}", "ADD_DECK")

            # Apply options
            try:
                from .utils import apply_sheets2anki_options_to_deck
                apply_sheets2anki_options_to_deck(deck_id)
            except Exception as e:
                add_debug_message(f"Warning: Error applying options: {e}", "ADD_DECK")

            # Reconnect if disconnected
            if is_deck_disconnected(url):
                from .config_manager import reconnect_deck
                reconnect_deck(url)

            self.accept()
            
            # Show success message (optional, but nice)
            # StyledMessageBox.success(self.parent(), "Success", f"Deck '{final_remote_name}' added successfully!")

        except Exception as e:
            StyledMessageBox.critical(self, "Error Adding Deck", "An unexpected error occurred while adding the deck.", detailed_text=str(e))
            self.add_button.setEnabled(True)
            self.add_button.setText("✓ Add Deck")
        finally:
            self._show_progress(False)

    def get_deck_info(self):
        """Returns information about the added deck."""
        from .deck_manager import DeckNameManager

        url = self.url_edit.text().strip()
        from .config_manager import get_deck_local_name

        final_remote_name = DeckNameManager.resolve_remote_name_conflict(
            url, self.suggested_name
        )
        parent_name = DEFAULT_PARENT_DECK_NAME
        full_name = f"{parent_name}::{final_remote_name}"

        actual_name = get_deck_local_name(url) or full_name

        return {"url": url, "name": actual_name, "is_automatic": True}


def show_add_deck_dialog(parent=None):
    """
    Shows the dialog for adding a new remote deck.

    Args:
        parent: Parent widget for the dialog

    Returns:
        tuple: (success, deck_info)
    """
    dialog = AddDeckDialog(parent)

    if safe_exec(dialog) == DialogAccepted:
        return True, dialog.get_deck_info()

    return False, None
