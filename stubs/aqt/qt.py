"""
Stub para aqt.qt - Componentes Qt para desenvolvimento fora do Anki
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
        
    def setWindowTitle(self, title):
        pass
        
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

class QAction(QObject):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self.text = text
        
    def triggered(self):
        pass
        
    def setShortcut(self, shortcut):
        pass

class QMenu(QWidget):
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        
    def addAction(self, action):
        pass
        
    def addSeparator(self):
        pass

class QKeySequence:
    def __init__(self, sequence=""):
        self.sequence = sequence

class Qt:
    # Qt5 style constants
    AlignTop = 0x20
    AlignLeft = 0x1
    
    # Qt6 style constants (for compatibility)
    class AlignmentFlag:
        AlignTop = 0x20
        AlignLeft = 0x1
