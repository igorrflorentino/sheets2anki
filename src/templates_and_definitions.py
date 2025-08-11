"""
Templates e definições de colunas para o addon Sheets2Anki.

Este módulo centraliza:
- Definições padronizadas de nomes de colunas das planilhas
- Templates HTML para cards do Anki
- Funções para criação de modelos de notas
- Validação de estrutura de dados

Consolidado de:
- card_templates.py: Templates e modelos de cards
- column_definitions.py: Definições de colunas da planilha
"""

# =============================================================================
# DEFINIÇÕES DE COLUNAS PRINCIPAIS
# =============================================================================

# Campos obrigatórios básicos
ID = "ID"  # Identificador único da questão
PERGUNTA = "PERGUNTA"  # Texto principal da questão/frente do cartão
MATCH = (
    "LEVAR PARA PROVA"  # Resposta sucinta e atômica da pergunta (núcleo da resposta)
)
SYNC = "SYNC?"  # Campo de controle de sincronização (true/false/1/0)
ALUNOS = "ALUNOS"  # Indica quais alunos têm interesse em estudar esta nota

# =============================================================================
# CAMPOS INFORMATIVOS E COMPLEMENTARES
# =============================================================================

# Informações adicionais sobre a questão
EXTRA_INFO_1 = "INFO COMPLEMENTAR"  # Informação complementar básica
EXTRA_INFO_2 = "INFO DETALHADA"  # Informação detalhada adicional

# =============================================================================
# CAMPOS DE EXEMPLOS
# =============================================================================

# Exemplos relacionados à questão (até 3 exemplos)
EXEMPLO_1 = "EXEMPLO 1"  # Primeiro exemplo
EXEMPLO_2 = "EXEMPLO 2"  # Segundo exemplo
EXEMPLO_3 = "EXEMPLO 3"  # Terceiro exemplo

# =============================================================================
# CAMPOS DE CATEGORIZAÇÃO E METADADOS
# =============================================================================

# Categorização hierárquica do conteúdo
TOPICO = "TOPICO"  # Tópico principal da questão
SUBTOPICO = "SUBTOPICO"  # Subtópico específico
CONCEITO = "CONCEITO"  # Conceito atômico sendo perguntado (mais refinado que subtópico)

# Informações de contexto e fonte
BANCAS = "BANCAS"  # Bancas organizadoras relacionadas
ANO = "ULTIMO ANO EM PROVA"  # Último ano em que apareceu em prova
CARREIRAS = "CARREIRAS"  # Carreiras ou áreas profissionais relacionadas
IMPORTANCIA = "IMPORTANCIA"  # Nível de importância da questão
MORE_TAGS = "TAGS ADICIONAIS"  # Tags adicionais para organização

# =============================================================================
# CONFIGURAÇÕES DE VALIDAÇÃO
# =============================================================================

# Lista completa de colunas obrigatórias na planilha
REQUIRED_COLUMNS = [
    ID,  # Identificador único
    PERGUNTA,  # Texto da questão
    MATCH,  # Resposta sucinta (núcleo da resposta)
    SYNC,  # Controle de sincronização
    ALUNOS,  # Controle de alunos interessados
    EXTRA_INFO_1,  # Info complementar
    EXTRA_INFO_2,  # Info detalhada
    EXEMPLO_1,  # Primeiro exemplo
    EXEMPLO_2,  # Segundo exemplo
    EXEMPLO_3,  # Terceiro exemplo
    TOPICO,  # Tópico principal
    SUBTOPICO,  # Subtópico
    CONCEITO,  # Conceito atômico
    BANCAS,  # Bancas relacionadas
    ANO,  # Ano da prova
    CARREIRAS,  # Carreiras ou áreas profissionais
    IMPORTANCIA,  # Nível de importância
    MORE_TAGS,  # Tags adicionais
]

# =============================================================================
# CONFIGURAÇÕES ESPECIAIS
# =============================================================================

