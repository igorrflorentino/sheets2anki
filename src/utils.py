"""
Funções utilitárias para o addon Sheets2Anki.

Este módulo contém funções auxiliares utilizadas em
diferentes partes do projeto.
"""

import hashlib
from . import column_definitions

def get_or_create_deck(col, deckName):
    """
    Cria ou obtém um deck existente no Anki.
    
    Args:
        col: Collection do Anki
        deckName: Nome do deck
        
    Returns:
        tuple: (deck_id, actual_name) onde deck_id é o ID do deck e actual_name é o nome real usado
        
    Raises:
        ValueError: Se o nome do deck for inválido
    """
    if not deckName or not isinstance(deckName, str) or deckName.strip() == "" or deckName.strip().lower() == "default":
        raise ValueError("Nome de deck inválido ou proibido para sincronização: '%s'" % deckName)
    
    deck = col.decks.by_name(deckName)
    if deck is None:
        try:
            deck_id = col.decks.id(deckName)
            # Obter o deck recém-criado para verificar o nome real usado
            new_deck = col.decks.get(deck_id)
            actual_name = new_deck["name"] if new_deck else deckName
        except Exception as e:
            raise ValueError(f"Não foi possível criar o deck '{deckName}': {str(e)}")
    else:
        deck_id = deck["id"]
        actual_name = deck["name"]
    return deck_id, actual_name

def get_model_suffix_from_url(url):
    """
    Gera um sufixo único e curto baseado na URL.
    
    Args:
        url: URL do deck remoto
        
    Returns:
        str: Sufixo de 8 caracteres baseado no hash SHA1 da URL
    """
    return hashlib.sha1(url.encode()).hexdigest()[:8]

def get_note_key(note):
    """
    Obtém a chave do campo de uma nota baseado no seu tipo.
    
    Args:
        note: Nota do Anki
        
    Returns:
        str: Valor da chave ou None se não encontrada
    """
    if "Text" in note:
        return note["Text"]
    elif "Front" in note:
        return note["Front"]
    return None
