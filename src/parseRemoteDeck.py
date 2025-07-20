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
from .constants import DEFAULT_TOPIC, DEFAULT_SUBTOPIC, DEFAULT_CONCEPT, TAG_ROOT, TAG_TOPICS, TAG_SUBTOPICS, TAG_CONCEPTS

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
        ignored_count (int): Número de cards ignorados devido à coluna SYNC?
    """
    
    def __init__(self):
        """Inicializa um deck remoto vazio."""
        self.deckName = ""
        self.questions = []  # Mantém o atributo 'questions' para compatibilidade
        self.media = []
        self.ignored_count = 0  # Contador de cards ignorados

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
    1. Validação da URL
    2. Modificação da URL para garantir valores calculados
    3. Download dos dados com fallback para URLs alternativas
    4. Decodificação do conteúdo
    5. Análise e validação dos dados TSV
    6. Construção do objeto RemoteDeck
    
    Args:
        url (str): URL da planilha em formato TSV
        
    Returns:
        RemoteDeck: Objeto contendo o deck processado
        
    Raises:
        RemoteDeckError: Se houver erro no download, decodificação ou processamento
    """
    original_url = url
    
    # 0. Validar URL antes de processá-la
    validation_result = validate_google_sheets_url(url)
    if not validation_result['valid']:
        issues = '; '.join(validation_result['issues'])
        suggestions = '; '.join(validation_result['suggestions']) if validation_result['suggestions'] else "Verifique se a URL está correta"
        raise RemoteDeckError(f"URL inválida: {issues}. Sugestões: {suggestions}")
    
    # 1. Garantir que a URL retorne valores calculados, não fórmulas
    try:
        processed_url = ensure_values_only_url(url)
        if processed_url != url:
            # Logging para debug (pode ser removido em produção)
            pass  # print(f"📝 URL modificada para garantir valores calculados: {processed_url}")
    except Exception as e:
        # Se falhar na modificação da URL, continuar com a original
        processed_url = url
    
    # 2. Preparar lista de URLs para tentar (principal + fallbacks)
    urls_to_try = [processed_url]
    fallback_urls = create_fallback_urls(processed_url, validation_result)
    urls_to_try.extend(fallback_urls)
    
    # 3. Tentar download com cada URL
    last_error = None
    successful_url = None
    
    for attempt, try_url in enumerate(urls_to_try, 1):
        try:
            # Headers apropriados
            headers = {
                'User-Agent': 'Mozilla/5.0 (Sheets2Anki) AnkiAddon'
            }
            request = urllib.request.Request(try_url, headers=headers)
            
            response = urllib.request.urlopen(request, timeout=30)
            
            if response.getcode() != 200:
                raise Exception(f"Código de status inesperado: {response.getcode()}")
            
            successful_url = try_url
            break  # Sucesso! Sair do loop
            
        except socket.timeout:
            last_error = RemoteDeckError(f"Timeout ao acessar URL (30s). Verifique sua conexão ou tente novamente.")
            continue
        except urllib.error.HTTPError as e:
            if e.code == 404:
                # Para erro 404, preparar mensagem específica
                if attempt == 1:
                    last_error = RemoteDeckError(
                        f"Planilha não encontrada (HTTP 404). Possíveis causas:\n"
                        f"• Planilha não está compartilhada publicamente\n"
                        f"• URL está incorreta ou incompleta\n"
                        f"• Planilha foi movida ou deletada\n"
                        f"• GID (ID da aba) está incorreto\n\n"
                        f"Tentando URLs alternativas..."
                    )
                else:
                    last_error = RemoteDeckError(
                        f"Planilha não encontrada após {attempt} tentativas. Verifique:\n"
                        f"• Se a planilha está compartilhada publicamente\n"
                        f"• Se a URL está correta: {original_url}\n"
                        f"• Se a aba especificada existe"
                    )
            elif e.code == 403:
                last_error = RemoteDeckError(
                    f"Acesso negado (HTTP 403). A planilha não está compartilhada publicamente.\n"
                    f"Vá em Arquivo > Compartilhar > Alterar para 'Qualquer pessoa com o link'"
                )
                break  # Para 403, não tentar outras URLs
            else:
                last_error = RemoteDeckError(f"Erro HTTP {e.code}: {e.reason}")
            continue
        except urllib.error.URLError as e:
            if isinstance(e.reason, socket.timeout):
                last_error = RemoteDeckError(f"Timeout ao acessar URL. Verifique sua conexão ou tente novamente.")
            elif isinstance(e.reason, socket.gaierror):
                last_error = RemoteDeckError(f"Erro de DNS. Verifique sua conexão com a internet.")
            else:
                last_error = RemoteDeckError(f"Erro de conexão: {str(e.reason)}")
            continue
        except Exception as e:
            last_error = RemoteDeckError(f"Erro inesperado de rede ao baixar TSV: {e}")
            continue
    
    # Se nenhuma URL funcionou, lançar o último erro
    if successful_url is None:
        if last_error:
            raise last_error
        else:
            raise RemoteDeckError(f"Falha ao acessar a planilha após {len(urls_to_try)} tentativas")
    
    # 4. Decodificação do conteúdo
    try:
        tsv_data = response.read().decode('utf-8')
    except UnicodeDecodeError as e:
        raise RemoteDeckError(f"Erro ao decodificar conteúdo TSV: {e}")

    # 5. Análise e construção do deck
    try:
        data = parse_tsv_data(tsv_data)
        remoteDeck = build_remote_deck_from_tsv(data)
        # Armazenar URLs para uso posterior
        remoteDeck.url = original_url
        remoteDeck.successful_url = successful_url
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

