"""
Módulo de Análise de Decks Remotos

Este módulo implementa a funcionalidade para baixar e processar dados de decks
remotos a partir de planilhas do Google Sheets em formato TSV.

Funcionalidades principais:
- Download de dados TSV de URLs remotas
- Validação de headers e estrutura dos dados
- Processamento de campos e criação de tags hierárquicas
- Detecção de cards cloze
- Tratamento robusto de erros

Fluxo de processamento:
1. getRemoteDeck() -> Download e coordenação geral
2. parse_tsv_data() -> Análise inicial dos dados TSV
3. build_remote_deck_from_tsv() -> Construção do deck
4. create_tags_from_fields() -> Criação de sistema hierárquico de tags

Classes:
- RemoteDeck: Representa um deck carregado de fonte remota
- RemoteDeckError: Exceção customizada para erros de deck remoto

Funções principais:
- getRemoteDeck(): Função principal para obter e processar deck remoto
- parse_tsv_data(): Análise e validação de dados TSV
- build_remote_deck_from_tsv(): Construção do objeto deck a partir dos dados
- create_tags_from_fields(): Criação de tags hierárquicas dos campos

Autor: Sheets2Anki Project
"""

# =============================================================================
# IMPORTS
# =============================================================================

import csv
import urllib.request
import urllib.error
import socket
import re  # Para expressões regulares
from . import column_definitions as cols  # Definições centralizadas de colunas

# =============================================================================
# CUSTOM EXCEPTIONS
# =============================================================================

class RemoteDeckError(Exception):
    """Exceção customizada para erros relacionados a decks remotos."""
    pass

# =============================================================================
# CORE CLASSES
# =============================================================================

class RemoteDeck:
    """
    Classe que representa um deck carregado de uma fonte TSV remota.
    
    Esta classe encapsula os dados de um deck obtido de uma planilha
    remota, incluindo questões, mídia e metadados.
    
    Attributes:
        deckName (str): Nome do deck
        questions (list): Lista de questões/cards do deck
        media (list): Lista de arquivos de mídia associados
    """
    
    def __init__(self):
        """Inicializa um deck remoto vazio."""
        self.deckName = ""
        self.questions = []  # Mantém o atributo 'questions' para compatibilidade
        self.media = []

    def getMedia(self):
        """
        Retorna a lista de arquivos de mídia do deck.
        
        Returns:
            list: Lista de arquivos de mídia
        """
        return self.media

# =============================================================================
# MAIN PROCESSING FUNCTIONS
# =============================================================================

