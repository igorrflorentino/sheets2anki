"""
Diálogo melhorado para adicionar novos decks remotos.

Este módulo fornece uma interface aprimorada para adicionar decks
com suporte a nomeação automática e resolução de conflitos.
"""

from .compat import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QGroupBox, QFormLayout, QMessageBox,
    QRadioButton, QCheckBox, QProgressBar, QTextEdit,
    DialogAccepted, mw
)
from .fix_exec import safe_exec
from .config_manager import (
    get_remote_decks, add_remote_deck, is_deck_disconnected,
    get_deck_naming_mode, get_parent_deck_name
)
from .deck_naming import (
    extract_deck_name_from_url, get_available_deck_name,
    check_deck_name_conflict, clean_deck_name
)
from .validation import validate_url
from .parseRemoteDeck import getRemoteDeck, RemoteDeckError
from .utils import get_or_create_deck


class AddDeckDialog(QDialog):
    """
    Diálogo aprimorado para adicionar novos decks remotos.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adicionar Novo Deck Remoto")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        self.remote_deck = None
        self.suggested_name = ""
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Configura a interface do usuário."""
        layout = QVBoxLayout()
        
        # Título
        title_label = QLabel("Adicionar Novo Deck Remoto")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Seção de URL
        url_group = QGroupBox("URL da Planilha")
        url_layout = QFormLayout()
        
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("https://docs.google.com/spreadsheets/d/...")
        
        self.validate_button = QPushButton("Validar URL")
        self.validate_button.setMaximumWidth(120)
        
        url_row = QHBoxLayout()
        url_row.addWidget(self.url_edit)
        url_row.addWidget(self.validate_button)
        
        url_layout.addRow("URL:", url_row)
        
        # Status da validação
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("margin-top: 5px;")
        url_layout.addRow(self.status_label)
        
        url_group.setLayout(url_layout)
        layout.addWidget(url_group)
        
        # Seção de nomeação
        naming_group = QGroupBox("Configurações do Deck")
        naming_layout = QVBoxLayout()
        
        # Opções de nomeação
        self.auto_naming_radio = QRadioButton("Usar nomeação automática")
        self.manual_naming_radio = QRadioButton("Definir nome manualmente")
        
        naming_layout.addWidget(self.auto_naming_radio)
        naming_layout.addWidget(self.manual_naming_radio)
        
        # Campo de nome do deck
        name_form = QFormLayout()
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Nome do deck será sugerido automaticamente")
        
        name_form.addRow("Nome do Deck:", self.name_edit)
        
        # Informações sobre hierarquia
        self.hierarchy_label = QLabel("")
        self.hierarchy_label.setStyleSheet("color: #666; font-size: 11px; margin-top: 5px;")
        self.hierarchy_label.setWordWrap(True)  # Permitir quebra de linha
        self.hierarchy_label.setMaximumWidth(450)  # Limitar largura para forçar quebra
        name_form.addRow(self.hierarchy_label)
        
        naming_layout.addLayout(name_form)
        
        # Opção de resolver conflitos
        self.resolve_conflicts_checkbox = QCheckBox("Resolver conflitos de nome automaticamente")
        self.resolve_conflicts_checkbox.setChecked(True)
        naming_layout.addWidget(self.resolve_conflicts_checkbox)
        
        naming_group.setLayout(naming_layout)
        layout.addWidget(naming_group)
        
        # Seção de informações do deck (inicialmente oculta)
        self.info_group = QGroupBox("Informações do Deck")
        self.info_group.setVisible(False)
        
        info_layout = QVBoxLayout()
        self.info_text = QTextEdit()
        self.info_text.setMaximumHeight(100)
        self.info_text.setReadOnly(True)
        info_layout.addWidget(self.info_text)
        
        self.info_group.setLayout(info_layout)
        layout.addWidget(self.info_group)
        
        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Botões
        buttons_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Adicionar Deck")
        self.add_button.setEnabled(False)
        self.cancel_button = QPushButton("Cancelar")
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.cancel_button)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
        # Configurar estado inicial
        self._update_naming_mode()
    
    def _connect_signals(self):
        """Conecta os sinais da interface."""
        self.validate_button.clicked.connect(self._validate_url)
        self.url_edit.textChanged.connect(self._on_url_changed)
        
        self.auto_naming_radio.toggled.connect(self._update_naming_mode)
        self.manual_naming_radio.toggled.connect(self._update_naming_mode)
        
        self.name_edit.textChanged.connect(self._on_name_changed)
        
        # Conectar checkbox para recalcular nome quando alterado
        self.resolve_conflicts_checkbox.toggled.connect(self._on_resolve_conflicts_changed)
        
        self.add_button.clicked.connect(self._add_deck)
        self.cancel_button.clicked.connect(self.reject)
    
    def _update_naming_mode(self):
        """Atualiza a interface baseada no modo de nomeação."""
        # Definir modo padrão baseado na configuração
        default_mode = get_deck_naming_mode()
        
        if not self.auto_naming_radio.isChecked() and not self.manual_naming_radio.isChecked():
            if default_mode == "automatic":
                self.auto_naming_radio.setChecked(True)
            else:
                self.manual_naming_radio.setChecked(True)
        
        # Atualizar interface
        is_auto = self.auto_naming_radio.isChecked()
        
        if is_auto:
            self.name_edit.setEnabled(False)
            self.name_edit.setPlaceholderText("Nome será extraído automaticamente da planilha")
            
            # Mostrar informações sobre hierarquia
            parent_name = get_parent_deck_name()
            self.hierarchy_label.setText(f"Deck será criado como: {parent_name}::Nome_Extraído")
        else:
            self.name_edit.setEnabled(True)
            self.name_edit.setPlaceholderText("Digite o nome do deck")
            self.hierarchy_label.setText("Deck será criado com o nome especificado")
        
        # Atualizar nome sugerido se já validado
        if self.remote_deck and self.suggested_name:
            self._update_suggested_name()
    
    def _on_url_changed(self):
        """Chamado quando a URL é alterada."""
        self.add_button.setEnabled(False)
        self.info_group.setVisible(False)
        self.status_label.setText("")
        self.status_label.setStyleSheet("color: #666;")
        self.remote_deck = None
        self.suggested_name = ""
        
        # Ajustar tamanho da janela automaticamente quando a seção de informações é ocultada
        self.adjustSize()
    
    def _on_name_changed(self):
        """Chamado quando o nome é alterado."""
        if self.manual_naming_radio.isChecked():
            self._check_name_conflict()
    
    def _on_resolve_conflicts_changed(self):
        """Chamado quando o checkbox de resolução de conflitos é alterado."""
        # Recalcular nome se há um nome atual e conflito
        current_name = self.name_edit.text().strip()
        
        if current_name and self.suggested_name:
            # Se checkbox foi marcado e há conflito, aplicar resolução
            if self.resolve_conflicts_checkbox.isChecked() and check_deck_name_conflict(current_name):
                from .deck_naming import resolve_deck_name_conflict
                alternative = resolve_deck_name_conflict(current_name)
                self.name_edit.setText(alternative)
                self._show_status(f"Nome ajustado para evitar conflito:\n{alternative}", "info")
            # Se checkbox foi desmarcado, voltar ao nome original sugerido
            elif not self.resolve_conflicts_checkbox.isChecked():
                self._update_suggested_name()
        
        # Recalcular conflitos com o estado atual
        self._check_name_conflict()
    
    def _validate_url(self):
        """Valida a URL e carrega informações do deck."""
        url = self.url_edit.text().strip()
        
        if not url:
            self._show_status("Por favor, informe uma URL.", "error")
            return
        
        # Verificar se URL já está em uso
        remote_decks = get_remote_decks()
        if url in remote_decks:
            # Verificar se foi desconectado
            if is_deck_disconnected(url):
                self._show_status("URL encontrada na lista de decks desconectados. Será reconectada.", "warning")
            else:
                self._show_status("Esta URL já está cadastrada como deck remoto.", "error")
                return
        
        # Mostrar progresso
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminado
        self.validate_button.setEnabled(False)
        
        try:
            # Validar formato da URL
            validate_url(url)
            
            # Tentar carregar o deck
            self.remote_deck = getRemoteDeck(url)
            
            # Extrair nome sugerido
            self.suggested_name = extract_deck_name_from_url(url)
            
            # Mostrar informações
            self._show_deck_info()
            self._update_suggested_name()
            
            self._show_status("URL validada com sucesso!", "success")
            self.add_button.setEnabled(True)
            
        except RemoteDeckError as e:
            self._show_status(f"Erro ao acessar a planilha: {str(e)}", "error")
        except Exception as e:
            self._show_status(f"Erro na validação: {str(e)}", "error")
        finally:
            self.progress_bar.setVisible(False)
            self.validate_button.setEnabled(True)
    
    def _show_deck_info(self):
        """Mostra informações do deck validado."""
        if not self.remote_deck:
            return
        
        info_lines = []
        
        # Número de questões
        question_count = len(self.remote_deck.questions) if self.remote_deck.questions else 0
        info_lines.append(f"Questões encontradas: {question_count}")
        
        # Questões ignoradas
        if hasattr(self.remote_deck, 'ignored_count') and self.remote_deck.ignored_count > 0:
            info_lines.append(f"Questões ignoradas (SYNC? = não): {self.remote_deck.ignored_count}")
        
        # Arquivos de mídia
        if hasattr(self.remote_deck, 'media') and self.remote_deck.media:
            info_lines.append(f"Arquivos de mídia: {len(self.remote_deck.media)}")
        
        # Nome sugerido
        if self.suggested_name:
            info_lines.append(f"Nome sugerido: {self.suggested_name}")
        
        self.info_text.setText("\n".join(info_lines))
        self.info_group.setVisible(True)
        
        # Ajustar tamanho da janela automaticamente para acomodar as novas informações
        self.adjustSize()
    
    def _update_suggested_name(self):
        """Atualiza o nome sugerido no campo de nome."""
        if not self.suggested_name:
            return
        
        if self.auto_naming_radio.isChecked():
            # Modo automático: mostrar nome com hierarquia
            parent_name = get_parent_deck_name()
            full_name = f"{parent_name}::{self.suggested_name}"
            self.name_edit.setText(full_name)
            
            # Mostrar informações detalhadas no hierarchy_label
            hierarchy_info = f"Deck criado como: {parent_name}::{self.suggested_name}"
            if len(hierarchy_info) > 60:  # Se muito longo, quebrar linha
                hierarchy_info = f"Deck criado como:\n{parent_name}::\n{self.suggested_name}"
            self.hierarchy_label.setText(hierarchy_info)
        else:
            # Modo manual: mostrar apenas o nome base
            self.name_edit.setText(self.suggested_name)
            
            # Mostrar informações no hierarchy_label
            hierarchy_info = f"Deck será criado com nome: {self.suggested_name}"
            if len(hierarchy_info) > 60:  # Se muito longo, quebrar linha
                hierarchy_info = f"Deck será criado com nome:\n{self.suggested_name}"
            self.hierarchy_label.setText(hierarchy_info)
        
        self._check_name_conflict()
    
    def _check_name_conflict(self):
        """Verifica se há conflito de nome."""
        name = self.name_edit.text().strip()
        
        if not name:
            return
        
        if check_deck_name_conflict(name):
            self._show_status("⚠️ Já existe um deck com este nome.", "warning")
            
            if self.resolve_conflicts_checkbox.isChecked():
                # Sugerir nome alternativo
                from .deck_naming import resolve_deck_name_conflict
                alternative = resolve_deck_name_conflict(name)
                self.name_edit.setText(alternative)
                self._show_status(f"Nome ajustado para evitar conflito:\n{alternative}", "info")
        else:
            self._show_status("✓ Nome disponível.", "success")
    
    def _show_status(self, message, status_type="info"):
        """Mostra mensagem de status."""
        colors = {
            "info": "#0066cc",
            "success": "#009900",
            "warning": "#ff9900",
            "error": "#cc0000"
        }
        
        color = colors.get(status_type, "#666")
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {color}; margin-top: 5px;")
    
    def _add_deck(self):
        """Adiciona o deck remoto."""
        url = self.url_edit.text().strip()
        name = self.name_edit.text().strip()
        
        if not url or not name:
            QMessageBox.warning(self, "Erro", "Por favor, preencha a URL e o nome do deck.")
            return
        
        # Verificar conflito final
        if check_deck_name_conflict(name) and not self.resolve_conflicts_checkbox.isChecked():
            QMessageBox.warning(
                self, 
                "Conflito de Nome", 
                "Já existe um deck com este nome. Ative a opção de resolver conflitos automaticamente ou escolha outro nome."
            )
            return
        
        try:
            # Resolver conflito se necessário
            if self.resolve_conflicts_checkbox.isChecked():
                from .deck_naming import resolve_deck_name_conflict
                name = resolve_deck_name_conflict(name)
            
            # Criar deck no Anki
            deck_id = get_or_create_deck(mw.col, name)
            
            # Adicionar à configuração
            deck_info = {
                "url": url,
                "deck_id": deck_id,
                "deck_name": name,
                "created_at": self._get_current_timestamp()
            }
            
            add_remote_deck(url, deck_info)
            
            # Reconectar se estava desconectado
            if is_deck_disconnected(url):
                from .config_manager import reconnect_deck
                reconnect_deck(url)
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao adicionar deck: {str(e)}")
    
    def _get_current_timestamp(self):
        """Obtém timestamp atual."""
        import time
        return int(time.time())
    
    def get_deck_info(self):
        """Retorna informações do deck adicionado."""
        return {
            "url": self.url_edit.text().strip(),
            "name": self.name_edit.text().strip(),
            "is_automatic": self.auto_naming_radio.isChecked()
        }


def show_add_deck_dialog(parent=None):
    """
    Mostra o diálogo para adicionar novo deck remoto.
    
    Args:
        parent: Widget pai para o diálogo
        
    Returns:
        tuple: (success, deck_info) onde success é bool e deck_info é dict
    """
    dialog = AddDeckDialog(parent)
    
    if safe_exec(dialog) == DialogAccepted:
        return True, dialog.get_deck_info()
    
    return False, None
