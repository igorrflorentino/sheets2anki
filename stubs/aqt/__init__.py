"""
Stub package para aqt - Anki Qt interface
"""

from unittest.mock import MagicMock

# =============================================================================
# MOCK CLASSES (duplicadas aqui para evitar imports circulares)
# =============================================================================

class MockNote:
    def __init__(self):
        self.tags = []
        self.fields = {}
        
    def __contains__(self, key):
        return key in self.fields
        
    def __getitem__(self, key):
        return self.fields.get(key, "")
        
    def __setitem__(self, key, value):
        self.fields[key] = value
        
    def flush(self):
        pass

class MockDeckManager:
    def by_name(self, name):
        return {"id": 1, "name": name} if name else None
        
    def get(self, deck_id):
        return {"id": deck_id, "name": "Test Deck"}
        
    def id(self, name):
        return 1

class MockModelManager:
    def by_name(self, name):
        return {"id": 1, "name": name} if name else None
        
    def new(self, name):
        return {
            "id": 1,
            "name": name,
            "type": 0,
            "did": 1,
            "flds": [],
            "tmpls": []
        }
        
    def new_field(self, name):
        return {"name": name, "ord": 0}
        
    def add_field(self, model, field):
        model["flds"].append(field)
        
    def new_template(self, name):
        return {"name": name, "ord": 0}
        
    def add_template(self, model, template):
        model["tmpls"].append(template)
        
    def save(self, model):
        pass
        
    def set_current(self, model):
        pass

class Collection:
    def __init__(self):
        self.decks = MockDeckManager()
        self.models = MockModelManager()
    
    def find_cards(self, query):
        return []
        
    def findNotes(self, query):
        return []
    
    def getNote(self, note_id):
        return MockNote()
        
    def get_note(self, note_id):
        return MockNote()
        
    def add_note(self, note, deck_id):
        return 1
        
    def remove_notes(self, note_ids):
        pass
        
    def save(self):
        pass
        
    def new_note(self, model):
        return MockNote()

class MockAddonManager:
    def getConfig(self, addon_name):
        return {"remote-decks": {}}
        
    def writeConfig(self, addon_name, config):
        pass

class MockApp:
    def processEvents(self):
        pass

class MockMainWindow:
    def __init__(self):
        self.col = Collection()
        self.addonManager = MockAddonManager()
        self.app = MockApp()
        self.form = MagicMock()  # Adicionar form como mock

# =============================================================================
# MAIN EXPORTS
# =============================================================================

# Criar instância do mock main window
mw = MockMainWindow()

# Importar submódulos
from . import utils
from . import qt  
from . import importing

# Funções de conveniência
showInfo = utils.showInfo
qconnect = utils.qconnect
ImportDialog = importing.ImportDialog

__all__ = [
    'mw', 'utils', 'qt', 'importing',
    'showInfo', 'qconnect', 'ImportDialog'
]