# Campos que são considerados obrigatórios para criação de notas
ESSENTIAL_FIELDS = [ID]

# Campos que podem ser usados para filtragem/seleção (exceto SYNC que é apenas controle interno)
FILTER_FIELDS = [MATCH, TOPICO, SUBTOPICO, CONCEITO, BANCAS, CARREIRAS, IMPORTANCIA]

# Campos que contêm informações textuais extensas
TEXT_FIELDS = [
    PERGUNTA,
    MATCH,
    EXTRA_INFO_1,
    EXTRA_INFO_2,
    EXEMPLO_1,
    EXEMPLO_2,
    EXEMPLO_3,
]

# Campos que devem ser incluídos nas notas do Anki (excluindo controles internos)
NOTE_FIELDS = [
    ID,  # Identificador único
    PERGUNTA,  # Texto da questão
    MATCH,  # Resposta sucinta (núcleo da resposta)
    EXTRA_INFO_1,  # Info complementar
    EXTRA_INFO_2,  # Info detalhada
    EXEMPLO_1,  # Primeiro exemplo
    EXEMPLO_2,  # Segundo exemplo
    EXEMPLO_3,  # Terceiro exemplo
    TOPICO,  # Tópico principal
    SUBTOPICO,  # Subtópico
    CONCEITO,  # Conceito atômico
    BANCAS,  # Bancas relacionadas
    ANO,  # Ano da prova
    CARREIRAS,  # Carreiras ou áreas profissionais
    IMPORTANCIA,  # Nível de importância
    MORE_TAGS,  # Tags adicionais
]

# Campos que contêm metadados e tags
METADATA_FIELDS = [
    TOPICO,
    SUBTOPICO,
    CONCEITO,
    BANCAS,
    ANO,
    CARREIRAS,
    IMPORTANCIA,
    MORE_TAGS,
]

