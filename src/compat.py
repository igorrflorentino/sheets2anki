"""
Módulo de Compatibilidade Qt/Anki

Este módulo fornece uma camada de compatibilidade entre diferentes versões
do Qt e Anki, garantindo que o add-on funcione nas versões 23.x, 24.x e 25.x.

Funcionalidades:
- Importação segura de módulos Qt
- Constantes de compatibilidade
- Fallbacks para versões antigas
- Detecção automática de versão
"""

import sys
from typing import Any, Optional

# =============================================================================
# DETECÇÃO DE VERSÃO DO ANKI
# =============================================================================

def get_anki_version() -> tuple[int, int, int]:
    """
    Detecta a versão do Anki em execução.
    
    Returns:
        Tuple com (major, minor, patch) da versão do Anki
    """
    try:
        import anki
        version_str = anki.version
        # Formato: "25.02.7" ou "2.1.66"
        parts = version_str.split('.')
        return (int(parts[0]), int(parts[1]), int(parts[2]) if len(parts) > 2 else 0)
    except:
        # Fallback para versão antiga
        return (2, 1, 0)

ANKI_VERSION = get_anki_version()
IS_ANKI_25_PLUS = ANKI_VERSION[0] >= 25
IS_ANKI_24_PLUS = ANKI_VERSION[0] >= 24 or (ANKI_VERSION[0] == 2 and ANKI_VERSION[1] >= 1 and ANKI_VERSION[2] >= 60)

# =============================================================================
# IMPORTS DO ANKI
# =============================================================================

try:
    from aqt import mw
    from aqt.utils import showInfo, showWarning, showCritical, tooltip
    from aqt.qt import qconnect, QAction, QMenu, QKeySequence
except ImportError as e:
    raise ImportError(f"Não foi possível importar módulos do Anki: {e}")

# Exportar qconnect para uso direto
safe_qconnect = qconnect

# =============================================================================
# IMPORTS DO QT COM COMPATIBILIDADE
# =============================================================================

try:
    from aqt.qt import (
        QApplication,
        QDialog,
        QVBoxLayout,
        QHBoxLayout,
        QGridLayout,
        QFormLayout,
        QPushButton,
        QLabel,
        QLineEdit,
        QTextEdit,
        QTextBrowser,
        QCheckBox,
        QComboBox,
        QSpinBox,
        QRadioButton,
        QButtonGroup,
        QGroupBox,
        QListWidget,
        QListWidgetItem,
        QTabWidget,
        QProgressBar,
        QProgressDialog,
        QInputDialog,
        QMessageBox,
        QFileDialog,
        QWidget,
        QFrame,
        QScrollArea,
        QSizePolicy,
        QSplitter,
        QKeySequence,
        QAction,
        QMenu,
        QFont,
        QDialogButtonBox,
        QTimer,
        QAbstractItemView,
        Qt
    )
    
    # Verificar se temos Qt6 ou Qt5
    QT_VERSION = 6 if hasattr(Qt, 'AlignmentFlag') else 5
    
except ImportError as e:
    raise ImportError(f"Não foi possível importar componentes Qt: {e}")

# =============================================================================
# CONSTANTES DE COMPATIBILIDADE
# =============================================================================

# Constantes de alinhamento
if QT_VERSION >= 6:
    # Qt6 style
    AlignTop = Qt.AlignmentFlag.AlignTop
    AlignLeft = Qt.AlignmentFlag.AlignLeft
    AlignCenter = Qt.AlignmentFlag.AlignCenter
    AlignRight = Qt.AlignmentFlag.AlignRight
    AlignBottom = Qt.AlignmentFlag.AlignBottom
    AlignVCenter = Qt.AlignmentFlag.AlignVCenter
    AlignHCenter = Qt.AlignmentFlag.AlignHCenter
else:
    # Qt5 style
    AlignTop = Qt.AlignTop
    AlignLeft = Qt.AlignLeft
    AlignCenter = Qt.AlignCenter
    AlignRight = Qt.AlignRight
    AlignBottom = Qt.AlignBottom
    AlignVCenter = Qt.AlignVCenter
    AlignHCenter = Qt.AlignHCenter

# Constantes de teclas
if QT_VERSION >= 6:
    Key_Return = Qt.Key.Key_Return
    Key_Enter = Qt.Key.Key_Enter
    Key_Escape = Qt.Key.Key_Escape
else:
    Key_Return = Qt.Key_Return
    Key_Enter = Qt.Key_Enter
    Key_Escape = Qt.Key_Escape
    
# Constantes de formato de texto
if QT_VERSION >= 6:
    TextFormat_RichText = Qt.TextFormat.RichText
    TextFormat_PlainText = Qt.TextFormat.PlainText
else:
    TextFormat_RichText = Qt.RichText
    TextFormat_PlainText = Qt.PlainText

# Constantes de orientação
if QT_VERSION >= 6:
    Horizontal = Qt.Orientation.Horizontal
    Vertical = Qt.Orientation.Vertical
else:
    Horizontal = Qt.Horizontal
    Vertical = Qt.Vertical

