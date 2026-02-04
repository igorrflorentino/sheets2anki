"""
Configuration manager for the Sheets2Anki addon.

This module implements a hierarchical configuration system that uses:
- config.json: Addon default settings
- meta.json: User settings and remote deck data (source of truth)

Features:
- Loading and saving configurations
- Migrating old configurations
- User preference management
- Remote deck control
"""

import json
import os
import time
import traceback
import copy

try:
    from .compat import mw
    from .styled_messages import StyledMessageBox
    from .utils import get_spreadsheet_id_from_url, add_debug_message
except ImportError:
    # For standalone tests
    from compat import mw
    from utils import get_spreadsheet_id_from_url, add_debug_message


def add_debug_msg(message, category="CONFIG"):
    """Local helper for debug messages."""
    add_debug_message(message, category)

# =============================================================================
# UTILITY FUNCTIONS FOR SPREADSHEET ID
# =============================================================================


def get_deck_id(url):
    """
    Gets the spreadsheet ID to identify a deck.

    Args:
        url (str): Remote deck edit URL

    Returns:
        str: Google Sheets spreadsheet ID
        
    Raises:
        ValueError: If the URL is not a valid edit URL
    """
    return get_spreadsheet_id_from_url(url)


# =============================================================================
# CONFIGURATION CONSTANTS
# =============================================================================

DEFAULT_CONFIG = {
    "config": {
        "debug": False,
        "auto_sync_on_startup": False,
        "max_sync_retries": 3,
        "sync_timeout_seconds": 60,
        "deck_options_mode": "individual",  # "shared", "individual", "manual"
        "ankiweb_sync_mode": "sync",  # "none", "sync"
        # Automatic backup settings
        "auto_backup_enabled": False,  # enable automatic configuration backup
        "auto_backup_directory": None,  # directory to save automatic backups (empty = use default)
        "auto_backup_max_files": 50,  # maximum backup files to keep
        "auto_backup_type": "simple",  # "simple" or "full"
        "accumulate_logs": True  # whether to keep logs between sessions
    },
    "students": {
        "available_students": [],
        "enabled_students": [],
        "auto_remove_disabled_students": True,
        "sync_missing_students_notes": True,
        # Persistent history of students who have already been synchronized
        "sync_history": {}  # format: "student_name": {"first_sync": timestamp, "last_sync": timestamp, "total_syncs": count}
    },
    "decks": {}
}

DEFAULT_META = copy.deepcopy(DEFAULT_CONFIG)

# =============================================================================
# MAIN FUNCTIONS
# =============================================================================


def get_config():
    """
    Loads default configuration from config.json.

    Returns:
        dict: Addon default configuration
    """
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "config.json"
    )

    try:
        if os.path.exists(config_path):
            with open(config_path, encoding="utf-8") as f:
                config = json.load(f)

            # Merge with defaults to ensure compatibility
            merged_config = DEFAULT_CONFIG.copy()
            merged_config.update(config)
            return merged_config
        else:
            return DEFAULT_CONFIG.copy()
    except Exception as e:
        if mw:
            StyledMessageBox.warning(
                mw,
                "Config Load Error",
                f"Error loading config.json: {str(e)}",
                detailed_text="Using default configuration."
            )
        return DEFAULT_CONFIG.copy()


def get_meta():
    """
    Loads user metadata from meta.json (source of truth).
    If meta.json doesn't exist, allows initialization from config.json.

    Returns:
        dict: User metadata including preferences and remote decks
    """
    try:
        import json
        import os

        # Paths
        addon_path = os.path.dirname(os.path.dirname(__file__))
        meta_path = os.path.join(addon_path, "meta.json")
        config_path = os.path.join(addon_path, "config.json")

        # 1. Try to load meta.json (User settings)
        if os.path.exists(meta_path):
            with open(meta_path, encoding="utf-8") as f:
                meta = json.load(f)
        
        # 2. If meta.json doesn't exist, try config.json (Defaults)
        elif os.path.exists(config_path):
            with open(config_path, encoding="utf-8") as f:
                meta = json.load(f)
                
        # 3. Fallback to hardcoded defaults
        else:
            meta = DEFAULT_META.copy()

        # Ensure proper structure
        meta = _ensure_meta_structure(meta)

        return meta
    except Exception as e:
        if mw:
            StyledMessageBox.warning(
                mw,
                "Meta Load Error",
                f"Error loading meta.json: {str(e)}",
                detailed_text="Using default configuration."
            )
        return DEFAULT_META.copy()


def save_meta(meta):
    """
    Saves user metadata to meta.json.

    Args:
        meta (dict): Metadata to save
    """
    try:
        import json
        import os

        # Save directly to meta.json file
        addon_path = os.path.dirname(os.path.dirname(__file__))
        meta_path = os.path.join(addon_path, "meta.json")

        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=4, ensure_ascii=False)
    except Exception as e:
        if mw:
            StyledMessageBox.warning(mw, "Meta Save Error", f"Error saving meta.json: {str(e)}")


def get_remote_decks():
    """
    Gets configured remote decks with hash-based structure.

    Returns:
        dict: Dictionary {hash_key: deck_info} where deck_info contains:
            - local_deck_id: Deck ID in Anki
            - local_deck_name: Deck name in Anki
            - remote_deck_url: Remote deck URL
            - remote_deck_name: Remote file name
            - note_types: Dict {note_type_id: expected_name}
    """
    meta = get_meta()
    return meta.get("decks", {})


def save_remote_decks(remote_decks):
    """
    Saves remote decks to the configuration using hash-based structure.

    Args:
        remote_decks (dict): Dictionary {hash_key: deck_info}
    """
    # Debug: Log what is being saved
    from .utils import add_debug_message

    add_debug_message("=== SAVING DECK INFO TO META.JSON ===", "Config Manager")
    for hash_key, deck_info in remote_decks.items():
        local_deck_id = deck_info.get("local_deck_id", "N/A")
        local_deck_name = deck_info.get("local_deck_name", "N/A")
        add_debug_message(
            f"Hash {hash_key}: local_deck_id={local_deck_id}, local_deck_name='{local_deck_name}'",
            "Config Manager",
        )

    meta = get_meta()
    meta["decks"] = remote_decks
    save_meta(meta)

    add_debug_message("✓ Deck info successfully saved to meta.json", "Config Manager")


def add_remote_deck(url, deck_info):
    """
    Adds a remote deck to the configuration using hash as key.

    Args:
        url (str): Remote deck URL
        deck_info (dict): Deck information in the new structure
    """
    # Generate hash for the spreadsheet ID
    spreadsheet_id = get_deck_id(url)

    remote_decks = get_remote_decks()
    remote_decks[spreadsheet_id] = deck_info
    save_remote_decks(remote_decks)


def create_deck_info(
    url, local_deck_id, local_deck_name, remote_deck_name=None, **additional_info
):
    """
    Creates a deck info dictionary with the new structure.

    Args:
        url (str): Remote deck URL
        local_deck_id (int): Deck ID in Anki
        local_deck_name (str): Deck name in Anki
        remote_deck_name (str, optional): Remote file name
        **additional_info: Additional fields

    Returns:
        dict: Full deck structure
    """
    # Resolve remote_deck_name conflicts using DeckNameManager
    from .deck_manager import DeckNameManager
    import time

    resolved_remote_name = DeckNameManager.resolve_remote_name_conflict(
        url, remote_deck_name or ""
    )

    # Determine options group name based on current mode
    deck_options_mode = get_deck_options_mode()
    if deck_options_mode == "individual":
        options_group_name = f"Sheets2Anki - {resolved_remote_name}"
    elif deck_options_mode == "shared":
        options_group_name = "Sheets2Anki - Default Options"
    else:  # manual
        options_group_name = None

    # Ensure created_at always exists
    current_timestamp = int(time.time())
    created_at = additional_info.pop('created_at', current_timestamp)

    deck_info = {
        "remote_deck_url": url,
        "local_deck_id": local_deck_id,
        "local_deck_name": local_deck_name,
        "remote_deck_name": resolved_remote_name,
        "note_types": {},
        "is_test_deck": False,
        "is_sync": True,
        "local_deck_configurations_package_name": options_group_name,
        "created_at": created_at,
        "last_sync": None,  # null = never synchronized (NEW)
        "first_sync": None,  # First synchronization timestamp
        "sync_count": 0,  # Synchronization counter
    }

    # Add extra fields if provided
    deck_info.update(additional_info)

    return deck_info


def add_remote_deck_simple(
    url, local_deck_id, local_deck_name, remote_deck_name=None, **additional_info
):
    """
    Simplified version to add remote deck with clean structure.

    Args:
        url (str): Remote deck URL
        local_deck_id (int): Deck ID in Anki
        local_deck_name (str): Deck name in Anki
        remote_deck_name (str, optional): Remote file name
        **additional_info: Additional fields
    """
    deck_info = create_deck_info(
        url, local_deck_id, local_deck_name, remote_deck_name, **additional_info
    )
    add_remote_deck(url, deck_info)


def ensure_deck_consistency():
    """
    Ensures that all decks have all required fields.
    Fixes inconsistencies in existing decks.
    """
    import time
    
    meta = get_meta()
    decks = meta.get("decks", {})
    modified = False
    
    required_fields = {
        "remote_deck_url": None,
        "local_deck_id": None,
        "local_deck_name": None,
        "remote_deck_name": None,
        "note_types": {},
        "is_test_deck": False,
        "is_sync": True,
        "local_deck_configurations_package_name": None,
        "created_at": int(time.time()),
        "last_sync": None,  # null = never synchronized
        "first_sync": None,  # First synchronization timestamp
        "sync_count": 0,  # Synchronization counter
    }
    
    for spreadsheet_id, deck_info in decks.items():
        for field, default_value in required_fields.items():
            if field not in deck_info:
                if field == "created_at":
                    # For created_at, use timestamp based on local_deck_id if available
                    # or current timestamp as fallback
                    deck_info[field] = deck_info.get("local_deck_id", int(time.time()))
                elif field in ["last_sync", "first_sync"]:
                    # Synchronization fields always start as None for existing decks
                    # that didn't have these fields (consider them as already synced)
                    deck_info[field] = None
                elif field == "sync_count":
                    # For existing decks without sync_count, assume they were already synced
                    deck_info[field] = 1
                else:
                    deck_info[field] = default_value
                modified = True
                add_debug_msg(f"[CONSISTENCY] Added field '{field}' to deck {spreadsheet_id}")
    
    if modified:
        save_meta(meta)
        add_debug_msg(f"[CONSISTENCY] {len(decks)} decks fixed to ensure consistency")
    else:
        add_debug_msg("[CONSISTENCY] All decks are already consistent")
    
    return modified