def clean_formula_errors(cell_value):
    """
    Limpa erros de fórmula e expressões de fórmula do Google Sheets.
    
    Esta função remove erros de fórmula como #NAME?, #REF!, etc. e
    expressões de fórmula como =SUM(), =VLOOKUP(), etc.
    
    Args:
        cell_value (str): Valor da célula a ser limpo
        
    Returns:
        str: Valor limpo sem erros de fórmula ou expressões de fórmula
        
    Examples:
        >>> clean_formula_errors('#NAME?')
        ''
        >>> clean_formula_errors('=SUM(A1:A10)')
        ''
        >>> clean_formula_errors('Conteúdo normal')
        'Conteúdo normal'
    """
    if not cell_value or not isinstance(cell_value, str):
        return ""
    
    # Padrões de erro de fórmula
    error_patterns = [
        r'#NAME\?', r'#REF!', r'#VALUE!', r'#DIV/0!', 
        r'#N/A', r'#NULL!', r'#NUM!'
    ]
    
    # Verificar se é um erro de fórmula completo
    for pattern in error_patterns:
        if re.match(f'^{pattern}$', cell_value):
            return ""
    
    # Verificar se é uma expressão de fórmula completa
    if cell_value.startswith('='):
        # Verificar se é uma fórmula completa
        if re.match(r'^=\w+\(.*\)$', cell_value) or re.match(r'^=[A-Z0-9+\-*/]+$', cell_value):
            return ""
    
    # Limpar erros de fórmula dentro do texto
    cleaned_value = cell_value
    for pattern in error_patterns:
        cleaned_value = re.sub(pattern, '', cleaned_value)
    
    # Limpar expressões de fórmula dentro do texto
    cleaned_value = re.sub(r'=\w+\([^)]*\)', '', cleaned_value)
    
    return cleaned_value

