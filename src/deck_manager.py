"""
Gerenciamento de decks para o addon Sheets2Anki.

Este módulo contém funções para adicionar, remover e gerenciar
decks remotos no Anki com suporte a nomeação automática e
desconexão de decks, incluindo gerenciamento de alunos.
"""

from .add_deck_dialog import show_add_deck_dialog
from .compat import DialogAccepted
from .compat import QCheckBox
from .compat import QDialog
from .compat import QHBoxLayout
from .compat import QInputDialog
from .compat import QLabel
from .compat import QPushButton
from .compat import QVBoxLayout
from .compat import mw
from .compat import safe_exec
from .compat import showInfo
from .config_manager import add_remote_deck
from .config_manager import create_deck_info
from .config_manager import detect_deck_name_changes
from .config_manager import disconnect_deck
from .config_manager import get_deck_local_name
from .config_manager import get_remote_decks
from .data_processor import getRemoteDeck
from .disconnect_dialog import show_disconnect_dialog
from .sync_dialog import show_sync_dialog
from .templates_and_definitions import TEST_SHEETS_URLS
from .utils import get_or_create_deck


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
        from .config_manager import get_deck_note_type_ids
        from .config_manager import get_deck_remote_name

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
                from anki.models import NotetypeId

                model = mw.col.models.get(NotetypeId(note_type_id))

                if not model:
                    print(f"[DEBUG] Note type ID {note_type_id} não encontrado no Anki")
                    continue

                model_name = model["name"]
                print(f"[DEBUG] Found note type: {model_name} (ID: {note_type_id})")

                # Verificar se o note type é usado apenas por este deck
                notes_with_model = mw.col.find_notes(f'note:"{model_name}"')
                print(
                    f"[DEBUG] Notes with model '{model_name}': {len(notes_with_model)}"
                )

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
                        print(
                            f"[DEBUG] Note type '{model_name}' usado em outros decks, mantendo"
                        )
                else:
                    # Nenhuma nota usando este model, pode deletar
                    models_to_delete.append(model)
                    print(
                        f"[DEBUG] Note type '{model_name}' sem notas, marcado para deleção"
                    )

            except Exception as e:
                print(f"[DEBUG] Erro ao verificar note type {note_type_id_str}: {e}")

        # 2. Deletar todas as notas do deck
        card_ids = mw.col.find_cards(f'deck:"{deck_name}"')
        print(f"[DEBUG] Cards encontrados para deletar: {len(card_ids)}")
        if card_ids:
            mw.col.remove_cards_and_orphaned_notes(card_ids)

        # 3. Deletar o deck (isso remove automaticamente subdecks)
        if mw.col.decks.get(deck_id):
            mw.col.decks.rem(
                deck_id, cardsToo=True
            )  # cardsToo=True força remoção de cards restantes
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
        if hasattr(mw, "deckBrowser"):
            mw.deckBrowser.refresh()
        if hasattr(mw, "reset"):
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
                print(
                    f"[FORCE DELETE] Deletados {deleted_by_ids} note types usando IDs armazenados"
                )
                # Forçar salvar e reset
                mw.col.save()
                if hasattr(mw, "reset"):
                    mw.reset()
                return

            print(
                "[FORCE DELETE] Nenhum note type encontrado via IDs, tentando método direto..."
            )

        # Fallback: buscar note types diretamente no Anki baseado no nome do deck remoto
        from .config_manager import get_deck_remote_name

        if not remote_deck_name and url:
            remote_deck_name = get_deck_remote_name(url) or "RemoteDeck"

        print(
            f"[FORCE DELETE] Buscando note types para deck remoto: '{remote_deck_name}'"
        )

        models_to_delete = []
        for model in mw.col.models.all():
            model_name = model["name"]

            # Verificar se é um note type do Sheets2Anki e contém o nome do deck remoto
            if (
                model_name.startswith("Sheets2Anki - ")
                and remote_deck_name
                and remote_deck_name in model_name
            ):
                models_to_delete.append(model)
                print(f"[FORCE DELETE] Forçando deleção do note type: {model_name}")

        # Deletar os note types encontrados
        for model in models_to_delete:
            try:
                mw.col.models.rem(model)
                print(
                    f"[FORCE DELETE] Note type '{model['name']}' deletado com sucesso"
                )
            except Exception as e:
                print(
                    f"[FORCE DELETE] Erro ao deletar note type '{model['name']}': {e}"
                )

        # Forçar salvar
        mw.col.save()
        if hasattr(mw, "reset"):
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
        from .sync import syncDecks

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
                showInfo(
                    f"Nome do deck '{deck_names[0]}' foi atualizado na configuração."
                )
            else:
                names_str = "', '".join(deck_names)
                showInfo(
                    f"Nomes dos decks '{names_str}' foram atualizados na configuração."
                )

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
            from .sync import syncDecks

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
        False,
    )

    if not okPressed or not selection:
        return

    # Buscar a URL correspondente ao deck selecionado
    url = dict(TEST_SHEETS_URLS)[selection]

    # Gerar nome automático para o deck usando DeckNameManager
    remote_name = DeckNameManager.extract_remote_name_from_url(url)
    deck_name = DeckNameManager.generate_local_name(remote_name)

    # Verificar se URL já está configurada
    remote_decks = get_remote_decks()
    if url in remote_decks:
        local_name = get_deck_local_name(url) or "Deck"
        showInfo(f"Este deck de teste já está configurado como '{local_name}'.")
        return

    try:
        # Criar deck no Anki
        deck_id, actual_name = get_or_create_deck(mw.col, deck_name)

        # Extrair nome remoto da URL usando DeckNameManager
        remote_deck_name = DeckNameManager.extract_remote_name_from_url(url)

        # Adicionar à configuração usando a nova estrutura modular
        deck_info = create_deck_info(
            url=url,
            local_deck_id=deck_id,
            local_deck_name=actual_name,
            remote_deck_name=remote_deck_name,
            is_test_deck=True,
        )

        add_remote_deck(url, deck_info)

        # Sincronizar o deck
        from .sync import syncDecks

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
        from .sync import syncDecks

        syncDecks(selected_deck_urls=[url])

        # Obter o nome final do deck após a sincronização (pode ter sido alterado)
        from .config_manager import get_remote_decks

        remote_decks = get_remote_decks()
        if url in remote_decks:
            final_deck_name = get_deck_local_name(url) or deck_info["name"]
        else:
            final_deck_name = deck_info["name"]


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
                deck_name = (
                    deck["name"]
                    if deck
                    else (get_deck_local_name(url) or "Deck Desconhecido")
                )

                # Se deve deletar dados locais, fazê-lo antes da desconexão
                if delete_local_data and deck:
                    _delete_local_deck_data(deck_id, deck_name, url)

                    # Fallback: tentar deleção forçada dos note types
                    try:
                        from .config_manager import get_deck_remote_name
                        from .utils import get_model_suffix_from_url

                        suffix = get_model_suffix_from_url(url)
                        remote_deck_name = get_deck_remote_name(url)
                        _force_delete_note_types_by_suffix(
                            suffix, remote_deck_name, url
                        )
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
    from .student_manager import extract_students_from_remote_data
    from .student_manager import show_student_selection_dialog

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
        except Exception:
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
        False,
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
            showInfo(
                "Não foram encontrados alunos na coluna ALUNOS desta planilha.\n\n"
                "Certifique-se de que a planilha contém a coluna ALUNOS com nomes de alunos."
            )
            return

        # Mostrar dialog de seleção de alunos
        selected_students = show_student_selection_dialog(
            selected_url, available_students
        )

        if selected_students is not None:
            deck_name = get_deck_local_name(selected_url) or "Deck remoto"
            selected_count = len(selected_students)
            total_count = len(available_students)

            if selected_count == 0:
                showInfo(
                    f"Nenhum aluno foi selecionado para o deck '{deck_name}'.\n\n"
                    "Nenhuma nota será sincronizada para este deck até que você selecione ao menos um aluno."
                )
            else:
                alunos_list = ", ".join(sorted(selected_students))
                showInfo(
                    f"Configuração salva para o deck '{deck_name}'!\n\n"
                    f"Alunos selecionados ({selected_count} de {total_count}):\n{alunos_list}\n\n"
                    "Na próxima sincronização, apenas as notas dos alunos selecionados serão incluídas."
                )

    except Exception as e:
        showInfo(
            f"Erro ao gerenciar alunos: {str(e)}\n\n"
            "Verifique se a URL do deck está correta e se a planilha está acessível."
        )


