"""
Funções utilitárias para o addon Sheets2Anki.

Este módulo contém funções auxiliares utilizadas em
diferentes partes do projeto.
"""

import hashlib
import re

try:
    from .compat import mw
    from .templates_and_definitions import DEFAULT_PARENT_DECK_NAME
except ImportError:
    # Para testes independentes
    from compat import mw
    from templates_and_definitions import DEFAULT_PARENT_DECK_NAME


def safe_find_cards(search_query):
    """
    Realiza uma busca segura de cards, escapando caracteres problemáticos.
    
    Args:
        search_query (str): Query de busca
        
    Returns:
        list: Lista de IDs de cards encontrados
    """
    try:
        if not mw or not mw.col:
            return []
        
        # Verificar se a query está vazia
        if not search_query or not search_query.strip():
            return []
        
        return mw.col.find_cards(search_query)
    except Exception as e:
        print(f"[SEARCH_ERROR] Erro na busca de cards: {e}")
        return []


def safe_find_cards_by_deck(deck_name):
    """
    Busca cards por nome de deck de forma segura.
    
    Args:
        deck_name (str): Nome do deck
        
    Returns:
        list: Lista de IDs de cards encontrados
    """
    try:
        if not deck_name or not deck_name.strip():
            return []
        
        # Escapar aspas duplas no nome do deck
        escaped_deck_name = deck_name.replace('"', '\\"')
        search_query = f'deck:"{escaped_deck_name}"'
        
        return safe_find_cards(search_query)
    except Exception as e:
        print(f"[SEARCH_ERROR] Erro na busca por deck '{deck_name}': {e}")
        return []


def extract_spreadsheet_id_from_url(url):
    """
    Extrai o ID da planilha de uma URL de edição do Google Sheets.

    Args:
        url (str): URL de edição do Google Sheets

    Returns:
        str: ID da planilha ou None se não encontrado

    Examples:
        >>> extract_spreadsheet_id_from_url("https://docs.google.com/spreadsheets/d/1N-Va4ZzLUJBsD6wBaOkoeFTE6EnbZdaP/edit?usp=sharing")
        "1N-Va4ZzLUJBsD6wBaOkoeFTE6EnbZdaP"
    """
    if not url:
        return None

    # Extrair ID da planilha de URLs de edição (ID entre /d/ e /edit)
    edit_pattern = r"/spreadsheets/d/([a-zA-Z0-9-_]+)/edit"
    match = re.search(edit_pattern, url)
    
    if match:
        return match.group(1)

    return None


def get_spreadsheet_id_from_url(url):
    """
    Extrai o ID da planilha de uma URL de edição do Google Sheets.
    Esta função substitui get_publication_key_hash para trabalhar apenas com IDs reais.

    Args:
        url (str): URL de edição do Google Sheets

    Returns:
        str: ID da planilha (usado diretamente como identificador)

    Raises:
        ValueError: Se a URL não for uma URL de edição válida do Google Sheets
    """
    spreadsheet_id = extract_spreadsheet_id_from_url(url)
    
    if not spreadsheet_id:
        raise ValueError(
            "URL deve ser uma URL de edição válida do Google Sheets no formato:\n"
            "https://docs.google.com/spreadsheets/d/{ID}/edit?usp=sharing"
        )
    
    return spreadsheet_id


def update_note_type_names_for_deck_rename(
    url, old_remote_name, new_remote_name, debug_messages=None
):
    """
    Atualiza apenas os nomes das strings dos note types no meta.json quando o remote_deck_name muda.
    A sincronização com o Anki será feita posteriormente pela função sync_note_type_names_with_config.

    Args:
        url (str): URL do deck remoto
        old_remote_name (str): Nome remoto antigo
        new_remote_name (str): Nome remoto novo
        debug_messages (list, optional): Lista para debug

    Returns:
        int: Número de note types atualizados
    """
    from .config_manager import get_deck_id
    from .config_manager import get_deck_note_type_ids
    from .config_manager import get_meta
    from .config_manager import save_meta

    def add_debug_msg(message, category="NOTE_TYPE_RENAME"):
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] [{category}] {message}"
        if debug_messages is not None:
            debug_messages.append(formatted_msg)
        print(formatted_msg)

    try:
        add_debug_msg(
            f"Atualizando strings dos note types: '{old_remote_name}' → '{new_remote_name}'"
        )

        # Obter note types atuais
        note_types_config = get_deck_note_type_ids(url)
        updated_count = 0

        if not note_types_config:
            add_debug_msg("Nenhum note type para atualizar")
            return 0

        # Atualizar apenas as strings dos nomes
        updated_note_types = {}

        for note_type_id_str, current_name in note_types_config.items():
            if old_remote_name and old_remote_name in current_name:
                # Substituir nome remoto antigo pelo novo na string
                new_name = current_name.replace(old_remote_name, new_remote_name)
                updated_note_types[note_type_id_str] = new_name
                add_debug_msg(
                    f"Note type ID {note_type_id_str}: '{current_name}' → '{new_name}'"
                )
                updated_count += 1
            else:
                # Manter nome atual
                updated_note_types[note_type_id_str] = current_name

        # Salvar no meta.json apenas se houve mudanças
        if updated_count > 0:
            try:
                meta = get_meta()
                spreadsheet_id = get_deck_id(url)

                if "decks" in meta and spreadsheet_id in meta["decks"]:
                    meta["decks"][spreadsheet_id]["note_types"] = updated_note_types
                    save_meta(meta)
                    add_debug_msg(
                        f"✅ Meta.json atualizado: {updated_count} strings de note types atualizadas"
                    )

            except Exception as meta_error:
                add_debug_msg(f"❌ Erro ao atualizar meta.json: {meta_error}")

        add_debug_msg(
            f"✅ {updated_count} strings de note types atualizadas no meta.json"
        )
        return updated_count

    except Exception as e:
        add_debug_msg(f"❌ ERRO ao atualizar strings dos note types: {e}")
        return 0


def sync_note_type_names_with_config(col, deck_url, debug_messages=None):
    """
    Sincroniza os nomes dos note types no Anki com as configurações no meta.json.
    Esta função usa note_types como source of truth para os nomes.

    Args:
        col: Collection do Anki
        deck_url (str): URL do deck remoto
        debug_messages (list, optional): Lista para debug

    Returns:
        dict: Estatísticas da sincronização
    """
    from .config_manager import get_deck_note_type_ids

    def add_debug_msg(message, category="NOTE_TYPE_SYNC"):
        """Helper para adicionar mensagens de debug com timestamp."""
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] [{category}] {message}"
        if debug_messages is not None:
            debug_messages.append(formatted_msg)
        print(formatted_msg)

    stats = {
        "total_note_types": 0,
        "synced_note_types": 0,
        "unchanged_note_types": 0,
        "error_note_types": 0,
        "errors": [],
    }

    try:
        add_debug_msg("🔄 INICIANDO sincronização de note types...")

        # Obter note types configurados
        note_types_config = get_deck_note_type_ids(deck_url)
        stats["total_note_types"] = len(note_types_config)

        if not note_types_config:
            add_debug_msg("⚠️ Nenhum note type configurado para sincronizar")
            return stats

        add_debug_msg(
            f"📋 Sincronizando {stats['total_note_types']} note types configurados"
        )

        # Listar todos os note types configurados primeiro
        for note_type_id_str, expected_name in note_types_config.items():
            add_debug_msg(f"  - ID {note_type_id_str}: '{expected_name}'")

        # Agora processar cada um
        for note_type_id_str, expected_name in note_types_config.items():
            try:
                note_type_id = int(note_type_id_str)

                add_debug_msg(f"🔍 Processando note type ID {note_type_id}...")

                # Buscar o note type no Anki
                from anki.models import NotetypeId
                note_type = col.models.get(NotetypeId(note_type_id))
                if not note_type:
                    add_debug_msg(f"❌ Note type ID {note_type_id} não existe no Anki")
                    stats["error_note_types"] += 1
                    continue

                current_name = note_type.get("name", "")
                add_debug_msg(f"📝 Note type ID {note_type_id}:")
                add_debug_msg(f"    Nome atual no Anki: '{current_name}'")
                add_debug_msg(f"    Nome esperado (config): '{expected_name}'")

                # SEMPRE tentar atualizar para garantir sincronização
                if current_name != expected_name:
                    add_debug_msg(
                        f"� ATUALIZANDO note type de '{current_name}' para '{expected_name}'"
                    )

                    # Atualizar o nome do note type no Anki
                    note_type["name"] = expected_name
                    col.models.save(note_type)

                    # Forçar save da collection para garantir persistência imediata
                    col.save()
                    add_debug_msg("💾 Collection salva para garantir persistência")

                    # Verificar se realmente foi atualizado
                    updated_note_type = col.models.get(NotetypeId(note_type_id))
                    if (
                        updated_note_type
                        and updated_note_type.get("name") == expected_name
                    ):
                        stats["synced_note_types"] += 1
                        add_debug_msg("✅ Note type atualizado com SUCESSO")
                    else:
                        add_debug_msg(
                            "❌ FALHA ao atualizar note type - verificação pós-save falhou"
                        )
                        stats["error_note_types"] += 1
                else:
                    stats["unchanged_note_types"] += 1
                    add_debug_msg("✅ Note type já está sincronizado")

            except Exception as note_type_error:
                stats["error_note_types"] += 1
                error_msg = f"Erro ao sincronizar note type {note_type_id_str}: {note_type_error}"
                stats["errors"].append(error_msg)
                add_debug_msg(f"❌ {error_msg}")
                import traceback

                add_debug_msg(f"Traceback: {traceback.format_exc()}")

        add_debug_msg(
            f"📊 RESULTADO: {stats['synced_note_types']} sincronizados, {stats['unchanged_note_types']} inalterados, {stats['error_note_types']} erros"
        )

        # Limpeza de note types órfãos na configuração
        try:
            orphaned_count = cleanup_orphaned_note_types()
            if orphaned_count > 0:
                add_debug_msg(
                    f"🧹 Limpeza: {orphaned_count} note types órfãos removidos da configuração"
                )
        except Exception as cleanup_error:
            add_debug_msg(f"⚠️ Erro na limpeza de órfãos: {cleanup_error}")

        return stats

    except Exception as e:
        add_debug_msg(f"❌ ERRO geral na sincronização: {e}")
        stats["errors"].append(f"Erro geral: {e}")
        return stats


