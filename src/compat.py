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
    # Fallback para desenvolvimento
    import os
    stubs_path = os.path.join(os.path.dirname(__file__), '..', 'stubs')
    if os.path.exists(stubs_path):
        sys.path.insert(0, stubs_path)
        from aqt import mw
        from aqt.utils import showInfo, showWarning, showCritical, tooltip
        from aqt.qt import qconnect, QAction, QMenu, QKeySequence
    else:
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
        QCheckBox,
        QComboBox,
        QRadioButton,
        QGroupBox,
        QListWidget,
        QListWidgetItem,
        QProgressBar,
        QProgressDialog,
        QInputDialog,
        QMessageBox,
        QWidget,
        QFrame,
        QScrollArea,
        QSizePolicy,
        QKeySequence,
        QAction,
        QMenu,
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

# Constantes de diálogo
if hasattr(QDialog, 'Accepted'):
    DialogAccepted = QDialog.Accepted
    DialogRejected = QDialog.Rejected
else:
    DialogAccepted = 1
    DialogRejected = 0

# Constantes de echo mode para QLineEdit
if hasattr(QLineEdit, 'EchoMode'):
    EchoModeNormal = QLineEdit.EchoMode.Normal
    EchoModePassword = QLineEdit.EchoMode.Password
else:
    EchoModeNormal = QLineEdit.Normal
    EchoModePassword = QLineEdit.Password

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
