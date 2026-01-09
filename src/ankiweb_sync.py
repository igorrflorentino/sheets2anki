"""
Automatic synchronization module with AnkiWeb for the Sheets2Anki addon.

This module implements functionalities for automatic synchronization with AnkiWeb
after remote deck synchronization, including options for:
- Normal synchronization (download/upload as needed)
- Disable automatic synchronization

Features:
- Integration with Anki's sync API
- Timeout control and notifications
- Detailed operation logging
- Error and conflict handling
"""

from .compat import mw
from .styled_messages import StyledMessageBox
from .config_manager import get_ankiweb_sync_mode



# =============================================================================
# DEBUG UTILITIES
# =============================================================================

try:
    from .utils import add_debug_message
except ImportError:

    def add_debug_message(message, category="ANKIWEB_SYNC"):
        print(f"[{category}] {message}")


# =============================================================================
# MAIN SYNCHRONIZATION FUNCTIONS
# =============================================================================


def can_sync_ankiweb():
    """
    Checks if it's possible to synchronize with AnkiWeb.

    Returns:
        bool: True if it can sync, False otherwise
    """
    if not mw or not mw.col:
        add_debug_message("❌ Anki not available", "ANKIWEB_SYNC")
        return False

    # Check if profile manager exists
    if not hasattr(mw, "pm") or not mw.pm:
        add_debug_message("❌ Profile manager not available", "ANKIWEB_SYNC")
        return False

    # Check if credentials are configured
    try:
        # Method 1: Check if sync_key exists (default method)
        if hasattr(mw.pm, "sync_key") and mw.pm.sync_key():
            add_debug_message("✅ AnkiWeb configured (sync_key)", "ANKIWEB_SYNC")
            return True

        # Method 2: Check through profile
        if hasattr(mw.pm, "profile") and mw.pm.profile:
            profile = mw.pm.profile
            if isinstance(profile, dict):
                if profile.get("syncKey") or profile.get("syncUser"):
                    add_debug_message(
                        "✅ AnkiWeb configured (profile)", "ANKIWEB_SYNC"
                    )
                    return True

        # Method 3: Check if sync menu is available (indicates configuration)
        if hasattr(mw, "sync") and mw.sync:
            add_debug_message("✅ AnkiWeb: sync system available", "ANKIWEB_SYNC")
            return True

        add_debug_message(
            "⚠️ AnkiWeb is not configured - access Tools > Sync in Anki",
            "ANKIWEB_SYNC",
        )
        return False

    except Exception as e:
        add_debug_message(
            f"❌ Error checking AnkiWeb configuration: {e}", "ANKIWEB_SYNC"
        )
        return False


def sync_ankiweb_normal():
    """
    Executes normal synchronization with AnkiWeb (bidirectional).

    Returns:
        dict: Sync result with status and details
    """
    if not can_sync_ankiweb():
        return {
            "success": False,
            "error": "Cannot sync: AnkiWeb not configured or Anki not available",
        }

    add_debug_message(
        "🔄 Starting normal sync with AnkiWeb (bidirectional)...",
        "ANKIWEB_SYNC",
    )

    try:
        # Method 1: Use modern sync API
        if hasattr(mw, "sync") and hasattr(mw.sync, "sync"):
            add_debug_message(
                "🔄 Using modern sync API...", "ANKIWEB_SYNC"
            )
            mw.sync.sync()
            add_debug_message(
                "✅ AnkiWeb sync started (modern API)", "ANKIWEB_SYNC"
            )
            return {
                "success": True,
                "message": "AnkiWeb sync started successfully! Monitor progress in the Anki status bar.",
                "type": "normal",
            }

        # Method 2: Use onSync (direct method)
        elif hasattr(mw, "onSync"):
            add_debug_message("🔄 Using direct onSync method...", "ANKIWEB_SYNC")
            mw.onSync()
            add_debug_message(
                "✅ AnkiWeb sync started (onSync)", "ANKIWEB_SYNC"
            )
            return {
                "success": True,
                "message": "AnkiWeb sync started successfully! Anki will automatically decide whether to upload or download your data.",
                "type": "normal",
            }

        # Method 3: Try through menu actions
        elif hasattr(mw, "form") and hasattr(mw.form, "actionSync"):
            add_debug_message(
                "🔄 Using sync menu action...", "ANKIWEB_SYNC"
            )
            mw.form.actionSync.trigger()
            add_debug_message(
                "✅ AnkiWeb sync started (menu action)", "ANKIWEB_SYNC"
            )
            return {
                "success": True,
                "message": "AnkiWeb sync started via menu!",
                "type": "normal",
            }

        else:
            # Add debug info to understand what's available
            debug_info = []
            debug_info.append(f"mw exists: {mw is not None}")
            if mw:
                debug_info.append(f"mw.sync exists: {hasattr(mw, 'sync')}")
                if hasattr(mw, "sync"):
                    debug_info.append(
                        f"mw.sync.sync exists: {hasattr(mw.sync, 'sync')}"
                    )
                debug_info.append(f"mw.onSync exists: {hasattr(mw, 'onSync')}")
                debug_info.append(f"mw.form exists: {hasattr(mw, 'form')}")
                if hasattr(mw, "form"):
                    debug_info.append(
                        f"mw.form.actionSync exists: {hasattr(mw.form, 'actionSync')}"
                    )

            debug_message = " | ".join(debug_info)
            add_debug_message(f"🔍 Sync API debug: {debug_message}", "ANKIWEB_SYNC")

            return {
                "success": False,
                "error": f"Sync API not found. Debug: {debug_message}",
            }

    except Exception as e:
        add_debug_message(f"❌ Error during sync: {e}", "ANKIWEB_SYNC")
        return {"success": False, "error": f"Sync error: {str(e)}"}