def update_deck_sync_status(deck_url, success=True):
    """
    Updates synchronization fields for a deck after a sync.
    
    Args:
        deck_url (str): Synchronized deck URL
        success (bool): Whether the sync was successful
    
    Returns:
        bool: True if deck was new (never synchronized), False otherwise
    """
    import time
    
    meta = get_meta()
    decks = meta.get("decks", {})
    
    # Find deck by URL
    deck_hash = None
    deck_info = None
    
    for hash_key, info in decks.items():
        if info.get("remote_deck_url") == deck_url:
            deck_hash = hash_key
            deck_info = info
            break
    
    if not deck_info:
        add_debug_msg(f"[SYNC_STATUS] Deck not found for URL: {deck_url}")
        return False
    
    # Check if it's a new deck (never synchronized)
    was_new_deck = deck_info.get("last_sync") is None
    
    if success:
        current_timestamp = int(time.time())
        
        # If it's the first successful sync, set first_sync
        if deck_info.get("first_sync") is None:
            deck_info["first_sync"] = current_timestamp
        
        # Update last_sync
        deck_info["last_sync"] = current_timestamp
        
        # Increment counter
        deck_info["sync_count"] = deck_info.get("sync_count", 0) + 1
        
        # Save changes
        save_meta(meta)
        
        add_debug_msg(f"[SYNC_STATUS] Deck {deck_hash} synced (new: {was_new_deck})")
    
    return was_new_deck


def is_deck_new(deck_url):
    """
    Checks if a deck is new (has never been synchronized).
    
    Args:
        deck_url (str): Deck URL
        
    Returns:
        bool: True if the deck has never been synchronized, False otherwise
    """
    meta = get_meta()
    decks = meta.get("decks", {})
    
    for deck_info in decks.values():
        if deck_info.get("remote_deck_url") == deck_url:
            return deck_info.get("last_sync") is None
    
    return False


def get_deck_local_name(url):
    """
    Gets the local name of a deck from its URL.

    Args:
        url (str): Deck URL

    Returns:
        str: Local deck name or None if not found
    """
    # Generate spreadsheet ID
    spreadsheet_id = get_deck_id(url)

    remote_decks = get_remote_decks()
    deck_info = remote_decks.get(spreadsheet_id, {})

    return deck_info.get("local_deck_name")


def get_deck_remote_name(url):
    """
    Gets the remote name of a deck from its URL.

    Args:
        url (str): Deck URL

    Returns:
        str: Remote deck name or None if not found
    """
    # Generate hash for the spreadsheet ID
    spreadsheet_id = get_deck_id(url)

    remote_decks = get_remote_decks()
    deck_info = remote_decks.get(spreadsheet_id, {})

    # If it exists in the new structure, use it
    if "remote_deck_name" in deck_info:
        return deck_info["remote_deck_name"]

    # Fallback: extract from URL if it doesn't exist
    if url:
        # If prefix changed, re-extract from URL to keep consistency
        from .deck_manager import DeckNameManager

        return DeckNameManager.extract_remote_name_from_url(url)

    return None


def remove_remote_deck(url):
    """
    Removes a remote deck from the configuration.

    Args:
        url (str): Remote deck URL to be removed
    """
    # Generate hash for the spreadsheet ID
    spreadsheet_id = get_deck_id(url)

    remote_decks = get_remote_decks()
    if spreadsheet_id in remote_decks:
        del remote_decks[spreadsheet_id]
        save_remote_decks(remote_decks)


def disconnect_deck(url):
    """
    Completely removes a remote deck from the system.
    This action is irreversible - the deck can only be reconnected if it's re-registered.

    Args:
        url (str): Deck URL to be disconnected
    """
    # Generate hash for the spreadsheet ID
    spreadsheet_id = get_deck_id(url)

    meta = get_meta()
    remote_decks = meta.get("decks", {})

    # Completely remove deck from remote decks list
    if spreadsheet_id in remote_decks:
        del remote_decks[spreadsheet_id]
        meta["decks"] = remote_decks  # type: ignore
        save_meta(meta)


def is_deck_disconnected(url):
    """
    Checks if a deck is disconnected (no longer in the configuration).

    Args:
        url (str): Deck URL

    Returns:
        bool: True if disconnected (doesn't exist), False if it exists
    """
    # Generate hash for the spreadsheet ID
    spreadsheet_id = get_deck_id(url)

    remote_decks = get_remote_decks()
    return spreadsheet_id not in remote_decks


def get_active_decks():
    """
    Gets all active remote decks.
    In the new logic, all decks in 'decks' are considered active.

    Returns:
        dict: Dictionary with URLs as keys and deck data as values
    """
    meta = get_meta()
    return meta.get("decks", {})


def is_local_deck_missing(url):
    """
    Checks if the corresponding local deck for a remote deck was deleted.

    Args:
        url (str): Remote deck URL

    Returns:
        bool: True if remote deck exists but local deck doesn't
    """
    meta = get_meta()
    remote_decks = meta.get("decks", {})

    if url not in remote_decks:
        return False  # Remote deck doesn't exist

    deck_info = remote_decks[url]
    deck_id = deck_info.get("deck_id")

    if not deck_id:
        return True  # Remote deck has no local ID

    try:
        # Check if local deck exists in Anki
        if mw.col and mw.col.decks:
            deck = mw.col.decks.get(deck_id)
            return deck is None
        else:
            return True  # Collection or decks not available
    except:
        return True  # Error accessing deck = deck doesn't exist


def get_deck_naming_mode():
    """
    Gets current deck naming mode.

    Returns:
        str: Always "automatic" (fixed behavior)
    """
    return "automatic"


def set_deck_naming_mode(mode):
    """
    Sets deck naming mode.

    Args:
        mode (str): Ignored - behavior always automatic
    """
    # Kept for compatibility, does nothing
    pass


def get_create_subdecks_setting():
    """
    Checks if subdeck creation is enabled.

    Returns:
        bool: Always True (fixed behavior)
    """
    return True


def set_create_subdecks_setting(enabled):
    """
    Sets whether subdeck creation is enabled.

    Args:
        enabled (bool): Ignored - behavior always enabled
    """
    # Kept for compatibility, does nothing
    pass


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def verify_and_update_deck_info(url, local_deck_id, local_deck_name, silent=False):
    """
    Verifies and updates deck info in the configuration using the new structure.

    This function ensures that:
    1. local_deck_id is updated in the configuration
    2. local_deck_name is updated in the configuration
    3. remote_deck_name is synchronized with current URL
    4. Information matches Anki's current state

    Args:
        url (str): Remote deck URL
        local_deck_id (int): Current deck ID in Anki
        local_deck_name (str): Current local deck name in Anki
        silent (bool): If True, doesn't show notifications

    Returns:
        bool: True if there were updates, False otherwise
    """
    # Generate hash for the spreadsheet ID
    spreadsheet_id = get_deck_id(url)

    remote_decks = get_remote_decks()

    # Check if deck exists in the configuration
    if spreadsheet_id not in remote_decks:
        return False

    deck_info = remote_decks[spreadsheet_id]
    updated = False

    # Check if local_deck_id needs update
    current_local_deck_id = deck_info.get("local_deck_id")
    if current_local_deck_id != local_deck_id:
        deck_info["local_deck_id"] = local_deck_id
    # Check if local_deck_name needs update
    current_local_deck_name = deck_info.get("local_deck_name")
    if current_local_deck_name != local_deck_name:
        deck_info["local_deck_name"] = local_deck_name
        updated = True

    # Check if remote_deck_name needs update using DeckNameManager
    from .deck_manager import DeckNameManager

    current_remote_name = DeckNameManager.extract_remote_name_from_url(url)
    stored_remote_name = deck_info.get("remote_deck_name")
    if stored_remote_name != current_remote_name:
        resolved_remote_name = DeckNameManager.resolve_remote_name_conflict(
            url, current_remote_name
        )
        deck_info["remote_deck_name"] = resolved_remote_name
        
        # Also update local_deck_configurations_package_name for consistency
        deck_options_mode = get_deck_options_mode()
        if deck_options_mode == "individual":
            new_package_name = f"Sheets2Anki - {resolved_remote_name}"
            deck_info["local_deck_configurations_package_name"] = new_package_name
            add_debug_msg(f"[Sheets2Anki] Package name updated to '{new_package_name}'")
        elif deck_options_mode == "shared":
            deck_info["local_deck_configurations_package_name"] = "Sheets2Anki - Default Options"
        else:  # manual
            deck_info["local_deck_configurations_package_name"] = None
        
        updated = True
        if not silent:
            add_debug_msg(
                f"[Sheets2Anki] Remote deck name updated from '{stored_remote_name}' to '{resolved_remote_name}'"
            )

    # Save changes if there were updates
    if updated:
        save_remote_decks(remote_decks)
        return True

    return False


def get_deck_info_by_id(local_deck_id):
    """
    Gets remote deck information by local deck ID.

    Args:
        local_deck_id (int): Deck ID in Anki

    Returns:
        tuple: (url_hash, deck_info) or (None, None) if not found
    """
    remote_decks = get_remote_decks()

    for url_hash, deck_info in remote_decks.items():
        if deck_info.get("local_deck_id") == local_deck_id:
            return url_hash, deck_info

    return None, None


