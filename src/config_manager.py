"""
Gerenciador de configurações para o addon Sheets2Anki.

Este módulo implementa um sistema de configuração hierárquico que utiliza:
- config.json: Configurações padrão do addon
- meta.json: Configurações do usuário e dados de decks remotos (fonte de verdade)

Funcionalidades:
- Carregamento e salvamento de configurações
- Migração de configurações antigas
- Gerenciamento de preferências do usuário
- Controle de decks remotos
"""

import json
import os
import time
from .compat import mw, showWarning
from .utils import get_publication_key_hash

# =============================================================================
# FUNÇÕES UTILITÁRIAS PARA HASH
# =============================================================================

def get_deck_hash(url):
    """
    Gera um hash para identificar um deck baseado na chave de publicação da URL.
    
    Args:
        url (str): URL do deck remoto
        
    Returns:
        str: Hash de 8 caracteres baseado na chave de publicação
    """
    return get_publication_key_hash(url)

# =============================================================================
# CONSTANTES DE CONFIGURAÇÃO
# =============================================================================

DEFAULT_CONFIG = {
    "debug": False,
    "auto_sync_on_startup": False,
    "backup_before_sync": True,
    "max_sync_retries": 3,
    "sync_timeout_seconds": 30,
    "show_sync_notifications": True
}

DEFAULT_META = {
    "config": {
        "debug": False,
        "auto_sync_on_startup": False,
        "backup_before_sync": True,
        "max_sync_retries": 3,
        "sync_timeout_seconds": 30,
        "show_sync_notifications": True,
        "deck_options_mode": "shared"  # "shared", "individual", "manual"
    },
    "students": {
        "available_students": [],
        "enabled_students": [],
        "last_updated": None
    },
    "decks": {}
}

# =============================================================================
# FUNÇÕES PRINCIPAIS
# =============================================================================

def get_config():
    """
    Carrega a configuração padrão do config.json.
    
    Returns:
        dict: Configuração padrão do addon
    """
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Mesclar com padrões para garantir compatibilidade
            merged_config = DEFAULT_CONFIG.copy()
            merged_config.update(config)
            return merged_config
        else:
            return DEFAULT_CONFIG.copy()
    except Exception as e:
        showWarning(f"Erro ao carregar config.json: {str(e)}. Usando configuração padrão.")
        return DEFAULT_CONFIG.copy()

def get_meta():
    """
    Carrega os metadados do usuário do meta.json (fonte de verdade).
    
    Returns:
        dict: Metadados do usuário incluindo preferências e decks remotos
    """
    try:
        import json
        import os
        
        # Carregar diretamente do arquivo meta.json
        addon_path = os.path.dirname(os.path.dirname(__file__))
        meta_path = os.path.join(addon_path, "meta.json")
        
        if os.path.exists(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
        else:
            meta = DEFAULT_META.copy()
        
        # Garantir estrutura adequada
        meta = _ensure_meta_structure(meta)
        
        return meta
    except Exception as e:
        showWarning(f"Erro ao carregar meta.json: {str(e)}. Usando configuração padrão.")
        return DEFAULT_META.copy()

def save_meta(meta):
    """
    Salva os metadados do usuário no meta.json.
    
    Args:
        meta (dict): Metadados para salvar
    """
    try:
        import json
        import os
        
        # Salvar diretamente no arquivo meta.json
        addon_path = os.path.dirname(os.path.dirname(__file__))
        meta_path = os.path.join(addon_path, "meta.json")
        
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=4, ensure_ascii=False)
    except Exception as e:
        showWarning(f"Erro ao salvar meta.json: {str(e)}")

def get_remote_decks():
    """
    Obtém os decks remotos configurados com estrutura baseada em hash.
    
    Returns:
        dict: Dicionário {hash_key: deck_info} onde deck_info contém:
            - local_deck_id: ID do deck no Anki
            - local_deck_name: Nome do deck no Anki
            - remote_deck_url: URL do deck remoto
            - remote_deck_name: Nome do arquivo remoto
            - note_types: Dict {note_type_id: expected_name}
    """
    meta = get_meta()
    return meta.get("decks", {})

def save_remote_decks(remote_decks):
    """
    Salva os decks remotos na configuração usando estrutura baseada em hash.
    
    Args:
        remote_decks (dict): Dicionário {hash_key: deck_info}
    """
    # Debug: Log do que está sendo salvo
    from .utils import add_debug_message
    add_debug_message("=== SALVANDO DECK INFO NO META.JSON ===", "Config Manager")
    for hash_key, deck_info in remote_decks.items():
        local_deck_id = deck_info.get("local_deck_id", "N/A")
        local_deck_name = deck_info.get("local_deck_name", "N/A")
        add_debug_message(f"Hash {hash_key}: local_deck_id={local_deck_id}, local_deck_name='{local_deck_name}'", "Config Manager")
    
    meta = get_meta()
    meta["decks"] = remote_decks
    save_meta(meta)
    
    add_debug_message("✓ Deck info salvo no meta.json com sucesso", "Config Manager")

def add_remote_deck(url, deck_info):
    """
    Adiciona um deck remoto à configuração usando hash como chave.
    
    Args:
        url (str): URL do deck remoto
        deck_info (dict): Informações do deck na nova estrutura
    """
    # Gerar hash da chave de publicação
    url_hash = get_deck_hash(url)
    
    remote_decks = get_remote_decks()
    remote_decks[url_hash] = deck_info
    save_remote_decks(remote_decks)

