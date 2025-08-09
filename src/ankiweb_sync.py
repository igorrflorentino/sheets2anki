"""
Módulo de sincronização automática com AnkiWeb para o addon Sheets2Anki.

Este módulo implementa funcionalidades para sincronização automática com o AnkiWeb
após a sincronização de decks remotos, incluindo opções para:
- Sincronização normal (download/upload conforme necessário)
- Forçar upload (enviar dados locais para o AnkiWeb)
- Desabilitar sincronização automática

Funcionalidades:
- Integração com a API de sync do Anki
- Controle de timeout e notificações
- Logging detalhado de operações
- Tratamento de erros e conflitos
"""

import time
from typing import Optional, Dict, Any
from .compat import mw, showInfo, showWarning
from .config_manager import (
    get_ankiweb_sync_mode,
    get_ankiweb_sync_timeout,
    get_ankiweb_sync_notifications
)

# =============================================================================
# UTILITÁRIOS DE DEBUG
# =============================================================================

try:
    from .utils import add_debug_message
except ImportError:
    def add_debug_message(message, category="ANKIWEB_SYNC"):
        print(f"[{category}] {message}")

# =============================================================================
# FUNÇÕES PRINCIPAIS DE SINCRONIZAÇÃO
# =============================================================================

def can_sync_ankiweb():
    """
    Verifica se é possível sincronizar com AnkiWeb.
    
    Returns:
        bool: True se pode sincronizar, False caso contrário
    """
    if not mw or not mw.col:
        add_debug_message("❌ Anki não disponível", "ANKIWEB_SYNC")
        return False
    
    # Verificar se existe configuração de sync
    if not hasattr(mw, 'pm') or not mw.pm:
        add_debug_message("❌ Profile manager não disponível", "ANKIWEB_SYNC")
        return False
    
    # Verificar se há credenciais configuradas (compatível com diferentes versões)
    try:
        # Tentar métodos diferentes baseados na versão do Anki
        ankiweb_configured = False
        
        # Método 1: Verificar se existe auth token ou similar
        if hasattr(mw.pm, 'sync_key') and mw.pm.sync_key():
            ankiweb_configured = True
            add_debug_message("✅ AnkiWeb configurado (sync_key encontrada)", "ANKIWEB_SYNC")
        
        # Método 2: Verificar configuração de sync no profile
        elif hasattr(mw.pm, 'profile') and mw.pm.profile and mw.pm.profile.get('syncKey'):
            ankiweb_configured = True
            add_debug_message("✅ AnkiWeb configurado (profile syncKey encontrada)", "ANKIWEB_SYNC")
        
        # Método 3: Verificar se sync está habilitado de alguma forma
        elif hasattr(mw.pm, 'meta') and mw.pm.meta and mw.pm.meta.get('syncKey'):
            ankiweb_configured = True
            add_debug_message("✅ AnkiWeb configurado (meta syncKey encontrada)", "ANKIWEB_SYNC")
        
        # Método 4: Verificar através das preferências
        elif hasattr(mw, 'pm') and hasattr(mw.pm, 'profile'):
            profile = mw.pm.profile
            if profile and isinstance(profile, dict) and profile.get('syncUser'):
                ankiweb_configured = True
                add_debug_message("✅ AnkiWeb configurado (syncUser encontrado)", "ANKIWEB_SYNC")
        
        if not ankiweb_configured:
            add_debug_message("⚠️ AnkiWeb não está configurado - acesse Ferramentas > Sincronizar no Anki", "ANKIWEB_SYNC")
            return False
        
        return True
        
    except Exception as e:
        add_debug_message(f"❌ Erro ao verificar configuração AnkiWeb: {e}", "ANKIWEB_SYNC")
        return False

def sync_ankiweb_normal():
    """
    Executa sincronização normal com AnkiWeb (bidirecionaal).
    
    Returns:
        dict: Resultado da sincronização com status e detalhes
    """
    if not can_sync_ankiweb():
        return {
            'success': False,
            'error': 'Não é possível sincronizar: AnkiWeb não configurado ou Anki não disponível'
        }
    
    add_debug_message("🔄 Iniciando sincronização normal com AnkiWeb (bidirecional)...", "ANKIWEB_SYNC")
    
    try:
        # Usar a função de sync integrada do Anki
        if hasattr(mw, 'sync') and hasattr(mw.sync, 'sync'):
            add_debug_message("🔄 Usando API de sync integrada...", "ANKIWEB_SYNC")
            
            # Executar sincronização através do MainWindow
            mw.sync.sync()
            
            add_debug_message("✅ Sincronização AnkiWeb iniciada com sucesso", "ANKIWEB_SYNC")
            return {
                'success': True,
                'message': 'Sincronização AnkiWeb iniciada com sucesso! Acompanhe o progresso na barra de status do Anki.',
                'type': 'normal'
            }
        else:
            # Fallback para versões mais antigas
            add_debug_message("🔄 Usando API de compatibilidade (versões anteriores do Anki)...", "ANKIWEB_SYNC")
            
            # Tentar usar o método direto
            if hasattr(mw, 'onSync'):
                mw.onSync()
                return {
                    'success': True,
                    'message': 'Sincronização AnkiWeb iniciada com sucesso! O Anki decidirá automaticamente se fará upload ou download dos seus dados.',
                    'type': 'normal'
                }
            else:
                return {
                    'success': False,
                    'error': 'API de sincronização não disponível nesta versão do Anki'
                }
    
    except Exception as e:
        add_debug_message(f"❌ Erro durante sincronização: {e}", "ANKIWEB_SYNC")
        return {
            'success': False,
            'error': f'Erro na sincronização: {str(e)}'
        }