def detect_deck_name_changes(skip_deleted=False):
    """
    Detects changes in local deck names and updates the configuration.

    This function checks all configured remote decks and updates
    their information if the deck name was changed in Anki.

    Args:
        skip_deleted: If True, doesn't update names of deleted decks

    Returns:
        list: List of hash keys for the updated decks
    """
    from .compat import mw

    remote_decks = get_remote_decks()
    updated_hashes = []

    for url_hash, deck_info in remote_decks.items():
        local_deck_id = deck_info.get("local_deck_id")
        if not local_deck_id:
            continue

        # Get current deck from Anki
        if not mw.col or not mw.col.decks:
            continue  # Collection or decks not available

        deck = mw.col.decks.get(local_deck_id)

        # If deck was deleted and skip_deleted=True, skip
        if not deck and skip_deleted:
            continue

        # If deck exists, update name
        if deck:
            current_name = deck.get("name", "")
            saved_name = deck_info.get("local_deck_name", "")

            # Check if name changed
            if current_name and current_name != saved_name:
                # Update name in configuration
                deck_info["local_deck_name"] = current_name
                updated_hashes.append(url_hash)

    # Save changes if there were updates
    if updated_hashes:
        save_remote_decks(remote_decks)

    return updated_hashes


def get_sync_selection():
    """
    Gets persistent selection of decks for synchronization.

    Returns:
        dict: Dictionary with URLs as keys and bool as values
    """
    remote_decks = get_remote_decks()
    selection = {}

    for url, deck_info in remote_decks.items():
        # Use is_sync attribute from deck data, default True if doesn't exist
        selection[url] = deck_info.get("is_sync", True)

    return selection


def save_sync_selection(selection):
    """
    Saves the persistent deck selection for synchronization.

    Args:
        selection (dict): Dictionary with URLs as keys and bool as values
    """
    remote_decks = get_remote_decks()

    # Update is_sync attribute in each deck
    for url, is_selected in selection.items():
        if url in remote_decks:
            remote_decks[url]["is_sync"] = is_selected

    save_remote_decks(remote_decks)


def update_sync_selection(url, selected):
    """
    Updates selection for a specific deck.

    Args:
        url (str): Deck URL
        selected (bool): Whether the deck is selected
    """
    remote_decks = get_remote_decks()

    if url in remote_decks:
        remote_decks[url]["is_sync"] = selected
        save_remote_decks(remote_decks)


def clear_sync_selection():
    """
    Clears all persistent selection (sets all as unselected).
    """
    remote_decks = get_remote_decks()

    for url in remote_decks:
        remote_decks[url]["is_sync"] = False

    save_remote_decks(remote_decks)


def set_all_sync_selection(selected=True):
    """
    Sets all decks as selected or unselected.

    Args:
        selected (bool): True to select all, False to unselect all
    """
    remote_decks = get_remote_decks()

    for url in remote_decks:
        remote_decks[url]["is_sync"] = selected

    save_remote_decks(remote_decks)


def _ensure_meta_structure(meta):
    """
    Ensures that meta.json structure is correct.

    Args:
        meta (dict): Metadata to be checked

    Returns:
        dict: Metadata with corrected structure
    """
    # Ensure main keys
    if "decks" not in meta:
        meta["decks"] = {}

    # Migrate remote_decks data to decks if necessary
    if "remote_decks" in meta and meta["remote_decks"] and not meta.get("decks"):
        meta["decks"] = meta["remote_decks"]

    # Remove unnecessary old keys
    if "remote_decks" in meta:
        del meta["remote_decks"]
    if "user_preferencies" in meta:
        del meta["user_preferencies"]

    # Ensure all decks have is_sync attribute
    for url, deck_info in meta["decks"].items():
        if "is_sync" not in deck_info:
            deck_info["is_sync"] = True  # Default: selected for synchronization

    # Ensure students structure
    if "students" not in meta:
        meta["students"] = {
            "enabled_students": [],
            "student_sync_enabled": False,
        }

    return meta


# =============================================================================
# GLOBAL STUDENT MANAGEMENT FUNCTIONS
# =============================================================================


def get_global_student_config():
    """
    Gets global student configuration.

    Returns:
        dict: Student configuration with keys:
            - available_students: list of all known students
            - enabled_students: list of enabled students
            - student_sync_enabled: if student filter is active
            - auto_remove_disabled_students: if disabled students' data should be removed
            - sync_missing_students_notes: if notes without specific students should be synced
            - sync_history: detailed synchronization history per student
    """
    meta = get_meta()
    return meta.get(
        "students",
        {
            "available_students": [],
            "enabled_students": [],
            "auto_remove_disabled_students": False,
            "sync_missing_students_notes": False,
        },
    )


def save_global_student_config(
    enabled_students,
    available_students=None,
    auto_remove_disabled_students=None,
    sync_missing_students_notes=None,
):
    """
    Saves global student configuration.

    Args:
        enabled_students (list): List of students enabled for synchronization
        available_students (list): List of all known students (optional)
        auto_remove_disabled_students (bool): Whether to automatically remove disabled students' data (optional)
        sync_missing_students_notes (bool): Whether to synchronize notes without specific students (optional)
    """

    meta = get_meta()

    # Get current configuration
    current_config = meta.get("students", {})
    current_available = current_config.get("available_students", [])

    # Remove duplicates from student lists (case-sensitive)
    final_enabled = list(dict.fromkeys(enabled_students)) if enabled_students else []

    if available_students is not None:
        final_available = list(dict.fromkeys(available_students))
    else:
        # If not provided, keep current list and add enabled ones
        all_students = list(current_available) + final_enabled
        final_available = list(dict.fromkeys(all_students))

    # Determine value for auto_remove_disabled_students
    if auto_remove_disabled_students is not None:
        final_auto_remove = bool(auto_remove_disabled_students)
    else:
        final_auto_remove = current_config.get("auto_remove_disabled_students", False)

    # Determine value for sync_missing_students_notes
    if sync_missing_students_notes is not None:
        final_sync_missing = bool(sync_missing_students_notes)
    else:
        final_sync_missing = current_config.get("sync_missing_students_notes", False)

    # ⚠️ PRESERVE existing keys like sync_history
    # Instead of overwriting the whole "students" section, update only necessary keys
    if "students" not in meta:
        meta["students"] = {}
    
    meta["students"]["available_students"] = final_available
    meta["students"]["enabled_students"] = final_enabled
    meta["students"]["auto_remove_disabled_students"] = final_auto_remove
    meta["students"]["sync_missing_students_notes"] = final_sync_missing
    
    # sync_history and other keys are preserved automatically

    save_meta(meta)


def get_enabled_students():
    """
    Gets the list of students enabled for synchronization.

    Returns:
        list: List of enabled student names
    """
    config = get_global_student_config()
    return config.get("enabled_students", [])


def is_student_filter_active():
    """
    Checks if student filter is active based on enabled students list.

    Returns:
        bool: True if there are specific students selected (filter active), False otherwise
    """
    config = get_global_student_config()
    enabled_students = config.get("enabled_students", [])
    return len(enabled_students) > 0


def add_enabled_student(student_name):
    """
    Adds a student to the enabled list.

    Args:
        student_name (str): Student name to be added
    """
    config = get_global_student_config()
    enabled = set(config.get("enabled_students", []))
    enabled.add(student_name)
    save_global_student_config(list(enabled), config.get("available_students", []))


def remove_enabled_student(student_name):
    """
    Removes a student from the enabled list.

    Args:
        student_name (str): Student name to be removed
    """
    config = get_global_student_config()
    enabled = set(config.get("enabled_students", []))
    enabled.discard(student_name)
    save_global_student_config(list(enabled), config.get("available_students", []))


def is_auto_remove_disabled_students():
    """
    Checks if auto-removal of disabled students is enabled.

    Returns:
        bool: True if disabled students' data should be automatically removed
    """
    config = get_global_student_config()
    return config.get("auto_remove_disabled_students", False)


def set_auto_remove_disabled_students(enabled):
    """
    Enables or disables auto-removal of disabled students.

    Args:
        enabled (bool): Whether to automatically remove disabled students' data
    """
    config = get_global_student_config()
    save_global_student_config(
        config.get("enabled_students", []),
        config.get("available_students", []),
        enabled,
        config.get("sync_missing_students_notes", False),
    )


def is_sync_missing_students_notes():
    """
    Checks if synchronization of notes without specific students is enabled.

    Returns:
        bool: True if notes with empty STUDENTS column should be synced for [MISSING STUDENT] deck
    """
    config = get_global_student_config()
    return config.get("sync_missing_students_notes", False)


def set_sync_missing_students_notes(enabled):
    """
    Enables or disables synchronization of notes without specific students.

    Args:
        enabled (bool): Whether to synchronize notes with empty STUDENTS column
    """
    config = get_global_student_config()
    save_global_student_config(
        config.get("enabled_students", []),
        config.get("available_students", []),
        config.get("auto_remove_disabled_students", False),
        enabled,
    )


# =============================================================================
# STUDENT SYNCHRONIZATION HISTORY MANAGEMENT (NEW)
# =============================================================================

def get_student_sync_history():
    """
    Gets full student synchronization history.
    
    Returns:
        dict: History in format {
            "student_name": {
                "first_sync": timestamp,
                "last_sync": timestamp, 
                "total_syncs": count
            }
        }
    """
    meta = get_meta()
    return meta.get("students", {}).get("sync_history", {})