def create_deck_info(url, local_deck_id, local_deck_name, remote_deck_name=None, **additional_info):
    """
    Cria um dicionário de informações do deck com a nova estrutura.
    
    Args:
        url (str): URL do deck remoto
        local_deck_id (int): ID do deck no Anki
        local_deck_name (str): Nome do deck no Anki
        remote_deck_name (str, optional): Nome do arquivo remoto
        **additional_info: Campos adicionais
        
    Returns:
        dict: Estrutura completa do deck
    """
    # Resolver conflitos no remote_deck_name usando DeckNameManager
    from .deck_manager import DeckNameManager
    resolved_remote_name = DeckNameManager.resolve_remote_name_conflict(url, remote_deck_name or "")
    
    deck_info = {
        "remote_deck_url": url,
        "local_deck_id": local_deck_id,
        "local_deck_name": local_deck_name,
        "remote_deck_name": resolved_remote_name,
        "note_types": {},
        "is_test_deck": False,
        "is_sync": True
    }
    
    # Adicionar campos extras se fornecidos
    deck_info.update(additional_info)
    
    return deck_info

def add_remote_deck_simple(url, local_deck_id, local_deck_name, remote_deck_name=None, **additional_info):
    """
    Versão simplificada para adicionar deck remoto com estrutura limpa.
    
    Args:
        url (str): URL do deck remoto
        local_deck_id (int): ID do deck no Anki
        local_deck_name (str): Nome do deck no Anki
        remote_deck_name (str, optional): Nome do arquivo remoto
        **additional_info: Campos adicionais
    """
    deck_info = create_deck_info(url, local_deck_id, local_deck_name, remote_deck_name, **additional_info)
    add_remote_deck(url, deck_info)

def get_deck_local_name(url):
    """
    Obtém o nome local de um deck a partir da sua URL.
    
    Args:
        url (str): URL do deck
        
    Returns:
        str: Nome local do deck ou None se não encontrado
    """
    # Gerar hash da chave de publicação
    url_hash = get_deck_hash(url)
    
    remote_decks = get_remote_decks()
    deck_info = remote_decks.get(url_hash, {})
    
    return deck_info.get("local_deck_name")

def get_deck_remote_name(url):
    """
    Obtém o nome remoto de um deck a partir da sua URL.
    
    Args:
        url (str): URL do deck
        
    Returns:
        str: Nome remoto do deck ou None se não encontrado
    """
    # Gerar hash da chave de publicação
    url_hash = get_deck_hash(url)
    
    remote_decks = get_remote_decks()
    deck_info = remote_decks.get(url_hash, {})
    
    # Se existe na nova estrutura, usar
    if "remote_deck_name" in deck_info:
        return deck_info["remote_deck_name"]
    
    # Fallback: extrair da URL se não existe
    if url:
        # Se o prefixo mudou, extrair novamente da URL para manter consistência
        from .deck_manager import DeckNameManager
        return DeckNameManager.extract_remote_name_from_url(url)
    
    return None

def remove_remote_deck(url):
    """
    Remove um deck remoto da configuração.
    
    Args:
        url (str): URL do deck remoto a ser removido
    """
    # Gerar hash da chave de publicação
    url_hash = get_deck_hash(url)
    
    remote_decks = get_remote_decks()
    if url_hash in remote_decks:
        del remote_decks[url_hash]
        save_remote_decks(remote_decks)

def disconnect_deck(url):
    """
    Remove completamente um deck remoto do sistema.
    Esta ação é irreversível - o deck só pode ser reconectado se for re-cadastrado.
    
    Args:
        url (str): URL do deck a ser desconectado
    """
    # Gerar hash da chave de publicação
    url_hash = get_deck_hash(url)
    
    meta = get_meta()
    remote_decks = meta.get("decks", {})
    
    # Remover completamente o deck da lista de decks remotos
    if url_hash in remote_decks:
        del remote_decks[url_hash]
        meta["decks"] = remote_decks  # type: ignore
        save_meta(meta)

def is_deck_disconnected(url):
    """
    Verifica se um deck está desconectado (não existe mais na configuração).
    
    Args:
        url (str): URL do deck
        
    Returns:
        bool: True se desconectado (não existe), False se existe
    """
    # Gerar hash da chave de publicação
    url_hash = get_deck_hash(url)
    
    remote_decks = get_remote_decks()
    return url_hash not in remote_decks

def get_active_decks():
    """
    Obtém todos os decks remotos ativos.
    Na nova lógica, todos os decks em decks são considerados ativos.
    
    Returns:
        dict: Dicionário com URLs como chaves e dados dos decks como valores
    """
    meta = get_meta()
    return meta.get("decks", {})

def is_local_deck_missing(url):
    """
    Verifica se o deck local correspondente a um deck remoto foi deletado.
    
    Args:
        url (str): URL do deck remoto
        
    Returns:
        bool: True se o deck remoto existe mas o deck local não
    """
    meta = get_meta()
    remote_decks = meta.get("decks", {})
    
    if url not in remote_decks:
        return False  # Deck remoto não existe
    
    deck_info = remote_decks[url]
    deck_id = deck_info.get("deck_id")
    
    if not deck_id:
        return True  # Deck remoto não tem ID local
    
    try:
        # Verificar se o deck local existe no Anki
        if mw.col and mw.col.decks:
            deck = mw.col.decks.get(deck_id)
            return deck is None
        else:
            return True  # Collection ou decks não disponível
    except:
        return True  # Erro ao acessar deck = deck não existe