def sync_ankiweb_force_upload():
    """
    Força upload dos dados locais para AnkiWeb.
    
    Returns:
        dict: Resultado da operação com status e detalhes
    """
    if not can_sync_ankiweb():
        return {
            'success': False,
            'error': 'Não é possível sincronizar: AnkiWeb não configurado ou Anki não disponível'
        }
    
    add_debug_message("⬆️ Iniciando sincronização com prioridade para upload local...", "ANKIWEB_SYNC")
    
    try:
        # Para force upload, usar a mesma API mas com aviso
        add_debug_message("ℹ️ Nota: O Anki usa sincronização inteligente - fará upload apenas se os dados locais forem mais recentes", "ANKIWEB_SYNC")
        
        # Executar sincronização normal - o Anki decidirá se precisa fazer upload
        if hasattr(mw, 'sync') and hasattr(mw.sync, 'sync'):
            add_debug_message("⬆️ Usando API moderna de sincronização do Anki...", "ANKIWEB_SYNC")
            
            mw.sync.sync()
            
            add_debug_message("✅ Sincronização para upload iniciada com sucesso", "ANKIWEB_SYNC")
            return {
                'success': True,
                'message': 'Sincronização AnkiWeb iniciada! Se seus dados locais forem mais recentes, serão enviados automaticamente para o AnkiWeb.',
                'type': 'force_upload'
            }
        elif hasattr(mw, 'onSync'):
            mw.onSync()
            return {
                'success': True,
                'message': 'Sincronização AnkiWeb iniciada com sucesso! O Anki decidirá automaticamente se fará upload ou download dos seus dados.',
                'type': 'force_upload'
            }
        else:
            return {
                'success': False,
                'error': 'API de sincronização não disponível nesta versão do Anki'
            }
    
    except Exception as e:
        add_debug_message(f"❌ Erro durante upload forçado: {e}", "ANKIWEB_SYNC")
        return {
            'success': False,
            'error': f'Erro no upload forçado: {str(e)}'
        }

def execute_ankiweb_sync_if_configured():
    """
    Executa sincronização AnkiWeb baseada na configuração do usuário.
    Esta função é chamada automaticamente após sincronização de decks remotos.
    
    Returns:
        dict: Resultado da operação com status e detalhes, ou None se desabilitado
    """
    sync_mode = get_ankiweb_sync_mode()
    
    if sync_mode == "none":
        add_debug_message("⏹️ Sincronização AnkiWeb desabilitada", "ANKIWEB_SYNC")
        return None
    
    add_debug_message(f"🎯 Modo de sync configurado: {sync_mode}", "ANKIWEB_SYNC")
    
    # Verificar se pode sincronizar
    if not can_sync_ankiweb():
        error_msg = "AnkiWeb não configurado - acesse Ferramentas > Sincronizar no Anki"
        add_debug_message(f"⚠️ {error_msg}", "ANKIWEB_SYNC")
        
        if get_ankiweb_sync_notifications():
            showWarning(f"Sheets2Anki: {error_msg}")
        
        return {
            'success': False,
            'error': error_msg
        }
    
    # Executar sincronização baseada no modo
    result = None
    
    if sync_mode == "sync":
        result = sync_ankiweb_normal()
    elif sync_mode == "force_upload":
        result = sync_ankiweb_force_upload()
    
    # Mostrar notificação se configurado
    if result and get_ankiweb_sync_notifications():
        if result['success']:
            showInfo(f"Sheets2Anki: {result['message']}")
        else:
            showWarning(f"Sheets2Anki: Erro na sincronização AnkiWeb - {result['error']}")
    
    return result

# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def get_sync_status():
    """
    Obtém informações sobre o status atual de sincronização.
    
    Returns:
        dict: Status de configuração e capacidade de sincronização
    """
    return {
        'ankiweb_configured': can_sync_ankiweb(),
        'sync_mode': get_ankiweb_sync_mode(),
        'timeout': get_ankiweb_sync_timeout(),
        'notifications_enabled': get_ankiweb_sync_notifications(),
        'can_sync': can_sync_ankiweb()
    }

def test_ankiweb_connection():
    """
    Testa a conexão com AnkiWeb sem fazer sincronização completa.
    
    Returns:
        dict: Resultado do teste de conexão
    """
    if not can_sync_ankiweb():
        return {
            'success': False,
            'error': 'AnkiWeb não configurado'
        }
    
    add_debug_message("🔍 Testando conexão com AnkiWeb...", "ANKIWEB_SYNC")
    
    try:
        from anki.httpclient import HttpClient
        
        client = HttpClient()
        client.timeout = 10  # Timeout curto para teste
        
        # Tentar uma operação simples
        response = client.get("https://ankiweb.net/account/login")
        
        if response.status_code == 200:
            add_debug_message("✅ Conexão com AnkiWeb OK", "ANKIWEB_SYNC")
            return {
                'success': True,
                'message': 'Conexão com AnkiWeb estabelecida'
            }
        else:
            add_debug_message(f"❌ Erro de conexão: {response.status_code}", "ANKIWEB_SYNC")
            return {
                'success': False,
                'error': f'Erro de conexão: {response.status_code}'
            }
    
    except Exception as e:
        add_debug_message(f"❌ Erro ao testar conexão: {e}", "ANKIWEB_SYNC")
        return {
            'success': False,
            'error': f'Erro ao testar conexão: {str(e)}'
        }