# Constantes de Context Menu Policy
if QT_VERSION >= 6:
    CustomContextMenu = Qt.ContextMenuPolicy.CustomContextMenu
    NoContextMenu = Qt.ContextMenuPolicy.NoContextMenu
    DefaultContextMenu = Qt.ContextMenuPolicy.DefaultContextMenu
else:
    CustomContextMenu = Qt.CustomContextMenu
    NoContextMenu = Qt.NoContextMenu
    DefaultContextMenu = Qt.DefaultContextMenu

# Constantes de diálogo
if hasattr(QDialog, 'Accepted'):
    DialogAccepted = QDialog.Accepted
    DialogRejected = QDialog.Rejected
else:
    DialogAccepted = 1
    DialogRejected = 0
    
# Constantes de QDialogButtonBox
if QT_VERSION >= 6:
    ButtonBox_Ok = QDialogButtonBox.StandardButton.Ok
    ButtonBox_Cancel = QDialogButtonBox.StandardButton.Cancel
    ButtonBox_Yes = QDialogButtonBox.StandardButton.Yes
    ButtonBox_No = QDialogButtonBox.StandardButton.No
    ButtonBox_Apply = QDialogButtonBox.StandardButton.Apply
    ButtonBox_Close = QDialogButtonBox.StandardButton.Close
else:
    ButtonBox_Ok = QDialogButtonBox.Ok
    ButtonBox_Cancel = QDialogButtonBox.Cancel
    ButtonBox_Yes = QDialogButtonBox.Yes
    ButtonBox_No = QDialogButtonBox.No
    ButtonBox_Apply = QDialogButtonBox.Apply
    ButtonBox_Close = QDialogButtonBox.Close

# Constantes de QMessageBox
if QT_VERSION >= 6:
    MessageBox_Yes = QMessageBox.StandardButton.Yes
    MessageBox_No = QMessageBox.StandardButton.No
    MessageBox_Ok = QMessageBox.StandardButton.Ok
    MessageBox_Cancel = QMessageBox.StandardButton.Cancel
    MessageBox_Information = QMessageBox.Icon.Information
    MessageBox_Warning = QMessageBox.Icon.Warning
    MessageBox_Critical = QMessageBox.Icon.Critical
    MessageBox_Question = QMessageBox.Icon.Question
else:
    MessageBox_Yes = QMessageBox.Yes
    MessageBox_No = QMessageBox.No
    MessageBox_Ok = QMessageBox.Ok
    MessageBox_Cancel = QMessageBox.Cancel
    MessageBox_Information = QMessageBox.Information
    MessageBox_Warning = QMessageBox.Warning
    MessageBox_Critical = QMessageBox.Critical
    MessageBox_Question = QMessageBox.Question

# Constantes de echo mode para QLineEdit
if hasattr(QLineEdit, 'EchoMode'):
    EchoModeNormal = QLineEdit.EchoMode.Normal
    EchoModePassword = QLineEdit.EchoMode.Password
else:
    EchoModeNormal = QLineEdit.Normal
    EchoModePassword = QLineEdit.Password

# Constantes de QAbstractItemView
if QT_VERSION >= 6:
    MultiSelection = QAbstractItemView.SelectionMode.MultiSelection
    SingleSelection = QAbstractItemView.SelectionMode.SingleSelection
    NoSelection = QAbstractItemView.SelectionMode.NoSelection
    ExtendedSelection = QAbstractItemView.SelectionMode.ExtendedSelection
    ContiguousSelection = QAbstractItemView.SelectionMode.ContiguousSelection
else:
    MultiSelection = QAbstractItemView.MultiSelection
    SingleSelection = QAbstractItemView.SingleSelection
    NoSelection = QAbstractItemView.NoSelection
    ExtendedSelection = QAbstractItemView.ExtendedSelection
    ContiguousSelection = QAbstractItemView.ContiguousSelection

# Constantes de QFrame
if QT_VERSION >= 6:
    Frame_HLine = QFrame.Shape.HLine
    Frame_VLine = QFrame.Shape.VLine
    Frame_NoFrame = QFrame.Shape.NoFrame
    Frame_Sunken = QFrame.Shadow.Sunken
    Frame_Raised = QFrame.Shadow.Raised
    Frame_Plain = QFrame.Shadow.Plain
else:
    Frame_HLine = QFrame.HLine
    Frame_VLine = QFrame.VLine
    Frame_NoFrame = QFrame.NoFrame
    Frame_Sunken = QFrame.Sunken
    Frame_Raised = QFrame.Raised
    Frame_Plain = QFrame.Plain

# Constantes de QFont
if QT_VERSION >= 6:
    try:
        Font_Bold = QFont.Weight.Bold
        Font_Normal = QFont.Weight.Normal
        Font_Light = QFont.Weight.Light
    except AttributeError:
        Font_Bold = 75
        Font_Normal = 50
        Font_Light = 25
else:
    Font_Bold = QFont.Bold
    Font_Normal = QFont.Normal
    Font_Light = QFont.Light

# =============================================================================
# FUNÇÕES DE UTILIDADE
# =============================================================================

