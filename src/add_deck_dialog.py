"""
Diálogo melhorado para adicionar novos decks remotos.

Este módulo fornece uma interface aprimorada para adicionar decks
com suporte a nomeação automática e resolução de conflitos.
"""

from .compat import DialogAccepted
from .compat import QDialog
from .compat import QGroupBox
from .compat import QHBoxLayout
from .compat import QLabel
from .compat import QLineEdit
from .compat import QMessageBox
from .compat import QProgressBar
from .compat import QPushButton
from .compat import QTimer
from .compat import QVBoxLayout
from .compat import mw
from .compat import safe_exec
from .config_manager import add_remote_deck
from .config_manager import get_remote_decks
from .config_manager import is_deck_disconnected
from .data_processor import RemoteDeckError
from .data_processor import getRemoteDeck
from .templates_and_definitions import DEFAULT_PARENT_DECK_NAME
from .utils import get_or_create_deck
from .utils import validate_url
from .utils import get_spreadsheet_id_from_url


class AddDeckDialog(QDialog):
    """
    Diálogo aprimorado para adicionar novos decks remotos.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adicionar Deck Remoto")
        self.setModal(True)
        self.setMinimumWidth(480)
        # Remover altura fixa para permitir ajuste automático

        self.remote_deck = None
        self.suggested_name = ""
        self.validation_timer = QTimer()  # Inicializar aqui

        self._setup_ui()
        self._connect_signals()
        
        # Ajustar tamanho inicial
        self._adjust_dialog_size()

    def _check_duplicate_spreadsheet(self, url):
        """
        Verifica se uma planilha já está cadastrada no sistema usando o ID da planilha.
        
        Args:
            url (str): URL a ser verificada
            
        Returns:
            tuple: (is_duplicate, deck_info, is_disconnected)
        """
        try:
            # Extrair o ID da planilha da URL
            spreadsheet_id = get_spreadsheet_id_from_url(url)
            
            # Verificar se já existe um deck com este ID
            remote_decks = get_remote_decks()
            if spreadsheet_id in remote_decks:
                deck_info = remote_decks[spreadsheet_id]
                # Se encontramos o ID nos decks remotos, ele não está desconectado
                is_disconnected = False
                return True, deck_info, is_disconnected
                
            return False, None, False
        except ValueError:
            # Se não conseguir extrair o ID, trata como não duplicado
            return False, None, False

    def _format_deck_statistics(self, stats):
        """
        Formata as estatísticas do deck para exibição compacta.
        
        Args:
            stats (dict): Estatísticas do deck remoto
            
        Returns:
            list: Lista de strings formatadas para exibição
        """
        info_items = []
        
        # Estatísticas básicas
        valid_lines = stats.get("valid_note_lines", 0)
        total_lines = stats.get("total_table_lines", 0)
        invalid_lines = stats.get("invalid_note_lines", 0)
        
        # Questões válidas (principal)
        info_items.append(f"📝 {valid_lines} questões válidas")
        
        # Total na planilha (se diferente das válidas)
        if total_lines > valid_lines:
            info_items.append(f"📊 {total_lines} linhas totais")
        
        # Questões inválidas (se houver)
        if invalid_lines > 0:
            info_items.append(f"⚠️ {invalid_lines} linhas sem ID")
        
        # Alunos únicos
        unique_students = stats.get("unique_students_count", 0)
        if unique_students > 0:
            info_items.append(f"👥 {unique_students} aluno(s)")
        
        # Notas potenciais no Anki
        potential_notes = stats.get("total_potential_anki_notes", 0)
        if potential_notes > 0 and potential_notes != valid_lines:
            info_items.append(f"🎯 {potential_notes} notas no Anki")
        
        return info_items

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
        self.url_edit.setPlaceholderText(
            "Cole aqui o link da planilha do Google Sheets..."
        )
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
        self.conflict_warning.setStyleSheet(
            """
            font-size: 12px;
            font-weight: bold;
            color: #ff6600;
            background-color: #fff8dc;
            border: 2px solid #ffcc99;
            border-radius: 6px;
            padding: 8px 12px;
            margin: 4px 0px;
        """
        )
        self.conflict_warning.setWordWrap(True)
        preview_layout.addWidget(self.conflict_warning)

        # Nome do deck preview - Layout melhorado para evitar corte
        deck_name_container = QVBoxLayout()
        deck_name_container.setSpacing(8)

        # Label do título
        deck_name_title = QLabel("Será criado como:")
        deck_name_title.setStyleSheet(
            "font-size: 11px; color: #666; margin-bottom: 2px;"
        )
        deck_name_container.addWidget(deck_name_title)

        # Label do nome com padding adequado
        self.name_preview = QLabel("")
        self.name_preview.setStyleSheet(
            """
            font-weight: bold; 
            color: #2166ac; 
            font-size: 12px;
            padding: 4px 8px;
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 3px;
            margin: 2px 0px;
        """
        )
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
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: none;
                background-color: #e0e0e0;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 2px;
            }
        """
        )
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
        self.add_button.setStyleSheet(
            """
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
        """
        )

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

    def _adjust_dialog_size(self):
        """Ajusta o tamanho da janela baseado no conteúdo visível."""
        layout = self.layout()
        if not layout:
            return
            
        # Usar QTimer para garantir que o ajuste aconteça após o layout ser processado
        QTimer.singleShot(10, self._do_adjust_size)
    
    def _do_adjust_size(self):
        """Executa o ajuste de tamanho da janela."""
        layout = self.layout()
        if not layout:
            return
            
        # Força o layout a recalcular os tamanhos
        layout.activate()
        
        # Obtém o tamanho mínimo necessário baseado no conteúdo
        min_size = layout.minimumSize()
        size_hint = self.sizeHint()
        
        # Calcula o tamanho ideal considerando margens
        ideal_width = max(min_size.width(), size_hint.width(), 480)
        ideal_height = max(min_size.height(), size_hint.height())
        
        # Aplica o novo tamanho
        self.resize(ideal_width, ideal_height)
        
        # Atualiza a geometria da janela
        self.updateGeometry()

    def _on_url_changed(self):
        """Chamado quando a URL é alterada - inicia validação automática."""
        self.add_button.setEnabled(False)
        self.preview_group.setVisible(False)
        self.remote_deck = None
        self.suggested_name = ""
        
        # Ajustar tamanho da janela ao esconder o preview
        self._adjust_dialog_size()

        url = self.url_edit.text().strip()

        if not url:
            self._show_status("Digite ou cole a URL da planilha", "waiting")
            self.validation_timer.stop()
            return

        # Feedback imediato para URLs obviamente inválidas
        if not url.startswith(("http://", "https://")):
            self._show_status("URL deve começar com http:// ou https://", "error")
            self.validation_timer.stop()
            return

        if "docs.google.com/spreadsheets" not in url:
            self._show_status("URL deve ser de uma planilha do Google Sheets", "error")
            self.validation_timer.stop()
            return

        # Iniciar timer para validação automática (debounce de 1.5 segundos)
        self._show_status("Validando URL...", "validating")
        self.validation_timer.stop()
        self.validation_timer.start(1500)

    def _validate_url_auto(self):
        """Valida a URL automaticamente (chamada pelo timer)."""
        from .deck_manager import DeckNameManager

        url = self.url_edit.text().strip()

        if not url:
            return

        # Verificar se URL já está em uso
        is_duplicate, deck_info, is_disconnected = self._check_duplicate_spreadsheet(url)
        if is_duplicate:
            if is_disconnected:
                self._show_status("✓ Planilha reconectará deck desconectado", "warning")
            else:
                deck_name = deck_info.get('remote_deck_name', 'Nome não disponível') if deck_info else 'Nome não disponível'
                self._show_status(f"❌ Planilha já cadastrada: {deck_name}", "error")
                self.add_button.setEnabled(False)
                return

        # Mostrar progresso sutil
        self._show_progress(True)

        try:
            # Validar formato da URL e obter URL TSV
            self.tsv_url = validate_url(url)

            # Tentar carregar o deck usando a URL TSV
            self.remote_deck = getRemoteDeck(self.tsv_url)

            # Extrair nome sugerido da URL original (não TSV)
            self.suggested_name = DeckNameManager.extract_remote_name_from_url(url)

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
        
        # Ajustar tamanho da janela quando barra de progresso muda
        self._adjust_dialog_size()

    def _show_deck_preview(self):
        """Mostra preview compacto do deck validado com estatísticas completas."""
        if not self.remote_deck:
            return

        # Obter estatísticas completas do deck
        deck_stats = self.remote_deck.get_statistics()
        
        # Formatar estatísticas para exibição
        info_items = self._format_deck_statistics(deck_stats)
        
        # Informações adicionais (mídia, etc.)
        if hasattr(self.remote_deck, "media") and self.remote_deck.media:
            info_items.append(f"🖼️ {len(self.remote_deck.media)} arquivo(s) de mídia")

        self.info_label.setText("\n".join(info_items))

        # Mostrar nome final do deck com resolução de conflitos
        self._update_deck_name_preview()

        self.preview_group.setVisible(True)
        
        # Ajustar tamanho da janela ao mostrar o preview
        self._adjust_dialog_size()

    def _update_deck_name_preview(self):
        """Atualiza preview do nome do deck."""
        from .deck_manager import DeckNameManager

        if not self.suggested_name:
            return

        # Gerar nome final com resolução de conflitos usando DeckNameManager
        current_url = self.url_edit.text().strip()
        final_remote_name = DeckNameManager.resolve_remote_name_conflict(
            current_url, self.suggested_name
        )

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
            
            # Ajustar tamanho da janela ao mostrar aviso de conflito
            self._adjust_dialog_size()

            # Nome com estilo de conflito
            self.name_preview.setText(f"{full_name}")
            self.name_preview.setStyleSheet(
                """
                font-weight: bold; 
                color: #ff9900; 
                font-size: 12px;
                padding: 6px 10px;
                background-color: #fff8dc;
                border: 1px solid #ffcc99;
                border-radius: 3px;
                margin: 2px 0px;
            """
            )

        else:
            # SEM CONFLITO - Ocultar aviso
            self.conflict_warning.setVisible(False)
            
            # Ajustar tamanho da janela ao esconder aviso de conflito
            self._adjust_dialog_size()

            # Nome com estilo normal
            self.name_preview.setText(f"{full_name}")
            self.name_preview.setStyleSheet(
                """
                font-weight: bold; 
                color: #2166ac; 
                font-size: 12px;
                padding: 6px 10px;
                background-color: #f0f8ff;
                border: 1px solid #cce7ff;
                border-radius: 3px;
                margin: 2px 0px;
            """
            )

    def _show_status(self, message, status_type="info"):
        """Mostra mensagem de status com indicador visual."""
        # Indicadores visuais
        indicators = {
            "waiting": ("⚪", "#999999"),
            "validating": ("🔄", "#0066cc"),
            "success": ("✅", "#009900"),
            "warning": ("⚠️", "#ff9900"),
            "error": ("❌", "#cc0000"),
        }

        indicator, color = indicators.get(status_type, ("ℹ️", "#666666"))

        # Atualizar indicador visual
        self.status_indicator.setText(indicator)
        self.status_indicator.setStyleSheet(f"color: {color};")

        # Atualizar mensagem
        self.status_label.setText(message)
        self.status_label.setStyleSheet(
            f"color: {color}; font-size: 11px; margin: 2px 0;"
        )

    def _add_deck(self):
        """Adiciona o deck remoto."""
        from .deck_manager import DeckNameManager

        url = self.url_edit.text().strip()

        if not url or not self.remote_deck:
            QMessageBox.warning(self, "Erro", "Por favor, valide a URL primeiro.")
            return

        # Validação final: verificar se URL já está em uso
        is_duplicate, deck_info, is_disconnected = self._check_duplicate_spreadsheet(url)
        if is_duplicate and not is_disconnected:
            deck_name = deck_info.get('remote_deck_name', 'Nome não disponível') if deck_info else 'Nome não disponível'
            QMessageBox.warning(
                self, 
                "Planilha Já Cadastrada", 
                f"Esta planilha já está cadastrada no sistema.\n\n"
                f"Deck existente: {deck_name}"
            )
            return

        # Gerar nome do deck usando DeckNameManager
        parent_name = DEFAULT_PARENT_DECK_NAME
        final_remote_name = DeckNameManager.resolve_remote_name_conflict(
            url, self.suggested_name
        )
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
            )

            add_remote_deck(url, deck_info)

            # Sincronizar nome do deck no Anki com a configuração usando DeckNameManager
            sync_result = DeckNameManager.sync_deck_with_config(url)
            if sync_result:
                synced_deck_id, synced_name = sync_result
                print(f"[ADD_DECK] Deck sincronizado: {actual_name} → {synced_name}")

            # Aplicar opções Sheets2Anki ao deck recém-criado
            try:
                from .utils import apply_sheets2anki_options_to_deck

                apply_sheets2anki_options_to_deck(deck_id)
                print(
                    f"[ADD_DECK] Opções Sheets2Anki aplicadas ao deck '{actual_name}'"
                )
            except Exception as e:
                print(f"[ADD_DECK] Aviso: Erro ao aplicar opções: {e}")

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

    def get_deck_info(self):
        """Retorna informações do deck adicionado."""
        from .deck_manager import DeckNameManager

        url = self.url_edit.text().strip()
        from .config_manager import get_deck_local_name

        # Nome final com resolução de conflitos usando DeckNameManager
        final_remote_name = DeckNameManager.resolve_remote_name_conflict(
            url, self.suggested_name
        )
        parent_name = DEFAULT_PARENT_DECK_NAME
        full_name = f"{parent_name}::{final_remote_name}"

        # Tentar obter o nome real da configuração
        actual_name = get_deck_local_name(url) or full_name

        return {"url": url, "name": actual_name, "is_automatic": True}


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
