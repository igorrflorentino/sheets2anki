"""
Utilitários para nomeação automática de decks.

Este módulo fornece funções para extrair automaticamente nomes de decks
a partir de URLs do Google Sheets e gerenciar a nomeação hierárquica.
"""

import re
from urllib.parse import urlparse, parse_qs
from .parseRemoteDeck import getRemoteDeck, RemoteDeckError
from .config_manager import get_deck_naming_mode, get_parent_deck_name
from .compat import mw


def extract_deck_name_from_url(url):
    """
    Extrai o nome do deck automaticamente a partir da URL do Google Sheets.
    
    Prioridade de nomeação:
    1. Nome do arquivo TSV baixado (removendo extensão .tsv)
    2. Fallback para 'auto name fail - PlanilhaID xxxx AbaID xxxxx'
    3. Fallback final para 'auto name fatal fail'
    
    Args:
        url (str): URL do Google Sheets
        
    Returns:
        str: Nome sugerido para o deck
    """
    try:
        # Estratégia 1: Obter nome do arquivo TSV baixado
        try:
            import urllib.request
            
            # Headers apropriados
            headers = {
                'User-Agent': 'Mozilla/5.0 (Sheets2Anki) AnkiAddon'
            }
            request = urllib.request.Request(url, headers=headers)
            
            response = urllib.request.urlopen(request, timeout=10)
            
            # Verificar header Content-Disposition para nome do arquivo
            content_disposition = response.headers.get('Content-Disposition', '')
            if content_disposition:
                # Extrair nome do arquivo do header
                import re
                match = re.search(r'filename[^;=\n]*=(([\'"]).*?\2|[^;\n]*)', content_disposition)
                if match:
                    filename = match.group(1).strip('"\'')
                    if filename:
                        # Remover extensão .tsv se existir
                        if filename.lower().endswith('.tsv'):
                            filename = filename[:-4]
                        return clean_deck_name(filename)
            
            response.close()
            
        except Exception:
            pass
        
        # Estratégia 2: Fallback para ID da planilha e GID
        spreadsheet_id = _extract_spreadsheet_id(url)
        gid = _extract_gid(url)
        
        if spreadsheet_id:
            if gid and gid != "0":
                return f"auto name fail - PlanilhaID {spreadsheet_id[:8]} AbaID {gid}"
            else:
                return f"auto name fail - PlanilhaID {spreadsheet_id[:8]} AbaID 0"
        
        # Estratégia 3: Fallback final
        return "auto name fatal fail"
        
    except Exception:
        return "auto name fatal fail"


def generate_automatic_deck_name(url):
    """
    Gera um nome de deck automático seguindo as convenções do addon.
    
    Args:
        url (str): URL do Google Sheets
        
    Returns:
        str: Nome completo do deck (incluindo hierarquia se necessário)
    """
    base_name = extract_deck_name_from_url(url)
    
    # Se modo automático, usar hierarquia
    if get_deck_naming_mode() == "automatic":
        parent_name = get_parent_deck_name()
        return f"{parent_name}::{base_name}"
    
    return base_name


def clean_deck_name(name):
    """
    Limpa e normaliza um nome de deck.
    
    Args:
        name (str): Nome bruto do deck
        
    Returns:
        str: Nome limpo e normalizado
    """
    if not name:
        return "auto name fatal fail"
    
    # Converter para string se necessário
    name = str(name).strip()
    
    # Remover caracteres problemáticos, mas manter espaços
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    
    # Garantir que não está vazio
    if not name:
        return "auto name fatal fail"
    
    # Limitar tamanho
    if len(name) > 100:
        name = name[:100]
    
    return name


def check_deck_name_conflict(deck_name):
    """
    Verifica se já existe um deck com o nome especificado.
    
    Args:
        deck_name (str): Nome do deck a verificar
        
    Returns:
        bool: True se houver conflito, False caso contrário
    """
    try:
        existing_deck = mw.col.decks.by_name(deck_name)
        return existing_deck is not None
    except:
        return False


