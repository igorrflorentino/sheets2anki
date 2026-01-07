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
# CAMPOS DE CONTROLE
# =============================================================================

# Campos básicos do sistema
identificador = "ID"  # Identificador único da questão (obrigatório)
alunos = "ALUNOS"  # Indica quais alunos têm interesse em estudar esta nota
is_sync = "SYNC"  # Campo de controle de sincronização (true/false/1/0)

# =============================================================================
# CAMPOS PRINCIPAIS
# =============================================================================

# Campos principais da questão
pergunta = "PERGUNTA"  # Texto principal da questão/frente do cartão
resposta = "LEVAR PARA PROVA"  # Resposta sucinta e atômica da pergunta

# =============================================================================
# CAMPOS DE DETALHES
# =============================================================================

# Informações adicionais sobre a questão
info_1 = "INFO COMPLEMENTAR"  # Informação complementar básica
info_2 = "INFO DETALHADA"  # Informação detalhada adicional

# =============================================================================
# CAMPOS DE EXEMPLOS
# =============================================================================

# Exemplos relacionados à questão (até 3 exemplos)
exemplo_1 = "EXEMPLO 1"  # Primeiro exemplo
exemplo_2 = "EXEMPLO 2"  # Segundo exemplo
exemplo_3 = "EXEMPLO 3"  # Terceiro exemplo

# =============================================================================
# CAMPOS DE MULTIMIDIA
# =============================================================================

# Ajuda a tornar a informação visualmente mais atraente
multimidia_1 = "IMAGEM HTML"  # Código HTML para imagens e ilustrações renderizáveis
multimidia_2 = "VÍDEO HTML"  # Código HTML para vídeos embedded (YouTube, Vimeo, etc.)

# =============================================================================
# CAMPOS DE CATEGORIZAÇÃO
# =============================================================================

# Categorização hierárquica do conteúdo
hierarquia_1 = "IMPORTANCIA"  # Nível de importância da questão
hierarquia_2 = "TOPICO"  # Tópico principal da questão
hierarquia_3 = "SUBTOPICO"  # Subtópico específico
hierarquia_4 = "CONCEITO"  # Conceito atômico sendo perguntado (mais refinado que subtópico)

# =============================================================================
# CAMPOS DE METADADOS
# =============================================================================

# Informações de contexto e fonte
tags_1 = "BANCAS"  # Bancas organizadoras relacionadas
tags_2 = "ULTIMO ANO EM PROVA"  # Último ano em que apareceu em prova
tags_3 = "CARREIRAS"  # Carreiras ou áreas profissionais relacionadas
tags_4 = "TAGS ADICIONAIS"  # Tags adicionais para organização

# =============================================================================
# CAMPOS EXTRAS PERSONALIZÁVEIS
# =============================================================================

# Campos extras para uso personalizado do usuário
extra_field_1 = "EXTRA 1"  # Campo extra 1 - uso livre
extra_field_2 = "EXTRA 2"  # Campo extra 2 - uso livre
extra_field_3 = "EXTRA 3"  # Campo extra 3 - uso livre

# =============================================================================
# CONFIGURAÇÕES DE VALIDAÇÃO
# =============================================================================

# Lista completa de todas as colunas disponíveis na planilha
ALL_AVAILABLE_COLUMNS = [
    identificador,  # Identificador único
    alunos,  # Controle de alunos interessados
    is_sync,  # Controle de sincronização

    hierarquia_1,  # Nível de importância
    hierarquia_2,  # Tópico principal
    hierarquia_3,  # Subtópico
    hierarquia_4,  # Conceito atômico

    pergunta,  # Texto principal da questão/frente do cartão
    resposta,  # Resposta sucinta (núcleo da resposta)

    info_1,  # Info complementar
    info_2,  # Info detalhada

    exemplo_1,  # Primeiro exemplo
    exemplo_2,  # Segundo exemplo
    exemplo_3,  # Terceiro exemplo

    multimidia_1,  # Código HTML para imagens e ilustrações
    multimidia_2,  # Código HTML para vídeos embedded

    tags_1,  # Bancas relacionadas
    tags_2,  # Ano da prova
    tags_3,  # Carreiras ou áreas profissionais
    tags_4,  # Tags adicionais

    extra_field_1,  # Campo extra 1
    extra_field_2,  # Campo extra 2
    extra_field_3,  # Campo extra 3
]

