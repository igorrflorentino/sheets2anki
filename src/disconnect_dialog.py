"""
Dialog for disconnecting remote decks.

This module provides an interface for the user
to select and disconnect multiple remote decks using checkboxes.
"""

from .compat import DialogAccepted
from .compat import QApplication
from .compat import QCheckBox
from .compat import QDialog
from .compat import QFrame
from .compat import QGroupBox
from .compat import QHBoxLayout
from .compat import QLabel
from .compat import QMessageBox
from .compat import QPushButton
from .compat import QScrollArea
from .compat import QVBoxLayout
from .compat import QWidget
from .compat import Qt
from .compat import Palette_Window
from .compat import mw
from .compat import safe_exec
from .config_manager import get_deck_local_name
from .config_manager import get_deck_remote_name
from .config_manager import get_remote_decks
from .utils import add_debug_message


def clean_url_for_browser(url):
    """
    Removes the '&output=tsv' ending from URL to allow browser viewing.

    Args:
        url (str): Complete URL with TSV ending

    Returns:
        str: Clean URL for browser viewing
    """
    if url.endswith("&output=tsv"):
        return url[:-11]  # Removes '&output=tsv'
    elif url.endswith("&single=true&output=tsv"):
        return url[:-23]  # Removes '&single=true&output=tsv'
    return url


def copy_url_to_clipboard(url):
    """
    Copies the clean URL to system clipboard.

    Args:
        url (str): URL to copy
    """
    try:
        clean_url = clean_url_for_browser(url)
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(clean_url)
            return True
        return False
    except Exception as e:
        add_debug_message(f"Error copying URL: {e}", "UI")
        return False


