"""
Gerenciamento de decks para o addon Sheets2Anki.

Este módulo contém funções para adicionar, remover e gerenciar
decks remotos no Anki.
"""

from .compat import (
    mw, showInfo, QInputDialog, EchoModeNormal,
    DialogAccepted
)
from .constants import TEST_SHEETS_URLS
from .config import get_addon_config, save_addon_config
from .validation import validate_url
from .utils import get_or_create_deck
from .parseRemoteDeck import getRemoteDeck
from .exceptions import SyncError
from .sync import syncDecks
from .dialogs import DeckSelectionDialog

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
    
    Nota: Apenas o deck de teste importado será sincronizado, não afetando
    outros decks previamente configurados.
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
        # Sincronizar apenas o deck de teste recém-importado usando sua URL
        syncDecks(selected_deck_urls=[url])
    except SyncError as e:
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

def addNewDeck():
    """
    Adiciona um novo deck remoto a partir de uma URL TSV do Google Sheets.
    
    Esta função permite ao usuário:
    1. Inserir uma URL de planilha publicada em formato TSV
    2. Validar a URL
    3. Definir um nome para o deck
    4. Configurar e iniciar a sincronização apenas do novo deck
    
    Nota: Apenas o deck recém-cadastrado será sincronizado, não afetando
    outros decks previamente configurados.
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
    except Exception as e:
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

    # Salvar configuração e sincronizar apenas o novo deck
    try:
        config["remote-decks"][url] = {
            "url": url,
            "deck_id": deck_id,
            "deck_name": deckName
        }
        save_addon_config(config)
        # Sincronizar apenas o deck recém-cadastrado usando sua URL
        syncDecks(selected_deck_urls=[url])
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
