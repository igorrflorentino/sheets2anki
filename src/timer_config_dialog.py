"""
Dialog for configuring timer position on cards.

This module allows the user to choose between three timer positions:
1. Top Middle - Timer at top center of card
2. Between Sections - Timer between CONTEXT and CARD sections
3. Hidden - Timer disabled
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


class TimerConfigDialog(QDialog):
    """
    Dialog for configuring timer position on cards.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure Timer Position")
        self.setMinimumSize(500, 450)
        self.resize(550, 480)

        # Get current position
        from .config_manager import get_timer_position
        self.current_position = get_timer_position()

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
                    stop:0 {self.colors['accent_success']}, 
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

        title_label = QLabel("⏱️ Timer Position")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        header_layout.addWidget(title_label)

        desc_label = QLabel(
            "Choose where the review timer appears on your cards."
        )
        desc_label.setStyleSheet("font-size: 12pt; opacity: 0.9;")
        desc_label.setWordWrap(True)
        header_layout.addWidget(desc_label)

        layout.addWidget(header_frame)

        # Options section
        self.button_group = QButtonGroup()

        # Option 1: Top Middle
        top_middle_card = self._create_option_card(
            "top_middle",
            "📍 Top Middle",
            "Fixed",
            "Timer appears fixed at the top center of the screen, always visible.",
            self.colors['accent_primary'],
            0
        )
        layout.addWidget(top_middle_card)

        # Option 2: Between Sections
        between_sections_card = self._create_option_card(
            "between_sections",
            "📋 Between Sections",
            "Default",
            "Timer appears between CONTEXT and CARD sections, flows with content.",
            self.colors['accent_success'],
            1
        )
        layout.addWidget(between_sections_card)

        # Option 3: Hidden
        hidden_card = self._create_option_card(
            "hidden",
            "🚫 Hidden",
            "Disabled",
            "Timer is completely disabled. No timer will be shown on cards.",
            self.colors['accent_warning'],
            2
        )
        layout.addWidget(hidden_card)

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

    def _create_option_card(self, position, title, badge, description, accent_color, button_id):
        """Creates a styled option card."""
        card = QFrame()
        card.setObjectName(f"card_{position}")
        
        # Base card style
        card.setStyleSheet(f"""
            QFrame#card_{position} {{
                background-color: {self.colors['card_bg']};
                border: 2px solid {self.colors['border']};
                border-radius: 10px;
                padding: 5px;
            }}
            QFrame#card_{position}:hover {{
                border-color: {accent_color};
            }}
        """)
        
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(15, 12, 15, 12)
        card_layout.setSpacing(15)

        # Radio button
        radio = QRadioButton()
        radio.setChecked(self.current_position == position)
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

        # Store reference based on position
        if position == "top_middle":
            self.top_middle_radio = radio
        elif position == "between_sections":
            self.between_sections_radio = radio
        else:
            self.hidden_radio = radio

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
        positions = ["top_middle", "between_sections", "hidden"]

        if selected_id >= 0:
            new_position = positions[selected_id]

            try:
                from .config_manager import set_timer_position
                set_timer_position(new_position)

                # Feedback
                position_names = {
                    "top_middle": "Top Middle",
                    "between_sections": "Between Sections",
                    "hidden": "Hidden (Disabled)",
                }

                StyledMessageBox.success(
                    self,
                    "Timer Position Updated",
                    f"Timer position changed to: {position_names[new_position]}",
                    detailed_text="Run a sync (Ctrl+Shift+S) to update card templates with the new timer position."
                )

                self.accept()

            except Exception as e:
                StyledMessageBox.critical(
                    self, "Error", "Error applying configuration", detailed_text=str(e)
                )


def show_timer_config_dialog(parent=None):
    """
    Utility function to show timer configuration dialog.

    Args:
        parent: Parent widget (optional)

    Returns:
        bool: True if user accepted changes, False otherwise
    """
    dialog = TimerConfigDialog(parent)
    result = safe_exec_dialog(dialog)
    return result == DialogAccepted
