"""
Gerenciamento de subdecks para o addon Sheets2Anki.

Este módulo contém funções para criar e gerenciar subdecks
baseados nos valores das colunas IMPORTANCIA, TOPICO, SUBTOPICO e CONCEITO.
"""

try:
    from .compat import mw
except ImportError:
    # Fallback para importação direta
    from aqt import mw

from . import column_definitions as cols
from .config_manager import get_create_subdecks_setting, get_remote_decks
from .constants import DEFAULT_IMPORTANCE, DEFAULT_TOPIC, DEFAULT_SUBTOPIC, DEFAULT_CONCEPT

def get_subdeck_name(main_deck_name, fields):
    """
    Gera o nome do subdeck baseado no deck principal e nos campos IMPORTANCIA, TOPICO, SUBTOPICO e CONCEITO.
    
    Args:
        main_deck_name (str): Nome do deck principal
        fields (dict): Campos da nota com IMPORTANCIA, TOPICO, SUBTOPICO e CONCEITO
        
    Returns:
        str: Nome completo do subdeck no formato "DeckPrincipal::Importancia::Topico::Subtopico::Conceito"
    """
    # Verificar se a criação de subdecks está habilitada
    if not get_create_subdecks_setting():
        return main_deck_name
    
    # Obter valores dos campos, usando valores padrão se estiverem vazios
    importancia = fields.get(cols.IMPORTANCIA, "").strip() or DEFAULT_IMPORTANCE
    topico = fields.get(cols.TOPICO, "").strip() or DEFAULT_TOPIC
    subtopico = fields.get(cols.SUBTOPICO, "").strip() or DEFAULT_SUBTOPIC
    conceito = fields.get(cols.CONCEITO, "").strip() or DEFAULT_CONCEPT
    
    # Criar hierarquia completa de subdecks incluindo importância, tópico, subtópico e conceito
    return f"{main_deck_name}::{importancia}::{topico}::{subtopico}::{conceito}"

def ensure_subdeck_exists(deck_name):
    """
    Garante que um subdeck existe, criando-o se necessário.
    
    Esta função suporta nomes hierárquicos como "Deck::Subdeck::Subsubdeck".
    
    Args:
        deck_name (str): Nome completo do deck/subdeck
        
    Returns:
        int: ID do deck/subdeck
        
    Raises:
        RuntimeError: Se mw não estiver disponível
    """
    if not mw or not hasattr(mw, 'col') or not mw.col:
        raise RuntimeError("Anki main window (mw) não está disponível")
        
    # Verificar se o deck já existe
    did = mw.col.decks.id_for_name(deck_name)
    if did is not None:
        return did
    
    # Se não existe, criar o deck e todos os decks pai necessários
    return mw.col.decks.id(deck_name)

def move_note_to_subdeck(note_id, subdeck_id):
    """
    Move uma nota para um subdeck específico.
    
    Args:
        note_id (int): ID da nota a ser movida
        subdeck_id (int): ID do subdeck de destino
        
    Returns:
        bool: True se a operação foi bem-sucedida, False caso contrário
        
    Raises:
        RuntimeError: Se mw não estiver disponível
    """
    if not mw or not hasattr(mw, 'col') or not mw.col:
        raise RuntimeError("Anki main window (mw) não está disponível")
        
    try:
        # Obter a nota
        note = mw.col.get_note(note_id)
        
        # Obter todos os cards da nota
        card_ids = mw.col.find_cards(f"nid:{note_id}")
        
        # Mover cada card para o subdeck
        for card_id in card_ids:
            card = mw.col.get_card(card_id)
            card.did = subdeck_id
            card.flush()
        
        return True
    except Exception as e:
        print(f"Erro ao mover nota para subdeck: {e}")
        return False


def remove_empty_subdecks(remote_decks):
    """
    Remove subdecks vazios após a sincronização.
    
    Esta função verifica todos os subdecks dos decks remotos e remove aqueles
    que não contêm nenhuma nota ou card.
    
    Args:
        remote_decks (dict): Dicionário de decks remotos
        
    Returns:
        int: Número de subdecks vazios removidos
    """
    if not mw or not hasattr(mw, 'col') or not mw.col:
        return 0
        
    removed_count = 0
    processed_decks = set()
    
    # Coletar todos os decks principais para verificar seus subdecks
    main_deck_ids = []
    for deck_info in remote_decks.values():
        deck_id = deck_info.get("deck_id")
        if deck_id and deck_id not in processed_decks:
            main_deck_ids.append(deck_id)
            processed_decks.add(deck_id)
    
    # Para cada deck principal, verificar seus subdecks
    for deck_id in main_deck_ids:
        deck = mw.col.decks.get(deck_id)
        if not deck:
            continue
            
        main_deck_name = deck["name"]
        
        # Encontrar todos os subdecks deste deck principal
        all_decks = mw.col.decks.all_names_and_ids()
        subdecks = [d for d in all_decks if d.name.startswith(main_deck_name + "::")] 
        
        # Ordenar subdecks do mais profundo para o menos profundo para evitar problemas de dependência
        subdecks.sort(key=lambda d: d.name.count("::"), reverse=True)
        
        # Verificar cada subdeck
        for subdeck in subdecks:
            # Contar cards no subdeck
            card_count = len(mw.col.find_cards(f'deck:"{subdeck.name}"'))
            
            # Se o subdeck estiver vazio, removê-lo
            if card_count == 0:
                try:
                    mw.col.decks.remove([subdeck.id])
                    removed_count += 1
                except Exception as e:
                    # Ignorar erros na remoção de subdecks
                    pass
    
    # Atualizar a interface do Anki para refletir as mudanças
    if removed_count > 0 and mw is not None and hasattr(mw, 'reset'):
        mw.reset()
    
    return removed_count