def get_deck_naming_mode():
    """
    Obtém o modo de nomeação de decks atual.
    
    Returns:
        str: Sempre "automatic" (comportamento fixo)
    """
    return "automatic"

def set_deck_naming_mode(mode):
    """
    Define o modo de nomeação de decks.
    
    Args:
        mode (str): Ignorado - comportamento sempre automático
    """
    # Função mantida para compatibilidade, mas não faz nada
    pass
        
def get_create_subdecks_setting():
    """
    Verifica se a criação de subdecks está habilitada.
    
    Returns:
        bool: Sempre True (comportamento fixo)
    """
    return True

def set_create_subdecks_setting(enabled):
    """
    Define se a criação de subdecks está habilitada.
    
    Args:
        enabled (bool): Ignorado - comportamento sempre habilitado
    """
    # Função mantida para compatibilidade, mas não faz nada
    pass

# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def verify_and_update_deck_info(url, local_deck_id, local_deck_name, silent=False):
    """
    Verifica e atualiza as informações do deck na configuração usando nova estrutura.
    
    Esta função garante que:
    1. O local_deck_id está atualizado na configuração
    2. O local_deck_name está atualizado na configuração
    3. O remote_deck_name está sincronizado com a URL atual
    4. As informações correspondem à realidade atual do Anki
    
    Args:
        url (str): URL do deck remoto
        local_deck_id (int): ID atual do deck no Anki
        local_deck_name (str): Nome local atual do deck no Anki
        silent (bool): Se True, não mostra notificações
        
    Returns:
        bool: True se houve atualizações, False caso contrário
    """
    # Gerar hash da chave de publicação
    url_hash = get_deck_hash(url)
    
    remote_decks = get_remote_decks()
    
    # Verificar se o deck existe na configuração
    if url_hash not in remote_decks:
        return False
    
    deck_info = remote_decks[url_hash]
    updated = False
    
    # Verificar se o local_deck_id precisa ser atualizado
    current_local_deck_id = deck_info.get("local_deck_id")
    if current_local_deck_id != local_deck_id:
        deck_info["local_deck_id"] = local_deck_id
    # Verificar se o local_deck_name precisa ser atualizado
    current_local_deck_name = deck_info.get("local_deck_name")
    if current_local_deck_name != local_deck_name:
        deck_info["local_deck_name"] = local_deck_name
        updated = True
    
    # Verificar se o remote_deck_name precisa ser atualizado usando DeckNameManager
    from .deck_manager import DeckNameManager
    current_remote_name = DeckNameManager.extract_remote_name_from_url(url)
    stored_remote_name = deck_info.get("remote_deck_name")
    if stored_remote_name != current_remote_name:
        resolved_remote_name = DeckNameManager.resolve_remote_name_conflict(url, current_remote_name)
        deck_info["remote_deck_name"] = resolved_remote_name
        updated = True
        if not silent:
            print(f"[Sheets2Anki] Remote deck name updated from '{stored_remote_name}' to '{resolved_remote_name}'")
    
    # Salvar as alterações se houve atualizações
    if updated:
        save_remote_decks(remote_decks)
        return True
    
    return False

def get_deck_info_by_id(local_deck_id):
    """
    Obtém informações do deck remoto pelo ID do deck local.
    
    Args:
        local_deck_id (int): ID do deck no Anki
        
    Returns:
        tuple: (url_hash, deck_info) ou (None, None) se não encontrado
    """
    remote_decks = get_remote_decks()
    
    for url_hash, deck_info in remote_decks.items():
        if deck_info.get("local_deck_id") == local_deck_id:
            return url_hash, deck_info
    
    return None, None

def detect_deck_name_changes(skip_deleted=False):
    """
    Detecta mudanças nos nomes dos decks locais e atualiza a configuração.
    
    Esta função verifica todos os decks remotos configurados e atualiza
    suas informações se o nome do deck foi alterado no Anki.
    
    Args:
        skip_deleted: Se True, não atualiza nomes de decks que foram deletados
    
    Returns:
        list: Lista de hash keys dos decks que foram atualizados
    """
    from .compat import mw
    
    remote_decks = get_remote_decks()
    updated_hashes = []
    
    for url_hash, deck_info in remote_decks.items():
        local_deck_id = deck_info.get("local_deck_id")
        if not local_deck_id:
            continue
            
        # Obter deck atual do Anki
        if not mw.col or not mw.col.decks:
            continue  # Collection ou decks não disponível
            
        deck = mw.col.decks.get(local_deck_id)
        
        # Se o deck foi deletado e skip_deleted=True, pular
        if not deck and skip_deleted:
            continue
            
        # Se o deck existe, atualizar o nome
        if deck:
            current_name = deck.get("name", "")
            saved_name = deck_info.get("local_deck_name", "")
            
            # Verificar se o nome mudou
            if current_name and current_name != saved_name:
                # Atualizar nome na configuração
                deck_info["local_deck_name"] = current_name
                updated_hashes.append(url_hash)
    
    # Salvar alterações se houve atualizações
    if updated_hashes:
        save_remote_decks(remote_decks)
    
    return updated_hashes

def get_sync_selection():
    """
    Obtém a seleção persistente de decks para sincronização.
    
    Returns:
        dict: Dicionário com URLs como chaves e bool como valores
    """
    remote_decks = get_remote_decks()
    selection = {}
    
    for url, deck_info in remote_decks.items():
        # Usar o atributo is_sync dos dados do deck, padrão True se não existir
        selection[url] = deck_info.get("is_sync", True)
    
    return selection

