"""
Módulo para corrigir problemas de compatibilidade com exec_/exec
"""

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