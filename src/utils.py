"""
Funções utilitárias para o addon Sheets2Anki.

Este módulo contém funções auxiliares utilizadas em
diferentes partes do projeto.
"""

import hashlib
import re
from .compat import mw

def extract_publication_key_from_url(url):
    """
    Extrai a chave de publicação de uma URL do Google Sheets.
    
    Args:
        url (str): URL do Google Sheets
        
    Returns:
        str: Chave de publicação extraída ou None se não encontrada
        
    Examples:
        >>> extract_publication_key_from_url("https://docs.google.com/spreadsheets/d/e/2PACX-1vSample-Key/pub?output=tsv")
        "2PACX-1vSample-Key"
    """
    if not url:
        return None
        
    # Padrão para extrair a chave de publicação entre /d/e/ e /pub
    pattern = r'/spreadsheets/d/e/([^/]+)/'
    match = re.search(pattern, url)
    
    if match:
        return match.group(1)
    
    return None

def get_publication_key_hash(url):
    """
    Gera um hash de 8 caracteres baseado na chave de publicação da URL.
    
    Args:
        url (str): URL do Google Sheets
        
    Returns:
        str: Hash de 8 caracteres ou hash da URL completa como fallback
    """
    publication_key = extract_publication_key_from_url(url)
    
    if publication_key:
        # Usar a chave de publicação para gerar o hash
        hash_obj = hashlib.md5(publication_key.encode('utf-8'))
        return hash_obj.hexdigest()[:8]
    else:
        # Fallback: usar a URL completa (comportamento anterior)
        hash_obj = hashlib.md5(url.encode('utf-8'))
        return hash_obj.hexdigest()[:8]

def update_note_type_names_for_deck_rename(url, old_remote_name, new_remote_name, debug_messages=None):
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
    from .config_manager import get_deck_note_type_ids, get_meta, save_meta, get_deck_hash
    
    def add_debug_msg(message, category="NOTE_TYPE_RENAME"):
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] [{category}] {message}"
        if debug_messages is not None:
            debug_messages.append(formatted_msg)
        print(formatted_msg)
    
    try:
        add_debug_msg(f"Atualizando strings dos note types: '{old_remote_name}' → '{new_remote_name}'")
        
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
                add_debug_msg(f"Note type ID {note_type_id_str}: '{current_name}' → '{new_name}'")
                updated_count += 1
            else:
                # Manter nome atual
                updated_note_types[note_type_id_str] = current_name
        
        # Salvar no meta.json apenas se houve mudanças
        if updated_count > 0:
            try:
                meta = get_meta()
                deck_hash = get_deck_hash(url)
                
                if "decks" in meta and deck_hash in meta["decks"]:
                    meta["decks"][deck_hash]["note_types"] = updated_note_types
                    save_meta(meta)
                    add_debug_msg(f"✅ Meta.json atualizado: {updated_count} strings de note types atualizadas")
                    
            except Exception as meta_error:
                add_debug_msg(f"❌ Erro ao atualizar meta.json: {meta_error}")
        
        add_debug_msg(f"✅ {updated_count} strings de note types atualizadas no meta.json")
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
        'total_note_types': 0,
        'synced_note_types': 0,
        'unchanged_note_types': 0,
        'error_note_types': 0,
        'errors': []
    }
    
    try:
        add_debug_msg("🔄 INICIANDO sincronização de note types...")
        
        # Obter note types configurados
        note_types_config = get_deck_note_type_ids(deck_url)
        stats['total_note_types'] = len(note_types_config)
        
        if not note_types_config:
            add_debug_msg("⚠️ Nenhum note type configurado para sincronizar")
            return stats
            
        add_debug_msg(f"📋 Sincronizando {stats['total_note_types']} note types configurados")
        
        # Listar todos os note types configurados primeiro
        for note_type_id_str, expected_name in note_types_config.items():
            add_debug_msg(f"  - ID {note_type_id_str}: '{expected_name}'")
        
        # Agora processar cada um
        for note_type_id_str, expected_name in note_types_config.items():
            try:
                note_type_id = int(note_type_id_str)
                
                add_debug_msg(f"🔍 Processando note type ID {note_type_id}...")
                
                # Buscar o note type no Anki
                note_type = col.models.get(note_type_id)
                if not note_type:
                    add_debug_msg(f"❌ Note type ID {note_type_id} não existe no Anki")
                    stats['error_note_types'] += 1
                    continue
                
                current_name = note_type.get('name', '')
                add_debug_msg(f"📝 Note type ID {note_type_id}:")
                add_debug_msg(f"    Nome atual no Anki: '{current_name}'")
                add_debug_msg(f"    Nome esperado (config): '{expected_name}'")
                
                # SEMPRE tentar atualizar para garantir sincronização
                if current_name != expected_name:
                    add_debug_msg(f"� ATUALIZANDO note type de '{current_name}' para '{expected_name}'")
                    
                    # Atualizar o nome do note type no Anki
                    note_type['name'] = expected_name
                    col.models.save(note_type)
                    
                    # Forçar save da collection para garantir persistência imediata
                    col.save()
                    add_debug_msg(f"💾 Collection salva para garantir persistência")
                    
                    # Verificar se realmente foi atualizado
                    updated_note_type = col.models.get(note_type_id)
                    if updated_note_type and updated_note_type.get('name') == expected_name:
                        stats['synced_note_types'] += 1
                        add_debug_msg(f"✅ Note type atualizado com SUCESSO")
                    else:
                        add_debug_msg(f"❌ FALHA ao atualizar note type - verificação pós-save falhou")
                        stats['error_note_types'] += 1
                else:
                    stats['unchanged_note_types'] += 1
                    add_debug_msg(f"✅ Note type já está sincronizado")
                    
            except Exception as note_type_error:
                stats['error_note_types'] += 1
                error_msg = f"Erro ao sincronizar note type {note_type_id_str}: {note_type_error}"
                stats['errors'].append(error_msg)
                add_debug_msg(f"❌ {error_msg}")
                import traceback
                add_debug_msg(f"Traceback: {traceback.format_exc()}")
        
        add_debug_msg(f"📊 RESULTADO: {stats['synced_note_types']} sincronizados, {stats['unchanged_note_types']} inalterados, {stats['error_note_types']} erros")
        
        # Limpeza de note types órfãos na configuração
        try:
            orphaned_count = cleanup_orphaned_note_types()
            if orphaned_count > 0:
                add_debug_msg(f"🧹 Limpeza: {orphaned_count} note types órfãos removidos da configuração")
        except Exception as cleanup_error:
            add_debug_msg(f"⚠️ Erro na limpeza de órfãos: {cleanup_error}")
        
        return stats
        
    except Exception as e:
        add_debug_msg(f"❌ ERRO geral na sincronização: {e}")
        stats['errors'].append(f"Erro geral: {e}")
        return stats

