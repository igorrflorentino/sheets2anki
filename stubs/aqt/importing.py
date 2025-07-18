"""
Stub para aqt.importing - Importação do Anki
"""

# Evitar importação circular
class QDialog:
    def __init__(self, parent=None):
        pass

class ImportDialog:
    def __init__(self, mw=None):
        self.mw = mw
        
    def exec(self):
        return QDialog.Accepted
