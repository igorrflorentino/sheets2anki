"""
Diálogo para desconexão de decks remotos.

Este módulo fornece uma interface para o usuário
selecionar e desconectar múltiplos decks remotos usando checkboxes.
"""

from .compat import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QListWidget, QListWidgetItem, QGroupBox, QTextEdit,
    QCheckBox, QMessageBox, DialogAccepted, mw, QScrollArea, QWidget, QApplication
)
from .fix_exec import safe_exec
from .config_manager import get_remote_decks, disconnect_deck, get_deck_local_name, get_deck_remote_name, remove_remote_deck
import webbrowser


def clean_url_for_browser(url):
    """
    Remove a terminação '&output=tsv' da URL para permitir visualização no navegador.
    
    Args:
        url (str): URL completa com terminação TSV
        
    Returns:
        str: URL limpa para visualização no navegador
    """
    if url.endswith('&output=tsv'):
        return url[:-11]  # Remove '&output=tsv'
    elif url.endswith('&single=true&output=tsv'):
        return url[:-23]  # Remove '&single=true&output=tsv'
    return url


def copy_url_to_clipboard(url):
    """
    Copia a URL limpa para o clipboard do sistema.
    
    Args:
        url (str): URL para copiar
    """
    try:
        clean_url = clean_url_for_browser(url)
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(clean_url)
            return True
        return False
    except Exception as e:
        print(f"Erro ao copiar URL: {e}")
        return False


def get_copy_button_style():
    """
    Retorna estilo do botão Copy URL que se adapta ao tema (claro/escuro) do Anki.
    
    Usa palette do sistema com ajustes para melhor contraste em dark mode.
    """
    return (
        "QPushButton { "
        "font-size: 11px; padding: 2px 6px; border-radius: 3px; "
        "background-color: palette(alternateBase); "  # Mais claro que button
        "border: 1px solid palette(text); "           # Borda mais contrastante
        "color: palette(text); "                      # Texto bem contrastante
        "} "
        "QPushButton:hover { "
        "background-color: palette(highlight); "      # Destaque no hover
        "color: palette(highlightedText); "           # Texto do highlight
        "border: 1px solid palette(highlight); "
        "} "
        "QPushButton:pressed { "
        "background-color: palette(shadow); "         # Cor pressed distinta
        "color: palette(base); "                      # Texto contrastante
        "border: 1px solid palette(shadow); "
        "}"
    )