def safe_connect(signal, slot) -> None:
    """
    Conecta signal/slot de forma segura entre versões do Qt.
    
    Args:
        signal: Signal Qt para conectar
        slot: Slot/função para conectar ao signal
    """
    try:
        if hasattr(signal, 'connect'):
            signal.connect(slot)
        else:
            qconnect(signal, slot)
    except Exception as e:
        print(f"Erro ao conectar signal/slot: {e}")

def create_button(text: str, callback=None, tooltip_text: Optional[str] = None) -> QPushButton:
    """
    Cria um botão com callback e tooltip de forma compatível.
    
    Args:
        text: Texto do botão
        callback: Função a ser chamada quando botão é clicado
        tooltip_text: Texto do tooltip (opcional)
        
    Returns:
        QPushButton configurado
    """
    button = QPushButton(text)
    
    if callback:
        safe_connect(button.clicked, callback)
    
    if tooltip_text:
        button.setToolTip(tooltip_text)
    
    return button

def show_message(title: str, message: str, message_type: str = "info") -> None:
    """
    Mostra mensagem ao usuário de forma compatível entre versões.
    
    Args:
        title: Título da mensagem
        message: Conteúdo da mensagem
        message_type: Tipo da mensagem ("info", "warning", "error")
    """
    full_message = f"{title}\n\n{message}" if title else message
    
    if message_type == "warning":
        showWarning(full_message)
    elif message_type == "error":
        showCritical(full_message)
    else:
        showInfo(full_message)
        
def safe_exec_dialog(dialog) -> int:
    """
    Executa um diálogo de forma compatível entre versões do Qt.
    
    Args:
        dialog: Diálogo Qt a ser executado
        
    Returns:
        int: Código de resultado do diálogo (Accepted/Rejected)
    """
    if hasattr(dialog, "exec"):
        # Qt6 style
        return dialog.exec()
    else:
        # Qt5 style
        return dialog.exec_()

def safe_exec_menu(menu, position) -> Any:
    """
    Executa um menu de contexto de forma compatível entre versões do Qt.
    
    Args:
        menu: QMenu a ser executado
        position: Posição onde mostrar o menu
        
    Returns:
        QAction selecionada ou None
    """
    if hasattr(menu, "exec"):
        # Qt6 style
        return menu.exec(position)
    else:
        # Qt5 style
        return menu.exec_(position)

def show_tooltip(message: str, period: int = 3000) -> None:
    """
    Mostra tooltip temporário.
    
    Args:
        message: Mensagem do tooltip
        period: Duração em milissegundos
    """
    try:
        tooltip(message)
    except:
        # Fallback para showInfo se tooltip não estiver disponível
        showInfo(message)

# =============================================================================
# EXECUÇÃO DE DIÁLOGOS (antigo fix_exec.py)
# =============================================================================

def safe_exec(dialog):
    """
    Executa um diálogo de forma compatível com diferentes versões do Qt
    
    Args:
        dialog: O diálogo a ser executado
        
    Returns:
        O resultado da execução do diálogo
    """
    try:
        # Tentar método mais novo primeiro (Qt6+)
        return dialog.exec()
    except AttributeError:
        # Fallback para versões antigas
        return dialog.exec_()

# =============================================================================
# CONSTANTES DE SELEÇÃO (antigo fix_multiselection.py)
# =============================================================================

# Constantes de QAbstractItemView com fallback
try:
    # Tentar Qt6+ primeiro (enums tipados)
    MULTI_SELECTION = QAbstractItemView.SelectionMode.MultiSelection
    SINGLE_SELECTION = QAbstractItemView.SelectionMode.SingleSelection
    NO_SELECTION = QAbstractItemView.SelectionMode.NoSelection
    EXTENDED_SELECTION = QAbstractItemView.SelectionMode.ExtendedSelection
    CONTIGUOUS_SELECTION = QAbstractItemView.SelectionMode.ContiguousSelection
except AttributeError:
    try:
        # Tentar Qt5 (constantes de classe)
        MULTI_SELECTION = QAbstractItemView.MultiSelection
        SINGLE_SELECTION = QAbstractItemView.SingleSelection
        NO_SELECTION = QAbstractItemView.NoSelection
        EXTENDED_SELECTION = QAbstractItemView.ExtendedSelection
        CONTIGUOUS_SELECTION = QAbstractItemView.ContiguousSelection
    except AttributeError:
        # Fallback para valores numéricos
        MULTI_SELECTION = 2
        SINGLE_SELECTION = 1
        NO_SELECTION = 0
        EXTENDED_SELECTION = 3
        CONTIGUOUS_SELECTION = 4

# =============================================================================
# INFORMAÇÕES DE DEBUG
# =============================================================================

def get_compatibility_info() -> dict:
    """
    Retorna informações sobre compatibilidade para debug.
    
    Returns:
        Dict com informações de versão e compatibilidade
    """
    return {
        "anki_version": ANKI_VERSION,
        "qt_version": QT_VERSION,
        "is_anki_25_plus": IS_ANKI_25_PLUS,
        "is_anki_24_plus": IS_ANKI_24_PLUS,
        "python_version": sys.version_info[:3]
    }
