"""
Stub para aqt.qt - Componentes Qt para desenvolvimento fora do Anki
"""

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
    
    def setLayout(self, layout):
        pass
    
    def setWindowTitle(self, title):
        pass
    
    def setStyleSheet(self, style):
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

class QTabWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def addTab(self, widget, title):
        pass
    
    def setCurrentIndex(self, index):
        pass

class QFrame(QWidget):
    HLine = 4
    VLine = 5
    Sunken = 2
    
    # Enum classes para Qt6+
    class Shape:
        HLine = 4
        VLine = 5
        NoFrame = 0
        Box = 1
        Panel = 2
        StyledPanel = 6
    
    class Shadow:
        Sunken = 2
        Raised = 1
        Plain = 16
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def setFrameStyle(self, style):
        pass
    
    def setFrameShape(self, shape):
        pass
    
    def setFrameShadow(self, shadow):
        pass

class QLabel(QWidget):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self.text = text
    
    def setText(self, text):
        self.text = text
    
    def setAlignment(self, alignment):
        pass
    
    def font(self):
        return QFont()
    
    def setFont(self, font):
        pass
    
    def setWordWrap(self, wrap):
        pass

class QGroupBox(QWidget):
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.title = title

class QCheckBox(QWidget):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self.text = text
        self.checked = False
    
    def isChecked(self):
        return self.checked
    
    def setChecked(self, checked):
        self.checked = checked
    
    def setEnabled(self, enabled):
        pass

class QLineEdit(QWidget):
    Normal = 0  # EchoMode
    Password = 2
    NoEcho = 1
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._text = ""
    
    def text(self):
        return self._text
    
    def setText(self, text):
        self._text = text

class QPushButton(QWidget):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self.text = text
        self.clicked = MockSignal()
    
    def setEnabled(self, enabled):
        pass

class MockSignal:
    def connect(self, slot):
        pass
    
    def disconnect(self, slot=None):
        pass
    
    def emit(self, *args):
        pass

class QAbstractItemView(QWidget):
    # Selection modes
    MultiSelection = 2
    SingleSelection = 1
    NoSelection = 0
    ExtendedSelection = 3
    ContiguousSelection = 4
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def setSelectionMode(self, mode):
        pass

class QListWidget(QAbstractItemView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.items = []
    
    def addItem(self, item):
        self.items.append(item)
    
    def selectedItems(self):
        return []
    
    def clear(self):
        self.items = []

class QListWidgetItem:
    def __init__(self, text=""):
        self.text = text
        self.data_dict = {}
    
    def setData(self, role, data):
        self.data_dict[role] = data
    
    def data(self, role):
        return self.data_dict.get(role)

class QRadioButton(QWidget):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self.text = text
        self.checked = False
    
    def isChecked(self):
        return self.checked
    
    def setChecked(self, checked):
        self.checked = checked

class QButtonGroup:
    def __init__(self):
        self.buttons = []
    
    def addButton(self, button):
        self.buttons.append(button)

class QProgressDialog(QWidget):
    def __init__(self, text="", cancel_text="", min_val=0, max_val=100, parent=None):
        super().__init__(parent)
    
    def setWindowModality(self, modality):
        pass
    
    def setValue(self, value):
        pass
    
    def close(self):
        pass

class QTextBrowser(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.text = ""
    
    def setHtml(self, html):
        self.text = html

class QFont:
    def __init__(self):
        self.point_size = 12
        self.bold = False
    
    def setBold(self, bold):
        self.bold = bold
    
    def setPointSize(self, size):
        self.point_size = size

class QVBoxLayout:
    def __init__(self, parent=None):
        self.parent = parent
        self.widgets = []
    
    def addWidget(self, widget):
        self.widgets.append(widget)
    
    def addLayout(self, layout):
        self.widgets.append(layout)
    
    def addSpacing(self, spacing):
        pass
    
    def addStretch(self):
        pass

class QHBoxLayout:
    def __init__(self, parent=None):
        self.parent = parent
        self.widgets = []
    
    def addWidget(self, widget):
        self.widgets.append(widget)
    
    def addLayout(self, layout):
        self.widgets.append(layout)
    
    def addStretch(self):
        pass

class QTextEdit(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._text = ""
        
    def setPlainText(self, text):
        self._text = text
        
    def toPlainText(self):
        return self._text

class QComboBox(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.items = []
        
    def addItem(self, text):
        self.items.append(text)
        
    def currentText(self):
        return self.items[0] if self.items else ""

class QScrollArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def setWidget(self, widget):
        pass
        
    def setWidgetResizable(self, resizable):
        pass

class QSpinBox(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
        
    def setValue(self, value):
        self.value = value
        
    def value(self):
        return self.value

class QSlider(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
        
    def setValue(self, value):
        self.value = value
        
    def value(self):
        return self.value

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

class QTimer(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def start(self, interval):
        pass
        
    def stop(self):
        pass
        
    def timeout(self):
        pass

class QSplitter(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def addWidget(self, widget):
        pass

class QSizePolicy:
    Expanding = 7
    Preferred = 5
    Fixed = 0
    
    def __init__(self, horizontal=None, vertical=None):
        pass

class QTreeWidget(QAbstractItemView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.items = []
    
    def addTopLevelItem(self, item):
        self.items.append(item)

class QTreeWidgetItem:
    def __init__(self, text_list=None):
        self.text_list = text_list or []

class QProgressBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
        
    def setValue(self, value):
        self.value = value
        
    def value(self):
        return self.value

class QStatusBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def showMessage(self, message):
        print(f"[STATUS] {message}")

class QMainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def setCentralWidget(self, widget):
        pass
        
    def statusBar(self):
        return QStatusBar()

class QInputDialog(QDialog):
    @staticmethod
    def getText(parent, title, label, echo_mode=None, text=""):
        return ("test_input", True)
        
    @staticmethod
    def getItem(parent, title, label, items, current=0, editable=False):
        return (items[0] if items else "", True)

class QGridLayout:
    def __init__(self, parent=None):
        self.parent = parent
        self.widgets = []
    
    def addWidget(self, widget, row=0, col=0):
        self.widgets.append((widget, row, col))

class QFormLayout:
    def __init__(self, parent=None):
        self.parent = parent
        self.widgets = []
    
    def addRow(self, label, widget=None):
        self.widgets.append((label, widget))

class Qt:
    # Compatibilidade com diferentes versões
    UserRole = 256
    WindowModal = 1
    AlignCenter = 0x0004
    
    # Versões novas
    class ItemDataRole:
        UserRole = 256
    
    class WindowModality:
        WindowModal = 1
    
    class AlignmentFlag:
        AlignCenter = 0x0004
        AlignTop = 0x0020
        AlignLeft = 0x0001
        AlignRight = 0x0002
        AlignBottom = 0x0040
        AlignVCenter = 0x0080
        AlignHCenter = 0x0004
    
    class Key:
        Key_Return = 0x01000004
        Key_Enter = 0x01000005
        Key_Escape = 0x01000000

class QAction:
    def __init__(self, text="", parent=None):
        self.text = text
        self.parent = parent
    
    def triggered(self):
        pass

class QMenu:
    def __init__(self, parent=None):
        self.parent = parent
    
    def addAction(self, action):
        pass

class QKeySequence:
    def __init__(self, key=""):
        self.key = key

def qconnect(signal, slot):
    """Conecta signal ao slot"""
    pass

class QApplication:
    def __init__(self, args=None):
        pass
        
    def exec(self):
        pass
        
    def exec_(self):
        pass
        
    @staticmethod
    def instance():
        return QApplication()