def get_or_create_deck(col, deckName, remote_deck_name=None):
    """
    Cria ou obtém um deck existente no Anki e aplica as opções baseadas no modo configurado.

    Args:
        col: Collection do Anki
        deckName: Nome do deck
        remote_deck_name (str, optional): Nome do deck remoto para modo individual

    Returns:
        tuple: (deck_id, actual_name) onde deck_id é o ID do deck e actual_name é o nome real usado

    Raises:
        ValueError: Se o nome do deck for inválido
    """
    if (
        not deckName
        or not isinstance(deckName, str)
        or deckName.strip() == ""
        or deckName.strip().lower() == "default"
    ):
        raise ValueError(
            "Nome de deck inválido ou proibido para sincronização: '%s'" % deckName
        )

    deck = col.decks.by_name(deckName)
    deck_was_created = False

    if deck is None:
        try:
            deck_id = col.decks.id(deckName)
            deck_was_created = True
            # Obter o deck recém-criado para verificar o nome real usado
            new_deck = col.decks.get(deck_id)
            actual_name = new_deck["name"] if new_deck else deckName
        except Exception as e:
            raise ValueError(f"Não foi possível criar o deck '{deckName}': {str(e)}")
    else:
        deck_id = deck["id"]
        actual_name = deck["name"]

    # Aplicar opções baseadas no modo (novo ou existente que seja do Sheets2Anki)
    if deckName.startswith("Sheets2Anki::") or deck_was_created:
        try:
            apply_sheets2anki_options_to_deck(deck_id, remote_deck_name)
        except Exception as e:
            print(
                f"[DECK_OPTIONS] Aviso: Falha ao aplicar opções ao deck '{actual_name}': {e}"
            )

    return deck_id, actual_name


def get_model_suffix_from_url(url):
    """
    Gera um sufixo único e curto baseado na URL.

    Args:
        url: URL do deck remoto

    Returns:
        str: Sufixo de 8 caracteres baseado no hash SHA1 da URL
    """
    return hashlib.sha1(url.encode()).hexdigest()[:8]


def get_note_type_name(url, remote_deck_name, student=None, is_cloze=False):
    """
    Gera o nome padronizado para note types do Sheets2Anki.

    Formato: "Sheets2Anki - {remote_deck_name} - {nome_aluno} - Basic/Cloze"
    O remote_deck_name já vem com resolução de conflitos aplicada pelo config_manager.

    Args:
        url (str): URL do deck remoto
        remote_deck_name (str): Nome do deck remoto extraído da planilha (já com sufixo se necessário)
        student (str, optional): Nome do aluno para criar note type específico
        is_cloze (bool): Se é um note type do tipo Cloze

    Returns:
        str: Nome padronizado do note type
    """

    note_type = "Cloze" if is_cloze else "Basic"

    # Usar o nome remoto diretamente (já vem com sufixo de conflito do config_manager)
    clean_remote_name = remote_deck_name.strip() if remote_deck_name else "RemoteDeck"

    # Usar nome do estudante como fornecido (case-sensitive)
    if student:
        clean_student_name = student.strip()
        if clean_student_name:
            return f"Sheets2Anki - {clean_remote_name} - {clean_student_name} - {note_type}"
    else:
        return f"Sheets2Anki - {clean_remote_name} - {note_type}"


def register_note_type_for_deck(url, note_type_id, note_type_name, debug_messages=None):
    """
    Registra um note type ID no momento da criação/uso (abordagem inteligente).
    Armazena o nome completo do note type como source of truth.

    Args:
        url (str): URL do deck remoto
        note_type_id (int): ID do note type
        note_type_name (str): Nome completo do note type no formato padrão
        debug_messages (list, optional): Lista para acumular mensagens de debug
    """
    from .config_manager import add_note_type_id_to_deck

    def add_debug_msg(message, category="NOTE_TYPE_REG"):
        """Helper para adicionar mensagens de debug com timestamp."""
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] [{category}] {message}"
        if debug_messages is not None:
            debug_messages.append(formatted_msg)
        print(formatted_msg)

    try:
        add_debug_msg(
            f"Registrando note type: ID={note_type_id}, Nome='{note_type_name}'"
        )

        # Usar o nome completo como está (já no formato padrão)
        # O nome completo será a source of truth
        add_note_type_id_to_deck(url, note_type_id, note_type_name, debug_messages)
        add_debug_msg(f"✅ Note type registrado com sucesso: '{note_type_name}'")

    except Exception as e:
        add_debug_msg(f"❌ ERRO ao registrar note type: {e}")


def capture_deck_note_type_ids_from_cards(url, local_deck_id, debug_messages=None):
    """
    Captura note type IDs analisando os cards existentes no deck local (abordagem mais inteligente).
    Em vez de buscar por nome, analisa cards reais que pertencem ao deck.

    Args:
        url (str): URL do deck remoto
        local_deck_id (int): ID do deck local no Anki
        debug_messages (list, optional): Lista para acumular mensagens de debug
    """
    from .compat import mw
    from .config_manager import add_note_type_id_to_deck

    def add_debug_msg(message, category="NOTE_TYPE_IDS"):
        """Helper para adicionar mensagens de debug com timestamp."""
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] [{category}] {message}"
        if debug_messages is not None:
            debug_messages.append(formatted_msg)
        print(formatted_msg)

    add_debug_msg(f"CAPTURA INTELIGENTE: Analisando cards do deck ID {local_deck_id}")

    if not mw or not mw.col:
        add_debug_msg("ERRO: Anki não disponível")
        return

    try:
        # Buscar todos os cards do deck específico
        # Usar busca por ID de deck que é segura
        card_ids = mw.col.find_cards(f"did:{local_deck_id}")
        add_debug_msg(f"Encontrados {len(card_ids)} cards no deck")

        if not card_ids:
            add_debug_msg(
                "⚠️ Nenhum card encontrado no deck - note types serão capturados durante a sincronização"
            )
            return

        # Coletar note type IDs únicos dos cards existentes
        note_type_ids = set()
        note_type_info = {}  # {note_type_id: {'name': str, 'count': int}}

        for card_id in card_ids:
            try:
                card = mw.col.get_card(card_id)
                note = card.note()
                note_type = note.note_type()

                if not note_type:
                    add_debug_msg(
                        f"Ignorando card {card_id} - note type não encontrado"
                    )
                    continue

                note_type_id = note_type["id"]
                note_type_name = note_type["name"]

                note_type_ids.add(note_type_id)

                if note_type_id not in note_type_info:
                    note_type_info[note_type_id] = {"name": note_type_name, "count": 0}
                note_type_info[note_type_id]["count"] += 1

            except Exception as card_error:
                add_debug_msg(f"Erro ao processar card {card_id}: {card_error}")
                continue

        add_debug_msg(f"Note types únicos encontrados: {len(note_type_ids)}")

        # Registrar cada note type encontrado
        for note_type_id in note_type_ids:
            info = note_type_info[note_type_id]
            full_name = info["name"]  # Nome completo do note type
            count = info["count"]

            add_debug_msg(
                f"Registrando: ID {note_type_id}, Nome completo '{full_name}', Cards: {count}"
            )

            # Usar o nome completo como source of truth (não extrair partes)
            add_note_type_id_to_deck(url, note_type_id, full_name, debug_messages)

        add_debug_msg(
            f"✅ SUCESSO: Capturados {len(note_type_ids)} note types de cards existentes"
        )

    except Exception as e:
        add_debug_msg(f"❌ ERRO na captura inteligente: {e}")
        import traceback

        add_debug_msg(f"Detalhes: {traceback.format_exc()}")


def capture_deck_note_type_ids(
    url, remote_deck_name, enabled_students=None, debug_messages=None
):
    """
    Função de compatibilidade que usa a abordagem inteligente baseada em cards.

    Args:
        url (str): URL do deck remoto
        remote_deck_name (str): Nome do deck remoto
        enabled_students (list, optional): Lista de alunos habilitados
        debug_messages (list, optional): Lista para acumular mensagens de debug
    """
    from .config_manager import get_deck_local_id

    def add_debug_msg(message, category="NOTE_TYPE_IDS"):
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] [{category}] {message}"
        if debug_messages is not None:
            debug_messages.append(formatted_msg)
        print(formatted_msg)

    try:
        # Obter ID do deck local
        local_deck_id = get_deck_local_id(url)

        if local_deck_id:
            add_debug_msg(
                f"Usando captura inteligente para deck local ID: {local_deck_id}"
            )
            capture_deck_note_type_ids_from_cards(url, local_deck_id, debug_messages)
        else:
            add_debug_msg(
                "⚠️ Deck local não encontrado - note types serão registrados durante criação"
            )

    except Exception as e:
        add_debug_msg(f"❌ ERRO: {e}")
        import traceback

        add_debug_msg(f"Detalhes: {traceback.format_exc()}")
        import traceback

        error_details = traceback.format_exc()
        add_debug_msg(f"Detalhes do erro: {error_details}")


