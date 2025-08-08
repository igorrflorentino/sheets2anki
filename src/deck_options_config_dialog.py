"""
Diálogo para configurar o modo de gerenciamento de opções de deck.

Este módulo permite ao usuário escolher entre três modos:
1. Compartilhado - Todos os decks usam "Sheets2Anki - Default"
2. Individual - Cada deck tem seu próprio grupo "Sheets2Anki - [Nome]"
3. Manual - Nenhuma aplicação automática de opções
"""

from .compat import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QRadioButton, QButtonGroup, QTextEdit, QFont, Qt, QFrame,
    Frame_HLine, Frame_Sunken, AlignCenter, Font_Bold, DialogAccepted,
    MessageBox_Ok, safe_exec_dialog
)


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
        intro = QLabel("Escolha como o Sheets2Anki deve gerenciar as configurações de estudo dos seus decks:")
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
        self.button_group.buttonClicked.connect(self._update_description)
        self.ok_button.clicked.connect(self._apply_changes)
        self.cancel_button.clicked.connect(self.reject)
    
    def _update_description(self):
        """Atualiza a descrição baseada na opção selecionada."""
        descriptions = {
            0: """<b>Opções Compartilhadas</b><br><br>
• Todos os decks remotos usam o mesmo grupo de configurações: <b>"Sheets2Anki - Default"</b><br>
• Configure uma vez e todas as alterações se aplicam a todos os decks<br>
• Ideal para manter consistência nas configurações de estudo<br>
• <b>Recomendado para a maioria dos usuários</b>""",
            
            1: """<b>Opções Individuais</b><br><br>
• Cada deck remoto tem seu próprio grupo de configurações: <b>"Sheets2Anki - [Nome do Deck]"</b><br>
• Permite configurações diferentes para cada deck<br>
• Útil quando decks têm necessidades de estudo específicas<br>
• Requer configuração individual de cada deck""",
            
            2: """<b>Configuração Manual</b><br><br>
• O addon não aplica nenhuma configuração automaticamente<br>
• Você tem controle total sobre as opções de cada deck<br>
• Use as configurações padrão do Anki ou crie seus próprios grupos<br>
• <b>Para usuários avançados que preferem gerenciar manualmente</b>"""
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
                from .config_manager import set_deck_options_mode, get_meta
                set_deck_options_mode(new_mode)
                
                # Aplicar configurações imediatamente a todos os decks existentes
                applied_count = self._apply_mode_to_existing_decks(new_mode)
                
                # Feedback para o usuário
                mode_names = {
                    "shared": "Opções Compartilhadas",
                    "individual": "Opções Individuais", 
                    "manual": "Configuração Manual"
                }
                
                from .compat import QMessageBox
                
                msg = QMessageBox()
                msg.setWindowTitle("Configuração Aplicada")
                msg.setText(f"Modo alterado para: {mode_names[new_mode]}")
                
                if new_mode == "manual":
                    if applied_count > 0:
                        msg.setInformativeText(f"As opções automáticas foram removidas de {applied_count} deck(s) e seus subdecks. Você agora tem controle total sobre as configurações.")
                    else:
                        msg.setInformativeText("As opções não serão mais aplicadas automaticamente. Você tem controle total sobre as configurações.")
                elif new_mode == "individual":
                    if applied_count > 0:
                        msg.setInformativeText(f"Aplicado grupos de opções individuais a {applied_count} deck(s) e todos os seus subdecks. Cada deck remoto agora tem suas próprias configurações.")
                    else:
                        msg.setInformativeText("Cada novo deck terá seu próprio grupo de opções personalizado, incluindo todos os subdecks.")
                else:  # shared
                    if applied_count > 0:
                        msg.setInformativeText(f"Aplicado grupo compartilhado 'Sheets2Anki - Default' a {applied_count} deck(s) e todos os seus subdecks. Todos os decks agora compartilham as mesmas configurações.")
                    else:
                        msg.setInformativeText("Todos os decks e subdecks usarão o grupo compartilhado 'Sheets2Anki - Default'.")
                
                msg.setStandardButtons(MessageBox_Ok)
                safe_exec_dialog(msg)
                
                self.accept()
                
            except Exception as e:
                from .compat import QMessageBox
                QMessageBox.critical(self, "Erro", f"Erro ao aplicar configuração:\n{str(e)}")

    def _apply_mode_to_existing_decks(self, mode):
        """
        Aplica o modo de opções aos decks existentes imediatamente.
        
        Args:
            mode: O modo a ser aplicado ("shared", "individual", "manual")
            
        Returns:
            int: Número de decks aos quais as configurações foram aplicadas
        """
        try:
            from .config_manager import get_meta
            from .utils import apply_sheets2anki_options_to_deck, apply_options_to_subdecks
            
            # Obter todos os decks configurados
            meta = get_meta()
            decks = meta.get("decks", {})
            
            if not decks:
                return 0  # Nenhum deck para aplicar
            
            applied_count = 0
            
            for deck_id, deck_info in decks.items():
                remote_deck_name = deck_info.get("remote_deck_name")
                local_deck_id = deck_info.get("local_deck_id")
                local_deck_name = deck_info.get("local_deck_name")
                
                if local_deck_id and remote_deck_name and local_deck_name:
                    try:
                        # Aplicar as opções de acordo com o modo ao deck principal
                        success = apply_sheets2anki_options_to_deck(
                            deck_id=local_deck_id,
                            deck_name=remote_deck_name
                        )
                        
                        if success:
                            applied_count += 1
                            
                            # Aplicar também aos subdecks
                            apply_options_to_subdecks(
                                parent_deck_name=local_deck_name,
                                remote_deck_name=remote_deck_name if mode == "individual" else None
                            )
                            
                            print(f"✅ Opções aplicadas ao deck '{local_deck_name}' e seus subdecks")
                            
                    except Exception as e:
                        print(f"Erro ao aplicar opções ao deck '{local_deck_name}': {e}")
            
            if applied_count > 0:
                print(f"✅ Configurações aplicadas a {applied_count} deck(s) e seus subdecks no modo '{mode}'")
            
            return applied_count
            
        except Exception as e:
            print(f"Erro ao aplicar modo aos decks existentes: {e}")
            return 0


def show_deck_options_config_dialog(parent=None):
    """
    Exibe o diálogo de configuração de opções de deck.
    
    Args:
        parent: Widget pai (opcional)
        
    Returns:
        bool: True se o usuário aplicou mudanças, False se cancelou
    """
    try:
        dialog = DeckOptionsConfigDialog(parent)
        return safe_exec_dialog(dialog) == DialogAccepted
    except Exception as e:
        print(f"Erro ao exibir diálogo de configuração de opções: {e}")
        return False