def reset_student_selection():
    """
    Remove a seleção de alunos de todos os decks, voltando ao comportamento padrão.
    """
    from .compat import MessageBox_No
    from .compat import MessageBox_Yes
    from .compat import QMessageBox

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
        MessageBox_No,
    )

    if reply != MessageBox_Yes:
        return

    try:
        from .config_manager import get_meta
        from .config_manager import save_meta

        meta = get_meta()
        removed_count = 0

        # Remover student_selection de todos os decks
        if "decks" in meta:
            for deck_url in meta["decks"]:
                if "student_selection" in meta["decks"][deck_url]:
                    del meta["decks"][deck_url]["student_selection"]
                    removed_count += 1

        save_meta(meta)

        if removed_count > 0:
            showInfo(
                f"Seleção de alunos removida de {removed_count} deck(s).\n\n"
                "Todos os decks agora voltarão ao comportamento padrão na próxima sincronização."
            )
        else:
            showInfo("Nenhuma seleção de alunos foi encontrada para remover.")

    except Exception as e:
        showInfo(f"Erro ao resetar seleção de alunos: {str(e)}")


# =============================================================================
# GERENCIAMENTO DE NOMES DE DECKS (antigo deck_name_manager.py)
# =============================================================================

import re
from typing import Any
from typing import Dict
from typing import Optional
from typing import Tuple

