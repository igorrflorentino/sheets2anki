"""
Dialogs de interface do usuário para o addon Sheets2Anki.

Este módulo contém os dialogs Qt utilizados para
interação com o usuário.
"""

from .compat import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QCheckBox,
    DialogAccepted, DialogRejected, mw
)
from .fix_exec import safe_exec

class DeckSelectionDialog(QDialog):
    """
    Dialog para seleção de decks para sincronização.
    
    Permite ao usuário escolher quais decks remotos devem ser sincronizados,
    mostrando informações como nome do deck e número de cards.
    """
    
    def __init__(self, deck_info_list, parent=None):
        """
        Inicializa o dialog de seleção de decks.
        
        Args:
            deck_info_list: Lista de tuplas (deck_name, card_count)
            parent: Widget pai (opcional)
        """
        super().__init__(parent)
        self.setWindowTitle("Selecionar Decks para Sincronizar")
        self.setMinimumSize(500, 350)
        
        # Armazenar informações dos decks
        self.deck_info_list = deck_info_list
        
        # Configurar interface
        self._setup_ui()
        
        # Conectar eventos após criar todos os elementos
        self._connect_events()
        
        # Atualizar status inicial
        self.update_status()
    
    def _setup_ui(self):
        """Configura os elementos da interface do usuário."""
        # Layout principal
        layout = QVBoxLayout()
        
        # Label de instruções
        instruction_label = QLabel("Selecione os decks que deseja sincronizar:")
        instruction_label.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(instruction_label)
        
        # Criar checkboxes para cada deck
        self.checkboxes = {}
        for deck_name, card_count in self.deck_info_list:
            # Mostrar nome do deck e número de cards
            display_text = f"{deck_name} ({card_count} cards)"
            checkbox = QCheckBox(display_text)
            checkbox.setChecked(True)  # Por padrão, todos selecionados
            self.checkboxes[deck_name] = checkbox
            layout.addWidget(checkbox)
        
        # Espaçador
        layout.addSpacing(10)
        
        # Botões de seleção rápida
        self._add_selection_buttons(layout)
        
        # Espaçador
        layout.addSpacing(10)
        
        # Label de status
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(self.status_label)
        
        # Botões de confirmação
        self._add_confirmation_buttons(layout)
        
        self.setLayout(layout)
    
    def _add_selection_buttons(self, layout):
        """Adiciona botões de seleção rápida (Selecionar/Desmarcar Todos)."""
        button_layout = QHBoxLayout()
        
        select_all_btn = QPushButton("Selecionar Todos")
        select_all_btn.clicked.connect(self.select_all)
        button_layout.addWidget(select_all_btn)
        
        deselect_all_btn = QPushButton("Desmarcar Todos")
        deselect_all_btn.clicked.connect(self.deselect_all)
        button_layout.addWidget(deselect_all_btn)
        
        layout.addLayout(button_layout)
    
    def _add_confirmation_buttons(self, layout):
        """Adiciona botões OK e Cancel."""
        confirm_layout = QHBoxLayout()
        
        self.ok_btn = QPushButton("Sincronizar")
        self.ok_btn.clicked.connect(self.accept)
        confirm_layout.addWidget(self.ok_btn)
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        confirm_layout.addWidget(cancel_btn)
        
        layout.addLayout(confirm_layout)
    
    def _connect_events(self):
        """Conecta eventos após todos os elementos serem criados."""
        for checkbox in self.checkboxes.values():
            checkbox.stateChanged.connect(self.update_status)
    
    def select_all(self):
        """Marca todos os checkboxes."""
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(True)
    
    def deselect_all(self):
        """Desmarca todos os checkboxes."""
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(False)
    
    def update_status(self):
        """Atualiza o label de status e habilita/desabilita o botão OK."""
        selected_count = len(self.get_selected_decks())
        total_count = len(self.checkboxes)
        
        if selected_count == 0:
            self.status_label.setText("Nenhum deck selecionado")
            self.ok_btn.setEnabled(False)
        else:
            self.status_label.setText(f"{selected_count} de {total_count} decks selecionados")
            self.ok_btn.setEnabled(True)
    
    def get_selected_decks(self):
        """
        Retorna lista com nomes dos decks selecionados.
        
        Returns:
            list: Lista de nomes dos decks marcados
        """
        selected = []
        for deck_name, checkbox in self.checkboxes.items():
            if checkbox.isChecked():
                selected.append(deck_name)
        return selected
