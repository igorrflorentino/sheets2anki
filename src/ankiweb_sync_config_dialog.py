"""
Diálogo para configurar sincronização automática com AnkiWeb.

Este módulo permite ao usuário escolher entre dois modos de sincronização:
1. Desabilitado - Não fazer sincronização automática
2. Sincronização - Executar sync após sincronização de decks
"""

from .compat import AlignCenter
from .compat import DialogAccepted
from .compat import Frame_HLine
from .compat import Frame_Sunken
from .compat import QButtonGroup
from .compat import QCheckBox
from .compat import QDialog
from .compat import QFont
from .compat import QFrame
from .compat import QHBoxLayout
from .compat import QLabel
from .compat import QPushButton
from .compat import QRadioButton
from .compat import QSpinBox
from .compat import QTextEdit
from .compat import QVBoxLayout
from .compat import safe_exec_dialog
from .compat import showWarning


class AnkiWebSyncConfigDialog(QDialog):
    """
    Diálogo para configurar sincronização automática com AnkiWeb.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurar Sincronização AnkiWeb")
        self.setFixedSize(550, 500)

        # Obter configurações atuais
        from .config_manager import get_ankiweb_sync_mode
        from .config_manager import get_ankiweb_sync_notifications
        from .config_manager import get_ankiweb_sync_timeout

        self.current_mode = get_ankiweb_sync_mode()
        self.current_timeout = get_ankiweb_sync_timeout()
        self.current_notifications = get_ankiweb_sync_notifications()

        self._setup_ui()
        self._connect_signals()
        self._update_description()

    def _setup_ui(self):
        """Configura a interface do diálogo."""
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Título
        title = QLabel("Sincronização Automática com AnkiWeb")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(AlignCenter)
        layout.addWidget(title)

        # Descrição geral
        desc = QLabel(
            "Configure se o Sheets2Anki deve automaticamente sincronizar com AnkiWeb após sincronizar decks remotos."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Separator
        separator1 = QFrame()
        separator1.setFrameShape(Frame_HLine)
        separator1.setFrameShadow(Frame_Sunken)
        layout.addWidget(separator1)

        # Opções de modo
        mode_label = QLabel("Modo de Sincronização:")
        mode_font = QFont()
        mode_font.setBold(True)
        mode_label.setFont(mode_font)
        layout.addWidget(mode_label)

        # Grupo de botões de rádio
        self.mode_group = QButtonGroup()

        # Modo desabilitado
        self.radio_none = QRadioButton("🚫 Desabilitado")
        self.radio_none.setChecked(self.current_mode == "none")
        self.mode_group.addButton(self.radio_none, 0)
        layout.addWidget(self.radio_none)

        # Modo sincronização
        self.radio_sync = QRadioButton("🔄 Sincronizar com AnkiWeb")
        self.radio_sync.setChecked(self.current_mode == "sync")
        self.mode_group.addButton(self.radio_sync, 1)
        layout.addWidget(self.radio_sync)

        # Separator
        separator2 = QFrame()
        separator2.setFrameShape(Frame_HLine)
        separator2.setFrameShadow(Frame_Sunken)
        layout.addWidget(separator2)

        # Configurações avançadas
        advanced_label = QLabel("Configurações Avançadas:")
        advanced_label.setFont(mode_font)
        layout.addWidget(advanced_label)

        # Timeout
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("Timeout (segundos):"))

        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(10, 300)
        self.timeout_spin.setValue(self.current_timeout)
        self.timeout_spin.setSuffix("s")
        timeout_layout.addWidget(self.timeout_spin)

        timeout_layout.addStretch()
        layout.addLayout(timeout_layout)

        # Notificações
        self.notifications_check = QCheckBox("Mostrar notificações de sincronização")
        self.notifications_check.setChecked(self.current_notifications)
        layout.addWidget(self.notifications_check)

        # Separator
        separator3 = QFrame()
        separator3.setFrameShape(Frame_HLine)
        separator3.setFrameShadow(Frame_Sunken)
        layout.addWidget(separator3)

        # Área de descrição do modo selecionado
        self.description_text = QTextEdit()
        self.description_text.setReadOnly(True)
        self.description_text.setMaximumHeight(120)
        layout.addWidget(self.description_text)

        # Separator
        separator4 = QFrame()
        separator4.setFrameShape(Frame_HLine)
        separator4.setFrameShadow(Frame_Sunken)
        layout.addWidget(separator4)

        # Botões
        button_layout = QHBoxLayout()

        # Botão de teste
        self.test_button = QPushButton("🔍 Testar Conexão")
        self.test_button.clicked.connect(self._test_connection)
        button_layout.addWidget(self.test_button)

        button_layout.addStretch()

        # Botões padrão
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        self.save_button = QPushButton("Salvar")
        self.save_button.clicked.connect(self._save_settings)
        self.save_button.setDefault(True)
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _connect_signals(self):
        """Conecta sinais dos controles."""
        self.mode_group.buttonClicked.connect(self._update_description)

    def _update_description(self):
        """Atualiza a descrição baseada no modo selecionado."""
        descriptions = {
            0: """🚫 <b>Modo Desabilitado</b><br><br>
