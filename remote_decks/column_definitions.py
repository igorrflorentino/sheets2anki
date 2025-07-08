"""
Definições de Colunas para Planilhas Sheets2Anki

Este módulo centraliza todas as definições de nomes de colunas utilizadas
nas planilhas do Google Sheets para sincronização com o Anki.

Funcionalidades principais:
- Definição padronizada de nomes de colunas
- Mapeamento de campos da planilha para campos do Anki
- Validação de estrutura de dados
- Configuração centralizadas para facilitar manutenção

Estrutura da planilha esperada:
- ID: Identificador único da questão
- PERGUNTA: Texto principal da questão/frente do cartão
- LEVAR PARA PROVA: Campo de filtro para seleção de questões
- Campos informativos: Informações complementares e detalhadas
- Exemplos: Até 3 exemplos relacionados à questão
- Categorização: Tópico, subtópico, bancas e ano
- Tags: Tags adicionais para organização

Autor: Sheets2Anki Project
"""

# =============================================================================
# DEFINIÇÕES DE COLUNAS PRINCIPAIS
# =============================================================================

# Campos obrigatórios básicos
ID = 'ID'                           # Identificador único da questão
PERGUNTA = 'PERGUNTA'               # Texto principal da questão/frente do cartão
MATCH = 'LEVAR PARA PROVA'          # Campo de filtro (sim/não para incluir na sincronização)

# =============================================================================
# CAMPOS INFORMATIVOS E COMPLEMENTARES
# =============================================================================

# Informações adicionais sobre a questão
EXTRA_INFO_1 = 'INFO COMPLEMENTAR'  # Informação complementar básica
EXTRA_INFO_2 = 'INFO DETALHADA'     # Informação detalhada adicional

# =============================================================================
# CAMPOS DE EXEMPLOS
# =============================================================================

# Exemplos relacionados à questão (até 3 exemplos)
EXEMPLO_1 = 'EXEMPLO 1'             # Primeiro exemplo
EXEMPLO_2 = 'EXEMPLO 2'             # Segundo exemplo
EXEMPLO_3 = 'EXEMPLO 3'             # Terceiro exemplo

# =============================================================================
# CAMPOS DE CATEGORIZAÇÃO E METADADOS
# =============================================================================

# Categorização hierárquica do conteúdo
TOPICO = 'TOPICO'                   # Tópico principal da questão
SUBTOPICO = 'SUBTOPICO'             # Subtópico específico

# Informações de contexto e fonte
BANCAS = 'BANCAS'                   # Bancas organizadoras relacionadas
ANO = 'ULTIMO ANO EM PROVA'         # Último ano em que apareceu em prova
MORE_TAGS = 'TAGS ADICIONAIS'       # Tags adicionais para organização

# =============================================================================
# CONFIGURAÇÕES DE VALIDAÇÃO
# =============================================================================

# Lista completa de colunas obrigatórias na planilha
REQUIRED_COLUMNS = [
    ID,                    # Identificador único
    PERGUNTA,              # Texto da questão
    MATCH,                 # Filtro de inclusão
    EXTRA_INFO_1,          # Info complementar
    EXTRA_INFO_2,          # Info detalhada
    EXEMPLO_1,             # Primeiro exemplo
    EXEMPLO_2,             # Segundo exemplo
    EXEMPLO_3,             # Terceiro exemplo
    TOPICO,                # Tópico principal
    SUBTOPICO,             # Subtópico
    BANCAS,                # Bancas relacionadas
    ANO,                   # Ano da prova
    MORE_TAGS              # Tags adicionais
]

# =============================================================================
# CONFIGURAÇÕES ESPECIAIS
# =============================================================================

# Campos que são considerados obrigatórios para criação de notas
ESSENTIAL_FIELDS = [ID, PERGUNTA]

# Campos que podem ser usados para filtragem/seleção
FILTER_FIELDS = [MATCH, TOPICO, SUBTOPICO, BANCAS]

# Campos que contêm informações textuais extensas
TEXT_FIELDS = [PERGUNTA, EXTRA_INFO_1, EXTRA_INFO_2, EXEMPLO_1, EXEMPLO_2, EXEMPLO_3]

# Campos que contêm metadados e tags
METADATA_FIELDS = [TOPICO, SUBTOPICO, BANCAS, ANO, MORE_TAGS]

# =============================================================================
# FUNÇÕES UTILITÁRIAS
# =============================================================================

def validate_required_columns(columns):
    """
    Valida se todas as colunas obrigatórias estão presentes na planilha.
    
    Args:
        columns (list): Lista de nomes de colunas da planilha
        
    Returns:
        tuple: (is_valid, missing_columns) onde:
            - is_valid: bool indicando se todas as colunas estão presentes
            - missing_columns: lista de colunas ausentes
            
    Examples:
        >>> columns = ['ID', 'PERGUNTA', 'LEVAR PARA PROVA']
        >>> is_valid, missing = validate_required_columns(columns)
        >>> print(f"Válido: {is_valid}, Faltando: {missing}")
    """
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in columns]
    return len(missing_columns) == 0, missing_columns

def is_essential_field(field_name):
    """
    Verifica se um campo é considerado essencial para criação de notas.
    
    Args:
        field_name (str): Nome do campo a verificar
        
    Returns:
        bool: True se o campo é essencial, False caso contrário
        
    Examples:
        >>> is_essential_field('ID')
        True
        >>> is_essential_field('EXEMPLO_1')
        False
    """
    return field_name in ESSENTIAL_FIELDS

def is_filter_field(field_name):
    """
    Verifica se um campo pode ser usado para filtragem/seleção.
    
    Args:
        field_name (str): Nome do campo a verificar
        
    Returns:
        bool: True se o campo pode ser usado para filtro, False caso contrário
        
    Examples:
        >>> is_filter_field('TOPICO')
        True
        >>> is_filter_field('EXEMPLO_1')
        False
    """
    return field_name in FILTER_FIELDS

def get_field_category(field_name):
    """
    Retorna a categoria de um campo específico.
    
    Args:
        field_name (str): Nome do campo
        
    Returns:
        str: Categoria do campo ('essential', 'text', 'metadata', 'filter', 'unknown')
        
    Examples:
        >>> get_field_category('ID')
        'essential'
        >>> get_field_category('PERGUNTA')
        'essential'
        >>> get_field_category('TOPICO')
        'metadata'
    """
    if field_name in ESSENTIAL_FIELDS:
        return 'essential'
    elif field_name in TEXT_FIELDS:
        return 'text'
    elif field_name in METADATA_FIELDS:
        return 'metadata'
    elif field_name in FILTER_FIELDS:
        return 'filter'
    else:
        return 'unknown'

def get_all_column_info():
    """
    Retorna informações completas sobre todas as colunas definidas.
    
    Returns:
        dict: Dicionário com informações detalhadas de cada coluna
        
    Examples:
        >>> info = get_all_column_info()
        >>> print(info['ID']['category'])
        'essential'
    """
    column_info = {}
    
    for column in REQUIRED_COLUMNS:
        column_info[column] = {
            'name': column,
            'category': get_field_category(column),
            'is_essential': is_essential_field(column),
            'is_filter': is_filter_field(column),
            'is_text': column in TEXT_FIELDS,
            'is_metadata': column in METADATA_FIELDS
        }
    
    return column_info