def update_student_sync_history(students_synced):
    """
    Updates synchronization history for specified students.
    
    This function should be called EVERY TIME a synchronization is completed
    successfully, regardless of manual note type renames.
    
    Args:
        students_synced (set): Set of students that were synchronized
    """
    meta = get_meta()
    current_time = int(time.time())
    
    # Ensure structure
    if "students" not in meta:
        meta["students"] = {}
    if "sync_history" not in meta["students"]:
        meta["students"]["sync_history"] = {}
    
    sync_history = meta["students"]["sync_history"]
    
    for student in students_synced:
        if student in sync_history:
            # Student already exists in history - update
            sync_history[student]["last_sync"] = current_time
            sync_history[student]["total_syncs"] = sync_history[student].get("total_syncs", 0) + 1
        else:
            # New student - create entry
            sync_history[student] = {
                "first_sync": current_time,
                "last_sync": current_time,
                "total_syncs": 1
            }
    
    # Save changes
    save_meta(meta)
    add_debug_msg(f"📝 HISTORY: History updated for {len(students_synced)} students: {sorted(students_synced)}")


def get_students_with_sync_history():
    """
    Returns set of all students who have ever been synchronized.
    
    This is the definitive source of truth to know which students existed,
    regardless of manual renames or other modifications.
    
    Returns:
        set: Set of students that have been synchronized
    """
    sync_history = get_student_sync_history()
    historical_students = set(sync_history.keys())
    
    try:
        from .utils import add_debug_message
        add_debug_message(f"📚 HISTORY: Found {len(historical_students)} students in history: {sorted(historical_students)}", "CLEANUP")
    except:
        add_debug_msg(f"📚 HISTORY: Found {len(historical_students)} students in history: {sorted(historical_students)}")
    
    return historical_students


def remove_student_from_sync_history(student_name):
    """
    Removes a student from synchronization history.
    
    Should be called ONLY after confirmation that the user wants
    to permanently delete all student data.
    
    Args:
        student_name (str): Student name to be removed from history
    """
    meta = get_meta()
    sync_history = meta.get("students", {}).get("sync_history", {})
    
    if student_name in sync_history:
        del sync_history[student_name]
        save_meta(meta)
        add_debug_msg(f"🗑️ HISTORY: Student '{student_name}' removed from sync history")
    else:
        add_debug_msg(f"ℹ️ HISTORY: Student '{student_name}' not found in history")


def cleanup_orphaned_sync_history():
    """
    Removes sync history entries that no longer correspond
    to real data in Anki (maintenance cleanup).
    
    Returns:
        int: Number of entries removed
    """
    if not mw or not hasattr(mw, "col") or not mw.col:
        return 0
    
    sync_history = get_student_sync_history()
    if not sync_history:
        return 0
    
    orphaned_students = []
    col = mw.col
    
    # Check each student in history
    for student in sync_history.keys():
        # Search for notes that have ID starting with this student
        student_notes = []
        try:
            # Approximate search for notes that might belong to student
            all_notes = col.find_notes("*")[:2000]  # Limit search for performance - use wildcard
            
            for note_id in all_notes:
                try:
                    note = col.get_note(note_id)
                    if "ID" in note.keys():
                        unique_id = note["ID"].strip()
                        if unique_id.startswith(f"{student}_"):
                            student_notes.append(note_id)
                            break  # Found at least one note, student still exists
                except:
                    continue
            
            # If no note found, mark as orphan
            if not student_notes:
                orphaned_students.append(student)
                
        except Exception as e:
            add_debug_msg(f"⚠️ HISTORY: Error checking student '{student}': {e}")
            continue
    
    # Remove orphans
    if orphaned_students:
        meta = get_meta()
        sync_history = meta.get("students", {}).get("sync_history", {})
        
        for student in orphaned_students:
            if student in sync_history:
                del sync_history[student]
        
        save_meta(meta)
        add_debug_msg(f"Sweep HISTORY: Removed {len(orphaned_students)} orphaned entries: {orphaned_students}")
    
    return len(orphaned_students)


def discover_all_students_from_remote_decks():
    """
    Discovers all unique students from all configured remote decks.

    Returns:
        list: List of student names found (normalized)
    """
    from .student_manager import discover_students_from_tsv_url

    all_students = set()
    remote_decks = get_remote_decks()

    add_debug_msg("🔍 DEBUG: Starting student discovery...")
    add_debug_msg(f"📋 DEBUG: Found {len(remote_decks)} remote decks for analysis")

    for i, (hash_key, deck_info) in enumerate(remote_decks.items(), 1):
        deck_name = deck_info.get("remote_deck_name", f"Deck {i}")
        url = deck_info.get("remote_deck_url")

        if not url:
            add_debug_msg(f"   ⚠️ Deck {deck_name} has no URL configured, skipping...")
            continue

        add_debug_msg(f"🔍 DEBUG: Analyzing deck {i}/{len(remote_decks)}: {deck_name}")
        add_debug_msg(f"🌐 DEBUG: URL: {url}")

        try:
            students = discover_students_from_tsv_url(url)
            add_debug_msg(f"   ✓ Found {len(students)} students: {sorted(students)}")

            # Add discovered students (case-sensitive)
            for student in students:
                if student and student.strip():
                    all_students.add(student.strip())

            add_debug_msg(f"   ✓ Added {len(students)} valid students")

        except Exception as e:
            # In case of error, continue with next deck
            add_debug_msg(f"   ❌ Error discovering students from deck {deck_name}: {e}")
            continue

    final_students = sorted(all_students)
    add_debug_msg(
        f"✅ DEBUG: Discovery completed. Total unique students: {len(final_students)}"
    )
    add_debug_msg(f"📝 DEBUG: Final list: {final_students}")

    return final_students


def update_available_students_from_discovery():
    """
    Updates available students list by discovering from all remote decks.

    Returns:
        tuple: (students_found, new_students_count)
    """
    add_debug_msg("🔄 DEBUG: Starting discovery update for available students...")

    config = get_global_student_config()
    current_available = set(config.get("available_students", []))
    add_debug_msg(
        f"📋 DEBUG: Current available students: {len(current_available)} - {sorted(current_available)}"
    )

    discovered_students = set(discover_all_students_from_remote_decks())
    add_debug_msg(
        f"🔍 DEBUG: Discovered students: {len(discovered_students)} - {sorted(discovered_students)}"
    )

    # Combine discovered students with existing ones (case-sensitive)
    all_available = current_available.union(discovered_students)
    final_available = sorted(list(all_available))

    # Count new students
    new_count = len(discovered_students - current_available)
    add_debug_msg(f"✨ DEBUG: New students found: {new_count}")
    if new_count > 0:
        new_students = sorted(discovered_students - current_available)
        add_debug_msg(f"📝 DEBUG: New students list: {new_students}")

    add_debug_msg(
        f"💾 DEBUG: Saving configuration with {len(final_available)} available students..."
    )

    # Update configuration keeping enabled students
    save_global_student_config(config.get("enabled_students", []), final_available)

    add_debug_msg("✅ DEBUG: Update completed successfully!")
    return final_available, new_count


# =============================================================================
# NOTE TYPE IDS MANAGEMENT
# =============================================================================


def add_note_type_id_to_deck(
    deck_url, note_type_id, expected_name=None, debug_messages=None
):
    """
    Adds a note type ID to deck using new hash-based structure.

    Args:
        deck_url (str): Remote deck URL
        note_type_id (int): Note type ID
        expected_name (str, optional): Expected name of the note type
        debug_messages (list, optional): List to accumulate debug messages
    """

    def add_debug_msg(message, category="CONFIG"):
        """Helper to add debug messages with timestamp."""
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] [{category}] {message}"
        if debug_messages is not None:
            debug_messages.append(formatted_msg)

    try:
        add_debug_msg("add_note_type_id_to_deck CALL:")
        add_debug_msg(f"  - URL: {deck_url}")
        add_debug_msg(f"  - ID: {note_type_id}")
        add_debug_msg(f"  - Expected name: {expected_name}")

        # Generate spreadsheet ID
        spreadsheet_id = get_deck_id(deck_url)
        add_debug_msg(f"  - Spreadsheet ID: {spreadsheet_id}")

        meta = get_meta()
        add_debug_msg(f"Meta loaded: {len(meta.get('decks', {}))} decks in config")

        if spreadsheet_id not in meta["decks"]:
            add_debug_msg(f"ERROR: Deck {spreadsheet_id} not found in configuration")
            add_debug_msg("Available decks:")
            for key in meta.get("decks", {}).keys():
                add_debug_msg(f"  - {key}")
            return

        deck_info = meta["decks"][spreadsheet_id]
        add_debug_msg(f"Deck info found: {list(deck_info.keys())}")

        # Ensure note_types structure exists
        if "note_types" not in deck_info:
            deck_info["note_types"] = {}
            add_debug_msg("Initializing empty note_types dictionary")

        note_type_id_str = str(note_type_id)

        # Add or update current note type
        if note_type_id_str not in deck_info["note_types"]:
            # Add new note type with expected name
            deck_info["note_types"][note_type_id_str] = (
                expected_name or f"Note Type {note_type_id}"
            )
            add_debug_msg(f"Note type ID {note_type_id} added to dictionary")
        else:
            # Update expected name if provided and different
            current_name = deck_info["note_types"][note_type_id_str]
            if expected_name and current_name != expected_name:
                old_name = current_name
                deck_info["note_types"][note_type_id_str] = expected_name
                add_debug_msg(
                    f"Note type ID {note_type_id} name updated from '{old_name}' to '{expected_name}'"
                )
            else:
                add_debug_msg(
                    f"Note type ID {note_type_id} already registered with correct name"
                )

        # Save changes
        save_meta(meta)
        add_debug_msg("Meta successfully saved")

        name_info = f" ({expected_name})" if expected_name else ""
        add_debug_msg(f"✅ SUCCESS: Note type ID {note_type_id}{name_info} processed")

    except Exception as e:
        add_debug_msg(f"❌ ERROR adding note type ID: {e}")
        import traceback

        error_details = traceback.format_exc()
        add_debug_msg(f"Error details: {error_details}")


