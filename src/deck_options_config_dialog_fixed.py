"""
Diálogo para configurar o modo de gerenciamento de opções de deck.

Este módulo permite ao usuário escolher entre três modos:
1. Compartilhado - Todos os decks usam "Sheets2Anki - Default Options"
2. Individual - Cada deck tem seu próprio grupo "Sheets2Anki - [Nome]"
3. Manual - Nenhuma aplicação automática de opções
"""

from .compat import AlignCenter
from .compat import DialogAccepted
from .compat import Font_Bold
from .compat import Frame_HLine
from .compat import Frame_Sunken
from .compat import MessageBox_Ok
from .compat import QButtonGroup
from .compat import QDialog
from .compat import QFont
from .compat import QFrame
from .compat import QHBoxLayout
from .compat import QLabel
from .compat import QPushButton
from .compat import QRadioButton
from .compat import QTextEdit
from .compat import QVBoxLayout
from .compat import safe_exec_dialog


class DeckOptionsConfigDialog(QDialog):
    """
    Diálogo para configurar o modo de gerenciamento de opções de deck.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurar Gerenciamento de Opções de Deck")
        self.setFixedSize(500, 450)

        # Obter modo atual
        from .config_manager import get_deck_options_mode

        self.current_mode = get_deck_options_mode()

        self._setup_ui()
        self._connect_signals()
        self._update_description()

    def _setup_ui(self):
        """Configura a interface do diálogo."""
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Título
        title = QLabel("Gerenciamento de Opções de Deck")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(AlignCenter)
        layout.addWidget(title)

        # Descrição geral
        intro = QLabel(
            "Escolha como o Sheets2Anki deve gerenciar as configurações de estudo dos seus decks:"
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        # Grupo de botões de opção
        self.button_group = QButtonGroup()

        # Opção 1: Compartilhado
        self.shared_radio = QRadioButton("Opções Compartilhadas (Recomendado)")
        self.shared_radio.setChecked(self.current_mode == "shared")
        self.button_group.addButton(self.shared_radio, 0)
        layout.addWidget(self.shared_radio)

        # Opção 2: Individual
        self.individual_radio = QRadioButton("Opções Individuais por Deck")
        self.individual_radio.setChecked(self.current_mode == "individual")
        self.button_group.addButton(self.individual_radio, 1)
        layout.addWidget(self.individual_radio)

        # Opção 3: Manual
        self.manual_radio = QRadioButton("Configuração Manual")
        self.manual_radio.setChecked(self.current_mode == "manual")
        self.button_group.addButton(self.manual_radio, 2)
        layout.addWidget(self.manual_radio)

        # Separator
        separator = QFrame()
        separator.setFrameShape(Frame_HLine)
        separator.setFrameShadow(Frame_Sunken)
        layout.addWidget(separator)

        # Área de descrição
        desc_label = QLabel("Descrição:")
        desc_label.setFont(QFont("", 10, Font_Bold))
        layout.addWidget(desc_label)

        self.description_text = QTextEdit()
        self.description_text.setMaximumHeight(120)
        self.description_text.setReadOnly(True)
        layout.addWidget(self.description_text)

        # Botões
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self.cancel_button = QPushButton("Cancelar")
        self.ok_button = QPushButton("Aplicar")
        self.ok_button.setDefault(True)

        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.ok_button)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def _connect_signals(self):
        """Conecta os sinais da interface."""
        self.shared_radio.toggled.connect(self._update_description)
        self.individual_radio.toggled.connect(self._update_description)
        self.manual_radio.toggled.connect(self._update_description)

        self.ok_button.clicked.connect(self._apply_changes)
        self.cancel_button.clicked.connect(self.reject)

    def _update_description(self):
        """Atualiza a descrição baseada na opção selecionada."""
        descriptions = {
            0: """<b>Opções Compartilhadas</b><br><br>
• Todos os decks remotos usam o mesmo grupo de configurações: <b>"Sheets2Anki - Default Options"</b><br>
• Deck raiz usa configurações específicas: <b>"Sheets2Anki - Root Options"</b><br>
• Configure uma vez e todas as alterações se aplicam a todos os decks<br>
• Ideal para manter consistência nas configurações de estudo<br>
• <b>Recomendado para a maioria dos usuários</b>""",
            1: """<b>Opções Individuais</b><br><br>
