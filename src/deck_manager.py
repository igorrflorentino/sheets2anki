"""
Gerenciamento de decks para o addon Sheets2Anki.

Este módulo contém funções para adicionar, remover e gerenciar
decks remotos no Anki com suporte a nomeação automática e
desconexão de decks, incluindo gerenciamento de alunos.
"""

from .compat import (
    mw, showInfo, QInputDialog,
    DialogAccepted
)
from .fix_exec import safe_exec
from .constants import TEST_SHEETS_URLS
from .config_manager import (
    get_remote_decks, add_remote_deck, disconnect_deck, detect_deck_name_changes,
    get_deck_local_name, create_deck_info
)
from .deck_naming import DeckNamer
from .validation import validate_url
from .utils import get_or_create_deck
from .parseRemoteDeck import getRemoteDeck
from .exceptions import SyncError
from .sync import syncDecks
from .dialogs import DeckSelectionDialog
from .add_deck_dialog import show_add_deck_dialog
from .sync_dialog import show_sync_dialog
from .disconnect_dialog import show_disconnect_dialog
from .deck_naming import DeckNamer


def _delete_local_deck_data(deck_id, deck_name, url):
    """
    Deleta completamente os dados locais de um deck (deck, cards, notas e note types).
    
    Args:
        deck_id: ID do deck no Anki
        deck_name: Nome do deck para logs
        url: URL do deck remoto para identificação de note types
    """
    if not mw or not mw.col:
        return
    
    try:
        from .config_manager import get_deck_note_type_ids, get_deck_remote_name
        
        # Obter note types configurados para este deck
        note_types_config = get_deck_note_type_ids(url)
        remote_deck_name = get_deck_remote_name(url) or "RemoteDeck"
        print(f"[DEBUG] URL: {url}")
        print(f"[DEBUG] Remote deck name: {remote_deck_name}")
        print(f"[DEBUG] Configured note types: {note_types_config}")
        
        # 1. Identificar note types específicos deste deck baseado na configuração
        models_to_delete = []
        for note_type_id_str, note_type_name in note_types_config.items():
            try:
                note_type_id = int(note_type_id_str)
                model = mw.col.models.get(note_type_id)
                
                if not model:
                    print(f"[DEBUG] Note type ID {note_type_id} não encontrado no Anki")
                    continue
                    
                model_name = model['name']
                print(f"[DEBUG] Found note type: {model_name} (ID: {note_type_id})")
                
                # Verificar se o note type é usado apenas por este deck
                notes_with_model = mw.col.find_notes(f'note:"{model_name}"')
                print(f"[DEBUG] Notes with model '{model_name}': {len(notes_with_model)}")
                
                # Se há notas, verificar se são apenas deste deck
                if notes_with_model:
                    cards_from_other_decks = []
                    for note_id in notes_with_model:
                        card_ids = mw.col.card_ids_of_note(note_id)
                        for card_id in card_ids:
                            card = mw.col.get_card(card_id)
                            if card.did != deck_id:  # Card de outro deck
                                cards_from_other_decks.append(card_id)
                    
                    # Se não há cartas de outros decks, pode deletar o note type
                    if not cards_from_other_decks:
                        models_to_delete.append(model)
                        print(f"[DEBUG] Note type '{model_name}' marcado para deleção")
                    else:
                        print(f"[DEBUG] Note type '{model_name}' usado em outros decks, mantendo")
                else:
                    # Nenhuma nota usando este model, pode deletar
                    models_to_delete.append(model)
                    print(f"[DEBUG] Note type '{model_name}' sem notas, marcado para deleção")
                    
            except Exception as e:
                print(f"[DEBUG] Erro ao verificar note type {note_type_id_str}: {e}")
        
        # 2. Deletar todas as notas do deck
        card_ids = mw.col.find_cards(f'deck:"{deck_name}"')
        print(f"[DEBUG] Cards encontrados para deletar: {len(card_ids)}")
        if card_ids:
            mw.col.remove_cards_and_orphaned_notes(card_ids)
        
        # 3. Deletar o deck (isso remove automaticamente subdecks)
        if mw.col.decks.get(deck_id):
            mw.col.decks.rem(deck_id, cardsToo=True)  # cardsToo=True força remoção de cards restantes
            print(f"[DEBUG] Deck {deck_name} deletado")
        
        # 4. Agora deletar os note types identificados
        for model in models_to_delete:
            try:
                mw.col.models.rem(model)
                print(f"[DEBUG] Note type '{model['name']}' deletado com sucesso")
            except Exception as e:
                print(f"[DEBUG] Erro ao deletar note type '{model['name']}': {e}")
        
        # 5. Forçar salvar e atualizar a interface
        mw.col.save()
        if hasattr(mw, 'deckBrowser'):
            mw.deckBrowser.refresh()
        if hasattr(mw, 'reset'):
            mw.reset()  # Força reload completo da interface
        
        print(f"[DEBUG] Deleção completa do deck '{deck_name}' finalizada")
        
    except Exception as e:
        # Em caso de erro, continuar mas reportar
        print(f"Erro ao deletar dados locais do deck '{deck_name}': {str(e)}")
        import traceback
        traceback.print_exc()