# Campos que são considerados obrigatórios para criação de notas
ESSENTIAL_FIELDS = [identificador]

# Campos que são obrigatórios nos headers da planilha (para parsing funcionar)
REQUIRED_HEADERS = [identificador, pergunta, resposta]

# Campos que podem ser usados para filtragem/seleção
FILTER_FIELDS = [hierarquia_1, hierarquia_2, hierarquia_3, hierarquia_4,
                 tags_1, tags_2, tags_3, tags_4]

# Campos que contêm informações textuais extensas
TEXT_FIELDS = [
    pergunta,
    resposta,
    info_1,
    info_2,
    exemplo_1,
    exemplo_2,
    exemplo_3,
    extra_field_1,
    extra_field_2,
    extra_field_3,
]

# Campos que contêm mídias (imagens, vídeos, etc.)
MEDIA_FIELDS = [
    multimidia_1,
    multimidia_2,
]

# Campos que devem ser incluídos nas notas do Anki
NOTE_FIELDS = [
    identificador,  # Identificador único
    
    hierarquia_1,  # Nível de importância
    hierarquia_2,  # Tópico principal
    hierarquia_3,  # Subtópico
    hierarquia_4,  # Conceito atômico
    
    pergunta,  # Texto da questão
    resposta,  # Resposta sucinta (núcleo da resposta)
    
    info_1,  # Info complementar
    info_2,  # Info detalhada
    
    exemplo_1,  # Primeiro exemplo
    exemplo_2,  # Segundo exemplo
    exemplo_3,  # Terceiro exemplo
    
    multimidia_1,  # Código HTML para imagens e ilustrações
    multimidia_2,  # Código HTML para vídeos embedded

    extra_field_1,  # Campo extra 1
    extra_field_2,  # Campo extra 2
    extra_field_3,  # Campo extra 3
    
    tags_1,  # Bancas relacionadas
    tags_2,  # Ano da prova
    tags_3,  # Carreiras ou áreas profissionais
    tags_4,  # Tags adicionais
]

# Campos que contêm metadados
METADATA_FIELDS = [
    hierarquia_1,
    hierarquia_2,
    hierarquia_3,
    hierarquia_4,
    tags_1,
    tags_2,
    tags_3,
    tags_4,
]

# =============================================================================
# CONSTANTES E TEMPLATES
# =============================================================================

# Constante para identificar se estamos em modo de desenvolvimento
# Esta constante será alterada para False durante o processo de build
IS_DEVELOPMENT_MODE = True

# URLs hardcoded para testes e simulações
TEST_SHEETS_URLS = [
    (
        "Sheets2Anki Template (Edit Link)",
        "https://docs.google.com/spreadsheets/d/1N-Va4ZzLUJBsD6wBaOkoeFTE6EnbZdaPBB88FYl2hrs/edit?usp=sharing",
    )
]

# Template constants para geração de cards
CARD_SHOW_ALLWAYS_TEMPLATE = """
<b>➡️ {field_name}</b><br>
{{{{{field_value}}}}}<br><br>
"""

CARD_SHOW_HIDE_TEMPLATE = """
{{{{#{field_value}}}}}
<b>➡️ {field_name}</b><br>
{{{{{field_value}}}}}<br><br>
{{{{/{field_value}}}}}
"""

