"""
Image Processor Configuration Dialog for Sheets2Anki

Allows users to configure the automatic image processing feature:
- Enable/disable image processing
- Configure ImgBB API key
- Configure Google Apps Script Web App URL
- Test configuration

Author: Sheets2Anki Team
"""

import os
import json
from typing import Optional

from aqt import mw
from aqt.qt import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QTextEdit, QFrame, QWidget

from .compat import Palette_Window, safe_exec_dialog, DialogAccepted
from .config_manager import get_image_processor_config, set_image_processor_config
from .styled_messages import StyledMessageBox


class ImageProcessorConfigDialog(QDialog):
    """Dialog for configuring the Image Processor feature."""
    
    def __init__(self, parent=None):
        super().__init__(parent or mw)
        self.setWindowTitle("Configure Image Processor")
        self.setMinimumSize(700, 550)
        self.resize(750, 550)
        
        # Load current configuration
        self.config = get_image_processor_config()
        
        # Detect dark mode
        palette = self.palette()
        bg_color = palette.color(Palette_Window)
        self.is_dark_mode = bg_color.lightness() < 128
        
        self._setup_colors()
        self._setup_ui()
        self._apply_styles()
    
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
                'button_bg': '#3d3d3d',
                'button_hover': '#4a4a4a',
                'list_bg': '#252525',
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
                'button_bg': '#e0e0e0',
                'button_hover': '#d0d0d0',
                'list_bg': '#fafafa',
            }
    
    def _apply_styles(self):
        """Applies styles to the dialog."""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.colors['bg']};
                color: {self.colors['text']};
            }}
            QLineEdit {{
                background-color: {self.colors['card_bg']};
                color: {self.colors['text']};
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12pt;
            }}
            QLineEdit:focus {{
                border-color: {self.colors['accent_primary']};
            }}
            QCheckBox {{
                color: {self.colors['text']};
                font-size: 12pt;
                spacing: 8px;
            }}
            QTextEdit {{
                background-color: {self.colors['list_bg']};
                color: {self.colors['text']};
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                padding: 8px;
                font-size: 12pt;
            }}
            QScrollArea {{
                border: none;
                background-color: {self.colors['bg']};
            }}
            QScrollArea > QWidget > QWidget {{
                background-color: {self.colors['bg']};
            }}
        """)
    
    def _setup_ui(self):
        """Sets up the user interface."""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area for content
        from aqt.qt import QScrollArea
        from .compat import ScrollBarAlwaysOff
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(ScrollBarAlwaysOff)
        
        # Content widget (scrollable)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header section
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_frame.setStyleSheet(f"""
            QFrame#headerFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.colors['accent_primary']}, 
                    stop:1 {self.colors['accent_success']});
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
        
        title_label = QLabel("📸 Automatic Image Processing")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        desc_label = QLabel(
            "Deploy a script once at script.google.com — it works for all your spreadsheets. "
            "Images in the 'HTML IMAGE' column are uploaded to ImgBB and converted to HTML tags."
        )
        desc_label.setStyleSheet("font-size: 12pt; opacity: 0.9;")
        desc_label.setWordWrap(True)
        header_layout.addWidget(desc_label)
        
        content_layout.addWidget(header_frame)
        
        # Enable checkbox
        self.enable_checkbox = QCheckBox("✓ Enable automatic image processing")
        self.enable_checkbox.setStyleSheet(f"""
            QCheckBox {{
                font-size: 13pt;
                font-weight: bold;
                color: {self.colors['text']};
                padding: 12px;
                background-color: {self.colors['card_bg']};
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
            }}
        """)
        self.enable_checkbox.stateChanged.connect(self._on_enable_changed)
        content_layout.addWidget(self.enable_checkbox)
        
        # Setup Guide section
        setup_section = self._create_setup_section()
        content_layout.addWidget(setup_section)
        
        # API Configuration section
        api_section = self._create_api_section()
        content_layout.addWidget(api_section)
        
        # Processing Options section
        options_section = self._create_options_section()
        content_layout.addWidget(options_section)
        
        # Test section
        test_section = self._create_test_section()
        content_layout.addWidget(test_section)
        
        content_layout.addStretch()
        
        # Set content to scroll area
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        
        # Buttons (fixed at bottom)
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(20, 10, 20, 20)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(f"""
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
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("✓ Save Configuration")
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
        save_btn.setDefault(True)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(save_btn)
        
        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)
        
        # Load settings
        self._load_settings()
    
    def _create_section_style(self):
        """Returns the common GroupBox style."""
        return f"""
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
        """
    
    def _create_setup_section(self):
        """Creates the setup guide section with copy script button."""
        from .compat import QGroupBox
        
        section = QGroupBox("📖 Setup Guide (one-time)")
        section.setStyleSheet(self._create_section_style())
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Step-by-step instructions
        steps_label = QLabel(
            "<b>Step 1:</b> Copy the script below<br>"
            "<b>Step 2:</b> Go to <a href='https://script.google.com'>script.google.com</a> → New project → Paste → Save<br>"
            "<b>Step 3:</b> Deploy → New deployment → Web app → Execute as: Me, Access: Anyone → Deploy<br>"
            "<b>Step 4:</b> Copy the Web App URL and paste it below"
        )
        steps_label.setWordWrap(True)
        steps_label.setOpenExternalLinks(True)
        steps_label.setStyleSheet(f"color: {self.colors['text']}; font-size: 11pt; line-height: 1.5;")
        layout.addWidget(steps_label)
        
        # Copy script button
        copy_btn = QPushButton("📋 Copy Script to Clipboard")
        copy_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['accent_warning']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 12pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #E68900;
            }}
        """)
        copy_btn.clicked.connect(self._copy_script_to_clipboard)
        layout.addWidget(copy_btn)
        
        section.setLayout(layout)
        return section
    
    def _create_api_section(self):
        """Creates API configuration section."""
        from .compat import QGroupBox
        
        section = QGroupBox("🔧 Configuration")
        section.setStyleSheet(self._create_section_style())
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # ImgBB API Key
        imgbb_label = QLabel("🖼️ ImgBB API Key")
        imgbb_label.setStyleSheet(f"font-weight: bold; color: {self.colors['text']}; font-size: 12pt;")
        layout.addWidget(imgbb_label)
        
        imgbb_help = QLabel("Get your free API key at: api.imgbb.com")
        imgbb_help.setStyleSheet(f"color: {self.colors['text_secondary']}; font-size: 12pt;")
        layout.addWidget(imgbb_help)
        
        imgbb_input_layout = QHBoxLayout()
        self.imgbb_input = QLineEdit()
        self.imgbb_input.setPlaceholderText("Enter your ImgBB API key...")
        self.imgbb_input.setEchoMode(QLineEdit.EchoMode.Password)
        imgbb_input_layout.addWidget(self.imgbb_input)
        
        self.imgbb_show_btn = QPushButton("👁️ Show")
        self.imgbb_show_btn.setMaximumWidth(80)
        self.imgbb_show_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['button_bg']};
                color: {self.colors['text']};
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: {self.colors['button_hover']};
            }}
        """)
        self.imgbb_show_btn.clicked.connect(self._toggle_imgbb_visibility)
        imgbb_input_layout.addWidget(self.imgbb_show_btn)
        
        layout.addLayout(imgbb_input_layout)
        
        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background-color: {self.colors['border']};")
        sep.setFixedHeight(1)
        layout.addWidget(sep)
        
        # Web App URL
        webapp_label = QLabel("🌐 Google Apps Script Web App URL")
        webapp_label.setStyleSheet(f"font-weight: bold; color: {self.colors['text']}; font-size: 12pt;")
        layout.addWidget(webapp_label)
        
        webapp_help = QLabel(
            "Go to script.google.com → New project → paste ImageProcessor.gs → Deploy as Web App. "
            "One deployment works for all your spreadsheets."
        )
        webapp_help.setWordWrap(True)
        webapp_help.setStyleSheet(f"color: {self.colors['text_secondary']}; font-size: 12pt;")
        layout.addWidget(webapp_help)
        
        self.webapp_url_input = QLineEdit()
        self.webapp_url_input.setPlaceholderText("https://script.google.com/macros/s/.../exec")
        layout.addWidget(self.webapp_url_input)
        
        section.setLayout(layout)
        return section
    
    def _create_options_section(self):
        """Creates processing options section."""
        from .compat import QGroupBox
        
        section = QGroupBox("⚙️ Processing Options")
        section.setStyleSheet(self._create_section_style())
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        self.auto_process_checkbox = QCheckBox("📤 Process images automatically during each sync")
        self.auto_process_checkbox.setToolTip(
            "When enabled, images will be uploaded and converted automatically before syncing."
        )
        layout.addWidget(self.auto_process_checkbox)
        
        # Info box
        info_label = QLabel(
            "💡 Images are never deleted from your spreadsheet — only HTML tags are added. "
            "Already-processed images are skipped automatically."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet(f"""
            background-color: rgba(33, 150, 243, 0.15);
            border: 1px solid {self.colors['accent_primary']};
            border-radius: 6px;
            padding: 10px 14px;
            font-size: 12pt;
            color: {self.colors['text']};
        """)
        layout.addWidget(info_label)
        
        section.setLayout(layout)
        return section
    
    def _create_test_section(self):
        """Creates test section."""
        from .compat import QGroupBox
        
        section = QGroupBox("📋 Status & Testing")
        section.setStyleSheet(self._create_section_style())
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Test button
        buttons_row = QHBoxLayout()
        
        test_btn = QPushButton("🧪 Test Configuration")
        test_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['accent_primary']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 12pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #1976D2;
            }}
            QPushButton:disabled {{
                background-color: {self.colors['border']};
                color: {self.colors['text_secondary']};
            }}
        """)
        test_btn.clicked.connect(self._test_configuration)
        buttons_row.addWidget(test_btn)
        
        buttons_row.addStretch()
        
        layout.addLayout(buttons_row)
        
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(100)
        self.status_text.setPlainText(
            "💡 Quick Start:\n"
            "1. Get free ImgBB API key from api.imgbb.com\n"
            "2. Go to script.google.com → New project → paste ImageProcessor.gs\n"
            "3. Deploy as Web App (Execute as: Me, Access: Anyone)\n"
            "4. Paste the Web App URL above → Test Configuration"
        )
        layout.addWidget(self.status_text)
        
        self.test_btn = test_btn
        
        section.setLayout(layout)
        return section
    
    def _load_settings(self):
        """Loads current settings into the form."""
        self.enable_checkbox.setChecked(self.config.get("enabled", False))
        self.imgbb_input.setText(self.config.get("imgbb_api_key", ""))
        self.webapp_url_input.setText(self.config.get("webapp_url", ""))
        self.auto_process_checkbox.setChecked(self.config.get("auto_process", True))
        self._on_enable_changed()
    
    def _on_enable_changed(self):
        """Handles enable/disable checkbox state change."""
        enabled = self.enable_checkbox.isChecked()
        self.imgbb_input.setEnabled(enabled)
        self.imgbb_show_btn.setEnabled(enabled)
        self.webapp_url_input.setEnabled(enabled)
        self.auto_process_checkbox.setEnabled(enabled)
        self.test_btn.setEnabled(enabled)
    
    def _copy_script_to_clipboard(self):
        """Copies the Google Apps Script content to the clipboard."""
        from aqt.qt import QApplication
        from .image_processor_script import APPS_SCRIPT_CONTENT
        
        clipboard = QApplication.clipboard()
        clipboard.setText(APPS_SCRIPT_CONTENT.strip())
        
        StyledMessageBox.success(
            self,
            "Script Copied!",
            "The Google Apps Script has been copied to your clipboard.",
            detailed_text=(
                "Now go to script.google.com → New project → "
                "paste the script → Save → Deploy as Web App."
            )
        )
    
    def _toggle_imgbb_visibility(self):
        """Toggles visibility of the ImgBB API key."""
        if self.imgbb_input.echoMode() == QLineEdit.EchoMode.Password:
            self.imgbb_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.imgbb_show_btn.setText("🙈 Hide")
        else:
            self.imgbb_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.imgbb_show_btn.setText("👁️ Show")
    
    def _test_configuration(self):
        """Tests the current configuration."""
        self.status_text.setPlainText("🧪 Testing configuration...\n")
        self.test_btn.setEnabled(False)
        mw.app.processEvents()
        
        # 1. Check ImgBB API key
        imgbb_key = self.imgbb_input.text().strip()
        if not imgbb_key:
            self.status_text.append("❌ ImgBB API key is required")
            self.test_btn.setEnabled(True)
            return
        
        self.status_text.append("Validating ImgBB API key...")
        mw.app.processEvents()
        
        try:
            import urllib.request
            import urllib.parse
            
            # Test ImgBB with a 1x1 transparent PNG
            test_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
            
            data = urllib.parse.urlencode({
                "key": imgbb_key,
                "image": test_image
            }).encode("utf-8")
            
            req = urllib.request.Request("https://api.imgbb.com/1/upload", data=data)
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode("utf-8"))
                
                if result.get("success"):
                    self.status_text.append("✓ ImgBB API key is valid")
                else:
                    error_msg = result.get("error", {}).get("message", "Unknown error")
                    self.status_text.append(f"❌ ImgBB API key test failed: {error_msg}")
                    self.test_btn.setEnabled(True)
                    return
        except Exception as e:
            self.status_text.append(f"❌ ImgBB validation failed: {str(e)[:100]}")
            self.test_btn.setEnabled(True)
            return
        
        mw.app.processEvents()
        
        # 2. Check Web App URL
        webapp_url = self.webapp_url_input.text().strip()
        if not webapp_url:
            self.status_text.append("❌ Web App URL is required")
            self.test_btn.setEnabled(True)
            return
        
        if not webapp_url.startswith("https://script.google.com/"):
            self.status_text.append("⚠️ URL doesn't look like a Google Apps Script Web App URL")
            self.status_text.append("  Expected: https://script.google.com/macros/s/.../exec")
        
        self.status_text.append("\nTesting Web App connectivity...")
        mw.app.processEvents()
        
        try:
            req = urllib.request.Request(webapp_url)
            with urllib.request.urlopen(req, timeout=15) as response:
                result = json.loads(response.read().decode("utf-8"))
                
                if result.get("success"):
                    version = result.get("version", "unknown")
                    self.status_text.append(f"✓ Web App is reachable (v{version})")
                else:
                    self.status_text.append("⚠️ Web App responded but returned unexpected data")
        except Exception as e:
            self.status_text.append(f"❌ Could not reach Web App: {str(e)[:100]}")
            self.status_text.append("Make sure the script is deployed as a Web App with 'Anyone' access")
            self.test_btn.setEnabled(True)
            return
        
        # All tests passed!
        self.status_text.append("\n" + "=" * 40)
        self.status_text.append("✅ Configuration is valid!")
        self.status_text.append("\n• ImgBB API key: Valid ✓")
        self.status_text.append("• Web App URL: Reachable ✓")
        self.status_text.append("\nYou can save and use the Image Processor.")
        
        self.test_btn.setEnabled(True)
    
    def _save_settings(self):
        """Saves the configuration."""
        enabled = self.enable_checkbox.isChecked()
        imgbb_key = self.imgbb_input.text().strip()
        webapp_url = self.webapp_url_input.text().strip()
        auto_process = self.auto_process_checkbox.isChecked()
        
        if enabled:
            if not imgbb_key:
                StyledMessageBox.warning(self, "Missing Configuration", "ImgBB API key is required when Image Processor is enabled.")
                return
            
            if not webapp_url:
                StyledMessageBox.warning(self, "Missing Configuration", "Google Apps Script Web App URL is required when Image Processor is enabled.")
                return
        
        success = set_image_processor_config(
            enabled=enabled,
            imgbb_api_key=imgbb_key,
            webapp_url=webapp_url,
            auto_process=auto_process
        )
        
        if success:
            if enabled and auto_process:
                msg = "Images will be processed automatically during sync."
            elif not enabled:
                msg = "Image Processor is now disabled."
            else:
                msg = "Image Processor enabled, but auto-process is off."
            
            StyledMessageBox.success(self, "Configuration Saved", "Image Processor configuration saved successfully!", detailed_text=msg)
            self.accept()
        else:
            StyledMessageBox.critical(self, "Save Error", "Failed to save Image Processor configuration.")


def show_image_processor_config():
    """Shows the Image Processor configuration dialog."""
    dialog = ImageProcessorConfigDialog()
    return safe_exec_dialog(dialog) == DialogAccepted
