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
    EchoMode = type('EchoMode', (), {'Normal': 0, 'Password': 2, 'NoEcho': 1})

class QTextEdit(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._text = ""
        
    def setPlainText(self, text):
        self._text = text
        
    def toPlainText(self):
        return self._text

class QProgressDialog(QDialog):
    def __init__(self, labelText="", cancelButtonText="", minimum=0, maximum=100, parent=None):
        super().__init__(parent)
        
    def setValue(self, value):
        pass
        
    def wasCanceled(self):
        return False

class QMessageBox(QDialog):
    Information = 1
    Warning = 2
    Critical = 3
    Question = 4
    
    @staticmethod
    def information(parent, title, text):
        print(f"[INFO] {title}: {text}")
        
    @staticmethod
    def warning(parent, title, text):
        print(f"[WARNING] {title}: {text}")
        
    @staticmethod
    def critical(parent, title, text):
        print(f"[CRITICAL] {title}: {text}")

class QFrame(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

class QScrollArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def setWidget(self, widget):
        pass
        
    def setWidgetResizable(self, resizable):
        pass

class QGridLayout:
    def __init__(self):
        pass
        
    def addWidget(self, widget, row=0, col=0):
        pass

class QLabel(QWidget):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self.text = text
        
    def setText(self, text):
        self.text = text

class QComboBox(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.items = []
        
    def addItem(self, text):
        self.items.append(text)
        
    def currentText(self):
        return self.items[0] if self.items else ""

class QCheckBox(QWidget):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self.text = text
        self.checked = False
        
    def setChecked(self, checked):
        self.checked = checked
        
    def isChecked(self):
        return self.checked

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

class QApplication(QObject):
    def __init__(self, args=None):
        super().__init__()
        
    def exec_(self):
        return 0
        
    def quit(self):
        pass

class QSizePolicy:
    Expanding = 0
    Fixed = 1
    Minimum = 2
    Maximum = 3

class Qt:
    # Qt5 style constants
    AlignTop = 0x20
    AlignLeft = 0x1
    AlignCenter = 0x84
    AlignRight = 0x2
    AlignBottom = 0x40
    AlignVCenter = 0x80
    AlignHCenter = 0x4
    
    # Keys
    Key_Enter = 0x01000005
    Key_Return = 0x01000004
    Key_Escape = 0x01000000
    
    # Qt6 style constants (for compatibility)
    class AlignmentFlag:
        AlignTop = 0x20
        AlignLeft = 0x1
        AlignCenter = 0x84
        AlignRight = 0x2
        AlignBottom = 0x40
        AlignVCenter = 0x80
        AlignHCenter = 0x4
        
    class Key:
        Key_Enter = 0x01000005
        Key_Return = 0x01000004
        Key_Escape = 0x01000000


# =============================================================================
# QT UTILITIES
# =============================================================================

def qconnect(signal, slot):
    """Mock qconnect function for Qt signal/slot connections"""
    pass
