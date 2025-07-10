"""
Módulo Principal de Sincronização de Decks Remotos

Este módulo implementa a funcionalidade principal para sincronização de decks do Anki
com planilhas do Google Sheets em formato TSV. 

Funcionalidades principais:
- Sincronização bidirecional com Google Sheets
- Interface de seleção de decks
- Validação de URLs e dados
- Criação automática de modelos de cards
- Suporte a cards cloze e padrão
- Gerenciamento de erros robusto

Autor: Sheets2Anki Project
"""

# =============================================================================
# IMPORTS
# =============================================================================

# Imports dos módulos do projeto
from .sync import syncDecks
from .deck_manager import (
    syncDecksWithSelection, import_test_deck, 
    addNewDeck, removeRemoteDeck
)

# =============================================================================
# FUNÇÕES PRINCIPAIS EXPOSTAS
# =============================================================================

# Estas funções são os pontos de entrada principais do addon
# e são usadas pelo sistema de menus do Anki

__all__ = [
    'syncDecks',
    'syncDecksWithSelection', 
    'import_test_deck',
    'addNewDeck',
    'removeRemoteDeck'
]