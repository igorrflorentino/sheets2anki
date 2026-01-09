"""
Modern Backup & Restore Dialog for Sheets2Anki.

This module provides a comprehensive dialog for managing backups with:
- Simple backup (configuration only)
- Complete backup (configuration + deck data)
- Restore functionality
- Auto-backup configuration
"""

import os
from datetime import datetime
from pathlib import Path

from .compat import (
    mw,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QFrame,
    QMessageBox,
    QCheckBox,
    QSpinBox,
    QLineEdit,
    QScrollArea,
    QWidget,
    QButtonGroup,
    QRadioButton,
    QProgressDialog,
    QTimer,
    safe_exec_dialog,
    Palette_Window,
    AlignCenter,
    ScrollBarAlwaysOff,
)
from .styled_messages import StyledMessageBox
from .backup_system import SimplifiedBackupManager
from .config_manager import (
    get_auto_backup_config,
    set_auto_backup_config,
    get_auto_backup_directory,
)
import threading
import time


class BackupDialog(QDialog):
    """
    Modern dialog for managing backups (create, restore, and auto-backup configuration).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Backup & Restore - Sheets2Anki")
        self.setMinimumSize(700, 750)
        self.resize(750, 800)
        
        self.backup_manager = SimplifiedBackupManager()
        
        # Detect dark mode
        palette = self.palette()
        bg_color = palette.color(Palette_Window)
        self.is_dark_mode = bg_color.lightness() < 128
        
        self._setup_colors()
        self._setup_ui()
        self._apply_styles()
        self._load_current_settings()

    def _setup_colors(self):
        """Sets up color scheme based on theme."""
        if self.is_dark_mode:
            self.colors = {
                'bg': '#1e1e1e',
                'card_bg': '#2d2d2d',
                'text': '#ffffff',
                'text_secondary': '#b0b0b0',
                'text_muted': '#808080',
                'border': '#404040',
                'accent_primary': '#2196F3',
                'accent_success': '#4CAF50',
                'accent_warning': '#FF9800',
                'accent_danger': '#e53935',
                'accent_purple': '#9C27B0',
                'button_bg': '#3d3d3d',
                'button_hover': '#4a4a4a',
                'input_bg': '#383838',
            }
        else:
            self.colors = {
                'bg': '#f5f5f5',
                'card_bg': '#ffffff',
                'text': '#1a1a1a',
                'text_secondary': '#666666',
                'text_muted': '#999999',
                'border': '#d0d0d0',
                'accent_primary': '#1976D2',
                'accent_success': '#4CAF50',
                'accent_warning': '#FF9800',
                'accent_danger': '#d32f2f',
                'accent_purple': '#7B1FA2',
                'button_bg': '#e0e0e0',
                'button_hover': '#d0d0d0',
                'input_bg': '#fafafa',
            }

    def _apply_styles(self):
        """Applies the main stylesheet."""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.colors['bg']};
                color: {self.colors['text']};
            }}
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollArea > QWidget > QWidget {{
                background-color: transparent;
            }}
        """)

    def _setup_ui(self):
        """Sets up the dialog interface."""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Scrollable content area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(ScrollBarAlwaysOff)
        
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header section
        layout.addWidget(self._create_header())

        # Manual Backup Section
        layout.addWidget(self._create_manual_backup_section())

        # Restore Section
        layout.addWidget(self._create_restore_section())

        # Backup Directory Section (shared by all backup features)
        layout.addWidget(self._create_backup_directory_section())

        # Auto-Backup Configuration Section
        layout.addWidget(self._create_auto_backup_section())

        # Backup Info Section
        layout.addWidget(self._create_backup_info_section())

        layout.addStretch()

        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)

        # Bottom buttons
        main_layout.addWidget(self._create_bottom_buttons())

        self.setLayout(main_layout)

    def _create_header(self):
        """Creates the header section with gradient background."""
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

        title_label = QLabel("💾 Backup & Restore")
        title_label.setStyleSheet("font-size: 20pt; font-weight: bold;")
        header_layout.addWidget(title_label)

        desc_label = QLabel(
            "Protect your data by creating backups of your Sheets2Anki configuration and decks. "
            "Enable automatic backups to run before each synchronization."
        )
        desc_label.setStyleSheet("font-size: 12pt; opacity: 0.9;")
        desc_label.setWordWrap(True)
        header_layout.addWidget(desc_label)

        return header_frame

    def _create_manual_backup_section(self):
        """Creates the manual backup section."""
        section = self._create_section_frame("📦 Manual Backup", "Create a backup of your data now")
        layout = section.layout()

        # Backup type cards
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)

        # Simple backup card
        simple_card = self._create_action_card(
            "⚙️ Simple Backup",
            "Configuration files only",
            "Backs up your addon settings, remote deck links, and student configurations. "
            "Perfect for restoring after reinstalling the addon.",
            self.colors['accent_primary'],
            self._create_simple_backup
        )
        cards_layout.addWidget(simple_card)

        # Complete backup card
        complete_card = self._create_action_card(
            "📚 Complete Backup",
            "Configuration + Deck Data",
            "Backs up everything including your Sheets2Anki deck with all cards, "
            "scheduling data, and media files.",
            self.colors['accent_success'],
            self._create_complete_backup
        )
        cards_layout.addWidget(complete_card)

        layout.addLayout(cards_layout)
        return section

    def _create_restore_section(self):
        """Creates the restore section."""
        section = self._create_section_frame("🔄 Restore Backup", "Recover from a previous backup")
        layout = section.layout()

        # Restore type cards
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)

        # Restore config only
        config_card = self._create_action_card(
            "🔧 Restore Settings",
            "Configuration only",
            "Restores addon settings and remote deck links without modifying "
            "your Anki data. Creates a safety backup first.",
            self.colors['accent_warning'],
            self._restore_config_backup
        )
        cards_layout.addWidget(config_card)

        # Full restore
        full_card = self._create_action_card(
            "📥 Full Restore",
            "Complete data restore",
            "Restores everything including deck data. This will replace "
            "your current Sheets2Anki deck. Creates a safety backup first.",
            self.colors['accent_danger'],
            self._restore_full_backup
        )
        cards_layout.addWidget(full_card)

        layout.addLayout(cards_layout)

        # Warning message
        warning_frame = QFrame()
        warning_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors['accent_warning']}15;
                border-left: 3px solid {self.colors['accent_warning']};
                border-radius: 4px;
                padding: 10px;
            }}
        """)
        warning_layout = QHBoxLayout(warning_frame)
        warning_label = QLabel(
            "⚠️ <b>Important:</b> Before any restore operation, a safety backup of your current "
            "state will be automatically created to prevent data loss."
        )
        warning_label.setStyleSheet(f"color: {self.colors['text']}; font-size: 12pt;")
        warning_label.setWordWrap(True)
        warning_layout.addWidget(warning_label)
        layout.addWidget(warning_frame)

        return section

    def _create_backup_directory_section(self):
        """Creates the backup directory configuration section."""
        section = self._create_section_frame(
            "📁 Backup Directory", 
            "Where backups are saved and searched for in Backup Status"
        )
        layout = section.layout()

        # Directory selection
        dir_frame = QFrame()
        dir_frame.setObjectName("dirFrame")
        dir_frame.setStyleSheet(f"""
            QFrame#dirFrame {{
                background-color: {self.colors['input_bg']};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        dir_layout = QVBoxLayout(dir_frame)
        dir_layout.setSpacing(8)

        dir_label = QLabel("All backups (manual, automatic, and safety) will be saved to this directory:")
        dir_label.setStyleSheet(f"font-size: 12pt; color: {self.colors['text_secondary']};")
        dir_label.setWordWrap(True)
        dir_layout.addWidget(dir_label)

        dir_input_layout = QHBoxLayout()
        dir_input_layout.setSpacing(10)

        self.dir_input = QLineEdit()
        self.dir_input.setPlaceholderText("Default: Documents/Sheets2Anki/AutoBackups")
        self.dir_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.colors['card_bg']};
                border: none;
                border-bottom: 2px solid {self.colors['border']};
                border-radius: 0px;
                padding: 10px 12px;
                font-size: 12pt;
                color: {self.colors['text']};
            }}
            QLineEdit:focus {{
                border-bottom: 2px solid {self.colors['accent_primary']};
            }}
        """)
        dir_input_layout.addWidget(self.dir_input)

        browse_btn = QPushButton("Browse...")
        browse_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['button_bg']};
                color: {self.colors['text']};
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: {self.colors['button_hover']};
            }}
        """)
        browse_btn.clicked.connect(self._browse_directory)
        dir_input_layout.addWidget(browse_btn)

        dir_layout.addLayout(dir_input_layout)
        layout.addWidget(dir_frame)

        return section

    def _create_auto_backup_section(self):
        """Creates the auto-backup configuration section."""
        section = self._create_section_frame(
            "⏰ Automatic Backup", 
            "Configure automatic backups before each sync"
        )
        layout = section.layout()

        # Enable/disable toggle
        enable_frame = QFrame()
        enable_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors['input_bg']};
                border-radius: 8px;
                padding: 5px;
            }}
        """)
        enable_layout = QHBoxLayout(enable_frame)
        enable_layout.setContentsMargins(15, 10, 15, 10)

        self.auto_backup_check = QCheckBox("Enable automatic backup before each sync")
        self.auto_backup_check.setStyleSheet(f"""
            QCheckBox {{
                font-size: 12pt;
                font-weight: bold;
                color: {self.colors['text']};
                spacing: 8px;
            }}
        """)
        self.auto_backup_check.toggled.connect(self._on_auto_backup_toggled)
        enable_layout.addWidget(self.auto_backup_check)
        enable_layout.addStretch()
        layout.addWidget(enable_frame)

        # Auto backup type selection
        type_frame = QFrame()
        type_frame.setObjectName("autoTypeFrame")
        type_frame.setStyleSheet(f"""
            QFrame#autoTypeFrame {{
                background-color: {self.colors['input_bg']};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        type_layout = QVBoxLayout(type_frame)
        type_layout.setSpacing(8)

        type_label = QLabel("Backup type:")
        type_label.setStyleSheet(f"font-size: 12pt; color: {self.colors['text_secondary']};")
        type_layout.addWidget(type_label)

        self.auto_type_group = QButtonGroup(self)
        
        type_buttons_layout = QHBoxLayout()
        type_buttons_layout.setSpacing(20)

        self.radio_simple = QRadioButton("⚙️ Simple (config only)")
        self.radio_simple.setStyleSheet(f"""
            QRadioButton {{
                font-size: 12pt;
                color: {self.colors['text']};
            }}
            QRadioButton::indicator {{
                width: 18px;
                height: 18px;
            }}
        """)
        self.auto_type_group.addButton(self.radio_simple, 0)
        type_buttons_layout.addWidget(self.radio_simple)

        self.radio_complete = QRadioButton("📚 Complete (config + deck)")
        self.radio_complete.setStyleSheet(f"""
            QRadioButton {{
                font-size: 12pt;
                color: {self.colors['text']};
            }}
            QRadioButton::indicator {{
                width: 18px;
                height: 18px;
            }}
        """)
        self.auto_type_group.addButton(self.radio_complete, 1)
        type_buttons_layout.addWidget(self.radio_complete)

        type_buttons_layout.addStretch()
        type_layout.addLayout(type_buttons_layout)

        self.auto_type_frame = type_frame
        layout.addWidget(type_frame)

        # Max files setting
        max_frame = QFrame()
        max_frame.setObjectName("maxFrame")
        max_frame.setStyleSheet(f"""
            QFrame#maxFrame {{
                background-color: {self.colors['input_bg']};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        max_layout = QHBoxLayout(max_frame)
        max_layout.setContentsMargins(15, 10, 15, 10)

        max_label = QLabel("🗂️ Keep maximum backup files:")
        max_label.setStyleSheet(f"font-size: 12pt; color: {self.colors['text']};")
        max_layout.addWidget(max_label)

        self.max_files_spin = QSpinBox()
        self.max_files_spin.setRange(1, 99)
        self.max_files_spin.setValue(50)
        self.max_files_spin.setStyleSheet(f"""
            QSpinBox {{
                background-color: {self.colors['card_bg']};
                border: none;
                border-bottom: 2px solid {self.colors['border']};
                border-radius: 0px;
                padding: 8px 12px;
                font-size: 12pt;
                color: {self.colors['text']};
                min-width: 80px;
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 20px;
                border: none;
            }}
        """)
        max_layout.addWidget(self.max_files_spin)

        max_layout.addStretch()

        self.max_frame = max_frame
        layout.addWidget(max_frame)

        return section

    def _create_backup_info_section(self):
        """Creates the backup information section."""
        section = self._create_section_frame("📊 Backup Status", "Current backup information")
        layout = section.layout()

        info_frame = QFrame()
        info_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors['input_bg']};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(8)

        self.backup_status_label = QLabel("Loading backup information...")
        self.backup_status_label.setStyleSheet(f"""
            font-size: 12pt;
            color: {self.colors['text']};
            line-height: 1.5;
        """)
        self.backup_status_label.setWordWrap(True)
        info_layout.addWidget(self.backup_status_label)

        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Status")
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['accent_primary']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: #1565C0;
            }}
        """)
        refresh_btn.clicked.connect(self._refresh_backup_status)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(refresh_btn)
        info_layout.addLayout(btn_layout)

        layout.addWidget(info_frame)

        # Load initial status
        self._refresh_backup_status()

        return section

    def _create_bottom_buttons(self):
        """Creates the bottom button bar."""
        button_frame = QFrame()
        button_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors['card_bg']};
                border-top: 1px solid {self.colors['border']};
                padding: 15px 20px;
            }}
        """)
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 0, 0, 0)

        # Save settings button
        save_btn = QPushButton("✓ Save Settings")
        save_btn.setStyleSheet(f"""
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
        save_btn.clicked.connect(self._save_settings)
        button_layout.addWidget(save_btn)

        button_layout.addStretch()

        # Close button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['button_bg']};
                color: {self.colors['text']};
                border: none;
                border-radius: 8px;
                padding: 12px 25px;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: {self.colors['button_hover']};
            }}
        """)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        return button_frame

    def _create_section_frame(self, title, subtitle):
        """Creates a styled section frame."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors['card_bg']};
                border: none;
                border-radius: 12px;
            }}
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 15, 20, 20)
        layout.setSpacing(10)

        # Section title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: 14pt;
            font-weight: bold;
            color: {self.colors['text']};
        """)
        layout.addWidget(title_label)

        # Section subtitle
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet(f"""
            font-size: 12pt;
            color: {self.colors['text_secondary']};
            margin-bottom: 5px;
        """)
        layout.addWidget(subtitle_label)

        return frame

    def _create_action_card(self, title, subtitle, description, accent_color, callback):
        """Creates a styled action card with button."""
        card = QFrame()
        card.setObjectName(f"actionCard_{title.replace(' ', '_')}")
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors['input_bg']};
                border: none;
                border-radius: 10px;
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(8)

        # Title with icon
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: 12pt;
            font-weight: bold;
            color: {self.colors['text']};
        """)
        card_layout.addWidget(title_label)

        # Subtitle
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet(f"""
            font-size: 12pt;
            font-weight: bold;
            color: {accent_color};
        """)
        card_layout.addWidget(subtitle_label)

        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet(f"""
            font-size: 12pt;
            color: {self.colors['text_muted']};
        """)
        desc_label.setWordWrap(True)
        card_layout.addWidget(desc_label)

        card_layout.addStretch()

        # Action button
        action_btn = QPushButton("Execute")
        action_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {accent_color};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 12pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(accent_color)};
            }}
        """)
        action_btn.clicked.connect(callback)
        card_layout.addWidget(action_btn)

        return card

    def _darken_color(self, hex_color):
        """Darkens a hex color by 15%."""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, int(c * 0.85)) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"

    def _load_current_settings(self):
        """Loads current auto-backup settings."""
        config = get_auto_backup_config()
        
        self.auto_backup_check.setChecked(config.get("enabled", True))
        self.dir_input.setText(config.get("directory", ""))
        self.max_files_spin.setValue(config.get("max_files", 50))
        
        # Load backup type (default to simple)
        backup_type = config.get("type", "simple")
        if backup_type == "complete":
            self.radio_complete.setChecked(True)
        else:
            self.radio_simple.setChecked(True)
        
        # Update UI state
        self._on_auto_backup_toggled(config.get("enabled", True))

    def _on_auto_backup_toggled(self, enabled):
        """Handles auto-backup checkbox toggle."""
        self.auto_type_frame.setEnabled(enabled)
        self.max_frame.setEnabled(enabled)
        
        opacity = "1.0" if enabled else "0.5"
        for frame in [self.auto_type_frame, self.max_frame]:
            frame.setStyleSheet(frame.styleSheet() + f"opacity: {opacity};")

    def _browse_directory(self):
        """Opens directory browser dialog."""
        current_dir = self.dir_input.text() or get_auto_backup_directory()
        
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Backup Directory",
            current_dir,
        )
        
        if directory:
            self.dir_input.setText(directory)

    def _get_save_filename(self, default_name):
        """Opens a file dialog to save a backup."""
        # Use backup directory by default so backups are detected
        last_dir = get_auto_backup_directory()
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Backup",
            os.path.join(last_dir, default_name),
            "Zip Files (*.zip)"
        )
        return filename

    def _get_open_filename(self):
        """Opens a file dialog to select a backup file."""
        # Use backup directory by default so users find their backups
        last_dir = get_auto_backup_directory()
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select Backup File",
            last_dir,
            "Zip Files (*.zip)"
        )
        return filename

    def _validate_backup_directory(self) -> str:
        """
        Validates the backup directory is configured and exists.
        
        Returns:
            str: Valid backup directory path, or empty string if invalid
        """
        # Get the configured directory
        backup_dir = get_auto_backup_directory()
        
        # Check if directory is configured
        if not backup_dir:
            StyledMessageBox.warning(
                self,
                "Backup Directory Not Configured",
                "Please configure a backup directory first.",
                detailed_text="Go to the 'Backup Directory' section above and set a valid directory path."
            )
            return ""
        
        # Check if directory exists
        if not os.path.isdir(backup_dir):
            StyledMessageBox.warning(
                self,
                "Backup Directory Not Found",
                f"The backup directory does not exist:\n{backup_dir}",
                detailed_text="Please configure a valid directory in the 'Backup Directory' section above, or create the directory first."
            )
            return ""
        
        return backup_dir

    def _run_with_progress(self, operation_func, title: str, message: str, timeout_seconds: int = 60):
        """
        Runs an operation with a progress dialog and timeout.
        
        Args:
            operation_func: Function to execute (should return bool for success)
            title: Title for the progress dialog
            message: Message to show during operation
            timeout_seconds: Maximum time allowed for operation (default: 60)
            
        Returns:
            tuple: (success: bool, timed_out: bool, error: str or None)
        """
        result = {"success": False, "error": None, "completed": False}
        
        def run_operation():
            try:
                result["success"] = operation_func()
            except Exception as e:
                result["error"] = str(e)
            finally:
                result["completed"] = True
        
        # Create progress dialog
        progress = QProgressDialog(message, "Cancel", 0, 0, self)
        progress.setWindowTitle(title)
        progress.setMinimumDuration(0)
        progress.setAutoClose(False)
        progress.setAutoReset(False)
        progress.setCancelButton(None)  # No cancel button for backup operations
        progress.setMinimumWidth(400)
        
        # Apply styling
        progress.setStyleSheet(f"""
            QProgressDialog {{
                background-color: {self.colors['card_bg']};
                color: {self.colors['text']};
            }}
            QLabel {{
                font-size: 12pt;
                color: {self.colors['text']};
                padding: 10px;
            }}
            QProgressBar {{
                border: none;
                border-radius: 5px;
                background-color: {self.colors['input_bg']};
                height: 20px;
            }}
            QProgressBar::chunk {{
                background-color: {self.colors['accent_primary']};
                border-radius: 5px;
            }}
        """)
        
        progress.show()
        
        # Start operation in background thread
        thread = threading.Thread(target=run_operation, daemon=True)
        thread.start()
        
        # Track time for timeout
        start_time = time.time()
        
        # Wait for completion with timeout check
        while not result["completed"]:
            # Process Qt events to keep UI responsive
            if mw and mw.app:
                mw.app.processEvents()
            
            # Check timeout
            elapsed = time.time() - start_time
            if elapsed > timeout_seconds:
                progress.close()
                return (False, True, f"Operation timed out after {timeout_seconds} seconds")
            
            # Update progress message with elapsed time
            elapsed_int = int(elapsed)
            progress.setLabelText(f"{message}\n\nElapsed: {elapsed_int}s")
            
            # Small sleep to prevent CPU spinning
            time.sleep(0.1)
        
        progress.close()
        
        if result["error"]:
            return (False, False, result["error"])
        
        return (result["success"], False, None)

    def _create_simple_backup(self):
        """Creates a simple (config only) backup in the configured backup directory."""
        # Validate backup directory
        backup_dir = self._validate_backup_directory()
        if not backup_dir:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"sheets2anki_config_backup_{timestamp}.zip"
        path = os.path.join(backup_dir, backup_filename)
        
        # Run with progress dialog
        success, timed_out, error = self._run_with_progress(
            lambda: self.backup_manager.create_config_backup(path),
            "Creating Backup",
            "Creating simple backup (configuration only)..."
        )
        
        if timed_out:
            StyledMessageBox.critical(self, "Timeout", "The backup operation timed out after 60 seconds.")
        elif error:
            StyledMessageBox.critical(self, "Backup Failed", f"Error creating backup:\n{error}")
        elif success:
            StyledMessageBox.success(
                self, 
                "Backup Created", 
                "Simple backup created successfully!", 
                detailed_text=f"Location: {path}"
            )
            self._refresh_backup_status()
        else:
            StyledMessageBox.warning(self, "Backup Failed", "The backup operation failed. Please try again.")

    def _create_complete_backup(self):
        """Creates a complete (full) backup in the configured backup directory."""
        # Validate backup directory
        backup_dir = self._validate_backup_directory()
        if not backup_dir:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"sheets2anki_full_backup_{timestamp}.zip"
        path = os.path.join(backup_dir, backup_filename)
        
        # Run with progress dialog
        success, timed_out, error = self._run_with_progress(
            lambda: self.backup_manager.create_backup(path),
            "Creating Backup",
            "Creating complete backup (configuration + deck data)...\nThis may take a moment."
        )
        
        if timed_out:
            StyledMessageBox.critical(self, "Timeout", "The backup operation timed out after 60 seconds.")
        elif error:
            StyledMessageBox.critical(self, "Backup Failed", f"Error creating backup:\n{error}")
        elif success:
            StyledMessageBox.success(
                self, 
                "Backup Created", 
                "Complete backup created successfully!", 
                detailed_text=f"Location: {path}"
            )
            self._refresh_backup_status()
        else:
            StyledMessageBox.warning(self, "Backup Failed", "The backup operation failed. Please try again.")

    def _restore_config_backup(self):
        """Restores settings only from a backup."""
        path = self._get_open_filename()
        if not path:
            return
        
        # Run with progress dialog
        success, timed_out, error = self._run_with_progress(
            lambda: self.backup_manager.restore_config_only(path),
            "Restoring Backup",
            "Restoring configuration from backup..."
        )
        
        if timed_out:
            StyledMessageBox.critical(self, "Timeout", "The restore operation timed out after 60 seconds.")
        elif error:
            StyledMessageBox.critical(self, "Restore Failed", f"Error restoring backup:\n{error}")
        elif success:
            self._refresh_backup_status()
        # Note: restore_config_only shows its own success message

    def _restore_full_backup(self):
        """Restores a full backup."""
        path = self._get_open_filename()
        if not path:
            return
        
        # Run with progress dialog
        success, timed_out, error = self._run_with_progress(
            lambda: self.backup_manager.restore_backup(path),
            "Restoring Backup",
            "Restoring full backup (configuration + deck data)...\nThis may take a moment."
        )
        
        if timed_out:
            StyledMessageBox.critical(self, "Timeout", "The restore operation timed out after 60 seconds.")
        elif error:
            StyledMessageBox.critical(self, "Restore Failed", f"Error restoring backup:\n{error}")
        elif success:
            self._refresh_backup_status()
        # Note: restore_backup shows its own success message

    def _refresh_backup_status(self):
        """Refreshes the backup status display."""
        try:
            summary = self.backup_manager.get_backup_summary()
            
            status_text = []
            
            # Total backups
            total = summary.get("total_count", 0)
            if total > 0:
                status_text.append(f"📊 <b>Total backups found:</b> {total}")
                status_text.append(f"💾 <b>Total size:</b> {summary.get('total_size_human', '0 B')}")
                
                # By type
                status_text.append("")
                status_text.append(f"• Safety backups: {summary.get('safety_count', 0)}")
                status_text.append(f"• Auto backups: {summary.get('auto_count', 0)}")
                status_text.append(f"• Manual backups: {summary.get('manual_count', 0)}")
                status_text.append(f"• Full backups (with deck): {summary.get('full_count', 0)}")
                
                # Latest backup
                latest = summary.get("latest_backup")
                if latest:
                    status_text.append("")
                    status_text.append(f"🕐 <b>Latest backup:</b>")
                    status_text.append(f"   {latest.get('filename', 'Unknown')}")
                    status_text.append(f"   Created: {latest.get('created_at', 'Unknown')[:19].replace('T', ' ')}")
            else:
                status_text.append("📭 No backups found in the backup directory.")
                status_text.append("")
                status_text.append("Create your first backup using the options above!")
            
            self.backup_status_label.setText("<br>".join(status_text))
            
        except Exception as e:
            self.backup_status_label.setText(f"❌ Error loading backup status: {str(e)}")

    def _save_settings(self):
        """Saves auto-backup settings silently and closes the dialog."""
        try:
            # Get the directory value
            directory = self.dir_input.text().strip()
            
            # Validate directory if provided
            if directory:
                if not os.path.isdir(directory):
                    # Ask user if they want to create the directory
                    if StyledMessageBox.question(
                        self,
                        "Directory Not Found",
                        f"The directory does not exist:\n{directory}",
                        detailed_text="Would you like to create it now?",
                        yes_text="Create Directory",
                        no_text="Cancel"
                    ):
                        try:
                            os.makedirs(directory, exist_ok=True)
                        except Exception as e:
                            StyledMessageBox.critical(
                                self, 
                                "Cannot Create Directory", 
                                f"Failed to create directory:\n{str(e)}"
                            )
                            return
                    else:
                        # User cancelled - don't save
                        return
            
            # Get backup type
            backup_type = "complete" if self.radio_complete.isChecked() else "simple"
            
            # Save all settings using the updated config function
            success = set_auto_backup_config(
                enabled=self.auto_backup_check.isChecked(),
                directory=directory or None,
                max_files=self.max_files_spin.value(),
                backup_type=backup_type,
            )
            
            if success:
                # Silently close the dialog on success
                self.accept()
            else:
                StyledMessageBox.warning(self, "Saving Issue", "There was an issue saving the settings.")
                
        except Exception as e:
            StyledMessageBox.critical(self, "Error Saving Settings", f"Error saving settings: {str(e)}")


def show_backup_dialog():
    """
    Shows the backup management dialog.
    """
    dialog = BackupDialog(mw)
    safe_exec_dialog(dialog)