def save_sync_selection(selection):
    """
    Salva a seleção persistente de decks para sincronização.
    
    Args:
        selection (dict): Dicionário com URLs como chaves e bool como valores
    """
    remote_decks = get_remote_decks()
    
    # Atualizar o atributo is_sync em cada deck
    for url, is_selected in selection.items():
        if url in remote_decks:
            remote_decks[url]["is_sync"] = is_selected
    
    save_remote_decks(remote_decks)

def update_sync_selection(url, selected):
    """
    Atualiza a seleção de um deck específico.
    
    Args:
        url (str): URL do deck
        selected (bool): Se o deck está selecionado
    """
    remote_decks = get_remote_decks()
    
    if url in remote_decks:
        remote_decks[url]["is_sync"] = selected
        save_remote_decks(remote_decks)

def clear_sync_selection():
    """
    Limpa toda a seleção persistente (define todos como não selecionados).
    """
    remote_decks = get_remote_decks()
    
    for url in remote_decks:
        remote_decks[url]["is_sync"] = False
    
    save_remote_decks(remote_decks)

def set_all_sync_selection(selected=True):
    """
    Define todos os decks como selecionados ou não selecionados.
    
    Args:
        selected (bool): True para selecionar todos, False para desmarcar todos
    """
    remote_decks = get_remote_decks()
    
    for url in remote_decks:
        remote_decks[url]["is_sync"] = selected
    
    save_remote_decks(remote_decks)



def _ensure_meta_structure(meta):
    """
    Garante que a estrutura do meta.json está correta.
    
    Args:
        meta (dict): Metadados a serem verificados
        
    Returns:
        dict: Metadados com estrutura corrigida
    """
    # Garantir chaves principais
    if "decks" not in meta:
        meta["decks"] = {}
    
    # Migrar dados de remote_decks para decks se necessário
    if "remote_decks" in meta and meta["remote_decks"] and not meta.get("decks"):
        meta["decks"] = meta["remote_decks"]
    
    # Remover chaves antigas desnecessárias
    if "remote_decks" in meta:
        del meta["remote_decks"]
    if "user_preferences" in meta:
        del meta["user_preferences"]
    
    # Garantir que todos os decks têm o atributo is_sync
    for url, deck_info in meta["decks"].items():
        if "is_sync" not in deck_info:
            deck_info["is_sync"] = True  # Padrão: selecionado para sincronização
    
    # Garantir estrutura de students
    if "students" not in meta:
        meta["students"] = {
            "enabled_students": [],
            "student_sync_enabled": False,
            "last_updated": None
        }
    
    return meta


# =============================================================================
# FUNÇÕES DE GERENCIAMENTO GLOBAL DE ALUNOS
# =============================================================================

def get_global_student_config():
    """
    Obtém a configuração global de alunos.
    
    Returns:
        dict: Configuração de alunos com chaves:
            - available_students: lista de todos os alunos conhecidos
            - enabled_students: lista de alunos habilitados
            - student_sync_enabled: se o filtro de alunos está ativo
            - auto_remove_disabled_students: se deve remover dados de alunos desabilitados
            - last_updated: timestamp da última atualização
    """
    meta = get_meta()
    return meta.get("students", {
        "available_students": [],
        "enabled_students": [],
        "auto_remove_disabled_students": False,
        "sync_missing_students_notes": False,
        "last_updated": None
    })

def save_global_student_config(enabled_students, available_students=None, auto_remove_disabled_students=None, sync_missing_students_notes=None):
    """
    Salva a configuração global de alunos.
    
    Args:
        enabled_students (list): Lista de alunos habilitados para sincronização
        available_students (list): Lista de todos os alunos conhecidos (opcional)
        auto_remove_disabled_students (bool): Se deve remover dados de alunos desabilitados (opcional)
        sync_missing_students_notes (bool): Se deve sincronizar notas sem alunos específicos (opcional)
    """
    import time
    
    meta = get_meta()
    
    # Obter configuração atual
    current_config = meta.get("students", {})
    current_available = current_config.get("available_students", [])
    
    # Remover duplicatas das listas de estudantes (case-sensitive)
    final_enabled = list(dict.fromkeys(enabled_students)) if enabled_students else []
    
    if available_students is not None:
        final_available = list(dict.fromkeys(available_students))
    else:
        # Se não fornecido, manter a lista atual e adicionar os habilitados
        all_students = list(current_available) + final_enabled
        final_available = list(dict.fromkeys(all_students))
    
    # Determinar valor para auto_remove_disabled_students
    if auto_remove_disabled_students is not None:
        final_auto_remove = bool(auto_remove_disabled_students)
    else:
        final_auto_remove = current_config.get("auto_remove_disabled_students", False)
    
    # Determinar valor para sync_missing_students_notes
    if sync_missing_students_notes is not None:
        final_sync_missing = bool(sync_missing_students_notes)
    else:
        final_sync_missing = current_config.get("sync_missing_students_notes", False)
    
    meta["students"] = {
        "available_students": final_available,
        "enabled_students": final_enabled,
        "auto_remove_disabled_students": final_auto_remove,
        "sync_missing_students_notes": final_sync_missing,
        "last_updated": int(time.time())
    }
    
    save_meta(meta)

def get_enabled_students():
    """
    Obtém a lista de alunos habilitados para sincronização.
    
    Returns:
        list: Lista de nomes de alunos habilitados
    """
    config = get_global_student_config()
    return config.get("enabled_students", [])