def resolve_deck_name_conflict(base_name, max_attempts=100):
    """
    Resolve conflitos de nome de deck adicionando sufixos numéricos.
    
    Args:
        base_name (str): Nome base do deck
        max_attempts (int): Número máximo de tentativas
        
    Returns:
        str: Nome único do deck
    """
    if not check_deck_name_conflict(base_name):
        return base_name
    
    for i in range(2, max_attempts + 2):
        candidate_name = f"{base_name}_{i}"
        if not check_deck_name_conflict(candidate_name):
            return candidate_name
    
    # Se não conseguir resolver, usar timestamp
    import time
    timestamp = int(time.time())
    return f"{base_name}_{timestamp}"


def get_available_deck_name(url):
    """
    Obtém um nome de deck disponível (sem conflitos) para a URL.
    
    Args:
        url (str): URL do Google Sheets
        
    Returns:
        str: Nome único disponível para o deck
    """
    base_name = generate_automatic_deck_name(url)
    return resolve_deck_name_conflict(base_name)


def should_update_deck_name(url, current_name):
    """
    Determina se o nome do deck deve ser atualizado automaticamente.
    
    Args:
        url (str): URL do Google Sheets
        current_name (str): Nome atual do deck
        
    Returns:
        bool: True se deve atualizar, False caso contrário
    """
    # Só atualizar se estiver no modo automático
    if get_deck_naming_mode() != "automatic":
        return False
    
    # Gerar novo nome baseado na URL
    new_name = generate_automatic_deck_name(url)
    
    # Comparar com nome atual (ignorando case)
    return new_name.lower() != current_name.lower()


def update_deck_name_if_needed(url, deck_id, current_name):
    """
    Atualiza o nome do deck se necessário (modo automático).
    
    Args:
        url (str): URL do Google Sheets
        deck_id (int): ID do deck no Anki
        current_name (str): Nome atual do deck
        
    Returns:
        str: Nome final do deck (atualizado ou não)
    """
    if not should_update_deck_name(url, current_name):
        return current_name
    
    try:
        new_name = get_available_deck_name(url)
        
        # Atualizar nome no Anki
        deck = mw.col.decks.get(deck_id)
        if deck:
            deck['name'] = new_name
            mw.col.decks.save(deck)
            return new_name
    except Exception:
        pass
    
    return current_name


# =============================================================================
# FUNÇÕES AUXILIARES PRIVADAS
# =============================================================================

def _extract_spreadsheet_id(url):
    """
    Extrai o ID da planilha da URL.
    
    Args:
        url (str): URL do Google Sheets
        
    Returns:
        str: ID da planilha ou None se não encontrado
    """
    # Tentar padrão publicado /d/e/ID
    match = re.search(r'/spreadsheets/d/e/([a-zA-Z0-9-_]+)', url)
    if match:
        return match.group(1)
    
    # Tentar padrão normal /d/ID
    match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', url)
    if match:
        return match.group(1)
    
    return None


def _extract_gid(url):
    """
    Extrai o ID da aba (GID) da URL.
    
    Args:
        url (str): URL do Google Sheets
        
    Returns:
        str: GID da aba ou "0" se não encontrado
    """
    try:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        # Verificar se há parâmetro gid
        if 'gid' in query_params:
            return query_params['gid'][0]
        
        # Verificar se há gid no fragmento da URL
        if parsed_url.fragment:
            # Tentar extrair do fragmento (#gid=123)
            match = re.search(r'#gid=([^&\s]+)', parsed_url.fragment)
            if match:
                return match.group(1)
            
            # Tentar como query params no fragmento
            fragment_params = parse_qs(parsed_url.fragment)
            if 'gid' in fragment_params:
                return fragment_params['gid'][0]
        
        return "0"  # GID padrão se não encontrado
    except Exception:
        return "0"