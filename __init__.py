"""
Sheets2Anki Add-on - Módulo Principal de Integração com Anki

Este módulo serve como ponto de entrada para o add-on Sheets2Anki do Anki,
integrando funcionalidades de sincronização de decks remotos com Google Sheets.

Funcionalidades principais:
- Configuração do ambiente Python para dependências
- Integração com interface do usuário do Anki
- Criação de menus e ações para gerenciamento de decks remotos
- Tratamento de erros e feedback ao usuário
- Ponte entre interface do Anki e lógica de sincronização

Estrutura do add-on:
- __init__.py: Módulo principal (este arquivo)
- remote_decks/: Lógica de sincronização e processamento
- libs/: Bibliotecas e dependências externas

Autor: Dr. Basti
Email: drbasti.co@gmail.com
"""

# =============================================================================
# CONFIGURAÇÃO DO AMBIENTE PYTHON
# =============================================================================

import sys
import os

# Configurar caminhos para dependências externas
addon_path = os.path.dirname(__file__)
libs_path = os.path.join(addon_path, 'remote_decks', 'libs')

# Adicionar bibliotecas ao path do Python se ainda não estiverem presentes
if libs_path not in sys.path:
    sys.path.insert(0, libs_path)

# =============================================================================
# IMPORTS DO ANKI E MÓDULOS INTERNOS
# =============================================================================

# Imports principais do Anki
from aqt import mw
from aqt.utils import showInfo, qconnect
from aqt.qt import QAction, QMenu, QKeySequence
from aqt.importing import ImportDialog

# Imports dos módulos internos com tratamento de erro robusto
try:
    from .remote_decks.main import import_test_deck
    from .remote_decks.main import addNewDeck
    from .remote_decks.main import syncDecksWithSelection as sDecks
    from .remote_decks.main import removeRemoteDeck as rDecks
    from .remote_decks.libs.org_to_anki.utils import getAnkiPluginConnector as getConnector
except Exception as e:
    showInfo(f"Erro ao importar módulos do plugin sheets2anki:\n{e}")
    raise

# =============================================================================
# TEMPLATES E CONFIGURAÇÕES
# =============================================================================

# =============================================================================
# TEMPLATES E CONFIGURAÇÕES
# =============================================================================

# Template de mensagem de erro para o usuário
errorTemplate = """
Olá! Parece que ocorreu um erro durante a execução.

O erro foi: {}.

Se você quiser que eu corrija, por favor relate aqui: https://github.com/sebastianpaez/sheets2anki

Certifique-se de fornecer o máximo de informações possível, especialmente o arquivo que causou o erro.
"""

# =============================================================================
# FUNÇÕES DE INTERFACE DO USUÁRIO
# =============================================================================

def addDeck():
    """
    Adiciona um novo deck remoto conectado a uma planilha do Google Sheets.
    
    Esta função:
    1. Inicializa a ponte com o Anki
    2. Chama a interface para adicionar novo deck
    3. Trata erros e exibe feedback apropriado
    4. Garante limpeza de recursos mesmo em caso de erro
    """
    ankiBridge = None
    try:
        ankiBridge = getConnector()
        ankiBridge.startEditing()
        addNewDeck()
    except Exception as e:
        errorMessage = str(e)
        showInfo(errorTemplate.format(errorMessage))
        if ankiBridge and ankiBridge.getConfig().get("debug", False):
            import traceback
            trace = traceback.format_exc()
            showInfo(str(trace))
    finally:
        if ankiBridge:
            ankiBridge.stopEditing()

def syncDecks():
    """
    Sincroniza todos os decks remotos configurados com suas fontes.
    
    Esta função:
    1. Inicializa a ponte com o Anki
    2. Executa sincronização de todos os decks remotos
    3. Exibe feedback de conclusão ao usuário
    4. Trata erros e garante limpeza de recursos
    """
    ankiBridge = None
    try:
        ankiBridge = getConnector()
        ankiBridge.startEditing()
        sDecks()
    except Exception as e:
        errorMessage = str(e)
        showInfo(errorTemplate.format(errorMessage))
        if ankiBridge and ankiBridge.getConfig().get("debug", False):
            import traceback
            trace = traceback.format_exc()
            showInfo(str(trace))
    finally:
        showInfo("Sincronização concluída")
        if ankiBridge:
            ankiBridge.stopEditing()

def removeRemote():
    """
    Remove a conexão de um deck remoto do sistema.
    
    Esta função:
    1. Inicializa a ponte com o Anki
    2. Permite ao usuário desconectar um deck remoto
    3. Trata erros e exibe feedback apropriado
    4. Garante limpeza de recursos
    """
    ankiBridge = None
    try:
        ankiBridge = getConnector()
        ankiBridge.startEditing()
        rDecks()
    except Exception as e:
        errorMessage = str(e)
        showInfo(errorTemplate.format(errorMessage))
        if ankiBridge and ankiBridge.getConfig().get("debug", False):
            import traceback
            trace = traceback.format_exc()
            showInfo(str(trace))
    finally:
        if ankiBridge:
            ankiBridge.stopEditing()

# =============================================================================
# CONFIGURAÇÃO DA INTERFACE DO ANKI
# =============================================================================

# Verificar se o Anki está disponível antes de configurar a interface
if mw is not None:
    # Criar submenu principal para funcionalidades do Sheets2Anki
    remoteDecksSubMenu = QMenu("Gerenciar Decks sheets2anki", mw)
    mw.form.menuTools.addMenu(remoteDecksSubMenu)

    # =========================================================================
    # AÇÕES DO MENU
    # =========================================================================

    # Ação: Adicionar novo deck remoto
    remoteDeckAction = QAction("Adicionar Novo Deck Remoto sheets2anki", mw)
    remoteDeckAction.setShortcut(QKeySequence("Ctrl+Shift+A"))
    qconnect(remoteDeckAction.triggered, addDeck)
    remoteDecksSubMenu.addAction(remoteDeckAction)

    # Ação: Sincronizar decks remotos
    syncDecksAction = QAction("Sincronizar Decks", mw)
    syncDecksAction.setShortcut(QKeySequence("Ctrl+Shift+S"))
    qconnect(syncDecksAction.triggered, syncDecks)
    remoteDecksSubMenu.addAction(syncDecksAction)

    # Ação: Desconectar deck remoto
    removeRemoteDeck = QAction("Desconectar um Deck Remoto", mw)
    removeRemoteDeck.setShortcut(QKeySequence("Ctrl+Shift+D"))
    qconnect(removeRemoteDeck.triggered, removeRemote)
    remoteDecksSubMenu.addAction(removeRemoteDeck)

    # Ação: Importar deck de teste (para desenvolvimento/debug)
    importTestDeckAction = QAction("Importar Deck de Teste", mw)
    importTestDeckAction.setShortcut(QKeySequence("Ctrl+Shift+T"))
    qconnect(importTestDeckAction.triggered, import_test_deck)
    remoteDecksSubMenu.addAction(importTestDeckAction)