def clean_formula_errors_with_logging(cell_value, field_name="", row_num=None):
    """
    Preserva valores de célula do TSV com logging para debug.
    
    MODIFICAÇÃO: Esta função agora retorna SEMPRE o valor original sem nenhuma 
    conversão para string vazia. Os dados do TSV devem ser entregues para as 
    notas do Anki tal qual como foram capturados.
    
    Args:
        cell_value (str): Valor da célula a ser preservado
        field_name (str): Nome do campo (para logging)
        row_num (int): Número da linha (para logging)
        
    Returns:
        str: Valor original sem modificações
    """
    # Retornar sempre o valor original sem nenhuma modificação
    return cell_value
        
        # Para ambientes de desenvolvimento, você pode descomentar esta linha:
        # print(f"⚠️  {problem_type.title()} detectado e limpo: '{original_value.strip()}' → '' ({location_info})")
    
    return cleaned_value

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
    
    Estrutura de tags criadas (todas sob a tag raiz 'sheet2anki'):
    - sheet2anki::topicos::topico1::subtopico1::conceito1
    - sheet2anki::conceitos::conceito1 (tag extra para fácil filtragem)
    - sheet2anki::bancas::banca1
    - sheet2anki::provas::ano1
    - sheet2anki::carreiras::carreira1
    - sheet2anki::importancia::nivel_importancia
    - sheet2anki::variado::tag_adicional1
    
    Args:
        fields (dict): Dicionário contendo os campos do card
        
    Returns:
        list: Lista de tags hierárquicas compatíveis com o Anki
    """
    tags = []
    
    # Processar TOPICO, SUBTOPICO e CONCEITO de forma hierárquica
    topico = clean_tag_text(fields.get(cols.TOPICO, '') or DEFAULT_TOPIC)
    subtopicos = [clean_tag_text(s) for s in (fields.get(cols.SUBTOPICO, '') or DEFAULT_SUBTOPIC).split(',') if clean_tag_text(s)]
    conceitos = [clean_tag_text(c) for c in (fields.get(cols.CONCEITO, '') or DEFAULT_CONCEPT).split(',') if clean_tag_text(c)]

    for subtopico in subtopicos:
        tags.append(f"{TAG_ROOT}::{TAG_TOPICS}::{topico}::{subtopico}")
        for conceito in conceitos:
            tags.append(f"{TAG_ROOT}::{TAG_TOPICS}::{topico}::{subtopico}::{conceito}")
            tags.append(f"{TAG_ROOT}::{TAG_CONCEPTS}::{conceito}")
            
    # Processar BANCAS (pode ter múltiplos valores separados por vírgula)
    bancas = fields.get(cols.BANCAS, '')
    if bancas:
        for banca in bancas.split(','):
            banca_clean = clean_tag_text(banca)
            if banca_clean:
                tags.append(f"{TAG_ROOT}::bancas::{banca_clean}")
                
    # Processar ANO
    ano = clean_tag_text(fields.get(cols.ANO, ''))
    if ano:
        tags.append(f"{TAG_ROOT}::provas::{ano}")
        
    # Processar CARREIRA (pode ter múltiplos valores separados por vírgula)
    carreira = fields.get(cols.CARREIRA, '')
    if carreira:
        for carr in carreira.split(','):
            carr_clean = clean_tag_text(carr)
            if carr_clean:
                tags.append(f"{TAG_ROOT}::carreiras::{carr_clean}")
        
    # Processar IMPORTANCIA
    importancia = clean_tag_text(fields.get(cols.IMPORTANCIA, ''))
    if importancia:
        tags.append(f"{TAG_ROOT}::importancia::{importancia}")
        
    # Processar MORE_TAGS (tags adicionais)
    more_tags = fields.get(cols.MORE_TAGS, '')
    if more_tags:
        for tag in more_tags.split(','):
            tag_clean = clean_tag_text(tag)
            if tag_clean:
                tags.append(f"{TAG_ROOT}::variado::{tag_clean}")
    
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
    6. Contagem de cards ignorados devido à coluna SYNC?
    
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
    ignored_count = 0
    for row_num, row in enumerate(data[1:], start=2):
        question = _process_tsv_row(row, headers, header_indices, row_num)
        if question:  # Apenas adicionar se a questão for válida
            questions.append(question)
        else:
            # Verificar se foi ignorada devido à coluna SYNC?
            if _row_ignored_due_to_sync(row, headers, header_indices):
                ignored_count += 1

    # 4. Criar e retornar deck
    remoteDeck = RemoteDeck()
    remoteDeck.deckName = "Deck from TSV"
    remoteDeck.questions = questions
    remoteDeck.ignored_count = ignored_count

    return remoteDeck

def _row_ignored_due_to_sync(row, headers, header_indices):
    """
    Verifica se uma linha foi ignorada especificamente devido à coluna SYNC?.
    
    Args:
        row (list): Dados da linha
        headers (list): Lista de headers
        header_indices (dict): Mapeamento de header para índice
        
    Returns:
        bool: True se a linha foi ignorada devido à coluna SYNC?, False caso contrário
    """
    # Verificar se a linha não está vazia
    if not any(cell.strip() for cell in row):
        return False
    
    # Verificar se o comprimento da linha é válido
    if len(row) != len(headers):
        return False
    
    # Criar dicionário de campos
    fields = _create_fields_dict(row, headers, header_indices)
    
    # Verificar se os campos obrigatórios estão presentes
    if not fields[cols.ID] or not fields[cols.PERGUNTA]:
        return False
    
    # Se chegou até aqui, a linha só foi rejeitada se should_sync_question retornou False
    return not cols.should_sync_question(fields)

def _process_tsv_row(row, headers, header_indices, row_num):
    """
    Processa uma única linha do TSV e cria uma questão.
    
    Args:
        row (list): Dados da linha atual
        headers (list): Lista de headers
        header_indices (dict): Mapeamento de header para índice
        row_num (int): Número da linha (para debug)
        
    Returns:
        dict: Questão processada ou None se inválida ou não deve ser sincronizada
    """
    # Pular linhas vazias
    if not any(cell.strip() for cell in row):
        return None

    # Validar comprimento da linha
    if len(row) != len(headers):
        return None

    # Criar dicionário de campos
    fields = _create_fields_dict(row, headers, header_indices, row_num)

    # Validar campos obrigatórios
    if not fields[cols.ID] or not fields[cols.PERGUNTA]:
        return None

    # Verificar se a questão deve ser sincronizada
    if not cols.should_sync_question(fields):
        return None

    # Gerar tags dos campos
    tags = create_tags_from_fields(fields)
    
    # Criar e retornar questão com tags
    return {
        'fields': fields,
        'tags': tags
    }

def _create_fields_dict(row, headers, header_indices, row_num=None):
    """
    Cria dicionário de campos a partir da linha de dados.
    
    Aplica limpeza nos valores das células para remover erros de fórmulas
    do Google Sheets (como #NAME?, #REF!, etc.).
    
    Args:
        row (list): Dados da linha
        headers (list): Lista de headers
        header_indices (dict): Mapeamento de header para índice
        row_num (int, optional): Número da linha para logging
        
    Returns:
        dict: Dicionário com campos preenchidos e limpos
    """
    fields = {}
    for header in headers:
        idx = header_indices[header]
        if idx < len(row):
            raw_value = row[idx].strip()
            # Limpar erros de fórmula antes de armazenar (com logging)
            cleaned_value = clean_formula_errors_with_logging(raw_value, header, row_num)
            fields[header] = cleaned_value
        else:
            fields[header] = ""
    
    return fields

def ensure_values_only_url(url):
    """
    Garante que a URL do Google Sheets retorne apenas valores calculados, não fórmulas.
    
    O Google Sheets tem diferentes parâmetros de exportação:
    - format=tsv: Exporta em formato TSV
    - gid=: ID da aba (se específica)
    - output=tsv: Força output TSV
    - exportFormat=tsv: Formato de exportação
    
    Para garantir valores calculados ao invés de fórmulas:
    - Usar /export? ao invés de /edit#gid=
    - Adicionar parâmetros que forçam valor calculado
    
    Args:
        url (str): URL original da planilha
        
    Returns:
        str: URL modificada para garantir valores calculados
        
    Examples:
        >>> url = "https://docs.google.com/spreadsheets/d/ABC123/edit#gid=0"
        >>> ensure_values_only_url(url)
        "https://docs.google.com/spreadsheets/d/ABC123/export?format=tsv&gid=0"
    """
    import re
    from urllib.parse import urlparse, parse_qs
    
    # Se não é URL do Google Sheets, retornar como está
    if 'docs.google.com/spreadsheets' not in url:
        return url
    
    # Extrair ID da planilha - considerar tanto URLs normais (/d/ID) quanto publicadas (/d/e/ID)
    # Tentar primeiro o formato publicado /d/e/ID
    spreadsheet_id_match = re.search(r'/spreadsheets/d/e/([a-zA-Z0-9-_]+)', url)
    if spreadsheet_id_match:
        spreadsheet_id = spreadsheet_id_match.group(1)
        # Para URLs publicadas, apenas garantir que estão no formato correto
        # Não converter para /export pois isso não funciona para URLs publicadas
        return url
    
    # Tentar formato normal /d/ID
    spreadsheet_id_match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', url)
    if not spreadsheet_id_match:
        return url
    
    spreadsheet_id = spreadsheet_id_match.group(1)
    
    # Extrair GID se presente
    gid = "0"  # Padrão
    
    # Tentar extrair GID do fragmento (#gid=123)
    if '#gid=' in url:
        gid_match = re.search(r'#gid=([^&\s]+)', url)
        if gid_match:
            gid = gid_match.group(1)
    
    # Tentar extrair GID dos parâmetros (?gid=123)
    elif '?gid=' in url or '&gid=' in url:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        if 'gid' in params:
            gid = params['gid'][0]
    
    # Construir URL de export que garante valores calculados
    export_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export"
    export_url += f"?format=tsv&exportFormat=tsv&gid={gid}"
    
    return export_url

def detect_formula_content(cell_value):
    """
    Detecta se o conteúdo da célula ainda contém uma fórmula não calculada.
    
    Além dos erros de fórmula (#NAME?, #REF!, etc.), algumas vezes o Google Sheets
    pode exportar a própria fórmula como texto. Esta função detecta esses casos.
    
    Args:
        cell_value (str): Valor da célula
        
    Returns:
        bool: True se parecer ser uma fórmula, False caso contrário
        
    Examples:
        >>> detect_formula_content('=SUM(A1:A10)')
        True
        >>> detect_formula_content('=VLOOKUP(B2,D:E,2,FALSE)')
        True
        >>> detect_formula_content('=GEMINI_2_5_FLASH("texto")')
        True
        >>> detect_formula_content('Texto normal')
        False
        >>> detect_formula_content('=5+3')
        True
        >>> detect_formula_content('= não é fórmula')
        False
        >>> detect_formula_content('=')
        False
    """
    if not cell_value or not isinstance(cell_value, str):
        return False
    
    cell_value = cell_value.strip()
    
    # Verificar se é apenas o sinal de igual
    if cell_value == '=':
        return False
    
    # Verificar se começa com = mas não é uma fórmula válida
    if cell_value.startswith('='):
        # Deve ter pelo menos um caractere após o =
        if len(cell_value) <= 1:
            return False
        
        # Verificar padrões de fórmulas Gemini PRIMEIRO (prioridade máxima)
        # Fórmulas Gemini são sempre consideradas válidas, independente do conteúdo
        gemini_patterns = [
            r'^=GEMINI_\w+\(',  # =GEMINI_QUALQUER_COISA(
            r'^=AI_\w+\(',      # =AI_QUALQUER_COISA(
        ]
        
        for pattern in gemini_patterns:
            if re.search(pattern, cell_value):
                return True
        
        # Verificar padrões de fórmulas válidas PRIMEIRO (antes dos indicadores)
        # Isso permite que fórmulas legítimas sejam detectadas mesmo com palavras comuns
        valid_formula_patterns = [
            r'^=\w+\(',  # =FUNCAO(
            r'^=\w+_\w+\(',  # =FUNCAO_COMPOSTA( (ex: GEMINI_2_5_FLASH)
            r'^=\w+_\w+_\w+\(',  # =FUNCAO_COMPOSTA_LONGA( (ex: GEMINI_2_5_FLASH)
            r'^=\d+[\+\-\*\/]',  # =5+, =10*, etc.
            r'^=[A-Z]+\d+',  # =A1, =B2, etc.
            r'^=.*\([^\)]*\).*$',  # Qualquer função com parênteses
            r'^=\d+(\.\d+)?([\+\-\*\/]\d+(\.\d+)?)+$',  # Operações matemáticas: =5+3, =10*2.5
        ]
        
        # Verificar padrões válidos primeiro
        for pattern in valid_formula_patterns:
            if re.search(pattern, cell_value):
                # Se coincide com um padrão válido, verificar se não é falso positivo
                # Para fórmulas com parênteses, assumir que são válidas
                if '(' in cell_value and ')' in cell_value:
                    return True
                # Para outros padrões, continuar com verificação de indicadores
                break
        else:
            # Se não coincide com nenhum padrão válido, não é fórmula
            return False
        
        # Verificar padrões de fórmulas válidas
        formula_content = cell_value[1:]  # Remove o =
        
        # Se contém apenas espaços após =, não é fórmula
        if not formula_content.strip():
            return False
        
        # Para fórmulas com parênteses, ser menos restritivo com indicadores
        # Verificar se é uma função válida (tem parênteses balanceados)
        if '(' in cell_value and ')' in cell_value:
            # Contar parênteses para verificar se estão balanceados
            open_count = cell_value.count('(')
            close_count = cell_value.count(')')
            if open_count == close_count and open_count > 0:
                # É provável que seja uma função válida, aplicar filtros mais relaxados
                restrictive_indicators = [
                    ' não é ', ' nao é ', ' não deve ', ' nao deve ',
                    ' não pode ', ' nao pode ', ' não tem ', ' nao tem ',
                ]
                
                for indicator in restrictive_indicators:
                    if indicator in cell_value.lower():
                        return False
                
                # Se passou nos filtros restritivos, é uma fórmula
                return True
        
        # Para outros casos, aplicar filtros mais rigorosos
        non_formula_indicators = [
            ' não ', ' nao ', ' is ', ' are ', ' was ', ' were ',
            ' the ', ' and ', ' or ', ' but ', ' if ', ' when ',
            ' para ', ' com ', ' sem ', ' por ', ' em ',
            # Removido ' de ' - muito comum em fórmulas legítimas (ex: Gemini)
        ]
        
        for indicator in non_formula_indicators:
            if indicator in cell_value.lower():
                return False
        
        # Se passou em todos os testes, verificar novamente os padrões
        for pattern in valid_formula_patterns:
            if re.search(pattern, cell_value):
                return True
        
        return False
    
    return False

def validate_google_sheets_url(url):
    """
    Valida se a URL é uma URL válida do Google Sheets.
    
    Verifica estrutura, ID da planilha e se a URL está bem formatada.
    
    Args:
        url (str): URL a ser validada
        
    Returns:
        dict: Resultado da validação com detalhes
        
    Examples:
        >>> validate_google_sheets_url("https://docs.google.com/spreadsheets/d/1ABC123/edit#gid=0")
        {'valid': True, 'spreadsheet_id': '1ABC123', 'gid': '0', 'issues': []}
    """
    import re
    from urllib.parse import urlparse
    
    result = {
        'valid': False,
        'spreadsheet_id': None,
        'gid': None,
        'issues': [],
        'suggestions': []
    }
    
    if not url or not isinstance(url, str):
        result['issues'].append("URL está vazia ou não é uma string")
        return result
    
    url = url.strip()
    
    # Verificar se é URL do Google Sheets
    if 'docs.google.com/spreadsheets' not in url:
        result['issues'].append("URL não é do Google Sheets")
        result['suggestions'].append("URL deve conter 'docs.google.com/spreadsheets'")
        return result
    
    # Verificar estrutura básica da URL
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            result['issues'].append("URL mal formatada (sem scheme ou netloc)")
            return result
    except Exception as e:
        result['issues'].append(f"Erro ao analisar URL: {e}")
        return result
    
    # Extrair ID da planilha - tentar primeiro padrão de URL publicada
    spreadsheet_id_match = re.search(r'/spreadsheets/d/e/([^/]+)', url)
    if not spreadsheet_id_match:
        # Tentar padrão normal (/d/ID)
        spreadsheet_id_match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', url)
        if not spreadsheet_id_match:
            result['issues'].append("ID da planilha não encontrado na URL")
            result['suggestions'].append("URL deve ter formato: /spreadsheets/d/[ID]/ ou /spreadsheets/d/e/[ID]/")
            return result
    
    result['spreadsheet_id'] = spreadsheet_id_match.group(1)
    
    # Extrair GID se presente
    gid = "0"  # Padrão
    
    # Tentar extrair GID do fragmento (#gid=123)
    if '#gid=' in url:
        gid_match = re.search(r'#gid=([^&\s]+)', url)
        if gid_match:
            gid = gid_match.group(1)
    
    # Tentar extrair GID dos parâmetros (?gid=123)
    elif '?gid=' in url or '&gid=' in url:
        from urllib.parse import parse_qs
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        if 'gid' in params:
            gid = params['gid'][0]
    
    result['gid'] = gid
    
    # Verificar se ID da planilha é muito curto (erro crítico)
    if len(result['spreadsheet_id']) < 10:
        result['issues'].append("ID da planilha muito curto - provavelmente inválido")
        result['suggestions'].append("Verifique se a URL está completa e correta")
    # Warning para IDs curtos mas possivelmente válidos
    elif len(result['spreadsheet_id']) < 20:
        result['suggestions'].append("ID da planilha parece curto - IDs do Google geralmente têm 44+ caracteres")
    
    # Se chegou até aqui sem problemas críticos, é válida
    if not result['issues']:
        result['valid'] = True
    
    return result

def create_fallback_urls(original_url, validation_result):
    """
    Cria URLs alternativas para tentar em caso de erro 404.
    
    Args:
        original_url (str): URL original que falhou
        validation_result (dict): Resultado da validação da URL
        
    Returns:
        list: Lista de URLs alternativas para tentar
    """
    fallback_urls = []
    
    if not validation_result.get('valid') or not validation_result.get('spreadsheet_id'):
        return fallback_urls
    
    spreadsheet_id = validation_result['spreadsheet_id']
    gid = validation_result.get('gid', '0')
    
    # Detectar se é URL publicada (/d/e/) ou normal (/d/)
    is_published = '/d/e/' in original_url
    
    if is_published:
        # Para URLs publicadas, usar formato /d/e/ID/pub
        
        # URL 1: Pub TSV com GID 0
        fallback_urls.append(
            f"https://docs.google.com/spreadsheets/d/e/{spreadsheet_id}/pub?output=tsv&gid=0"
        )
        
        # URL 2: Pub TSV com GID específico (se diferente de 0)
        if gid != '0':
            fallback_urls.append(
                f"https://docs.google.com/spreadsheets/d/e/{spreadsheet_id}/pub?output=tsv&gid={gid}"
            )
        
        # URL 3: Pub CSV como fallback
        fallback_urls.append(
            f"https://docs.google.com/spreadsheets/d/e/{spreadsheet_id}/pub?output=csv&gid=0"
        )
        
        # URL 4: Tentar formato tradicional (sem /e/)
        fallback_urls.append(
            f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=tsv&gid=0"
        )
    else:
        # Para URLs normais, usar formato /d/ID/export
        
        # URL 1: Export básico com GID 0 (aba padrão)
        fallback_urls.append(
            f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=tsv&exportFormat=tsv&gid=0"
        )
        
        # URL 2: Export com GID detectado (se diferente de 0)
        if gid != '0':
            fallback_urls.append(
                f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=tsv&exportFormat=tsv&gid={gid}"
            )
        
        # URL 3: Export sem GID especificado
        fallback_urls.append(
            f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=tsv&exportFormat=tsv"
        )
        
        # URL 4: Export com output=tsv
        fallback_urls.append(
            f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?output=tsv&gid=0"
        )
    
    # Remover duplicatas mantendo ordem
    seen = set()
    unique_fallbacks = []
    for url in fallback_urls:
        if url not in seen and url != original_url:
            seen.add(url)
            unique_fallbacks.append(url)
    
    return unique_fallbacks
