"""
Diálogo para sincronização de decks ativos.

Este módulo fornece uma interface para o usuário
selecionar e sincronizar decks ativos do sistema.
"""

from .compat import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QListWidget, QListWidgetItem, QGroupBox, QTextEdit,
    QCheckBox, QMessageBox, DialogAccepted, mw, QScrollArea, QWidget
)
from .fix_exec import safe_exec
from .config_manager import get_active_decks, get_sync_selection, save_sync_selection


class SyncDialog(QDialog):
    """
    Diálogo para sincronização de decks ativos com checkboxes.
    
    Permite seleção múltipla através de checkboxes e mantém
    a seleção persistente entre sessões.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sincronizar Decks")
        self.setModal(True)
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)
        
        self.active_decks = []
        self.deck_checkboxes = {}  # URL -> QCheckBox
        self.sync_selection = {}   # URL -> bool
        
        self._setup_ui()
        self._load_decks()
        self._load_persistent_selection()
        self._connect_signals()
    
    def _setup_ui(self):
        """Configura a interface do usuário."""
        layout = QVBoxLayout()
        
        # Título
        title_label = QLabel("Sincronizar Decks")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Descrição
        desc_label = QLabel(
            "Selecione quais decks remotos deseja sincronizar. "
            "Sua seleção será lembrada para próximas sincronizações."
        )
        desc_label.setStyleSheet("margin-bottom: 15px; color: #666;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Seção de decks remotos
        remote_group = QGroupBox("Decks Remotos Disponíveis")
        remote_layout = QVBoxLayout()
        
        # Área de scroll para os checkboxes
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(300)
        
        self.checkboxes_widget = QWidget()
        self.checkboxes_layout = QVBoxLayout()
        self.checkboxes_widget.setLayout(self.checkboxes_layout)
        self.checkboxes_layout.setContentsMargins(10, 10, 10, 10)
        
        scroll_area.setWidget(self.checkboxes_widget)
        remote_layout.addWidget(scroll_area)
        
        # Botões para seleção em massa
        buttons_layout = QHBoxLayout()
        
        self.select_all_button = QPushButton("Selecionar Todos")
        self.select_all_button.setToolTip("Seleciona todos os decks para sincronização")
        
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
        
        # Botões principais
        main_buttons_layout = QHBoxLayout()
        
        self.sync_button = QPushButton("Sincronizar Selecionados")
        self.sync_button.setStyleSheet(
            "font-weight: bold; padding: 10px 20px; "
            "background-color: #4CAF50; color: white; border-radius: 4px;"
        )
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setStyleSheet("padding: 10px 20px; border-radius: 4px;")
        
        main_buttons_layout.addStretch()
        main_buttons_layout.addWidget(self.sync_button)
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
        self.sync_button.clicked.connect(self._sync_selected)
        self.cancel_button.clicked.connect(self.reject)
    
    def _load_decks(self):
        """Carrega os decks ativos como checkboxes."""
        # Limpar checkboxes existentes
        for checkbox in self.deck_checkboxes.values():
            checkbox.setParent(None)
        self.deck_checkboxes.clear()
        self.active_decks.clear()
        
        # Carregar decks ativos
        active_decks = get_active_decks()
        
        for url, deck_info in active_decks.items():
            deck_id = deck_info["deck_id"]
            deck = None
            if mw and hasattr(mw, 'col') and mw.col and hasattr(mw.col, 'decks'):
                deck = mw.col.decks.get(deck_id)
            
            # Verificar se o deck existe localmente
            if deck and deck["name"].strip().lower() != "default":
                # Deck existe localmente
                deck_name = deck["name"]
                card_count = 0
                if mw and hasattr(mw, 'col') and mw.col and hasattr(mw.col, 'find_cards'):
                    card_count = len(mw.col.find_cards(f'deck:"{deck_name}"'))
                
                checkbox_text = f"{deck_name} ({card_count} cards)"
                checkbox = QCheckBox(checkbox_text)
                checkbox.setToolTip(f"URL: {url}")
                
                # Adicionar ao layout
                self.checkboxes_layout.addWidget(checkbox)
                
                # Armazenar referências
                self.deck_checkboxes[url] = checkbox
                self.active_decks.append({
                    "url": url,
                    "deck_info": deck_info,
                    "deck_name": deck_name,
                    "card_count": card_count
                })
                
                # Conectar sinal de mudança
                checkbox.toggled.connect(lambda checked, u=url: self._on_checkbox_changed(u, checked))
                
            else:
                # Deck foi deletado localmente - mostrar como "a ser recriado"
                saved_deck_name = deck_info.get("deck_name", "Deck Remoto")
                
                checkbox_text = f"⚠️ {saved_deck_name} (será recriado)"
                checkbox = QCheckBox(checkbox_text)
                checkbox.setToolTip(f"Deck local foi deletado. Será recriado durante a sincronização.\nURL: {url}")
                checkbox.setStyleSheet("color: #e67e22; font-weight: bold;")
                
                # Adicionar ao layout
                self.checkboxes_layout.addWidget(checkbox)
                
                # Armazenar referências
                self.deck_checkboxes[url] = checkbox
                self.active_decks.append({
                    "url": url,
                    "deck_info": deck_info,
                    "deck_name": saved_deck_name,
                    "card_count": 0
                })
                
                # Conectar sinal de mudança
                checkbox.toggled.connect(lambda checked, u=url: self._on_checkbox_changed(u, checked))
        
        # Atualizar informações
        self._update_selection_info()
    
    def _load_persistent_selection(self):
        """Carrega a seleção persistente salva."""
        from .config_manager import get_sync_selection
        
        self.sync_selection = get_sync_selection()
        
        # Aplicar seleção salva aos checkboxes
        for url, checkbox in self.deck_checkboxes.items():
            is_selected = self.sync_selection.get(url, False)
            checkbox.setChecked(is_selected)
    
    def _save_persistent_selection(self):
        """Salva a seleção atual de forma persistente."""
        from .config_manager import save_sync_selection
        
        save_sync_selection(self.sync_selection)
    
    def _on_checkbox_changed(self, url, checked):
        """Callback para quando um checkbox é alterado."""
        self.sync_selection[url] = checked
        self._update_selection_info()
        self._save_persistent_selection()
    
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
        # Contar seleções
        selected_count = sum(1 for checked in self.sync_selection.values() if checked)
        total_count = len(self.deck_checkboxes)
        
        # Atualizar texto informativo
        if selected_count == 0:
            info_text = "Nenhum deck selecionado"
            info_color = "#e74c3c"
        elif selected_count == total_count:
            info_text = f"Todos os {total_count} deck(s) selecionados"
            info_color = "#27ae60"
        else:
            info_text = f"{selected_count} de {total_count} deck(s) selecionados"
            info_color = "#3498db"
        
        self.selection_info.setText(info_text)
        self.selection_info.setStyleSheet(
            f"margin-top: 10px; padding: 8px; background-color: {info_color}; "
            f"color: white; border-radius: 4px; font-weight: bold;"
        )
        
        # Habilitar/desabilitar botão de sincronização
        self.sync_button.setEnabled(selected_count > 0)
    
    def _sync_selected(self):
        """Sincroniza os decks selecionados."""
        # Coletar URLs selecionadas
        selected_urls = [url for url, checked in self.sync_selection.items() if checked]
        
        # Armazenar URLs selecionadas para uso posterior
        self.selected_urls = selected_urls
        
        self.accept()
    
    def get_selected_urls(self):
        """Retorna as URLs selecionadas para sincronização."""
        return getattr(self, 'selected_urls', [])


def show_sync_dialog(parent=None):
    """
    Mostra o diálogo de sincronização.
    
    Args:
        parent: Widget pai para o diálogo
        
    Returns:
        tuple: (success, selected_urls) onde success é bool e selected_urls é list
    """
    dialog = SyncDialog(parent)
    
    if safe_exec(dialog) == DialogAccepted:
        return True, dialog.get_selected_urls()
    
    return False, []