• Cada deck remoto tem seu próprio grupo de configurações: <b>"Sheets2Anki - [Nome do Deck]"</b><br>
• Deck raiz sempre usa: <b>"Sheets2Anki - Root Options"</b><br>
• Permite configurações diferentes para cada deck<br>
• Útil quando decks têm necessidades de estudo específicas<br>
• Requer configuração individual de cada deck""",
            2: """<b>Configuração Manual</b><br><br>
• O addon não aplica nenhuma configuração automaticamente<br>
• Você tem controle total sobre as opções de cada deck<br>
• Use as configurações padrão do Anki ou crie seus próprios grupos<br>
• Sistema de limpeza automática é desativado<br>
• <b>Para usuários avançados que preferem gerenciar manualmente</b>""",
        }

        selected_id = self.button_group.checkedId()
        if selected_id >= 0:
            self.description_text.setHtml(descriptions.get(selected_id, ""))

    def _apply_changes(self):
        """Aplica as mudanças de configuração."""
        selected_id = self.button_group.checkedId()
        modes = ["shared", "individual", "manual"]

        if selected_id >= 0:
            new_mode = modes[selected_id]

            try:
                from .config_manager import set_deck_options_mode

                set_deck_options_mode(new_mode)

                # Aplicar sistema automático completo usando a nova função
                from .utils import apply_automatic_deck_options_system

                auto_result = apply_automatic_deck_options_system()

                # Feedback para o usuário
                mode_names = {
                    "shared": "Opções Compartilhadas",
                    "individual": "Opções Individuais",
                    "manual": "Configuração Manual",
                }

                from .compat import QMessageBox

                msg = QMessageBox()
                msg.setWindowTitle("Configuração Aplicada")
                msg.setText(f"Modo alterado para: {mode_names[new_mode]}")

                # Mensagem detalhada baseada no resultado
                if new_mode == "manual":
                    msg.setInformativeText(
                        "As opções não serão mais aplicadas automaticamente. Você tem controle total sobre as configurações de deck."
                    )
                elif auto_result.get("success", False):
                    details = []
                    if auto_result.get("root_deck_updated", False):
                        details.append(
                            "Deck raiz configurado com 'Sheets2Anki - Root Options'"
                        )
                    if auto_result.get("remote_decks_updated", 0) > 0:
                        deck_count = auto_result["remote_decks_updated"]
                        if new_mode == "individual":
                            details.append(
                                f"{deck_count} decks configurados com opções individuais"
                            )
                        else:
                            details.append(
                                f"{deck_count} decks configurados com 'Sheets2Anki - Default Options'"
                            )
                    if auto_result.get("cleaned_groups", 0) > 0:
                        details.append(
                            f"{auto_result['cleaned_groups']} grupos órfãos removidos"
                        )

                    if details:
                        msg.setInformativeText(
                            "Sistema automático aplicado:\n• " + "\n• ".join(details)
                        )
                    else:
                        if new_mode == "individual":
                            msg.setInformativeText(
                                "Cada novo deck terá seu próprio grupo de opções personalizado."
                            )
                        else:
                            msg.setInformativeText(
                                "Todos os decks usarão o grupo 'Sheets2Anki - Default Options'."
                            )

                    # Mostrar erros se houver
                    if auto_result.get("errors"):
                        errors_text = "\n".join(auto_result["errors"])
                        current_text = msg.informativeText()
                        msg.setInformativeText(
                            f"{current_text}\n\nAvisos:\n{errors_text}"
                        )
                else:
                    msg.setInformativeText(
                        f"Modo alterado, mas houve problemas na aplicação: {auto_result.get('error', 'Erro desconhecido')}"
                    )

                msg.setStandardButtons(MessageBox_Ok)
                safe_exec_dialog(msg)

                self.accept()

            except Exception as e:
                from .compat import QMessageBox

                QMessageBox.critical(
                    self, "Erro", f"Erro ao aplicar configuração:\n{str(e)}"
                )


def show_deck_options_config_dialog(parent=None):
    """
    Função utilitária para mostrar o diálogo de configuração de opções de deck.

    Args:
        parent: Widget pai (opcional)

    Returns:
        bool: True se o usuário aceitou as mudanças, False caso contrário
    """
    dialog = DeckOptionsConfigDialog(parent)
    result = safe_exec_dialog(dialog)
    return result == DialogAccepted