from .templates_and_definitions import DEFAULT_PARENT_DECK_NAME


class DeckNameManager:
    """
    Classe centralizada para gerenciar todos os aspectos da nomeação de decks.

    Esta classe unifica e substitui toda a lógica dispersa de:
    - Extração de nomes de URLs
    - Resolução de conflitos
    - Sincronização com configuração
    - Atualização automática de nomes
    - Geração de nomes hierárquicos
    """

    # =============================================================================
    # MÉTODOS DE EXTRAÇÃO E GERAÇÃO DE NOMES
    # =============================================================================

    @staticmethod
    def extract_remote_name_from_url(url: str) -> str:
        """
        Extrai o nome remoto do deck usando estratégias múltiplas.

        Args:
            url: URL do Google Sheets

        Returns:
            Nome remoto extraído ou fallback
        """
        try:
            # Estratégia 1: Título da planilha via HTML
            title = DeckNameManager._extract_spreadsheet_title(url)
            if title and title != "auto name fail":
                return DeckNameManager.clean_name(title)

            # Estratégia 2: Nome do arquivo via Content-Disposition
            filename = DeckNameManager._extract_filename_from_headers(url)
            if filename and filename != "auto name fail":
                return DeckNameManager.clean_name(filename)

            # Estratégia 3: Fallback para ID da planilha e GID
            return DeckNameManager._generate_fallback_name(url)

        except Exception:
            return "auto name fatal fail"

    @staticmethod
    def generate_local_name(
        remote_name: str, parent_name: str = DEFAULT_PARENT_DECK_NAME
    ) -> str:
        """
        Gera o nome local hierárquico: {parent}::{remote_name}

        Args:
            remote_name: Nome remoto do deck
            parent_name: Nome do deck pai

        Returns:
            Nome local no formato hierárquico
        """
        if not remote_name:
            return f"{parent_name}::UnknownDeck"

        clean_remote_name = DeckNameManager.clean_name(remote_name)
        return f"{parent_name}::{clean_remote_name}"

    @staticmethod
    def generate_complete_names(url: str) -> Tuple[str, str]:
        """
        Gera tanto o nome local quanto remoto para uma URL.

        Args:
            url: URL do Google Sheets

        Returns:
            Tupla (local_name, remote_name)
        """
        remote_name = DeckNameManager.extract_remote_name_from_url(url)
        local_name = DeckNameManager.generate_local_name(remote_name)
        return local_name, remote_name

    # =============================================================================
    # MÉTODOS DE RESOLUÇÃO DE CONFLITOS
    # =============================================================================

    @staticmethod
    def resolve_remote_name_conflict(url: str, remote_name: str) -> str:
        """
        Resolve conflitos de nome remoto centralizadamente.

        Args:
            url: URL do deck (para identificação única)
            remote_name: Nome remoto proposto

        Returns:
            Nome remoto resolvido (pode ter sufixo #conflito se necessário)
        """
        if not remote_name:
            return "RemoteDeck"

        clean_name = remote_name.strip()
        if not clean_name:
            return "RemoteDeck"

        # Obter todos os nomes remotos existentes (exceto o deck atual)
        existing_names = DeckNameManager._get_existing_remote_names(exclude_url=url)

        # Se não há conflito, usar nome original
        if clean_name not in existing_names:
            return clean_name

        # Resolver conflito com sufixo
        conflict_index = 1
        while conflict_index <= 100:
            candidate_name = f"{clean_name} #conflito{conflict_index}"
            if candidate_name not in existing_names:
                return candidate_name
            conflict_index += 1

        # Fallback se não conseguir resolver
        return f"{clean_name} #conflito{conflict_index}"

    @staticmethod
    def resolve_local_name_conflict(local_name: str) -> str:
        """
        Resolve conflitos de nome local no Anki.

        Args:
            local_name: Nome local proposto

        Returns:
            Nome local único (pode ter sufixo _X se necessário)
        """
        if not DeckNameManager._check_anki_name_conflict(local_name):
            return local_name

        # Adicionar sufixo numérico
        counter = 2
        while counter <= 100:
            candidate_name = f"{local_name}_{counter}"
            if not DeckNameManager._check_anki_name_conflict(candidate_name):
                return candidate_name
            counter += 1

        # Fallback com timestamp
        import time

        timestamp = int(time.time())
        return f"{local_name}_{timestamp}"

    # =============================================================================
    # MÉTODOS DE SINCRONIZAÇÃO E ATUALIZAÇÃO
    # =============================================================================

    @staticmethod
    def sync_deck_with_config(
        deck_url: str, debug_callback=None
    ) -> Optional[Tuple[int, str]]:
        """
        Sincroniza nome do deck no Anki com a configuração (source of truth).

        Args:
            deck_url: URL do deck remoto
            debug_callback: Função para callback de debug (opcional)

        Returns:
            Tupla (deck_id, synced_name) ou None se erro
        """
        from .config_manager import get_deck_local_id
        from .config_manager import get_deck_local_name

        def debug(message: str):
            if debug_callback:
                debug_callback(f"[DECK_SYNC] {message}")

        try:
            # Obter informações do meta.json
            local_deck_id = get_deck_local_id(deck_url)
            expected_name = get_deck_local_name(deck_url)

            if not local_deck_id or not expected_name:
                debug(
                    f"Deck não encontrado na configuração: ID={local_deck_id}, Nome='{expected_name}'"
                )
                return None

            # Verificar se o deck existe no Anki
            if not mw or not mw.col:
                debug("Anki não disponível")
                return None

            from anki.decks import DeckId

            deck = mw.col.decks.get(DeckId(local_deck_id))
            if not deck:
                debug(f"❌ ERRO: Deck ID {local_deck_id} não existe no Anki")
                return None

            current_name = deck["name"]
            debug(f"Nome atual: '{current_name}' -> Esperado: '{expected_name}'")

            # Sincronizar se necessário
            if current_name != expected_name:
                debug(f"📝 Atualizando nome: '{current_name}' -> '{expected_name}'")
                deck["name"] = expected_name
                mw.col.decks.save(deck)
                debug("✅ Nome atualizado com sucesso")
                return (local_deck_id, expected_name)
            else:
                debug("✅ Nome já sincronizado")
                return (local_deck_id, current_name)

        except Exception as e:
            debug(f"❌ ERRO na sincronização: {e}")
            return None

    @staticmethod
    def update_deck_names_automatically(
        deck_url: str,
        deck_id: int,
        current_local_name: str,
        remote_name: Optional[str] = None,
        debug_callback=None,
    ) -> str:
        """
        Atualiza nomes de deck automaticamente se necessário.

        Esta função centraliza toda a lógica de atualização automática de nomes.

        Args:
            deck_url: URL do deck
            deck_id: ID do deck no Anki
            current_local_name: Nome local atual
            remote_name: Nome remoto (se já conhecido)
            debug_callback: Função para debug

        Returns:
            Nome local final (atualizado ou mantido)
        """

        def debug(message: str):
            if debug_callback:
                debug_callback(f"[NAME_UPDATE] {message}")

        try:
            # Obter nome remoto se não fornecido
            if not remote_name:
                remote_name = DeckNameManager.extract_remote_name_from_url(deck_url)

            # Gerar nome local desejado
            desired_local_name = DeckNameManager.generate_local_name(remote_name)
            debug(
                f"Nome desejado: '{desired_local_name}' (atual: '{current_local_name}')"
            )

            # Verificar se precisa atualizar
            if not DeckNameManager._should_update_name(
                current_local_name, desired_local_name
            ):
                debug("Não precisa atualizar")
                return current_local_name

            # Obter nome disponível
            available_name = DeckNameManager.resolve_local_name_conflict(
                desired_local_name
            )
            debug(f"Nome disponível: '{available_name}'")

            # Atualizar no Anki
            success = DeckNameManager._update_deck_in_anki(deck_id, available_name)
            if success:
                # Atualizar na configuração
                DeckNameManager._update_name_in_config(deck_url, available_name)
                debug(f"✅ Nome atualizado para: '{available_name}'")
                return available_name
            else:
                debug("❌ Falha ao atualizar no Anki")
                return current_local_name

        except Exception as e:
            debug(f"❌ ERRO na atualização: {e}")
            return current_local_name

    @staticmethod
    def create_deck_with_proper_naming(
        deck_url: str, suggested_remote_name: Optional[str] = None
    ) -> Tuple[int, str, str]:
        """
        Cria um deck com nomeação adequada e resolve todos os conflitos.

        Esta função centraliza toda a lógica usada em add_deck_dialog.py.

        Args:
            deck_url: URL do deck
            suggested_remote_name: Nome remoto sugerido (opcional)

        Returns:
            Tupla (deck_id, final_local_name, final_remote_name)
        """
        # Obter nome remoto final
        if suggested_remote_name:
            final_remote_name = DeckNameManager.resolve_remote_name_conflict(
                deck_url, suggested_remote_name
            )
        else:
            extracted_name = DeckNameManager.extract_remote_name_from_url(deck_url)
            final_remote_name = DeckNameManager.resolve_remote_name_conflict(
                deck_url, extracted_name
            )

        # Gerar nome local hierárquico
        desired_local_name = DeckNameManager.generate_local_name(final_remote_name)
        final_local_name = DeckNameManager.resolve_local_name_conflict(
            desired_local_name
        )

        # Criar deck no Anki
        from .utils import get_or_create_deck

        deck_id, actual_name = get_or_create_deck(mw.col, final_local_name)

        return deck_id, actual_name, final_remote_name

    # =============================================================================
    # MÉTODOS PRIVADOS/INTERNOS
    # =============================================================================

    @staticmethod
    def _get_existing_remote_names(exclude_url: Optional[str] = None) -> set:
        """Obtém todos os nomes remotos existentes."""
        from .config_manager import get_remote_decks

        existing_names = set()
        remote_decks = get_remote_decks()

        for deck_url, deck_info in remote_decks.items():
            # Pular o deck atual se especificado
            if exclude_url and deck_info.get("remote_deck_url") == exclude_url:
                continue

            remote_name = deck_info.get("remote_deck_name", "")
            if remote_name:
                existing_names.add(remote_name)

        return existing_names

    @staticmethod
    def _check_anki_name_conflict(name: str) -> bool:
        """Verifica se há conflito de nome no Anki."""
        try:
            if mw and mw.col and mw.col.decks:
                existing_deck = mw.col.decks.by_name(name)
                return existing_deck is not None
            return False
        except:
            return False

    @staticmethod
    def _should_update_name(current_name: str, desired_name: str) -> bool:
        """Determina se deve atualizar o nome."""
        if not current_name or not desired_name:
            return False

        # Extrair nome base (sem sufixo numérico)
        has_suffix, base_name, _ = DeckNameManager._extract_numeric_suffix(current_name)
        comparison_name = base_name if has_suffix else current_name

        return desired_name.lower() != comparison_name.lower()

    @staticmethod
    def _extract_numeric_suffix(name: str) -> Tuple[bool, str, Optional[int]]:
        """Extrai sufixo numérico do nome."""
        suffix_match = re.search(r"_(\d+)$", name)
        if suffix_match:
            suffix_number = int(suffix_match.group(1))
            base_name = name[: suffix_match.start()]
            return True, base_name, suffix_number
        return False, name, None

    @staticmethod
    def _update_deck_in_anki(deck_id: int, new_name: str) -> bool:
        """Atualiza nome do deck no Anki."""
        try:
            if mw and mw.col and mw.col.decks:
                from anki.decks import DeckId

                deck = mw.col.decks.get(DeckId(deck_id))
                if deck:
                    deck["name"] = new_name
                    mw.col.decks.save(deck)
                    return True
            return False
        except Exception:
            return False

    @staticmethod
    def _update_name_in_config(deck_url: str, new_name: str) -> bool:
        """Atualiza nome na configuração."""
        try:
            from .config_manager import get_deck_hash
            from .config_manager import get_meta
            from .config_manager import save_meta

            meta = get_meta()
            deck_hash = get_deck_hash(deck_url)

            if "decks" in meta and deck_hash in meta["decks"]:
                meta["decks"][deck_hash]["local_deck_name"] = new_name
                save_meta(meta)
                return True
            return False
        except Exception:
            return False

    # =============================================================================
    # MÉTODOS DE LIMPEZA E EXTRAÇÃO ESPECÍFICOS
    # =============================================================================

    @staticmethod
    def clean_name(name: str) -> str:
        """Limpa e normaliza um nome de deck."""
        if not name:
            return "auto name fatal fail"

        name = str(name).strip()

        # Remover terminação " - Google Drive" ou " - Google Sheets"
        name = re.sub(
            r"\s*-\s*Google\s+(Drive|Sheets)\s*$", "", name, flags=re.IGNORECASE
        )

        # Remover caracteres problemáticos, mas manter espaços
        name = re.sub(r'[<>:"/\\|?*]', "_", name)

        if not name:
            return "auto name fatal fail"

        # Limitar tamanho
        if len(name) > 100:
            name = name[:100]

        return name

    @staticmethod
    def _extract_spreadsheet_title(url: str) -> Optional[str]:
        """Extrai título da planilha via HTML."""
        try:
            import urllib.parse
            import urllib.request

            # Construir URL para metadados
            base_url = (
                url.replace("&output=tsv", "")
                .replace("?output=tsv", "")
                .replace("&single=true", "")
            )
            parsed = urllib.parse.urlparse(base_url)
            query_params = urllib.parse.parse_qs(parsed.query)

            # Manter apenas gid se existir
            filtered_params = {}
            if "gid" in query_params:
                filtered_params["gid"] = query_params["gid"]

            new_query = urllib.parse.urlencode(filtered_params, doseq=True)
            meta_url = urllib.parse.urlunparse(
                (
                    parsed.scheme,
                    parsed.netloc,
                    parsed.path,
                    parsed.params,
                    new_query,
                    parsed.fragment,
                )
            )

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            request = urllib.request.Request(meta_url, headers=headers)

            with urllib.request.urlopen(request, timeout=15) as response:
                html = response.read().decode("utf-8", errors="ignore")

                # Múltiplos padrões para extrair título
                title_patterns = [
                    r"<title>([^<]+?)\s*-\s*Google\s*(Sheets|Planilhas)</title>",
                    r"<title>([^<]+)</title>",
                    r'"title":"([^"]+)"',
                    r'<meta property="og:title" content="([^"]+)"',
                    r'"doc-name":"([^"]+)"',
                ]

                for pattern in title_patterns:
                    match = re.search(pattern, html, re.IGNORECASE)
                    if match:
                        title = match.group(1).strip()
                        if title and title.lower() not in [
                            "untitled",
                            "sem título",
                            "planilha sem título",
                        ]:
                            return title

                return None

        except Exception:
            return None

    @staticmethod
    def _extract_filename_from_headers(url: str) -> Optional[str]:
        """Extrai nome do arquivo via headers."""
        try:
            import urllib.request

            headers = {"User-Agent": "Mozilla/5.0 (Sheets2Anki) AnkiAddon"}
            request = urllib.request.Request(url, headers=headers)

            with urllib.request.urlopen(request, timeout=10) as response:
                content_disposition = response.headers.get("Content-Disposition", "")
                if content_disposition:
                    match = re.search(
                        r'filename[^;=\n]*=(([\'"]).*?\2|[^;\n]*)', content_disposition
                    )
                    if match:
                        filename = match.group(1).strip("\"'")
                        if filename:
                            if filename.lower().endswith(".tsv"):
                                filename = filename[:-4]
                            return filename

                return None

        except Exception:
            return None

    @staticmethod
    def _generate_fallback_name(url: str) -> str:
        """Gera nome fallback baseado em ID da planilha."""
        try:
            from urllib.parse import parse_qs
            from urllib.parse import urlparse

            # Extrair ID da planilha
            match = re.search(r"/spreadsheets/d/e/([a-zA-Z0-9-_]+)", url)
            if not match:
                match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", url)

            if match:
                spreadsheet_id = match.group(1)

                # Extrair GID
                parsed_url = urlparse(url)
                query_params = parse_qs(parsed_url.query)
                gid = query_params.get("gid", ["0"])[0]

                if gid != "0":
                    return f"Planilha {spreadsheet_id[:8]} - Aba {gid}"
                else:
                    return f"Planilha {spreadsheet_id[:8]} - Aba Principal"

            return "Planilha Externa"

        except Exception:
            return "auto name fatal fail"


