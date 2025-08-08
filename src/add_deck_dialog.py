"""
Diálogo melhorado para adicionar novos decks remotos.

Este módulo fornece uma interface aprimorada para adicionar decks
com suporte a nomeação automática e resolução de conflitos.
"""

from .compat import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QGroupBox, QFormLayout, QMessageBox,
    QRadioButton, QProgressBar, QTextEdit, QTimer,
    DialogAccepted, mw
)
from .fix_exec import safe_exec
from .config_manager import (
    get_remote_decks, add_remote_deck, is_deck_disconnected
)
from .constants import DEFAULT_PARENT_DECK_NAME
from .deck_naming import DeckNamer
from .validation import validate_url
from .parseRemoteDeck import getRemoteDeck, RemoteDeckError
from .utils import get_or_create_deck


class AddDeckDialog(QDialog):
    """
    Diálogo aprimorado para adicionar novos decks remotos.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adicionar Deck Remoto")
        self.setModal(True)
        self.setMinimumWidth(480)
        self.setMaximumWidth(520)
        
        self.remote_deck = None
        self.suggested_name = ""
        self.validation_timer = QTimer()  # Inicializar aqui
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Configura a interface do usuário de forma mais compacta."""
        layout = QVBoxLayout()
        layout.setSpacing(12)  # Espaçamento reduzido
        
        # Seção de URL - Mais compacta
        url_group = QGroupBox("URL da Planilha Google Sheets")
        url_layout = QVBoxLayout()
        url_layout.setSpacing(8)
        
        # Input de URL com validação visual inline
        url_row = QHBoxLayout()
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("Cole aqui o link da planilha do Google Sheets...")
        self.url_edit.setMinimumHeight(32)
        
        # Status visual inline (mais compacto)
        self.status_indicator = QLabel("⚪")  # Indicador visual simples
        self.status_indicator.setFixedWidth(20)
        self.status_indicator.setToolTip("Status da validação")
        
        url_row.addWidget(self.url_edit)
        url_row.addWidget(self.status_indicator)
        url_layout.addLayout(url_row)
        
        # Status message (mais compacto)
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("font-size: 11px; margin: 2px 0;")
        self.status_label.setWordWrap(True)
        url_layout.addWidget(self.status_label)
        
        url_group.setLayout(url_layout)
        layout.addWidget(url_group)
        
        # Seção de preview - Apenas quando necessário
        self.preview_group = QGroupBox("Preview do Deck")
        self.preview_group.setVisible(False)
        preview_layout = QVBoxLayout()
        preview_layout.setSpacing(6)
        
        # Informações compactas em formato de lista
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("font-size: 11px; line-height: 1.4;")
        self.info_label.setWordWrap(True)
        preview_layout.addWidget(self.info_label)
        
        # Aviso de conflito de nome (inicialmente oculto)
        self.conflict_warning = QLabel("")
        self.conflict_warning.setVisible(False)
        self.conflict_warning.setStyleSheet("""
            font-size: 12px;
            font-weight: bold;
            color: #ff6600;
            background-color: #fff8dc;
            border: 2px solid #ffcc99;
            border-radius: 6px;
            padding: 8px 12px;
            margin: 4px 0px;
        """)
        self.conflict_warning.setWordWrap(True)
        preview_layout.addWidget(self.conflict_warning)
        
        # Nome do deck preview - Layout melhorado para evitar corte
        deck_name_container = QVBoxLayout()
        deck_name_container.setSpacing(8)
        
        # Label do título
        deck_name_title = QLabel("Será criado como:")
        deck_name_title.setStyleSheet("font-size: 11px; color: #666; margin-bottom: 2px;")
        deck_name_container.addWidget(deck_name_title)
        
        # Label do nome com padding adequado
        self.name_preview = QLabel("")
        self.name_preview.setStyleSheet("""
            font-weight: bold; 
            color: #2166ac; 
            font-size: 12px;
            padding: 4px 8px;
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 3px;
            margin: 2px 0px;
        """)
        self.name_preview.setWordWrap(True)
        self.name_preview.setMinimumHeight(24)  # Altura mínima para evitar corte
        deck_name_container.addWidget(self.name_preview)
        
        preview_layout.addLayout(deck_name_container)
        
        self.preview_group.setLayout(preview_layout)
        layout.addWidget(self.preview_group)
        
        # Barra de progresso compacta
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(4)  # Muito mais fina
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #e0e0e0;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 2px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Botões - Layout mais limpo
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 8, 0, 0)
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setMaximumWidth(80)
        
        self.add_button = QPushButton("Adicionar Deck")
        self.add_button.setEnabled(False)
        self.add_button.setMinimumWidth(120)  # Garantir largura mínima
        self.add_button.setMaximumWidth(140)  # Aumentar largura máxima
        self.add_button.setStyleSheet("""
            QPushButton:enabled {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
                padding: 8px 16px;
                border-radius: 4px;
            }
        """)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.add_button)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
        # Configurar estado inicial
        self._show_status("Digite ou cole a URL da planilha", "waiting")
        self.conflict_warning.setVisible(False)  # Inicialmente oculto
    
    def _connect_signals(self):
        """Conecta os sinais da interface."""
        # Configurar timer para validação automática com debounce
        self.validation_timer.setSingleShot(True)
        self.validation_timer.timeout.connect(self._validate_url_auto)
        
        self.url_edit.textChanged.connect(self._on_url_changed)
        self.add_button.clicked.connect(self._add_deck)
        self.cancel_button.clicked.connect(self.reject)
    
    def _on_url_changed(self):
        """Chamado quando a URL é alterada - inicia validação automática."""
        self.add_button.setEnabled(False)
        self.preview_group.setVisible(False)
        self.remote_deck = None
        self.suggested_name = ""
        
        url = self.url_edit.text().strip()
        
        if not url:
            self._show_status("Digite ou cole a URL da planilha", "waiting")
            self.validation_timer.stop()
            return
        
        # Feedback imediato para URLs obviamente inválidas
        if not url.startswith(('http://', 'https://')):
            self._show_status("URL deve começar com http:// ou https://", "error")
            self.validation_timer.stop()
            return
        
        if 'docs.google.com/spreadsheets' not in url:
            self._show_status("URL deve ser de uma planilha do Google Sheets", "error")
            self.validation_timer.stop()
            return
        
        # Iniciar timer para validação automática (debounce de 1.5 segundos)
        self._show_status("Validando URL...", "validating")
        self.validation_timer.stop()
        self.validation_timer.start(1500)
    
    def _validate_url_auto(self):
        """Valida a URL automaticamente (chamada pelo timer)."""
        url = self.url_edit.text().strip()
        
        if not url:
            return
        
        # Verificar se URL já está em uso
        remote_decks = get_remote_decks()
        if url in remote_decks:
            # Verificar se foi desconectado
            if is_deck_disconnected(url):
                self._show_status("✓ URL reconectará deck desconectado", "warning")
            else:
                self._show_status("❌ Esta URL já está cadastrada", "error")
                return
        
        # Mostrar progresso sutil
        self._show_progress(True)
        
        try:
            # Validar formato da URL
            validate_url(url)
            
            # Tentar carregar o deck
            self.remote_deck = getRemoteDeck(url)
            
            # Extrair nome sugerido
            self.suggested_name = DeckNamer.extract_name_from_url(url)
            
            # Mostrar informações de forma compacta
            self._show_deck_preview()
            
            self._show_status("✓ URL validada com sucesso!", "success")
            self.add_button.setEnabled(True)
            
        except RemoteDeckError as e:
            self._show_status(f"❌ Erro ao acessar planilha: {str(e)}", "error")
        except Exception as e:
            self._show_status(f"❌ Erro na validação: {str(e)}", "error")
        finally:
            self._show_progress(False)
    
    def _show_progress(self, show):
        """Mostra/oculta a barra de progresso."""
        if show:
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminado
        else:
            self.progress_bar.setVisible(False)
    
    def _show_deck_preview(self):
        """Mostra preview compacto do deck validado."""
        if not self.remote_deck:
            return
        
        # Informações básicas em formato compacto
        info_items = []
        
        # Número de questões
        question_count = len(self.remote_deck.questions) if self.remote_deck.questions else 0
        info_items.append(f"📝 {question_count} questões encontradas")
        
        # Questões ignoradas
        if hasattr(self.remote_deck, 'ignored_count') and self.remote_deck.ignored_count > 0:
            info_items.append(f"⚠️ {self.remote_deck.ignored_count} questões ignoradas")
        
        # Arquivos de mídia
        if hasattr(self.remote_deck, 'media') and self.remote_deck.media:
            info_items.append(f"🖼️ {len(self.remote_deck.media)} arquivos de mídia")
        
        self.info_label.setText(" • ".join(info_items))
        
        # Mostrar nome final do deck com resolução de conflitos
        self._update_deck_name_preview()
        
        self.preview_group.setVisible(True)
    
    def _update_deck_name_preview(self):
        """Atualiza preview do nome do deck."""
        if not self.suggested_name:
            return
        
        # Gerar nome final com resolução de conflitos
        from .config_manager import resolve_remote_deck_name_conflict
        current_url = self.url_edit.text().strip()
        final_remote_name = resolve_remote_deck_name_conflict(current_url, self.suggested_name)
        
        # Nome completo hierárquico
        parent_name = DEFAULT_PARENT_DECK_NAME
        full_name = f"{parent_name}::{final_remote_name}"
        
        # Verificar se há conflito e mostrar aviso apropriado
        if final_remote_name != self.suggested_name:
            # CONFLITO DETECTADO - Mostrar aviso destacado
            conflict_message = (
                f"🚨 <b>Conflito de nome do deck remoto detectado!</b><br>"
                f"📝 <b>Nome original:</b> '{self.suggested_name}'<br>"
                f"🔄 <b>Renomeação automática aplicada</b>"
            )
            self.conflict_warning.setText(conflict_message)
            self.conflict_warning.setVisible(True)
            
            # Nome com estilo de conflito
            self.name_preview.setText(f"{full_name}")
            self.name_preview.setStyleSheet("""
                font-weight: bold; 
                color: #ff9900; 
                font-size: 12px;
                padding: 6px 10px;
                background-color: #fff8dc;
                border: 1px solid #ffcc99;
                border-radius: 3px;
                margin: 2px 0px;
            """)
            
        else:
            # SEM CONFLITO - Ocultar aviso
            self.conflict_warning.setVisible(False)
            
            # Nome com estilo normal
            self.name_preview.setText(f"{full_name}")
            self.name_preview.setStyleSheet("""
                font-weight: bold; 
                color: #2166ac; 
                font-size: 12px;
                padding: 6px 10px;
                background-color: #f0f8ff;
                border: 1px solid #cce7ff;
                border-radius: 3px;
                margin: 2px 0px;
            """)
    
    def _show_status(self, message, status_type="info"):
        """Mostra mensagem de status com indicador visual."""
        # Indicadores visuais
        indicators = {
            "waiting": ("⚪", "#999999"),
            "validating": ("🔄", "#0066cc"),
            "success": ("✅", "#009900"),
            "warning": ("⚠️", "#ff9900"),
            "error": ("❌", "#cc0000")
        }
        
        indicator, color = indicators.get(status_type, ("ℹ️", "#666666"))
        
        # Atualizar indicador visual
        self.status_indicator.setText(indicator)
        self.status_indicator.setStyleSheet(f"color: {color};")
        
        # Atualizar mensagem
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {color}; font-size: 11px; margin: 2px 0;")
    
    def _add_deck(self):
        """Adiciona o deck remoto."""
        url = self.url_edit.text().strip()
        
        if not url or not self.remote_deck:
            QMessageBox.warning(self, "Erro", "Por favor, valide a URL primeiro.")
            return
        
        # Gerar nome do deck
        parent_name = DEFAULT_PARENT_DECK_NAME
        from .config_manager import resolve_remote_deck_name_conflict
        final_remote_name = resolve_remote_deck_name_conflict(url, self.suggested_name)
        full_name = f"{parent_name}::{final_remote_name}"
        
        self._show_progress(True)
        self.add_button.setEnabled(False)
        
        try:
            # Criar deck no Anki
            deck_id, actual_name = get_or_create_deck(mw.col, full_name)
            
            # Adicionar à configuração usando a nova estrutura modular
            from .config_manager import create_deck_info
            deck_info = create_deck_info(
                url=url,
                local_deck_id=deck_id,
                local_deck_name=actual_name,
                remote_deck_name=final_remote_name,
                created_at=self._get_current_timestamp()
            )
            
            add_remote_deck(url, deck_info)
            
            # Sincronizar nome do deck no Anki com a configuração
            from .utils import sync_deck_name_with_config
            sync_result = sync_deck_name_with_config(mw.col, url, debug_messages=[])
            if sync_result:
                synced_deck_id, synced_name = sync_result
                print(f"[ADD_DECK] Deck sincronizado: {actual_name} → {synced_name}")
            
            # Reconectar se estava desconectado
            if is_deck_disconnected(url):
                from .config_manager import reconnect_deck
                reconnect_deck(url)
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao adicionar deck:\n{str(e)}")
            self.add_button.setEnabled(True)
        finally:
            self._show_progress(False)
    
    def _get_current_timestamp(self):
        """Obtém timestamp atual."""
        import time
        return int(time.time())
    
    def get_deck_info(self):
        """Retorna informações do deck adicionado."""
        url = self.url_edit.text().strip()
        from .config_manager import get_deck_local_name, resolve_remote_deck_name_conflict
        
        # Nome final com resolução de conflitos
        final_remote_name = resolve_remote_deck_name_conflict(url, self.suggested_name)
        parent_name = DEFAULT_PARENT_DECK_NAME
        full_name = f"{parent_name}::{final_remote_name}"
        
        # Tentar obter o nome real da configuração
        actual_name = get_deck_local_name(url) or full_name
            
        return {
            "url": url,
            "name": actual_name,
            "is_automatic": True
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