MARCADORES_TEMPLATE = """
<h2 style="color: orange; text-align: center; margin-bottom: 0;">{texto}</h2>
<div style="text-align: center; font-size: 0.8em; color: gray;">{observacao}</div>
<hr>
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
    missing_columns = [col for col in ALL_AVAILABLE_COLUMNS if col not in columns]
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
    sync_value = fields.get(is_sync, "").strip().lower()

    # Considerar valores positivos: true, 1, sim, yes, verdadeiro
    positive_values = ["true", "1", "sim", "yes", "verdadeiro", "v"]

    if sync_value in positive_values:
        return True
    else:
        # Se o valor não for reconhecido ou estiver vazio, NÃO sincronizar
        # A sincronização deve ser explicitamente marcada
        return False


def get_all_column_info():
    """
    Retorna informações completas sobre todas as colunas definidas.

    Returns:
        dict: Dicionário com informações detalhadas de cada coluna
    """
    column_info = {}

    for column in ALL_AVAILABLE_COLUMNS:
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
        (hierarquia_1, hierarquia_1),
        (hierarquia_2, hierarquia_2),
        (hierarquia_3, hierarquia_3),
        (hierarquia_4, hierarquia_4),
    ]

    # Construir seção de cabeçalho
    header = ""
    for field_name, field_value in header_fields:
        header += CARD_SHOW_ALLWAYS_TEMPLATE.format(
            field_name=field_name.capitalize(), field_value=field_value
        )

    # Formato da pergunta
    question = (
        f"<b>❓ {pergunta.capitalize()}</b><br>"
        f"{{{{{'cloze:' if is_cloze else ''}{pergunta}}}}}<br><br>"
    )

    # Formato da resposta
    answer = (
        f"<b>❗️ {resposta.capitalize()}</b><br>"
        f"{{{{{'cloze:' if is_cloze else ''}{resposta}}}}}<br><br>"
    )

    # Campos de informações
    info_fields = [info_1, info_2]

    extra_infos = ""
    for info_field in info_fields:
        extra_infos += CARD_SHOW_HIDE_TEMPLATE.format(
            field_name=info_field.capitalize(), field_value=info_field
        )

    # Campo de multimídia imagem
    image_html = CARD_SHOW_HIDE_TEMPLATE.format(
        field_name=multimidia_1.capitalize(), field_value=multimidia_1
    )

    # Campo de multimídia vídeo
    video_html = CARD_SHOW_HIDE_TEMPLATE.format(
        field_name=multimidia_2.capitalize(), field_value=multimidia_2
    )

    # Campos de exemplo
    example_fields = [exemplo_1, exemplo_2, exemplo_3]

    examples = ""
    for field in example_fields:
        examples += CARD_SHOW_HIDE_TEMPLATE.format(
            field_name=field.capitalize(), field_value=field
        )

    # Campos extras personalizáveis
    extra_fields = [extra_field_1, extra_field_2, extra_field_3]

    extras = ""
    for field in extra_fields:
        extras += CARD_SHOW_HIDE_TEMPLATE.format(
            field_name=field.capitalize(), field_value=field
        )

    # Campos de rodapé
    footer_fields = [
        (tags_1, tags_1),
        (tags_2, tags_2),
        (tags_3, tags_3),
        (tags_4, tags_4),
    ]

    # Construir seção de rodapé
    footer = ""
    for field_name, field_value in footer_fields:
        footer += CARD_SHOW_HIDE_TEMPLATE.format(
            field_name=field_name.capitalize(), field_value=field_value
        )

    # Construir templates completos
    qfmt = (
        MARCADORES_TEMPLATE.format(texto="CONTEXTO", observacao="") +
        header +        
        MARCADORES_TEMPLATE.format(texto="CARD", observacao="") +
        question  # Frente: apenas cabeçalho e pergunta
    )
    afmt = (
        MARCADORES_TEMPLATE.format(texto="CONTEXTO", observacao="") +
        (header + 
        MARCADORES_TEMPLATE.format(texto="CARD", observacao="") +
         question +
        MARCADORES_TEMPLATE.format(texto="INFORMAÇÕES", observacao="Pode vir vazio") +
         extra_infos + 
         examples + 
         image_html + 
         video_html + 
         extras + 
         MARCADORES_TEMPLATE.format(texto="TAGS", observacao="Pode vir vazio") + 
         footer)
        if is_cloze
        else (
            "{{FrontSide}}" + 
            answer +
            MARCADORES_TEMPLATE.format(texto="INFORMAÇÕES", observacao="Pode vir vazio") +
            extra_infos + 
            examples + 
            image_html + 
            video_html + 
            extras + 
            MARCADORES_TEMPLATE.format(texto="TAGS", observacao="Pode vir vazio") +
            footer)
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

    # Adicionar campos (excluindo campos de controle interno como SYNC)
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
                    from anki.models import NotetypeId
                    model = col.models.get(NotetypeId(note_type_id))
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

def update_existing_note_type_templates(col, debug_messages=None):
    """
    Atualiza os templates de todos os note types existentes do Sheets2Anki
    para incluir a nova coluna ILUSTRAÇÃO HTML.
    
    Args:
        col: Objeto de coleção do Anki
        debug_messages (list, optional): Lista para debug
    
    Returns:
        int: Número de note types atualizados
    """
    if debug_messages is None:
        debug_messages = []
    
    updated_count = 0
    
    # Buscar todos os note types que começam com "Sheets2Anki"
    all_models = col.models.all()
    sheets2anki_models = [
        model for model in all_models 
        if model.get("name", "").startswith("Sheets2Anki")
    ]
    
    debug_messages.append(f"[UPDATE_TEMPLATES] Encontrados {len(sheets2anki_models)} note types do Sheets2Anki")
    
    for model in sheets2anki_models:
        try:
            model_name = model.get("name", "")
            is_cloze = model.get("type") == 1
            
            debug_messages.append(f"[UPDATE_TEMPLATES] Processando: {model_name} (cloze: {is_cloze})")
            
            # Verificar se o campo ILUSTRAÇÃO HTML já existe
            existing_fields = []
            for field in model.get("flds", []):
                # Lidar com diferentes formatos de campo (dict ou objeto)
                if hasattr(field, 'get'):
                    field_name = field.get("name", "")
                elif isinstance(field, dict):
                    field_name = field.get("name", "")
                else:
                    # Assumir que é um objeto com atributo name
                    field_name = getattr(field, 'name', "")
                existing_fields.append(field_name)
            
            if multimidia_1 not in existing_fields:
                debug_messages.append(f"[UPDATE_TEMPLATES] Adicionando campo {multimidia_1}")
                # Adicionar o campo ILUSTRAÇÃO HTML
                field_template = col.models.new_field(multimidia_1)
                col.models.add_field(model, field_template)
            else:
                debug_messages.append(f"[UPDATE_TEMPLATES] Campo {multimidia_1} já existe")
            
            # Atualizar templates de cards
            templates = model.get("tmpls", [])
            if templates:
                new_card_template = create_card_template(is_cloze)
                template_updated = False
                
                for i, template in enumerate(templates):
                    # Lidar com diferentes formatos de template
                    if hasattr(template, 'get'):
                        old_qfmt = template.get("qfmt", "")
                        old_afmt = template.get("afmt", "")
                    elif isinstance(template, dict):
                        old_qfmt = template.get("qfmt", "")
                        old_afmt = template.get("afmt", "")
                    else:
                        old_qfmt = getattr(template, 'qfmt', "")
                        old_afmt = getattr(template, 'afmt', "")
                    
                    # Verificar se precisa atualizar (se não tem ILUSTRAÇÃO HTML no template)
                    needs_update = multimidia_1 not in old_afmt
                    
                    if needs_update:
                        # Atualizar template
                        if hasattr(template, '__setitem__'):
                            template["qfmt"] = new_card_template["qfmt"]
                            template["afmt"] = new_card_template["afmt"]
                        elif isinstance(template, dict):
                            template["qfmt"] = new_card_template["qfmt"]
                            template["afmt"] = new_card_template["afmt"]
                        else:
                            setattr(template, 'qfmt', new_card_template["qfmt"])
                            setattr(template, 'afmt', new_card_template["afmt"])
                        
                        template_updated = True
                        debug_messages.append(f"[UPDATE_TEMPLATES] Template {i+1} atualizado para {model_name}")
                    else:
                        debug_messages.append(f"[UPDATE_TEMPLATES] Template {i+1} já contém {multimidia_1}")
                
                if not template_updated:
                    debug_messages.append(f"[UPDATE_TEMPLATES] Nenhum template precisou ser atualizado para {model_name}")
            
            # Salvar o modelo atualizado
            col.models.save(model)
            updated_count += 1
            debug_messages.append(f"[UPDATE_TEMPLATES] ✅ {model_name} processado com sucesso")
            
        except Exception as e:
            debug_messages.append(f"[UPDATE_TEMPLATES] ❌ Erro ao atualizar {model.get('name', 'unknown')}: {e}")
    
    debug_messages.append(f"[UPDATE_TEMPLATES] 🎯 Total de note types processados: {updated_count}")
    return updated_count
