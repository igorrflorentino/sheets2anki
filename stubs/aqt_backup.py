"""
Stubs para módulos do Anki (aqt) - Para desenvolvimento fora do ambiente Anki

Este arquivo simula os módulos do Anki para evitar erros de import durante desenvolvimento.
Não deve ser usado em produção - apenas para análise estática e desenvolvimento.
"""

# =============================================================================
# MOCK ANKI MODULES
# =============================================================================

# Mock para anki modules
class Collection:
    def __init__(self):
        self.decks = MockDeckManager()
        self.models = MockModelManager()
    
    def find_cards(self, query):
        """Find cards by query"""
        return []
        
    def findNotes(self, query):
        return []
    
    def getNote(self, note_id):
        return MockNote()
        
    def get_note(self, note_id):
        """Get note by ID (newer API)"""
        return MockNote()
        
    def add_note(self, note, deck_id):
        """Add note to collection"""
        return 1
        
    def remove_notes(self, note_ids):
        """Remove notes by IDs"""
        pass
        
    def save(self):
        """Save collection"""
        pass
        
    def new_note(self, model):
        """Create new note with model"""
        return MockNote()

class MockDeckManager:
    def allNames(self):
        return []
    
    def byName(self, name):
        return None
        
    def get(self, deck_id):
        """Get deck by ID"""
        return {"id": deck_id, "name": "Test Deck"}
        
    def by_name(self, name):
        """Get deck by name"""  
        return {"id": 1, "name": name} if name else None
        
    def id(self, name):
        """Get or create deck ID"""
        return 1

class MockNote:
    def __init__(self):
        self.fields = []
        self.tags = []
    
    def flush(self):
        pass

# Mock main window
class MockAddonManager:
    """Mock addon manager"""
    
    def getConfig(self, addon_name):
        """Get addon config"""
        return {"remote-decks": {}}
        
    def writeConfig(self, addon_name, config):
        """Write addon config"""
        pass

class MockApp:
    """Mock QApplication"""
    
    def processEvents(self):
        """Process pending events"""
        pass

class MockMainWindow:
    def __init__(self):
        self.col = Collection()
        self.addonManager = MockAddonManager()
        self.app = MockApp()
    
    def moveToState(self, state):
        pass
    
    def requireReset(self, modal=False):
        pass

# Global mw instance
mw = MockMainWindow()

# =============================================================================
# MOCK QT CLASSES
# =============================================================================

class QObject:
    def __init__(self, parent=None):
        self.parent = parent