def _force_delete_note_types_by_suffix(suffix, remote_deck_name=None, url=None):
    """
    Força a deleção de note types usando IDs armazenados (preferido) ou padrões de nome.
    Usado como fallback se a deleção segura falhar.
    
    Args:
        suffix (str): Sufixo do hash da URL
        remote_deck_name (str, optional): Nome do deck remoto para busca específica
        url (str, optional): URL para extrair informações adicionais
    """
    if not mw or not mw.col:
        return
    
    try:
        # Primeiro, tentar deletar usando IDs armazenados se temos a URL
        if url:
            from .utils import delete_deck_note_types_by_ids
            deleted_by_ids = delete_deck_note_types_by_ids(url)
            
            if deleted_by_ids > 0:
                print(f"[FORCE DELETE] Deletados {deleted_by_ids} note types usando IDs armazenados")
                # Forçar salvar e reset
                mw.col.save()
                if hasattr(mw, 'reset'):
                    mw.reset()
                return
            
            print(f"[FORCE DELETE] Nenhum note type encontrado via IDs, tentando método direto...")
        
        # Fallback: buscar note types diretamente no Anki baseado no nome do deck remoto
        from .config_manager import get_deck_remote_name
        
        if not remote_deck_name and url:
            remote_deck_name = get_deck_remote_name(url) or "RemoteDeck"
        
        print(f"[FORCE DELETE] Buscando note types para deck remoto: '{remote_deck_name}'")
        
        models_to_delete = []
        for model in mw.col.models.all():
            model_name = model['name']
            
            # Verificar se é um note type do Sheets2Anki e contém o nome do deck remoto
            if (model_name.startswith("Sheets2Anki - ") and 
                remote_deck_name and remote_deck_name in model_name):
                models_to_delete.append(model)
                print(f"[FORCE DELETE] Forçando deleção do note type: {model_name}")
        
        # Deletar os note types encontrados
        for model in models_to_delete:
            try:
                mw.col.models.rem(model)
                print(f"[FORCE DELETE] Note type '{model['name']}' deletado com sucesso")
            except Exception as e:
                print(f"[FORCE DELETE] Erro ao deletar note type '{model['name']}': {e}")
        
        # Forçar salvar
        mw.col.save()
        if hasattr(mw, 'reset'):
            mw.reset()
            
    except Exception as e:
        print(f"[FORCE DELETE] Erro na deleção forçada: {e}")


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
                # Usar local_deck_name da nova estrutura, com fallback para deck_name antigo
                deck_name = get_deck_local_name(url) or "Deck"
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
        local_name = get_deck_local_name(url) or "Deck"
        showInfo(f"Este deck de teste já está configurado como '{local_name}'.")
        return

    try:
        # Criar deck no Anki
        deck_id, actual_name = get_or_create_deck(mw.col, deck_name)
        
        # Extrair nome remoto da URL
        remote_deck_name = DeckNamer.extract_remote_name_from_url(url)
        
        # Adicionar à configuração usando a nova estrutura modular
        deck_info = create_deck_info(
            url=url,
            local_deck_id=deck_id,
            local_deck_name=actual_name,
            remote_deck_name=remote_deck_name,
            is_test_deck=True
        )
        
        add_remote_deck(url, deck_info)
        
        # Sincronizar o deck
        syncDecks(selected_deck_urls=[url])
        
        # Obter o nome final do deck após a sincronização (pode ter sido alterado)
        remote_decks = get_remote_decks()
        if url in remote_decks:
            final_deck_name = get_deck_local_name(url) or actual_name
        else:
            final_deck_name = actual_name
        
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
            final_deck_name = get_deck_local_name(url) or deck_info['name']
        else:
            final_deck_name = deck_info['name']

