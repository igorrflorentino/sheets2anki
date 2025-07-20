"""
Gerenciamento de decks para o addon Sheets2Anki.

Este módulo contém funções para adicionar, remover e gerenciar
decks remotos no Anki com suporte a nomeação automática e
desconexão de decks.
"""

from .compat import (
    mw, showInfo, QInputDialog,
    DialogAccepted
)
from .fix_exec import safe_exec
from .constants import TEST_SHEETS_URLS
from .config_manager import (
    get_remote_decks, add_remote_deck, disconnect_deck, detect_deck_name_changes
)
from .validation import validate_url
from .utils import get_or_create_deck
from .parseRemoteDeck import getRemoteDeck
from .exceptions import SyncError
from .sync import syncDecks
from .dialogs import DeckSelectionDialog
from .add_deck_dialog import show_add_deck_dialog
from .sync_dialog import show_sync_dialog
from .disconnect_dialog import show_disconnect_dialog
from .deck_naming_dialog import show_deck_naming_dialog
from .deck_naming import DeckNamer

def syncDecksWithSelection():
    """
    Mostra interface para selecionar decks e sincroniza apenas os selecionados.
    
    Esta função é o ponto de entrada principal para sincronização interativa.
    Utiliza o novo sistema de configuração e permite reconexão de decks desconectados.
    
    Nota: Os nomes dos decks só serão atualizados quando o usuário clicar em 'sincronizar selecionados'.
    """
    # Usar o novo diálogo de sincronização sem verificar mudanças nos nomes dos decks
    # para evitar notificações indesejadas
    success, selected_urls = show_sync_dialog(mw)
    
    if success and selected_urls:
        # Sincronizar apenas os decks selecionados
        # As atualizações de nomes serão feitas silenciosamente durante a sincronização
        syncDecks(selected_deck_urls=selected_urls)
    elif not selected_urls:
        showInfo("Nenhum deck selecionado para sincronização.")
    
    return

def check_and_update_deck_names(silent=False):
    """
    Verifica e atualiza os nomes dos decks na configuração.
    
    Esta função deve ser chamada regularmente para garantir que
    a configuração sempre reflita os nomes atuais dos decks.
    
    Nota: Decks deletados não são atualizados automaticamente.
    
    Args:
        silent (bool): Se True, não mostra notificações
        
    Returns:
        list: Lista de URLs dos decks que foram atualizados
    """
    try:
        updated_urls = detect_deck_name_changes(skip_deleted=True)
        
        if updated_urls and not silent:
            # Mostrar informação sobre as atualizações apenas se não estiver em modo silencioso
            deck_names = []
            remote_decks = get_remote_decks()
            
            for url in updated_urls:
                deck_info = remote_decks.get(url, {})
                deck_name = deck_info.get("deck_name", "Deck")
                deck_names.append(deck_name)
            
            if len(deck_names) == 1:
                showInfo(f"Nome do deck '{deck_names[0]}' foi atualizado na configuração.")
            else:
                names_str = "', '".join(deck_names)
                showInfo(f"Nomes dos decks '{names_str}' foram atualizados na configuração.")
        
        return updated_urls
    except Exception as e:
        if not silent:
            showInfo(f"Erro ao verificar nomes dos decks: {str(e)}")
        return []

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
    
    for url, deck_info in get_remote_decks().items():
        deck_id = deck_info["deck_id"]
        # Verificar se a coleção e o gerenciador de decks estão disponíveis
        if mw and mw.col and mw.col.decks:
            deck = mw.col.decks.get(deck_id)
            
            # Verificar se o deck ainda existe e não é o deck padrão
            if deck and deck["name"].strip().lower() != "default":
                deck_name = deck["name"]
                # Contar cards no deck (verificando se find_cards está disponível)
                if mw.col.find_cards:
                    card_count = len(mw.col.find_cards(f'deck:"{deck_name}"'))
                else:
                    card_count = 0  # Fallback se find_cards não estiver disponível
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
    
    # Usar função de compatibilidade para exec/exec_
    result = safe_exec(dialog)
    
    if result == DialogAccepted:
        selected_decks = dialog.get_selected_decks()
        if selected_decks:
            syncDecks(selected_decks)
        else:
            showInfo("Nenhum deck foi selecionado para sincronização.")