def getRemoteDeck(url):
    """
    Obtém e processa um deck remoto a partir de uma URL TSV.
    
    Esta é a função principal que coordena todo o processo de:
    1. Download dos dados da URL remota
    2. Decodificação do conteúdo
    3. Análise e validação dos dados TSV
    4. Construção do objeto RemoteDeck
    
    Args:
        url (str): URL da planilha em formato TSV
        
    Returns:
        RemoteDeck: Objeto contendo o deck processado
        
    Raises:
        RemoteDeckError: Se houver erro no download, decodificação ou processamento
    """
    # 1. Download dos dados remotos
    try:
        # Usar timeout de 30 segundos e headers apropriados
        headers = {
            'User-Agent': 'Mozilla/5.0 (Sheets2Anki) AnkiAddon'
        }
        request = urllib.request.Request(url, headers=headers)
        
        response = urllib.request.urlopen(request, timeout=30)  # ✅ TIMEOUT LOCAL
        
        if response.getcode() != 200:
            raise RemoteDeckError(f"URL retornou código de status inesperado: {response.getcode()}")
            
    except socket.timeout:
        raise RemoteDeckError(f"Timeout ao acessar URL (30s). Verifique sua conexão ou tente novamente.")
    except urllib.error.HTTPError as e:
        raise RemoteDeckError(f"Erro HTTP {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        if isinstance(e.reason, socket.timeout):
            raise RemoteDeckError(f"Timeout ao acessar URL. Verifique sua conexão ou tente novamente.")
        elif isinstance(e.reason, socket.gaierror):
            raise RemoteDeckError(f"Erro de DNS. Verifique sua conexão com a internet.")
        else:
            raise RemoteDeckError(f"Erro de conexão: {str(e.reason)}")
    except Exception as e:
        raise RemoteDeckError(f"Erro inesperado de rede ao baixar TSV: {e}")
    
    # 2. Decodificação do conteúdo
    try:
        tsv_data = response.read().decode('utf-8')
    except UnicodeDecodeError as e:
        raise RemoteDeckError(f"Erro ao decodificar conteúdo TSV: {e}")

    # 3. Análise e construção do deck
    try:
        data = parse_tsv_data(tsv_data)
        remoteDeck = build_remote_deck_from_tsv(data)
        return remoteDeck
    except Exception as e:
        raise RemoteDeckError(f"Erro ao processar deck remoto: {e}")

# =============================================================================
# DATA PARSING AND VALIDATION FUNCTIONS
# =============================================================================

def validate_tsv_headers(headers):
    """
    Valida se o TSV possui os headers obrigatórios.
    
    Verifica se todos os campos obrigatórios definidos em column_definitions
    estão presentes no arquivo TSV.
    
    Args:
        headers (list): Lista de headers do arquivo TSV
        
    Returns:
        list: Lista de headers em maiúsculas para padronização
        
    Raises:
        ValueError: Se algum header obrigatório estiver faltando
    """
    headers_upper = [h.strip().upper() for h in headers]
    missing_headers = [h for h in cols.REQUIRED_COLUMNS if h not in headers_upper]
    
    if missing_headers:
        raise ValueError(f"Colunas obrigatórias faltando: {', '.join(missing_headers)}")
    
    return headers_upper

def parse_tsv_data(tsv_data):
    """
    Analisa e valida dados TSV.
    
    Processa o conteúdo TSV bruto e valida sua estrutura básica,
    garantindo que possui headers e pelo menos uma linha de dados.
    
    Args:
        tsv_data (str): Conteúdo TSV bruto como string
        
    Returns:
        list: Lista de listas representando as linhas do TSV
        
    Raises:
        ValueError: Se o arquivo estiver vazio, mal formatado ou sem dados suficientes
    """
    try:
        reader = csv.reader(tsv_data.splitlines(), delimiter='\t')
        data = list(reader)
        
        if not data:
            raise ValueError("Arquivo TSV está vazio")
            
        if len(data) < 2:  # Pelo menos headers e uma linha
            raise ValueError("Arquivo TSV deve conter headers e pelo menos um card")
            
        return data
    except csv.Error as e:
        raise ValueError(f"Formato TSV inválido: {str(e)}")

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def has_cloze_deletion(text):
    """
    Verifica se o texto contém deletions cloze no formato {{c1::text}}.
    
    Utiliza expressão regular para detectar padrões de cloze deletion
    que são usados para criar cards de preenchimento de lacunas.
    
    Args:
        text (str): Texto a ser verificado
        
    Returns:
        bool: True se contém cloze deletions, False caso contrário
    """
    return bool(re.search(r'\{\{c\d+::.+?\}\}', text))

def clean_tag_text(text):
    """
    Limpa texto para uso em tags removendo caracteres especiais.
    
    Remove caracteres especiais e converte espaços em underscores
    para criar tags compatíveis com o Anki.
    
    Args:
        text (str): Texto a ser limpo
        
    Returns:
        str: Texto limpo e formatado para tag, ou string vazia se inválido
    """
    if not text or not text.strip():
        return ""
    return re.sub(r'[^\w\s]', '', text.strip()).replace(' ', '_')

# =============================================================================
# TAG CREATION FUNCTIONS
# =============================================================================

def create_tags_from_fields(fields):
    """
    Cria tags hierárquicas a partir de campos específicos.
    
    Esta função processa diferentes campos do card e cria um sistema
    hierárquico de tags para melhor organização no Anki.
    
    Estrutura de tags criadas:
    - topicos::topico1::subtopicos_do_topico1
    - bancas::banca1
    - provas::ano1
    - variado::tag_adicional1
    
    Args:
        fields (dict): Dicionário contendo os campos do card
        
    Returns:
        list: Lista de tags hierárquicas compatíveis com o Anki
        
    Examples:
        >>> fields = {'TOPICO': 'Direito Civil', 'SUBTOPICO': 'Contratos, Responsabilidade'}
        >>> create_tags_from_fields(fields)
        ['topicos::Direito_Civil::Contratos', 'topicos::Direito_Civil::Responsabilidade']
    """
    tags = []
    
    # Processar TOPICO e SUBTOPICO
    topico = clean_tag_text(fields.get(cols.TOPICO, ''))
    subtopicos_raw = fields.get(cols.SUBTOPICO, '')
    
    if topico:
        if subtopicos_raw:
            # Dividir subtópicos por vírgula e processar cada um
            for subtopico in subtopicos_raw.split(','):
                subtopico_clean = clean_tag_text(subtopico)
                if subtopico_clean:
                    tags.append(f"topicos::{topico}::{subtopico_clean}")
        else:
            # Se não há subtópicos, criar tag apenas com tópico principal
            tags.append(f"topicos::{topico}")
            
    # Processar BANCAS (pode ter múltiplos valores separados por vírgula)
    bancas = fields.get(cols.BANCAS, '')
    if bancas:
        for banca in bancas.split(','):
            banca_clean = clean_tag_text(banca)
            if banca_clean:
                tags.append(f"bancas::{banca_clean}")
                
    # Processar ANO
    ano = clean_tag_text(fields.get(cols.ANO, ''))
    if ano:
        tags.append(f"provas::{ano}")
        
    # Processar MORE_TAGS (tags adicionais)
    more_tags = fields.get(cols.MORE_TAGS, '')
    if more_tags:
        for tag in more_tags.split(','):
            tag_clean = clean_tag_text(tag)
            if tag_clean:
                tags.append(f"variado::{tag_clean}")
    
    return tags

# =============================================================================
# DECK BUILDING FUNCTIONS
# =============================================================================

def build_remote_deck_from_tsv(data):
    """
    Constrói um objeto RemoteDeck a partir de dados TSV processados.
    
    Esta função é responsável pela construção completa do deck, incluindo:
    1. Validação e processamento de headers
    2. Processamento linha por linha dos dados
    3. Validação de campos obrigatórios
    4. Criação de tags hierárquicas
    5. Construção das questões finais
    
    Args:
        data (list): Lista de listas contendo os dados TSV (headers + rows)
        
    Returns:
        RemoteDeck: Objeto deck completamente processado e validado
        
    Raises:
        ValueError: Se os headers forem inválidos ou dados estiverem malformados
    """
    # 1. Processar e validar headers
    headers = validate_tsv_headers(data[0])
    
    # 2. Criar mapeamento de header para índice
    header_indices = {header: idx for idx, header in enumerate(headers)}
    
    # 3. Processar cada linha de dados
    questions = []
    for row_num, row in enumerate(data[1:], start=2):
        question = _process_tsv_row(row, headers, header_indices, row_num)
        if question:  # Apenas adicionar se a questão for válida
            questions.append(question)

    # 4. Criar e retornar deck
    remoteDeck = RemoteDeck()
    remoteDeck.deckName = "Deck from CSV"
    remoteDeck.questions = questions

    return remoteDeck

def _process_tsv_row(row, headers, header_indices, row_num):
    """
    Processa uma única linha do TSV e cria uma questão.
    
    Args:
        row (list): Dados da linha atual
        headers (list): Lista de headers
        header_indices (dict): Mapeamento de header para índice
        row_num (int): Número da linha (para debug)
        
    Returns:
        dict: Questão processada ou None se inválida
    """
    # Pular linhas vazias
    if not any(cell.strip() for cell in row):
        return None

    # Validar comprimento da linha
    if len(row) != len(headers):
        return None

    # Criar dicionário de campos
    fields = _create_fields_dict(row, headers, header_indices)

    # Validar campos obrigatórios
    if not fields[cols.ID] or not fields[cols.PERGUNTA]:
        return None

    # Gerar tags dos campos
    tags = create_tags_from_fields(fields)
    
    # Criar e retornar questão com tags
    return {
        'fields': fields,
        'tags': tags
    }

def _create_fields_dict(row, headers, header_indices):
    """
    Cria dicionário de campos a partir da linha de dados.
    
    Args:
        row (list): Dados da linha
        headers (list): Lista de headers
        header_indices (dict): Mapeamento de header para índice
        
    Returns:
        dict: Dicionário com campos preenchidos
    """
    fields = {}
    for header in headers:
        idx = header_indices[header]
        if idx < len(row):
            fields[header] = row[idx].strip()
        else:
            fields[header] = ""
    
    return fields
