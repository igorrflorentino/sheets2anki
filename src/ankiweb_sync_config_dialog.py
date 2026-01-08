"""
Dialog for configuring automatic synchronization with AnkiWeb.

This module allows the user to choose between two synchronization modes:
1. Disabled - No automatic synchronization
2. Sync - Execute sync after deck synchronization
"""

from .compat import AlignCenter
from .compat import DialogAccepted
from .compat import Palette_Window
from .compat import QButtonGroup
from .compat import QCheckBox
from .compat import QDialog
from .compat import QFrame
from .compat import QGroupBox
from .compat import QHBoxLayout
from .compat import QLabel
from .compat import QPushButton
from .compat import QRadioButton
from .compat import QSpinBox
from .compat import QVBoxLayout
from .compat import safe_exec_dialog
from .styled_messages import StyledMessageBox


class AnkiWebSyncConfigDialog(QDialog):
    """
    Dialog for configuring automatic synchronization with AnkiWeb.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure AnkiWeb Synchronization")
        self.setMinimumSize(550, 550)
        self.resize(600, 600)

        # Get current settings
        from .config_manager import get_ankiweb_sync_mode
        from .config_manager import get_ankiweb_sync_notifications
        from .config_manager import get_ankiweb_sync_timeout

        self.current_mode = get_ankiweb_sync_mode()
        self.current_timeout = get_ankiweb_sync_timeout()
        self.current_notifications = get_ankiweb_sync_notifications()

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
                'accent_danger': '#e53935',
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
                'accent_danger': '#d32f2f',
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
            QSpinBox {{
                background-color: {self.colors['card_bg']};
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12pt;
                color: {self.colors['text']};
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 20px;
                border: none;
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
                    stop:0 {self.colors['accent_primary']}, 
                    stop:1 #00BCD4);
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

        title_label = QLabel("☁️ AnkiWeb Synchronization")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        header_layout.addWidget(title_label)

        desc_label = QLabel(
            "Configure automatic synchronization with AnkiWeb after syncing remote decks."
        )
        desc_label.setStyleSheet("font-size: 12pt; opacity: 0.9;")
        desc_label.setWordWrap(True)
        header_layout.addWidget(desc_label)

        layout.addWidget(header_frame)

        # Mode selection section
        self.mode_group = QButtonGroup()

        # Option 1: Disabled
        disabled_card = self._create_mode_card(
            "none",
            "🚫 Disabled",
            "No automatic synchronization. Sync manually via Tools > Sync.",
            self.colors['text_secondary'],
            0
        )
        layout.addWidget(disabled_card)

        # Option 2: Sync
        sync_card = self._create_mode_card(
            "sync",
            "🔄 Sync with AnkiWeb",
            "Automatically sync with AnkiWeb after each deck synchronization. Recommended for multi-device users.",
            self.colors['accent_success'],
            1
        )
        layout.addWidget(sync_card)

        # Advanced settings
        advanced_group = QGroupBox("Advanced Settings")
        advanced_layout = QVBoxLayout()
        advanced_layout.setSpacing(12)

        # Timeout setting
        timeout_frame = QFrame()
        timeout_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors['bg']};
                border-radius: 6px;
                padding: 5px;
            }}
        """)
        timeout_layout = QHBoxLayout(timeout_frame)
        timeout_layout.setContentsMargins(10, 8, 10, 8)

        timeout_label = QLabel("⏱️ Timeout:")
        timeout_label.setStyleSheet(f"font-size: 12pt; color: {self.colors['text']};")
        timeout_layout.addWidget(timeout_label)

        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(10, 300)
        self.timeout_spin.setValue(self.current_timeout)
        self.timeout_spin.setSuffix(" seconds")
        self.timeout_spin.setMinimumWidth(120)
        timeout_layout.addWidget(self.timeout_spin)

        timeout_layout.addStretch()
        advanced_layout.addWidget(timeout_frame)

        # Notifications checkbox
        self.notifications_check = QCheckBox("🔔 Show synchronization notifications")
        self.notifications_check.setChecked(self.current_notifications)
        self.notifications_check.setStyleSheet(f"""
            QCheckBox {{
                padding: 10px;
                background-color: {self.colors['bg']};
                border-radius: 6px;
            }}
        """)
        advanced_layout.addWidget(self.notifications_check)

        advanced_group.setLayout(advanced_layout)
        layout.addWidget(advanced_group)

        layout.addStretch()

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 10, 0, 0)

        # Test connection button
        self.test_button = QPushButton("🔍 Test Connection")
        self.test_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['accent_primary']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: #1565C0;
            }}
        """)
        self.test_button.clicked.connect(self._test_connection)
        buttons_layout.addWidget(self.test_button)

        buttons_layout.addStretch()

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
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)

        self.save_button = QPushButton("✓ Save")
        self.save_button.setStyleSheet(f"""
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
        self.save_button.clicked.connect(self._save_settings)
        self.save_button.setDefault(True)
        buttons_layout.addWidget(self.save_button)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def _create_mode_card(self, mode, title, description, accent_color, button_id):
        """Creates a styled mode selection card."""
        card = QFrame()
        card.setObjectName(f"modeCard_{mode}")
        card.setStyleSheet(f"""
            QFrame#modeCard_{mode} {{
                background-color: {self.colors['card_bg']};
                border: 2px solid {self.colors['border']};
                border-radius: 10px;
                padding: 5px;
            }}
            QFrame#modeCard_{mode}:hover {{
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
        self.mode_group.addButton(radio, button_id)
        card_layout.addWidget(radio)

        # Store reference
        if mode == "none":
            self.radio_none = radio
        else:
            self.radio_sync = radio

        # Content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(4)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-size: 13pt; font-weight: bold; color: {self.colors['text']};")
        content_layout.addWidget(title_label)

        desc_label = QLabel(description)
        desc_label.setStyleSheet(f"font-size: 12pt; color: {self.colors['text_secondary']};")
        desc_label.setWordWrap(True)
        content_layout.addWidget(desc_label)

        card_layout.addLayout(content_layout, 1)

        # Make entire card clickable
        card.mousePressEvent = lambda e: radio.setChecked(True)

        return card

    def _connect_signals(self):
        """Connects control signals."""
        pass  # Signals connected inline during setup

    def _test_connection(self):
        """Tests connection with AnkiWeb."""
        try:
            from .ankiweb_sync import get_sync_status
            from .ankiweb_sync import test_ankiweb_connection

            self.test_button.setText("🔍 Testing...")
            self.test_button.setEnabled(False)

            result = test_ankiweb_connection()

            if result["success"]:
                StyledMessageBox.success(self, "Connection Successful", result['message'])
            else:
                status = get_sync_status()
                debug_info = status.get("debug_info", {})

                error_msg = f"{result['error']}\n\n"
                error_msg += "Diagnostic information:\n"
                error_msg += f"• Sync system available: {debug_info.get('has_sync_system', 'N/A')}\n"
                error_msg += f"• Sync key present: {debug_info.get('has_sync_key', 'N/A')}\n"
                error_msg += f"• Valid profile: {debug_info.get('has_profile', 'N/A')}\n"
                error_msg += f"• Profile syncKey: {debug_info.get('has_profile_synckey', 'N/A')}\n"
                error_msg += f"• Profile syncUser: {debug_info.get('has_profile_syncuser', 'N/A')}\n"

                StyledMessageBox.warning(self, "Connection Failed", "Connection test failed", detailed_text=error_msg)

        except Exception as e:
            StyledMessageBox.warning(self, "Error", f"Error testing connection: {str(e)}")
        finally:
            self.test_button.setText("🔍 Test Connection")
            self.test_button.setEnabled(True)

    def _save_settings(self):
        """Saves settings and closes dialog."""
        try:
            from .config_manager import set_ankiweb_sync_config

            mode_map = {0: "none", 1: "sync"}
            selected_mode = mode_map[self.mode_group.checkedId()]

            set_ankiweb_sync_config(
                selected_mode,
                self.timeout_spin.value(),
                self.notifications_check.isChecked(),
            )

            self.accept()

        except Exception as e:
            StyledMessageBox.warning(self, "Error", f"Error saving settings: {str(e)}")

    @staticmethod
    def show_config_dialog():
        """
        Static method to show the configuration dialog.

        Returns:
            bool: True if user saved settings, False if cancelled
        """
        dialog = AnkiWebSyncConfigDialog()
        return safe_exec_dialog(dialog) == DialogAccepted


# Convenience function for external use
def show_ankiweb_sync_config():
    """Shows the AnkiWeb synchronization configuration dialog."""
    return AnkiWebSyncConfigDialog.show_config_dialog()
