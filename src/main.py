"""
Módulo Principal de Sincronização de Decks Remotos

Este módulo implementa a funcionalidade principal para sincronização de decks do Anki
com planilhas do Google Sheets em formato TSV. 

Funcionalidades principais:
- Sincronização bidirecional com Google Sheets
- Interface de seleção de decks
- Validação de URLs e dados
- Criação automática de modelos de cards
- Suporte a cards cloze e padrão
- Gerenciamento de erros robusto

Estrutura do código:
1. Imports e configuração de compatibilidade
2. Constantes e dados de teste
3. Exceções customizadas
4. Dialogs de interface do usuário
5. Funções de gerenciamento de decks
6. Funções de validação
7. Funções principais de sincronização
8. Funções utilitárias
9. Funções de template de cards
10. Funções de processamento de notas
11. Funções de interface para gerenciamento

Autor: Sheets2Anki Project
"""

# =============================================================================
# IMPORTS
# =============================================================================

# Compatibilidade Qt/Anki
from .compat import (
    mw, showInfo, showWarning, showCritical, show_tooltip,
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QCheckBox,
    QInputDialog, QLineEdit, QProgressDialog, QMessageBox,
    Qt, AlignTop, AlignLeft, AlignCenter, DialogAccepted, DialogRejected,
    EchoModeNormal, safe_connect, create_button, show_message,
    get_compatibility_info
)

# Import QDialog separadamente para herança
from .compat import QDialog

# Standard library imports
import sys
import urllib.request
import urllib.error
import socket
import hashlib
import json
from typing import List, Dict, Tuple, Optional, Any

# Local imports
from .parseRemoteDeck import getRemoteDeck, has_cloze_deletion
from . import column_definitions

# =============================================================================
# CONSTANTS AND TEST DATA
# =============================================================================

# URLs hardcoded para testes e simulações
TEST_SHEETS_URLS = [
    ("Mais importantes", "https://docs.google.com/spreadsheets/d/e/2PACX-1vSART0Xw_lDq5bn4bylNox7vxOmU6YkoOjOwqdS3kZ-O1JEBLR8paqDv_bcGTW55yXchaO0jzK2cB8x/pub?gid=334628680&output=tsv"),
    ("Menos importantes", "https://docs.google.com/spreadsheets/d/e/2PACX-1vSART0Xw_lDq5bn4bylNox7vxOmU6YkoOjOwqdS3kZ-O1JEBLR8paqDv_bcGTW55yXchaO0jzK2cB8x/pub?gid=1869088045&output=tsv"),
]

# Template constants para geração de cards
CARD_SHOW_ALLWAYS_TEMPLATE = """
<b>{field_name}:</b><br>
{{{{{field_value}}}}}<br><br>
"""

CARD_SHOW_HIDE_TEMPLATE = """
{{{{#{field_value}}}}}
<b>{field_name}:</b><br>
{{{{{field_value}}}}}<br><br>
{{{{/{field_value}}}}}
"""

# =============================================================================
# CUSTOM EXCEPTIONS
# =============================================================================

class SyncError(Exception):
    """Base exception for sync-related errors."""
    pass

class NoteProcessingError(SyncError):
    """Exception raised when processing a note fails."""
    pass

class CollectionSaveError(SyncError):
    """Exception raised when saving the collection fails."""
    pass

# =============================================================================
# UI DIALOGS
# =============================================================================

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

# =============================================================================
# DECK MANAGEMENT FUNCTIONS
# =============================================================================

def syncDecksWithSelection():
    """
    Mostra interface para selecionar decks e sincroniza apenas os selecionados.
    
    Esta função é o ponto de entrada principal para sincronização interativa.
    Permite ao usuário escolher quais decks devem ser sincronizados através
    de uma interface gráfica.
    """
    # Carregar configuração
    config = get_addon_config()

    # Verificar se há decks configurados
    if not config["remote-decks"]:
        showInfo("Nenhum deck remoto configurado para sincronização.")
        return

    # Obter informações dos decks válidos
    deck_info_list, valid_decks = _get_valid_deck_info(config)
    
    # Verificar se há decks válidos
    if not deck_info_list:
        showInfo("Nenhum deck remoto válido encontrado para sincronização.")
        return

    # Se há apenas um deck, sincronizar diretamente
    if len(deck_info_list) == 1:
        syncDecks()
        return

    # Mostrar interface de seleção e processar resultado
    _show_selection_dialog_and_sync(deck_info_list)

def _get_valid_deck_info(config):
    """
    Extrai informações dos decks válidos da configuração.
    
    Args:
        config: Configuração do addon
        
    Returns:
        tuple: (deck_info_list, valid_decks) onde deck_info_list contém
               tuplas (deck_name, card_count) e valid_decks mapeia 
               nomes para informações dos decks
    """
    deck_info_list = []
    valid_decks = {}
    
    for url, deck_info in config["remote-decks"].items():
        deck_id = deck_info["deck_id"]
        deck = mw.col.decks.get(deck_id)
        
        # Verificar se o deck ainda existe e não é o deck padrão
        if deck and deck["name"].strip().lower() != "default":
            deck_name = deck["name"]
            # Contar cards no deck
            card_count = len(mw.col.find_cards(f'deck:"{deck_name}"'))
            deck_info_list.append((deck_name, card_count))
            valid_decks[deck_name] = deck_info
    
    return deck_info_list, valid_decks

