"""
Templates e modelos de cards para o addon Sheets2Anki.

Este módulo contém funções para criar templates de cards
e modelos de notas no Anki.
"""

from .constants import CARD_SHOW_ALLWAYS_TEMPLATE, CARD_SHOW_HIDE_TEMPLATE
from .utils import get_model_suffix_from_url
from . import column_definitions

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
        (column_definitions.TOPICO, column_definitions.TOPICO),
        (column_definitions.SUBTOPICO, column_definitions.SUBTOPICO),
        (column_definitions.CONCEITO, column_definitions.CONCEITO),
    ]
    
    # Construir seção de cabeçalho
    header = ""
    for field_name, field_value in header_fields:
        header += CARD_SHOW_ALLWAYS_TEMPLATE.format(
            field_name=field_name.capitalize(),
            field_value=field_value
        )
    
    # Formato da pergunta
    question = (
        "<hr><br>"
        f"<b>{column_definitions.PERGUNTA.capitalize()}:</b><br>"
        f"{{{{{'cloze:' if is_cloze else ''}{column_definitions.PERGUNTA}}}}}"
    )

    # Formato da resposta
    match = (
        "<br><br>"
        f"<b>{column_definitions.MATCH.capitalize()}:</b><br>"
        f"{{{{{'cloze:' if is_cloze else ''}{column_definitions.MATCH}}}}}"
        "<br><br><hr><br>"
    )

    # Campos de informação extra
    extra_info_fields = [
        column_definitions.EXTRA_INFO_1,
        column_definitions.EXTRA_INFO_2
    ]
    
    extra_info = ""
    for field in extra_info_fields:
        extra_info += CARD_SHOW_HIDE_TEMPLATE.format(
            field_name=field.capitalize(),
            field_value=field
        )
    
    # Campos de exemplo
    example_fields = [
        column_definitions.EXEMPLO_1,
        column_definitions.EXEMPLO_2,
        column_definitions.EXEMPLO_3
    ]
    
    examples = ""
    for field in example_fields:
        examples += CARD_SHOW_HIDE_TEMPLATE.format(
            field_name=field.capitalize(),
            field_value=field
        )

    # Campos de rodapé
    footer_fields = [
        (column_definitions.BANCAS, column_definitions.BANCAS),
        (column_definitions.ANO, column_definitions.ANO),
        (column_definitions.MORE_TAGS, column_definitions.MORE_TAGS)
    ]

    # Construir seção de rodapé
    footer = ""
    for field_name, field_value in footer_fields:
        footer += CARD_SHOW_HIDE_TEMPLATE.format(
            field_name=field_name.capitalize(),
            field_value=field_value
        )
    
    # Construir templates completos
    qfmt = header + question
    afmt = (header + 
            question + 
            match + 
            extra_info + 
            examples + 
            "<hr><br>" + 
            footer) if is_cloze else ("{{FrontSide}}" + 
                                      match + 
                                      extra_info + 
                                      examples + 
                                      "<hr><br>" + 
                                      footer)

    return {'qfmt': qfmt, 'afmt': afmt}

def create_model(col, model_name, is_cloze=False):
    """
    Cria um novo modelo de nota do Anki.
    
    Args:
        col: Objeto de coleção do Anki
        model_name (str): Nome para o novo modelo
        is_cloze (bool): Se deve criar um modelo de cloze
        
    Returns:
        object: O modelo do Anki criado
    """
    model = col.models.new(model_name)
    if is_cloze:
        model['type'] = 1  # Definir como tipo cloze
    
    # Adicionar campos (excluindo campos de controle interno como SYNC?)
    for field in column_definitions.NOTE_FIELDS:
        template = col.models.new_field(field)
        col.models.add_field(model, template)
    
    # Adicionar template de card
    template = col.models.new_template("Cloze" if is_cloze else "Card 1")
    card_template = create_card_template(is_cloze)
    template['qfmt'] = card_template['qfmt']
    template['afmt'] = card_template['afmt']
    
    col.models.add_template(model, template)
    col.models.save(model)
    return model

def ensure_custom_models(col, url):
    """
    Garante que ambos os modelos (padrão e cloze) existam no Anki.
    
    Args:
        col: Objeto de coleção do Anki
        url (str): URL do deck remoto
        
    Returns:
        dict: Dicionário contendo os modelos 'standard' e 'cloze'
    """
    models = {}
    suffix = get_model_suffix_from_url(url)
    
    # Modelo padrão
    model_name = f"CadernoErrosConcurso_{suffix}_Basic"
    model = col.models.by_name(model_name)
    if model is None:
        model = create_model(col, model_name)
    models['standard'] = model
    
    # Modelo cloze
    cloze_model_name = f"CadernoErrosConcurso_{suffix}_Cloze"
    cloze_model = col.models.by_name(cloze_model_name)
    if cloze_model is None:
        cloze_model = create_model(col, cloze_model_name, is_cloze=True)
    models['cloze'] = cloze_model
    
    return models
