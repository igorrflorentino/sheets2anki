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
    
    Tenta várias estratégias para obter um nome significativo:
    1. Nome do arquivo TSV baixado (a partir dos headers HTTP)
    2. Nome da aba (se GID específico)
    3. Nome da planilha (via título do documento)
    4. Nome baseado no ID da planilha
    5. Nome genérico como fallback
    
    Args:
        url (str): URL do Google Sheets
        
    Returns:
        str: Nome sugerido para o deck
    """
    try:
        # Estratégia 1: Tentar obter nome do arquivo TSV baixado
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
                    if filename and filename.endswith('.tsv'):
                        # Remover extensão .tsv e limpar nome
                        deck_name = filename[:-4]
                        return clean_deck_name(deck_name)
            
            # Tentar extrair da URL se não há Content-Disposition
            if 'export' in url and 'format=tsv' in url:
                # Tentar obter nome da planilha fazendo uma requisição adicional
                try:
                    # Converter para URL de visualização para obter título
                    spreadsheet_id = _extract_spreadsheet_id(url)
                    if spreadsheet_id:
                        title = _get_spreadsheet_title(spreadsheet_id)
                        if title:
                            return clean_deck_name(title)
                except:
                    pass
            
            response.close()
            
        except Exception:
            pass
        
        # Estratégia 2: Tentar obter dados do deck para extrair nome
        try:
            remote_deck = getRemoteDeck(url)
            if hasattr(remote_deck, 'deckName') and remote_deck.deckName:
                return clean_deck_name(remote_deck.deckName)
        except:
            pass
        
        # Estratégia 3: Extrair informações da URL
        spreadsheet_id = _extract_spreadsheet_id(url)
        gid = _extract_gid(url)
        
        # Estratégia 4: Tentar obter nome da aba via GID
        if gid and gid != "0":
            try:
                sheet_name = _get_sheet_name_from_gid(url, gid)
                if sheet_name:
                    return clean_deck_name(sheet_name)
            except:
                pass
        
        # Estratégia 5: Nome baseado no ID da planilha
        if spreadsheet_id:
            # Usar apenas os primeiros 8 caracteres do ID para legibilidade
            short_id = spreadsheet_id[:8]
            deck_name = f"Sheets_Deck_{short_id}"
            if gid and gid != "0":
                deck_name += f"_Sheet_{gid}"
            return deck_name
        
        # Estratégia 6: Nome genérico
        return "Imported_Deck"
        
    except Exception:
        return "Imported_Deck"


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
        return "Unnamed_Deck"
    
    # Converter para string se necessário
    name = str(name).strip()
    
    # Remover caracteres problemáticos
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    
    # Remover espaços duplos e converter espaços em underscores
    name = re.sub(r'\s+', '_', name)
    
    # Remover underscores duplos
    name = re.sub(r'_+', '_', name)
    
    # Remover underscores no início e fim
    name = name.strip('_')
    
    # Garantir que não está vazio
    if not name:
        return "Unnamed_Deck"
    
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
    Extrai o GID (ID da aba) da URL.
    
    Args:
        url (str): URL do Google Sheets
        
    Returns:
        str: GID da aba ou None se não encontrado
    """
    # Tentar extrair do fragmento (#gid=123)
    if '#gid=' in url:
        match = re.search(r'#gid=([^&\s]+)', url)
        if match:
            return match.group(1)
    
    # Tentar extrair dos parâmetros (?gid=123)
    if '?gid=' in url or '&gid=' in url:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        if 'gid' in params:
            return params['gid'][0]
    
    return None


def _get_spreadsheet_title(spreadsheet_id):
    """
    Tenta obter o título da planilha a partir do ID.
    
    Esta função faz uma requisição à URL de visualização da planilha
    para tentar extrair o título da página HTML.
    
    Args:
        spreadsheet_id (str): ID da planilha
        
    Returns:
        str: Título da planilha ou None se não conseguir obter
    """
    try:
        import urllib.request
        
        # URL de visualização da planilha
        view_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Sheets2Anki) AnkiAddon'
        }
        request = urllib.request.Request(view_url, headers=headers)
        
        response = urllib.request.urlopen(request, timeout=10)
        html_content = response.read().decode('utf-8')
        response.close()
        
        # Tentar extrair título da tag <title>
        match = re.search(r'<title[^>]*>([^<]+)</title>', html_content, re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            # Remover sufixos comuns do Google Sheets
            title = re.sub(r'\s*-\s*Google\s+(Sheets|Planilhas).*$', '', title, flags=re.IGNORECASE)
            if title:
                return title
        
        return None
        
    except Exception:
        return None


def _get_sheet_name_from_gid(url, gid):
    """
    Tenta obter o nome da aba a partir do GID.
    
    Esta função é um placeholder para uma futura implementação
    que poderia usar a API do Google Sheets.
    
    Args:
        url (str): URL do Google Sheets
        gid (str): GID da aba
        
    Returns:
        str: Nome da aba ou None se não conseguir obter
    """
    # Por enquanto, retornar None
    # Futura implementação poderia usar a API do Google Sheets
    return None