def get_deck_local_id(deck_url):
    """
    Gets the local deck ID from a remote deck using new structure.

    Args:
        deck_url (str): Remote deck URL

    Returns:
        int: Local deck ID or None if not found
    """
    try:
        spreadsheet_id = get_deck_id(deck_url)

        meta = get_meta()

        if spreadsheet_id in meta.get("decks", {}):
            return meta["decks"][spreadsheet_id].get("local_deck_id")
        return None

    except Exception as e:
        add_debug_msg(f"[CONFIG] Error getting local deck ID: {e}")
        return None


def get_deck_note_type_ids(deck_url):
    """
    Gets note type IDs of a deck using new structure.

    Args:
        deck_url (str): Remote deck URL

    Returns:
        dict: {note_type_id: expected_name} dictionary
    """
    try:
        spreadsheet_id = get_deck_id(deck_url)

        meta = get_meta()

        if spreadsheet_id in meta.get("decks", {}):
            return meta["decks"][spreadsheet_id].get("note_types", {})
        return {}

    except Exception as e:
        add_debug_msg(f"[NOTE_TYPE_IDS] Error getting note type IDs: {e}")
        return {}


def remove_note_type_id_from_deck(deck_url, note_type_id):
    """
    Removes a note type ID from a deck using new structure.

    Args:
        deck_url (str): Remote deck URL
        note_type_id (int): Note type ID to be removed
    """
    try:
        spreadsheet_id = get_deck_id(deck_url)

        meta = get_meta()

        if spreadsheet_id not in meta["decks"]:
            return

        deck_info = meta["decks"][spreadsheet_id]
        note_type_id_str = str(note_type_id)

        if "note_types" in deck_info and note_type_id_str in deck_info["note_types"]:
            del deck_info["note_types"][note_type_id_str]
            save_meta(meta)
            add_debug_msg(
                f"[NOTE_TYPE_IDS] Removed note type ID {note_type_id} from deck {spreadsheet_id}"
            )

    except Exception as e:
        add_debug_msg(f"[NOTE_TYPE_IDS] Error removing note type ID: {e}")


def cleanup_invalid_note_type_ids():
    """
    Removes note type IDs that no longer exist in Anki from all decks.

    Returns:
        int: Number of IDs removed
    """
    from .compat import mw

    if not mw or not mw.col:
        return 0

    try:
        # Get all valid note types from Anki
        all_models = mw.col.models.all()
        valid_ids = {str(model["id"]) for model in all_models}

        meta = get_meta()

        removed_count = 0

        for deck_hash, deck_info in meta.get("decks", {}).items():
            if "note_types" in deck_info:
                invalid_ids = []
                for note_type_id in deck_info["note_types"].keys():
                    if note_type_id not in valid_ids:
                        invalid_ids.append(note_type_id)

                # Remove invalid IDs
                for invalid_id in invalid_ids:
                    del deck_info["note_types"][invalid_id]
                    removed_count += 1

        if removed_count > 0:
            save_meta(meta)
            add_debug_msg(f"[NOTE_TYPE_IDS] Removed {removed_count} invalid IDs")

        return removed_count

    except Exception as e:
        add_debug_msg(f"[NOTE_TYPE_IDS] Error during cleanup of invalid IDs: {e}")
        return 0


def get_all_deck_note_types():
    """
    Gets all note types from all decks.

    Returns:
        dict: {spreadsheet_id: {note_type_id: expected_name}} dictionary
    """
    try:
        meta = get_meta()

        result = {}
        for spreadsheet_id, deck_info in meta.get("decks", {}).items():
            result[spreadsheet_id] = deck_info.get("note_types", {})

        return result

    except Exception as e:
        add_debug_msg(f"[NOTE_TYPE_IDS] Error getting all note types: {e}")
        return {}


def update_note_type_names_if_needed():
    """
    Updates note type names in Anki if there are discrepancies with expected names.

    Returns:
        int: Number of renamed note types
    """
    from .compat import mw

    if not mw or not mw.col:
        return 0

    try:
        meta = get_meta()

        renamed_count = 0

        for deck_hash, deck_info in meta.get("decks", {}).items():
            note_types = deck_info.get("note_types", {})

            for note_type_id, expected_name in note_types.items():
                try:
                    note_type_id_int = int(note_type_id)
                    # Find model using more robust method
                    model = None
                    for m in mw.col.models.all():
                        if m["id"] == note_type_id_int:
                            model = m
                            break

                    if model and model.get("name") != expected_name:
                        # Name diverges - update in Anki
                        old_name = model["name"]
                        model["name"] = expected_name
                        mw.col.models.update(model)
                        renamed_count += 1
                        add_debug_msg(
                            f"[Sheets2Anki] Note type renamed: '{old_name}' -> '{expected_name}'"
                        )

                except (ValueError, TypeError) as e:
                    add_debug_msg(
                        f"[WARNING] Error processing note type ID {note_type_id}: {e}"
                    )
                    continue

        return renamed_count

    except Exception as e:
        add_debug_msg(f"[NOTE_TYPE_IDS] Error updating note type names: {e}")
        return 0


def get_deck_note_types_by_ids(deck_url):
    """
    Gets Anki note type objects based on saved IDs for a deck.

    Args:
        deck_url (str): Remote deck URL

    Returns:
        list: List of Anki note type dictionaries
    """
    from .compat import mw

    if not mw or not mw.col:
        return []

    try:
        note_types_dict = get_deck_note_type_ids(deck_url)
        note_types = []

        for note_type_id_str in note_types_dict.keys():
            try:
                note_type_id_int = int(note_type_id_str)
                # Search using more robust method
                for model in mw.col.models.all():
                    if model["id"] == note_type_id_int:
                        note_types.append(model)
                        break
                else:
                    add_debug_msg(
                        f"[NOTE_TYPE_IDS] Note type with ID {note_type_id_int} not found"
                    )
            except ValueError:
                add_debug_msg(f"[NOTE_TYPE_IDS] Invalid ID: {note_type_id_str}")
                continue

        return note_types

    except Exception as e:
        add_debug_msg(f"[NOTE_TYPE_IDS] Error getting note types by ID: {e}")
        return []


def test_note_type_id_capture():
    """
    Test function to manually capture note type IDs.
    Use this function to test the system independently of sync.
    """
    from .compat import mw

    if not mw or not mw.col:
        add_debug_msg("[TEST] Anki is not available")
        return

    add_debug_msg("[TEST] === MANUAL NOTE TYPE ID CAPTURE TEST ===")

    # List all note types
    all_models = mw.col.models.all()
    add_debug_msg(f"[TEST] Total note types in Anki: {len(all_models)}")

    sheets2anki_models = []
    for model in all_models:
        model_name = model["name"]
        add_debug_msg(f"[TEST] Note type found: '{model_name}' (ID: {model['id']})")
        if "Sheets2Anki" in model_name:
            sheets2anki_models.append(model)
            add_debug_msg(
                f"[TEST] ✅ Sheets2Anki note type: '{model_name}' (ID: {model['id']})"
            )

    if not sheets2anki_models:
        add_debug_msg("[TEST] ❌ No Sheets2Anki note types found!")
        return

    # Check if we have configured decks
    meta = get_meta()
    decks = meta.get("decks", {})
    add_debug_msg(f"[TEST] Configured decks: {len(decks)}")

    if not decks:
        add_debug_msg("[TEST] ❌ No decks configured!")
        return

    # For each configured deck, try to capture IDs
    for deck_url, deck_info in decks.items():
        add_debug_msg(f"[TEST] Processing deck: {deck_info.get('local_deck_name', 'Unknown')}")
        add_debug_msg(f"[TEST] URL: {deck_url}")

        # Simulate capture
        from .utils import get_model_suffix_from_url

        try:
            url_hash = get_model_suffix_from_url(deck_url)
            hash_pattern = f"Sheets2Anki - {url_hash} - "
            add_debug_msg(f"[TEST] Hash: {url_hash}")
            add_debug_msg(f"[TEST] Pattern: {hash_pattern}")

            matching_models = []
            for model in sheets2anki_models:
                if hash_pattern in model["name"]:
                    matching_models.append(model)
                    add_debug_msg(f"[TEST] ✅ Match: '{model['name']}'")

            if matching_models:
                add_debug_msg(f"[TEST] Adding {len(matching_models)} IDs to deck...")
                for model in matching_models:
                    add_note_type_id_to_deck(deck_url, model["id"], model["name"])
            else:
                add_debug_msg(
                    f"[TEST] ❌ No note type found for pattern '{hash_pattern}'"
                )

        except Exception as e:
            add_debug_msg(f"[TEST] Error processing deck: {e}")

    add_debug_msg("[TEST] === END OF TEST ===")

    # Show final result
    meta_final = get_meta()
    for deck_url, deck_info in meta_final.get("decks", {}).items():
        note_type_ids = deck_info.get("note_type_ids", [])
        add_debug_msg(
            f"[TEST] Deck {deck_info.get('local_deck_name', 'Unknown')}: {len(note_type_ids)} IDs saved"
        )
        if note_type_ids:
            add_debug_msg(f"[TEST]   IDs: {note_type_ids}")


