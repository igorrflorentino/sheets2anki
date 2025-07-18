"""
Módulo para corrigir problemas de compatibilidade com QAbstractItemView.MultiSelection
"""

from aqt.qt import QAbstractItemView

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