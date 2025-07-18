"""
Stub para aqt.utils - Utilitários do Anki
"""

def showInfo(message):
    """Mostra uma mensagem informativa"""
    print(f"[INFO] {message}")

def showWarning(message):
    """Mostra uma mensagem de aviso"""
    print(f"[WARNING] {message}")

def showCritical(message):
    """Mostra uma mensagem crítica"""
    print(f"[CRITICAL] {message}")

def askUser(message, parent=None):
    """Pergunta ao usuário"""
    print(f"[QUESTION] {message}")
    return True

def getFile(parent, title, dir="", filter="", selectedFilter=""):
    """Abre diálogo para selecionar arquivo"""
    return "/tmp/test_file.txt"

def getSaveFile(parent, title, dir="", filter="", selectedFilter=""):
    """Abre diálogo para salvar arquivo"""
    return "/tmp/test_save.txt"

def qconnect(signal, slot):
    """Conecta signal ao slot"""
    pass

def tooltip(message):
    """Mostra um tooltip"""
    print(f"[TOOLTIP] {message}")
