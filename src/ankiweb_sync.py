"""
Módulo de sincronização automática com AnkiWeb para o addon Sheets2Anki.

Este módulo implementa funcionalidades para sincronização automática com o AnkiWeb
após a sincronização de decks remotos, incluindo opções para:
- Sincronização normal (download/upload conforme necessário)
- Desabilitar sincronização automática

Funcionalidades:
- Integração com a API de sync do Anki
- Controle de timeout e notificações
- Logging detalhado de operações
- Tratamento de erros e conflitos
"""

from .compat import mw
from .compat import showWarning
from .config_manager import get_ankiweb_sync_mode
from .config_manager import get_ankiweb_sync_notifications
from .config_manager import get_ankiweb_sync_timeout

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

    # Verificar se existe profile manager
    if not hasattr(mw, "pm") or not mw.pm:
        add_debug_message("❌ Profile manager não disponível", "ANKIWEB_SYNC")
        return False

    # Verificar se há credenciais configuradas
    try:
        # Método 1: Verificar se existe sync_key (método padrão)
        if hasattr(mw.pm, "sync_key") and mw.pm.sync_key():
            add_debug_message("✅ AnkiWeb configurado (sync_key)", "ANKIWEB_SYNC")
            return True

        # Método 2: Verificar através do profile
        if hasattr(mw.pm, "profile") and mw.pm.profile:
            profile = mw.pm.profile
            if isinstance(profile, dict):
                if profile.get("syncKey") or profile.get("syncUser"):
                    add_debug_message(
                        "✅ AnkiWeb configurado (profile)", "ANKIWEB_SYNC"
                    )
                    return True

        # Método 3: Verificar se o menu de sync está disponível (indica configuração)
        if hasattr(mw, "sync") and mw.sync:
            add_debug_message("✅ AnkiWeb: sistema de sync disponível", "ANKIWEB_SYNC")
            return True

        add_debug_message(
            "⚠️ AnkiWeb não está configurado - acesse Ferramentas > Sincronizar no Anki",
            "ANKIWEB_SYNC",
        )
        return False

    except Exception as e:
        add_debug_message(
            f"❌ Erro ao verificar configuração AnkiWeb: {e}", "ANKIWEB_SYNC"
        )
        return False


