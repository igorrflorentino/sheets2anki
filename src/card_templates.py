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
        (column_definitions.CARREIRA, column_definitions.CARREIRA),
        (column_definitions.IMPORTANCIA, column_definitions.IMPORTANCIA),
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
    
    # Registrar automaticamente o note type se URL foi fornecida
    if url and model.get('id'):
        try:
            register_note_type_for_deck(url, model['id'], model_name, debug_messages)
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
    from .utils import get_note_type_name, register_note_type_for_deck
    from .config_manager import get_deck_remote_name, get_deck_note_type_ids
    
    def add_debug_msg(message):
        if debug_messages:
            debug_messages.append(f"[ENSURE_MODELS] {message}")
        print(f"[ENSURE_MODELS] {message}")
    
    models = {}
    
    # Obter nome do deck remoto e note types existentes
    remote_deck_name = get_deck_remote_name(url) or "RemoteDeck"
    existing_note_types = get_deck_note_type_ids(url) or {}
    
    add_debug_msg(f"Procurando note types para student='{student}', remote_deck_name='{remote_deck_name}'")
    add_debug_msg(f"Note types existentes: {len(existing_note_types)} encontrados")
    
    # Função helper para encontrar note type por padrão
    def find_existing_note_type(is_cloze):
        target_type = "Cloze" if is_cloze else "Basic"
        target_pattern = f" - {student} - {target_type}" if student else f" - {target_type}"
        
        # Procurar nos note types existentes
        for note_type_id_str, note_type_name in existing_note_types.items():
            if note_type_name.endswith(target_pattern):
                try:
                    note_type_id = int(note_type_id_str)
                    model = col.models.get(note_type_id)
                    if model:
                        add_debug_msg(f"Encontrado note type existente: ID {note_type_id} - '{note_type_name}'")
                        return model, note_type_name
                except (ValueError, TypeError):
                    continue
        return None, None
    
    # Modelo padrão (Basic)
    expected_name = get_note_type_name(url, remote_deck_name, student=student, is_cloze=False)
    existing_model, existing_name = find_existing_note_type(is_cloze=False)
    
    if existing_model:
        # Use o modelo existente e NÃO force um nome novo se já está registrado
        current_registered_name = None
        for note_type_id_str, note_type_name in existing_note_types.items():
            try:
                if int(note_type_id_str) == existing_model['id']:
                    current_registered_name = note_type_name
                    break
            except ValueError:
                continue
        
        if current_registered_name:
            # Já está registrado, usar nome atual da configuração
            add_debug_msg(f"Usando modelo existente (Basic) JÁ REGISTRADO: '{existing_name}' com nome config: '{current_registered_name}'")
            models['standard'] = existing_model
        else:
            # Não está registrado, registrar com nome esperado
            register_note_type_for_deck(url, existing_model['id'], expected_name, debug_messages)
            models['standard'] = existing_model
            add_debug_msg(f"Modelo existente (Basic) registrado: '{existing_name}' → esperado: '{expected_name}'")
    else:
        # Criar novo modelo apenas se realmente não existir
        add_debug_msg(f"Criando novo modelo (Basic): '{expected_name}'")
        model = create_model(col, expected_name, is_cloze=False, url=url, debug_messages=debug_messages)
        models['standard'] = model
    
    # Modelo cloze
    expected_cloze_name = get_note_type_name(url, remote_deck_name, student=student, is_cloze=True)
    existing_cloze_model, existing_cloze_name = find_existing_note_type(is_cloze=True)
    
    if existing_cloze_model:
        # Use o modelo existente e NÃO force um nome novo se já está registrado
        current_registered_cloze_name = None
        for note_type_id_str, note_type_name in existing_note_types.items():
            try:
                if int(note_type_id_str) == existing_cloze_model['id']:
                    current_registered_cloze_name = note_type_name
                    break
            except ValueError:
                continue
        
        if current_registered_cloze_name:
            # Já está registrado, usar nome atual da configuração
            add_debug_msg(f"Usando modelo existente (Cloze) JÁ REGISTRADO: '{existing_cloze_name}' com nome config: '{current_registered_cloze_name}'")
            models['cloze'] = existing_cloze_model
        else:
            # Não está registrado, registrar com nome esperado
            register_note_type_for_deck(url, existing_cloze_model['id'], expected_cloze_name, debug_messages)
            models['cloze'] = existing_cloze_model
            add_debug_msg(f"Modelo existente (Cloze) registrado: '{existing_cloze_name}' → esperado: '{expected_cloze_name}'")
    else:
        # Criar novo modelo apenas se realmente não existir
        add_debug_msg(f"Criando novo modelo (Cloze): '{expected_cloze_name}'")
        cloze_model = create_model(col, expected_cloze_name, is_cloze=True, url=url, debug_messages=debug_messages)
        models['cloze'] = cloze_model
    
    return models
