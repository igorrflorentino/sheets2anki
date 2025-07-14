"""
Gerenciamento de configuração do addon Sheets2Anki.

Este módulo fornece funções para carregar e salvar
a configuração do addon de forma segura.
"""

from .compat import mw, showWarning
import os
import json

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

def get_default_config():
    """
    Obter configuração padrão do addon.
    
    Returns:
        dict: Configuração padrão do addon
    """
    return {
        "remote-decks": {},
        "deck_name": "Imported Deck",
        "model_name": "Basic",
        "sync_enabled": True,
        "max_cards": 1000,
        "auto_sync": False,
        "debug_mode": False
    }

def load_config():
    """
    Carregar configuração do addon.
    
    Returns:
        dict: Configuração carregada ou padrão
    """
    try:
        config = get_addon_config()
        default_config = get_default_config()
        
        # Mesclar configuração padrão com configuração carregada
        for key, value in default_config.items():
            if key not in config:
                config[key] = value
                
        return config
    except Exception:
        return get_default_config()

def validate_config(config):
    """
    Validar configuração do addon.
    
    Args:
        config (dict): Configuração para validar
        
    Returns:
        bool: True se configuração for válida, False caso contrário
    """
    if not isinstance(config, dict):
        return False
        
    # Verificar campos obrigatórios
    required_fields = ['deck_name', 'model_name', 'sync_enabled']
    for field in required_fields:
        if field not in config:
            return False
            
    # Verificar tipos de dados
    deck_name = config.get('deck_name')
    if not isinstance(deck_name, str) or not deck_name.strip():
        return False
        
    model_name = config.get('model_name')
    if not isinstance(model_name, str) or not model_name.strip():
        return False
        
    if not isinstance(config.get('sync_enabled'), bool):
        return False
        
    # Verificar valores numéricos
    if 'max_cards' in config:
        if not isinstance(config['max_cards'], int) or config['max_cards'] < 0:
            return False
            
    return True

def save_config(config):
    """
    Salvar configuração para arquivo JSON.
    
    Args:
        config (dict): Configuração para salvar
        
    Returns:
        bool: True se salvou com sucesso, False caso contrário
    """
    try:
        # Validar configuração antes de salvar
        if not validate_config(config):
            return False
            
        # Caminho do arquivo de configuração
        config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
        
        # Salvar configuração
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            
        return True
        
    except Exception:
        return False
