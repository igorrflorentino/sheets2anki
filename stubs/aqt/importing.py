"""
Stub para aqt.importing - Importação do Anki
"""

from .qt import QDialog

class ImportDialog:
    def __init__(self, mw=None):
        self.mw = mw
        
    def exec(self):
        return QDialog.Accepted
