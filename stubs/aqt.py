"""
Stubs para módulos do Anki (aqt) - Para desenvolvimento fora do ambiente Anki

Este arquivo simula os módulos do Anki para evitar erros de import durante desenvolvimento.
Não deve ser usado em produção - apenas para análise estática e desenvolvimento.
"""

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
        
    def isVisible(self):
        return True

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

class QInputDialog(QDialog):
    @staticmethod
    def getText(parent, title, label, echo_mode=None, text=""):
        return ("test_input", True)
        
    @staticmethod
    def getItem(parent, title, label, items, current=0, editable=False):
        return (items[0] if items else "", True)

class QLineEdit(QWidget):
    Normal = 0  # EchoMode
    EchoMode = type('EchoMode', (), {'Normal': 0})

class QProgressDialog(QDialog):
    def __init__(self, text="", cancel_button_text=None, min_val=0, max_val=100, parent=None):
        super().__init__(parent)
        self._text = text
        
    def setLabelText(self, text):
        self._text = text
        
    def setValue(self, value):
        pass
        
    def setMinimumDuration(self, ms):
        pass
        
    def setCancelButton(self, button):
        pass
        
    def setAutoClose(self, auto):
        pass
        
    def setAutoReset(self, auto):
        pass
        
    def wasCanceled(self):
        return False
        
    def findChild(self, child_type):
        if child_type == QLabel:
            return QLabel()
        return None

class QLabel(QWidget):
    def setWordWrap(self, wrap):
        pass
        
    def setAlignment(self, alignment):
        pass

class QCheckBox(QWidget):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self._checked = False
        
    def setChecked(self, checked):
        self._checked = checked
        
    def isChecked(self):
        return self._checked
        
    def stateChanged(self):
        pass

class QPushButton(QWidget):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        
    def clicked(self):
        pass
        
    def setEnabled(self, enabled):
        pass

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

class Qt:
    # Qt5 style constants
    AlignTop = 0x20
    AlignLeft = 0x1
    
    # Qt6 style constants (for compatibility)
    class AlignmentFlag:
        AlignTop = 0x20
        AlignLeft = 0x1

# =============================================================================
# MOCK ANKI COLLECTION CLASSES
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

# =============================================================================
# MOCK AQT MODULE
# =============================================================================

# Mock main window
mw = MockMainWindow()

class utils:
    @staticmethod
    def showInfo(message):
        print(f"[INFO] {message}")
        
    @staticmethod
    def qconnect(signal, slot):
        pass
        
    @staticmethod
    def tooltip(message):
        print(f"[TOOLTIP] {message}")

class qt:
    QInputDialog = QInputDialog
    QLineEdit = QLineEdit
    QDialog = QDialog
    QVBoxLayout = QVBoxLayout
    QHBoxLayout = QHBoxLayout
    QCheckBox = QCheckBox
    QPushButton = QPushButton
    QLabel = QLabel
    QProgressDialog = QProgressDialog
    Qt = Qt

class importing:
    class ImportDialog:
        def __init__(self, mw=None):
            self.mw = mw
            
        def exec(self):
            return QDialog.Accepted

# Export at module level
showInfo = utils.showInfo
qconnect = utils.qconnect
ImportDialog = importing.ImportDialog
