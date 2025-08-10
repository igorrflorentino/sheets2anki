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
- src/: Lógica de sincronização e processamento
- libs/: Bibliotecas e dependências externas

Autor: Igor Florentino
Email: igorlopesc@gmail.com
"""

# =============================================================================
# CONFIGURAÇÃO DO AMBIENTE PYTHON
# =============================================================================

import sys
import os

# Configurar caminhos para dependências externas
addon_path = os.path.dirname(__file__)
libs_path = os.path.join(addon_path, 'libs')

# Adicionar bibliotecas ao path do Python se ainda não estiverem presentes
if libs_path not in sys.path:
    sys.path.insert(0, libs_path)

# =============================================================================
# IMPORTS DO ANKI E MÓDULOS INTERNOS
# =============================================================================

# Imports principais do Anki com compatibilidade
try:
    from .src.compat import mw, showInfo, QAction, QMenu, QKeySequence, safe_qconnect as qconnect
    from aqt.importing import ImportDialog
except ImportError as e:
    # Fallback para desenvolvimento
    print(f"Erro ao importar módulos de compatibilidade: {e}")
    from aqt import mw
    from aqt.utils import showInfo
    from aqt.qt import QAction, QMenu, QKeySequence, qconnect
    from aqt.importing import ImportDialog

# Imports dos módulos internos com tratamento de erro robusto
try:
    from .src.deck_manager import import_test_deck
    from .src.deck_manager import addNewDeck
    from .src.deck_manager import syncDecksWithSelection as sDecks
    from .src.deck_manager import removeRemoteDeck as rDecks
    from .src.backup_system import show_backup_dialog
    from .src.templates_and_definitions import DEFAULT_PARENT_DECK_NAME
    from .libs.org_to_anki.utils import getAnkiPluginConnector as getConnector
    
except Exception as e:
    showInfo(f"Erro ao importar módulos do plugin Sheets2Anki:\n{e}")
    raise

# =============================================================================
# TEMPLATES E CONFIGURAÇÕES
# =============================================================================

# Template de mensagem de erro para o usuário
errorTemplate = """
Olá! Parece que ocorreu um erro durante a execução.

O erro foi: {}.

Se você quiser que eu corrija, por favor relate aqui: https://github.com/igorrflorentino/sheets2anki

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

def backup_decks():
    """
    Abre o diálogo de backup de decks remotos.
    
    Esta função permite ao usuário:
    1. Criar backup completo de suas configurações
    2. Restaurar backups anteriores
    3. Exportar/importar configurações específicas
    """
    try:
        show_backup_dialog()
    except Exception as e:
        error_msg = errorTemplate.format(str(e))
        showInfo(error_msg)

def syncDecks():
    """
    Sincroniza todos os decks remotos configurados.
    
    Esta função inicia o processo de sincronização de todos os decks
    cadastrados no sistema, baixando dados atualizados das planilhas
    do Google Sheets.
    """
    try:
        sDecks()
    except Exception as e:
        error_msg = errorTemplate.format(str(e))
        showInfo(error_msg)

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

def configure_global_students():
    """
    Abre o diálogo de configuração global de alunos.
    
    Esta função permite ao usuário configurar globalmente quais alunos
    devem ser sincronizados em todos os decks remotos.
    """
    try:
        from .src.global_student_config_dialog import show_global_student_config_dialog
        show_global_student_config_dialog(mw)
    except Exception as e:
        error_msg = errorTemplate.format(str(e))
        showInfo(error_msg)

def configure_deck_options_mode():
    """
    Abre o diálogo de configuração de modo de opções de deck.
    
    Esta função permite ao usuário escolher entre três modos:
    1. Compartilhado - Todos os decks usam "Sheets2Anki - Default"
    2. Individual - Cada deck tem seu próprio grupo "Sheets2Anki - [Nome]"
    3. Manual - Nenhuma aplicação automática de opções
    """
    try:
        from .src.deck_options_config_dialog import show_deck_options_config_dialog
        show_deck_options_config_dialog(mw)
    except Exception as e:
        error_msg = errorTemplate.format(str(e))
        showInfo(error_msg)

