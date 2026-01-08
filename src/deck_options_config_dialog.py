"""
Dialog for configuring deck options management mode.

This module allows the user to choose between three modes:
1. Shared - All decks use "Sheets2Anki - Default Options"
2. Individual - Each deck has its own group "Sheets2Anki - [Name]"
3. Manual - No automatic application of options
"""

from .compat import AlignCenter
from .compat import DialogAccepted
from .compat import MessageBox_Ok
from .compat import Palette_Window
from .compat import QButtonGroup
from .compat import QDialog
from .compat import QFrame
from .compat import QHBoxLayout
from .compat import QLabel
from .compat import QPushButton
from .compat import QRadioButton
from .compat import QVBoxLayout
from .styled_messages import StyledMessageBox
from .compat import safe_exec_dialog


class DeckOptionsConfigDialog(QDialog):
    """
    Dialog for configuring deck options management mode.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure Deck Options Management")
        self.setMinimumSize(550, 500)
        self.resize(600, 550)

        # Get current mode
        from .config_manager import get_deck_options_mode
        self.current_mode = get_deck_options_mode()

        # Detect dark mode
        palette = self.palette()
        bg_color = palette.color(Palette_Window)
        self.is_dark_mode = bg_color.lightness() < 128

        self._setup_colors()
        self._setup_ui()
        self._apply_styles()
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
                'accent_primary': '#2196F3',
                'accent_success': '#4CAF50',
                'accent_warning': '#FF9800',
                'accent_purple': '#9C27B0',
                'button_bg': '#3d3d3d',
                'button_hover': '#4a4a4a',
            }
        else:
            self.colors = {
                'bg': '#f5f5f5',
                'card_bg': '#ffffff',
                'text': '#1a1a1a',
                'text_secondary': '#666666',
                'border': '#d0d0d0',
                'accent_primary': '#1976D2',
                'accent_success': '#4CAF50',
                'accent_warning': '#FF9800',
                'accent_purple': '#7B1FA2',
                'button_bg': '#e0e0e0',
                'button_hover': '#d0d0d0',
            }

    def _apply_styles(self):
        """Applies styles to the dialog."""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.colors['bg']};
                color: {self.colors['text']};
            }}
        """)

    def _setup_ui(self):
        """Sets up the dialog interface."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header section
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_frame.setStyleSheet(f"""
            QFrame#headerFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.colors['accent_purple']}, 
                    stop:1 {self.colors['accent_primary']});
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

        title_label = QLabel("⚙️ Deck Options Management")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        header_layout.addWidget(title_label)

        desc_label = QLabel(
            "Choose how Sheets2Anki should manage study settings for your decks."
        )
        desc_label.setStyleSheet("font-size: 12pt; opacity: 0.9;")
        desc_label.setWordWrap(True)
        header_layout.addWidget(desc_label)

        layout.addWidget(header_frame)

        # Options section
        self.button_group = QButtonGroup()

        # Option 1: Shared
        shared_card = self._create_option_card(
            "shared",
            "📦 Shared Options",
            "Recommended",
            "All remote decks use the same settings group. Configure once and all changes apply to all decks.",
            self.colors['accent_success'],
            0
        )
        layout.addWidget(shared_card)

        # Option 2: Individual
        individual_card = self._create_option_card(
            "individual",
            "🎯 Individual Options",
            "Per Deck",
            "Each remote deck has its own settings group. Useful when decks have specific study needs.",
            self.colors['accent_primary'],
            1
        )
        layout.addWidget(individual_card)

        # Option 3: Manual
        manual_card = self._create_option_card(
            "manual",
            "🔧 Manual Configuration",
            "Advanced",
            "The addon does not apply any settings automatically. Full control over each deck's options.",
            self.colors['accent_warning'],
            2
        )
        layout.addWidget(manual_card)

        layout.addStretch()

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 10, 0, 0)

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

        self.ok_button = QPushButton("✓ Apply")
        self.ok_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['accent_success']};
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
        self.ok_button.setDefault(True)

        buttons_layout.addStretch()
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.ok_button)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def _create_option_card(self, mode, title, badge, description, accent_color, button_id):
        """Creates a styled option card."""
        card = QFrame()
        card.setObjectName(f"card_{mode}")
        
        # Base card style
        card.setStyleSheet(f"""
            QFrame#card_{mode} {{
                background-color: {self.colors['card_bg']};
                border: 2px solid {self.colors['border']};
                border-radius: 10px;
                padding: 5px;
            }}
            QFrame#card_{mode}:hover {{
                border-color: {accent_color};
            }}
        """)
        
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(15, 12, 15, 12)
        card_layout.setSpacing(15)

        # Radio button
        radio = QRadioButton()
        radio.setChecked(self.current_mode == mode)
        radio.setStyleSheet(f"""
            QRadioButton::indicator {{
                width: 22px;
                height: 22px;
            }}
            QRadioButton::indicator:checked {{
                background-color: {accent_color};
                border: 2px solid {accent_color};
                border-radius: 11px;
            }}
            QRadioButton::indicator:unchecked {{
                background-color: {self.colors['card_bg']};
                border: 2px solid {self.colors['border']};
                border-radius: 11px;
            }}
        """)
        self.button_group.addButton(radio, button_id)
        card_layout.addWidget(radio)

        # Store reference based on mode
        if mode == "shared":
            self.shared_radio = radio
        elif mode == "individual":
            self.individual_radio = radio
        else:
            self.manual_radio = radio

        # Content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(4)

        # Title row with badge
        title_row = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-size: 13pt; font-weight: bold; color: {self.colors['text']};")
        title_row.addWidget(title_label)

        badge_label = QLabel(badge)
        badge_label.setStyleSheet(f"""
            background-color: {accent_color};
            color: white;
            font-size: 12pt;
            font-weight: bold;
            padding: 3px 10px;
            border-radius: 10px;
        """)
        title_row.addWidget(badge_label)
        title_row.addStretch()

        content_layout.addLayout(title_row)

        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet(f"font-size: 12pt; color: {self.colors['text_secondary']};")
        desc_label.setWordWrap(True)
        content_layout.addWidget(desc_label)

        card_layout.addLayout(content_layout, 1)

        # Make entire card clickable
        card.mousePressEvent = lambda e: radio.setChecked(True)

        return card

    def _connect_signals(self):
        """Connects interface signals."""
        self.ok_button.clicked.connect(self._apply_changes)
        self.cancel_button.clicked.connect(self.reject)

    def _apply_changes(self):
        """Applies configuration changes."""
        selected_id = self.button_group.checkedId()
        modes = ["shared", "individual", "manual"]

        if selected_id >= 0:
            new_mode = modes[selected_id]

            try:
                from .config_manager import set_deck_options_mode
                set_deck_options_mode(new_mode)

                # Apply full automatic system
                from .utils import apply_automatic_deck_options_system
                auto_result = apply_automatic_deck_options_system()

                # Feedback logic
                mode_names = {
                    "shared": "Shared Options",
                    "individual": "Individual Options",
                    "manual": "Manual Configuration",
                }

                info_text = ""
                message_type = StyledMessageBox.SUCCESS
                title = "Configuration Applied"
                main_text = f"Mode changed to: {mode_names[new_mode]}"

                if new_mode == "manual":
                    info_text = "Options will no longer be applied automatically. You have full control over deck settings."
                elif auto_result.get("success", False):
                    details = []
                    if auto_result.get("root_deck_updated", False):
                        details.append("Root deck configured with 'Sheets2Anki - Root Options'")
                    if auto_result.get("remote_decks_updated", 0) > 0:
                        deck_count = auto_result["remote_decks_updated"]
                        if new_mode == "individual":
                            details.append(f"{deck_count} decks configured with individual options")
                        else:
                            details.append(f"{deck_count} decks configured with 'Sheets2Anki - Default Options'")
                    if auto_result.get("cleaned_groups", 0) > 0:
                        details.append(f"{auto_result['cleaned_groups']} orphaned groups removed")

                    if details:
                        info_text = "Automatic system applied:\n• " + "\n• ".join(details)
                    else:
                        if new_mode == "individual":
                            info_text = "Each new deck will have its own custom options group."
                        else:
                            info_text = "All decks will use 'Sheets2Anki - Default Options' group."

                    if auto_result.get("errors"):
                        errors_text = "\n".join(auto_result["errors"])
                        info_text += f"\n\nWarnings:\n{errors_text}"
                        message_type = StyledMessageBox.WARNING
                else:
                    info_text = f"Mode changed, but there were problems applying the settings: {auto_result.get('error', 'Unknown error')}"
                    message_type = StyledMessageBox.WARNING

                # Show message
                if message_type == StyledMessageBox.SUCCESS:
                    StyledMessageBox.success(self, title, main_text, detailed_text=info_text)
                else:
                    StyledMessageBox.warning(self, title, main_text, detailed_text=info_text)

                self.accept()

            except Exception as e:
                StyledMessageBox.critical(
                    self, "Error", "Error applying configuration", detailed_text=str(e)
                )


def show_deck_options_config_dialog(parent=None):
    """
    Utility function to show deck options configuration dialog.

    Args:
        parent: Parent widget (optional)

    Returns:
        bool: True if user accepted changes, False otherwise
    """
    dialog = DeckOptionsConfigDialog(parent)
    result = safe_exec_dialog(dialog)
    return result == DialogAccepted