def update_note_type_names_in_meta(url, new_remote_deck_name, enabled_students=None):
    """
    Updates note type names in meta.json when remote_deck_name changes.

    Args:
        url (str): Remote deck URL
        new_remote_deck_name (str): New remote deck name
        enabled_students (list, optional): List of enabled students
    """
    try:
        from .utils import get_note_type_name

        meta = get_meta()
        spreadsheet_id = get_deck_id(url)

        if "decks" not in meta or spreadsheet_id not in meta["decks"]:
            return

        deck_info = meta["decks"][spreadsheet_id]
        note_types = deck_info.get("note_types", {})

        if not note_types:
            return

        add_debug_msg(
            f"[UPDATE_META] Updating note type names for deck: {new_remote_deck_name}"
        )

        # Update each note type ID with the new expected name
        for note_type_id, old_name in note_types.items():
            # Analyze old name to extract student and type
            # IMPORTANT: deck_name may contain " - ", so parse from the END
            if old_name.startswith("Sheets2Anki - "):
                parts = old_name.split(" - ")

                if len(parts) >= 4:
                    # Format: "Sheets2Anki - remote_name - student - type"
                    # Last part is the type (Basic/Cloze)
                    note_type = parts[-1].strip()
                    # Second-to-last part is the student name
                    student = parts[-2].strip()
                    is_cloze = note_type == "Cloze"
                    is_reverse = note_type == "Reverse"

                    new_name = get_note_type_name(
                        url, new_remote_deck_name, student=student, is_cloze=is_cloze, is_reverse=is_reverse
                    )

                elif len(parts) == 3:  # Format: "Sheets2Anki - remote_name - type"
                    note_type = parts[-1].strip()
                    is_cloze = note_type == "Cloze"
                    is_reverse = note_type == "Reverse"

                    new_name = get_note_type_name(
                        url, new_remote_deck_name, student=None, is_cloze=is_cloze, is_reverse=is_reverse
                    )

                else:
                    # Unrecognized format, try to deduce
                    is_cloze = "Cloze" in old_name
                    is_reverse = "Reverse" in old_name
                    student_candidates = enabled_students or []
                    student = None

                    for candidate in student_candidates:
                        if candidate in old_name:
                            student = candidate
                            break

                    new_name = get_note_type_name(
                        url, new_remote_deck_name, student=student, is_cloze=is_cloze, is_reverse=is_reverse
                    )

                # Update if name changed
                if new_name != old_name:
                    note_types[note_type_id] = new_name
                    add_debug_msg(f"[UPDATE_META] ✅ Updated: {old_name} -> {new_name}")

        # Save changes
        save_meta(meta)
        add_debug_msg("[UPDATE_META] ✅ Meta.json updated with new note type names")

    except Exception as e:
        add_debug_msg(f"[UPDATE_META] ❌ Error updating names in meta.json: {e}")
        import traceback

        traceback.print_exc()


# =============================================================================
# DECK OPTIONS SETTINGS MANAGEMENT
# =============================================================================


def get_deck_options_mode():
    """
    Gets the current deck options configuration mode.

    Returns:
        str: "shared", "individual", or "manual"
    """
    meta = get_meta()
    config = meta.get("config", {})
    return config.get("deck_options_mode", "shared")


def set_deck_options_mode(mode):
    """
    Sets the deck options configuration mode.

    Args:
        mode (str): "shared", "individual", or "manual"
    """
    if mode not in ["shared", "individual", "manual"]:
        raise ValueError(
            f"Invalid mode: {mode}. Use 'shared', 'individual' or 'manual'"
        )

    meta = get_meta()
    if "config" not in meta:
        meta["config"] = {}

    meta["config"]["deck_options_mode"] = mode
    save_meta(meta)
    add_debug_msg(f"[DECK_OPTIONS_MODE] Mode changed to: {mode}")
    
    # Update existing deck settings to reflect the new mode
    update_deck_configurations_for_mode(mode)


def update_deck_configurations_for_mode(mode):
    """
    Updates existing deck settings when the options mode is changed.
    
    Args:
        mode (str): The new mode ("shared", "individual", or "manual")
    """
    meta = get_meta()
    remote_decks = meta.get("decks", {})
    
    for deck_hash, deck_info in remote_decks.items():
        remote_deck_name = deck_info.get("remote_deck_name", "UnknownDeck")
        
        if mode == "individual":
            options_group_name = f"Sheets2Anki - {remote_deck_name}"
        elif mode == "shared":
            options_group_name = "Sheets2Anki - Default Options"
        else:  # manual
            options_group_name = None
            
        deck_info["local_deck_configurations_package_name"] = options_group_name
    
    save_meta(meta)
    add_debug_msg(f"[DECK_CONFIG_UPDATE] Updated {len(remote_decks)} decks' configurations to '{mode}' mode")


def get_deck_configurations_package_name(url):
    """
    Gets the configured options group name for a specific deck.
    
    Args:
        url (str): Remote deck URL
        
    Returns:
        str or None: Options group name or None if manual mode
    """
    remote_decks = get_remote_decks()
    spreadsheet_id = get_deck_id(url)
    deck_info = remote_decks.get(spreadsheet_id)
    
    if deck_info:
        return deck_info.get("local_deck_configurations_package_name")
    return None


def set_deck_configurations_package_name(url, package_name):
    """
    Sets the options group name for a specific deck.
    
    Args:
        url (str): Remote deck URL
        package_name (str or None): Options group name
    """
    remote_decks = get_remote_decks()
    spreadsheet_id = get_deck_id(url)
    deck_info = remote_decks.get(spreadsheet_id)
    
    if deck_info:
        deck_info["local_deck_configurations_package_name"] = package_name
        add_remote_deck(url, deck_info)
        add_debug_msg(f"[DECK_CONFIG] Options group '{package_name}' defined for deck {deck_info.get('remote_deck_name', 'Unknown')}")
    else:
        add_debug_msg(f"[DECK_CONFIG] Deck not found for URL: {url}")


def ensure_deck_configurations_consistency():
    """
    Ensures that all decks have local_deck_configurations_package_name setting
    based on the current mode and that it's consistent with remote_deck_name.
    """
    current_mode = get_deck_options_mode()
    meta = get_meta()
    remote_decks = meta.get("decks", {})
    
    added_count = 0
    fixed_count = 0
    
    for deck_hash, deck_info in remote_decks.items():
        remote_deck_name = deck_info.get("remote_deck_name", "UnknownDeck")
        current_package_name = deck_info.get("local_deck_configurations_package_name")
        
        # Calculate what the correct name should be
        if current_mode == "individual":
            expected_package_name = f"Sheets2Anki - {remote_deck_name}"
        elif current_mode == "shared":
            expected_package_name = "Sheets2Anki - Default Options"
        else:  # manual
            expected_package_name = None
        
        # If configuration doesn't exist, add it
        if "local_deck_configurations_package_name" not in deck_info:
            deck_info["local_deck_configurations_package_name"] = expected_package_name
            added_count += 1
        # If it exists but is inconsistent, fix it
        elif current_package_name != expected_package_name:
            deck_info["local_deck_configurations_package_name"] = expected_package_name
            fixed_count += 1
    
    total_changes = added_count + fixed_count
    if total_changes > 0:
        save_meta(meta)
        if added_count > 0:
            add_debug_msg(f"[DECK_CONFIG_CONSISTENCY] Added local_deck_configurations_package_name configuration to {added_count} decks")
        if fixed_count > 0:
            add_debug_msg(f"[DECK_CONFIG_CONSISTENCY] Fixed inconsistencies in {fixed_count} decks")
    
    return total_changes


# =============================================================================
# TIMER POSITION SETTINGS
# =============================================================================


def get_timer_position():
    """
    Gets the current timer position setting.

    Returns:
        str: "top_middle", "between_sections", or "hidden"
    """
    meta = get_meta()
    config = meta.get("config", {})
    return config.get("timer_position", "between_sections")


def set_timer_position(position):
    """
    Sets the timer position setting.

    Args:
        position (str): "top_middle", "between_sections", or "hidden"
    """
    valid_positions = ["top_middle", "between_sections", "hidden"]
    if position not in valid_positions:
        raise ValueError(
            f"Invalid position: {position}. Use one of: {valid_positions}"
        )

    meta = get_meta()
    if "config" not in meta:
        meta["config"] = {}

    meta["config"]["timer_position"] = position
    save_meta(meta)
    add_debug_msg(f"[TIMER_POSITION] Timer position changed to: {position}")


# =============================================================================
# ANKIWEB SYNCHRONIZATION SETTINGS MANAGEMENT
# =============================================================================


def get_ankiweb_sync_mode():
    """
    Gets the current automatic AnkiWeb synchronization mode.

    Returns:
        str: "none" (do not synchronize), "sync" (normal synchronization)
    """
    meta = get_meta()
    config = meta.get("config", {})
    return config.get("ankiweb_sync_mode", "none")


def set_ankiweb_sync_mode(mode):
    """
    Sets the automatic AnkiWeb synchronization mode.

    Args:
        mode (str): "none" or "sync"
    """
    if mode not in ["none", "sync"]:
        raise ValueError(f"Invalid mode: {mode}. Use 'none' or 'sync'")

    meta = get_meta()
    if "config" not in meta:
        meta["config"] = {}

    meta["config"]["ankiweb_sync_mode"] = mode
    save_meta(meta)
    add_debug_msg(f"[ANKIWEB_SYNC_MODE] Mode changed to: {mode}")








def set_ankiweb_sync_notifications(enabled):
    """
    Enables or disables AnkiWeb sync notifications.

    Args:
        enabled (bool): True to enable, False to disable
    """
    meta = get_meta()
    if "config" not in meta:
        meta["config"] = {}

    meta["config"]["show_ankiweb_sync_notifications"] = bool(enabled)
    save_meta(meta)
    add_debug_msg(
        f"[ANKIWEB_SYNC_NOTIFICATIONS] Notifications {'enabled' if enabled else 'disabled'}"
    )


def set_ankiweb_sync_config(mode):
    """
    Sets all AnkiWeb synchronization configuration at once.

    Args:
        mode (str): "none" or "sync"
    """
    # Validation
    if mode not in ["none", "sync"]:
        raise ValueError(f"Invalid mode: {mode}")

    meta = get_meta()
    if "config" not in meta:
        meta["config"] = {}

    meta["config"]["ankiweb_sync_mode"] = mode
    # Timeout setting removed
    # Notification setting removed (always enabled)

    save_meta(meta)
    add_debug_msg(
        f"[ANKIWEB_CONFIG] Updated: mode={mode}"
    )