def import_test_deck():
    """
    Importa um deck de teste para desenvolvimento e demonstração.
    
    Esta função permite selecionar entre diferentes planilhas de teste
    pré-configuradas e usar o sistema de nomeação automática.
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

    # Gerar nome automático para o deck
    deck_name = DeckNamer.get_available_name(url)
    
    # Verificar se URL já está configurada
    remote_decks = get_remote_decks()
    if url in remote_decks:
        showInfo(f"Este deck de teste já está configurado como '{remote_decks[url]['deck_name']}'.")
        return

    try:
        # Criar deck no Anki
        deck_id, actual_name = get_or_create_deck(mw.col, deck_name)
        
        # Adicionar à configuração
        deck_info = {
            "url": url,
            "deck_id": deck_id,
            "deck_name": actual_name,  # Usar o nome real usado pelo Anki
            "is_test_deck": True
        }
        
        add_remote_deck(url, deck_info)
        
        # Sincronizar o deck
        syncDecks(selected_deck_urls=[url])
        
        # Obter o nome final do deck após a sincronização (pode ter sido alterado)
        remote_decks = get_remote_decks()
        if url in remote_decks:
            final_deck_name = remote_decks[url].get("deck_name", actual_name)
        else:
            final_deck_name = actual_name
            
        showInfo(f"Deck de teste '{final_deck_name}' importado e sincronizado com sucesso!")
        
    except Exception as e:
        showInfo(f"Erro ao importar deck de teste:\n{str(e)}")
        return

def addNewDeck():
    """
    Adiciona um novo deck remoto usando o novo sistema de configuração.
    
    Esta função utiliza o diálogo aprimorado que suporta nomeação automática,
    resolução de conflitos e reconexão de decks desconectados.
    """
    # Usar o novo diálogo de adicionar deck
    success, deck_info = show_add_deck_dialog(mw)
    
    if success and deck_info:
        # Sincronizar apenas o deck recém-adicionado
        url = deck_info["url"]
        syncDecks(selected_deck_urls=[url])
        
        # Obter o nome final do deck após a sincronização (pode ter sido alterado)
        from .config_manager import get_remote_decks
        remote_decks = get_remote_decks()
        if url in remote_decks:
            final_deck_name = remote_decks[url].get("deck_name", deck_info['name'])
        else:
            final_deck_name = deck_info['name']
            
        showInfo(f"Deck '{final_deck_name}' adicionado e sincronizado com sucesso!")

def configure_deck_naming():
    """
    Mostra o diálogo para configurar as preferências de nomeação de decks.
    
    Esta função permite ao usuário escolher entre nomeação automática e manual,
    além de configurar o nome do deck pai para hierarquias.
    """
    success = show_deck_naming_dialog(mw)
    
    if success:
        from .config_manager import get_deck_naming_mode
        mode = get_deck_naming_mode()
        
        if mode == "automatic":
            showInfo("Configuração salva! Novos decks usarão nomeação automática com hierarquia.")
        else:
            showInfo("Configuração salva! Novos decks usarão nomeação manual.")
    else:
        showInfo("Configuração cancelada. Nenhuma alteração foi feita.")

def removeRemoteDeck():
    """
    Remove decks remotos da configuração usando interface com checkboxes.
    
    Esta função utiliza o novo diálogo de desconexão que permite selecionar
    múltiplos decks para desconexão simultânea, mantendo os decks locais.
    """
    # Usar o novo diálogo de desconexão
    success, selected_urls = show_disconnect_dialog(mw)
    
    if success and selected_urls:
        # Processar desconexão dos decks selecionados
        disconnected_decks = []
        
        for url in selected_urls:
            # Obter informações do deck antes de desconectar
            remote_decks = get_remote_decks()
            if url in remote_decks:
                deck_info = remote_decks[url]
                deck_id = deck_info["deck_id"]
                deck = None
                # Verificar se a coleção e o gerenciador de decks estão disponíveis
                if mw and mw.col and mw.col.decks:
                    deck = mw.col.decks.get(deck_id)
                deck_name = deck["name"] if deck else deck_info.get("deck_name", "Deck Desconhecido")
                
                # Desconectar o deck
                disconnect_deck(url)
                disconnected_decks.append(deck_name)
        
        # Mostrar mensagem de sucesso
        if len(disconnected_decks) == 1:
            message = (
                f"O deck '{disconnected_decks[0]}' foi desconectado de sua fonte remota.\n\n"
                f"O deck local permanece no Anki e pode ser gerenciado normalmente.\n"
                f"Para reconectar, você precisará adicioná-lo novamente."
            )
        else:
            decks_list = "', '".join(disconnected_decks)
            message = (
                f"Os decks '{decks_list}' foram desconectados de suas fontes remotas.\n\n"
                f"Os decks locais permanecem no Anki e podem ser gerenciados normalmente.\n"
                f"Para reconectar, você precisará adicioná-los novamente."
            )
        
        showInfo(message)
    elif not selected_urls:
        showInfo("Nenhum deck selecionado para desconexão.")
    
    return
