"""
Qt/Anki Compatibility Module

This module provides clean imports and constants for Anki 25.x+ with Qt6.
All backward compatibility code has been removed.
"""

from typing import Any, Optional

# =============================================================================
# ANKI IMPORTS
# =============================================================================

from aqt import mw
from aqt.qt import (
    QAbstractItemView,
    QAction,
    QApplication,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFont,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QKeySequence,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QPalette,
    QProgressBar,
    QProgressDialog,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSize,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    Qt,
    QTabWidget,
    QTextBrowser,
    QTextEdit,
    QTimer,
    QVBoxLayout,
    QWidget,
    qconnect,
)
from aqt.utils import showCritical, showInfo, showWarning, tooltip

# Export qconnect for direct use
safe_qconnect = qconnect

# =============================================================================
# QT6 CONSTANTS
# =============================================================================

# Alignment constants
AlignTop = Qt.AlignmentFlag.AlignTop
AlignLeft = Qt.AlignmentFlag.AlignLeft
AlignCenter = Qt.AlignmentFlag.AlignCenter
AlignRight = Qt.AlignmentFlag.AlignRight
AlignBottom = Qt.AlignmentFlag.AlignBottom
AlignVCenter = Qt.AlignmentFlag.AlignVCenter
AlignHCenter = Qt.AlignmentFlag.AlignHCenter

# Key constants
Key_Return = Qt.Key.Key_Return
Key_Enter = Qt.Key.Key_Enter
Key_Escape = Qt.Key.Key_Escape

# Text format constants
TextFormat_RichText = Qt.TextFormat.RichText
TextFormat_PlainText = Qt.TextFormat.PlainText

# Orientation constants
Horizontal = Qt.Orientation.Horizontal
Vertical = Qt.Orientation.Vertical

# Context Menu Policy constants
CustomContextMenu = Qt.ContextMenuPolicy.CustomContextMenu
NoContextMenu = Qt.ContextMenuPolicy.NoContextMenu
DefaultContextMenu = Qt.ContextMenuPolicy.DefaultContextMenu

# Dialog constants
DialogAccepted = QDialog.DialogCode.Accepted
DialogRejected = QDialog.DialogCode.Rejected

# Window modality constants
WINDOW_MODAL = Qt.WindowModality.WindowModal
APPLICATION_MODAL = Qt.WindowModality.ApplicationModal
NON_MODAL = Qt.WindowModality.NonModal

# QDialogButtonBox constants
ButtonBox_Ok = QDialogButtonBox.StandardButton.Ok
ButtonBox_Cancel = QDialogButtonBox.StandardButton.Cancel
ButtonBox_Yes = QDialogButtonBox.StandardButton.Yes
ButtonBox_No = QDialogButtonBox.StandardButton.No
ButtonBox_Apply = QDialogButtonBox.StandardButton.Apply
ButtonBox_Close = QDialogButtonBox.StandardButton.Close

# QMessageBox constants
MessageBox_Yes = QMessageBox.StandardButton.Yes
MessageBox_No = QMessageBox.StandardButton.No
MessageBox_Ok = QMessageBox.StandardButton.Ok
MessageBox_Cancel = QMessageBox.StandardButton.Cancel
MessageBox_Information = QMessageBox.Icon.Information
MessageBox_Warning = QMessageBox.Icon.Warning
MessageBox_Critical = QMessageBox.Icon.Critical
MessageBox_Question = QMessageBox.Icon.Question

# Echo mode constants for QLineEdit
EchoModeNormal = QLineEdit.EchoMode.Normal
EchoModePassword = QLineEdit.EchoMode.Password

# QPalette constants
Palette_Window = QPalette.ColorRole.Window
Palette_WindowText = QPalette.ColorRole.WindowText
Palette_Base = QPalette.ColorRole.Base
Palette_Text = QPalette.ColorRole.Text

# QAbstractItemView constants
MultiSelection = QAbstractItemView.SelectionMode.MultiSelection
SingleSelection = QAbstractItemView.SelectionMode.SingleSelection
NoSelection = QAbstractItemView.SelectionMode.NoSelection
ExtendedSelection = QAbstractItemView.SelectionMode.ExtendedSelection
ContiguousSelection = QAbstractItemView.SelectionMode.ContiguousSelection

# Alternative names for consistency
MULTI_SELECTION = MultiSelection
SINGLE_SELECTION = SingleSelection
NO_SELECTION = NoSelection
EXTENDED_SELECTION = ExtendedSelection
CONTIGUOUS_SELECTION = ContiguousSelection

# QFrame constants
Frame_HLine = QFrame.Shape.HLine
Frame_VLine = QFrame.Shape.VLine
Frame_NoFrame = QFrame.Shape.NoFrame
Frame_Sunken = QFrame.Shadow.Sunken
Frame_Raised = QFrame.Shadow.Raised
Frame_Plain = QFrame.Shadow.Plain

# QFont constants
Font_Bold = QFont.Weight.Bold
Font_Normal = QFont.Weight.Normal
Font_Light = QFont.Weight.Light

# ScrollBar Policy constants
ScrollBarAlwaysOff = Qt.ScrollBarPolicy.ScrollBarAlwaysOff
ScrollBarAlwaysOn = Qt.ScrollBarPolicy.ScrollBarAlwaysOn
ScrollBarAsNeeded = Qt.ScrollBarPolicy.ScrollBarAsNeeded

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def safe_connect(signal, slot) -> None:
    """
    Connects signal/slot safely.

    Args:
        signal: Qt signal to connect
        slot: Slot/function to connect to the signal
    """
    try:
        signal.connect(slot)
    except Exception as e:
        try:
            from .utils import add_debug_message

            add_debug_message(f"Error connecting signal/slot: {e}", "COMPAT")
        except ImportError:
            print(f"Error connecting signal/slot: {e}")


def create_button(
    text: str, callback=None, tooltip_text: Optional[str] = None
) -> QPushButton:
    """
    Creates a button with callback and tooltip.

    Args:
        text: Button text
        callback: Function to be called when button is clicked
        tooltip_text: Tooltip text (optional)

    Returns:
        Configured QPushButton
    """
    button = QPushButton(text)

    if callback:
        safe_connect(button.clicked, callback)

    if tooltip_text:
        button.setToolTip(tooltip_text)

    return button


def show_message(title: str, message: str, message_type: str = "info") -> None:
    """
    Shows message to user.

    Args:
        title: Message title
        message: Message content
        message_type: Message type ("info", "warning", "error")
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
    Executes a dialog.

    Args:
        dialog: Qt dialog to execute

    Returns:
        int: Dialog result code (Accepted/Rejected)
    """
    return dialog.exec()


def safe_exec_menu(menu, position) -> Any:
    """
    Executes a context menu.

    Args:
        menu: QMenu to execute
        position: Position where to show the menu

    Returns:
        Selected QAction or None
    """
    return menu.exec(position)


def show_tooltip(message: str, period: int = 3000) -> None:
    """
    Shows temporary tooltip.

    Args:
        message: Tooltip message
        period: Duration in milliseconds
    """
    tooltip(message)


# Alias for consistency
safe_exec = safe_exec_dialog