# =============================================================================
# GERENCIAMENTO DE SUBDECKS (antigo subdeck_manager.py)
# =============================================================================

# =============================================================================
# RECREAÇÃO DE DECKS (antigo deck_recreation.py)
# =============================================================================


class DeckRecreationManager:
    """Gerenciador para recreação de decks deletados."""

    @staticmethod
    def recreate_deck_if_missing(
        deck_info: Dict[str, Any],
    ) -> Tuple[bool, Optional[int], Optional[str]]:
        """
        Recria um deck se ele estiver faltando.

        Args:
            deck_info: Informações do deck da configuração

        Returns:
            Tuple[bool, Optional[int], Optional[str]]:
            (foi_recriado, novo_deck_id, nome_atual)
        """
        from .utils import add_debug_message

        # Verificar se mw e col estão disponíveis
        if not mw or not mw.col:
            raise ValueError("Anki não está disponível")

        local_deck_id = deck_info.get("local_deck_id")
        add_debug_message(
            f"🔍 Verificando deck com ID: {local_deck_id}", "DECK_RECREATION"
        )

        # Verificar se o deck existe
        deck = mw.col.decks.get(local_deck_id) if local_deck_id is not None else None

        if deck:
            deck_name = deck.get("name", "")
            expected_name = deck_info.get("local_deck_name", "")

            add_debug_message(
                f"📋 Deck encontrado: '{deck_name}' (ID: {local_deck_id})",
                "DECK_RECREATION",
            )
            add_debug_message(f"📋 Nome esperado: '{expected_name}'", "DECK_RECREATION")

            # Verificar se é realmente o deck correto ou se foi renomeado/alterado
            if deck_name == expected_name or expected_name in deck_name:
                add_debug_message("✅ Deck existe e nome confere", "DECK_RECREATION")
                return False, local_deck_id, deck_name
            else:
                add_debug_message(
                    f"⚠️ ATENÇÃO: Deck existe mas nome mudou: '{deck_name}' != '{expected_name}'",
                    "DECK_RECREATION",
                )
                add_debug_message(
                    "🔧 Considerando como deck a ser recriado devido à inconsistência de nome",
                    "DECK_RECREATION",
                )
                # Continuar para recriação
        else:
            add_debug_message(
                f"❌ Deck com ID {local_deck_id} não encontrado", "DECK_RECREATION"
            )

        # Deck não existe ou foi alterado, precisa recriar
        add_debug_message(
            "⚠️ Deck local foi deletado ou alterado, iniciando recriação",
            "DECK_RECREATION",
        )

        try:
            new_deck_id, actual_name = DeckRecreationManager._create_new_deck(deck_info)

            # Aplicar opções do Sheets2Anki ao deck recriado
            from .utils import apply_sheets2anki_options_to_deck

            remote_deck_name = deck_info.get("remote_deck_name")
            try:
                apply_sheets2anki_options_to_deck(new_deck_id, remote_deck_name)
                add_debug_message(
                    f"✅ Opções aplicadas ao deck recriado: {actual_name}",
                    "DECK_RECREATION",
                )
            except Exception as e:
                add_debug_message(
                    f"⚠️ Falha ao aplicar opções ao deck recriado: {e}",
                    "DECK_RECREATION",
                )

            add_debug_message(
                f"✅ Deck recriado com sucesso: {actual_name} (ID: {new_deck_id})",
                "DECK_RECREATION",
            )
            return True, new_deck_id, actual_name

        except Exception as e:
            add_debug_message(f"❌ Erro na recreação do deck: {e}", "DECK_RECREATION")
            raise

    @staticmethod
    def _create_new_deck(deck_info: Dict[str, Any]) -> Tuple[int, str]:
        """
        Cria um novo deck com base nas informações fornecidas.

        Args:
            deck_info: Informações do deck

        Returns:
            Tuple[int, str]: (deck_id, nome_atual)
        """
        from .utils import add_debug_message

        # Verificar se mw e col estão disponíveis
        if not mw or not mw.col:
            raise ValueError("Anki não está disponível")

        # Determinar o nome desejado para o deck
        current_remote_name = deck_info.get("remote_deck_name")

        if current_remote_name:
            desired_local_name = DeckNameManager.generate_local_name(
                current_remote_name
            )
        else:
            # Fallback para o nome salvo na configuração
            local_deck_id = deck_info.get("local_deck_id")
            desired_local_name = (
                deck_info.get("local_deck_name") or f"Sheets2Anki::Deck_{local_deck_id}"
            )

        add_debug_message(
            f"🎯 Nome desejado para recreação: {desired_local_name}", "DECK_RECREATION"
        )

        # Verificar se já existe um deck com esse nome antes de criar
        existing_deck = mw.col.decks.by_name(desired_local_name)

        if existing_deck:
            # Deck já existe, usar o existente
            new_deck_id = existing_deck["id"]
            actual_name = existing_deck["name"]
            add_debug_message(
                f"📂 Usando deck existente: {actual_name} (ID: {new_deck_id})",
                "DECK_RECREATION",
            )
        else:
            # Deck não existe, criar novo
            try:
                add_debug_message(
                    f"🆕 Criando novo deck: '{desired_local_name}'", "DECK_RECREATION"
                )
                new_deck_id = mw.col.decks.id(desired_local_name)
                add_debug_message(
                    f"🆔 ID retornado pela API do Anki: {new_deck_id} (tipo: {type(new_deck_id)})",
                    "DECK_RECREATION",
                )

                # Verificar se o deck foi criado corretamente
                if new_deck_id is None:
                    raise ValueError(f"Falha ao criar deck: {desired_local_name}")

                # Verificar se o nome foi mantido ou alterado pelo Anki
                new_deck = mw.col.decks.get(new_deck_id)
                if not new_deck:
                    raise ValueError(
                        f"Falha ao obter deck criado: {desired_local_name}"
                    )

                actual_name = new_deck["name"]
                add_debug_message(
                    f"✅ Deck confirmado no Anki: '{actual_name}' (ID: {new_deck_id})",
                    "DECK_RECREATION",
                )

                if actual_name != desired_local_name:
                    add_debug_message(
                        f"📝 Nome alterado durante criação: {desired_local_name} -> {actual_name}",
                        "DECK_RECREATION",
                    )

                add_debug_message(
                    f"🆕 Novo deck criado: {actual_name} (ID: {new_deck_id})",
                    "DECK_RECREATION",
                )

            except Exception:
                # Em caso de erro, usar nome único baseado em timestamp
                import time

                unique_suffix = str(int(time.time()))[-6:]
                fallback_name = f"Sheets2Anki::Deck_{unique_suffix}"

                add_debug_message(
                    f"🔄 Criando com nome de fallback: {fallback_name}",
                    "DECK_RECREATION",
                )

                new_deck_id = mw.col.decks.id(fallback_name)
                if new_deck_id is None:
                    raise ValueError(
                        f"Falha ao criar deck com nome de fallback: {fallback_name}"
                    )

                new_deck = mw.col.decks.get(new_deck_id)

                if not new_deck:
                    raise ValueError(
                        f"Falha ao obter deck com nome de fallback: {fallback_name}"
                    )

                actual_name = new_deck["name"]

        return int(new_deck_id), str(actual_name)

    @staticmethod
    def update_deck_info_after_recreation(
        deck_info: Dict[str, Any], new_deck_id: int, actual_name: str
    ) -> None:
        """
        Atualiza as informações do deck após recreação.

        Args:
            deck_info: Informações do deck (será modificado in-place)
            new_deck_id: Novo ID do deck
            actual_name: Nome atual do deck
        """
        from .utils import add_debug_message

        old_deck_id = deck_info.get("local_deck_id")

        if new_deck_id != old_deck_id:
            add_debug_message(
                f"🔄 Atualizando deck ID: {old_deck_id} -> {new_deck_id}",
                "DECK_RECREATION",
            )
            deck_info["local_deck_id"] = new_deck_id
            add_debug_message(
                f"✅ Confirmação: deck_info['local_deck_id'] agora = {deck_info['local_deck_id']}",
                "DECK_RECREATION",
            )

        old_name = deck_info.get("local_deck_name", "")
        if actual_name != old_name:
            add_debug_message(
                f"📝 Atualizando nome do deck: '{old_name}' -> '{actual_name}'",
                "DECK_RECREATION",
            )
            deck_info["local_deck_name"] = actual_name


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
            self.status_label.setText(
                f"{selected_count} de {total_count} decks selecionados"
            )
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