def sync_deck_name_with_config(col, deck_url, debug_messages=None):
    """
    Garante que o nome do deck local no Anki corresponda ao local_deck_name no meta.json.
    Esta função usa local_deck_name como source of truth.
    
    Args:
        col: Collection do Anki
        deck_url (str): URL do deck remoto
        debug_messages (list, optional): Lista para debug
        
    Returns:
        tuple: (deck_id, synced_name) ou None se não encontrado
    """
    from .config_manager import get_deck_local_id, get_deck_local_name
    
    def add_debug_msg(message, category="DECK_SYNC"):
        """Helper para adicionar mensagens de debug com timestamp."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] [{category}] {message}"
        if debug_messages is not None:
            debug_messages.append(formatted_msg)
        print(formatted_msg)
    
    try:
        # Obter informações do meta.json
        local_deck_id = get_deck_local_id(deck_url)
        expected_name = get_deck_local_name(deck_url)
        
        if not local_deck_id or not expected_name:
            add_debug_msg(f"Deck não encontrado na configuração: ID={local_deck_id}, Nome='{expected_name}'")
            return None
            
        add_debug_msg(f"Sincronizando deck ID {local_deck_id} com nome esperado: '{expected_name}'")
        
        # Verificar se o deck existe no Anki
        deck = col.decks.get(local_deck_id)
        if not deck:
            add_debug_msg(f"❌ ERRO: Deck ID {local_deck_id} não existe no Anki")
            return None
        
        current_name = deck["name"]
        add_debug_msg(f"Nome atual no Anki: '{current_name}'")
        
        # Se os nomes são diferentes, atualizar no Anki
        if current_name != expected_name:
            add_debug_msg(f"📝 ATUALIZANDO nome do deck de '{current_name}' para '{expected_name}'")
            
            # Atualizar o nome do deck no Anki
            deck["name"] = expected_name
            col.decks.save(deck)
            
            add_debug_msg(f"✅ Nome do deck atualizado com sucesso")
            return (local_deck_id, expected_name)
        else:
            add_debug_msg(f"✅ Nome do deck já está sincronizado")
            return (local_deck_id, current_name)
            
    except Exception as e:
        add_debug_msg(f"❌ ERRO ao sincronizar nome do deck: {e}")
        import traceback
        add_debug_msg(f"Detalhes: {traceback.format_exc()}")
        return None

def get_or_create_deck(col, deckName):
    """
    Cria ou obtém um deck existente no Anki.
    
    Args:
        col: Collection do Anki
        deckName: Nome do deck
        
    Returns:
        tuple: (deck_id, actual_name) onde deck_id é o ID do deck e actual_name é o nome real usado
        
    Raises:
        ValueError: Se o nome do deck for inválido
    """
    if not deckName or not isinstance(deckName, str) or deckName.strip() == "" or deckName.strip().lower() == "default":
        raise ValueError("Nome de deck inválido ou proibido para sincronização: '%s'" % deckName)
    
    deck = col.decks.by_name(deckName)
    if deck is None:
        try:
            deck_id = col.decks.id(deckName)
            # Obter o deck recém-criado para verificar o nome real usado
            new_deck = col.decks.get(deck_id)
            actual_name = new_deck["name"] if new_deck else deckName
        except Exception as e:
            raise ValueError(f"Não foi possível criar o deck '{deckName}': {str(e)}")
    else:
        deck_id = deck["id"]
        actual_name = deck["name"]
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
        add_debug_msg(f"Registrando note type: ID={note_type_id}, Nome='{note_type_name}'")
        
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
        card_ids = mw.col.find_cards(f"deck:{local_deck_id}")
        add_debug_msg(f"Encontrados {len(card_ids)} cards no deck")
        
        if not card_ids:
            add_debug_msg("⚠️ Nenhum card encontrado no deck - note types serão capturados durante a sincronização")
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
                    add_debug_msg(f"Ignorando card {card_id} - note type não encontrado")
                    continue
                    
                note_type_id = note_type['id']
                note_type_name = note_type['name']
                
                note_type_ids.add(note_type_id)
                
                if note_type_id not in note_type_info:
                    note_type_info[note_type_id] = {'name': note_type_name, 'count': 0}
                note_type_info[note_type_id]['count'] += 1
                
            except Exception as card_error:
                add_debug_msg(f"Erro ao processar card {card_id}: {card_error}")
                continue
        
        add_debug_msg(f"Note types únicos encontrados: {len(note_type_ids)}")
        
        # Registrar cada note type encontrado
        for note_type_id in note_type_ids:
            info = note_type_info[note_type_id]
            full_name = info['name']  # Nome completo do note type
            count = info['count']
            
            add_debug_msg(f"Registrando: ID {note_type_id}, Nome completo '{full_name}', Cards: {count}")
            
            # Usar o nome completo como source of truth (não extrair partes)
            add_note_type_id_to_deck(url, note_type_id, full_name, debug_messages)
        
        add_debug_msg(f"✅ SUCESSO: Capturados {len(note_type_ids)} note types de cards existentes")
        
    except Exception as e:
        add_debug_msg(f"❌ ERRO na captura inteligente: {e}")
        import traceback
        add_debug_msg(f"Detalhes: {traceback.format_exc()}")

def capture_deck_note_type_ids(url, remote_deck_name, enabled_students=None, debug_messages=None):
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
            add_debug_msg(f"Usando captura inteligente para deck local ID: {local_deck_id}")
            capture_deck_note_type_ids_from_cards(url, local_deck_id, debug_messages)
        else:
            add_debug_msg("⚠️ Deck local não encontrado - note types serão registrados durante criação")
            
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
    from .config_manager import get_deck_note_type_ids, remove_note_type_id_from_deck, cleanup_invalid_note_type_ids
    
    if not mw or not mw.col:
        print("[DELETE_BY_IDS] Anki não disponível")
        return 0
        
    try:
        # Primeiro limpar IDs inválidos
        cleanup_invalid_note_type_ids()
        
        # Obter IDs válidos
        note_type_ids = get_deck_note_type_ids(url)
        
        if not note_type_ids:
            print(f"[DELETE_BY_IDS] Nenhum note type ID encontrado para o deck")
            return 0
        
        deleted_count = 0
        
        for note_type_id in note_type_ids.copy():  # Usar cópia para modificar durante iteração
            model = mw.col.models.get(note_type_id)
            if model:
                model_name = model['name']
                
                try:
                    # Verificar se há notas usando este note type
                    note_ids = mw.col.models.nids(note_type_id)
                    if note_ids:
                        print(f"[DELETE_BY_IDS] Note type '{model_name}' tem {len(note_ids)} notas, deletando-as primeiro...")
                        mw.col.remove_notes(note_ids)
                    
                    # Deletar o note type
                    mw.col.models.rem(model)
                    deleted_count += 1
                    
                    # Remover ID da configuração
                    remove_note_type_id_from_deck(url, note_type_id)
                    
                    print(f"[DELETE_BY_IDS] Note type '{model_name}' (ID: {note_type_id}) deletado com sucesso")
                    
                except Exception as e:
                    print(f"[DELETE_BY_IDS] Erro ao deletar note type '{model_name}' (ID: {note_type_id}): {e}")
            else:
                # ID não existe mais, remover da configuração
                remove_note_type_id_from_deck(url, note_type_id)
                print(f"[DELETE_BY_IDS] Note type ID {note_type_id} não encontrado, removido da configuração")
        
        if deleted_count > 0:
            mw.col.save()
            print(f"[DELETE_BY_IDS] Operação concluída: {deleted_count} note types deletados")
        
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
            print(f"[RENAME_NOTE_TYPE] Anki não está disponível")
            return False
        
        # Obter o model existente
        model = mw.col.models.get(note_type_id)  # type: ignore
        if not model:
            print(f"[RENAME_NOTE_TYPE] Note type ID {note_type_id} não encontrado")
            return False
        
        old_name = model['name']
        
        # Só renomear se o nome for diferente
        if old_name == new_name:
            print(f"[RENAME_NOTE_TYPE] Note type {note_type_id} já tem o nome correto: '{new_name}'")
            return True
        
        print(f"[RENAME_NOTE_TYPE] Renomeando note type {note_type_id} de '{old_name}' para '{new_name}'")
        
        # Alterar apenas o nome do model existente
        model['name'] = new_name
        
        # Salvar as alterações
        mw.col.models.save(model)
        
        print(f"[RENAME_NOTE_TYPE] ✅ Note type renomeado com sucesso!")
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
        print(f"[CLEANUP_ORPHANED] Iniciando limpeza de note types órfãos...")
        
        if not mw or not mw.col:
            print(f"[CLEANUP_ORPHANED] Anki não está disponível")
            return 0
        
        from .config_manager import get_meta, save_meta
        
        meta = get_meta()
        if not meta or "decks" not in meta:
            print(f"[CLEANUP_ORPHANED] Nenhuma configuração de decks encontrada")
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
                    model = mw.col.models.get(note_type_id)  # type: ignore
                    
                    if not model:
                        orphaned_ids.append(note_type_id_str)
                        print(f"[CLEANUP_ORPHANED] Órfão encontrado: ID {note_type_id_str} - '{note_type_name}'")
                        
                except (ValueError, TypeError):
                    # ID inválido, remover também
                    orphaned_ids.append(note_type_id_str)
                    print(f"[CLEANUP_ORPHANED] ID inválido encontrado: '{note_type_id_str}'")
            
            # Remover órfãos da configuração
            for orphaned_id in orphaned_ids:
                del deck_info["note_types"][orphaned_id]
                cleaned_count += 1
                print(f"[CLEANUP_ORPHANED] Removido órfão: ID {orphaned_id}")
        
        if cleaned_count > 0:
            save_meta(meta)
            print(f"[CLEANUP_ORPHANED] Limpeza concluída: {cleaned_count} note types órfãos removidos")
        else:
            print(f"[CLEANUP_ORPHANED] Nenhum note type órfão encontrado")
        
        return cleaned_count
        
    except Exception as e:
        print(f"[CLEANUP_ORPHANED] Erro na limpeza: {e}")
        import traceback
        traceback.print_exc()
        return 0

