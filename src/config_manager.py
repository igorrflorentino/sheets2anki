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
    "user_preferences": {
        "deck_naming_mode": "automatic",  # "automatic" ou "manual"
        "parent_deck_name": "Sheets2Anki",
        "auto_update_names": True,
        "create_subdecks": True  # Habilitar criação de subdecks por padrão
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

def get_user_preferences():
    """
    Obtém as preferências do usuário.
    
    Returns:
        dict: Preferências do usuário
    """
    meta = get_meta()
    return meta.get("user_preferences", DEFAULT_META["user_preferences"].copy())

def save_user_preferences(preferences):
    """
    Salva as preferências do usuário.
    
    Args:
        preferences (dict): Preferências para salvar
    """
    meta = get_meta()
    meta["user_preferences"] = preferences
    save_meta(meta)

def get_remote_decks():
    """
    Obtém a lista de decks remotos configurados.
    
    Returns:
        dict: Dicionário de decks remotos {url: deck_info}
    """
    meta = get_meta()
    return meta.get("decks", {})

def save_remote_decks(remote_decks):
    """
    Salva a lista de decks remotos.
    
    Args:
        remote_decks (dict): Dicionário de decks remotos
    """
    meta = get_meta()
    meta["decks"] = remote_decks
    save_meta(meta)

def add_remote_deck(url, deck_info):
    """
    Adiciona um deck remoto à configuração.
    
    Args:
        url (str): URL do deck remoto
        deck_info (dict): Informações do deck
    """
    remote_decks = get_remote_decks()
    remote_decks[url] = deck_info
    save_remote_decks(remote_decks)

def remove_remote_deck(url):
    """
    Remove um deck remoto da configuração.
    
    Args:
        url (str): URL do deck remoto a ser removido
    """
    remote_decks = get_remote_decks()
    if url in remote_decks:
        del remote_decks[url]
        save_remote_decks(remote_decks)

def disconnect_deck(url):
    """
    Remove completamente um deck remoto do sistema.
    Esta ação é irreversível - o deck só pode ser reconectado se for re-cadastrado.
    
    Args:
        url (str): URL do deck a ser desconectado
    """
    meta = get_meta()
    remote_decks = meta.get("decks", {})
    
    # Remover completamente o deck da lista de decks remotos
    if url in remote_decks:
        del remote_decks[url]
        meta["decks"] = remote_decks  # type: ignore
        save_meta(meta)
        
        # TODO: Opcionalmente, podemos manter um log de decks desconectados
        # para auditoria, mas não para reconexão

def is_deck_disconnected(url):
    """
    Verifica se um deck está presente na lista de decks remotos.
    Na nova lógica, um deck desconectado é completamente removido, 
    então esta função sempre retorna False para decks que ainda existem.
    
    Args:
        url (str): URL do deck
        
    Returns:
        bool: Sempre False (decks desconectados não existem mais)
    """
    # Na nova lógica, se o deck existe em remote_decks, ele está ativo
    # Se foi desconectado, ele foi removido completamente
    return False

def reconnect_deck(url):
    """
    DEPRECATED: Na nova lógica, não é possível reconectar decks desconectados.
    Um deck desconectado é completamente removido e deve ser re-cadastrado.
    
    Args:
        url (str): URL do deck a ser reconectado
        
    Raises:
        NotImplementedError: Esta função não é mais suportada
    """
    raise NotImplementedError(
        "Reconexão não é mais suportada. Decks desconectados devem ser "
        "re-cadastrados como novos decks remotos."
    )

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
            return deck is None or deck.get("name", "").strip().lower() == "default"
        else:
            return True  # Collection ou decks não disponível
    except:
        return True  # Erro ao acessar deck = deck não existe

def get_deck_naming_mode():
    """
    Obtém o modo de nomeação de decks atual.
    
    Returns:
        str: "automatic" ou "manual"
    """
    prefs = get_user_preferences()
    if prefs:
        return prefs.get("deck_naming_mode", "automatic")
    return "automatic"

def set_deck_naming_mode(mode):
    """
    Define o modo de nomeação de decks.
    
    Args:
        mode (str): "automatic" ou "manual"
    """
    prefs = get_user_preferences()
    if prefs:
        prefs["deck_naming_mode"] = mode
        save_user_preferences(prefs)

def get_parent_deck_name():
    """
    Obtém o nome do deck pai para decks automáticos.
    
    Returns:
        str: Nome do deck pai
    """
    prefs = get_user_preferences()
    if prefs:
        return prefs.get("parent_deck_name", "Sheets2Anki")
    return "Sheets2Anki"

def set_parent_deck_name(name):
    """
    Define o nome do deck pai para decks automáticos.
    
    Args:
        name (str): Nome do deck pai
    """
    prefs = get_user_preferences()
    if prefs:
        prefs["parent_deck_name"] = name
        save_user_preferences(prefs)
        
def get_create_subdecks_setting():
    """
    Verifica se a criação de subdecks está habilitada.
    
    Returns:
        bool: True se a criação de subdecks está habilitada, False caso contrário
    """
    prefs = get_user_preferences()
    if prefs:
        return prefs.get("create_subdecks", True)
    return True

def set_create_subdecks_setting(enabled):
    """
    Define se a criação de subdecks está habilitada.
    
    Args:
        enabled (bool): True para habilitar, False para desabilitar
    """
    prefs = get_user_preferences()
    if prefs:
        prefs["create_subdecks"] = enabled
        save_user_preferences(prefs)

# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def verify_and_update_deck_info(url, deck_id, deck_name, silent=False):
    """
    Verifica e atualiza as informações do deck na configuração.
    
    Esta função garante que:
    1. O deck_id está atualizado na configuração
    2. O deck_name está atualizado na configuração
    3. As informações correspondem à realidade atual do Anki
    
    Args:
        url (str): URL do deck remoto
        deck_id (int): ID atual do deck no Anki
        deck_name (str): Nome atual do deck no Anki
        silent (bool): Se True, não mostra notificações
        
    Returns:
        bool: True se houve atualizações, False caso contrário
    """
    remote_decks = get_remote_decks()
    
    # Verificar se o deck existe na configuração
    if url not in remote_decks:
        return False
    
    deck_info = remote_decks[url]
    updated = False
    
    # Verificar se o deck_id precisa ser atualizado
    current_deck_id = deck_info.get("deck_id")
    if current_deck_id != deck_id:
        deck_info["deck_id"] = deck_id
        updated = True
    
    # Verificar se o deck_name precisa ser atualizado
    current_deck_name = deck_info.get("deck_name")
    if current_deck_name != deck_name:
        deck_info["deck_name"] = deck_name
        updated = True
    
    # Salvar as alterações se houve atualizações
    if updated:
        save_remote_decks(remote_decks)
        return True
    
    return False

def get_deck_info_by_id(deck_id):
    """
    Obtém informações do deck remoto pelo ID do deck.
    
    Args:
        deck_id (int): ID do deck no Anki
        
    Returns:
        tuple: (url, deck_info) ou (None, None) se não encontrado
    """
    remote_decks = get_remote_decks()
    
    for url, deck_info in remote_decks.items():
        if deck_info.get("deck_id") == deck_id:
            return url, deck_info
    
    return None, None

def detect_deck_name_changes(skip_deleted=False):
    """
    Detecta mudanças nos nomes dos decks locais e atualiza a configuração.
    
    Esta função verifica todos os decks remotos configurados e atualiza
    suas informações se o nome do deck foi alterado no Anki.
    
    Args:
        skip_deleted: Se True, não atualiza nomes de decks que foram deletados
    
    Returns:
        list: Lista de URLs dos decks que foram atualizados
    """
    from .compat import mw
    
    remote_decks = get_remote_decks()
    updated_urls = []
    
    for url, deck_info in remote_decks.items():
        deck_id = deck_info.get("deck_id")
        if not deck_id:
            continue
            
        # Obter deck atual do Anki
        if not mw.col or not mw.col.decks:
            continue  # Collection ou decks não disponível
            
        deck = mw.col.decks.get(deck_id)
        
        # Se o deck foi deletado e skip_deleted=True, pular
        if not deck and skip_deleted:
            continue
            
        # Se o deck existe, atualizar o nome
        if deck:
            current_name = deck.get("name", "")
            saved_name = deck_info.get("deck_name", "")
            
            # Verificar se o nome mudou
            if current_name and current_name != saved_name:
                # Atualizar nome na configuração
                deck_info["deck_name"] = current_name
                updated_urls.append(url)
    
    # Salvar alterações se houve atualizações
    if updated_urls:
        save_remote_decks(remote_decks)
    
    return updated_urls

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

def migrate_sync_selection():
    """Função removida - migração não necessária"""
    return False

def _ensure_meta_structure(meta):
    """
    Garante que a estrutura do meta.json está correta.
    
    Args:
        meta (dict): Metadados a serem verificados
        
    Returns:
        dict: Metadados com estrutura corrigida
    """
    # Garantir chaves principais
    if "user_preferences" not in meta:
        meta["user_preferences"] = DEFAULT_META["user_preferences"].copy()
    
    if "decks" not in meta:
        meta["decks"] = {}
    
    # Migrar dados de remote_decks para decks se necessário
    if "remote_decks" in meta and meta["remote_decks"] and not meta.get("decks"):
        meta["decks"] = meta["remote_decks"]
    
    # Remover chave antiga
    if "remote_decks" in meta:
        del meta["remote_decks"]
    
    # Garantir preferências do usuário
    user_prefs = meta["user_preferences"]
    default_prefs = DEFAULT_META["user_preferences"]
    
    for key, value in default_prefs.items():
        if key not in user_prefs:
            user_prefs[key] = value
    
    # Garantir que todos os decks têm o atributo is_sync
    for url, deck_info in meta["decks"].items():
        if "is_sync" not in deck_info:
            deck_info["is_sync"] = True  # Padrão: selecionado para sincronização
    
    return meta