def delete_deck_note_types_by_ids(url):
    """
    Deleta note types usando os IDs armazenados na configuração do deck.
    Esta é uma alternativa mais robusta à busca por padrões de nome.

    Args:
        url (str): URL do deck remoto

    Returns:
        int: Número de note types deletados
    """
    from .compat import mw
    from .config_manager import cleanup_invalid_note_type_ids
    from .config_manager import get_deck_note_type_ids
    from .config_manager import remove_note_type_id_from_deck

    if not mw or not mw.col:
        print("[DELETE_BY_IDS] Anki não disponível")
        return 0

    try:
        # Primeiro limpar IDs inválidos
        cleanup_invalid_note_type_ids()

        # Obter IDs válidos
        note_type_ids = get_deck_note_type_ids(url)

        if not note_type_ids:
            print("[DELETE_BY_IDS] Nenhum note type ID encontrado para o deck")
            return 0

        deleted_count = 0

        for (
            note_type_id
        ) in note_type_ids.copy():  # Usar cópia para modificar durante iteração
            from anki.models import NotetypeId
            model = mw.col.models.get(NotetypeId(note_type_id))
            if model:
                model_name = model["name"]

                try:
                    # Verificar se há notas usando este note type
                    note_ids = mw.col.models.nids(note_type_id)
                    if note_ids:
                        print(
                            f"[DELETE_BY_IDS] Note type '{model_name}' tem {len(note_ids)} notas, deletando-as primeiro..."
                        )
                        mw.col.remove_notes(note_ids)

                    # Deletar o note type
                    mw.col.models.rem(model)
                    deleted_count += 1

                    # Remover ID da configuração
                    remove_note_type_id_from_deck(url, note_type_id)

                    print(
                        f"[DELETE_BY_IDS] Note type '{model_name}' (ID: {note_type_id}) deletado com sucesso"
                    )

                except Exception as e:
                    print(
                        f"[DELETE_BY_IDS] Erro ao deletar note type '{model_name}' (ID: {note_type_id}): {e}"
                    )
            else:
                # ID não existe mais, remover da configuração
                remove_note_type_id_from_deck(url, note_type_id)
                print(
                    f"[DELETE_BY_IDS] Note type ID {note_type_id} não encontrado, removido da configuração"
                )

        if deleted_count > 0:
            mw.col.save()
            print(
                f"[DELETE_BY_IDS] Operação concluída: {deleted_count} note types deletados"
            )

        return deleted_count

    except Exception as e:
        print(f"[DELETE_BY_IDS] Erro na deleção por IDs: {e}")
        import traceback

        traceback.print_exc()
        return 0


def rename_note_type_in_anki(note_type_id, new_name):
    """
    Renomeia um note type existente no Anki sem criar um novo.

    Args:
        note_type_id (int): ID do note type a ser renomeado
        new_name (str): Novo nome para o note type

    Returns:
        bool: True se renomeado com sucesso, False caso contrário
    """
    try:
        from aqt import mw

        if not mw or not mw.col:
            print("[RENAME_NOTE_TYPE] Anki não está disponível")
            return False

        # Obter o model existente
        from anki.models import NotetypeId
        model = mw.col.models.get(NotetypeId(note_type_id))  # type: ignore
        if not model:
            print(f"[RENAME_NOTE_TYPE] Note type ID {note_type_id} não encontrado")
            return False

        old_name = model["name"]

        # Só renomear se o nome for diferente
        if old_name == new_name:
            print(
                f"[RENAME_NOTE_TYPE] Note type {note_type_id} já tem o nome correto: '{new_name}'"
            )
            return True

        print(
            f"[RENAME_NOTE_TYPE] Renomeando note type {note_type_id} de '{old_name}' para '{new_name}'"
        )

        # Alterar apenas o nome do model existente
        model["name"] = new_name

        # Salvar as alterações
        mw.col.models.save(model)

        print("[RENAME_NOTE_TYPE] ✅ Note type renomeado com sucesso!")
        return True

    except Exception as e:
        print(f"[RENAME_NOTE_TYPE] ❌ Erro ao renomear note type {note_type_id}: {e}")
        import traceback

        traceback.print_exc()
        return False


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


def cleanup_orphaned_note_types():
    """
    Remove da configuração note types que não existem mais no Anki.
    Útil para limpar referências de note types que foram deletados.

    Returns:
        int: Número de note types órfãos removidos da configuração
    """
    try:
        from aqt import mw

        print("[CLEANUP_ORPHANED] Iniciando limpeza de note types órfãos...")

        if not mw or not mw.col:
            print("[CLEANUP_ORPHANED] Anki não está disponível")
            return 0

        from .config_manager import get_meta
        from .config_manager import save_meta

        meta = get_meta()
        if not meta or "decks" not in meta:
            print("[CLEANUP_ORPHANED] Nenhuma configuração de decks encontrada")
            return 0

        cleaned_count = 0

        for publication_key, deck_info in meta["decks"].items():
            if "note_types" not in deck_info:
                continue

            orphaned_ids = []

            # Verificar quais note types da configuração não existem mais no Anki
            for note_type_id_str, note_type_name in deck_info["note_types"].items():
                try:
                    note_type_id = int(note_type_id_str)
                    # Usar o mesmo padrão do resto do código
                    from anki.models import NotetypeId
                    model = mw.col.models.get(NotetypeId(note_type_id))  # type: ignore

                    if not model:
                        orphaned_ids.append(note_type_id_str)
                        print(
                            f"[CLEANUP_ORPHANED] Órfão encontrado: ID {note_type_id_str} - '{note_type_name}'"
                        )

                except (ValueError, TypeError):
                    # ID inválido, remover também
                    orphaned_ids.append(note_type_id_str)
                    print(
                        f"[CLEANUP_ORPHANED] ID inválido encontrado: '{note_type_id_str}'"
                    )

            # Remover órfãos da configuração
            for orphaned_id in orphaned_ids:
                del deck_info["note_types"][orphaned_id]
                cleaned_count += 1
                print(f"[CLEANUP_ORPHANED] Removido órfão: ID {orphaned_id}")

        if cleaned_count > 0:
            save_meta(meta)
            print(
                f"[CLEANUP_ORPHANED] Limpeza concluída: {cleaned_count} note types órfãos removidos"
            )
        else:
            print("[CLEANUP_ORPHANED] Nenhum note type órfão encontrado")

        return cleaned_count

    except Exception as e:
        print(f"[CLEANUP_ORPHANED] Erro na limpeza: {e}")
        import traceback

        traceback.print_exc()
        return 0


# =============================================================================
# GERENCIAMENTO DE OPÇÕES DE DECK COMPARTILHADAS
# =============================================================================


def _is_default_config(config, config_type="default"):
    """
    Verifica se a configuração ainda está com valores padrão do Sheets2Anki.

    Args:
        config (dict): Configuração do deck
        config_type (str): Tipo da configuração ("root" ou "default")

    Returns:
        bool: True se ainda estiver com valores padrão do addon
    """
    try:
        if config_type == "root":
            # Valores padrão para o deck raiz
            expected_values = {
                "new_perDay": 20,
                "rev_perDay": 200,
                "new_delays": [1, 10],
                "lapse_delays": [10],
                "lapse_minInt": 1,
                "lapse_mult": 0.0,
            }
        else:
            # Valores padrão para decks remotos
            expected_values = {
                "new_perDay": 20,
                "rev_perDay": 200,
                "new_delays": [1, 10],
                "lapse_delays": [10],
                "lapse_minInt": 1,
                "lapse_mult": 0.0,
            }

        # Verificar cada valor esperado
        checks = [
            config["new"]["perDay"] == expected_values["new_perDay"],
            config["rev"]["perDay"] == expected_values["rev_perDay"],
            config["new"]["delays"] == expected_values["new_delays"],
            config["lapse"]["delays"] == expected_values["lapse_delays"],
            config["lapse"]["minInt"] == expected_values["lapse_minInt"],
            config["lapse"]["mult"] == expected_values["lapse_mult"],
        ]

        return all(checks)
    except (KeyError, TypeError):
        # Se houver erro ao acessar algum campo, considerar como personalizada
        return False


def _should_update_config_version(config):
    """
    Verifica se a configuração precisa ser atualizada para uma nova versão do addon.
    Esta função pode ser usada no futuro para aplicar atualizações de configuração
    sem sobrescrever personalizações do usuário.

    Args:
        config (dict): Configuração do deck

    Returns:
        bool: True se precisa atualizar para nova versão
    """
    # Para versões futuras, podemos adicionar lógica aqui para detectar
    # configurações antigas que precisam ser atualizadas
    config_version = config.get("sheets2anki_version", "1.0.0")
    addon_version = "1.0.0"  # Esta seria obtida do manifest.json

    # Por enquanto, sempre retorna False para não forçar atualizações
    return False