def execute_ankiweb_sync_if_configured():
    """
    Executes AnkiWeb sync based on user configuration.
    This function is automatically called after remote deck synchronization.

    Returns:
        dict: Operation result with status and details, or None if disabled
    """
    sync_mode = get_ankiweb_sync_mode()

    if sync_mode == "none":
        add_debug_message("⏹️ AnkiWeb sync disabled", "ANKIWEB_SYNC")
        return None

    add_debug_message(f"🎯 Configured sync mode: {sync_mode}", "ANKIWEB_SYNC")

    # Check if can sync
    if not can_sync_ankiweb():
        error_msg = "AnkiWeb not configured - access Tools > Sync in Anki"
        add_debug_message(f"⚠️ {error_msg}", "ANKIWEB_SYNC")

        StyledMessageBox.warning(None, "AnkiWeb Config Error", f"Sheets2Anki: {error_msg}")

        return {"success": False, "error": error_msg}

    # Execute sync based on mode
    result = None

    if sync_mode == "sync":
        result = sync_ankiweb_normal()

    return result


# =============================================================================
# AUXILIARY FUNCTIONS
# =============================================================================


def get_sync_status():
    """
    Gets information about the current sync status.

    Returns:
        dict: Configuration status and sync capability
    """
    status = {
        "ankiweb_configured": can_sync_ankiweb(),
        "sync_mode": get_ankiweb_sync_mode(),

        "notifications_enabled": True,
        "can_sync": can_sync_ankiweb(),
        "debug_info": {},
    }

    # Add debug info
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
    Tests basic connectivity with AnkiWeb.
    This function tests network connectivity only, not credential configuration.

    Returns:
        dict: Connection test result
    """
    add_debug_message("🔍 Testing connectivity with AnkiWeb...", "ANKIWEB_SYNC")

    try:
        from anki.httpclient import HttpClient

        client = HttpClient()
        client.timeout = 10  # Short timeout for test

        # Try a simple operation
        response = client.get("https://ankiweb.net/account/login")

        if response.status_code == 200:
            add_debug_message("✅ AnkiWeb connectivity OK", "ANKIWEB_SYNC")

            # Also check if AnkiWeb is configured to give complete feedback
            is_configured = can_sync_ankiweb()

            # Check which sync APIs are available
            sync_methods = []
            if hasattr(mw, "sync") and hasattr(mw.sync, "sync"):
                sync_methods.append("modern API")
            if hasattr(mw, "onSync"):
                sync_methods.append("onSync")
            if hasattr(mw, "form") and hasattr(mw.form, "actionSync"):
                sync_methods.append("Menu action")

            methods_info = (
                f" (Available methods: {', '.join(sync_methods)})"
                if sync_methods
                else " (No sync method found)"
            )

            if is_configured:
                return {
                    "success": True,
                    "message": f"Connectivity OK and AnkiWeb configured! ✅{methods_info}",
                }
            else:
                return {
                    "success": True,
                    "message": f"Connectivity OK, but AnkiWeb is not configured. Access Tools > Sync in Anki to configure. ⚠️{methods_info}",
                }
        else:
            add_debug_message(
                f"❌ Connectivity error: {response.status_code}", "ANKIWEB_SYNC"
            )
            return {
                "success": False,
                "error": f"Connectivity error: HTTP {response.status_code}",
            }

    except Exception as e:
        add_debug_message(f"❌ Error testing connectivity: {e}", "ANKIWEB_SYNC")
        return {"success": False, "error": f"Connectivity error: {str(e)}"}
