"""
Diálogo para sincronização de decks ativos.

Este módulo fornece uma interface para o usuário
selecionar e sincronizar decks ativos do sistema.
"""

from .compat import DialogAccepted
from .compat import QApplication
from .compat import QCheckBox
from .compat import QDialog
from .compat import QGroupBox
from .compat import QHBoxLayout
from .compat import QLabel
from .compat import QPushButton
from .compat import QScrollArea
from .compat import QVBoxLayout
from .compat import QWidget
from .compat import mw
from .compat import safe_exec
from .config_manager import get_active_decks
from .config_manager import get_deck_local_name
from .config_manager import get_deck_remote_name


def clean_url_for_browser(url):
    """
    Remove a terminação '&output=tsv' da URL para permitir visualização no navegador.

    Args:
        url (str): URL completa com terminação TSV

    Returns:
        str: URL limpa para visualização no navegador
    """
    if url.endswith("&output=tsv"):
        return url[:-11]  # Remove '&output=tsv'
    elif url.endswith("&single=true&output=tsv"):
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
        "border: 1px solid palette(text); "  # Borda mais contrastante
        "color: palette(text); "  # Texto bem contrastante
        "} "
        "QPushButton:hover { "
        "background-color: palette(highlight); "  # Destaque no hover
        "color: palette(highlightedText); "  # Texto do highlight
        "border: 1px solid palette(highlight); "
        "} "
        "QPushButton:pressed { "
        "background-color: palette(shadow); "  # Cor pressed distinta
        "color: palette(base); "  # Texto contrastante
        "border: 1px solid palette(shadow); "
        "}"
    )


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
        self.deck_checkboxes = {}  # hash_key -> QCheckBox
        self.deck_hash_mapping = {}  # URL -> hash_key (para compatibilidade)

        self._setup_ui()
        self._load_decks()
        self._load_persistent_selection()
        self._connect_signals()

    def _setup_ui(self):
        """Configura a interface do usuário."""
        layout = QVBoxLayout()

        # Título
        title_label = QLabel("Sincronizar Decks")
        title_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; margin-bottom: 10px;"
        )
        layout.addWidget(title_label)

        # Descrição
        desc_label = QLabel(
            "Selecione quais decks remotos deseja sincronizar. "
            "Os nomes mostrados são dos arquivos TSV remotos. "
            "Use o botão 'Copy URL' para visualizar o deck no navegador. "
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

        for hash_key, deck_info in active_decks.items():
            local_deck_id = deck_info["local_deck_id"]
            remote_deck_url = deck_info.get("remote_deck_url", "")
            deck = None
            if mw and hasattr(mw, "col") and mw.col and hasattr(mw.col, "decks"):
                deck = mw.col.decks.get(local_deck_id)

            # Obter nome remoto do deck
            remote_name = get_deck_remote_name(remote_deck_url) or "Deck Remoto"

            # Verificar se o deck existe localmente
            if deck and deck["name"].strip().lower() != "default":
                # Deck existe localmente
                local_deck_name = deck["name"]
                card_count = 0
                if (
                    mw
                    and hasattr(mw, "col")
                    and mw.col
                    and hasattr(mw.col, "find_cards")
                ):
                    escaped_deck_name = local_deck_name.replace('"', '\\"')
                    card_count = len(mw.col.find_cards(f'deck:"{escaped_deck_name}"'))

                # Usar nome remoto com contador de cards
                checkbox_text = f"{remote_name} ({card_count} cards)"

                # Criar layout horizontal para checkbox + botão
                row_layout = QHBoxLayout()

                checkbox = QCheckBox(checkbox_text)
                checkbox.setToolTip(
                    f"Deck remoto: {remote_name}\nDeck local: {local_deck_name}\nURL: {remote_deck_url}"
                )

                # Botão Copy URL
                copy_button = QPushButton("Copy URL")
                copy_button.setMaximumWidth(80)
                copy_button.setMaximumHeight(25)
                copy_button.setToolTip("Copiar URL para visualizar no navegador")
                copy_button.setStyleSheet(get_copy_button_style())
                copy_button.clicked.connect(
                    lambda checked, u=remote_deck_url: self._copy_url(u)
                )

                row_layout.addWidget(checkbox)
                row_layout.addWidget(copy_button)
                row_layout.addStretch()

                # Criar widget container para o layout
                row_widget = QWidget()
                row_widget.setLayout(row_layout)

                # Adicionar ao layout principal
                self.checkboxes_layout.addWidget(row_widget)

                # Armazenar referências - usar hash_key como chave principal
                self.deck_checkboxes[hash_key] = checkbox
                self.deck_hash_mapping[remote_deck_url] = hash_key
                self.active_decks.append(
                    {
                        "url": remote_deck_url,
                        "hash_key": hash_key,
                        "deck_info": deck_info,
                        "local_deck_name": local_deck_name,
                        "remote_deck_name": remote_name,
                        "card_count": card_count,
                    }
                )

                # Conectar sinal de mudança - passar hash_key
                checkbox.toggled.connect(
                    lambda checked, hk=hash_key: self._on_checkbox_changed(hk, checked)
                )

            else:
                # Deck foi deletado localmente, mas pode ser recriado
                local_deck_name = (
                    get_deck_local_name(remote_deck_url) or "Deck Local Deletado"
                )

                # Usar nome remoto com aviso
                checkbox_text = f"⚠️ {remote_name} (será recriado)"

                # Criar layout horizontal para checkbox + botão
                row_layout = QHBoxLayout()

                checkbox = QCheckBox(checkbox_text)
                checkbox.setToolTip(
                    f"Deck remoto: {remote_name}\nDeck local foi deletado: {local_deck_name}\nSerá recriado durante a sincronização.\nURL: {remote_deck_url}"
                )
                checkbox.setStyleSheet(
                    "color: palette(bright-text); font-weight: bold; background-color: rgba(230, 126, 34, 0.2);"
                )

                # Botão Copy URL
                copy_button = QPushButton("Copy URL")
                copy_button.setMaximumWidth(80)
                copy_button.setMaximumHeight(25)
                copy_button.setToolTip("Copiar URL para visualizar no navegador")
                copy_button.setStyleSheet(get_copy_button_style())
                copy_button.clicked.connect(
                    lambda checked, u=remote_deck_url: self._copy_url(u)
                )

                row_layout.addWidget(checkbox)
                row_layout.addWidget(copy_button)
                row_layout.addStretch()

                # Criar widget container para o layout
                row_widget = QWidget()
                row_widget.setLayout(row_layout)

                # Adicionar ao layout principal
                self.checkboxes_layout.addWidget(row_widget)

                # Armazenar referências - usar hash_key como chave principal
                self.deck_checkboxes[hash_key] = checkbox
                self.deck_hash_mapping[remote_deck_url] = hash_key
                self.active_decks.append(
                    {
                        "url": remote_deck_url,
                        "hash_key": hash_key,
                        "deck_info": deck_info,
                        "local_deck_name": local_deck_name,
                        "remote_deck_name": remote_name,
                        "card_count": 0,
                    }
                )

                # Conectar sinal de mudança - passar hash_key
                checkbox.toggled.connect(
                    lambda checked, hk=hash_key: self._on_checkbox_changed(hk, checked)
                )

        # Atualizar informações
        self._update_selection_info()

    def _load_persistent_selection(self):
        """Carrega a seleção persistente salva baseada no is_sync do meta.json."""
        from .config_manager import get_meta

        meta = get_meta()
        decks = meta.get("decks", {})

        # Aplicar seleção salva aos checkboxes baseado no is_sync de cada deck
        for hash_key, checkbox in self.deck_checkboxes.items():
            deck_info = decks.get(hash_key, {})
            is_selected = deck_info.get("is_sync", True)  # Padrão: True
            checkbox.setChecked(is_selected)

        self._update_selection_info()

    def _on_checkbox_changed(self, hash_key, checked):
        """Callback para quando um checkbox é alterado."""
        from .config_manager import get_meta
        from .config_manager import save_meta

        # Atualizar o is_sync no meta.json
        meta = get_meta()
        if "decks" not in meta:
            meta["decks"] = {}

        if hash_key in meta["decks"]:
            meta["decks"][hash_key]["is_sync"] = checked
            save_meta(meta)

        self._update_selection_info()

    def _select_all(self):
        """Seleciona todos os decks."""
        for hash_key, checkbox in self.deck_checkboxes.items():
            checkbox.setChecked(True)

    def _select_none(self):
        """Desmarca todos os decks."""
        for hash_key, checkbox in self.deck_checkboxes.items():
            checkbox.setChecked(False)

    def _invert_selection(self):
        """Inverte a seleção atual."""
        for hash_key, checkbox in self.deck_checkboxes.items():
            checkbox.setChecked(not checkbox.isChecked())

    def _update_selection_info(self):
        """Atualiza as informações de seleção."""
        # Contar seleções baseado nos checkboxes
        selected_count = sum(
            1 for checkbox in self.deck_checkboxes.values() if checkbox.isChecked()
        )
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

    def _copy_url(self, url):
        """
        Copia a URL limpa para o clipboard.

        Args:
            url (str): URL do deck remoto
        """
        copy_url_to_clipboard(url)

    def _sync_selected(self):
        """Sincroniza os decks selecionados."""
        # Coletar URLs selecionadas baseado nos checkboxes
        selected_urls = []
        for hash_key, checkbox in self.deck_checkboxes.items():
            if checkbox.isChecked():
                # Encontrar a URL correspondente ao hash_key
                for deck_info in self.active_decks:
                    if deck_info["hash_key"] == hash_key:
                        selected_urls.append(deck_info["url"])
                        break

        # Armazenar URLs selecionadas para uso posterior
        self.selected_urls = selected_urls

        self.accept()

    def get_selected_urls(self):
        """Retorna as URLs selecionadas para sincronização."""
        return getattr(self, "selected_urls", [])


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