class DisconnectDialog(QDialog):
    """
    Dialog for disconnecting remote decks with checkboxes.

    Allows multiple selection through checkboxes to disconnect
    multiple remote decks at the same time.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Disconnect Remote Decks")
        self.setModal(True)
        self.setMinimumWidth(750)
        self.setMinimumHeight(700)

        self.remote_decks = []
        self.deck_checkboxes = {}  # URL -> QCheckBox
        self.selected_urls = []

        # Detect dark mode
        palette = self.palette()
        bg_color = palette.color(Palette_Window)
        self.is_dark_mode = bg_color.lightness() < 128

        # Define color scheme
        self._setup_colors()
        self._setup_ui()
        self._apply_styles()
        self._load_decks()
        self._connect_signals()

    def _setup_colors(self):
        """Sets up color scheme based on theme."""
        if self.is_dark_mode:
            self.colors = {
                'bg': '#1e1e1e',
                'card_bg': '#2d2d2d',
                'text': '#ffffff',
                'text_secondary': '#b0b0b0',
                'border': '#404040',
                'accent_danger': '#e53935',
                'accent_warning': '#FF9800',
                'accent_info': '#2196F3',
                'button_bg': '#3d3d3d',
                'button_hover': '#4a4a4a',
                'row_hover': '#363636',
                'warning_bg': 'rgba(255, 152, 0, 0.15)',
            }
        else:
            self.colors = {
                'bg': '#f5f5f5',
                'card_bg': '#ffffff',
                'text': '#1a1a1a',
                'text_secondary': '#666666',
                'border': '#d0d0d0',
                'accent_danger': '#d32f2f',
                'accent_warning': '#FF9800',
                'accent_info': '#1976D2',
                'button_bg': '#e0e0e0',
                'button_hover': '#d0d0d0',
                'row_hover': '#f0f0f0',
                'warning_bg': 'rgba(255, 152, 0, 0.1)',
            }

    def _apply_styles(self):
        """Applies styles to the dialog."""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.colors['bg']};
                color: {self.colors['text']};
            }}
            QGroupBox {{
                font-weight: bold;
                font-size: 12pt;
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                margin-top: 16px;
                padding: 12px;
                padding-top: 28px;
                background-color: {self.colors['card_bg']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 12px;
                top: 4px;
                padding: 2px 10px;
                background-color: {self.colors['card_bg']};
                border-radius: 4px;
                color: {self.colors['text_secondary']};
                font-size: 12pt;
            }}
            QScrollArea {{
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                background-color: {self.colors['card_bg']};
            }}
            QScrollArea > QWidget > QWidget {{
                background-color: {self.colors['card_bg']};
            }}

        """)

    def _setup_ui(self):
        """Sets up the user interface."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header section with danger styling
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_frame.setStyleSheet(f"""
            QFrame#headerFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.colors['accent_danger']}, 
                    stop:1 {self.colors['accent_warning']});
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

        # Title with icon
        title_label = QLabel("🔌 Disconnect Remote Decks")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        header_layout.addWidget(title_label)

        # Description
        desc_label = QLabel(
            "Select which remote decks you want to disconnect. "
            "Local decks will remain in Anki but will no longer be synchronized."
        )
        desc_label.setStyleSheet("font-size: 12pt; opacity: 0.9;")
        desc_label.setWordWrap(True)
        header_layout.addWidget(desc_label)

        layout.addWidget(header_frame)

        # Warning banner
        warning_frame = QFrame()
        warning_frame.setObjectName("warningFrame")
        warning_frame.setStyleSheet(f"""
            QFrame#warningFrame {{
                background-color: {self.colors['warning_bg']};
                border: 2px solid {self.colors['accent_warning']};
                border-radius: 8px;
                padding: 8px;
            }}
            QFrame#warningFrame QLabel {{
                background: transparent;
                border: none;
            }}
        """)
        warning_layout = QHBoxLayout(warning_frame)
        warning_layout.setContentsMargins(15, 12, 15, 12)

        warning_icon = QLabel("⚠️")
        warning_icon.setStyleSheet("font-size: 20pt;")
        warning_layout.addWidget(warning_icon)

        warning_text = QLabel(
            "This action will permanently disconnect selected decks. "
            "To reconnect, you will need to add them again."
        )
        warning_text.setStyleSheet(f"color: {self.colors['accent_warning']}; font-size: 12pt;")
        warning_text.setWordWrap(True)
        warning_layout.addWidget(warning_text)

        layout.addWidget(warning_frame)

        # Remote decks section
        remote_group = QGroupBox("Configured Remote Decks")
        remote_layout = QVBoxLayout()
        remote_layout.setSpacing(10)

        # Scroll area for checkboxes
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(100)  # Reduced minimum height

        self.checkboxes_widget = QWidget()
        self.checkboxes_layout = QVBoxLayout()
        self.checkboxes_widget.setLayout(self.checkboxes_layout)
        self.checkboxes_layout.setContentsMargins(10, 10, 10, 10)
        self.checkboxes_layout.setSpacing(5)

        scroll_area.setWidget(self.checkboxes_widget)
        remote_layout.addWidget(scroll_area, 1)  # Give scroll area stretch factor

        remote_group.setLayout(remote_layout)
        layout.addWidget(remote_group, 1)  # Give group box stretch factor

        # Bulk selection buttons - OUTSIDE the group box
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        buttons_layout.setContentsMargins(0, 5, 0, 5)

        btn_style = f"""
            QPushButton {{
                background-color: {self.colors['button_bg']};
                color: {self.colors['text']};
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: {self.colors['button_hover']};
                border-color: {self.colors['accent_info']};
            }}
        """

        self.select_all_button = QPushButton("✓ Select All")
        self.select_all_button.setStyleSheet(btn_style)
        self.select_all_button.setToolTip("Selects all decks for disconnection")

        self.select_none_button = QPushButton("✗ Deselect All")
        self.select_none_button.setStyleSheet(btn_style)
        self.select_none_button.setToolTip("Deselects all decks")

        self.invert_selection_button = QPushButton("⇄ Invert")
        self.invert_selection_button.setStyleSheet(btn_style)
        self.invert_selection_button.setToolTip("Inverts current selection")

        buttons_layout.addWidget(self.select_all_button)
        buttons_layout.addWidget(self.select_none_button)
        buttons_layout.addWidget(self.invert_selection_button)
        buttons_layout.addStretch()

        layout.addLayout(buttons_layout)

        # Selection information
        self.selection_info = QLabel("")
        self.selection_info.setObjectName("selectionInfo")
        layout.addWidget(self.selection_info)

        # Option to delete local data
        self.delete_local_data_checkbox = QCheckBox(
            "🗑️ Delete local data (decks, cards, notes and note types)"
        )
        self.delete_local_data_checkbox.setToolTip(
            "ATTENTION: This action is irreversible!\n\n"
            "If checked, all local data for selected decks will be deleted:\n"
            "• Local decks and subdecks\n"
            "• All cards and notes\n"
            "• Specific note types (if not used in other decks)\n\n"
            "Use with caution!"
        )
        self.delete_local_data_checkbox.setStyleSheet(f"""
            QCheckBox {{
                padding: 14px 16px;
                background-color: {self.colors['warning_bg']};
                border: 2px solid {self.colors['accent_danger']};
                border-radius: 8px;
                color: {self.colors['text']};
                font-weight: bold;
                font-size: 12pt;
            }}
            QCheckBox:hover {{
                background-color: rgba(229, 57, 53, 0.2);
            }}
        """)
        layout.addWidget(self.delete_local_data_checkbox)

        # Main buttons
        main_buttons_layout = QHBoxLayout()
        main_buttons_layout.setContentsMargins(0, 10, 0, 0)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['button_bg']};
                color: {self.colors['text']};
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                padding: 12px 25px;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: {self.colors['button_hover']};
            }}
        """)

        self.disconnect_button = QPushButton("🔌 Disconnect Selected")
        self.disconnect_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['accent_danger']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 25px;
                font-size: 12pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #c62828;
            }}
            QPushButton:disabled {{
                background-color: {self.colors['border']};
                color: {self.colors['text_secondary']};
            }}
        """)

        main_buttons_layout.addStretch()
        main_buttons_layout.addWidget(self.cancel_button)
        main_buttons_layout.addWidget(self.disconnect_button)

        layout.addLayout(main_buttons_layout)
        self.setLayout(layout)

    def _get_copy_button_style(self):
        """Returns the style for copy URL buttons."""
        return f"""
            QPushButton {{
                background-color: {self.colors['button_bg']};
                color: {self.colors['text']};
                border: 1px solid {self.colors['border']};
                border-radius: 4px;
                padding: 4px 10px;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: {self.colors['accent_info']};
                color: white;
                border-color: {self.colors['accent_info']};
            }}
        """

    def _connect_signals(self):
        """Connects interface signals."""
        # Bulk selection buttons
        self.select_all_button.clicked.connect(self._select_all)
        self.select_none_button.clicked.connect(self._select_none)
        self.invert_selection_button.clicked.connect(self._invert_selection)

        # Main buttons
        self.disconnect_button.clicked.connect(self._disconnect_selected)
        self.cancel_button.clicked.connect(self.reject)

    def _load_decks(self):
        """Loads remote decks as checkboxes."""
        # Clear existing checkboxes
        for checkbox in self.deck_checkboxes.values():
            checkbox.setParent(None)
        self.deck_checkboxes.clear()
        self.remote_decks.clear()

        # Load remote decks
        remote_decks = get_remote_decks()

        if not remote_decks:
            # Show message if no decks
            no_decks_label = QLabel("No remote deck configured.")
            no_decks_label.setStyleSheet(f"""
                color: {self.colors['text_secondary']};
                font-style: italic;
                padding: 30px;
                font-size: 12pt;
            """)
            no_decks_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.checkboxes_layout.addWidget(no_decks_label)
            return

        for hash_key, deck_info in remote_decks.items():
            local_deck_id = deck_info["local_deck_id"]
            deck = None
            if mw.col and hasattr(mw.col, "decks"):
                deck = mw.col.decks.get(local_deck_id)

            # Get URL and remote deck name
            remote_deck_url = deck_info.get("remote_deck_url", "")
            remote_name = get_deck_remote_name(remote_deck_url) or "Remote Deck"

            # Create row widget
            row_widget = QFrame()
            row_id = hash_key[:8] if hash_key else "unknown"
            row_widget.setObjectName(f"row_{row_id}")
            row_widget.setStyleSheet(f"""
                QFrame#row_{row_id} {{
                    background-color: {self.colors['card_bg']};
                    border-radius: 6px;
                    padding: 4px;
                }}
                QFrame#row_{row_id}:hover {{
                    background-color: {self.colors['row_hover']};
                }}
            """)
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(8, 6, 8, 6)
            row_layout.setSpacing(10)

            # Check if deck exists locally
            if deck and deck["name"].strip().lower() != "default":
                # Deck exists locally
                local_deck_name = deck["name"]
                card_count = 0
                if mw.col and hasattr(mw.col, "find_cards"):
                    escaped_deck_name = local_deck_name.replace('"', '\\"')
                    card_count = len(mw.col.find_cards(f'deck:"{escaped_deck_name}"'))

                checkbox_text = f"{remote_name}"
                checkbox = QCheckBox(checkbox_text)
                checkbox.setToolTip(
                    f"Remote deck: {remote_name}\nLocal deck: {local_deck_name}\nURL: {remote_deck_url}"
                )

                # Card count label
                count_label = QLabel(f"📚 {card_count} cards")
                count_label.setStyleSheet(f"""
                    color: {self.colors['text_secondary']};
                    font-size: 12pt;
                    padding: 2px 8px;
                    background-color: {self.colors['bg']};
                    border-radius: 4px;
                """)

                row_layout.addWidget(checkbox)
                row_layout.addWidget(count_label)

            else:
                # Deck was deleted locally
                local_deck_name = (
                    get_deck_local_name(remote_deck_url) or "Deleted Local Deck"
                )

                checkbox_text = f"🗑️ {remote_name}"
                checkbox = QCheckBox(checkbox_text)
                checkbox.setToolTip(
                    f"Remote deck: {remote_name}\nLocal deck was deleted: {local_deck_name}\nConfiguration still exists.\nURL: {remote_deck_url}"
                )

                # Status label
                status_label = QLabel("Local deck deleted")
                status_label.setStyleSheet(f"""
                    color: {self.colors['text_secondary']};
                    font-size: 12pt;
                    font-style: italic;
                    padding: 2px 8px;
                    background-color: {self.colors['bg']};
                    border-radius: 4px;
                """)

                row_layout.addWidget(checkbox)
                row_layout.addWidget(status_label)
                card_count = 0

            # Copy URL button
            copy_button = QPushButton("Copy URL")
            copy_button.setMaximumWidth(80)
            copy_button.setStyleSheet(self._get_copy_button_style())
            copy_button.clicked.connect(
                lambda checked, u=remote_deck_url: self._copy_url(u)
            )

            row_layout.addStretch()
            row_layout.addWidget(copy_button)

            # Add to main layout
            self.checkboxes_layout.addWidget(row_widget)

            # Store references
            self.deck_checkboxes[remote_deck_url] = checkbox
            self.remote_decks.append(
                {
                    "url": remote_deck_url,
                    "hash_key": hash_key,
                    "deck_info": deck_info,
                    "local_deck_name": local_deck_name if deck else get_deck_local_name(remote_deck_url),
                    "remote_deck_name": remote_name,
                    "card_count": card_count if deck else 0,
                }
            )

            # Connect change signal
            checkbox.toggled.connect(
                lambda checked, u=remote_deck_url: self._on_checkbox_changed(u, checked)
            )

        # Add stretch at the end
        self.checkboxes_layout.addStretch()

        # Update information
        self._update_selection_info()

    def _copy_url(self, url):
        """Copies URL to clipboard and opens in browser"""
        copy_url_to_clipboard(url)

    def _on_checkbox_changed(self, url, checked):
        """Callback for when a checkbox is changed."""
        if checked:
            if url not in self.selected_urls:
                self.selected_urls.append(url)
        else:
            if url in self.selected_urls:
                self.selected_urls.remove(url)

        self._update_selection_info()

    def _select_all(self):
        """Selects all decks."""
        for url, checkbox in self.deck_checkboxes.items():
            checkbox.setChecked(True)

    def _select_none(self):
        """Deselects all decks."""
        for url, checkbox in self.deck_checkboxes.items():
            checkbox.setChecked(False)

    def _invert_selection(self):
        """Inverts current selection."""
        for url, checkbox in self.deck_checkboxes.items():
            checkbox.setChecked(not checkbox.isChecked())

    def _update_selection_info(self):
        """Updates selection information."""
        selected_count = len(self.selected_urls)
        total_count = len(self.deck_checkboxes)

        # Update informative text
        if selected_count == 0:
            info_text = "No deck selected"
            bg_color = self.colors['border']
        elif selected_count == total_count:
            info_text = f"⚠️ All {total_count} deck(s) selected for disconnection"
            bg_color = self.colors['accent_danger']
        else:
            info_text = f"📋 {selected_count} of {total_count} deck(s) selected"
            bg_color = self.colors['accent_warning']

        self.selection_info.setText(info_text)
        self.selection_info.setStyleSheet(f"""
            padding: 12px 16px;
            background-color: {bg_color};
            color: white;
            border-radius: 8px;
            font-weight: bold;
            font-size: 12pt;
        """)

        # Enable/disable disconnect button
        self.disconnect_button.setEnabled(selected_count > 0)

    def _disconnect_selected(self):
        """Disconnects selected decks."""
        if not self.selected_urls:
            return

        # Check if should delete local data
        delete_local_data = self.delete_local_data_checkbox.isChecked()

        # Show confirmation
        selected_count = len(self.selected_urls)

        if selected_count == 1:
            # Get deck name for confirmation
            deck_name = None
            for deck in self.remote_decks:
                if deck["url"] == self.selected_urls[0]:
                    # Use local_deck_name from new structure
                    deck_name = get_deck_local_name(deck["url"]) or deck.get(
                        "local_deck_name", "Deck"
                    )
                    break

            if delete_local_data:
                msg = (
                    f"Disconnect deck '{deck_name}' and DELETE all local data?"
                )
            else:
                msg = f"Disconnect deck '{deck_name}' from remote source?"
        else:
            if delete_local_data:
                msg = f"Disconnect {selected_count} decks and DELETE all local data?"
            else:
                msg = f"Disconnect {selected_count} decks from their remote sources?"

        if delete_local_data:
            msg += (
                "\n\n⚠️ ATTENTION: ALL LOCAL DATA WILL BE PERMANENTLY DELETED!"
            )
            msg += "\n• Local decks and subdecks"
            msg += "\n• All cards and notes"
            msg += "\n• Specific note types (if not used in other decks)"
            msg += "\n\nThis action CANNOT be undone!"
        else:
            msg += "\n\nThis action cannot be undone. Local decks will remain in Anki."

        reply = QMessageBox.question(
            self,
            "Confirm Disconnection",
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.accept()

    def get_selected_urls(self):
        """Returns selected URLs for disconnection."""
        return self.selected_urls

    def should_delete_local_data(self):
        """Returns whether to delete local data along with disconnection."""
        return self.delete_local_data_checkbox.isChecked()


def show_disconnect_dialog(parent=None):
    """
    Shows the remote deck disconnection dialog.

    Args:
        parent: Parent widget for the dialog

    Returns:
        tuple: (success, selected_urls, delete_local_data) where:
            - success: bool indicating if user confirmed
            - selected_urls: list of selected URLs
            - delete_local_data: bool indicating if should delete local data
    """
    dialog = DisconnectDialog(parent)

    if safe_exec(dialog) == DialogAccepted:
        return True, dialog.get_selected_urls(), dialog.should_delete_local_data()

    return False, [], False