def _show_selection_dialog_and_sync(deck_info_list):
    """
    Mostra o dialog de seleção e executa a sincronização dos decks selecionados.
    
    Args:
        deck_info_list: Lista de informações dos decks válidos
    """
    dialog = DeckSelectionDialog(deck_info_list, mw)
    
    # Compatibilidade com diferentes versões do Qt
    try:
        # Qt6 usa exec()
        result = dialog.exec()
    except AttributeError:
        # Qt5 usa exec_()
        result = dialog.exec_()
    
    if result == DialogAccepted:
        selected_decks = dialog.get_selected_decks()
        if selected_decks:
            syncDecks(selected_decks)
        else:
            showInfo("Nenhum deck foi selecionado para sincronização.")

def import_test_deck():
    """
    Permite importar rapidamente um dos decks de teste hardcoded.
    
    Esta função é útil para desenvolvimento e testes, permitindo
    importar rapidamente decks pré-configurados sem precisar
    inserir URLs manualmente.
    """
    # Obter lista de nomes dos decks de teste
    names = [name for name, url in TEST_SHEETS_URLS]
    
    # Mostrar dialog de seleção
    selection, okPressed = QInputDialog.getItem(
        mw,
        "Importar Deck de Teste",
        "Escolha um deck de teste para importar:",
        names,
        0,
        False
    )
    
    if not okPressed or not selection:
        return

    # Buscar a URL correspondente ao deck selecionado
    url = dict(TEST_SHEETS_URLS)[selection]

    # Sugerir um nome padrão para o deck
    deckName = f"Deck de Teste do sheet2anki:: {selection}"

    try:
        # Validar URL e importar deck
        _import_deck_from_url(url, deckName)
        syncDecks()
    except (ValueError, SyncError) as e:
        showInfo(f"Erro ao importar deck de teste:\n{str(e)}")
    except Exception as e:
        showInfo(f"Erro inesperado ao importar deck de teste:\n{str(e)}")

def _import_deck_from_url(url, deckName):
    """
    Importa um deck a partir de uma URL, validando e configurando.
    
    Args:
        url: URL do Google Sheets em formato TSV
        deckName: Nome do deck a ser criado
    """
    # Validar URL
    validate_url(url)
    
    # Criar ou obter o deck
    deck_id = get_or_create_deck(mw.col, deckName)

    # Buscar dados do deck remoto
    deck = getRemoteDeck(url)
    deck.deckName = deckName
    # deck.url = url  # Comentado devido ao erro de atribuição

    # Atualizar configuração
    config = get_addon_config()
    
    config["remote-decks"][url] = {
        "url": url,
        "deck_id": deck_id,
        "deck_name": deckName
    }
    save_addon_config(config)

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_addon_config():
    """
    Obter configuração do addon de forma segura.
    
    Returns:
        dict: Configuração do addon com chave 'remote-decks' garantida
    """
    try:
        config = mw.addonManager.getConfig(__name__)
        if not config:
            config = {}
        
        # Garantir que a chave 'remote-decks' existe
        if "remote-decks" not in config:
            config["remote-decks"] = {}
            
        return config
    except Exception as e:
        showWarning(f"Erro ao carregar configuração: {str(e)}")
        return {"remote-decks": {}}

def save_addon_config(config):
    """
    Salvar configuração do addon de forma segura.
    
    Args:
        config: Dicionário com configuração do addon
    """
    try:
        mw.addonManager.writeConfig(__name__, config)
    except Exception as e:
        showWarning(f"Erro ao salvar configuração: {str(e)}")

# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def validate_url(url):
    """
    Valida se a URL é uma URL válida do Google Sheets em formato TSV.
    
    Args:
        url (str): A URL a ser validada
        
    Raises:
        ValueError: Se a URL for inválida ou inacessível
        URLError: Se houver problemas de conectividade de rede
        HTTPError: Se o servidor retornar um erro de status
    """
    # Verificar se a URL não está vazia
    if not url or not isinstance(url, str):
        raise ValueError("URL deve ser uma string não vazia")

    # Validar formato da URL
    if not url.startswith(('http://', 'https://')):
        raise ValueError("URL inválida: Deve começar com http:// ou https://")
    
    # Validar formato TSV do Google Sheets
    if not any(param in url.lower() for param in ['output=tsv', 'format=tsv']):
        raise ValueError("A URL fornecida não parece ser um TSV publicado do Google Sheets. "
                        "Certifique-se de publicar a planilha em formato TSV.")
    
    # Testar acessibilidade da URL com timeout e tratamento de erros adequado
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Sheets2Anki) AnkiAddon'  # User agent mais específico
        }
        request = urllib.request.Request(url, headers=headers)
        
        # USAR TIMEOUT LOCAL ao invés de global para evitar conflitos
        # socket.setdefaulttimeout(30)  # ❌ REMOVIDO: configuração global
        
        response = urllib.request.urlopen(request, timeout=30)  # ✅ TIMEOUT LOCAL
        
        if response.getcode() != 200:
            raise ValueError(f"URL retornou código de status inesperado: {response.getcode()}")
        
        # Validar tipo de conteúdo
        content_type = response.headers.get('Content-Type', '').lower()
        if not any(valid_type in content_type for valid_type in ['text/tab-separated-values', 'text/plain', 'text/csv']):
            raise ValueError(f"URL não retorna conteúdo TSV (recebido {content_type})")
            
    except socket.timeout:
        raise ValueError("Timeout de conexão ao acessar a URL (30s). Verifique sua conexão ou tente novamente.")
    except urllib.error.HTTPError as e:
        raise ValueError(f"Erro HTTP {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        if isinstance(e.reason, socket.timeout):
            raise ValueError("Timeout de conexão ao acessar a URL. Verifique sua conexão ou tente novamente.")
        elif isinstance(e.reason, socket.gaierror):
            raise ValueError("Erro de DNS. Verifique sua conexão com a internet.")
        else:
            raise ValueError(f"Erro ao acessar URL - Problema de rede ou servidor: {str(e.reason)}")
    except Exception as e:
        raise ValueError(f"Erro inesperado ao acessar URL: {str(e)}")
    # finally:  # ❌ REMOVIDO: não precisamos resetar timeout global
    #     # Resetar timeout padrão
    #     socket.setdefaulttimeout(None)

# =============================================================================
# CORE SYNCHRONIZATION FUNCTIONS
# =============================================================================
    
def syncDecks(selected_deck_names=None):
    """
    Sincroniza todos os decks remotos com suas fontes.
    
    Esta é a função principal de sincronização que:
    1. Baixa dados dos decks remotos
    2. Processa e valida os dados
    3. Atualiza o banco de dados do Anki
    4. Mostra progresso ao usuário
    
    Args:
        selected_deck_names: Lista de nomes de decks para sincronizar. 
                           Se None, sincroniza todos os decks.
    """
    col = mw.col
    config = get_addon_config()

    # Inicializar estatísticas e controles
    sync_errors = []
    status_msgs = []
    decks_synced = 0
    total_stats = {
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'errors': 0,
        'error_details': []
    }

    # Determinar quais decks sincronizar
    deck_keys = _get_deck_keys_to_sync(config, selected_deck_names)
    total_decks = len(deck_keys)
    
    # Verificar se há decks para sincronizar
    if total_decks == 0:
        _show_no_decks_message(selected_deck_names)
        return
    
    # Configurar e mostrar barra de progresso
    progress = _setup_progress_dialog(total_decks)
    
    step = 0
    try:
        # Sincronizar cada deck
        for deckKey in deck_keys:
            try:
                step, deck_sync_increment, current_stats = _sync_single_deck(
                    config, deckKey, progress, status_msgs, step
                )
                
                # Acumular estatísticas
                _accumulate_stats(total_stats, current_stats)
                decks_synced += deck_sync_increment

            except (ValueError, SyncError) as e:
                step, sync_errors = _handle_sync_error(
                    e, deckKey, config, progress, status_msgs, sync_errors, step
                )
                continue
            except Exception as e:
                step, sync_errors = _handle_unexpected_error(
                    e, deckKey, config, progress, status_msgs, sync_errors, step
                )
                continue
        
        # Finalizar progresso e mostrar resultados
        _finalize_sync(progress, total_decks, decks_synced, total_stats, sync_errors)
    
    finally:
        # Garantir que o dialog de progresso seja fechado
        if progress.isVisible():
            progress.close()

def _get_deck_keys_to_sync(config, selected_deck_names):
    """
    Determina quais chaves de deck devem ser sincronizadas.
    
    Args:
        config: Configuração do addon
        selected_deck_names: Nomes dos decks selecionados ou None
        
    Returns:
        list: Lista de chaves de deck para sincronizar
    """
    deck_keys = list(config["remote-decks"].keys())
    
    # Filtrar decks se uma seleção específica foi fornecida
    if selected_deck_names is not None:
        # Mapear nomes de deck para suas chaves de configuração (URLs)
        name_to_key = _build_name_to_key_mapping(config)
        
        # Filtrar apenas os decks selecionados
        filtered_keys = []
        for deck_name in selected_deck_names:
            if deck_name in name_to_key:
                filtered_keys.append(name_to_key[deck_name])
        
        deck_keys = filtered_keys
    
    return deck_keys

def _build_name_to_key_mapping(config):
    """
    Constrói mapeamento de nomes de deck para chaves de configuração.
    
    Args:
        config: Configuração do addon
        
    Returns:
        dict: Mapeamento de nomes para chaves
    """
    name_to_key = {}
    for key, deck_info in config["remote-decks"].items():
        # Obter o nome real do deck no Anki, não o nome salvo na config
        deck_id = deck_info.get("deck_id")
        if deck_id:
            deck = mw.col.decks.get(deck_id)
            if deck:
                actual_deck_name = deck["name"]
                name_to_key[actual_deck_name] = key
            else:
                # Fallback para o nome salvo na config se o deck não existir
                config_deck_name = deck_info.get("deck_name", "")
                if config_deck_name:
                    name_to_key[config_deck_name] = key
    
    return name_to_key

def _show_no_decks_message(selected_deck_names):
    """Mostra mensagem quando não há decks para sincronizar."""
    if selected_deck_names is not None:
        showInfo(f"Nenhum dos decks selecionados foi encontrado na configuração.\n\nDecks selecionados: {', '.join(selected_deck_names)}")
    else:
        showInfo("Nenhum deck remoto configurado para sincronização.")

def _setup_progress_dialog(total_decks):
    """
    Configura e retorna o dialog de progresso com tamanho fixo.
    
    Esta função configura uma barra de progresso com:
    - Largura fixa de 500px para evitar redimensionamento horizontal
    - Altura mínima de 120px e máxima de 300px para acomodar texto multilinha
    - Quebra automática de linha para textos longos
    - Alinhamento adequado do texto
    
    Args:
        total_decks: Número total de decks para calcular o máximo da barra
        
    Returns:
        QProgressDialog: Dialog de progresso configurado
    """
    progress = QProgressDialog("Sincronizando decks...", "", 0, total_decks * 3, mw)
    progress.setWindowTitle("Sincronização de Decks")
    progress.setMinimumDuration(0)
    progress.setValue(0)
    progress.setCancelButton(None)
    progress.setAutoClose(False)  # Não fechar automaticamente
    progress.setAutoReset(False)  # Não resetar automaticamente
    
    # Configurar tamanho fixo horizontal e permitir ajuste vertical
    progress.setFixedWidth(500)  # Largura fixa de 500 pixels
    progress.setMinimumHeight(120)  # Altura mínima
    progress.setMaximumHeight(300)  # Altura máxima
    
    # Configurar o label para quebrar linha automaticamente
    label = progress.findChild(QLabel)
    if label:
        label.setWordWrap(True)  # Permitir quebra de linha
        label.setAlignment(AlignTop | AlignLeft)  # Alinhar ao topo e à esquerda
    
    progress.show()
    mw.app.processEvents()  # Força a exibição da barra
    return progress

def _update_progress_text(progress, status_msgs, max_lines=3):
    """
    Atualiza o texto da barra de progresso com formatação adequada.
    
    Args:
        progress: QProgressDialog instance
        status_msgs: Lista de mensagens de status
        max_lines: Número máximo de linhas a mostrar
    """
    # Pegar apenas as últimas mensagens
    recent_msgs = status_msgs[-max_lines:] if len(status_msgs) > max_lines else status_msgs
    
    # Juntar mensagens com quebra de linha
    text = "\n".join(recent_msgs)
    
    # Limitar o comprimento de cada linha para evitar texto muito longo
    lines = text.split('\n')
    formatted_lines = []
    
    for line in lines:
        # Se a linha for muito longa, quebrar em palavras
        if len(line) > 60:  # Aproximadamente 60 caracteres por linha
            words = line.split(' ')
            current_line = ""
            for word in words:
                if len(current_line + word + " ") <= 60:
                    current_line += word + " "
                else:
                    if current_line:
                        formatted_lines.append(current_line.strip())
                    current_line = word + " "
            if current_line:
                formatted_lines.append(current_line.strip())
        else:
            formatted_lines.append(line)
    
    # Atualizar o texto da barra de progresso
    final_text = "\n".join(formatted_lines)
    progress.setLabelText(final_text)
    
    # Forçar atualização da interface
    mw.app.processEvents()

def _sync_single_deck(config, deckKey, progress, status_msgs, step):
    """
    Sincroniza um único deck.
    
    Returns:
        tuple: (step_updated, decks_synced_increment, deck_stats)
    """
    currentRemoteInfo = config["remote-decks"][deckKey]
    deck_id = currentRemoteInfo["deck_id"]

    # Obter nome do deck para exibição
    deck = mw.col.decks.get(deck_id)
    
    # Se o deck não existe ou virou Default, remover da config e pular
    if not deck or deck["name"].strip().lower() == "default":
        removed_name = currentRemoteInfo.get("deck_name", str(deck_id))
        del config["remote-decks"][deckKey]
        save_addon_config(config)
        info_msg = f"A sincronização do deck '{removed_name}' foi encerrada automaticamente porque o deck foi excluído ou virou o deck padrão (Default)."
        status_msgs.append(info_msg)
        _update_progress_text(progress, status_msgs)
        step += 3
        progress.setValue(step)
        mw.app.processEvents()
        return step, 0, {'created': 0, 'updated': 0, 'deleted': 0, 'errors': 0, 'error_details': []}
    
    deckName = deck["name"]

    # Validar URL antes de tentar sincronizar
    validate_url(currentRemoteInfo["url"])

    # 1. Download
    msg = f"{deckName}: baixando arquivo..."
    status_msgs.append(msg)
    _update_progress_text(progress, status_msgs)
    
    remoteDeck = getRemoteDeck(currentRemoteInfo["url"])
    step += 1
    progress.setValue(step)
    mw.app.processEvents()

    # 2. Parsing (já inclusos no getRemoteDeck)
    msg = f"{deckName}: processando dados..."
    status_msgs.append(msg)
    _update_progress_text(progress, status_msgs)
    
    remoteDeck.deckName = deckName
    # remoteDeck.url = currentRemoteInfo["url"]  # Comentado devido ao erro
    step += 1
    progress.setValue(step)
    mw.app.processEvents()

    # 3. Escrita no banco
    msg = f"{deckName}: escrevendo no banco de dados..."
    status_msgs.append(msg)
    _update_progress_text(progress, status_msgs)
    
    deck_stats = create_or_update_notes(mw.col, remoteDeck, deck_id)
    step += 1
    progress.setValue(step)
    mw.app.processEvents()
    
    return step, 1, deck_stats

def _accumulate_stats(total_stats, deck_stats):
    """Acumula estatísticas de um deck nas estatísticas totais."""
    total_stats['created'] += deck_stats['created']
    total_stats['updated'] += deck_stats['updated']
    total_stats['deleted'] += deck_stats['deleted']
    total_stats['errors'] += deck_stats['errors']
    total_stats['error_details'].extend(deck_stats['error_details'])

def _handle_sync_error(e, deckKey, config, progress, status_msgs, sync_errors, step):
    """Trata erros de sincronização de deck."""
    # Tentar obter o nome do deck para a mensagem de erro
    try:
        deck_info = config["remote-decks"][deckKey]
        deck_id = deck_info["deck_id"]
        deck = mw.col.decks.get(deck_id)
        deckName = deck["name"] if deck else deck_info.get("deck_name", str(deck_id))
    except:
        deckName = "Unknown"
    
    error_msg = f"Failed to sync deck '{deckName}': {str(e)}"
    sync_errors.append(error_msg)
    status_msgs.append(error_msg)
    _update_progress_text(progress, status_msgs)
    step += 3
    progress.setValue(step)
    mw.app.processEvents()
    return step, sync_errors

def _handle_unexpected_error(e, deckKey, config, progress, status_msgs, sync_errors, step):
    """Trata erros inesperados durante sincronização."""
    # Tentar obter o nome do deck para a mensagem de erro
    try:
        deck_info = config["remote-decks"][deckKey]
        deck_id = deck_info["deck_id"]
        deck = mw.col.decks.get(deck_id)
        deckName = deck["name"] if deck else deck_info.get("deck_name", str(deck_id))
    except:
        deckName = "Unknown"
    
    error_msg = f"Unexpected error syncing deck '{deckName}': {str(e)}"
    sync_errors.append(error_msg)
    status_msgs.append(error_msg)
    _update_progress_text(progress, status_msgs)
    step += 3
    progress.setValue(step)
    mw.app.processEvents()
    return step, sync_errors

def _finalize_sync(progress, total_decks, decks_synced, total_stats, sync_errors):
    """Finaliza a sincronização mostrando resultados."""
    progress.setValue(total_decks * 3)
    mw.app.processEvents()
    
    # Preparar mensagem final para exibir na barra de progresso
    if sync_errors or total_stats['errors'] > 0:
        final_msg = f"Concluído com problemas: {decks_synced}/{total_decks} decks sincronizados"
        if total_stats['created'] > 0:
            final_msg += f", {total_stats['created']} cards criados"
        if total_stats['updated'] > 0:
            final_msg += f", {total_stats['updated']} atualizados"
        if total_stats['deleted'] > 0:
            final_msg += f", {total_stats['deleted']} deletados"
        final_msg += f", {total_stats['errors'] + len(sync_errors)} erros"
    else:
        final_msg = f"Sincronização concluída com sucesso!"
        if total_stats['created'] > 0:
            final_msg += f" {total_stats['created']} cards criados"
        if total_stats['updated'] > 0:
            final_msg += f", {total_stats['updated']} atualizados"
        if total_stats['deleted'] > 0:
            final_msg += f", {total_stats['deleted']} deletados"
    
    # Exibir mensagem final na barra e adicionar botão OK
    # Usar uma lista temporária para a mensagem final
    final_status_msgs = [final_msg]
    _update_progress_text(progress, final_status_msgs, max_lines=5)  # Permitir mais linhas para mensagem final
    
    # Criar e configurar o botão OK
    ok_button = QPushButton("OK")
    progress.setCancelButton(ok_button)
    
    # Aguardar o usuário clicar em OK
    while progress.isVisible() and not progress.wasCanceled():
        mw.app.processEvents()
        import time
        time.sleep(0.1)
    
    # Mostrar resumo abrangente dos resultados da sincronização
    _show_sync_summary(sync_errors, total_stats, decks_synced, total_decks)

def _show_sync_summary(sync_errors, total_stats, decks_synced, total_decks):
    """Mostra resumo detalhado da sincronização."""
    if sync_errors or total_stats['errors'] > 0:
        summary = f"Sincronização concluída com alguns problemas:\n\n"
        summary += f"Decks sincronizados: {decks_synced}/{total_decks}\n"
        summary += f"Cards criados: {total_stats['created']}\n"
        summary += f"Cards atualizados: {total_stats['updated']}\n"
        summary += f"Cards deletados: {total_stats['deleted']}\n"
        summary += f"Erros encontrados: {total_stats['errors'] + len(sync_errors)}\n\n"
        
        # Adicionar erros de nível de deck
        if sync_errors:
            summary += "Erros de sincronização de decks:\n"
            summary += "\n".join(sync_errors) + "\n\n"
        
        # Adicionar erros de nível de note
        if total_stats['error_details']:
            summary += "Erros de processamento de cards:\n"
            summary += "\n".join(total_stats['error_details'][:10])  # Limitar aos primeiros 10 erros
            if len(total_stats['error_details']) > 10:
                summary += f"\n... e mais {len(total_stats['error_details']) - 10} erros."
        
        showInfo(summary)
    else:
        summary = f"Sincronização concluída com sucesso!\n\n"
        summary += f"Decks sincronizados: {decks_synced}\n"
        summary += f"Cards criados: {total_stats['created']}\n"
        summary += f"Cards atualizados: {total_stats['updated']}\n"
        summary += f"Cards deletados: {total_stats['deleted']}\n"
        summary += "Nenhum erro encontrado."
        showInfo(summary)

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_or_create_deck(col, deckName):
    """
    Cria ou obtém um deck existente no Anki.
    
    Args:
        col: Collection do Anki
        deckName: Nome do deck
        
    Returns:
        int: ID do deck
        
    Raises:
        ValueError: Se o nome do deck for inválido
    """
    if not deckName or not isinstance(deckName, str) or deckName.strip() == "" or deckName.strip().lower() == "default":
        raise ValueError("Nome de deck inválido ou proibido para sincronização: '%s'" % deckName)
    
    deck = col.decks.by_name(deckName)
    if deck is None:
        try:
            deck_id = col.decks.id(deckName)
        except Exception as e:
            raise ValueError(f"Não foi possível criar o deck '{deckName}': {str(e)}")
    else:
        deck_id = deck["id"]
    return deck_id

def get_model_suffix_from_url(url):
    """
    Gera um sufixo único e curto baseado na URL.
    
    Args:
        url: URL do deck remoto
        
    Returns:
        str: Sufixo de 8 caracteres baseado no hash SHA1 da URL
    """
    return hashlib.sha1(url.encode()).hexdigest()[:8]

def get_note_key(note):
    """
    Obtém a chave do campo de uma nota baseado no seu tipo.
    
    Args:
        note: Nota do Anki
        
    Returns:
        str: Valor da chave ou None se não encontrada
    """
    if "Text" in note:
        return note["Text"]
    elif "Front" in note:
        return note["Front"]
    return None

# =============================================================================
# CARD TEMPLATE FUNCTIONS
# =============================================================================

def create_card_template(is_cloze=False):
    """
    Cria o template HTML para um card (padrão ou cloze).
    
    Args:
        is_cloze (bool): Se deve criar um template de cloze
        
    Returns:
        dict: Dicionário com strings de template 'qfmt' e 'afmt'
    """
    # Campos de cabeçalho comuns
    header_fields = [
        (column_definitions.TOPICO, column_definitions.TOPICO),
        (column_definitions.SUBTOPICO, column_definitions.SUBTOPICO),
    ]
    
    # Construir seção de cabeçalho
    header = ""
    for field_name, field_value in header_fields:
        header += CARD_SHOW_ALLWAYS_TEMPLATE.format(
            field_name=field_name.capitalize(),
            field_value=field_value
        )
    
    # Formato da pergunta
    question = (
        "<hr><br>"
        f"<b>{column_definitions.PERGUNTA.capitalize()}:</b><br>"
        f"{{{{{'cloze:' if is_cloze else ''}{column_definitions.PERGUNTA}}}}}"
    )

    # Formato da resposta
    match = (
        "<br><br>"
        f"<b>{column_definitions.MATCH.capitalize()}:</b><br>"
        f"{{{{{'cloze:' if is_cloze else ''}{column_definitions.MATCH}}}}}"
        "<br><br><hr><br>"
    )

    # Campos de informação extra
    extra_info_fields = [
        column_definitions.EXTRA_INFO_1,
        column_definitions.EXTRA_INFO_2
    ]
    
    extra_info = ""
    for field in extra_info_fields:
        extra_info += CARD_SHOW_HIDE_TEMPLATE.format(
            field_name=field.capitalize(),
            field_value=field
        )
    
    # Campos de exemplo
    example_fields = [
        column_definitions.EXEMPLO_1,
        column_definitions.EXEMPLO_2,
        column_definitions.EXEMPLO_3
    ]
    
    examples = ""
    for field in example_fields:
        examples += CARD_SHOW_HIDE_TEMPLATE.format(
            field_name=field.capitalize(),
            field_value=field
        )

    # Campos de rodapé
    footer_fields = [
        (column_definitions.BANCAS, column_definitions.BANCAS),
        (column_definitions.ANO, column_definitions.ANO),
        (column_definitions.MORE_TAGS, column_definitions.MORE_TAGS)
    ]

    # Construir seção de rodapé
    footer = ""
    for field_name, field_value in footer_fields:
        footer += CARD_SHOW_HIDE_TEMPLATE.format(
            field_name=field_name.capitalize(),
            field_value=field_value
        )
    
    # Construir templates completos
    qfmt = header + question
    afmt = (header + 
            question + 
            match + 
            extra_info + 
            examples + 
            "<hr><br>" + 
            footer) if is_cloze else ("{{FrontSide}}" + 
                                      match + 
                                      extra_info + 
                                      examples + 
                                      "<hr><br>" + 
                                      footer)

    return {'qfmt': qfmt, 'afmt': afmt}

def create_model(col, model_name, is_cloze=False):
    """
    Cria um novo modelo de nota do Anki.
    
    Args:
        col: Objeto de coleção do Anki
        model_name (str): Nome para o novo modelo
        is_cloze (bool): Se deve criar um modelo de cloze
        
    Returns:
        object: O modelo do Anki criado
    """
    model = col.models.new(model_name)
    if is_cloze:
        model['type'] = 1  # Definir como tipo cloze
    
    # Adicionar campos
    for field in column_definitions.REQUIRED_COLUMNS:
        template = col.models.new_field(field)
        col.models.add_field(model, template)
    
    # Adicionar template de card
    template = col.models.new_template("Cloze" if is_cloze else "Card 1")
    card_template = create_card_template(is_cloze)
    template['qfmt'] = card_template['qfmt']
    template['afmt'] = card_template['afmt']
    
    col.models.add_template(model, template)
    col.models.save(model)
    return model

def ensure_custom_models(col, url):
    """
    Garante que ambos os modelos (padrão e cloze) existam no Anki.
    
    Args:
        col: Objeto de coleção do Anki
        url (str): URL do deck remoto
        
    Returns:
        dict: Dicionário contendo os modelos 'standard' e 'cloze'
    """
    models = {}
    suffix = get_model_suffix_from_url(url)
    
    # Modelo padrão
    model_name = f"CadernoErrosConcurso_{suffix}_Basic"
    model = col.models.by_name(model_name)
    if model is None:
        model = create_model(col, model_name)
    models['standard'] = model
    
    # Modelo cloze
    cloze_model_name = f"CadernoErrosConcurso_{suffix}_Cloze"
    cloze_model = col.models.by_name(cloze_model_name)
    if cloze_model is None:
        cloze_model = create_model(col, cloze_model_name, is_cloze=True)
    models['cloze'] = cloze_model
    
    return models

# =============================================================================
# NOTE PROCESSING FUNCTIONS
# =============================================================================

def create_or_update_notes(col, remoteDeck, deck_id):
    """
    Cria ou atualiza notas no deck baseado nos dados remotos.
    
    Esta função sincroniza o deck do Anki com os dados remotos através de:
    1. Criação de novas notas para itens que não existem no Anki
    2. Atualização de notas existentes com novo conteúdo da fonte remota
    3. Remoção de notas que não existem mais na fonte remota
    
    Args:
        col: Objeto de coleção do Anki
        remoteDeck (RemoteDeck): Objeto do deck remoto contendo os dados para sincronizar
        deck_id (int): ID do deck do Anki para sincronizar
        
    Returns:
        dict: Estatísticas de sincronização contendo contagens para notas criadas,
              atualizadas, deletadas e erros
        
    Raises:
        SyncError: Se houver erros críticos durante a sincronização
        CollectionSaveError: Se falhar ao salvar a coleção
    """
    def note_needs_update(note, fields, tags):
        """Verifica se uma nota precisa ser atualizada."""
        # Comparar todos os campos relevantes
        for field_name, value in fields.items():
            if field_name in note:
                # Anki armazena campos como string
                if str(note[field_name]).strip() != str(value).strip():
                    return True
        # Comparar tags (ordem não importa)
        note_tags = set(note.tags) if hasattr(note, 'tags') else set()
        tsv_tags = set(tags) if tags else set()
        if note_tags != tsv_tags:
            return True
        return False

    try:
        # Garantir que os modelos customizados existam
        models = ensure_custom_models(col, remoteDeck.url if hasattr(remoteDeck, 'url') else "")
        
        # Rastrear estatísticas de sincronização
        stats = {
            'created': 0,
            'updated': 0,
            'deleted': 0,
            'errors': 0,
            'error_details': []
        }
        
        # Construir índice de notas existentes
        existing_notes = {}
        existing_note_ids = {}
        for nid in col.find_notes(f'deck:"{remoteDeck.deckName}"'):
            note = col.get_note(nid)
            key = note[column_definitions.ID] if column_definitions.ID in note else None
            if key:
                existing_notes[key] = note
                existing_note_ids[key] = nid

        # Rastrear chaves processadas para identificar exclusões
        processed_keys = set()

        # Processar cada pergunta da fonte remota
        for question in remoteDeck.questions:
            try:
                fields = question['fields']
                
                # Validar campos obrigatórios
                key = fields.get(column_definitions.ID)
                if not key:
                    raise NoteProcessingError("Row missing required ID field")
                
                if not fields.get(column_definitions.PERGUNTA):
                    raise NoteProcessingError(f"Row with ID {key} missing required question field")
                
                processed_keys.add(key)
                
                # Processar tags
                tags = question.get('tags', [])

                if key in existing_notes:
                    # Atualizar nota existente SOMENTE SE houver diferença real
                    note = existing_notes[key]
                    if note_needs_update(note, fields, tags):
                        for field_name, value in fields.items():
                            if field_name in note:
                                note[field_name] = value
                        note.tags = tags
                        try:
                            note.flush()
                            stats['updated'] += 1
                        except Exception as e:
                            raise NoteProcessingError(f"Error updating note {key}: {str(e)}")
                else:
                    # Criar nova nota
                    has_cloze = has_cloze_deletion(fields[column_definitions.PERGUNTA])
                    model_to_use = models['cloze'] if has_cloze else models['standard']
                    
                    col.models.set_current(model_to_use)
                    model_to_use['did'] = deck_id
                    col.models.save(model_to_use)

                    note = col.new_note(model_to_use)
                    for field_name, value in fields.items():
                        if field_name in note:
                            note[field_name] = value
                    note.tags = tags
                    
                    try:
                        col.add_note(note, deck_id)
                        stats['created'] += 1
                    except Exception as e:
                        raise NoteProcessingError(f"Error creating note {key}: {str(e)}")

            except NoteProcessingError as e:
                stats['errors'] += 1
                stats['error_details'].append(str(e))
                continue

        # Lidar com exclusões
        notes_to_delete = set(existing_notes.keys()) - processed_keys
        stats['deleted'] = len(notes_to_delete)

        if notes_to_delete:
            try:
                note_ids_to_delete = [existing_note_ids[key] for key in notes_to_delete]
                col.remove_notes(note_ids_to_delete)
            except Exception as e:
                raise NoteProcessingError(f"Error deleting notes: {str(e)}")

        # Salvar mudanças
        try:
            col.save()
        except Exception as e:
            raise CollectionSaveError(f"Error saving collection: {str(e)}")

        # Retornar estatísticas sem mostrar info
        return stats

    except SyncError as e:
        error_msg = f"Critical sync error: {str(e)}"
        raise SyncError(error_msg)
    except Exception as e:
        error_msg = f"Unexpected error during sync: {str(e)}"
        raise SyncError(error_msg)

# =============================================================================
# DECK MANAGEMENT INTERFACE FUNCTIONS
# =============================================================================

def addNewDeck():
    """
    Adiciona um novo deck remoto a partir de uma URL TSV do Google Sheets.
    
    Esta função permite ao usuário:
    1. Inserir uma URL de planilha publicada em formato TSV
    2. Validar a URL
    3. Definir um nome para o deck
    4. Configurar e iniciar a sincronização
    """
    # Solicitar URL do usuário
    url, okPressed = QInputDialog.getText(
        mw, "Add New Remote Deck", "URL of published TSV:", EchoModeNormal, ""
    )
    if not okPressed or not url.strip():
        return

    url = url.strip()

    try:
        # Validar formato e acessibilidade da URL
        validate_url(url)
    except ValueError as e:
        showInfo(str(e))
        return

    # Obter nome do deck
    deckName, okPressed = QInputDialog.getText(
        mw, "Deck Name", "Enter the name of the deck:", EchoModeNormal, ""
    )
    if not okPressed:
        return
    
    deckName = deckName.strip()
    if not deckName:
        deckName = "Deck from CSV"

    # Verificar configuração
    config = get_addon_config()

    # Verificar se a URL já está em uso
    if url in config["remote-decks"]:
        showInfo(f"This URL has already been added as a remote deck.")
        return

    # Criar ou obter ID do deck
    deck_id = get_or_create_deck(mw.col, deckName)

    # Validar se o deck pode ser obtido
    try:
        deck = getRemoteDeck(url)
        deck.deckName = deckName
        # deck.url = url  # Comentado devido ao erro de atribuição
    except Exception as e:
        showInfo(f"Error fetching the remote deck:\n{str(e)}")
        return

    # Salvar configuração e sincronizar
    try:
        config["remote-decks"][url] = {
            "url": url,
            "deck_id": deck_id,
            "deck_name": deckName
        }
        save_addon_config(config)
        syncDecks()
    except Exception as e:
        showInfo(f"Error saving deck configuration:\n{str(e)}")
        # Remover configuração com falha
        if url in config["remote-decks"]:
            del config["remote-decks"][url]
            save_addon_config(config)

def removeRemoteDeck():
    """
    Remove um deck remoto da configuração mantendo o deck local.
    
    Esta função permite ao usuário:
    1. Visualizar todos os decks remotos configurados
    2. Selecionar um deck para desconectar da fonte remota
    3. Remover a configuração de sincronização automática
    
    O deck local permanece intacto no Anki após a remoção.
    """
    config = get_addon_config()

    remoteDecks = config["remote-decks"]

    # Verificar se há decks remotos configurados
    if not remoteDecks:
        showInfo("There are currently no remote decks configured.")
        return

    # Obter informações de todos os decks e suas URLs
    deck_info, deck_map = _build_deck_info_for_removal(remoteDecks)

    # Solicitar seleção do usuário
    selection, okPressed = QInputDialog.getItem(
        mw,
        "Select a Deck to Unlink",
        "Select a deck to unlink from remote source:\n(The local deck will remain in Anki)",
        deck_info,
        0,
        False
    )

    if okPressed and selection:
        try:
            _process_deck_removal(selection, deck_map, remoteDecks, config)
        except Exception as e:
            showInfo(f"Error unlinking deck: {str(e)}")
            return

def _build_deck_info_for_removal(remoteDecks):
    """
    Constrói informações dos decks para interface de remoção.
    
    Args:
        remoteDecks: Dicionário de decks remotos da configuração
        
    Returns:
        tuple: (deck_info, deck_map) onde deck_info é lista de strings para exibição
               e deck_map mapeia strings de exibição para URLs
    """
    deck_info = []
    deck_map = {}  # Mapear strings de exibição para chaves de URL
    
    for url, info in remoteDecks.items():
        deck_id = info["deck_id"]
        # Verificar se o deck ainda existe no Anki
        deck = mw.col.decks.get(deck_id)
        if deck:
            deck_name = deck["name"]
            status = "Available"
        else:
            deck_name = f"Unknown (ID: {deck_id})"
            status = "Not found in Anki"
            
        display_str = f"{deck_name} ({status})"
        deck_info.append(display_str)
        deck_map[display_str] = url
    
    return deck_info, deck_map

def _process_deck_removal(selection, deck_map, remoteDecks, config):
    """
    Processa a remoção de um deck da configuração.
    
    Args:
        selection: String de seleção do usuário
        deck_map: Mapeamento de seleções para URLs
        remoteDecks: Dicionário de decks remotos
        config: Configuração do addon
    """
    # Obter URL da seleção usando nosso mapeamento
    url = deck_map[selection]
    
    # Obter nome do deck para exibição
    deck_id = remoteDecks[url]["deck_id"]
    deck = mw.col.decks.get(deck_id)
    deck_name = deck["name"] if deck else f"Unknown (ID: {deck_id})"
    
    # Remover o deck da configuração
    del remoteDecks[url]

    # Salvar a configuração atualizada
    save_addon_config(config)

    # Mostrar mensagem de sucesso com instruções
    message = (
        f"The deck '{deck_name}' has been unlinked from its remote source.\n\n"
        f"The local deck remains in Anki and can now be managed normally.\n"
        f"Future updates from the Google Sheet will no longer affect this deck."
    )
    showInfo(message)