def is_student_filter_active():
    """
    Verifica se o filtro de alunos está ativo baseado na lista de alunos habilitados.
    
    Returns:
        bool: True se há alunos específicos selecionados (filtro ativo), False caso contrário
    """
    config = get_global_student_config()
    enabled_students = config.get("enabled_students", [])
    return len(enabled_students) > 0

def add_enabled_student(student_name):
    """
    Adiciona um aluno à lista de habilitados.
    
    Args:
        student_name (str): Nome do aluno a ser adicionado
    """
    config = get_global_student_config()
    enabled = set(config.get("enabled_students", []))
    enabled.add(student_name)
    save_global_student_config(
        list(enabled), 
        config.get("available_students", [])
    )

def remove_enabled_student(student_name):
    """
    Remove um aluno da lista de habilitados.
    
    Args:
        student_name (str): Nome do aluno a ser removido
    """
    config = get_global_student_config()
    enabled = set(config.get("enabled_students", []))
    enabled.discard(student_name)
    save_global_student_config(
        list(enabled), 
        config.get("available_students", [])
    )

def is_auto_remove_disabled_students():
    """
    Verifica se a auto-remoção de estudantes desabilitados está ativada.
    
    Returns:
        bool: True se deve remover automaticamente dados de estudantes desabilitados
    """
    config = get_global_student_config()
    return config.get("auto_remove_disabled_students", False)

def set_auto_remove_disabled_students(enabled):
    """
    Ativa ou desativa a auto-remoção de estudantes desabilitados.
    
    Args:
        enabled (bool): Se deve remover automaticamente dados de estudantes desabilitados
    """
    config = get_global_student_config()
    save_global_student_config(
        config.get("enabled_students", []), 
        config.get("available_students", []),
        enabled,
        config.get("sync_missing_students_notes", False)
    )

def is_sync_missing_students_notes():
    """
    Verifica se a sincronização de notas sem alunos específicos está ativada.
    
    Returns:
        bool: True se deve sincronizar notas com coluna ALUNOS vazia para deck [MISSING A.]
    """
    config = get_global_student_config()
    return config.get("sync_missing_students_notes", False)

def set_sync_missing_students_notes(enabled):
    """
    Ativa ou desativa a sincronização de notas sem alunos específicos.
    
    Args:
        enabled (bool): Se deve sincronizar notas com coluna ALUNOS vazia
    """
    config = get_global_student_config()
    save_global_student_config(
        config.get("enabled_students", []), 
        config.get("available_students", []),
        config.get("auto_remove_disabled_students", False),
        enabled
    )

def discover_all_students_from_remote_decks():
    """
    Descobre todos os estudantes únicos de todos os decks remotos configurados.
    
    Returns:
        list: Lista de nomes de estudantes encontrados (normalizados)
    """
    from .student_manager import discover_students_from_tsv_url
    
    all_students = set()
    remote_decks = get_remote_decks()
    
    print(f"🔍 DEBUG: Iniciando descoberta de estudantes...")
    print(f"📋 DEBUG: Encontrados {len(remote_decks)} decks remotos para analisar")
    
    for i, (hash_key, deck_info) in enumerate(remote_decks.items(), 1):
        deck_name = deck_info.get('remote_deck_name', f'Deck {i}')
        url = deck_info.get('remote_deck_url')
        
        if not url:
            print(f"   ⚠️ Deck {deck_name} não possui URL configurada, pulando...")
            continue
            
        print(f"🔍 DEBUG: Analisando deck {i}/{len(remote_decks)}: {deck_name}")
        print(f"🌐 DEBUG: URL: {url}")
        
        try:
            students = discover_students_from_tsv_url(url)
            print(f"   ✓ Encontrados {len(students)} estudantes: {sorted(students)}")
            
            # Adicionar estudantes encontrados (case-sensitive)
            for student in students:
                if student and student.strip():
                    all_students.add(student.strip())
            
            print(f"   ✓ Adicionados {len(students)} estudantes válidos")
            
        except Exception as e:
            # Em caso de erro, continuar com próximo deck
            print(f"   ❌ Erro ao descobrir alunos do deck {deck_name}: {e}")
            continue
    
    final_students = sorted(all_students)
    print(f"✅ DEBUG: Descoberta concluída. Total de estudantes únicos: {len(final_students)}")
    print(f"📝 DEBUG: Lista final: {final_students}")
    
    return final_students

def update_available_students_from_discovery():
    """
    Atualiza a lista de estudantes disponíveis descobrindo de todos os decks remotos.
    
    Returns:
        tuple: (students_found, new_students_count)
    """
    print("🔄 DEBUG: Iniciando atualização de estudantes disponíveis...")
    
    config = get_global_student_config()
    current_available = set(config.get("available_students", []))
    print(f"📋 DEBUG: Estudantes disponíveis atuais: {len(current_available)} - {sorted(current_available)}")
    
    discovered_students = set(discover_all_students_from_remote_decks())
    print(f"🔍 DEBUG: Estudantes descobertos: {len(discovered_students)} - {sorted(discovered_students)}")
    
    # Combinar estudantes descobertos com os existentes (case-sensitive)
    all_available = current_available.union(discovered_students)
    final_available = sorted(list(all_available))
    
    # Contar novos estudantes
    new_count = len(discovered_students - current_available)
    print(f"✨ DEBUG: Novos estudantes encontrados: {new_count}")
    if new_count > 0:
        new_students = sorted(discovered_students - current_available)
        print(f"📝 DEBUG: Lista de novos estudantes: {new_students}")
    
    print(f"💾 DEBUG: Salvando configuração com {len(final_available)} estudantes disponíveis...")
    
    # Atualizar configuração mantendo estudantes habilitados
    save_global_student_config(
        config.get("enabled_students", []),
        final_available
    )
    
    print(f"✅ DEBUG: Atualização concluída com sucesso!")
    return final_available, new_count

