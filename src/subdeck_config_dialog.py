"""
Diálogo de configuração de subdecks para o addon Sheets2Anki.

Este módulo implementa um diálogo para configurar a criação
automática de subdecks baseados em TOPICO e SUBTOPICO.
"""

from .compat import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QPushButton, QDialogButtonBox, TextFormat_RichText,
    ButtonBox_Ok, ButtonBox_Cancel, DialogAccepted,
    safe_exec_dialog
)
from .config_manager import get_create_subdecks_setting, set_create_subdecks_setting
from .constants import DEFAULT_TOPIC, DEFAULT_SUBTOPIC, DEFAULT_CONCEPT

class SubdeckConfigDialog(QDialog):
    """
    Diálogo para configurar a criação automática de subdecks.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuração de Subdecks")
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface do diálogo."""
        layout = QVBoxLayout()
        
        # Título e descrição
        title_label = QLabel("<h3>Configuração de Subdecks</h3>")
        desc_label = QLabel(
            "Configure como os cards serão organizados em subdecks "
            "com base nos valores das colunas TOPICO e SUBTOPICO."
        )
        desc_label.setWordWrap(True)
        
        # Checkbox para habilitar/desabilitar subdecks
        self.enable_subdecks_cb = QCheckBox("Criar subdecks automaticamente")
        self.enable_subdecks_cb.setChecked(get_create_subdecks_setting())
        
        # Descrição da estrutura
        structure_label = QLabel(
            f"<b>Estrutura de subdecks:</b><br>"
            f"• <code>DeckPrincipal::Topico::Subtopico::Conceito</code> (sempre, usando valores padrão quando campos estão vazios)<br><br>"
            f"<b>Valores padrão:</b><br>"
            f"• Tópico vazio: <code>{DEFAULT_TOPIC}</code><br>"
            f"• Subtópico vazio: <code>{DEFAULT_SUBTOPIC}</code><br>"
            f"• Conceito vazio: <code>{DEFAULT_CONCEPT}</code>"
        )
        structure_label.setTextFormat(TextFormat_RichText)
        structure_label.setWordWrap(True)
        
        # Botões
        button_box = QDialogButtonBox(ButtonBox_Ok | ButtonBox_Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # Adicionar widgets ao layout
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addSpacing(10)
        layout.addWidget(self.enable_subdecks_cb)
        layout.addSpacing(10)
        layout.addWidget(structure_label)
        layout.addSpacing(20)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        self.resize(400, 300)
        
    def accept(self):
        """Salva as configurações quando o usuário clica em OK."""
        enabled = self.enable_subdecks_cb.isChecked()
        set_create_subdecks_setting(enabled)
        super().accept()

def show_subdeck_config_dialog(parent=None):
    """
    Mostra o diálogo de configuração de subdecks.
    
    Args:
        parent: Widget pai para o diálogo
        
    Returns:
        bool: True se o usuário aceitou as alterações, False caso contrário
    """
    dialog = SubdeckConfigDialog(parent)
    result = safe_exec_dialog(dialog)
    return result == DialogAccepted