def fix_note_type_names_consistency(url, correct_remote_name):
    """
    Fixes inconsistencies in note_type names.

    This function detects and fixes note_types that have names inconsistent
    with the current remote_deck_name, such as duplications or incorrect suffixes.

    Args:
        url (str): Remote deck URL
        correct_remote_name (str): Correct remote name to be used

    Returns:
        int: Number of fixed note_types
    """
    try:
        from .utils import get_note_type_name

        meta = get_meta()
        spreadsheet_id = get_deck_id(url)

        if "decks" not in meta or spreadsheet_id not in meta["decks"]:
            return 0

        deck_info = meta["decks"][spreadsheet_id]
        note_types = deck_info.get("note_types", {})

        if not note_types:
            return 0

        def fix_note_type_name(old_name):
            """Fixes an inconsistent note_type name."""
            if not old_name.startswith("Sheets2Anki - "):
                return old_name  # Not a system note_type

            parts = old_name.split(" - ")
            if len(parts) < 3:
                return old_name  # Unrecognized format

            # Extract information from old name
            # IMPORTANT: deck_name may contain " - ", so parse from the END
            if len(parts) >= 4:  # Format: "Sheets2Anki - remote_name - student - type"
                # Last part is the type (Basic/Cloze)
                note_type = parts[-1].strip()
                # Second-to-last part is the student name
                student = parts[-2].strip()
                is_cloze = note_type == "Cloze"
                is_reverse = note_type == "Reverse"

                return get_note_type_name(
                    url, correct_remote_name, student=student, is_cloze=is_cloze, is_reverse=is_reverse
                )

            elif len(parts) == 3:  # Format: "Sheets2Anki - remote_name - type"
                note_type = parts[-1].strip()
                is_cloze = note_type == "Cloze"
                is_reverse = note_type == "Reverse"

                return get_note_type_name(
                    url, correct_remote_name, student=None, is_cloze=is_cloze, is_reverse=is_reverse
                )

            return old_name  # Could not fix

        fixed_count = 0

        # Check and fix each note_type
        for note_type_id, old_name in note_types.items():
            corrected_name = fix_note_type_name(old_name)

            if corrected_name != old_name:
                note_types[note_type_id] = corrected_name
                fixed_count += 1
                add_debug_msg(
                    f"[NOTE_TYPE_FIX] ✅ Fixed {note_type_id}: '{old_name}' -> '{corrected_name}'"
                )

        # Save changes if there were fixes
        if fixed_count > 0:
            save_meta(meta)
            add_debug_msg(f"[NOTE_TYPE_FIX] {fixed_count} note_types fixed and saved")

        return fixed_count

    except Exception as e:
        add_debug_msg(f"[NOTE_TYPE_FIX] Error in consistency fix: {e}")
        return 0


def sync_note_type_names_robustly(url, correct_remote_name, enabled_students):
    """
    Robust note_types synchronization: recreates names, detects changes,
    renames in Anki and migrates notes if necessary.

    This is the full implementation of the desired logic:
    1. At each synchronization: Recreates note_type names following the correct pattern
    2. Detects changes: Compares old vs. recreated string
    3. Renames in Anki: Updates physical note type name in Anki
    4. Checks notes: Ensures notes are in the correct note type

    Args:
        url (str): Remote deck URL
        correct_remote_name (str): Current correct remote name
        enabled_students (list): Enabled students list

    Returns:
        dict: Sync result with counters
    """
    try:
        from aqt import mw

        from .utils import get_note_type_name

        if not mw or not mw.col:
            add_debug_msg("[NOTE_TYPE_SYNC] Anki is not available")
            return {"updated_count": 0, "renamed_in_anki": 0, "updated_in_meta": 0}

        meta = get_meta()
        spreadsheet_id = get_deck_id(url)

        if "decks" not in meta or spreadsheet_id not in meta["decks"]:
            add_debug_msg(f"[NOTE_TYPE_SYNC] Deck {spreadsheet_id} not found in meta.json")
            return {"updated_count": 0, "renamed_in_anki": 0, "updated_in_meta": 0}

        deck_info = meta["decks"][spreadsheet_id]
        note_types = deck_info.get("note_types", {})

        if not note_types:
            add_debug_msg("[NOTE_TYPE_SYNC] No note_type found")
            return {"updated_count": 0, "renamed_in_anki": 0, "updated_in_meta": 0}

        def extract_student_and_type_from_name(old_name):
            """Extracts student and type from old name."""
            if not old_name.startswith("Sheets2Anki - "):
                return None, None, False, False

            parts = old_name.split(" - ")
            # IMPORTANT: deck_name may contain " - ", so parse from the END
            if len(parts) >= 4:  # "Sheets2Anki - remote_name - student - type"
                # Last part is the type (Basic/Cloze)
                note_type = parts[-1].strip()
                # Second-to-last part is the student name
                student = parts[-2].strip()
                is_cloze = note_type == "Cloze"
                is_reverse = note_type == "Reverse"
                return student, note_type, is_cloze, is_reverse
            elif len(parts) == 3:  # "Sheets2Anki - remote_name - type"
                note_type = parts[-1].strip()
                is_cloze = note_type == "Cloze"
                is_reverse = note_type == "Reverse"
                return None, note_type, is_cloze, is_reverse

            return None, None, False, False

        result = {
            "updated_count": 0,
            "renamed_in_anki": 0,
            "updated_in_meta": 0,
            "notes_migrated": 0,
        }

        add_debug_msg(
            f"[NOTE_TYPE_SYNC] Starting robust synchronization for {len(note_types)} note_types"
        )

        # Process each note_type
        for note_type_id, old_name in note_types.items():
            try:
                note_type_id_int = int(note_type_id)

                # 1. RECREATE: Generate expected name based on correct pattern
                student, note_type, is_cloze, is_reverse = extract_student_and_type_from_name(
                    old_name
                )

                if student is None and note_type is None:
                    add_debug_msg(
                        f"[NOTE_TYPE_SYNC] Unrecognized format for {note_type_id}: '{old_name}'"
                    )
                    continue

                expected_name = get_note_type_name(
                    url, correct_remote_name, student=student, is_cloze=is_cloze, is_reverse=is_reverse
                )

                # 2. DETECT: Compare old vs. recreated name
                if expected_name == old_name:
                    add_debug_msg(
                        f"[NOTE_TYPE_SYNC] ✅ {note_type_id} is already correct: '{old_name}'"
                    )
                    continue

                add_debug_msg(f"[NOTE_TYPE_SYNC] 🔄 {note_type_id} needs to be updated:")
                add_debug_msg(f"[NOTE_TYPE_SYNC]    Old:      '{old_name}'")
                add_debug_msg(f"[NOTE_TYPE_SYNC]    Expected: '{expected_name}'")

                # 3. RENAME IN ANKI: Update physical note type name
                from anki.models import NotetypeId

                note_type_obj = mw.col.models.get(NotetypeId(note_type_id_int))
                if note_type_obj:
                    old_anki_name = note_type_obj.get("name", "")
                    note_type_obj["name"] = expected_name
                    mw.col.models.save(note_type_obj)

                    add_debug_msg(
                        f"[NOTE_TYPE_SYNC] ✅ Renamed in Anki: '{old_anki_name}' -> '{expected_name}'"
                    )
                    result["renamed_in_anki"] += 1
                else:
                    add_debug_msg(
                        f"[NOTE_TYPE_SYNC] ⚠️ Note type {note_type_id} not found in Anki"
                    )

                # 4. UPDATE META.JSON: Update name in configuration
                note_types[note_type_id] = expected_name
                result["updated_in_meta"] += 1

                # 5. CHECK NOTES: Ensure notes are in the correct note type
                # (Normally notes automatically follow note_type in Anki)

                result["updated_count"] += 1

            except Exception as e:
                add_debug_msg(f"[NOTE_TYPE_SYNC] ❌ Error processing {note_type_id}: {e}")
                continue

        # Save meta.json changes if there were updates
        if result["updated_in_meta"] > 0:
            save_meta(meta)
            add_debug_msg(
                f"[NOTE_TYPE_SYNC] ✅ Meta.json saved with {result['updated_in_meta']} updates"
            )

        # Save Anki changes
        if result["renamed_in_anki"] > 0:
            mw.col.save()
            add_debug_msg(
                f"[NOTE_TYPE_SYNC] ✅ Anki saved with {result['renamed_in_anki']} note_types renamed"
            )

        return result

    except Exception as e:
        add_debug_msg(f"[NOTE_TYPE_SYNC] ❌ General error in robust synchronization: {e}")
        import traceback

        add_debug_msg(f"[NOTE_TYPE_SYNC] Traceback: {traceback.format_exc()}")
        return {"updated_count": 0, "renamed_in_anki": 0, "updated_in_meta": 0}


def fix_missing_created_at_fields():
    """
    Fixes decks that do not have 'created_at' key by adding a default timestamp.
    This function is useful for fixing inconsistencies in existing configurations.
    
    Returns:
        dict: Report with the number of fixed decks
    """
    import time
    
    try:
        remote_decks = get_remote_decks()
        corrected_count = 0
        
        # Default timestamp for decks that do not have created_at
        # Use a timestamp that indicates it's a later fix
        default_timestamp = int(time.time())
        
        for deck_hash, deck_info in remote_decks.items():
            if "created_at" not in deck_info:
                deck_info["created_at"] = default_timestamp
                corrected_count += 1
                add_debug_msg(f"[CONFIG_FIX] Added 'created_at' for deck: {deck_info.get('remote_deck_name', 'Name not defined')}")
        
        if corrected_count > 0:
            save_remote_decks(remote_decks)
            add_debug_msg(f"[CONFIG_FIX] ✅ Fixed {corrected_count} decks without 'created_at'")
        else:
            add_debug_msg("[CONFIG_FIX] ✅ All decks already have 'created_at'")
        
        return {
            "corrected_count": corrected_count,
            "total_decks": len(remote_decks),
            "success": True
        }
        
    except Exception as e:
        add_debug_msg(f"[CONFIG_FIX] ❌ Error fixing 'created_at': {e}")
        return {
            "corrected_count": 0,
            "total_decks": 0,
            "success": False,
            "error": str(e)
        }