def get_or_create_sheets2anki_options_group(deck_name=None, deck_url=None):
    """
    Obtém ou cria o grupo de opções baseado no modo configurado e configuração específica do deck.

    Args:
        deck_name (str, optional): Nome do deck remoto para modo individual
        deck_url (str, optional): URL do deck para obter configuração específica

    Returns:
        int: ID do grupo de opções ou None se modo manual
    """
    from .config_manager import get_deck_options_mode, get_deck_configurations_package_name

    if not mw or not mw.col:
        add_debug_message("❌ Anki não disponível", "DECK_OPTIONS")
        return None

    # Primeiro, verificar se há uma configuração específica armazenada para este deck
    if deck_url:
        stored_package_name = get_deck_configurations_package_name(deck_url)
        if stored_package_name:
            options_group_name = stored_package_name
            add_debug_message(
                f"Usando configuração específica do deck: '{options_group_name}'",
                "DECK_OPTIONS",
            )
        else:
            # Fallback para o modo global se não há configuração específica
            mode = get_deck_options_mode()
            if mode == "manual":
                add_debug_message(
                    "Modo manual ativo - não aplicando opções automáticas", "DECK_OPTIONS"
                )
                return None
            elif mode == "individual" and deck_name:
                options_group_name = f"Sheets2Anki - {deck_name}"
                add_debug_message(
                    f"Modo individual: criando/obtendo grupo '{options_group_name}'",
                    "DECK_OPTIONS",
                )
            else:  # mode == "shared" ou fallback
                options_group_name = "Sheets2Anki - Default Options"
                add_debug_message(
                    f"Modo shared: criando/obtendo grupo '{options_group_name}'", "DECK_OPTIONS"
                )
    else:
        # Verificar modo configurado (fallback quando não há URL)
        mode = get_deck_options_mode()

        if mode == "manual":
            add_debug_message(
                "Modo manual ativo - não aplicando opções automáticas", "DECK_OPTIONS"
            )
            return None
        elif mode == "individual" and deck_name:
            options_group_name = f"Sheets2Anki - {deck_name}"
            add_debug_message(
                f"Modo individual: criando/obtendo grupo '{options_group_name}'",
                "DECK_OPTIONS",
            )
        else:  # mode == "shared" ou fallback
            options_group_name = "Sheets2Anki - Default Options"
            add_debug_message(
                f"Modo shared: criando/obtendo grupo '{options_group_name}'", "DECK_OPTIONS"
            )

    try:
        # Procurar por grupo de opções existente
        all_option_groups = mw.col.decks.all_config()

        add_debug_message(
            f"Buscando grupo '{options_group_name}' entre {len(all_option_groups)} grupos existentes",
            "DECK_OPTIONS",
        )

        for group in all_option_groups:
            if group["name"] == options_group_name:
                add_debug_message(
                    f"✅ Grupo '{options_group_name}' já existe (ID: {group['id']})",
                    "DECK_OPTIONS",
                )

                # Verificar se as configurações foram personalizadas pelo usuário
                try:
                    existing_config = mw.col.decks.get_config(group["id"])
                    if existing_config and not _is_default_config(
                        existing_config, "default" if mode == "shared" else "default"
                    ):
                        add_debug_message(
                            f"🔒 Grupo '{options_group_name}' tem configurações personalizadas - preservando",
                            "DECK_OPTIONS",
                        )
                    else:
                        add_debug_message(
                            f"📋 Grupo '{options_group_name}' ainda tem configurações padrão",
                            "DECK_OPTIONS",
                        )
                except Exception as check_error:
                    add_debug_message(
                        f"⚠️ Erro ao verificar configurações do grupo existente: {check_error}",
                        "DECK_OPTIONS",
                    )

                return group["id"]

        # Se não existe, criar novo grupo
        add_debug_message(
            f"Grupo não existe, criando novo: '{options_group_name}'", "DECK_OPTIONS"
        )
        new_group = mw.col.decks.add_config_returning_id(options_group_name)
        add_debug_message(
            f"✅ Criado novo grupo '{options_group_name}' (ID: {new_group})",
            "DECK_OPTIONS",
        )

        # IMPORTANTE: Só aplicamos configurações padrão em grupos NOVOS
        # Grupos existentes podem ter sido personalizados pelo usuário
        add_debug_message(
            f"🔧 Aplicando configurações padrão ao grupo novo '{options_group_name}'",
            "DECK_OPTIONS",
        )

        # Configurar opções padrão otimizadas para flashcards de planilhas
        try:
            config = mw.col.decks.get_config(new_group)
            if not config:
                add_debug_message(
                    f"❌ Não foi possível obter config do grupo {new_group}",
                    "DECK_OPTIONS",
                )
                return None

            # Configurações otimizadas para estudo de planilhas
            config["new"]["perDay"] = 20  # 20 novos cards por dia (bom para planilhas)
            config["rev"]["perDay"] = 200  # 200 revisões por dia
            config["new"]["delays"] = [1, 10]  # Intervalos curtos iniciais
            config["lapse"]["delays"] = [10]  # Intervalo para cards esquecidos
            config["lapse"]["minInt"] = 1  # Intervalo mínimo após lapse
            config["lapse"]["mult"] = 0.0  # Redução do intervalo após lapse

            mw.col.decks.update_config(config)
            add_debug_message(
                f"✅ Configurações padrão aplicadas ao grupo novo '{options_group_name}'",
                "DECK_OPTIONS",
            )
            add_debug_message(
                f"📊 Valores aplicados: new/day={config['new']['perDay']}, rev/day={config['rev']['perDay']}",
                "DECK_OPTIONS",
            )
        except Exception as config_error:
            add_debug_message(
                f"⚠️ Erro ao configurar grupo {new_group}: {config_error}",
                "DECK_OPTIONS",
            )
            # Ainda retornamos o ID do grupo mesmo se a configuração falhou
            add_debug_message(
                f"Retornando grupo {new_group} mesmo com erro de configuração",
                "DECK_OPTIONS",
            )

        return new_group

    except Exception as e:
        add_debug_message(
            f"❌ Erro ao criar/obter grupo de opções: {e}", "DECK_OPTIONS"
        )
        import traceback

        traceback.print_exc()
        return None


def apply_sheets2anki_options_to_deck(deck_id, deck_name=None):
    """
    Aplica o grupo de opções baseado no modo configurado a um deck específico.

    Args:
        deck_id (int): ID do deck no Anki
        deck_name (str, optional): Nome do deck remoto para modo individual

    Returns:
        bool: True se aplicado com sucesso, False caso contrário
    """
    from .config_manager import get_deck_options_mode

    if not mw or not mw.col or not deck_id:
        add_debug_message("❌ Anki ou deck_id inválido", "DECK_OPTIONS")
        return False

    # Verificar se modo manual está ativo
    mode = get_deck_options_mode()
    if mode == "manual":
        add_debug_message(
            f"Modo manual ativo - não aplicando opções ao deck {deck_id}",
            "DECK_OPTIONS",
        )
        return False

    try:
        add_debug_message(
            f"Aplicando opções ao deck {deck_id} (nome para opções: {deck_name})",
            "DECK_OPTIONS",
        )

        # Obter ou criar grupo de opções baseado no modo
        options_group_id = get_or_create_sheets2anki_options_group(deck_name)

        if not options_group_id:
            add_debug_message("❌ Falha ao obter grupo de opções", "DECK_OPTIONS")
            return False

        # Obter informações do deck
        deck = mw.col.decks.get(deck_id)
        if not deck:
            add_debug_message(f"❌ Deck não encontrado: {deck_id}", "DECK_OPTIONS")
            return False

        deck_full_name = deck["name"]

        add_debug_message(
            f"Grupo de opções obtido: {options_group_id} para deck '{deck_full_name}'",
            "DECK_OPTIONS",
        )

        # Aplicar o grupo de opções ao deck
        deck["conf"] = options_group_id
        mw.col.decks.save(deck)

        add_debug_message(
            f"✅ Grupo aplicado ao deck '{deck_full_name}' (ID: {deck_id})",
            "DECK_OPTIONS",
        )
        return True

    except Exception as e:
        add_debug_message(
            f"❌ Erro ao aplicar opções ao deck {deck_id}: {e}", "DECK_OPTIONS"
        )
        import traceback

        traceback.print_exc()
        return False


def apply_sheets2anki_options_to_all_remote_decks():
    """
    Aplica o grupo de opções baseado no modo configurado a todos os decks remotos.

    Returns:
        dict: Estatísticas da operação
    """
    from .config_manager import get_deck_options_mode
    from .config_manager import get_remote_decks

    if not mw or not mw.col:
        add_debug_message("❌ Anki não disponível", "DECK_OPTIONS")
        return {"success": False, "error": "Anki não disponível"}

    # Verificar se modo manual está ativo
    mode = get_deck_options_mode()
    if mode == "manual":
        add_debug_message(
            "Modo manual ativo - não aplicando opções automaticamente", "DECK_OPTIONS"
        )
        return {
            "success": True,
            "total_decks": 0,
            "updated_decks": 0,
            "failed_decks": 0,
            "errors": [
                "Modo manual ativo - configurações não aplicadas automaticamente"
            ],
        }

    stats = {
        "success": True,
        "total_decks": 0,
        "updated_decks": 0,
        "failed_decks": 0,
        "errors": [],
    }

    try:
        # Obter todos os decks remotos
        remote_decks = get_remote_decks()
        stats["total_decks"] = len(remote_decks)

        add_debug_message(
            f"Decks remotos encontrados: {len(remote_decks)}", "DECK_OPTIONS"
        )

        if not remote_decks:
            add_debug_message("Nenhum deck remoto encontrado", "DECK_OPTIONS")
            return stats

        mode_desc = {
            "shared": "opções compartilhadas (Default)",
            "individual": "opções individuais por deck",
        }

        add_debug_message(
            f"Aplicando {mode_desc.get(mode, 'opções')} a {len(remote_decks)} decks remotos...",
            "DECK_OPTIONS",
        )

        # Log detalhado dos decks encontrados
        for spreadsheet_id, deck_info in remote_decks.items():
            add_debug_message(
                f"Deck ID: {spreadsheet_id}, Info: {deck_info}", "DECK_OPTIONS"
            )

        # Aplicar opções a cada deck remoto
        for spreadsheet_id, deck_info in remote_decks.items():
            try:
                local_deck_id = deck_info.get("local_deck_id")
                local_deck_name = deck_info.get("local_deck_name", "Unknown")
                remote_deck_name = deck_info.get("remote_deck_name", "Unknown")

                add_debug_message(
                    f"Processando deck: {local_deck_name} (ID: {local_deck_id}, Remote: {remote_deck_name})",
                    "DECK_OPTIONS",
                )

                if not local_deck_id:
                    error_msg = f"Deck '{local_deck_name}' não tem local_deck_id"
                    stats["errors"].append(error_msg)
                    stats["failed_decks"] += 1
                    add_debug_message(f"❌ {error_msg}", "DECK_OPTIONS")
                    continue

                # Para modo individual, usar o nome do deck remoto
                deck_name_for_options = (
                    remote_deck_name if mode == "individual" else None
                )

                add_debug_message(
                    f"Nome para opções: {deck_name_for_options} (modo: {mode})",
                    "DECK_OPTIONS",
                )

                # Aplicar opções ao deck principal
                if apply_sheets2anki_options_to_deck(
                    local_deck_id, deck_name_for_options
                ):
                    stats["updated_decks"] += 1
                    add_debug_message(
                        f"✅ Deck {local_deck_name} configurado com sucesso",
                        "DECK_OPTIONS",
                    )

                    # Aplicar também aos subdecks (se existirem)
                    apply_options_to_subdecks(
                        local_deck_name,
                        remote_deck_name if mode == "individual" else None,
                    )
                else:
                    stats["failed_decks"] += 1
                    add_debug_message(
                        f"❌ Falha ao configurar deck {local_deck_name}", "DECK_OPTIONS"
                    )

            except Exception as e:
                error_msg = f"Erro no deck {spreadsheet_id}: {e}"
                stats["errors"].append(error_msg)
                stats["failed_decks"] += 1
                add_debug_message(f"❌ {error_msg}", "DECK_OPTIONS")

        add_debug_message(
            f"Operação concluída: {stats['updated_decks']}/{stats['total_decks']} decks atualizados",
            "DECK_OPTIONS",
        )

        if stats["errors"]:
            add_debug_message(
                f"{len(stats['errors'])} erros encontrados:", "DECK_OPTIONS"
            )
            for error in stats["errors"]:
                add_debug_message(f"  - {error}", "DECK_OPTIONS")

        return stats

    except Exception as e:
        error_msg = f"Erro geral na aplicação de opções: {e}"
        stats["success"] = False
        stats["errors"].append(error_msg)
        print(f"[DECK_OPTIONS] {error_msg}")
        return stats