class QWidget(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def show(self):
        pass
        
    def hide(self):
        pass
        
    def setMinimumSize(self, width, height):
        pass
        
    def setFixedWidth(self, width):
        pass
        
    def setMinimumHeight(self, height):
        pass
        
    def setMaximumHeight(self, height):
        pass

class QDialog(QWidget):
    Accepted = 1
    Rejected = 0
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def exec(self):
        return self.Accepted
        
    def exec_(self):
        return self.Accepted
        
    def accept(self):
        pass
        
    def reject(self):
        pass
        
    def setWindowTitle(self, title):
        pass

class QProgressDialog(QDialog):
    def __init__(self, text="", cancel_button=None, minimum=0, maximum=100, parent=None):
        super().__init__(parent)
        self.text = text
        self.minimum = minimum
        self.maximum = maximum
        self.value = 0
        self.visible = False
        
    def setValue(self, value):
        self.value = value
        
    def setLabelText(self, text):
        self.text = text
        
    def setMinimumDuration(self, duration):
        pass
        
    def setCancelButton(self, button):
        pass
        
    def setAutoClose(self, auto_close):
        pass
        
    def setAutoReset(self, auto_reset):
        pass
        
    def isVisible(self):
        return self.visible
        
    def close(self):
        self.visible = False
        
    def wasCanceled(self):
        return False
        
    def findChild(self, class_type):
        if class_type == QLabel:
            return QLabel()
        return None

class QLabel(QWidget):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self.text = text
        
    def setText(self, text):
        self.text = text
        
    def setWordWrap(self, wrap):
        pass
        
    def setAlignment(self, alignment):
        pass
        
    def setStyleSheet(self, style):
        pass

class QPushButton(QWidget):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self.text = text
        self.clicked = MockSignal()
        
    def setEnabled(self, enabled):
        pass

class QCheckBox(QWidget):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self.text = text
        self.checked = False
        self.stateChanged = MockSignal()
        
    def setChecked(self, checked):
        self.checked = checked
        
    def isChecked(self):
        return self.checked

class QInputDialog:
    @staticmethod
    def getText(parent, title, label, echo_mode=None, text=""):
        return ("mock_input", True)
        
    @staticmethod
    def getItem(parent, title, label, items, current=0, editable=False):
        return (items[0] if items else "mock_item", True)

class QLineEdit(QWidget):
    Normal = 0
    
    class EchoMode:
        Normal = 0

class QVBoxLayout:
    def __init__(self):
        pass
        
    def addWidget(self, widget):
        pass
        
    def addLayout(self, layout):
        pass
        
    def addSpacing(self, spacing):
        pass

class QHBoxLayout:
    def __init__(self):
        pass
        
    def addWidget(self, widget):
        pass

class QAction:
    def __init__(self, text, parent=None):
        self.text = text
        self.parent = parent
        self.triggered = MockSignal()
        
    def setShortcut(self, shortcut):
        pass

class QMenu:
    def __init__(self, text, parent=None):
        self.text = text
        self.parent = parent
        
    def addAction(self, action):
        pass
        
    def addMenu(self, menu):
        pass

class QKeySequence:
    def __init__(self, key):
        self.key = key

class Qt:
    AlignTop = 0x20
    AlignLeft = 0x1

class MockSignal:
    def connect(self, slot):
        pass
        
    def emit(self, *args):
        pass

# =============================================================================
# MOCK ANKI CLASSES
# =============================================================================

class MockDecks:
    def get(self, deck_id):
        return {"id": deck_id, "name": "Test Deck"}
        
    def by_name(self, name):
        return {"id": 1, "name": name} if name else None
        
    def id(self, name):
        return 1

class MockCollection:
    def __init__(self):
        self.decks = MockDecks()
        self.models = MockModelManager()
        
    def find_notes(self, query):
        return []
        
    def find_cards(self, query):
        return []
        
    def get_note(self, nid):
        return MockNote()
        
    def new_note(self, model):
        return MockNote()
        
    def add_note(self, note, deck_id):
        pass
        
    def remove_notes(self, note_ids):
        pass
        
    def save(self):
        pass

class MockDecks:
    def by_name(self, name):
        return {"id": 1, "name": name}
        
    def get(self, deck_id):
        return {"id": deck_id, "name": "Mock Deck"}
        
    def id(self, name):
        return 1

class MockModelManager:
    """Mock model/note type manager"""
    
    def by_name(self, name):
        """Get model by name"""
        return {"id": 1, "name": name} if name else None
        
    def new(self, name):
        """Create new model"""
        return {
            "id": 1,
            "name": name,
            "type": 0,
            "did": 1,
            "flds": [],
            "tmpls": []
        }
        
    def new_field(self, name):
        """Create new field"""
        return {"name": name, "ord": 0}
        
    def add_field(self, model, field):
        """Add field to model"""
        model["flds"].append(field)
        
    def new_template(self, name):
        """Create new template"""
        return {"name": name, "ord": 0}
        
    def add_template(self, model, template):
        """Add template to model"""
        model["tmpls"].append(template)
        
    def save(self, model):
        """Save model"""
        pass
        
    def set_current(self, model):
        """Set current model"""
        pass

# =============================================================================
# MOCK AQT MODULE
# =============================================================================

# Mock main window
mw = MockMainWindow()

class utils:
    @staticmethod
    def showInfo(message):
        print(f"[Anki Info] {message}")
        
    @staticmethod
    def qconnect(signal, slot):
        pass

class qt:
    QAction = QAction
    QMenu = QMenu
    QInputDialog = QInputDialog
    QLineEdit = QLineEdit
    QKeySequence = QKeySequence
    QDialog = QDialog
    QVBoxLayout = QVBoxLayout
    QHBoxLayout = QHBoxLayout
    QCheckBox = QCheckBox
    QPushButton = QPushButton
    QLabel = QLabel
    QProgressDialog = QProgressDialog
    Qt = Qt

class importing:
    """Mock importing module"""
    
    class ImportDialog:
        def __init__(self, mw=None):
            self.mw = mw
            
        def exec(self):
            return QDialog.Accepted

# Export at module level for direct imports
showInfo = utils.showInfo
qconnect = utils.qconnect
ImportDialog = importing.ImportDialog