# =============================================================================
# AUTOMATIC BACKUP CONFIGURATION FUNCTIONS
# =============================================================================

def get_auto_backup_config():
    """
    Gets automatic backup settings.
    
    Returns:
        dict: Automatic backup settings including:
            - enabled: Whether auto-backup is enabled
            - directory: Directory to save backups
            - max_files: Maximum number of backup files to keep
            - type: Backup type ('simple' for config only, 'complete' for full backup)
    """
    meta = get_meta()
    config = meta.get("config", {})
    
    return {
        "enabled": config.get("auto_backup_enabled", True),
        "directory": config.get("auto_backup_directory", ""),
        "max_files": config.get("auto_backup_max_files", 50),
        "type": config.get("auto_backup_type", "simple")  # 'simple' or 'complete'
    }


def set_auto_backup_config(enabled=None, directory=None, max_files=None, backup_type=None):
    """
    Sets automatic backup settings.
    
    Args:
        enabled (bool, optional): Enable automatic backup
        directory (str, optional): Directory to save backups
        max_files (int, optional): Maximum files to keep
        backup_type (str, optional): Backup type ('simple' or 'complete')
    
    Returns:
        bool: True if successfully saved
    """
    try:
        meta = get_meta()
        config = meta.get("config", {})
        
        if enabled is not None:
            config["auto_backup_enabled"] = enabled
        if directory is not None:
            config["auto_backup_directory"] = directory
        if max_files is not None:
            config["auto_backup_max_files"] = max_files
        if backup_type is not None:
            if backup_type not in ["simple", "complete"]:
                add_debug_msg(f"[AUTO_BACKUP] Invalid backup type: {backup_type}. Using 'simple'.")
                backup_type = "simple"
            config["auto_backup_type"] = backup_type
        
        meta["config"] = config
        save_meta(meta)
        
        add_debug_msg(f"[AUTO_BACKUP] Settings updated: enabled={enabled}, directory={directory}, max_files={max_files}, type={backup_type}")
        return True
        
    except Exception as e:
        add_debug_msg(f"[AUTO_BACKUP] Error saving settings: {e}")  
        return False


def get_auto_backup_directory():
    """
    Gets the configured directory for automatic backup.
    If not configured, returns a default directory.
    
    Returns:
        str: Automatic backup directory path
    """
    import os
    from pathlib import Path
    
    config = get_auto_backup_config()
    directory = config.get("directory", "")
    
    # If not configured, use default directory
    if not directory:
        # Use user/Documents/Sheets2Anki/AutoBackups directory
        user_home = Path.home()
        default_dir = user_home / "Documents" / "Sheets2Anki" / "AutoBackups"
        directory = str(default_dir)
    
    # Create directory if it doesn't exist
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        add_debug_msg(f"[AUTO_BACKUP] Error creating directory {directory}: {e}")
        # Fallback to temporary directory
        import tempfile
        directory = tempfile.gettempdir()
    
    return directory


# =============================================================================
# AI HELP CONFIGURATION SETTINGS
# =============================================================================

# Default prompt template for AI Help
AI_HELP_PROMPTS = {
    "english": """I'm studying with flashcards and need help understanding this one better.

Here is the card content:
{card_content}

Please help me understand:
1. What is this card trying to teach me?
2. Contextualized explanation: explain the card's information using examples and real-life situations where that information applies.
3. Why is this information important?
4. How can I better remember this concept?

Keep your explanation clear and concise.""",
    "portuguese_br": """Estou estudando com flashcards e preciso de ajuda para entender este cartão melhor.

Aqui está o conteúdo do cartão:
{card_content}

Por favor, ajude-me a entender:
1. O que este cartão está tentando me ensinar?
2. Explicando de forma contextualizada: explique a informação do cartão usando exemplos e situações reais onde aquela informação se aplica.
3. Por que esta informação é importante?
4. Como posso me lembrar melhor deste conceito?

Mantenha sua explicação clara e concisa.""",
    "spanish_latam": """Estoy estudiando con tarjetas de memoria y necesito ayuda para entender esta tarjeta mejor.

Aquí está el contenido de la tarjeta:
{card_content}

Por favor ayúdame a entender:
1. ¿Qué intenta enseñarme esta tarjeta?
2. Explicación contextualizada: explique la información de la tarjeta usando ejemplos y situaciones reales donde esa información se aplica.
3. ¿Por qué es importante esta información?
4. ¿Cómo puedo recordar mejor este concepto?

Mantén tu explicación clara y concisa."""
}

# Default prompt template for AI Help (English)
DEFAULT_AI_HELP_PROMPT = AI_HELP_PROMPTS["english"]


def get_ai_help_config():
    """
    Gets AI Help configuration settings.
    
    Returns:
        dict: AI Help settings including:
            - enabled: Whether AI Help is enabled
            - service: Selected service (gemini, claude, openai)
            - model: Selected model for the service
            - api_key: API key for the service
            - prompt: Custom prompt template
            - mobile_enabled: Whether to embed API key for mobile support
    """
    meta = get_meta()
    config = meta.get("config", {})
    
    return {
        "enabled": config.get("ai_help_enabled", False),
        "service": config.get("ai_help_service", "gemini"),
        "model": config.get("ai_help_model", ""),
        "api_key": config.get("ai_help_api_key", ""),
        "prompt": config.get("ai_help_prompt", DEFAULT_AI_HELP_PROMPT),
        "mobile_enabled": config.get("ai_help_mobile_enabled", False),
        "language": config.get("ai_help_language", "english"),
    }


def set_ai_help_config(enabled=None, service=None, model=None, api_key=None, prompt=None, mobile_enabled=None, language=None):
    """
    Sets AI Help configuration settings.
    
    Args:
        enabled (bool, optional): Whether AI Help is enabled
        service (str, optional): Selected service (gemini, claude, openai)
        model (str, optional): Selected model for the service
        api_key (str, optional): API key for the service
        prompt (str, optional): Custom prompt template
        mobile_enabled (bool, optional): Whether to embed API key for mobile support
    
    Returns:
        bool: True if settings were saved successfully
    """
    valid_services = ["gemini", "claude", "openai"]
    
    try:
        meta = get_meta()
        config = meta.get("config", {})
        
        if enabled is not None:
            config["ai_help_enabled"] = bool(enabled)
        
        if service is not None:
            if service not in valid_services:
                add_debug_msg(f"[AI_HELP] Invalid service: {service}. Using 'gemini'.")
                service = "gemini"
            config["ai_help_service"] = service
        
        if model is not None:
            config["ai_help_model"] = str(model)
        
        if api_key is not None:
            config["ai_help_api_key"] = str(api_key)
        
        if prompt is not None:
            config["ai_help_prompt"] = str(prompt)
        
        if mobile_enabled is not None:
            config["ai_help_mobile_enabled"] = bool(mobile_enabled)
            
        if language is not None:
            config["ai_help_language"] = str(language)
        
        meta["config"] = config
        save_meta(meta)
        
        add_debug_msg(f"[AI_HELP] Settings updated: enabled={enabled}, service={service}, model={model}, mobile={mobile_enabled}, language={language}")
        return True
        
    except Exception as e:
        add_debug_msg(f"[AI_HELP] Error saving settings: {e}")
        return False


def get_ai_help_enabled():
    """
    Gets whether AI Help is enabled.
    
    Returns:
        bool: True if AI Help is enabled
    """
    return get_ai_help_config().get("enabled", False)


def set_ai_help_enabled(enabled):
    """
    Sets whether AI Help is enabled.
    
    Args:
        enabled (bool): True to enable AI Help
    """
    set_ai_help_config(enabled=enabled)


def get_ai_help_service():
    """
    Gets the selected AI service.
    
    Returns:
        str: Service name (gemini, claude, openai)
    """
    return get_ai_help_config().get("service", "gemini")


def set_ai_help_service(service):
    """
    Sets the AI service.
    
    Args:
        service (str): Service name (gemini, claude, openai)
    """
    set_ai_help_config(service=service)


def get_ai_help_model():
    """
    Gets the selected AI model.
    
    Returns:
        str: Model name
    """
    return get_ai_help_config().get("model", "")


def set_ai_help_model(model):
    """
    Sets the AI model.
    
    Args:
        model (str): Model name
    """
    set_ai_help_config(model=model)


def get_ai_help_api_key():
    """
    Gets the API key for the AI service.
    
    Returns:
        str: API key
    """
    return get_ai_help_config().get("api_key", "")


def set_ai_help_api_key(api_key):
    """
    Sets the API key for the AI service.
    
    Args:
        api_key (str): API key
    """
    set_ai_help_config(api_key=api_key)


def get_ai_help_prompt():
    """
    Gets the custom prompt template.
    
    Returns:
        str: Prompt template
    """
    return get_ai_help_config().get("prompt", DEFAULT_AI_HELP_PROMPT)


def set_ai_help_prompt(prompt):
    """
    Sets the custom prompt template.
    
    Args:
        prompt (str): Prompt template
    """
    set_ai_help_config(prompt=prompt)


def reset_ai_help_prompt():
    """
    Resets the prompt template to the default.
    """
    set_ai_help_config(prompt=DEFAULT_AI_HELP_PROMPT)


# =============================================================================
# DEBUG LOG CONFIGURATION
# =============================================================================

def should_accumulate_logs():
    """Checks if logs should be accumulated over time."""
    meta = get_meta()
    return meta.get("config", {}).get("accumulate_logs", True)


def set_accumulate_logs(enabled):
    """Sets whether logs should be accumulated over time."""
    meta = get_meta()
    if "config" not in meta:
        meta["config"] = {}
    meta["config"]["accumulate_logs"] = enabled
    save_meta(meta)
