"""
Diálogo para configurações de nomeação de decks.

Este módulo fornece uma interface para o usuário configurar
as preferências de nomeação de decks.
"""

from .compat import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton, 
    QLineEdit, QPushButton, QGroupBox, QFormLayout, QMessageBox,
    DialogAccepted, DialogRejected
)
from .fix_exec import safe_exec
from .config_manager import (
    get_deck_naming_mode, set_deck_naming_mode,
    get_parent_deck_name, set_parent_deck_name
)


class DeckNamingDialog(QDialog):
    """
    Diálogo para configuração de nomeação de decks.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurações de Nomeação de Decks")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        # Carregar configurações atuais
        self.current_mode = get_deck_naming_mode()
        self.current_parent = get_parent_deck_name()
        
        self._setup_ui()
        self._load_current_settings()
        self._connect_signals()
    
    def _setup_ui(self):
        """Configura a interface do usuário."""
        layout = QVBoxLayout()
        
        # Título e descrição
        title_label = QLabel("Configurações de Nomeação de Decks")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        desc_label = QLabel(
            "Configure como os decks serão nomeados quando importados do Google Sheets."
        )
        desc_label.setStyleSheet("margin-bottom: 15px;")
        layout.addWidget(desc_label)
        
        # Grupo de opções de nomeação
        naming_group = QGroupBox("Modo de Nomeação")
        naming_layout = QVBoxLayout()
        
        # Opção automática
        self.auto_radio = QRadioButton("Nomeação Automática")
        auto_desc = QLabel(
            "• O nome do deck será extraído automaticamente da planilha\n"
            "• Decks ficam organizados sob um deck pai\n"
            "• Nomes são atualizados automaticamente a cada sincronização"
        )
        auto_desc.setStyleSheet("margin-left: 20px; margin-bottom: 10px; color: #666;")
        
        naming_layout.addWidget(self.auto_radio)
        naming_layout.addWidget(auto_desc)
        
        # Opção manual
        self.manual_radio = QRadioButton("Nomeação Manual")
        manual_desc = QLabel(
            "• Você define o nome do deck manualmente\n"
            "• Nomes não são alterados automaticamente\n"
            "• Maior controle sobre a organização"
        )
        manual_desc.setStyleSheet("margin-left: 20px; margin-bottom: 10px; color: #666;")
        
        naming_layout.addWidget(self.manual_radio)
        naming_layout.addWidget(manual_desc)
        
        naming_group.setLayout(naming_layout)
        layout.addWidget(naming_group)
        
        # Configurações do deck pai (só para modo automático)
        parent_group = QGroupBox("Configurações de Hierarquia")
        parent_layout = QFormLayout()
        
        self.parent_label = QLabel("Nome do Deck Pai:")
        self.parent_edit = QLineEdit()
        self.parent_edit.setPlaceholderText("ex: Sheets2Anki")
        
        parent_layout.addRow(self.parent_label, self.parent_edit)
        
        parent_help = QLabel(
            "Decks automáticos serão criados como: \"Deck Pai::Nome do Deck\""
        )
        parent_help.setStyleSheet("color: #666; font-size: 11px;")
        parent_layout.addRow(parent_help)
        
        parent_group.setLayout(parent_layout)
        self.parent_group = parent_group
        layout.addWidget(parent_group)
        
        # Botões
        buttons_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancelar")
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.ok_button)
        buttons_layout.addWidget(self.cancel_button)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def _load_current_settings(self):
        """Carrega as configurações atuais na interface."""
        if self.current_mode == "automatic":
            self.auto_radio.setChecked(True)
        else:
            self.manual_radio.setChecked(True)
        
        self.parent_edit.setText(self.current_parent)
        self._update_parent_group_visibility()
    
    def _connect_signals(self):
        """Conecta os sinais da interface."""
        self.auto_radio.toggled.connect(self._update_parent_group_visibility)
        self.manual_radio.toggled.connect(self._update_parent_group_visibility)
        
        self.ok_button.clicked.connect(self._on_ok_clicked)
        self.cancel_button.clicked.connect(self.reject)
    
    def _update_parent_group_visibility(self):
        """Atualiza a visibilidade do grupo de configurações do deck pai."""
        is_automatic = self.auto_radio.isChecked()
        self.parent_group.setEnabled(is_automatic)
    
    def _on_ok_clicked(self):
        """Processa o clique no botão OK."""
        # Validar dados
        if not self._validate_input():
            return
        
        # Salvar configurações
        new_mode = "automatic" if self.auto_radio.isChecked() else "manual"
        new_parent = self.parent_edit.text().strip()
        
        set_deck_naming_mode(new_mode)
        set_parent_deck_name(new_parent)
        
        self.accept()
    
    def _validate_input(self):
        """Valida os dados inseridos pelo usuário."""
        if self.auto_radio.isChecked():
            parent_name = self.parent_edit.text().strip()
            if not parent_name:
                QMessageBox.warning(
                    self,
                    "Erro de Validação",
                    "Por favor, informe o nome do deck pai para o modo automático."
                )
                return False
            
            # Verificar caracteres inválidos
            invalid_chars = '<>:"/\\|?*'
            if any(char in parent_name for char in invalid_chars):
                QMessageBox.warning(
                    self,
                    "Erro de Validação",
                    f"O nome do deck pai contém caracteres inválidos: {invalid_chars}"
                )
                return False
        
        return True
    
    def get_selected_mode(self):
        """
        Retorna o modo selecionado.
        
        Returns:
            str: "automatic" ou "manual"
        """
        return "automatic" if self.auto_radio.isChecked() else "manual"
    
    def get_parent_name(self):
        """
        Retorna o nome do deck pai.
        
        Returns:
            str: Nome do deck pai
        """
        return self.parent_edit.text().strip()


def show_deck_naming_dialog(parent=None):
    """
    Mostra o diálogo de configuração de nomeação de decks.
    
    Args:
        parent: Widget pai para o diálogo
        
    Returns:
        bool: True se o usuário confirmou as alterações
    """
    dialog = DeckNamingDialog(parent)
    return safe_exec(dialog) == DialogAccepted
