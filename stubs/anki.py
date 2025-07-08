"""
Stubs para módulos do Anki (anki) - Para desenvolvimento fora do ambiente Anki

Este arquivo simula os módulos core do Anki para evitar erros de import durante desenvolvimento.
Não deve ser usado em produção - apenas para análise estática e desenvolvimento.
"""

# =============================================================================
# MOCK ANKI CORE MODULES  
# =============================================================================

class Collection:
    """Mock Collection class"""
    
    def __init__(self):
        self._decks = MockDeckManager()
        self._models = MockModelManager()
        
    def decks(self):
        return self._decks
    
    def models(self):
        return self._models
        
    def findNotes(self, query):
        """Find notes by query"""
        return []
    
    def getNote(self, note_id):
        """Get note by ID"""
        return MockNote()
        
    def addNote(self, note):
        """Add note to collection"""
        return 1
        
    def flush(self):
        """Flush changes"""
        pass

class MockDeckManager:
    """Mock deck manager"""
    
    def allNames(self):
        """Get all deck names"""
        return ["Default"]
    
    def byName(self, name):
        """Get deck by name"""
        return {"id": 1, "name": name} if name else None
        
    def id(self, name):
        """Get deck ID by name"""
        return 1

class MockModelManager:
    """Mock model/note type manager"""
    
    def byName(self, name):
        """Get model by name"""
        return {"id": 1, "name": name} if name else None
        
    def fieldNames(self, model):
        """Get field names for model"""
        return ["Front", "Back"]

class MockNote:
    """Mock Note class"""
    
    def __init__(self):
        self.tags = []
        self.fields = ["", ""]  # List of field values
        self.mid = 1  # Model ID
        
    def __contains__(self, key):
        return True
        
    def __getitem__(self, key):
        if isinstance(key, int):
            return self.fields[key] if key < len(self.fields) else ""
        return ""
        
    def __setitem__(self, key, value):
        if isinstance(key, int) and key < len(self.fields):
            self.fields[key] = value
        
    def flush(self):
        """Save changes"""
        pass

# =============================================================================
# MOCK STATES AND CONSTANTS
# =============================================================================

class States:
    """Mock states"""
    DECKBROWSER = "deckBrowser"
    OVERVIEW = "overview" 
    REVIEW = "review"

# Export commonly used classes
states = States()