# =============================================================================
# FUNÇÕES DE VALIDAÇÃO DE COLUNAS
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
    """
    return field_name in ESSENTIAL_FIELDS


def is_filter_field(field_name):
    """
    Verifica se um campo pode ser usado para filtragem/seleção.

    Args:
        field_name (str): Nome do campo a verificar

    Returns:
        bool: True se o campo pode ser usado para filtro, False caso contrário
    """
    return field_name in FILTER_FIELDS


def get_field_category(field_name):
    """
    Retorna a categoria de um campo específico.

    Args:
        field_name (str): Nome do campo

    Returns:
        str: Categoria do campo ('essential', 'text', 'metadata', 'filter', 'unknown')
    """
    if field_name in ESSENTIAL_FIELDS:
        return "essential"
    elif field_name in TEXT_FIELDS:
        return "text"
    elif field_name in METADATA_FIELDS:
        return "metadata"
    elif field_name in FILTER_FIELDS:
        return "filter"
    else:
        return "unknown"


def should_sync_question(fields):
    """
    Verifica se uma questão deve ser sincronizada com base no campo SYNC.

    Args:
        fields (dict): Dicionário com campos da questão

    Returns:
        bool: True se deve sincronizar, False caso contrário
    """
    sync_value = fields.get(SYNC, "").strip().lower()

    # Considerar valores positivos: true, 1, sim, yes, verdadeiro
    positive_values = ["true", "1", "sim", "yes", "verdadeiro", "v"]

    # Considerar valores negativos: false, 0, não, no, falso
    negative_values = ["false", "0", "não", "nao", "no", "falso", "f"]

    if sync_value in positive_values:
        return True
    elif sync_value in negative_values:
        return False
    else:
        # Se o valor não for reconhecido, assumir que deve sincronizar
        # para manter compatibilidade com planilhas antigas
        return True


def get_all_column_info():
    """
    Retorna informações completas sobre todas as colunas definidas.

    Returns:
        dict: Dicionário com informações detalhadas de cada coluna
    """
    column_info = {}

    for column in REQUIRED_COLUMNS:
        column_info[column] = {
            "name": column,
            "category": get_field_category(column),
            "is_essential": is_essential_field(column),
            "is_filter": is_filter_field(column),
            "is_text": column in TEXT_FIELDS,
            "is_metadata": column in METADATA_FIELDS,
        }

    return column_info


# =============================================================================
# TEMPLATES DE CARDS
# =============================================================================


def create_card_template(is_cloze=False):
    """
    Cria o template HTML para um card (padrão ou cloze).

    Args:
        is_cloze (bool): Se deve criar um template de cloze

    Returns:
        dict: Dicionário com strings de template 'qfmt' e 'afmt'
    """

    # Campos de cabeçalho comuns
    header_fields = [
        (TOPICO, TOPICO),
        (SUBTOPICO, SUBTOPICO),
        (CONCEITO, CONCEITO),
    ]

    # Construir seção de cabeçalho
    header = ""
    for field_name, field_value in header_fields:
        header += CARD_SHOW_ALLWAYS_TEMPLATE.format(
            field_name=field_name.capitalize(), field_value=field_value
        )

    # Formato da pergunta
    question = (
        "<hr><br>"
        f"<b>{PERGUNTA.capitalize()}:</b><br>"
        f"{{{{{'cloze:' if is_cloze else ''}{PERGUNTA}}}}}"
    )

    # Formato da resposta
    match = (
        "<br><br>"
        f"<b>{MATCH.capitalize()}:</b><br>"
        f"{{{{{'cloze:' if is_cloze else ''}{MATCH}}}}}"
        "<br><br><hr><br>"
    )

    # Campos de informação extra
    extra_info_fields = [EXTRA_INFO_1, EXTRA_INFO_2]

    extra_info = ""
    for field in extra_info_fields:
        extra_info += CARD_SHOW_HIDE_TEMPLATE.format(
            field_name=field.capitalize(), field_value=field
        )

    # Campos de exemplo
    example_fields = [EXEMPLO_1, EXEMPLO_2, EXEMPLO_3]

    examples = ""
    for field in example_fields:
        examples += CARD_SHOW_HIDE_TEMPLATE.format(
            field_name=field.capitalize(), field_value=field
        )

    # Campos de rodapé
    footer_fields = [
        (BANCAS, BANCAS),
        (ANO, ANO),
        (CARREIRAS, CARREIRAS),
        (IMPORTANCIA, IMPORTANCIA),
        (MORE_TAGS, MORE_TAGS),
    ]

    # Construir seção de rodapé
    footer = ""
    for field_name, field_value in footer_fields:
        footer += CARD_SHOW_HIDE_TEMPLATE.format(
            field_name=field_name.capitalize(), field_value=field_value
        )

    # Construir templates completos
    qfmt = header + question
    afmt = (
        (header + question + match + extra_info + examples + "<hr><br>" + footer)
        if is_cloze
        else ("{{FrontSide}}" + match + extra_info + examples + "<hr><br>" + footer)
    )

    return {"qfmt": qfmt, "afmt": afmt}


def create_model(col, model_name, is_cloze=False, url=None, debug_messages=None):
    """
    Cria um novo modelo de nota do Anki.

    Args:
        col: Objeto de coleção do Anki
        model_name (str): Nome para o novo modelo
        is_cloze (bool): Se deve criar um modelo de cloze
        url (str, optional): URL do deck remoto para registro automático
        debug_messages (list, optional): Lista para debug

    Returns:
        object: O modelo do Anki criado
    """
    from .utils import register_note_type_for_deck

    model = col.models.new(model_name)
    if is_cloze:
        model["type"] = 1  # Definir como tipo cloze

    # Adicionar campos (excluindo campos de controle interno como SYNC?)
    for field in NOTE_FIELDS:
        template = col.models.new_field(field)
        col.models.add_field(model, template)

    # Adicionar template de card
    template = col.models.new_template("Cloze" if is_cloze else "Card 1")
    card_template = create_card_template(is_cloze)
    template["qfmt"] = card_template["qfmt"]
    template["afmt"] = card_template["afmt"]

    col.models.add_template(model, template)
    col.models.save(model)

    # Registrar automaticamente o note type se URL foi fornecida
    if url and model.get("id"):
        try:
            register_note_type_for_deck(url, model["id"], model_name, debug_messages)
        except Exception as e:
            if debug_messages:
                debug_messages.append(f"Erro ao registrar note type {model['id']}: {e}")

    return model


def ensure_custom_models(col, url, student=None, debug_messages=None):
    """
    Garante que ambos os modelos (padrão e cloze) existam no Anki.
    Usa os IDs armazenados no meta.json para encontrar note types existentes,
    ao invés de buscar apenas por nome.

    Args:
        col: Objeto de coleção do Anki
        url (str): URL do deck remoto
        student (str, optional): Nome do aluno para criar modelos específicos
        debug_messages (list, optional): Lista para debug

    Returns:
        dict: Dicionário contendo os modelos 'standard' e 'cloze'
    """
    from .config_manager import get_deck_note_type_ids
    from .config_manager import get_deck_remote_name
    from .utils import get_note_type_name
    from .utils import register_note_type_for_deck

    def add_debug_msg(message):
        if debug_messages:
            debug_messages.append(f"[ENSURE_MODELS] {message}")
        print(f"[ENSURE_MODELS] {message}")

    models = {}

    # Obter nome do deck remoto e note types existentes
    remote_deck_name = get_deck_remote_name(url) or "RemoteDeck"
    existing_note_types = get_deck_note_type_ids(url) or {}

    add_debug_msg(
        f"Procurando note types para student='{student}', remote_deck_name='{remote_deck_name}'"
    )
    add_debug_msg(f"Note types existentes: {len(existing_note_types)} encontrados")

    # Função helper para encontrar note type por padrão
    def find_existing_note_type(is_cloze):
        target_type = "Cloze" if is_cloze else "Basic"
        target_pattern = (
            f" - {student} - {target_type}" if student else f" - {target_type}"
        )

        # Procurar nos note types existentes
        for note_type_id_str, note_type_name in existing_note_types.items():
            if note_type_name.endswith(target_pattern):
                try:
                    note_type_id = int(note_type_id_str)
                    model = col.models.get(note_type_id)
                    if model:
                        add_debug_msg(
                            f"Encontrado note type existente: ID {note_type_id} - '{note_type_name}'"
                        )
                        return model, note_type_name
                except (ValueError, TypeError):
                    continue
        return None, None

    # Modelo padrão (Basic)
    expected_name = get_note_type_name(
        url, remote_deck_name, student=student, is_cloze=False
    )
    existing_model, existing_name = find_existing_note_type(is_cloze=False)

    if existing_model:
        # Use o modelo existente e NÃO force um nome novo se já está registrado
        current_registered_name = None
        for note_type_id_str, note_type_name in existing_note_types.items():
            try:
                if int(note_type_id_str) == existing_model["id"]:
                    current_registered_name = note_type_name
                    break
            except ValueError:
                continue

        if current_registered_name:
            # Já está registrado, usar nome atual da configuração
            add_debug_msg(
                f"Usando modelo existente (Basic) JÁ REGISTRADO: '{existing_name}' com nome config: '{current_registered_name}'"
            )
            models["standard"] = existing_model
        else:
            # Não está registrado, registrar com nome esperado
            register_note_type_for_deck(
                url, existing_model["id"], expected_name, debug_messages
            )
            models["standard"] = existing_model
            add_debug_msg(
                f"Modelo existente (Basic) registrado: '{existing_name}' → esperado: '{expected_name}'"
            )
    else:
        # Criar novo modelo apenas se realmente não existir
        add_debug_msg(f"Criando novo modelo (Basic): '{expected_name}'")
        model = create_model(
            col, expected_name, is_cloze=False, url=url, debug_messages=debug_messages
        )
        models["standard"] = model

    # Modelo cloze
    expected_cloze_name = get_note_type_name(
        url, remote_deck_name, student=student, is_cloze=True
    )
    existing_cloze_model, existing_cloze_name = find_existing_note_type(is_cloze=True)

    if existing_cloze_model:
        # Use o modelo existente e NÃO force um nome novo se já está registrado
        current_registered_cloze_name = None
        for note_type_id_str, note_type_name in existing_note_types.items():
            try:
                if int(note_type_id_str) == existing_cloze_model["id"]:
                    current_registered_cloze_name = note_type_name
                    break
            except ValueError:
                continue

        if current_registered_cloze_name:
            # Já está registrado, usar nome atual da configuração
            add_debug_msg(
                f"Usando modelo existente (Cloze) JÁ REGISTRADO: '{existing_cloze_name}' com nome config: '{current_registered_cloze_name}'"
            )
            models["cloze"] = existing_cloze_model
        else:
            # Não está registrado, registrar com nome esperado
            register_note_type_for_deck(
                url, existing_cloze_model["id"], expected_cloze_name, debug_messages
            )
            models["cloze"] = existing_cloze_model
            add_debug_msg(
                f"Modelo existente (Cloze) registrado: '{existing_cloze_name}' → esperado: '{expected_cloze_name}'"
            )
    else:
        # Criar novo modelo apenas se realmente não existir
        add_debug_msg(f"Criando novo modelo (Cloze): '{expected_cloze_name}'")
        cloze_model = create_model(
            col,
            expected_cloze_name,
            is_cloze=True,
            url=url,
            debug_messages=debug_messages,
        )
        models["cloze"] = cloze_model

    return models


# =============================================================================
# CONSTANTES E TEMPLATES (movidas de utils.py)
# =============================================================================

# Constante para identificar se estamos em modo de desenvolvimento
# Esta constante será alterada para False durante o processo de build
IS_DEVELOPMENT_MODE = True

# URLs hardcoded para testes e simulações
TEST_SHEETS_URLS = [
    (
        "Sheets2Anki Template",
        "https://docs.google.com/spreadsheets/d/e/2PACX-1vSsNCEFZvBR3UjBwTbyaPPz-B1SKw17I7Jb72XWweS1y75HmzXfgdFJ1TpZX6_S06m9_phJTy5XnCI6/pub?gid=36065074&single=true&output=tsv",
    ),
]

# Template constants para geração de cards
CARD_SHOW_ALLWAYS_TEMPLATE = """
<b>{field_name}:</b><br>
{{{{{field_value}}}}}<br><br>
"""

CARD_SHOW_HIDE_TEMPLATE = """
{{{{#{field_value}}}}}
<b>{field_name}:</b><br>
{{{{{field_value}}}}}<br><br>
{{{{/{field_value}}}}}
"""

# Valores padrão para campos vazios
DEFAULT_IMPORTANCE = "[MISSING I.]"
DEFAULT_TOPIC = "[MISSING T.]"
DEFAULT_SUBTOPIC = "[MISSING S.]"
DEFAULT_CONCEPT = "[MISSING C.]"

# Nome do deck raiz - constante não modificável pelo usuário
DEFAULT_PARENT_DECK_NAME = "Sheets2Anki"

# Prefixos para tags
TAG_ROOT = "Sheets2Anki"
TAG_TOPICS = "topicos"
TAG_SUBTOPICS = "subtopicos"
TAG_CONCEPTS = "conceitos"
TAG_BANCAS = "bancas"
TAG_ANOS = "anos"
TAG_CARREIRAS = "carreiras"
TAG_IMPORTANCIA = "importancia"
TAG_ADICIONAIS = "adicionais"