class DisconnectDialog(QDialog):
    """
    Diálogo para desconexão de decks remotos com checkboxes.
    
    Permite seleção múltipla através de checkboxes para desconectar
    vários decks remotos ao mesmo tempo.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Desconectar Decks Remotos")
        self.setModal(True)
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)
        
        self.remote_decks = []
        self.deck_checkboxes = {}  # URL -> QCheckBox
        self.selected_urls = []
        
        self._setup_ui()
        self._load_decks()
        self._connect_signals()
    
    def _setup_ui(self):
        """Configura a interface do usuário."""
        layout = QVBoxLayout()
        
        # Título
        title_label = QLabel("Desconectar Decks Remotos")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Descrição
        desc_label = QLabel(
            "Selecione quais decks remotos deseja desconectar. "
            "Os nomes mostrados são dos arquivos TSV remotos. "
            "Use o botão 'Copy URL' para visualizar o deck no navegador. "
            "Os decks locais permanecerão no Anki, mas não serão mais sincronizados."
        )
        desc_label.setStyleSheet("margin-bottom: 15px; color: #666;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Aviso importante
        warning_label = QLabel(
            "⚠️ AVISO: Esta ação desconectará permanentemente os decks selecionados. "
            "Para reconectar, você precisará adicioná-los novamente."
        )
        warning_label.setStyleSheet(
            "margin-bottom: 15px; padding: 10px; background-color: #fff3cd; "
            "border: 1px solid #ffeaa7; border-radius: 4px; color: #856404;"
        )
        warning_label.setWordWrap(True)
        layout.addWidget(warning_label)
        
        # Seção de decks remotos
        remote_group = QGroupBox("Decks Remotos Configurados")
        remote_layout = QVBoxLayout()
        
        # Área de scroll para os checkboxes
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(250)
        
        self.checkboxes_widget = QWidget()
        self.checkboxes_layout = QVBoxLayout()
        self.checkboxes_widget.setLayout(self.checkboxes_layout)
        self.checkboxes_layout.setContentsMargins(10, 10, 10, 10)
        
        scroll_area.setWidget(self.checkboxes_widget)
        remote_layout.addWidget(scroll_area)
        
        # Botões para seleção em massa
        buttons_layout = QHBoxLayout()
        
        self.select_all_button = QPushButton("Selecionar Todos")
        self.select_all_button.setToolTip("Seleciona todos os decks para desconexão")
        
        self.select_none_button = QPushButton("Desmarcar Todos")
        self.select_none_button.setToolTip("Desmarca todos os decks")
        
        self.invert_selection_button = QPushButton("Inverter Seleção")
        self.invert_selection_button.setToolTip("Inverte a seleção atual")
        
        buttons_layout.addWidget(self.select_all_button)
        buttons_layout.addWidget(self.select_none_button)
        buttons_layout.addWidget(self.invert_selection_button)
        buttons_layout.addStretch()
        
        remote_layout.addLayout(buttons_layout)
        remote_group.setLayout(remote_layout)
        layout.addWidget(remote_group)
        
        # Informações de seleção
        self.selection_info = QLabel("")
        self.selection_info.setStyleSheet(
            "margin-top: 10px; padding: 8px; background-color: #e8f4f8; "
            "border-radius: 4px; font-weight: bold;"
        )
        layout.addWidget(self.selection_info)
        
        # Opção para deletar dados locais
        self.delete_local_data_checkbox = QCheckBox("🗑️ Deletar dados locais (decks, cards, notas e note types)")
        self.delete_local_data_checkbox.setToolTip(
            "ATENÇÃO: Esta ação é irreversível!\n\n"
            "Se marcada, todos os dados locais dos decks selecionados serão deletados:\n"
            "• Decks locais e subdecks\n"
            "• Todas as cartas e notas\n"
            "• Note types específicos (se não usados em outros decks)\n\n"
            "Use com cuidado!"
        )
        self.delete_local_data_checkbox.setStyleSheet(
            "QCheckBox {"
            "margin: 10px 0; padding: 10px; "
            "background-color: palette(alternateBase); "
            "border: 2px solid palette(mid); "
            "border-radius: 6px; "
            "color: palette(text); "
            "font-weight: bold;"
            "}"
            "QCheckBox:hover {"
            "border: 2px solid palette(highlight); "
            "background-color: palette(base);"
            "}"
            "QCheckBox::indicator {"
            "width: 18px; height: 18px;"
            "}"
        )
        layout.addWidget(self.delete_local_data_checkbox)
        
        # Botões principais
        main_buttons_layout = QHBoxLayout()
        
        self.disconnect_button = QPushButton("Desconectar Selecionados")
        self.disconnect_button.setStyleSheet(
            "font-weight: bold; padding: 10px 20px; "
            "background-color: #e74c3c; color: white; border-radius: 4px;"
        )
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setStyleSheet("padding: 10px 20px; border-radius: 4px;")
        
        main_buttons_layout.addStretch()
        main_buttons_layout.addWidget(self.disconnect_button)
        main_buttons_layout.addWidget(self.cancel_button)
        
        layout.addLayout(main_buttons_layout)
        self.setLayout(layout)
    
    def _connect_signals(self):
        """Conecta os sinais da interface."""
        # Botões de seleção em massa
        self.select_all_button.clicked.connect(self._select_all)
        self.select_none_button.clicked.connect(self._select_none)
        self.invert_selection_button.clicked.connect(self._invert_selection)
        
        # Botões principais
        self.disconnect_button.clicked.connect(self._disconnect_selected)
        self.cancel_button.clicked.connect(self.reject)
    
    def _load_decks(self):
        """Carrega os decks remotos como checkboxes."""
        # Limpar checkboxes existentes
        for checkbox in self.deck_checkboxes.values():
            checkbox.setParent(None)
        self.deck_checkboxes.clear()
        self.remote_decks.clear()
        
        # Carregar decks remotos
        remote_decks = get_remote_decks()
        
        if not remote_decks:
            # Mostrar mensagem se não há decks
            no_decks_label = QLabel("Nenhum deck remoto configurado.")
            no_decks_label.setStyleSheet("color: #666; font-style: italic; padding: 20px;")
            self.checkboxes_layout.addWidget(no_decks_label)
            return
        
        for hash_key, deck_info in remote_decks.items():
            local_deck_id = deck_info["local_deck_id"]
            deck = None
            if mw.col and hasattr(mw.col, 'decks'):
                deck = mw.col.decks.get(local_deck_id)
            
            # Obter URL e nome remoto do deck
            remote_deck_url = deck_info.get("remote_deck_url", "")
            remote_name = get_deck_remote_name(remote_deck_url) or "Deck Remoto"
            
            # Verificar se o deck existe localmente
            if deck and deck["name"].strip().lower() != "default":
                # Deck existe localmente
                local_deck_name = deck["name"]
                card_count = 0
                if mw.col and hasattr(mw.col, 'find_cards'):
                    card_count = len(mw.col.find_cards(f'deck:"{local_deck_name}"'))
                
                # Usar nome remoto com contador de cards
                checkbox_text = f"{remote_name} ({card_count} cards)"
                
                # Criar layout horizontal para checkbox + botão
                row_layout = QHBoxLayout()
                
                checkbox = QCheckBox(checkbox_text)
                checkbox.setToolTip(f"Deck remoto: {remote_name}\nDeck local: {local_deck_name}\nURL: {remote_deck_url}")
                
                # Botão Copy URL
                copy_button = QPushButton("Copy URL")
                copy_button.setMaximumWidth(80)
                copy_button.setMaximumHeight(25)
                copy_button.setToolTip("Copiar URL para visualizar no navegador")
                copy_button.setStyleSheet(get_copy_button_style())
                copy_button.clicked.connect(lambda checked, u=remote_deck_url: self._copy_url(u))
                
                row_layout.addWidget(checkbox)
                row_layout.addWidget(copy_button)
                row_layout.addStretch()
                
                # Criar widget container para o layout
                row_widget = QWidget()
                row_widget.setLayout(row_layout)
                
                # Adicionar ao layout principal
                self.checkboxes_layout.addWidget(row_widget)
                
                # Armazenar referências - usar URL como chave para compatibilidade
                self.deck_checkboxes[remote_deck_url] = checkbox
                self.remote_decks.append({
                    "url": remote_deck_url,
                    "hash_key": hash_key,
                    "deck_info": deck_info,
                    "local_deck_name": local_deck_name,
                    "remote_deck_name": remote_name,
                    "card_count": card_count
                })
                
                # Conectar sinal de mudança
                checkbox.toggled.connect(lambda checked, u=remote_deck_url: self._on_checkbox_changed(u, checked))
                
            else:
                # Deck foi deletado localmente
                local_deck_name = get_deck_local_name(remote_deck_url) or "Deck Local Deletado"
                
                # Usar nome remoto com aviso
                checkbox_text = f"🗑️ {remote_name} (deck local deletado)"
                
                # Criar layout horizontal para checkbox + botão
                row_layout = QHBoxLayout()
                
                checkbox = QCheckBox(checkbox_text)
                checkbox.setToolTip(f"Deck remoto: {remote_name}\nDeck local foi deletado: {local_deck_name}\nConfiguração ainda existe.\nURL: {remote_deck_url}")
                checkbox.setStyleSheet("color: palette(bright-text); font-style: italic; background-color: rgba(149, 165, 166, 0.2);")
                
                # Botão Copy URL
                copy_button = QPushButton("Copy URL")
                copy_button.setMaximumWidth(80)
                copy_button.setMaximumHeight(25)
                copy_button.setToolTip("Copiar URL para visualizar no navegador")
                copy_button.setStyleSheet(get_copy_button_style())
                copy_button.clicked.connect(lambda checked, u=remote_deck_url: self._copy_url(u))
                
                row_layout.addWidget(checkbox)
                row_layout.addWidget(copy_button)
                row_layout.addStretch()
                
                # Criar widget container para o layout
                row_widget = QWidget()
                row_widget.setLayout(row_layout)
                
                # Adicionar ao layout principal
                self.checkboxes_layout.addWidget(row_widget)
                
                # Armazenar referências - usar URL como chave para compatibilidade
                self.deck_checkboxes[remote_deck_url] = checkbox
                self.remote_decks.append({
                    "url": remote_deck_url,
                    "hash_key": hash_key,
                    "deck_info": deck_info,
                    "local_deck_name": local_deck_name,
                    "remote_deck_name": remote_name,
                    "card_count": 0
                })
                
                # Conectar sinal de mudança
                checkbox.toggled.connect(lambda checked, u=remote_deck_url: self._on_checkbox_changed(u, checked))
        
        # Atualizar informações
        self._update_selection_info()
    
    def _copy_url(self, url):
        """Copia URL para o clipboard e abre no navegador"""
        copy_url_to_clipboard(url)
    
    def _on_checkbox_changed(self, url, checked):
        """Callback para quando um checkbox é alterado."""
        if checked:
            if url not in self.selected_urls:
                self.selected_urls.append(url)
        else:
            if url in self.selected_urls:
                self.selected_urls.remove(url)
        
        self._update_selection_info()
    
    def _select_all(self):
        """Seleciona todos os decks."""
        for url, checkbox in self.deck_checkboxes.items():
            checkbox.setChecked(True)
    
    def _select_none(self):
        """Desmarca todos os decks."""
        for url, checkbox in self.deck_checkboxes.items():
            checkbox.setChecked(False)
    
    def _invert_selection(self):
        """Inverte a seleção atual."""
        for url, checkbox in self.deck_checkboxes.items():
            checkbox.setChecked(not checkbox.isChecked())
    
    def _update_selection_info(self):
        """Atualiza as informações de seleção."""
        selected_count = len(self.selected_urls)
        total_count = len(self.deck_checkboxes)
        
        # Atualizar texto informativo
        if selected_count == 0:
            info_text = "Nenhum deck selecionado"
            info_color = "#95a5a6"
        elif selected_count == total_count:
            info_text = f"Todos os {total_count} deck(s) selecionados para desconexão"
            info_color = "#e74c3c"
        else:
            info_text = f"{selected_count} de {total_count} deck(s) selecionados para desconexão"
            info_color = "#f39c12"
        
        self.selection_info.setText(info_text)
        self.selection_info.setStyleSheet(
            f"margin-top: 10px; padding: 8px; background-color: {info_color}; "
            f"color: white; border-radius: 4px; font-weight: bold;"
        )
        
        # Habilitar/desabilitar botão de desconexão
        self.disconnect_button.setEnabled(selected_count > 0)
    
    def _disconnect_selected(self):
        """Desconecta os decks selecionados."""
        if not self.selected_urls:
            return
        
        # Verificar se deve deletar dados locais
        delete_local_data = self.delete_local_data_checkbox.isChecked()
        
        # Mostrar confirmação
        selected_count = len(self.selected_urls)
        
        if selected_count == 1:
            # Obter nome do deck para confirmação
            deck_name = None
            for deck in self.remote_decks:
                if deck["url"] == self.selected_urls[0]:
                    # Usar local_deck_name da nova estrutura
                    deck_name = get_deck_local_name(deck["url"]) or deck.get("local_deck_name", "Deck")
                    break
            
            if delete_local_data:
                msg = f"Desconectar o deck '{deck_name}' e DELETAR todos os dados locais?"
            else:
                msg = f"Desconectar o deck '{deck_name}' da fonte remota?"
        else:
            if delete_local_data:
                msg = f"Desconectar {selected_count} decks e DELETAR todos os dados locais?"
            else:
                msg = f"Desconectar {selected_count} decks das suas fontes remotas?"
        
        if delete_local_data:
            msg += "\n\n⚠️ ATENÇÃO: TODOS OS DADOS LOCAIS SERÃO DELETADOS PERMANENTEMENTE!"
            msg += "\n• Decks locais e subdecks"
            msg += "\n• Todas as cartas e notas"  
            msg += "\n• Note types específicos (se não usados em outros decks)"
            msg += "\n\nEsta ação NÃO PODE ser desfeita!"
        else:
            msg += "\n\nEsta ação não pode ser desfeita. Os decks locais permanecerão no Anki."
        
        reply = QMessageBox.question(
            self,
            "Confirmar Desconexão",
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.accept()
    
    def get_selected_urls(self):
        """Retorna as URLs selecionadas para desconexão."""
        return self.selected_urls
    
    def should_delete_local_data(self):
        """Retorna se deve deletar os dados locais junto com a desconexão."""
        return self.delete_local_data_checkbox.isChecked()


def show_disconnect_dialog(parent=None):
    """
    Mostra o diálogo de desconexão de decks remotos.
    
    Args:
        parent: Widget pai para o diálogo
        
    Returns:
        tuple: (success, selected_urls, delete_local_data) onde:
            - success: bool indicando se o usuário confirmou
            - selected_urls: list de URLs selecionadas
            - delete_local_data: bool indicando se deve deletar dados locais
    """
    dialog = DisconnectDialog(parent)
    
    if safe_exec(dialog) == DialogAccepted:
        return True, dialog.get_selected_urls(), dialog.should_delete_local_data()
    
    return False, [], False