def apply_options_to_subdecks(parent_deck_name, remote_deck_name=None):
    """
    Aplica as opções baseadas no modo a todos os subdecks de um deck pai.

    Args:
        parent_deck_name (str): Nome do deck pai
        remote_deck_name (str, optional): Nome do deck remoto para modo individual
    """
    from .config_manager import get_deck_options_mode

    if not mw or not mw.col or not parent_deck_name:
        add_debug_message("❌ Parâmetros inválidos para subdecks", "DECK_OPTIONS")
        return

    # Verificar se modo manual está ativo
    mode = get_deck_options_mode()
    if mode == "manual":
        add_debug_message(
            "Modo manual ativo - não aplicando opções aos subdecks", "DECK_OPTIONS"
        )
        return

    try:
        add_debug_message(f"Buscando subdecks de: {parent_deck_name}", "DECK_OPTIONS")

        # Buscar todos os decks que começam com o nome do deck pai
        all_decks = mw.col.decks.all()
        subdeck_count = 0

        for deck in all_decks:
            deck_name = deck["name"]

            # Verificar se é subdeck (contém :: após o nome pai)
            if deck_name.startswith(parent_deck_name + "::"):
                add_debug_message(f"Encontrado subdeck: {deck_name}", "DECK_OPTIONS")
                deck_name_for_options = (
                    remote_deck_name if mode == "individual" else None
                )

                if apply_sheets2anki_options_to_deck(deck["id"], deck_name_for_options):
                    add_debug_message(
                        f"✅ Opções aplicadas ao subdeck: {deck_name}", "DECK_OPTIONS"
                    )
                    subdeck_count += 1
                else:
                    add_debug_message(
                        f"❌ Falha ao aplicar opções ao subdeck: {deck_name}",
                        "DECK_OPTIONS",
                    )

        add_debug_message(
            f"Total de subdecks processados: {subdeck_count}", "DECK_OPTIONS"
        )

    except Exception as e:
        add_debug_message(
            f"❌ Erro ao aplicar opções aos subdecks de '{parent_deck_name}': {e}",
            "DECK_OPTIONS",
        )
        import traceback

        traceback.print_exc()


def cleanup_orphaned_deck_option_groups():
    """
    Remove grupos de opções de deck órfãos que começam com "Sheets2Anki" e não estão
    atrelados a nenhum deck (total de zero decks atrelados).

    Returns:
        int: Número de grupos de opções órfãos removidos
    """
    if not mw or not mw.col:
        print("[DECK_OPTIONS_CLEANUP] Anki não está disponível")
        return 0

    try:
        print("[DECK_OPTIONS_CLEANUP] Iniciando limpeza de grupos de opções órfãos...")

        # Obter todos os grupos de opções
        all_option_groups = mw.col.decks.all_config()
        sheets2anki_groups = []

        # Filtrar apenas grupos que começam com "Sheets2Anki"
        for group in all_option_groups:
            if group["name"].startswith("Sheets2Anki"):
                sheets2anki_groups.append(group)

        if not sheets2anki_groups:
            print("[DECK_OPTIONS_CLEANUP] Nenhum grupo Sheets2Anki encontrado")
            return 0

        # Obter todos os decks para verificar quais grupos estão em uso
        all_decks = mw.col.decks.all()
        groups_in_use = set()

        for deck in all_decks:
            conf_id = deck.get("conf", None)
            if conf_id:
                groups_in_use.add(conf_id)

        # Identificar grupos órfãos (não utilizados por nenhum deck)
        orphaned_groups = []
        for group in sheets2anki_groups:
            group_id = group["id"]
            if group_id not in groups_in_use:
                orphaned_groups.append(group)
                print(
                    f"[DECK_OPTIONS_CLEANUP] Grupo órfão encontrado: '{group['name']}' (ID: {group_id})"
                )

        # Remover grupos órfãos
        removed_count = 0
        for group in orphaned_groups:
            try:
                mw.col.decks.remove_config(group["id"])
                print(
                    f"[DECK_OPTIONS_CLEANUP] Removido: '{group['name']}' (ID: {group['id']})"
                )
                removed_count += 1
            except Exception as e:
                print(
                    f"[DECK_OPTIONS_CLEANUP] Erro ao remover grupo '{group['name']}': {e}"
                )

        if removed_count > 0:
            print(
                f"[DECK_OPTIONS_CLEANUP] Limpeza concluída: {removed_count} grupos órfãos removidos"
            )
        else:
            print("[DECK_OPTIONS_CLEANUP] Nenhum grupo órfão encontrado")

        return removed_count

    except Exception as e:
        print(f"[DECK_OPTIONS_CLEANUP] Erro na limpeza de grupos órfãos: {e}")
        return 0


def apply_automatic_deck_options_system():
    """
    Aplica o sistema automático completo de configuração de opções de deck.
    Esta função deve ser chamada ao final da sincronização e quando o usuário
    clicar no botão "Aplicar" nas configurações de deck.

    Executa as seguintes ações (quando modo automático estiver ativo):
    1. Aplica opções ao deck raiz "Sheets2Anki"
    2. Aplica opções a todos os decks remotos e subdecks
    3. Remove grupos de opções órfãos (limpeza)

    Returns:
        dict: Estatísticas da operação
    """
    add_debug_message(
        "🚀 INICIANDO sistema automático de opções de deck...", "DECK_OPTIONS_SYSTEM"
    )

    from .config_manager import get_deck_options_mode

    if not mw or not mw.col:
        add_debug_message("❌ Anki não disponível", "DECK_OPTIONS_SYSTEM")
        return {"success": False, "error": "Anki não disponível"}

    try:
        mode = get_deck_options_mode()
        add_debug_message(f"📋 Modo atual: '{mode}'", "DECK_OPTIONS_SYSTEM")
    except Exception as e:
        add_debug_message(f"❌ Erro ao obter modo: {e}", "DECK_OPTIONS_SYSTEM")
        return {"success": False, "error": f"Erro ao obter modo: {e}"}

    if mode == "manual":
        add_debug_message(
            "⏹️ Modo manual ativo - sistema automático desativado", "DECK_OPTIONS_SYSTEM"
        )
        return {
            "success": True,
            "mode": "manual",
            "root_deck_updated": False,
            "remote_decks_updated": 0,
            "cleaned_groups": 0,
            "message": "Modo manual ativo - sistema automático desativado",
        }

    add_debug_message(
        f"⚙️ Aplicando sistema automático no modo: {mode}", "DECK_OPTIONS_SYSTEM"
    )

    try:
        stats = {
            "success": True,
            "mode": mode,
            "root_deck_updated": False,
            "remote_decks_updated": 0,
            "cleaned_groups": 0,
            "errors": [],
        }

        add_debug_message(
            "🎯 ETAPA 1: Configurando deck raiz...", "DECK_OPTIONS_SYSTEM"
        )
        # 1. Aplicar opções ao deck raiz
        try:
            root_result = ensure_root_deck_has_root_options()
            stats["root_deck_updated"] = root_result
            if root_result:
                add_debug_message(
                    "✅ Deck raiz configurado com sucesso", "DECK_OPTIONS_SYSTEM"
                )
            else:
                add_debug_message(
                    "⚠️ Deck raiz não foi configurado", "DECK_OPTIONS_SYSTEM"
                )
        except Exception as e:
            error_msg = f"Erro ao configurar deck raiz: {e}"
            stats["errors"].append(error_msg)
            add_debug_message(f"❌ {error_msg}", "DECK_OPTIONS_SYSTEM")
            import traceback

            traceback.print_exc()

        add_debug_message(
            "🎯 ETAPA 2: Configurando decks remotos...", "DECK_OPTIONS_SYSTEM"
        )
        # 2. Aplicar opções a todos os decks remotos
        try:
            remote_result = apply_sheets2anki_options_to_all_remote_decks()
            if remote_result and remote_result.get("success", False):
                stats["remote_decks_updated"] = remote_result.get("updated_decks", 0)
                add_debug_message(
                    f"✅ {remote_result.get('updated_decks', 0)} decks remotos configurados",
                    "DECK_OPTIONS_SYSTEM",
                )
                if remote_result.get("errors"):
                    stats["errors"].extend(remote_result["errors"])
            else:
                error_detail = (
                    remote_result.get("error", "Erro desconhecido nos decks remotos")
                    if remote_result
                    else "Resultado vazio"
                )
                stats["errors"].append(error_detail)
                add_debug_message(
                    f"❌ Falha nos decks remotos: {error_detail}", "DECK_OPTIONS_SYSTEM"
                )
        except Exception as e:
            error_msg = f"Erro ao configurar decks remotos: {e}"
            stats["errors"].append(error_msg)
            add_debug_message(f"❌ {error_msg}", "DECK_OPTIONS_SYSTEM")
            import traceback

            traceback.print_exc()

        add_debug_message(
            "🎯 ETAPA 3: Limpeza de grupos órfãos...", "DECK_OPTIONS_SYSTEM"
        )
        # 3. Limpeza de grupos órfãos (só quando sistema automático ativo)
        try:
            cleaned_count = cleanup_orphaned_deck_option_groups()
            stats["cleaned_groups"] = cleaned_count
            if cleaned_count > 0:
                add_debug_message(
                    f"✅ {cleaned_count} grupos órfãos removidos", "DECK_OPTIONS_SYSTEM"
                )
            else:
                add_debug_message(
                    "ℹ️ Nenhum grupo órfão encontrado", "DECK_OPTIONS_SYSTEM"
                )
        except Exception as e:
            error_msg = f"Erro na limpeza de grupos órfãos: {e}"
            stats["errors"].append(error_msg)
            add_debug_message(f"❌ {error_msg}", "DECK_OPTIONS_SYSTEM")
            import traceback

            traceback.print_exc()

        add_debug_message("📊 Gerando resumo final...", "DECK_OPTIONS_SYSTEM")
        # Gerar mensagem de resumo
        messages = []
        if stats["root_deck_updated"]:
            messages.append("Deck raiz configurado")
        if stats["remote_decks_updated"] > 0:
            messages.append(
                f"{stats['remote_decks_updated']} decks remotos configurados"
            )
        if stats["cleaned_groups"] > 0:
            messages.append(f"{stats['cleaned_groups']} grupos órfãos removidos")

        if messages:
            stats["message"] = f"Sistema automático aplicado: {', '.join(messages)}"
        else:
            stats["message"] = "Sistema automático executado sem alterações"

        if stats["errors"]:
            stats["message"] += f" ({len(stats['errors'])} erros)"
            add_debug_message(
                f"⚠️ Erros encontrados: {stats['errors']}", "DECK_OPTIONS_SYSTEM"
            )

        add_debug_message(f"🎉 CONCLUÍDO: {stats['message']}", "DECK_OPTIONS_SYSTEM")
        return stats

    except Exception as e:
        error_msg = f"Erro geral no sistema automático: {e}"
        add_debug_message(f"❌ FALHA GERAL: {error_msg}", "DECK_OPTIONS_SYSTEM")
        import traceback

        traceback.print_exc()
        return {
            "success": False,
            "mode": mode if "mode" in locals() else "unknown",
            "root_deck_updated": False,
            "remote_decks_updated": 0,
            "cleaned_groups": 0,
            "error": error_msg,
        }