def removeRemoteDeck():
    """
    Remove decks remotos da configuração usando interface com checkboxes.
    
    Esta função utiliza o novo diálogo de desconexão que permite selecionar
    múltiplos decks para desconexão simultânea, mantendo os decks locais.
    """
    # Usar o novo diálogo de desconexão
    success, selected_urls, delete_local_data = show_disconnect_dialog(mw)
    
    if success and selected_urls:
        # Processar desconexão dos decks selecionados
        disconnected_decks = []
        
        for url in selected_urls:
            # Obter informações do deck antes de desconectar
            from .utils import get_publication_key_hash
            
            # Gerar hash da chave de publicação
            url_hash = get_publication_key_hash(url)
            
            remote_decks = get_remote_decks()
            if url_hash in remote_decks:
                deck_info = remote_decks[url_hash]
                deck_id = deck_info["local_deck_id"]
                deck = None
                # Verificar se a coleção e o gerenciador de decks estão disponíveis
                if mw and mw.col and mw.col.decks:
                    deck = mw.col.decks.get(deck_id)
                deck_name = deck["name"] if deck else (get_deck_local_name(url) or "Deck Desconhecido")
                
                # Se deve deletar dados locais, fazê-lo antes da desconexão
                if delete_local_data and deck:
                    _delete_local_deck_data(deck_id, deck_name, url)
                    
                    # Fallback: tentar deleção forçada dos note types
                    try:
                        from .utils import get_model_suffix_from_url
                        from .config_manager import get_deck_remote_name
                        
                        suffix = get_model_suffix_from_url(url)
                        remote_deck_name = get_deck_remote_name(url)
                        _force_delete_note_types_by_suffix(suffix, remote_deck_name, url)
                    except Exception as fallback_error:
                        print(f"[DEBUG] Fallback também falhou: {fallback_error}")
                
                # Desconectar o deck
                disconnect_deck(url)
                disconnected_decks.append(deck_name)
        
        # Mostrar mensagem de sucesso
        if len(disconnected_decks) == 1:
            if delete_local_data:
                message = (
                    f"O deck '{disconnected_decks[0]}' foi desconectado e todos os dados locais foram deletados.\n\n"
                    f"Dados deletados:\n"
                    f"• Deck local e subdecks\n"
                    f"• Todas as cartas e notas\n"
                    f"• Note types específicos (se não usados em outros decks)\n\n"
                    f"Para reconectar, você precisará adicioná-lo novamente."
                )
            else:
                message = (
                    f"O deck '{disconnected_decks[0]}' foi desconectado de sua fonte remota.\n\n"
                    f"O deck local permanece no Anki e pode ser gerenciado normalmente.\n"
                    f"Para reconectar, você precisará adicioná-lo novamente."
                )
        else:
            decks_list = "', '".join(disconnected_decks)
            if delete_local_data:
                message = (
                    f"Os decks '{decks_list}' foram desconectados e todos os dados locais foram deletados.\n\n"
                    f"Dados deletados para cada deck:\n"
                    f"• Decks locais e subdecks\n"
                    f"• Todas as cartas e notas\n"
                    f"• Note types específicos (se não usados em outros decks)\n\n"
                    f"Para reconectar, você precisará adicioná-los novamente."
                )
            else:
                message = (
                    f"Os decks '{decks_list}' foram desconectados de suas fontes remotas.\n\n"
                    f"Os decks locais permanecem no Anki e podem ser gerenciados normalmente.\n"
                    f"Para reconectar, você precisará adicioná-los novamente."
                )
        
        showInfo(message)
    
    return


