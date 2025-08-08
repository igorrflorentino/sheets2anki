"""
Utilitários para nomeação automática de decks.

Este módulo fornece funções para extrair automaticamente nomes de decks
a partir de URLs do Google Sheets e gerenciar a nomeação hierárquica.
"""

import re
from urllib.parse import urlparse, parse_qs
from .parseRemoteDeck import getRemoteDeck, RemoteDeckError
from .constants import DEFAULT_PARENT_DECK_NAME
from .compat import mw


# =============================================================================
# CLASSE CENTRALIZADA PARA GERENCIAMENTO DE NOMES DE DECKS
# =============================================================================

class DeckNamer:
    """
    Classe centralizada para gerenciar nomes de decks no Anki.
    
    Esta classe encapsula toda a lógica de nomeação, resolução de conflitos
    e atualização de nomes de decks, tornando o código mais robusto e fácil de manter.
    """
    
    @staticmethod
    def extract_remote_name_from_url(url):
        """
        Extrai o nome do deck de forma inteligente usando múltiplas estratégias.
        
        Estratégias (em ordem de preferência):
        1. Título da planilha via metadados HTML
        2. Nome do arquivo via Content-Disposition
        3. Fallback: ID da planilha + GID
        
        Args:
            url (str): URL do Google Sheets
            
        Returns:
            str: Nome do deck remoto
        """
        try:
            # Estratégia 1: Extrair título da planilha via HTML
            title = DeckNamer._extract_spreadsheet_title(url)
            if title and title != "auto name fail":
                return DeckNamer.clean_name(title)
            
            # Estratégia 2: Nome do arquivo via Content-Disposition
            filename = DeckNamer._extract_filename_from_headers(url)
            if filename and filename != "auto name fail":
                return DeckNamer.clean_name(filename)
            
            # Estratégia 3: Fallback para ID da planilha e GID
            return DeckNamer._generate_fallback_name(url)
            
        except Exception:
            return "auto name fatal fail"
    
    @staticmethod
    def _extract_spreadsheet_title(url):
        """
        Tenta extrair o título da planilha via metadados HTML.
        
        Args:
            url (str): URL do Google Sheets
            
        Returns:
            str: Título da planilha ou None
        """
        try:
            import urllib.request
            import urllib.parse
            
            # Construir URL para acessar metadados (página HTML da planilha)
            base_url = url.replace('&output=tsv', '').replace('?output=tsv', '').replace('&single=true', '')
            
            # Limpar parâmetros desnecessários mas manter gid se existir
            parsed = urllib.parse.urlparse(base_url)
            query_params = urllib.parse.parse_qs(parsed.query)
            
            # Manter apenas gid se existir
            filtered_params = {}
            if 'gid' in query_params:
                filtered_params['gid'] = query_params['gid']
                
            new_query = urllib.parse.urlencode(filtered_params, doseq=True)
            meta_url = urllib.parse.urlunparse((
                parsed.scheme, parsed.netloc, parsed.path,
                parsed.params, new_query, parsed.fragment
            ))
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            request = urllib.request.Request(meta_url, headers=headers)
            
            with urllib.request.urlopen(request, timeout=15) as response:
                html = response.read().decode('utf-8', errors='ignore')
                
                # Múltiplos padrões para extrair título
                title_patterns = [
                    r'<title>([^<]+?)\s*-\s*Google\s*(Sheets|Planilhas)</title>',  # Título principal
                    r'<title>([^<]+)</title>',  # Fallback para qualquer título
                    r'"title":"([^"]+)"',  # JSON metadata
                    r'<meta property="og:title" content="([^"]+)"',  # Open Graph
                    r'"doc-name":"([^"]+)"',  # Nome interno do documento
                ]
                
                for pattern in title_patterns:
                    match = re.search(pattern, html, re.IGNORECASE)
                    if match:
                        title = match.group(1).strip()
                        # Filtrar títulos inválidos
                        if title and title.lower() not in ['untitled', 'sem título', 'planilha sem título']:
                            return title
                            
                return None
                
        except Exception:
            return None
    
    @staticmethod
    def _extract_filename_from_headers(url):
        """
        Extrai nome do arquivo via header Content-Disposition.
        
        Args:
            url (str): URL do Google Sheets
            
        Returns:
            str: Nome do arquivo ou None
        """
        try:
            import urllib.request
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Sheets2Anki) AnkiAddon'
            }
            request = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(request, timeout=10) as response:
                # Verificar header Content-Disposition para nome do arquivo
                content_disposition = response.headers.get('Content-Disposition', '')
                if content_disposition:
                    # Extrair nome do arquivo do header
                    match = re.search(r'filename[^;=\n]*=(([\'"]).*?\2|[^;\n]*)', content_disposition)
                    if match:
                        filename = match.group(1).strip('"\'')
                        if filename:
                            # Remover extensão .tsv se existir
                            if filename.lower().endswith('.tsv'):
                                filename = filename[:-4]
                            return filename
                            
                return None
                
        except Exception:
            return None
    
    @staticmethod
    def _generate_fallback_name(url):
        """
        Gera nome fallback baseado em ID da planilha e GID.
        
        Args:
            url (str): URL do Google Sheets
            
        Returns:
            str: Nome fallback
        """
        try:
            spreadsheet_id = _extract_spreadsheet_id(url)
            gid = _extract_gid(url)
            
            if spreadsheet_id:
                if gid and gid != "0":
                    return f"Planilha {spreadsheet_id[:8]} - Aba {gid}"
                else:
                    return f"Planilha {spreadsheet_id[:8]} - Aba Principal"
            
            return "Planilha Externa"
            
        except Exception:
            return "auto name fatal fail"
    
    @staticmethod
    def extract_name_from_url(url):
        """
        Extrai o nome do deck automaticamente a partir da URL do Google Sheets.
        
        Args:
            url (str): URL do Google Sheets
            
        Returns:
            str: Nome sugerido para o deck
        """
        # Reutilizar a lógica de extração do nome remoto
        return DeckNamer.extract_remote_name_from_url(url)
    
    @staticmethod
    def get_deck_names(url):
        """
        Obtém tanto o nome local quanto remoto do deck a partir da URL.
        
        Args:
            url (str): URL do Google Sheets
            
        Returns:
            tuple: (local_deck_name, remote_deck_name)
        """
        remote_name = DeckNamer.extract_remote_name_from_url(url)
        
        # Nome local sempre usa a hierarquia
        parent_name = DEFAULT_PARENT_DECK_NAME
        local_name = f"{parent_name}::{remote_name}"
        
        return local_name, remote_name
    
    @staticmethod
    def clean_name(name):
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
        
        # Remover terminação " - Google Drive" ou " - Google Sheets" que são adicionadas pelo título da página
        name = re.sub(r'\s*-\s*Google\s+(Drive|Sheets)\s*$', '', name, flags=re.IGNORECASE)
        
        # Remover caracteres problemáticos, mas manter espaços
        name = re.sub(r'[<>:"/\\|?*]', '_', name)
        
        # Garantir que não está vazio
        if not name:
            return "auto name fatal fail"
        
        # Limitar tamanho
        if len(name) > 100:
            name = name[:100]
        
        return name
    
    @staticmethod
    def generate_local_deck_name(remote_deck_name, root_name="Sheets2Anki"):
        """
        Gera o nome local do deck baseado no formato: {root}::{remote_deck_name}
        
        Args:
            remote_deck_name (str): Nome remoto do deck
            root_name (str): Nome raiz do deck (padrão: "Sheets2Anki")
            
        Returns:
            str: Nome local no formato "{root}::{remote_deck_name}"
        """
        if not remote_deck_name:
            return f"{root_name}::UnknownDeck"
        
        # Limpar o nome remoto diretamente aqui
        import re
        clean_remote_name = str(remote_deck_name).strip()
        # Remover caracteres problemáticos, mas manter espaços
        clean_remote_name = re.sub(r'[<>:"/\\|?*]', '_', clean_remote_name)
        # Limitar tamanho
        if len(clean_remote_name) > 80:
            clean_remote_name = clean_remote_name[:80]
        
        return f"{root_name}::{clean_remote_name}"
    
    @staticmethod
    def has_numeric_suffix(name):
        """
        Verifica se o nome já tem um sufixo numérico (_X).
        
        Args:
            name (str): Nome do deck
            
        Returns:
            tuple: (has_suffix, base_name, suffix_number) ou (False, name, None)
        """
        suffix_match = re.search(r'_(\d+)$', name)
        if suffix_match:
            suffix_number = int(suffix_match.group(1))
            base_name = name[:suffix_match.start()]
            return True, base_name, suffix_number
        return False, name, None
    
    @staticmethod
    def check_conflict(deck_name):
        """
        Verifica se já existe um deck com o nome especificado.
        
        Args:
            deck_name (str): Nome do deck a verificar
            
        Returns:
            bool: True se houver conflito, False caso contrário
        """
        try:
            if mw and mw.col and mw.col.decks:
                existing_deck = mw.col.decks.by_name(deck_name)
                return existing_deck is not None
            return False
        except:
            return False
    
    @staticmethod
    def generate_name(url):
        """
        Gera um nome de deck automático seguindo as convenções do addon.
        
        Args:
            url (str): URL do Google Sheets
            
        Returns:
            str: Nome completo do deck (sempre com hierarquia)
        """
        base_name = DeckNamer.extract_name_from_url(url)
        
        # Sempre usar hierarquia
        parent_name = DEFAULT_PARENT_DECK_NAME
        return f"{parent_name}::{base_name}"
    
    @staticmethod
    def resolve_conflict(base_name, max_attempts=100):
        """
        Resolve conflitos de nome de deck adicionando sufixos numéricos.
        
        Args:
            base_name (str): Nome base do deck
            max_attempts (int): Número máximo de tentativas
            
        Returns:
            str: Nome único do deck
        """
        if not DeckNamer.check_conflict(base_name):
            return base_name
        
        # Verificar se o nome já termina com um sufixo numérico (_X)
        has_suffix, clean_base_name, suffix_number = DeckNamer.has_numeric_suffix(base_name)
        
        # Definir o índice inicial para busca
        if has_suffix:
            # Garante que suffix_number não é None
            start_index = (suffix_number if suffix_number is not None else 1) + 1
        else:
            start_index = 2
        
        # Verificar cada possível nome com sufixo
        base_to_use = clean_base_name  # Usar o nome base sem sufixo
        for i in range(start_index, max_attempts + start_index):
            candidate_name = f"{base_to_use}_{i}"
            if not DeckNamer.check_conflict(candidate_name):
                return candidate_name
        
        # Se não conseguir resolver, usar timestamp
        import time
        timestamp = int(time.time())
        return f"{base_to_use}_{timestamp}"
    
    @staticmethod
    def get_available_name(url):
        """
        Obtém um nome de deck disponível (sem conflitos) para a URL.
        
        Args:
            url (str): URL do Google Sheets
            
        Returns:
            str: Nome único disponível para o deck
        """
        base_name = DeckNamer.generate_name(url)
        return DeckNamer.resolve_conflict(base_name)
    
    @staticmethod
    def should_update_name(url, current_name):
        """
        Determina se o nome do deck deve ser atualizado automaticamente.
        
        Args:
            url (str): URL do Google Sheets
            current_name (str): Nome atual do deck
            
        Returns:
            bool: True se deve atualizar, False caso contrário
        """
        # Gerar novo nome baseado na URL
        new_name = DeckNamer.generate_name(url)
        
        # Extrair nome base do nome atual (removendo sufixo numérico se existir)
        has_suffix, base_name, _ = DeckNamer.has_numeric_suffix(current_name)
        comparison_name = base_name if has_suffix else current_name
        
        # Comparar nome base com novo nome (ignorando case)
        should_update = new_name.lower() != comparison_name.lower()
        
        return should_update
    
    @staticmethod
    def update_name_if_needed(url, deck_id, current_name, remote_deck_name=None):
        """
        Atualiza o nome do deck se necessário (modo automático).
        
        Args:
            url (str): URL do Google Sheets
            deck_id (int): ID do deck no Anki
            current_name (str): Nome atual do deck
            remote_deck_name (str, optional): Nome remoto do deck. Se não fornecido, será extraído da URL.
            
        Returns:
            str: Nome final do deck (atualizado ou não)
        """
        try:
            # Usar o nome remoto fornecido ou extrair da URL
            if remote_deck_name:
                remote_name = remote_deck_name
            else:
                remote_name = DeckNamer.generate_name(url)
            
            # Gerar o nome local baseado no padrão Sheets2Anki::{remote_name}
            desired_local_name = DeckNamer.generate_local_deck_name(remote_name)
            
            # Verificar se precisa atualizar comparando com o nome desejado
            if not DeckNamer._should_update_to_desired_name(current_name, desired_local_name):
                return current_name
            
            # Obter nome disponível (pode ter sufixo se já existe)
            new_name = DeckNamer._get_available_deck_name(desired_local_name)
            
            # Atualizar nome no Anki
            if mw and mw.col and mw.col.decks:
                deck = mw.col.decks.get(deck_id)
                if deck:
                    deck['name'] = new_name
                    mw.col.decks.save(deck)
                    
                    # Atualizar também na configuração
                    from .config_manager import get_meta, save_meta, get_deck_hash
                    try:
                        meta = get_meta()
                        deck_hash = get_deck_hash(url)
                        if 'decks' in meta and deck_hash in meta['decks']:
                            meta['decks'][deck_hash]['local_deck_name'] = new_name
                            save_meta(meta)
                    except Exception as e:
                        print(f"[WARNING] Erro ao atualizar local_deck_name na configuração: {e}")
                    
                    return new_name
        except Exception as e:
            print(f"[WARNING] Erro ao atualizar nome do deck: {e}")
            pass
        
        return current_name
    
    @staticmethod
    def _should_update_to_desired_name(current_name, desired_name):
        """
        Determina se deve atualizar para o nome desejado.
        Compara o nome base (sem sufixo numérico) com o nome desejado.
        
        Args:
            current_name (str): Nome atual do deck
            desired_name (str): Nome desejado
            
        Returns:
            bool: True se deve atualizar
        """
        if not current_name or not desired_name:
            return False
        
        # Extrair nome base do atual (removendo sufixo numérico)
        has_suffix, base_name, _ = DeckNamer.has_numeric_suffix(current_name)
        comparison_name = base_name if has_suffix else current_name
        
        # Comparar com o nome desejado (ignorando case)
        should_update = desired_name.lower() != comparison_name.lower()
        
        return should_update
    
    @staticmethod
    def _get_available_deck_name(desired_name):
        """
        Obtém um nome disponível para o deck, adicionando sufixo se necessário.
        
        Args:
            desired_name (str): Nome desejado
            
        Returns:
            str: Nome disponível (pode ter sufixo numérico se o desejado já existir)
        """
        if not mw or not mw.col or not mw.col.decks:
            return desired_name
        
        # Verificar se o nome desejado está disponível
        existing_deck = mw.col.decks.by_name(desired_name)
        if not existing_deck:
            return desired_name
        
        # Se já existe, adicionar sufixo numérico
        counter = 2
        while True:
            candidate_name = f"{desired_name}_{counter}"
            existing = mw.col.decks.by_name(candidate_name)
            if not existing:
                return candidate_name
            counter += 1
            
            # Evitar loop infinito
            if counter > 100:
                return f"{desired_name}_{counter}"


# =============================================================================
# FUNÇÕES DE COMPATIBILIDADE PARA MANTER A API EXISTENTE
# =============================================================================

# Estas funções são mantidas para compatibilidade com o código existente
# e simplesmente delegam para os métodos estáticos da classe DeckNamer

def extract_deck_name_from_url(url):
    return DeckNamer.extract_name_from_url(url)

def generate_automatic_deck_name(url):
    return DeckNamer.generate_name(url)

def clean_deck_name(name):
    return DeckNamer.clean_name(name)

def check_deck_name_conflict(deck_name):
    return DeckNamer.check_conflict(deck_name)

def resolve_deck_name_conflict(base_name, max_attempts=100):
    return DeckNamer.resolve_conflict(base_name, max_attempts)

def get_available_deck_name(url):
    return DeckNamer.get_available_name(url)

def should_update_deck_name(url, current_name):
    return DeckNamer.should_update_name(url, current_name)

def update_deck_name_if_needed(url, deck_id, current_name, remote_deck_name=None):
    return DeckNamer.update_name_if_needed(url, deck_id, current_name, remote_deck_name)


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