def sync_ankiweb_normal():
    """
    Executa sincronização normal com AnkiWeb (bidirecionaal).

    Returns:
        dict: Resultado da sincronização com status e detalhes
    """
    if not can_sync_ankiweb():
        return {
            "success": False,
            "error": "Não é possível sincronizar: AnkiWeb não configurado ou Anki não disponível",
        }

    add_debug_message(
        "🔄 Iniciando sincronização normal com AnkiWeb (bidirecional)...",
        "ANKIWEB_SYNC",
    )

    try:
        # Método 1: Usar a API moderna de sincronização
        if hasattr(mw, "sync") and hasattr(mw.sync, "sync"):
            add_debug_message(
                "🔄 Usando API moderna de sincronização...", "ANKIWEB_SYNC"
            )
            mw.sync.sync()
            add_debug_message(
                "✅ Sincronização AnkiWeb iniciada (API moderna)", "ANKIWEB_SYNC"
            )
            return {
                "success": True,
                "message": "Sincronização AnkiWeb iniciada com sucesso! Acompanhe o progresso na barra de status do Anki.",
                "type": "normal",
            }

        # Método 2: Usar onSync (método direto)
        elif hasattr(mw, "onSync"):
            add_debug_message("🔄 Usando método onSync direto...", "ANKIWEB_SYNC")
            mw.onSync()
            add_debug_message(
                "✅ Sincronização AnkiWeb iniciada (onSync)", "ANKIWEB_SYNC"
            )
            return {
                "success": True,
                "message": "Sincronização AnkiWeb iniciada com sucesso! O Anki decidirá automaticamente se fará upload ou download dos seus dados.",
                "type": "normal",
            }

        # Método 3: Tentar através de ações do menu
        elif hasattr(mw, "form") and hasattr(mw.form, "actionSync"):
            add_debug_message(
                "🔄 Usando ação de menu de sincronização...", "ANKIWEB_SYNC"
            )
            mw.form.actionSync.trigger()
            add_debug_message(
                "✅ Sincronização AnkiWeb iniciada (menu action)", "ANKIWEB_SYNC"
            )
            return {
                "success": True,
                "message": "Sincronização AnkiWeb iniciada através do menu!",
                "type": "normal",
            }

        else:
            # Adicionar informações de debug para entender o que está disponível
            debug_info = []
            debug_info.append(f"mw existe: {mw is not None}")
            if mw:
                debug_info.append(f"mw.sync existe: {hasattr(mw, 'sync')}")
                if hasattr(mw, "sync"):
                    debug_info.append(
                        f"mw.sync.sync existe: {hasattr(mw.sync, 'sync')}"
                    )
                debug_info.append(f"mw.onSync existe: {hasattr(mw, 'onSync')}")
                debug_info.append(f"mw.form existe: {hasattr(mw, 'form')}")
                if hasattr(mw, "form"):
                    debug_info.append(
                        f"mw.form.actionSync existe: {hasattr(mw.form, 'actionSync')}"
                    )

            debug_message = " | ".join(debug_info)
            add_debug_message(f"🔍 Debug API sync: {debug_message}", "ANKIWEB_SYNC")

            return {
                "success": False,
                "error": f"API de sincronização não encontrada. Debug: {debug_message}",
            }

    except Exception as e:
        add_debug_message(f"❌ Erro durante sincronização: {e}", "ANKIWEB_SYNC")
        return {"success": False, "error": f"Erro na sincronização: {str(e)}"}


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

        return {"success": False, "error": error_msg}

    # Executar sincronização baseada no modo
    result = None

    if sync_mode == "sync":
        result = sync_ankiweb_normal()

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
    status = {
        "ankiweb_configured": can_sync_ankiweb(),
        "sync_mode": get_ankiweb_sync_mode(),
        "timeout": get_ankiweb_sync_timeout(),
        "notifications_enabled": get_ankiweb_sync_notifications(),
        "can_sync": can_sync_ankiweb(),
        "debug_info": {},
    }

    # Adicionar informações de debug
    if mw and mw.pm:
        try:
            debug_info = {}
            debug_info["has_sync_key"] = hasattr(mw.pm, "sync_key") and bool(
                mw.pm.sync_key()
            )
            debug_info["has_profile"] = hasattr(mw.pm, "profile") and bool(
                mw.pm.profile
            )
            debug_info["has_sync_system"] = hasattr(mw, "sync") and bool(mw.sync)

            if (
                hasattr(mw.pm, "profile")
                and mw.pm.profile
                and isinstance(mw.pm.profile, dict)
            ):
                profile = mw.pm.profile
                debug_info["has_profile_synckey"] = bool(profile.get("syncKey"))
                debug_info["has_profile_syncuser"] = bool(profile.get("syncUser"))

            status["debug_info"] = debug_info
        except Exception as e:
            status["debug_info"]["error"] = str(e)

    return status


def test_ankiweb_connection():
    """
    Testa conectividade básica com AnkiWeb.
    Esta função testa apenas a conectividade de rede, não a configuração de credenciais.

    Returns:
        dict: Resultado do teste de conexão
    """
    add_debug_message("🔍 Testando conectividade com AnkiWeb...", "ANKIWEB_SYNC")

    try:
        from anki.httpclient import HttpClient

        client = HttpClient()
        client.timeout = 10  # Timeout curto para teste

        # Tentar uma operação simples
        response = client.get("https://ankiweb.net/account/login")

        if response.status_code == 200:
            add_debug_message("✅ Conectividade com AnkiWeb OK", "ANKIWEB_SYNC")

            # Verificar também se AnkiWeb está configurado para dar feedback completo
            is_configured = can_sync_ankiweb()

            # Verificar quais APIs de sync estão disponíveis
            sync_methods = []
            if hasattr(mw, "sync") and hasattr(mw.sync, "sync"):
                sync_methods.append("API moderna")
            if hasattr(mw, "onSync"):
                sync_methods.append("onSync")
            if hasattr(mw, "form") and hasattr(mw.form, "actionSync"):
                sync_methods.append("Menu action")

            methods_info = (
                f" (Métodos disponíveis: {', '.join(sync_methods)})"
                if sync_methods
                else " (Nenhum método de sync encontrado)"
            )

            if is_configured:
                return {
                    "success": True,
                    "message": f"Conectividade OK e AnkiWeb configurado! ✅{methods_info}",
                }
            else:
                return {
                    "success": True,
                    "message": f"Conectividade OK, mas AnkiWeb não está configurado. Acesse Ferramentas > Sincronizar no Anki para configurar. ⚠️{methods_info}",
                }
        else:
            add_debug_message(
                f"❌ Erro de conectividade: {response.status_code}", "ANKIWEB_SYNC"
            )
            return {
                "success": False,
                "error": f"Erro de conectividade: HTTP {response.status_code}",
            }

    except Exception as e:
        add_debug_message(f"❌ Erro ao testar conectividade: {e}", "ANKIWEB_SYNC")
        return {"success": False, "error": f"Erro de conectividade: {str(e)}"}