def manage_deck_students():
    """
    Permite ao usuário gerenciar quais alunos deseja sincronizar para cada deck remoto.
    """
    from .student_manager import (
        extract_students_from_remote_data, 
        get_selected_students_for_deck,
        show_student_selection_dialog
    )
    
    remote_decks = get_remote_decks()
    
    if not remote_decks:
        showInfo("Nenhum deck remoto configurado. Adicione um deck primeiro.")
        return
    
    # Criar lista de opções para o usuário selecionar um deck
    deck_options = []
    deck_urls = []
    
    for url, deck_info in remote_decks.items():
        try:
            deck_name = get_deck_local_name(url) or "Deck sem nome"
            deck_options.append(f"{deck_name} ({url[:50]}...)")
            deck_urls.append(url)
        except Exception as e:
            deck_options.append(f"Deck com erro ({url[:50]}...)")
            deck_urls.append(url)
    
    # Mostrar dialog de seleção de deck
    from .compat import QInputDialog
    
    deck_choice, ok = QInputDialog.getItem(
        None,
        "Gerenciar Alunos - Selecionar Deck",
        "Selecione o deck para gerenciar alunos:",
        deck_options,
        0,
        False
    )
    
    if not ok:
        return
    
    # Obter URL do deck selecionado
    deck_index = deck_options.index(deck_choice)
    selected_url = deck_urls[deck_index]
    
    try:
        # Baixar dados remotos para extrair alunos
        showInfo("Baixando dados da planilha para obter lista de alunos...")
        
        remote_deck = getRemoteDeck(selected_url)
        available_students = extract_students_from_remote_data(remote_deck)
        
        if not available_students:
            showInfo("Não foram encontrados alunos na coluna ALUNOS desta planilha.\n\n"
                    "Certifique-se de que a planilha contém a coluna ALUNOS com nomes de alunos.")
            return
        
        # Mostrar dialog de seleção de alunos
        selected_students = show_student_selection_dialog(selected_url, available_students)
        
        if selected_students is not None:
            deck_name = get_deck_local_name(selected_url) or "Deck remoto"
            selected_count = len(selected_students)
            total_count = len(available_students)
            
            if selected_count == 0:
                showInfo(f"Nenhum aluno foi selecionado para o deck '{deck_name}'.\n\n"
                        "Nenhuma nota será sincronizada para este deck até que você selecione ao menos um aluno.")
            else:
                alunos_list = ", ".join(sorted(selected_students))
                showInfo(f"Configuração salva para o deck '{deck_name}'!\n\n"
                        f"Alunos selecionados ({selected_count} de {total_count}):\n{alunos_list}\n\n"
                        "Na próxima sincronização, apenas as notas dos alunos selecionados serão incluídas.")
        
    except Exception as e:
        showInfo(f"Erro ao gerenciar alunos: {str(e)}\n\n"
                "Verifique se a URL do deck está correta e se a planilha está acessível.")


def reset_student_selection():
    """
    Remove a seleção de alunos de todos os decks, voltando ao comportamento padrão.
    """
    from .compat import QMessageBox, MessageBox_Yes, MessageBox_No
    
    remote_decks = get_remote_decks()
    
    if not remote_decks:
        showInfo("Nenhum deck remoto configurado.")
        return
    
    # Confirmar com o usuário
    reply = QMessageBox.question(
        None,
        "Resetar Seleção de Alunos",
        "Tem certeza de que deseja remover a seleção de alunos de todos os decks?\n\n"
        "Isso fará com que todos os decks voltem ao comportamento padrão "
        "(sincronizar todas as notas independentemente da coluna ALUNOS).",
        MessageBox_Yes | MessageBox_No,
        MessageBox_No
    )
    
    if reply != MessageBox_Yes:
        return
    
    try:
        from .config_manager import get_meta, save_meta
        
        meta = get_meta()
        removed_count = 0
        
        # Remover student_selection de todos os decks
        if 'decks' in meta:
            for deck_url in meta['decks']:
                if 'student_selection' in meta['decks'][deck_url]:
                    del meta['decks'][deck_url]['student_selection']
                    removed_count += 1
        
        save_meta(meta)
        
        if removed_count > 0:
            showInfo(f"Seleção de alunos removida de {removed_count} deck(s).\n\n"
                    "Todos os decks agora voltarão ao comportamento padrão na próxima sincronização.")
        else:
            showInfo("Nenhuma seleção de alunos foi encontrada para remover.")
    
    except Exception as e:
        showInfo(f"Erro ao resetar seleção de alunos: {str(e)}")

