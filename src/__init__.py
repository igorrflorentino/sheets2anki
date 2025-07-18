"""
Sheets2Anki - Add-on para sincronizar decks do Anki com planilhas do Google Sheets
"""

# Importar módulos de compatibilidade para garantir que estejam disponíveis
from . import fix_multiselection
from .fix_exec import safe_exec