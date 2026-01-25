"""
Dialog for configuring AI Help feature.

This module allows the user to configure:
1. AI Service (Gemini, Claude, OpenAI)
2. API Key
3. Model selection (fetched from API)
4. Custom prompt template
"""

from .compat import AlignCenter
from .compat import AlignLeft
from .compat import DialogAccepted
from .compat import EchoModeNormal
from .compat import EchoModePassword
from .compat import MessageBox_Ok
from .compat import Palette_Window
from .compat import QButtonGroup
from .compat import QCheckBox
from .compat import QComboBox
from .compat import QDialog
from .compat import QFrame
from .compat import QHBoxLayout
from .compat import QLabel
from .compat import QLineEdit
from .compat import QPushButton
from .compat import QRadioButton
from .compat import QTextEdit
from .compat import QVBoxLayout
from .compat import QTimer
from .compat import QScrollArea
from .compat import QWidget
from .styled_messages import StyledMessageBox
from .compat import safe_exec_dialog


class AIHelpConfigDialog(QDialog):
    """
    Dialog for configuring AI Help settings.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure AI Help")
        self.setMinimumSize(550, 500)
        self.resize(650, 700)

        # Get current config
        from .config_manager import get_ai_help_config, DEFAULT_AI_HELP_PROMPT
        self.current_config = get_ai_help_config()
        self.default_prompt = DEFAULT_AI_HELP_PROMPT

        # Detect dark mode
        palette = self.palette()
        bg_color = palette.color(Palette_Window)
        self.is_dark_mode = bg_color.lightness() < 128

        self._setup_colors()
        self._setup_ui()
        self._apply_styles()
        self._connect_signals()
        self._load_current_config()

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
                'input_bg': '#3d3d3d',
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
                'input_bg': '#ffffff',
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
        # Main dialog layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {self.colors['bg']};
                border: none;
            }}
        """)

        # Create content widget for scroll area
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)

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

        title_label = QLabel("🤖 AI Help Configuration")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        header_layout.addWidget(title_label)

        desc_label = QLabel(
            "Configure AI assistance to help you understand your flashcards better."
        )
        desc_label.setStyleSheet("font-size: 12pt; opacity: 0.9;")
        desc_label.setWordWrap(True)
        header_layout.addWidget(desc_label)

        layout.addWidget(header_frame)

        # Enable checkbox
        self.enable_checkbox = QCheckBox("Enable AI Help button on cards")
        self.enable_checkbox.setStyleSheet(f"""
            QCheckBox {{
                font-size: 12pt;
                color: {self.colors['text']};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
            }}
        """)
        layout.addWidget(self.enable_checkbox)

        # Mobile support checkbox
        mobile_frame = QFrame()
        mobile_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors['card_bg']};
                border: 1px solid {self.colors['accent_warning']};
                border-radius: 8px;
                padding: 8px;
            }}
        """)
        mobile_layout = QVBoxLayout(mobile_frame)
        mobile_layout.setContentsMargins(12, 8, 12, 8)
        mobile_layout.setSpacing(4)
        
        self.mobile_checkbox = QCheckBox("📱 Enable mobile support (embed API key in cards)")
        self.mobile_checkbox.setStyleSheet(f"""
            QCheckBox {{
                font-size: 11pt;
                color: {self.colors['text']};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
            }}
        """)
        mobile_layout.addWidget(self.mobile_checkbox)
        
        mobile_warning = QLabel("⚠️ Warning: API key will be visible in card HTML. Don't share decks with this enabled.")
        mobile_warning.setStyleSheet(f"color: {self.colors['accent_warning']}; font-size: 10pt;")
        mobile_warning.setWordWrap(True)
        mobile_layout.addWidget(mobile_warning)
        
        layout.addWidget(mobile_frame)

        # Service Selection
        service_frame = self._create_section_frame("AI Service")
        service_layout = QHBoxLayout()
        service_layout.setSpacing(15)

        self.service_group = QButtonGroup()
        
        self.gemini_radio = self._create_service_radio("🔮 Gemini", "gemini", 0)
        self.claude_radio = self._create_service_radio("🧠 Claude", "claude", 1)
        self.openai_radio = self._create_service_radio("💬 OpenAI", "openai", 2)

        service_layout.addWidget(self.gemini_radio)
        service_layout.addWidget(self.claude_radio)
        service_layout.addWidget(self.openai_radio)
        service_layout.addStretch()

        service_frame.layout().addLayout(service_layout)
        layout.addWidget(service_frame)

        # API Key section
        api_key_frame = self._create_section_frame("API Key")
        api_layout = QHBoxLayout()

        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(EchoModePassword)
        self.api_key_input.setPlaceholderText("Enter your API key...")
        self.api_key_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.colors['input_bg']};
                color: {self.colors['text']};
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                padding: 10px;
                font-size: 12pt;
            }}
        """)

        self.show_key_btn = QPushButton("👁")
        self.show_key_btn.setFixedWidth(40)
        self.show_key_btn.setCheckable(True)
        self.show_key_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['button_bg']};
                color: {self.colors['text']};
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                padding: 8px;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: {self.colors['button_hover']};
            }}
            QPushButton:checked {{
                background-color: {self.colors['accent_primary']};
                color: white;
            }}
        """)

        api_layout.addWidget(self.api_key_input)
        api_layout.addWidget(self.show_key_btn)
        api_key_frame.layout().addLayout(api_layout)
        layout.addWidget(api_key_frame)

        # Model selection
        model_frame = self._create_section_frame("Model")
        model_layout = QHBoxLayout()

        self.model_combo = QComboBox()
        self.model_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {self.colors['input_bg']};
                color: {self.colors['text']};
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                padding: 10px;
                font-size: 12pt;
                min-width: 300px;
            }}
            QComboBox::drop-down {{
                border: none;
                padding-right: 10px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {self.colors['input_bg']};
                color: {self.colors['text']};
                selection-background-color: {self.colors['accent_primary']};
            }}
        """)

        self.fetch_models_btn = QPushButton("🔄 Fetch Models")
        self.fetch_models_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['accent_primary']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 15px;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: #1565C0;
            }}
            QPushButton:disabled {{
                background-color: {self.colors['button_bg']};
                color: {self.colors['text_secondary']};
            }}
        """)

        model_layout.addWidget(self.model_combo, 1)
        model_layout.addWidget(self.fetch_models_btn)
        model_frame.layout().addLayout(model_layout)

        self.model_status_label = QLabel("")
        self.model_status_label.setStyleSheet(f"color: {self.colors['text_secondary']}; font-size: 10pt;")
        model_frame.layout().addWidget(self.model_status_label)

        layout.addWidget(model_frame)

        # Custom Prompt section
        prompt_frame = self._create_section_frame("Custom Prompt")
        
        prompt_desc = QLabel("Use {card_content} as placeholder for the card content.")
        prompt_desc.setStyleSheet(f"color: {self.colors['text_secondary']}; font-size: 10pt;")
        prompt_frame.layout().addWidget(prompt_desc)

        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText("Enter your custom prompt template...")
        self.prompt_edit.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.colors['input_bg']};
                color: {self.colors['text']};
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                padding: 10px;
                font-size: 11pt;
            }}
        """)
        self.prompt_edit.setMinimumHeight(120)
        self.prompt_edit.setMaximumHeight(150)
        prompt_frame.layout().addWidget(self.prompt_edit)

        self.reset_prompt_btn = QPushButton("↻ Reset to Default")
        self.reset_prompt_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['button_bg']};
                color: {self.colors['text']};
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                padding: 8px 15px;
                font-size: 11pt;
            }}
            QPushButton:hover {{
                background-color: {self.colors['button_hover']};
            }}
        """)
        prompt_frame.layout().addWidget(self.reset_prompt_btn, alignment=AlignLeft)

        layout.addWidget(prompt_frame)

        # Set content widget to scroll area
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        # Buttons (outside scroll area, fixed at bottom)
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(10, 10, 10, 0)

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

        self.ok_button = QPushButton("✓ Save")
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

        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)

    def _create_section_frame(self, title):
        """Creates a styled section frame with title."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors['card_bg']};
                border: 1px solid {self.colors['border']};
                border-radius: 10px;
                padding: 10px;
            }}
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(10)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-size: 13pt; font-weight: bold; color: {self.colors['text']};")
        layout.addWidget(title_label)
        
        return frame

    def _create_service_radio(self, text, service_id, button_id):
        """Creates a styled service radio button."""
        radio = QRadioButton(text)
        radio.setProperty("service_id", service_id)
        radio.setStyleSheet(f"""
            QRadioButton {{
                font-size: 12pt;
                color: {self.colors['text']};
                spacing: 8px;
            }}
            QRadioButton::indicator {{
                width: 18px;
                height: 18px;
            }}
        """)
        self.service_group.addButton(radio, button_id)
        return radio

    def _connect_signals(self):
        """Connects interface signals."""
        self.ok_button.clicked.connect(self._apply_changes)
        self.cancel_button.clicked.connect(self.reject)
        self.show_key_btn.clicked.connect(self._toggle_key_visibility)
        self.fetch_models_btn.clicked.connect(self._fetch_models)
        self.reset_prompt_btn.clicked.connect(self._reset_prompt)
        self.service_group.buttonClicked.connect(self._on_service_changed)

    def _load_current_config(self):
        """Loads current configuration into the UI."""
        self.enable_checkbox.setChecked(self.current_config.get("enabled", False))
        
        # Set service
        service = self.current_config.get("service", "gemini")
        if service == "gemini":
            self.gemini_radio.setChecked(True)
        elif service == "claude":
            self.claude_radio.setChecked(True)
        elif service == "openai":
            self.openai_radio.setChecked(True)
        
        # Set API key
        self.api_key_input.setText(self.current_config.get("api_key", ""))
        
        # Set model (add to combo if not empty)
        model = self.current_config.get("model", "")
        if model:
            self.model_combo.addItem(model, model)
            self.model_combo.setCurrentText(model)
        
        # Set prompt
        prompt = self.current_config.get("prompt", self.default_prompt)
        self.prompt_edit.setPlainText(prompt)
        
        # Set mobile enabled
        self.mobile_checkbox.setChecked(self.current_config.get("mobile_enabled", False))

    def _toggle_key_visibility(self):
        """Toggles API key visibility."""
        if self.show_key_btn.isChecked():
            self.api_key_input.setEchoMode(EchoModeNormal)
        else:
            self.api_key_input.setEchoMode(EchoModePassword)

    def _get_selected_service(self):
        """Gets the currently selected service."""
        if self.gemini_radio.isChecked():
            return "gemini"
        elif self.claude_radio.isChecked():
            return "claude"
        elif self.openai_radio.isChecked():
            return "openai"
        return "gemini"

    def _on_service_changed(self):
        """Called when service selection changes."""
        # Clear models when service changes
        self.model_combo.clear()
        self.model_status_label.setText("Click 'Fetch Models' to load available models.")

    def _fetch_models(self):
        """Fetches available models from the selected service."""
        api_key = self.api_key_input.text().strip()
        if not api_key:
            StyledMessageBox.warning(
                self,
                "API Key Required",
                "Please enter your API key first.",
            )
            return

        service = self._get_selected_service()
        
        self.fetch_models_btn.setEnabled(False)
        self.fetch_models_btn.setText("Loading...")
        self.model_status_label.setText("Fetching models...")

        # Use QTimer to allow UI to update before blocking call
        QTimer.singleShot(100, lambda: self._do_fetch_models(service, api_key))

    def _do_fetch_models(self, service, api_key):
        """Actually fetches the models (called after UI update)."""
        try:
            from .ai_service import get_available_models
            
            models = get_available_models(service, api_key)
            
            self.model_combo.clear()
            for model in models:
                self.model_combo.addItem(model["name"], model["id"])
            
            self.model_status_label.setText(f"✓ Found {len(models)} models")
            
            # Try to select previously configured model
            prev_model = self.current_config.get("model", "")
            if prev_model:
                index = self.model_combo.findData(prev_model)
                if index >= 0:
                    self.model_combo.setCurrentIndex(index)

        except Exception as e:
            self.model_status_label.setText(f"✗ Error: {str(e)[:50]}")
            StyledMessageBox.critical(
                self,
                "Failed to Fetch Models",
                "Could not fetch models from the API.",
                detailed_text=str(e)
            )
        finally:
            self.fetch_models_btn.setEnabled(True)
            self.fetch_models_btn.setText("🔄 Fetch Models")

    def _reset_prompt(self):
        """Resets prompt to default."""
        self.prompt_edit.setPlainText(self.default_prompt)

    def _apply_changes(self):
        """Applies configuration changes."""
        try:
            from .config_manager import set_ai_help_config

            enabled = self.enable_checkbox.isChecked()
            service = self._get_selected_service()
            api_key = self.api_key_input.text().strip()
            model = self.model_combo.currentData() or self.model_combo.currentText()
            prompt = self.prompt_edit.toPlainText().strip()
            mobile_enabled = self.mobile_checkbox.isChecked()

            # Validate if enabled
            if enabled:
                if not api_key:
                    StyledMessageBox.warning(
                        self,
                        "API Key Required",
                        "Please enter an API key to enable AI Help.",
                    )
                    return
                if not model:
                    StyledMessageBox.warning(
                        self,
                        "Model Required",
                        "Please select a model (click 'Fetch Models' first).",
                    )
                    return

            set_ai_help_config(
                enabled=enabled,
                service=service,
                model=model,
                api_key=api_key,
                prompt=prompt if prompt else None,
                mobile_enabled=mobile_enabled
            )

            status = "enabled" if enabled else "disabled"
            StyledMessageBox.success(
                self,
                "AI Help Configuration Saved",
                f"AI Help is now {status}.",
                detailed_text="Run a sync (Ctrl+Shift+S) to update card templates with the AI Help button." if enabled else None
            )

            self.accept()

        except Exception as e:
            StyledMessageBox.critical(
                self, "Error", "Error saving configuration", detailed_text=str(e)
            )


def show_ai_help_config_dialog(parent=None):
    """
    Utility function to show AI Help configuration dialog.

    Args:
        parent: Parent widget (optional)

    Returns:
        bool: True if user accepted changes, False otherwise
    """
    dialog = AIHelpConfigDialog(parent)
    result = safe_exec_dialog(dialog)
    return result == DialogAccepted