Nenhuma sincronização automática será executada. Você precisará sincronizar manualmente com AnkiWeb usando Ferramentas > Sincronizar no menu do Anki.<br><br>
<b>Recomendado para:</b> Usuários que preferem controle total sobre quando sincronizar.""",
            1: """🔄 <b>Sincronização AnkiWeb</b><br><br>
Após cada sincronização de decks remotos, o Sheets2Anki executará uma sincronização com AnkiWeb. O Anki decidirá automaticamente se deve fazer upload ou download baseado nas mudanças.<br><br>
<b>Recomendado para:</b> Usuários que usam Anki em múltiplos dispositivos.""",
        }

        selected_id = self.mode_group.checkedId()
        if selected_id >= 0:
            self.description_text.setHtml(descriptions.get(selected_id, ""))

    def _test_connection(self):
        """Testa a conexão com AnkiWeb."""
        try:
            from .ankiweb_sync import get_sync_status
            from .ankiweb_sync import test_ankiweb_connection

            self.test_button.setText("🔍 Testando...")
            self.test_button.setEnabled(False)

            result = test_ankiweb_connection()

            if result["success"]:
                from .compat import showInfo

                showInfo(f"✅ {result['message']}")
            else:
                # Obter informações de debug para diagnóstico
                status = get_sync_status()
                debug_info = status.get("debug_info", {})

                error_msg = f"❌ {result['error']}\n\n"
                error_msg += "Informações de diagnóstico:\n"
                error_msg += f"• Sistema de sync disponível: {debug_info.get('has_sync_system', 'N/A')}\n"
                error_msg += (
                    f"• Sync key presente: {debug_info.get('has_sync_key', 'N/A')}\n"
                )
                error_msg += (
                    f"• Profile válido: {debug_info.get('has_profile', 'N/A')}\n"
                )
                error_msg += f"• Profile syncKey: {debug_info.get('has_profile_synckey', 'N/A')}\n"
                error_msg += f"• Profile syncUser: {debug_info.get('has_profile_syncuser', 'N/A')}\n"

                showWarning(error_msg)

        except Exception as e:
            showWarning(f"Erro ao testar conexão: {str(e)}")
        finally:
            self.test_button.setText("🔍 Testar Conexão")
            self.test_button.setEnabled(True)

    def _save_settings(self):
        """Salva as configurações e fecha o diálogo."""
        try:
            from .config_manager import set_ankiweb_sync_mode
            from .config_manager import set_ankiweb_sync_notifications
            from .config_manager import set_ankiweb_sync_timeout

            # Determinar modo selecionado
            mode_map = {0: "none", 1: "sync"}
            selected_mode = mode_map[self.mode_group.checkedId()]

            # Salvar configurações
            set_ankiweb_sync_mode(selected_mode)
            set_ankiweb_sync_timeout(self.timeout_spin.value())
            set_ankiweb_sync_notifications(self.notifications_check.isChecked())

            # Salvar silenciosamente e fechar
            self.accept()

        except Exception as e:
            showWarning(f"Erro ao salvar configurações: {str(e)}")

    @staticmethod
    def show_config_dialog():
        """
        Método estático para mostrar o diálogo de configuração.

        Returns:
            bool: True se o usuário salvou as configurações, False se cancelou
        """
        dialog = AnkiWebSyncConfigDialog()
        return safe_exec_dialog(dialog) == DialogAccepted


# Função de conveniência para uso externo
def show_ankiweb_sync_config():
    """Mostra o diálogo de configuração de sincronização AnkiWeb."""
    return AnkiWebSyncConfigDialog.show_config_dialog()