def ensure_root_deck_has_root_options():
    """
    Garante que o deck raiz 'Sheets2Anki' use o grupo de opções específico
    "Sheets2Anki - Root Options".

    Returns:
        bool: True se aplicado com sucesso, False caso contrário
    """
    from .config_manager import get_deck_options_mode

    if not mw or not mw.col:
        add_debug_message("Anki não está disponível", "DECK_OPTIONS")
        return False

    # Verificar se modo manual está ativo
    mode = get_deck_options_mode()
    if mode == "manual":
        add_debug_message(
            "Modo manual ativo - não aplicando opções ao deck raiz", "DECK_OPTIONS"
        )
        return False

    try:
        add_debug_message(
            f"Verificando deck raiz: '{DEFAULT_PARENT_DECK_NAME}'", "DECK_OPTIONS"
        )

        # Obter ou criar o deck raiz
        parent_deck = mw.col.decks.by_name(DEFAULT_PARENT_DECK_NAME)

        if not parent_deck:
            add_debug_message(
                f"Deck raiz '{DEFAULT_PARENT_DECK_NAME}' não existe, criando...",
                "DECK_OPTIONS",
            )
            # Criar o deck raiz se não existir
            parent_deck_id = mw.col.decks.id(DEFAULT_PARENT_DECK_NAME)
            if parent_deck_id is not None:
                parent_deck = mw.col.decks.get(parent_deck_id)
                add_debug_message(
                    f"Deck raiz criado com ID: {parent_deck_id}", "DECK_OPTIONS"
                )
            else:
                add_debug_message("❌ Falha ao criar deck raiz", "DECK_OPTIONS")
                return False
        else:
            add_debug_message(
                f"Deck raiz encontrado: ID {parent_deck['id']}", "DECK_OPTIONS"
            )

        if parent_deck:
            # Obter o grupo de opções raiz atual do deck
            current_conf_id = parent_deck.get("conf", 1)  # 1 é o padrão do Anki
            add_debug_message(
                f"Configuração atual do deck raiz: {current_conf_id}", "DECK_OPTIONS"
            )

            # Aplicar grupo específico do deck raiz
            add_debug_message(
                "Chamando get_or_create_root_options_group()...", "DECK_OPTIONS"
            )
            root_options_group_id = get_or_create_root_options_group()
            add_debug_message(
                f"get_or_create_root_options_group() retornou: {root_options_group_id}",
                "DECK_OPTIONS",
            )

            if root_options_group_id:
                if current_conf_id != root_options_group_id:
                    parent_deck["conf"] = root_options_group_id
                    mw.col.decks.save(parent_deck)
                    add_debug_message(
                        f"✅ Opções raiz aplicadas ao deck '{DEFAULT_PARENT_DECK_NAME}' (ID: {root_options_group_id})",
                        "DECK_OPTIONS",
                    )
                else:
                    add_debug_message(
                        f"✅ Deck raiz já usa as opções corretas (ID: {root_options_group_id})",
                        "DECK_OPTIONS",
                    )
                return True
            else:
                add_debug_message(
                    "❌ Falha ao obter/criar grupo de opções raiz", "DECK_OPTIONS"
                )
                return False
        else:
            add_debug_message("❌ Falha ao obter/criar deck raiz", "DECK_OPTIONS")
            return False

    except Exception as e:
        add_debug_message(
            f"❌ Erro ao aplicar opções raiz ao deck pai: {e}", "DECK_OPTIONS"
        )
        import traceback

        traceback.print_exc()
        return False


def get_or_create_root_options_group():
    """
    Obtém ou cria o grupo de opções específico para o deck raiz "Sheets2Anki - Root Options".

    Returns:
        int: ID do grupo de opções ou None se erro
    """
    if not mw or not mw.col:
        add_debug_message(
            "Anki não disponível para criar grupo de opções raiz", "DECK_OPTIONS"
        )
        return None

    options_group_name = "Sheets2Anki - Root Options"
    add_debug_message(
        f"Buscando/criando grupo de opções: '{options_group_name}'", "DECK_OPTIONS"
    )

    try:
        # Procurar por grupo de opções existente
        all_option_groups = mw.col.decks.all_config()
        add_debug_message(
            f"Total de grupos de opções encontrados: {len(all_option_groups)}",
            "DECK_OPTIONS",
        )

        for group in all_option_groups:
            if group["name"] == options_group_name:
                add_debug_message(
                    f"✅ Grupo raiz '{options_group_name}' já existe (ID: {group['id']})",
                    "DECK_OPTIONS",
                )

                # Verificar se as configurações foram personalizadas pelo usuário
                try:
                    existing_config = mw.col.decks.get_config(group["id"])
                    if existing_config and not _is_default_config(
                        existing_config, "root"
                    ):
                        add_debug_message(
                            f"🔒 Grupo raiz '{options_group_name}' tem configurações personalizadas - preservando",
                            "DECK_OPTIONS",
                        )
                    else:
                        add_debug_message(
                            f"📋 Grupo raiz '{options_group_name}' ainda tem configurações padrão",
                            "DECK_OPTIONS",
                        )
                except Exception as check_error:
                    add_debug_message(
                        f"⚠️ Erro ao verificar configurações do grupo raiz existente: {check_error}",
                        "DECK_OPTIONS",
                    )

                return group["id"]

        add_debug_message(
            f"Grupo '{options_group_name}' não existe, criando novo...", "DECK_OPTIONS"
        )
        # Se não existe, criar novo grupo
        new_group = mw.col.decks.add_config_returning_id(options_group_name)
        add_debug_message(
            f"✅ Criado novo grupo raiz '{options_group_name}' (ID: {new_group})",
            "DECK_OPTIONS",
        )

        # IMPORTANTE: Só aplicamos configurações padrão em grupos NOVOS
        # Grupos existentes podem ter sido personalizados pelo usuário
        add_debug_message(
            f"🔧 Aplicando configurações padrão ao grupo raiz novo '{options_group_name}'",
            "DECK_OPTIONS",
        )

        # Configurar opções padrão otimizadas para o deck raiz
        add_debug_message(
            f"📋 Configurando opções para o grupo raiz '{options_group_name}' (ID: {new_group})...",
            "DECK_OPTIONS",
        )

        # Usar a API correta para configurar o grupo de opções
        # Em versões recentes do Anki, usamos mw.col.decks.get_config() e mw.col.decks.update_config()
        try:
            # Obter a configuração atual do grupo
            config = mw.col.decks.get_config(new_group)
            if config is None:
                add_debug_message(
                    f"❌ Não foi possível obter configuração para grupo ID {new_group}",
                    "DECK_OPTIONS",
                )
                return new_group  # Retorna o grupo mesmo sem configurar

            add_debug_message(
                f"📋 Configuração obtida para grupo ID {new_group}", "DECK_OPTIONS"
            )

            # Configurações específicas para o deck raiz - mais conservadoras
            config["new"][
                "perDay"
            ] = 30  # 30 novos cards por dia (conservador para deck raiz)
            config["rev"]["perDay"] = 150  # 150 revisões por dia
            config["new"]["delays"] = [1, 10]  # Intervalos curtos iniciais
            config["lapse"]["delays"] = [10]  # Intervalo para cards esquecidos
            config["lapse"]["minInt"] = 1  # Intervalo mínimo após lapse
            config["lapse"]["mult"] = 0.0  # Redução do intervalo após lapse

            # Salvar as configurações
            mw.col.decks.update_config(config)
            add_debug_message(
                f"💾 Configurações salvas para grupo ID {new_group}", "DECK_OPTIONS"
            )
            add_debug_message(
                f"📊 Valores aplicados ao grupo raiz: new/day={config['new']['perDay']}, rev/day={config['rev']['perDay']}",
                "DECK_OPTIONS",
            )

        except (AttributeError, TypeError) as api_error:
            add_debug_message(
                f"⚠️ API get_config/update_config não disponível: {api_error}",
                "DECK_OPTIONS",
            )
            # Fallback para método mais antigo se disponível
            try:
                # Método alternativo para versões mais antigas
                config = mw.col.decks.confForDid(new_group)
                if config is None:
                    add_debug_message(
                        f"❌ confForDid retornou None para grupo ID {new_group}",
                        "DECK_OPTIONS",
                    )
                    return new_group

                add_debug_message(
                    f"📋 Usando confForDid como fallback para grupo ID {new_group}",
                    "DECK_OPTIONS",
                )

                config["new"]["perDay"] = 30
                config["rev"]["perDay"] = 150
                config["new"]["delays"] = [1, 10]
                config["lapse"]["delays"] = [10]
                config["lapse"]["minInt"] = 1
                config["lapse"]["mult"] = 0.0

                mw.col.decks.save(config)
                add_debug_message(
                    f"💾 Configurações salvas via fallback para grupo ID {new_group}",
                    "DECK_OPTIONS",
                )

            except Exception as fallback_error:
                add_debug_message(
                    f"❌ Falha no fallback: {fallback_error}", "DECK_OPTIONS"
                )
                # Se nenhum método funcionar, pelo menos o grupo foi criado
                add_debug_message(
                    "⚠️ Grupo criado mas configurações não aplicadas devido a incompatibilidade da API",
                    "DECK_OPTIONS",
                )
        add_debug_message(
            f"✅ Configurações padrão aplicadas ao grupo raiz '{options_group_name}'",
            "DECK_OPTIONS",
        )

        return new_group

    except Exception as e:
        add_debug_message(
            f"❌ Erro ao criar/obter grupo de opções raiz: {str(e)}", "DECK_OPTIONS"
        )
        return None


