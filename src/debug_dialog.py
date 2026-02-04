"""
Debug Mode Dialog for Sheets2Anki.

This module provides a dialog for managing the debug mode,
viewing debug logs, and clearing them.
"""

import os
from datetime import datetime

from .compat import (
    mw,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QCheckBox,
    QGroupBox,
    safe_exec_dialog,
    Palette_Window,
)
from .utils import (
    get_debug_log_path,
    is_debug_enabled,
    clear_debug_log,
    add_debug_message,
)
from .config_manager import (
    get_meta,
    save_meta,
    should_accumulate_logs,
    set_accumulate_logs,
)
from .styled_messages import StyledMessageBox




class DebugModeDialog(QDialog):
    """
    Dialog for managing debug mode and viewing logs.
    
    Features:
    - Toggle debug mode on/off
    - View the debug log file contents
    - Clear the debug log file
    - Auto-refresh log view
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Debug Mode - Sheets2Anki")
        self.setMinimumSize(800, 600)
        self.resize(900, 650)
        
        # Detect dark mode
        palette = self.palette()
        bg_color = palette.color(Palette_Window)
        self.is_dark_mode = bg_color.lightness() < 128
        
        self._setup_ui()
        self._apply_styles()
        self._load_debug_status()
        self._load_log_content()

    def _setup_ui(self):
        """Sets up the user interface."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel("🔧 Debug Mode Configuration")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # Debug mode toggle section
        toggle_group = QGroupBox("Debug Mode Status")
        toggle_layout = QVBoxLayout()
        
        # Status and checkbox row
        status_row = QHBoxLayout()
        
        self.debug_checkbox = QCheckBox("Enable Debug Mode")
        self.debug_checkbox.setStyleSheet("font-size: 12pt; padding: 8px;")
        self.debug_checkbox.toggled.connect(self._on_debug_toggled)
        status_row.addWidget(self.debug_checkbox)
        
        status_row.addStretch()
        
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("font-size: 12pt; padding: 5px;")
        status_row.addWidget(self.status_label)
        
        toggle_layout.addLayout(status_row)
        
        # Accumulate logs checkbox
        self.accumulate_checkbox = QCheckBox("Accumulate logs over time (do not clear at each sync)")
        self.accumulate_checkbox.setStyleSheet("font-size: 11pt; padding: 5px;")
        self.accumulate_checkbox.toggled.connect(self._on_accumulate_toggled)
        toggle_layout.addWidget(self.accumulate_checkbox)
        
        # Info text
        info_label = QLabel(
            "ℹ️ When debug mode is enabled, detailed logs are written to a file. "
            "This can help diagnose issues but may impact performance slightly."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("font-size: 12pt; color: gray; padding: 5px;")
        toggle_layout.addWidget(info_label)
        
        toggle_group.setLayout(toggle_layout)
        layout.addWidget(toggle_group)

        # Log viewer section
        log_group = QGroupBox("Debug Log")
        log_layout = QVBoxLayout()
        
        # Log file path
        self.path_label = QLabel("")
        self.path_label.setStyleSheet("font-size: 12pt; color: gray;")
        self.path_label.setWordWrap(True)
        log_layout.addWidget(self.path_label)
        
        # Log content viewer
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        log_layout.addWidget(self.log_viewer)
        
        # Log action buttons
        log_buttons = QHBoxLayout()
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self._load_log_content)
        log_buttons.addWidget(self.refresh_btn)
        
        self.scroll_bottom_btn = QPushButton("⬇️ Scroll to End")
        self.scroll_bottom_btn.clicked.connect(self._scroll_to_bottom)
        log_buttons.addWidget(self.scroll_bottom_btn)
        
        log_buttons.addStretch()
        
        self.clear_btn = QPushButton("🗑️ Clear Log")
        self.clear_btn.clicked.connect(self._clear_log)
        log_buttons.addWidget(self.clear_btn)
        
        self.open_folder_btn = QPushButton("📁 Open Log Folder")
        self.open_folder_btn.clicked.connect(self._open_log_folder)
        log_buttons.addWidget(self.open_folder_btn)
        
        log_layout.addLayout(log_buttons)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

        # Close button
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        
        self.close_btn = QPushButton("Close")
        self.close_btn.setMinimumWidth(100)
        self.close_btn.clicked.connect(self.accept)
        close_layout.addWidget(self.close_btn)
        
        layout.addLayout(close_layout)

        self.setLayout(layout)

    def _apply_styles(self):
        """Applies styles based on dark/light mode."""
        if self.is_dark_mode:
            self.setStyleSheet("""
                QDialog {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 1px solid #555555;
                    border-radius: 6px;
                    margin-top: 12px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                }
                QTextEdit {
                    background-color: #1e1e1e;
                    color: #d4d4d4;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    font-family: 'Monaco', 'Consolas', 'Courier New', monospace;
                    font-size: 12pt;
                    padding: 8px;
                }
                QPushButton {
                    background-color: #4a4a4a;
                    color: #ffffff;
                    border: 1px solid #666666;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-size: 12pt;
                }
                QPushButton:hover {
                    background-color: #5a5a5a;
                    border-color: #777777;
                }
                QPushButton:pressed {
                    background-color: #3a3a3a;
                }
                QCheckBox {
                    spacing: 8px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                }
            """)
        else:
            self.setStyleSheet("""
                QDialog {
                    background-color: #ffffff;
                    color: #000000;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 1px solid #cccccc;
                    border-radius: 6px;
                    margin-top: 12px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                }
                QTextEdit {
                    background-color: #fafafa;
                    color: #333333;
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    font-family: 'Monaco', 'Consolas', 'Courier New', monospace;
                    font-size: 12pt;
                    padding: 8px;
                }
                QPushButton {
                    background-color: #f0f0f0;
                    color: #000000;
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-size: 12pt;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                    border-color: #999999;
                }
                QPushButton:pressed {
                    background-color: #d0d0d0;
                }
                QCheckBox {
                    spacing: 8px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                }
            """)

    def _load_debug_status(self):
        """Loads the current debug mode status."""
        try:
            debug_enabled = is_debug_enabled()
            self.debug_checkbox.setChecked(debug_enabled)
            self._update_status_display(debug_enabled)
            
            accumulate_enabled = should_accumulate_logs()
            self.accumulate_checkbox.setChecked(accumulate_enabled)
        except Exception as e:
            self.status_label.setText(f"⚠️ Error loading status: {e}")

    def _update_status_display(self, enabled: bool):
        """Updates the status display."""
        if enabled:
            self.status_label.setText("✅ Debug mode is ACTIVE")
            self.status_label.setStyleSheet(
                "font-size: 12pt; padding: 5px; color: #4CAF50; font-weight: bold;"
            )
        else:
            self.status_label.setText("⭕ Debug mode is INACTIVE")
            self.status_label.setStyleSheet(
                "font-size: 12pt; padding: 5px; color: #888888;"
            )

    def _on_debug_toggled(self, checked: bool):
        """Handles debug mode toggle."""
        try:
            meta = get_meta()
            if "config" not in meta:
                meta["config"] = {}
            meta["config"]["debug"] = checked
            save_meta(meta)
            
            self._update_status_display(checked)
            
            if checked:
                # Add a message to log when debug is enabled
                add_debug_message("🔧 Debug mode ENABLED by user", "DEBUG")
            
        except Exception as e:
            StyledMessageBox.warning(
                self,
                "Error",
                f"Failed to update debug mode: {e}"
            )
            # Revert checkbox state
            self.debug_checkbox.setChecked(not checked)

    def _on_accumulate_toggled(self, checked: bool):
        """Handles accumulate logs toggle."""
        try:
            set_accumulate_logs(checked)
            if checked:
                add_debug_message("📝 Log accumulation ENABLED", "DEBUG")
            else:
                add_debug_message("📝 Log accumulation DISABLED (clear at each sync)", "DEBUG")
        except Exception as e:
            StyledMessageBox.warning(
                self,
                "Error",
                f"Failed to update log accumulation setting: {e}"
            )
            # Revert checkbox state
            self.accumulate_checkbox.setChecked(not checked)

    def _load_log_content(self):
        """Loads and displays the debug log content."""
        try:
            log_path = get_debug_log_path()
            self.path_label.setText(f"📄 Log file: {log_path}")
            
            if os.path.exists(log_path):
                with open(log_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                if content.strip():
                    self.log_viewer.setPlainText(content)
                    # Get file size info
                    file_size = os.path.getsize(log_path)
                    line_count = content.count('\n')
                    self.path_label.setText(
                        f"📄 Log file: {log_path}\n"
                        f"📊 Size: {self._format_file_size(file_size)} | Lines: {line_count}"
                    )
                else:
                    self.log_viewer.setPlainText("(Log file is empty)")
            else:
                self.log_viewer.setPlainText("(Log file does not exist yet. Enable debug mode and perform actions to generate logs.)")
                
        except Exception as e:
            self.log_viewer.setPlainText(f"Error loading log file:\n{e}")

    def _format_file_size(self, size_bytes: int) -> str:
        """Formats file size in a human-readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"

    def _scroll_to_bottom(self):
        """Scrolls the log viewer to the bottom."""
        scrollbar = self.log_viewer.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _clear_log(self):
        """Clears the debug log file after confirmation."""
        if StyledMessageBox.question(
            self,
            "Clear Debug Log",
            "Are you sure you want to clear the debug log?",
            detailed_text="This will delete all logged messages. This action cannot be undone.",
            yes_text="Clear Log",
            no_text="Cancel",
            destructive=True
        ):
            try:
                clear_debug_log()
                self._load_log_content()
                StyledMessageBox.information(
                    self,
                    "Log Cleared",
                    "The debug log has been cleared successfully."
                )
            except Exception as e:
                StyledMessageBox.warning(
                    self,
                    "Error",
                    f"Failed to clear log: {e}"
                )

    def _open_log_folder(self):
        """Opens the folder containing the log file."""
        try:
            import subprocess
            import platform
            
            log_path = get_debug_log_path()
            folder_path = os.path.dirname(log_path)
            
            if platform.system() == "Darwin":  # macOS
                subprocess.run(["open", folder_path])
            elif platform.system() == "Windows":
                subprocess.run(["explorer", folder_path])
            else:  # Linux
                subprocess.run(["xdg-open", folder_path])
                
        except Exception as e:
            StyledMessageBox.warning(
                self,
                "Error",
                f"Failed to open folder: {e}"
            )


def show_debug_mode_dialog():
    """
    Shows the debug mode configuration dialog.
    
    This is the main entry point for the debug mode feature.
    """
    dialog = DebugModeDialog(mw)
    safe_exec_dialog(dialog)
