"""
Gerenciamento de configuração do addon Sheets2Anki.

Este módulo fornece funções para carregar e salvar
a configuração do addon de forma segura.
"""

from .compat import mw, showWarning

def get_addon_config():
    """
    Obter configuração do addon de forma segura.
    
    Returns:
        dict: Configuração do addon com chave 'remote-decks' garantida
    """
    try:
        config = mw.addonManager.getConfig(__name__)
        if not config:
            config = {}
        
        # Garantir que a chave 'remote-decks' existe
        if "remote-decks" not in config:
            config["remote-decks"] = {}
            
        return config
    except Exception as e:
        showWarning(f"Erro ao carregar configuração: {str(e)}")
        return {"remote-decks": {}}

def save_addon_config(config):
    """
    Salvar configuração do addon de forma segura.
    
    Args:
        config: Dicionário com configuração do addon
    """
    try:
        mw.addonManager.writeConfig(__name__, config)
    except Exception as e:
        showWarning(f"Erro ao salvar configuração: {str(e)}")