# =============================================================================
# SISTEMA DE DEBUG E LOGGING (consolidado de debug_manager.py)
# =============================================================================

from datetime import datetime
from typing import List


class DebugManager:
    """Gerenciador centralizado de debug para o Sheets2Anki."""

    def __init__(self):
        self.messages: List[str] = []
        self.is_debug_enabled = False
        self._update_debug_status()

    def _update_debug_status(self):
        """Atualiza o status de debug baseado na configuração."""
        try:
            from .config_manager import get_meta

            meta = get_meta()
            # Debug está na seção config do meta.json
            self.is_debug_enabled = meta.get("config", {}).get("debug", False)
        except Exception:
            self.is_debug_enabled = False

    def add_message(self, message: str, category: str = "DEBUG") -> None:
        """
        Adiciona uma mensagem de debug.

        Args:
            message: Mensagem de debug
            category: Categoria da mensagem (SYNC, DECK, ERROR, etc.)
        """
        if not self.is_debug_enabled:
            return

        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]  # Com milissegundos
        formatted_msg = f"[{timestamp}] [{category}] {message}"
        self.messages.append(formatted_msg)

        # Print no console do Anki
        print(formatted_msg)

        # Salvar em arquivo para fácil acesso
        self._save_to_file(formatted_msg)

    def _save_to_file(self, message: str) -> None:
        """
        Salva mensagem de debug em arquivo.

        Args:
            message: Mensagem formatada para salvar
        """
        try:
            import os

            # Determinar o caminho do arquivo de log
            addon_path = os.path.dirname(os.path.dirname(__file__))
            log_path = os.path.join(addon_path, "debug_sheets2anki.log")

            # Salvar no arquivo
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(message + "\n")
                f.flush()  # Forçar escrita imediata

        except Exception as e:
            print(f"[DEBUG_FILE] Erro ao salvar log: {e}")

    def get_messages(self) -> List[str]:
        """Retorna todas as mensagens de debug."""
        return self.messages.copy()

    def clear_messages(self) -> None:
        """Limpa todas as mensagens de debug."""
        self.messages.clear()

    def initialize_log_file(self) -> None:
        """
        Inicializa o arquivo de log com header.
        """
        try:
            import os

            addon_path = os.path.dirname(os.path.dirname(__file__))
            log_path = os.path.join(addon_path, "debug_sheets2anki.log")

            # Criar arquivo se não existir ou adicionar separador de sessão
            separator = f"\n{'='*60}\n=== NOVA SESSÃO DEBUG - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n{'='*60}\n"

            mode = "w" if not os.path.exists(log_path) else "a"
            with open(log_path, mode, encoding="utf-8") as f:
                if mode == "w":
                    f.write(
                        f"=== SHEETS2ANKI DEBUG LOG - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n"
                    )
                else:
                    f.write(separator)
                f.flush()

            print(f"[DEBUG_FILE] Log inicializado: {log_path}")

        except Exception as e:
            print(f"[DEBUG_FILE] Erro ao inicializar log: {e}")

    def get_log_path(self) -> str:
        """
        Retorna o caminho do arquivo de log.

        Returns:
            str: Caminho completo do arquivo de log
        """
        import os

        addon_path = os.path.dirname(os.path.dirname(__file__))
        return os.path.join(addon_path, "debug_sheets2anki.log")

    def get_recent_messages(self, count: int = 10) -> List[str]:
        """
        Retorna as mensagens mais recentes.

        Args:
            count: Número de mensagens recentes a retornar
        """
        return self.messages[-count:] if self.messages else []


# Instância global do gerenciador de debug
debug_manager = DebugManager()


def add_debug_message(message: str, category: str = "DEBUG") -> None:
    """
    Função de conveniência para adicionar mensagens de debug.

    Args:
        message: Mensagem de debug
        category: Categoria da mensagem
    """
    debug_manager.add_message(message, category)


def is_debug_enabled() -> bool:
    """Verifica se o debug está habilitado."""
    debug_manager._update_debug_status()
    return debug_manager.is_debug_enabled


def get_debug_messages() -> List[str]:
    """Retorna todas as mensagens de debug."""
    return debug_manager.get_messages()


def clear_debug_messages() -> None:
    """Limpa todas as mensagens de debug."""
    debug_manager.clear_messages()


def initialize_debug_log() -> None:
    """Inicializa o arquivo de debug log."""
    debug_manager.initialize_log_file()


def get_debug_log_path() -> str:
    """Retorna o caminho do arquivo de debug log."""
    return debug_manager.get_log_path()


def clear_debug_log():
    """
    Limpa o arquivo de log de debug e inicia um novo.
    """
    try:
        from datetime import datetime

        log_path = debug_manager.get_log_path()

        with open(log_path, "w", encoding="utf-8") as f:
            f.write(
                f"=== SHEETS2ANKI DEBUG LOG - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n"
            )

        print(f"[DEBUG] Log limpo: {log_path}")

    except Exception as e:
        print(f"[DEBUG] Erro ao limpar log: {e}")


# =============================================================================
# GERENCIAMENTO DE OPÇÕES DE DECK COMPARTILHADAS
# =============================================================================


def debug_log(module, message, *args):
    """
    Sistema de debug que exibe logs no console do Anki e salva em arquivo.

    Args:
        module (str): Nome do módulo (ex: "SYNC", "CONFIG", "DECK_RECREATION")
        message (str): Mensagem principal
        *args: Argumentos adicionais para logar
    """
    from .config_manager import get_meta

    try:
        meta = get_meta()
        # Debug está na seção config do meta.json
        if not meta.get("config", {}).get("debug", False):
            return

        import os
        from datetime import datetime

        # Formatar timestamp
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        # Construir mensagem completa
        full_message = f"[{timestamp}] [{module}] {message}"

        # Adicionar argumentos extras
        if args:
            extra_info = " | ".join(str(arg) for arg in args)
            full_message += f" | {extra_info}"

        # Exibir no console do Anki
        print(full_message)

        # Salvar em arquivo para fácil acesso no macOS
        try:
            addon_path = os.path.dirname(os.path.dirname(__file__))
            log_path = os.path.join(addon_path, "debug_sheets2anki.log")

            with open(log_path, "a", encoding="utf-8") as f:
                f.write(full_message + "\n")
                f.flush()
        except Exception as log_error:
            print(f"[DEBUG] Erro ao salvar log: {log_error}")

    except Exception as e:
        print(f"[DEBUG] Erro no sistema de debug: {e}")


# ========================================================================================
# FUNÇÕES DE VALIDAÇÃO (consolidado de validation.py)
# ========================================================================================