def configure_ankiweb_sync():
    """
    Abre o diálogo de configuração de sincronização automática com AnkiWeb.
    
    Esta função permite ao usuário escolher entre dois modos:
    1. Desabilitado - Não fazer sincronização automática
    2. Sincronizar - Executar sync após sincronização de decks
    """
    try:
        from .src.ankiweb_sync_config_dialog import show_ankiweb_sync_config
        show_ankiweb_sync_config()
    except Exception as e:
        error_msg = errorTemplate.format(str(e))
        showInfo(error_msg)

# =============================================================================
# CONFIGURAÇÃO DA INTERFACE DO ANKI
# =============================================================================

# Verificar se o Anki está disponível antes de configurar a interface
if mw is not None:
    # Criar submenu principal para funcionalidades do Sheets2Anki
    remoteDecksSubMenu = QMenu(DEFAULT_PARENT_DECK_NAME, mw)
    mw.form.menuTools.addMenu(remoteDecksSubMenu)

    # =========================================================================
    # AÇÕES DO MENU
    # =========================================================================

    # Ação: Adicionar novo deck remoto
    remoteDeckAction = QAction("Adicionar Novo Deck Remoto", mw)
    remoteDeckAction.setShortcut(QKeySequence("Ctrl+Shift+A"))
    qconnect(remoteDeckAction.triggered, addDeck)
    remoteDecksSubMenu.addAction(remoteDeckAction)

    # Ação: Sincronizar decks remotos
    syncDecksAction = QAction("Sincronizar Decks Remotos", mw)
    syncDecksAction.setShortcut(QKeySequence("Ctrl+Shift+S"))
    qconnect(syncDecksAction.triggered, syncDecks)
    remoteDecksSubMenu.addAction(syncDecksAction)

    # Ação: Desconectar deck remoto
    removeRemoteDeck = QAction("Desconectar um Deck Remoto", mw)
    removeRemoteDeck.setShortcut(QKeySequence("Ctrl+Shift+D"))
    qconnect(removeRemoteDeck.triggered, removeRemote)
    remoteDecksSubMenu.addAction(removeRemoteDeck)

    # Separador
    remoteDecksSubMenu.addSeparator()

    # Ação: Configuração Global de Alunos
    studentConfigAction = QAction("Configurar Alunos Globalmente", mw)
    studentConfigAction.setShortcut(QKeySequence("Ctrl+Shift+G"))
    qconnect(studentConfigAction.triggered, configure_global_students)
    remoteDecksSubMenu.addAction(studentConfigAction)

    # Ação: Configurar modo de opções de deck
    deckOptionsConfigAction = QAction("Configurar Opções de Deck", mw)
    deckOptionsConfigAction.setShortcut(QKeySequence("Ctrl+Shift+O"))
    qconnect(deckOptionsConfigAction.triggered, configure_deck_options_mode)
    remoteDecksSubMenu.addAction(deckOptionsConfigAction)

    # Ação: Configurar sincronização AnkiWeb
    ankiWebSyncConfigAction = QAction("Configurar Sincronização AnkiWeb", mw)
    ankiWebSyncConfigAction.setShortcut(QKeySequence("Ctrl+Shift+W"))
    qconnect(ankiWebSyncConfigAction.triggered, configure_ankiweb_sync)
    remoteDecksSubMenu.addAction(ankiWebSyncConfigAction)

    # Separador
    remoteDecksSubMenu.addSeparator()

    # Ação: Backup de decks remotos
    backupDecksAction = QAction("Backup de Decks Remotos", mw)
    backupDecksAction.setShortcut(QKeySequence("Ctrl+Shift+B"))
    qconnect(backupDecksAction.triggered, backup_decks)
    remoteDecksSubMenu.addAction(backupDecksAction)

    # Ação: Importar deck de teste (apenas para desenvolvimento/debug)
    try:
        from .src.templates_and_definitions import IS_DEVELOPMENT_MODE
        if IS_DEVELOPMENT_MODE:
            importTestDeckAction = QAction("Importar Deck de Teste", mw)
            importTestDeckAction.setShortcut(QKeySequence("Ctrl+Shift+T"))
            qconnect(importTestDeckAction.triggered, import_test_deck)
            remoteDecksSubMenu.addAction(importTestDeckAction)
    except ImportError:
        pass  # Se não conseguir importar, não mostra o menu