# =============================================================================
# GERENCIAMENTO DE NOTE TYPE IDS
# =============================================================================

def add_note_type_id_to_deck(deck_url, note_type_id, expected_name=None, debug_messages=None):
    """
    Adiciona um ID de note type ao deck usando nova estrutura baseada em hash.
    
    Args:
        deck_url (str): URL do deck remoto
        note_type_id (int): ID do note type
        expected_name (str, optional): Nome esperado do note type
        debug_messages (list, optional): Lista para acumular mensagens de debug
    """
    def add_debug_msg(message, category="CONFIG"):
        """Helper para adicionar mensagens de debug com timestamp."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] [{category}] {message}"
        if debug_messages is not None:
            debug_messages.append(formatted_msg)
        print(formatted_msg)  # Também imprimir no console
    
    try:
        add_debug_msg(f"CHAMADA add_note_type_id_to_deck:")
        add_debug_msg(f"  - URL: {deck_url}")
        add_debug_msg(f"  - ID: {note_type_id}")
        add_debug_msg(f"  - Nome esperado: {expected_name}")
        
        # Gerar hash da chave de publicação
        url_hash = get_deck_hash(deck_url)
        add_debug_msg(f"  - Hash: {url_hash}")
        
        meta = get_meta()
        add_debug_msg(f"Meta carregado: {len(meta.get('decks', {}))} decks na config")
        
        if url_hash not in meta["decks"]:
            add_debug_msg(f"ERRO: Deck {url_hash} não encontrado na configuração")
            add_debug_msg(f"Decks disponíveis:")
            for key in meta.get("decks", {}).keys():
                add_debug_msg(f"  - {key}")
            return
            
        deck_info = meta["decks"][url_hash]
        add_debug_msg(f"Deck info encontrado: {list(deck_info.keys())}")
        
        # Garantir que a estrutura note_types existe
        if "note_types" not in deck_info:
            deck_info["note_types"] = {}
            add_debug_msg(f"Inicializando dicionário note_types vazio")
        
        note_type_id_str = str(note_type_id)
        
        # Adicionar ou atualizar o note type atual
        if note_type_id_str not in deck_info["note_types"]:
            # Adicionar novo note type com nome esperado
            deck_info["note_types"][note_type_id_str] = expected_name or f"Note Type {note_type_id}"
            add_debug_msg(f"Note type ID {note_type_id} adicionado ao dicionário")
        else:
            # Atualizar nome esperado se fornecido e diferente
            current_name = deck_info["note_types"][note_type_id_str]
            if expected_name and current_name != expected_name:
                old_name = current_name
                deck_info["note_types"][note_type_id_str] = expected_name
                add_debug_msg(f"Nome do note type ID {note_type_id} atualizado de '{old_name}' para '{expected_name}'")
            else:
                add_debug_msg(f"Note type ID {note_type_id} já está registrado com nome correto")
        
        # Salvar alterações
        save_meta(meta)
        add_debug_msg(f"Meta salvo com sucesso")
        
        name_info = f" ({expected_name})" if expected_name else ""
        add_debug_msg(f"✅ SUCESSO: Note type ID {note_type_id}{name_info} processado")
            
    except Exception as e:
        add_debug_msg(f"❌ ERRO ao adicionar note type ID: {e}")
        import traceback
        error_details = traceback.format_exc()
        add_debug_msg(f"Detalhes do erro: {error_details}")

def get_deck_local_id(deck_url):
    """
    Obtém o ID do deck local de um deck remoto usando nova estrutura.
    
    Args:
        deck_url (str): URL do deck remoto
        
    Returns:
        int: ID do deck local ou None se não encontrado
    """
    try:
        url_hash = get_deck_hash(deck_url)
        
        meta = get_meta()
        
        if url_hash in meta.get("decks", {}):
            return meta["decks"][url_hash].get("local_deck_id")
        return None
        
    except Exception as e:
        print(f"[CONFIG] Erro ao obter ID do deck local: {e}")
        return None

def get_deck_note_type_ids(deck_url):
    """
    Obtém os IDs dos note types de um deck usando nova estrutura.
    
    Args:
        deck_url (str): URL do deck remoto
        
    Returns:
        dict: Dicionário {note_type_id: expected_name}
    """
    try:
        url_hash = get_deck_hash(deck_url)
        
        meta = get_meta()
        
        if url_hash in meta.get("decks", {}):
            return meta["decks"][url_hash].get("note_types", {})
        return {}
        
    except Exception as e:
        print(f"[NOTE_TYPE_IDS] Erro ao obter note type IDs: {e}")
        return {}

def remove_note_type_id_from_deck(deck_url, note_type_id):
    """
    Remove um ID de note type de um deck usando nova estrutura.
    
    Args:
        deck_url (str): URL do deck remoto
        note_type_id (int): ID do note type a ser removido
    """
    try:
        url_hash = get_deck_hash(deck_url)
        
        meta = get_meta()
        
        if url_hash not in meta["decks"]:
            return
            
        deck_info = meta["decks"][url_hash]
        note_type_id_str = str(note_type_id)
        
        if "note_types" in deck_info and note_type_id_str in deck_info["note_types"]:
            del deck_info["note_types"][note_type_id_str]
            save_meta(meta)
            print(f"[NOTE_TYPE_IDS] Removido note type ID {note_type_id} do deck {url_hash}")
            
    except Exception as e:
        print(f"[NOTE_TYPE_IDS] Erro ao remover note type ID: {e}")

def cleanup_invalid_note_type_ids():
    """
    Remove IDs de note types que não existem mais no Anki de todos os decks.
    
    Returns:
        int: Número de IDs removidos
    """
    from .compat import mw
    
    if not mw or not mw.col:
        return 0
        
    try:
        # Obter todos os note types válidos do Anki
        all_models = mw.col.models.all()
        valid_ids = {str(model['id']) for model in all_models}
        
        meta = get_meta()
        
        removed_count = 0
        
        for deck_hash, deck_info in meta.get("decks", {}).items():
            if "note_types" in deck_info:
                invalid_ids = []
                for note_type_id in deck_info["note_types"].keys():
                    if note_type_id not in valid_ids:
                        invalid_ids.append(note_type_id)
                
                # Remover IDs inválidos
                for invalid_id in invalid_ids:
                    del deck_info["note_types"][invalid_id]
                    removed_count += 1
        
        if removed_count > 0:
            save_meta(meta)
            print(f"[NOTE_TYPE_IDS] Removidos {removed_count} IDs inválidos")
        
        return removed_count
        
    except Exception as e:
        print(f"[NOTE_TYPE_IDS] Erro na limpeza de IDs inválidos: {e}")
        return 0

def get_all_deck_note_types():
    """
    Obtém todos os note types de todos os decks.
    
    Returns:
        dict: Dicionário {deck_hash: {note_type_id: expected_name}}
    """
    try:
        meta = get_meta()
        
        result = {}
        for deck_hash, deck_info in meta.get("decks", {}).items():
            result[deck_hash] = deck_info.get("note_types", {})
        
        return result
        
    except Exception as e:
        print(f"[NOTE_TYPE_IDS] Erro ao obter todos os note types: {e}")
        return {}

def update_note_type_names_if_needed():
    """
    Atualiza nomes dos note types no Anki se houver discrepâncias com os nomes esperados.
    
    Returns:
        int: Número de note types renomeados
    """
    from .compat import mw
    
    if not mw or not mw.col:
        return 0
        
    try:
        meta = get_meta()
        
        renamed_count = 0
        
        for deck_hash, deck_info in meta.get("decks", {}).items():
            note_types = deck_info.get("note_types", {})
            
            for note_type_id, expected_name in note_types.items():
                try:
                    note_type_id_int = int(note_type_id)
                    # Buscar o modelo usando método mais robusto
                    model = None
                    for m in mw.col.models.all():
                        if m['id'] == note_type_id_int:
                            model = m
                            break
                    
                    if model and model.get("name") != expected_name:
                        # Nome diverge - atualizar no Anki
                        old_name = model["name"]
                        model["name"] = expected_name
                        mw.col.models.update(model)
                        renamed_count += 1
                        print(f"[Sheets2Anki] Note type renomeado: '{old_name}' -> '{expected_name}'")
                        
                except (ValueError, TypeError) as e:
                    print(f"[WARNING] Erro ao processar note type ID {note_type_id}: {e}")
                    continue
        
        return renamed_count
        
    except Exception as e:
        print(f"[NOTE_TYPE_IDS] Erro ao atualizar nomes dos note types: {e}")
        return 0

def get_deck_note_types_by_ids(deck_url):
    """
    Obtém os objetos note type do Anki baseado nos IDs salvos para um deck.
    
    Args:
        deck_url (str): URL do deck remoto
        
    Returns:
        list: Lista de dicionários de note types do Anki
    """
    from .compat import mw
    
    if not mw or not mw.col:
        return []
        
    try:
        note_types_dict = get_deck_note_type_ids(deck_url)
        note_types = []
        
        for note_type_id_str in note_types_dict.keys():
            try:
                note_type_id_int = int(note_type_id_str)
                # Buscar usando método mais robusto
                for model in mw.col.models.all():
                    if model['id'] == note_type_id_int:
                        note_types.append(model)
                        break
                else:
                    print(f"[NOTE_TYPE_IDS] Note type com ID {note_type_id_int} não encontrado")
            except ValueError:
                print(f"[NOTE_TYPE_IDS] ID inválido: {note_type_id_str}")
                continue
                
        return note_types
        
    except Exception as e:
        print(f"[NOTE_TYPE_IDS] Erro ao obter note types por ID: {e}")
        return []

def test_note_type_id_capture():
    """
    Função de teste para capturar manualmente os IDs de note types.
    Use esta função para testar o sistema independentemente do sync.
    """
    from .compat import mw
    
    if not mw or not mw.col:
        print("[TEST] Anki não está disponível")
        return
    
    print("[TEST] === TESTE MANUAL DE CAPTURA DE NOTE TYPE IDS ===")
    
    # Listar todos os note types
    all_models = mw.col.models.all()
    print(f"[TEST] Total de note types no Anki: {len(all_models)}")
    
    sheets2anki_models = []
    for model in all_models:
        model_name = model['name']
        print(f"[TEST] Note type encontrado: '{model_name}' (ID: {model['id']})")
        if 'Sheets2Anki' in model_name:
            sheets2anki_models.append(model)
            print(f"[TEST] ✅ Note type do Sheets2Anki: '{model_name}' (ID: {model['id']})")
    
    if not sheets2anki_models:
        print("[TEST] ❌ Nenhum note type do Sheets2Anki encontrado!")
        return
    
    # Verificar se temos decks configurados
    meta = get_meta()
    decks = meta.get('decks', {})
    print(f"[TEST] Decks configurados: {len(decks)}")
    
    if not decks:
        print("[TEST] ❌ Nenhum deck configurado!")
        return
    
    # Para cada deck configurado, tentar capturar IDs
    for deck_url, deck_info in decks.items():
        print(f"[TEST] Processando deck: {deck_info.get('local_deck_name', 'Unknown')}")
        print(f"[TEST] URL: {deck_url}")
        
        # Simular captura
        from .utils import get_model_suffix_from_url
        try:
            url_hash = get_model_suffix_from_url(deck_url)
            hash_pattern = f"Sheets2Anki - {url_hash} - "
            print(f"[TEST] Hash: {url_hash}")
            print(f"[TEST] Padrão: {hash_pattern}")
            
            matching_models = []
            for model in sheets2anki_models:
                if hash_pattern in model['name']:
                    matching_models.append(model)
                    print(f"[TEST] ✅ Match: '{model['name']}'")
            
            if matching_models:
                print(f"[TEST] Adicionando {len(matching_models)} IDs ao deck...")
                for model in matching_models:
                    add_note_type_id_to_deck(deck_url, model['id'], model['name'])
            else:
                print(f"[TEST] ❌ Nenhum note type encontrado para o padrão '{hash_pattern}'")
                
        except Exception as e:
            print(f"[TEST] Erro ao processar deck: {e}")
    
    print("[TEST] === FIM DO TESTE ===")
    
    # Mostrar resultado final
    meta_final = get_meta()
    for deck_url, deck_info in meta_final.get('decks', {}).items():
        note_type_ids = deck_info.get('note_type_ids', [])
        print(f"[TEST] Deck {deck_info.get('local_deck_name', 'Unknown')}: {len(note_type_ids)} IDs salvos")
        if note_type_ids:
            print(f"[TEST]   IDs: {note_type_ids}")


def update_note_type_names_in_meta(url, new_remote_deck_name, enabled_students=None):
    """
    Atualiza os nomes dos note types no meta.json quando o remote_deck_name muda.
    
    Args:
        url (str): URL do deck remoto
        new_remote_deck_name (str): Novo nome do deck remoto
        enabled_students (list, optional): Lista de alunos habilitados
    """
    try:
        from .utils import get_note_type_name
        
        meta = get_meta()
        deck_hash = get_deck_hash(url)
        
        if "decks" not in meta or deck_hash not in meta["decks"]:
            return
            
        deck_info = meta["decks"][deck_hash]
        note_types = deck_info.get("note_types", {})
        
        if not note_types:
            return
            
        print(f"[UPDATE_META] Atualizando nomes de note types para deck: {new_remote_deck_name}")
        
        # Atualizar cada note type ID com o novo nome esperado
        for note_type_id, old_name in note_types.items():
            # Analisar o nome antigo para extrair student e type
            if old_name.startswith("Sheets2Anki - "):
                parts = old_name.split(" - ")
                
                if len(parts) == 4:  # Formato: "Sheets2Anki - remote_name - student - type"
                    student = parts[2]
                    note_type = parts[3]
                    is_cloze = note_type == "Cloze"
                    
                    new_name = get_note_type_name(url, new_remote_deck_name, student=student, is_cloze=is_cloze)
                    
                elif len(parts) == 3:  # Formato: "Sheets2Anki - remote_name - type"
                    note_type = parts[2]
                    is_cloze = note_type == "Cloze"
                    
                    new_name = get_note_type_name(url, new_remote_deck_name, student=None, is_cloze=is_cloze)
                    
                else:
                    # Formato não reconhecido, tentar deduzir
                    is_cloze = "Cloze" in old_name
                    student_candidates = enabled_students or []
                    student = None
                    
                    for candidate in student_candidates:
                        if candidate in old_name:
                            student = candidate
                            break
                    
                    new_name = get_note_type_name(url, new_remote_deck_name, student=student, is_cloze=is_cloze)
                
                # Atualizar se o nome mudou
                if new_name != old_name:
                    note_types[note_type_id] = new_name
                    print(f"[UPDATE_META] ✅ Atualizado: {old_name} -> {new_name}")
        
        # Salvar mudanças
        save_meta(meta)
        print(f"[UPDATE_META] ✅ Meta.json atualizado com novos nomes de note types")
        
    except Exception as e:
        print(f"[UPDATE_META] ❌ Erro ao atualizar nomes no meta.json: {e}")
        import traceback
        traceback.print_exc()


# =============================================================================
# GERENCIAMENTO DE CONFIGURAÇÕES DE OPÇÕES DE DECK
# =============================================================================

def get_deck_options_mode():
    """
    Obtém o modo atual de configuração de opções de deck.
    
    Returns:
        str: "shared", "individual", ou "manual"
    """
    meta = get_meta()
    config = meta.get("config", {})
    return config.get("deck_options_mode", "shared")

def set_deck_options_mode(mode):
    """
    Define o modo de configuração de opções de deck.
    
    Args:
        mode (str): "shared", "individual", ou "manual"
    """
    if mode not in ["shared", "individual", "manual"]:
        raise ValueError(f"Modo inválido: {mode}. Use 'shared', 'individual' ou 'manual'")
    
    meta = get_meta()
    if "config" not in meta:
        meta["config"] = {}
    
    meta["config"]["deck_options_mode"] = mode
    save_meta(meta)
    print(f"[DECK_OPTIONS_MODE] Modo alterado para: {mode}")