def convert_edit_url_to_tsv(url):
    """
    Converte URLs de edição do Google Sheets para formato TSV de download.
    
    Args:
        url (str): URL de edição do Google Sheets
        
    Returns:
        str: URL no formato TSV para download
        
    Raises:
        ValueError: Se a URL não for uma URL de edição válida
    """
    import re
    
    if not url or not isinstance(url, str):
        raise ValueError("URL deve ser uma string não vazia")
    
    # Verificar se é uma URL do Google Sheets
    if "docs.google.com/spreadsheets" not in url:
        raise ValueError("URL deve ser do Google Sheets")
    
    # Extrair ID da planilha para URLs de edição
    edit_pattern = r"https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)/edit"
    match = re.search(edit_pattern, url)
    
    if match:
        spreadsheet_id = match.group(1)
        # Converter para formato de export TSV (sem gid para baixar a primeira aba automaticamente)
        return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=tsv"
    
    # Se chegou aqui, não é uma URL de edição válida
    raise ValueError(
        "URL deve ser uma URL de edição do Google Sheets no formato:\n"
        "https://docs.google.com/spreadsheets/d/{ID}/edit?usp=sharing"
    )


def validate_url(url):
    """
    Valida se a URL é uma URL de edição válida do Google Sheets.

    Args:
        url (str): A URL a ser validada

    Returns:
        str: URL no formato TSV válido para download

    Raises:
        ValueError: Se a URL for inválida ou inacessível
        URLError: Se houver problemas de conectividade de rede
        HTTPError: Se o servidor retornar um erro de status
    """
    import socket
    import urllib.error
    import urllib.request

    # Verificar se a URL não está vazia
    if not url or not isinstance(url, str):
        raise ValueError("URL deve ser uma string não vazia")

    # Validar formato da URL
    if not url.startswith(("http://", "https://")):
        raise ValueError("URL inválida: Deve começar com http:// ou https://")

    # Se a URL já está no formato TSV, retornar diretamente
    if "/export?format=tsv" in url:
        return url

    # Converter para formato TSV
    try:
        tsv_url = convert_edit_url_to_tsv(url)
    except ValueError as e:
        raise ValueError(f"URL inválida: {str(e)}")

    # Testar acessibilidade da URL TSV com timeout e tratamento de erros adequado
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Sheets2Anki) AnkiAddon"  # User agent mais específico
        }
        request = urllib.request.Request(tsv_url, headers=headers)

        # USAR TIMEOUT LOCAL ao invés de global para evitar conflitos
        response = urllib.request.urlopen(request, timeout=30)  # ✅ TIMEOUT LOCAL

        if response.getcode() != 200:
            raise ValueError(
                f"URL retornou código de status inesperado: {response.getcode()}"
            )

        # Validar tipo de conteúdo
        content_type = response.headers.get("Content-Type", "").lower()
        if not any(
            valid_type in content_type
            for valid_type in ["text/tab-separated-values", "text/plain", "text/csv"]
        ):
            raise ValueError(f"URL não retorna conteúdo TSV (recebido {content_type})")

        # Retornar a URL TSV válida
        return tsv_url

    except socket.timeout:
        raise ValueError(
            "Timeout de conexão ao acessar a URL (30s). Verifique sua conexão ou tente novamente."
        )
    except urllib.error.HTTPError as e:
        if e.code == 400:
            raise ValueError(
                f"Erro HTTP 400: A planilha não está acessível publicamente.\n\n"
                f"Para corrigir:\n"
                f"1. Abra a planilha no Google Sheets\n"
                f"2. Clique em 'Compartilhar'\n"
                f"3. Mude o acesso para 'Qualquer pessoa com o link'\n"
                f"4. Defina a permissão como 'Visualizador'\n\n"
                f"Alternativamente: Arquivo → Compartilhar → Publicar na web"
            )
        else:
            raise ValueError(f"Erro HTTP {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        if isinstance(e.reason, socket.timeout):
            raise ValueError(
                "Timeout de conexão ao acessar a URL. Verifique sua conexão ou tente novamente."
            )
        elif isinstance(e.reason, socket.gaierror):
            raise ValueError("Erro de DNS. Verifique sua conexão com a internet.")
        else:
            raise ValueError(
                f"Erro ao acessar URL - Problema de rede ou servidor: {str(e.reason)}"
            )
    except Exception as e:
        raise ValueError(f"Erro inesperado ao acessar URL: {str(e)}")


# ========================================================================================
# EXCEÇÕES CUSTOMIZADAS (consolidado de exceptions.py)
# ========================================================================================


class SyncError(Exception):
    """Base exception for sync-related errors."""

    pass


class NoteProcessingError(SyncError):
    """Exception raised when processing a note fails."""

    pass


class CollectionSaveError(SyncError):
    """Exception raised when saving the collection fails."""

    pass


class ConfigurationError(Exception):
    """Exception raised for configuration-related issues."""

    pass


# =============================================================================
# FUNÇÕES DE SUBDECK (movidas para evitar import circular)
# =============================================================================


def get_subdeck_name(main_deck_name, fields, student=None):
    """
    Gera o nome do subdeck baseado no deck principal e nos campos IMPORTANCIA, TOPICO, SUBTOPICO e CONCEITO.

    Args:
        main_deck_name (str): Nome do deck principal
        fields (dict): Campos da nota com IMPORTANCIA, TOPICO, SUBTOPICO e CONCEITO
        student (str, optional): Nome do aluno para incluir na hierarquia

    Returns:
        str: Nome completo do subdeck no formato "DeckPrincipal::[Aluno::]Importancia::Topico::Subtopico::Conceito"
    """
    from . import templates_and_definitions as cols

    # Obter valores dos campos, usando valores padrão se estiverem vazios
    importancia = fields.get(cols.hierarquia_1, "").strip() or cols.DEFAULT_IMPORTANCE
    topico = fields.get(cols.hierarquia_2, "").strip() or cols.DEFAULT_TOPIC
    subtopico = fields.get(cols.hierarquia_3, "").strip() or cols.DEFAULT_SUBTOPIC
    conceito = fields.get(cols.hierarquia_4, "").strip() or cols.DEFAULT_CONCEPT

    # Criar hierarquia completa de subdecks
    if student:
        # Com aluno: Deck::Aluno::Importancia::Topico::Subtopico::Conceito
        return f"{main_deck_name}::{student}::{importancia}::{topico}::{subtopico}::{conceito}"
    else:
        # Sem aluno: Deck::Importancia::Topico::Subtopico::Conceito (compatibilidade)
        return f"{main_deck_name}::{importancia}::{topico}::{subtopico}::{conceito}"


def ensure_subdeck_exists(deck_name):
    """
    Garante que um subdeck existe, criando-o se necessário.

    Esta função suporta nomes hierárquicos como "Deck::Subdeck::Subsubdeck".

    Args:
        deck_name (str): Nome completo do deck/subdeck

    Returns:
        int: ID do deck/subdeck

    Raises:
        RuntimeError: Se mw não estiver disponível
    """
    if not mw or not hasattr(mw, "col") or not mw.col:
        raise RuntimeError("Anki main window (mw) não está disponível")

    # Verificar se o deck já existe
    did = mw.col.decks.id_for_name(deck_name)
    if did is not None:
        return did

    # Se não existe, criar o deck e todos os decks pai necessários
    return mw.col.decks.id(deck_name)


def move_note_to_subdeck(note_id, subdeck_id):
    """
    Move uma nota para um subdeck específico.

    Args:
        note_id (int): ID da nota a ser movida
        subdeck_id (int): ID do subdeck de destino

    Returns:
        bool: True se a operação foi bem-sucedida, False caso contrário

    Raises:
        RuntimeError: Se mw não estiver disponível
    """
    if not mw or not hasattr(mw, "col") or not mw.col:
        raise RuntimeError("Anki main window (mw) não está disponível")

    try:
        # Obter a nota
        note = mw.col.get_note(note_id)

        # Obter todos os cards da nota usando busca por ID de nota
        card_ids = mw.col.find_cards(f"nid:{note_id}")

        # Mover cada card para o subdeck
        for card_id in card_ids:
            card = mw.col.get_card(card_id)
            card.did = subdeck_id
            card.flush()

        return True
    except Exception as e:
        print(f"Erro ao mover nota para subdeck: {e}")
        return False


def remove_empty_subdecks(remote_decks):
    """
    Remove subdecks vazios após a sincronização.

    Esta função verifica todos os subdecks dos decks remotos e remove aqueles
    que não contêm nenhuma nota ou card.

    Args:
        remote_decks (dict): Dicionário de decks remotos

    Returns:
        int: Número de subdecks vazios removidos
    """
    if not mw or not hasattr(mw, "col") or not mw.col:
        return 0

    removed_count = 0
    processed_decks = set()

    # Coletar todos os decks principais para verificar seus subdecks
    main_deck_ids = []
    for deck_info in remote_decks.values():
        local_deck_id = deck_info.get("local_deck_id")
        if local_deck_id and local_deck_id not in processed_decks:
            main_deck_ids.append(local_deck_id)
            processed_decks.add(local_deck_id)

    # Para cada deck principal, verificar seus subdecks
    for local_deck_id in main_deck_ids:
        deck = mw.col.decks.get(local_deck_id)
        if not deck:
            continue

        main_deck_name = deck["name"]

        # Encontrar todos os subdecks deste deck principal
        all_decks = mw.col.decks.all_names_and_ids()
        subdecks = [d for d in all_decks if d.name.startswith(main_deck_name + "::")]

        # Ordenar subdecks do mais profundo para o menos profundo para evitar problemas de dependência
        subdecks.sort(key=lambda d: d.name.count("::"), reverse=True)

        # Verificar cada subdeck
        for subdeck in subdecks:
            # Contar cards no subdeck
            escaped_subdeck_name = subdeck.name.replace('"', '\\"')
            card_count = len(mw.col.find_cards(f'deck:"{escaped_subdeck_name}"'))

            # Se o subdeck estiver vazio, removê-lo
            if card_count == 0:
                try:
                    # Converter o ID para o tipo esperado pelo Anki
                    subdeck_id = mw.col.decks.id(subdeck.name)
                    if subdeck_id is not None:
                        mw.col.decks.remove([subdeck_id])
                        removed_count += 1
                except Exception as e:
                    # Ignorar erros na remoção de subdecks
                    print(f"Erro ao remover subdeck: {e}")

    return removed_count
