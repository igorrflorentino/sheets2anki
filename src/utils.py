"""
Utility functions for the Sheets2Anki addon.

This module contains auxiliary functions used in
different parts of the project.
"""

import hashlib
import re
from datetime import datetime
from typing import List

try:
    from .compat import mw
    from .templates_and_definitions import DEFAULT_PARENT_DECK_NAME
except ImportError:
    # For independent tests
    from compat import mw
    from templates_and_definitions import DEFAULT_PARENT_DECK_NAME


def safe_find_cards(search_query):
    """
    Performs a safe card search, escaping problematic characters.
    
    Args:
        search_query (str): Search query
        
    Returns:
        list: List of IDs of found cards
    """
    try:
        if not mw or not mw.col:
            return []
        
        # Check if query is empty
        if not search_query or not search_query.strip():
            return []
        
        return mw.col.find_cards(search_query)
    except Exception:
        return []


def safe_find_cards_by_deck(deck_name):
    """
    Searches for cards by deck name safely.
    
    Args:
        deck_name (str): Deck name
        
    Returns:
        list: List of IDs of found cards
    """
    try:
        if not deck_name or not deck_name.strip():
            return []
        
        # Escape double quotes in deck name
        escaped_deck_name = deck_name.replace('"', '\\"')
        search_query = f'deck:"{escaped_deck_name}"'
        
        return safe_find_cards(search_query)
    except Exception as e:
        add_debug_message(f"Error searching by deck '{deck_name}': {e}", "SEARCH_ERROR")
        return []


def extract_publication_key_from_url(url):
    """
    Extracts a publication key or spreadsheet ID from a Google Sheets URL.
    Handles both published and edit URLs.

    Args:
        url (str): Google Sheets URL

    Returns:
        str: Extraction result or None
    """
    if not url:
        return None

    # Pattern for published URLs
    pub_pattern = r"/spreadsheets/d/e/([^/]+)/"
    pub_match = re.search(pub_pattern, url)
    if pub_match:
        return pub_match.group(1)

    # Pattern for edit URLs
    edit_pattern = r"/spreadsheets/d/([a-zA-Z0-9-_]+)"
    edit_match = re.search(edit_pattern, url)
    if edit_match:
        return edit_match.group(1)

    return None


def extract_spreadsheet_id_from_url(url):
    """
    Extracts the spreadsheet ID from a Google Sheets edit URL.

    Args:
        url (str): Google Sheets edit URL

    Returns:
        str: Spreadsheet ID or None if not found

    Examples:
        >>> extract_spreadsheet_id_from_url("https://docs.google.com/spreadsheets/d/1N-Va4ZzLUJBsD6wBaOkoeFTE6EnbZdaP/edit?usp=sharing")
        "1N-Va4ZzLUJBsD6wBaOkoeFTE6EnbZdaP"
    """
    if not url:
        return None

    # Extract spreadsheet ID from edit URLs (ID between /d/ and /edit)
    edit_pattern = r"/spreadsheets/d/([a-zA-Z0-9-_]+)/edit"
    match = re.search(edit_pattern, url)
    
    if match:
        return match.group(1)

    return None


def get_publication_key_hash(url):
    """
    Generates a hash for a publication key or spreadsheet ID.
    Used for compatibility in tests and some metadata.

    Args:
        url (str): Google Sheets URL

    Returns:
        str: 8-character hash
    """
    if not url:
        return ""
    
    # Try to extract ID, otherwise use full URL
    identifier = extract_spreadsheet_id_from_url(url) or url
    return hashlib.md5(identifier.encode()).hexdigest()[:8]


def get_spreadsheet_id_from_url(url):
    """
    Extracts the spreadsheet ID from a Google Sheets edit URL.
    This function replaces get_publication_key_hash to work only with actual IDs.

    Args:
        url (str): Google Sheets edit URL

    Returns:
        str: Spreadsheet ID (used directly as identifier)

    Raises:
        ValueError: If URL is not a valid Google Sheets edit URL
    """
    spreadsheet_id = extract_spreadsheet_id_from_url(url)
    
    if not spreadsheet_id:
        raise ValueError(
            "URL must be a valid Google Sheets edit URL in the format:\n"
            "https://docs.google.com/spreadsheets/d/{ID}/edit?usp=sharing"
        )
    
    return spreadsheet_id


def update_note_type_names_for_deck_rename(
    url, old_remote_name, new_remote_name, debug_messages=None
):
    """
    Updates only the note type name strings in meta.json when the remote_deck_name changes.
    Synchronization with Anki will be done later by the sync_note_type_names_with_config function.

    Args:
        url (str): Remote deck URL
        old_remote_name (str): Old remote name
        new_remote_name (str): New remote name
        debug_messages (list, optional): List for debug messages

    Returns:
        int: Number of updated note types
    """
    from .config_manager import get_deck_id
    from .config_manager import get_deck_note_type_ids
    from .config_manager import get_meta
    from .config_manager import save_meta

    def add_debug_msg(message, category="NOTE_TYPE_RENAME"):
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] [{category}] {message}"
        if debug_messages is not None:
            debug_messages.append(formatted_msg)

    try:
        add_debug_msg(
            f"Updating note type strings: '{old_remote_name}' → '{new_remote_name}'"
        )

        # Get current note types
        note_types_config = get_deck_note_type_ids(url)
        updated_count = 0

        if not note_types_config:
            add_debug_msg("No note types to update")
            return 0

        # Update only name strings
        updated_note_types = {}

        for note_type_id_str, current_name in note_types_config.items():
            if old_remote_name and old_remote_name in current_name:
                # Replace old remote name with new one in string
                new_name = current_name.replace(old_remote_name, new_remote_name)
                updated_note_types[note_type_id_str] = new_name
                add_debug_msg(
                    f"Note type ID {note_type_id_str}: '{current_name}' → '{new_name}'"
                )
                updated_count += 1
            else:
                # Keep current name
                updated_note_types[note_type_id_str] = current_name

        # Save to meta.json only if changes occurred
        if updated_count > 0:
            try:
                meta = get_meta()
                spreadsheet_id = get_deck_id(url)

                if "decks" in meta and spreadsheet_id in meta["decks"]:
                    meta["decks"][spreadsheet_id]["note_types"] = updated_note_types
                    save_meta(meta)
                    add_debug_msg(
                        f"✅ Meta.json updated: {updated_count} note type strings updated"
                    )

            except Exception as meta_error:
                add_debug_msg(f"❌ Error updating meta.json: {meta_error}")

        add_debug_msg(
            f"✅ {updated_count} note type strings updated in meta.json"
        )
        return updated_count

    except Exception as e:
        add_debug_msg(f"❌ ERROR updating note type strings: {e}")
        return 0


def sync_note_type_names_with_config(col, deck_url, debug_messages=None):
    """
    Synchronizes Anki note type names with meta.json configurations.
    This function uses note_types as the source of truth for names.

    Args:
        col: Anki Collection
        deck_url (str): Remote deck URL
        debug_messages (list, optional): List for debug messages

    Returns:
        dict: Synchronization statistics
    """
    from .config_manager import get_deck_note_type_ids

    def add_debug_msg(message, category="NOTE_TYPE_SYNC"):
        """Helper to add debug messages with timestamp."""
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] [{category}] {message}"
        if debug_messages is not None:
            debug_messages.append(formatted_msg)

    stats = {
        "total_note_types": 0,
        "synced_note_types": 0,
        "unchanged_note_types": 0,
        "error_note_types": 0,
        "errors": [],
    }

    try:
        add_debug_msg("🔄 STARTING note type synchronization...")

        # Get configured note types
        note_types_config = get_deck_note_type_ids(deck_url)
        stats["total_note_types"] = len(note_types_config)

        if not note_types_config:
            add_debug_msg("⚠️ No note types configured to synchronize")
            return stats

        add_debug_msg(
            f"📋 Synchronizing {stats['total_note_types']} configured note types"
        )

        # List all configured note types first
        for note_type_id_str, expected_name in note_types_config.items():
            add_debug_msg(f"  - ID {note_type_id_str}: '{expected_name}'")

        # Now process each one
        for note_type_id_str, expected_name in note_types_config.items():
            try:
                note_type_id = int(note_type_id_str)

                add_debug_msg(f"🔍 Processing note type ID {note_type_id}...")

                # Find note type in Anki
                from anki.models import NotetypeId
                note_type = col.models.get(NotetypeId(note_type_id))
                if not note_type:
                    add_debug_msg(f"❌ Note type ID {note_type_id} does not exist in Anki")
                    stats["error_note_types"] += 1
                    continue

                current_name = note_type.get("name", "")
                add_debug_msg(f"📝 Note type ID {note_type_id}:")
                add_debug_msg(f"    Current name in Anki: '{current_name}'")
                add_debug_msg(f"    Expected name (config): '{expected_name}'")

                # ALWAYS try to update to ensure synchronization
                if current_name != expected_name:
                    add_debug_message(
                        f"🔄 UPDATING note type from '{current_name}' to '{expected_name}'"
                    )

                    # Update note type name in Anki
                    note_type["name"] = expected_name
                    col.models.save(note_type)

                    # Force collection save to ensure immediate persistence
                    col.save()
                    add_debug_msg("💾 Collection saved to ensure persistence")

                    # Verify if it was actually updated
                    updated_note_type = col.models.get(NotetypeId(note_type_id))
                    if (
                        updated_note_type
                        and updated_note_type.get("name") == expected_name
                    ):
                        stats["synced_note_types"] += 1
                        add_debug_msg("✅ Note type updated SUCCESSFULLY")
                    else:
                        add_debug_msg(
                            "❌ FAILED to update note type - post-save verification failed"
                        )
                        stats["error_note_types"] += 1
                else:
                    stats["unchanged_note_types"] += 1
                    add_debug_msg("✅ Note type is already synchronized")

            except Exception as note_type_error:
                stats["error_note_types"] += 1
                error_msg = f"Error synchronizing note type {note_type_id_str}: {note_type_error}"
                stats["errors"].append(error_msg)
                add_debug_msg(f"❌ {error_msg}")
                import traceback

                add_debug_msg(f"Traceback: {traceback.format_exc()}")

        add_debug_msg(
            f"📊 RESULT: {stats['synced_note_types']} synchronized, {stats['unchanged_note_types']} unchanged, {stats['error_note_types']} errors"
        )

        # Cleanup orphaned note types in configuration
        try:
            orphaned_count = cleanup_orphaned_note_types()
            if orphaned_count > 0:
                add_debug_msg(
                    f"🧹 Cleanup: {orphaned_count} orphaned note types removed from configuration"
                )
        except Exception as cleanup_error:
            add_debug_msg(f"⚠️ Error cleaning up orphaned types: {cleanup_error}")

        return stats

    except Exception as e:
        add_debug_msg(f"❌ General synchronization ERROR: {e}")
        stats["errors"].append(f"General error: {e}")
        return stats


def get_or_create_deck(col, deckName, remote_deck_name=None):
    """
    Creates or gets an existing deck in Anki and applies options based on configured mode.

    Args:
        col: Anki Collection
        deckName: Deck name
        remote_deck_name (str, optional): Remote deck name for individual mode

    Returns:
        tuple: (deck_id, actual_name) where deck_id is the deck ID and actual_name is the real name used

    Raises:
        ValueError: If deck name is invalid
    """
    if (
        not deckName
        or not isinstance(deckName, str)
        or deckName.strip() == ""
        or deckName.strip().lower() == "default"
    ):
        raise ValueError(
            "Invalid deck name or forbidden for synchronization: '%s'" % deckName
        )

    deck = col.decks.by_name(deckName)
    deck_was_created = False

    if deck is None:
        try:
            deck_id = col.decks.id(deckName)
            deck_was_created = True
            # Get newly created deck to verify real name used
            new_deck = col.decks.get(deck_id)
            actual_name = new_deck["name"] if new_deck else deckName
        except Exception as e:
            raise ValueError(f"Could not create deck '{deckName}': {str(e)}")
    else:
        deck_id = deck["id"]
        actual_name = deck["name"]

    # Apply options based on mode (new or existing that is Sheets2Anki)
    if deckName.startswith("Sheets2Anki::") or deck_was_created:
        try:
            apply_sheets2anki_options_to_deck(deck_id, remote_deck_name)
        except Exception as e:
            add_debug_message(
                f"Warning: Failed to apply options to deck '{actual_name}': {e}",
                "DECK_OPTIONS"
            )

    return deck_id, actual_name


def get_model_suffix_from_url(url):
    """
    Generates a unique and short suffix based on the URL.

    Args:
        url: Remote deck URL

    Returns:
        str: 8-character suffix based on URL SHA1 hash
    """
    return hashlib.sha1(url.encode()).hexdigest()[:8]


def get_note_type_name(url, remote_deck_name, student=None, is_cloze=False):
    """
    Generates standardized name for Sheets2Anki note types.

    Format: "Sheets2Anki - {remote_deck_name} - {student_name} - Basic/Cloze"
    The remote_deck_name already has conflict resolution applied by config_manager.

    Args:
        url (str): Remote deck URL
        remote_deck_name (str): Remote deck name from spreadsheet (with suffix if necessary)
        student (str, optional): Student name for specific note type
        is_cloze (bool): If it's a Cloze note type

    Returns:
        str: Standardized note type name
    """

    note_type = "Cloze" if is_cloze else "Basic"

    # Use remote name directly (already comes with conflict suffix from config_manager)
    clean_remote_name = remote_deck_name.strip() if remote_deck_name else "RemoteDeck"

    # Use student name as provided (case-sensitive)
    if student:
        clean_student_name = student.strip()
        if clean_student_name:
            return f"Sheets2Anki - {clean_remote_name} - {clean_student_name} - {note_type}"
    else:
        return f"Sheets2Anki - {clean_remote_name} - {note_type}"


def register_note_type_for_deck(url, note_type_id, note_type_name, debug_messages=None):
    """
    Registers a note type ID at creation/use time (intelligent approach).
    Stores full note type name as source of truth.

    Args:
        url (str): Remote deck URL
        note_type_id (int): Note type ID
        note_type_name (str): Full note type name in standard format
        debug_messages (list, optional): List for debug messages
    """
    from .config_manager import add_note_type_id_to_deck

    def add_debug_msg(message, category="NOTE_TYPE_REG"):
        """Helper to add debug messages with timestamp."""
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] [{category}] {message}"
        if debug_messages is not None:
            debug_messages.append(formatted_msg)

    try:
        add_debug_msg(
            f"Registering note type: ID={note_type_id}, Name='{note_type_name}'"
        )

        # Use full name as is (already in standard format)
        # Full name will be the source of truth
        add_note_type_id_to_deck(url, note_type_id, note_type_name, debug_messages)
        add_debug_msg(f"✅ Note type successfully registered: '{note_type_name}'")

    except Exception as e:
        add_debug_msg(f"❌ ERROR registering note type: {e}")


def capture_deck_note_type_ids_from_cards(url, local_deck_id, debug_messages=None):
    """
    Captures note type IDs by analyzing existing cards in the local deck (more intelligent approach).
    Instead of searching by name, analyzes actual cards belonging to the deck.

    Args:
        url (str): Remote deck URL
        local_deck_id (int): Local deck ID in Anki
        debug_messages (list, optional): List for debug messages
    """
    from .compat import mw
    from .config_manager import add_note_type_id_to_deck

    def add_debug_msg(message, category="NOTE_TYPE_IDS"):
        """Helper to add debug messages with timestamp."""
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] [{category}] {message}"
        if debug_messages is not None:
            debug_messages.append(formatted_msg)

    add_debug_msg(f"INTELLIGENT CAPTURE: Analyzing cards from deck ID {local_deck_id}")

    if not mw or not mw.col:
        add_debug_msg("ERROR: Anki not available")
        return

    try:
        # Search for all cards in specific deck
        # Use safe deck ID search
        card_ids = mw.col.find_cards(f"did:{local_deck_id}")
        add_debug_msg(f"Found {len(card_ids)} cards in deck")

        if not card_ids:
            add_debug_msg(
                "⚠️ No cards found in deck - note types will be captured during synchronization"
            )
            return

        # Collect unique note type IDs from existing cards
        note_type_ids = set()
        note_type_info = {}  # {note_type_id: {'name': str, 'count': int}}

        for card_id in card_ids:
            try:
                card = mw.col.get_card(card_id)
                note = card.note()
                note_type = note.note_type()

                if not note_type:
                    add_debug_msg(
                        f"Ignoring card {card_id} - note type not found"
                    )
                    continue

                note_type_id = note_type["id"]
                note_type_name = note_type["name"]

                note_type_ids.add(note_type_id)

                if note_type_id not in note_type_info:
                    note_type_info[note_type_id] = {"name": note_type_name, "count": 0}
                note_type_info[note_type_id]["count"] += 1

            except Exception as card_error:
                add_debug_msg(f"Error processing card {card_id}: {card_error}")
                continue

        add_debug_msg(f"Unique note types found: {len(note_type_ids)}")

        # Register each found note type
        for note_type_id in note_type_ids:
            info = note_type_info[note_type_id]
            full_name = info["name"]  # Full note type name
            count = info["count"]

            add_debug_msg(
                f"Registering: ID {note_type_id}, Full Name '{full_name}', Cards: {count}"
            )

            # Use full name as source of truth (don't extract parts)
            add_note_type_id_to_deck(url, note_type_id, full_name, debug_messages)

        add_debug_msg(
            f"✅ SUCCESS: Captured {len(note_type_ids)} note types from existing cards"
        )

    except Exception as e:
        add_debug_msg(f"❌ ERROR in intelligent capture: {e}")
        import traceback

        add_debug_msg(f"Details: {traceback.format_exc()}")


def capture_deck_note_type_ids(
    url, remote_deck_name, enabled_students=None, debug_messages=None
):
    """
    Compatibility function using card-based intelligent approach.

    Args:
        url (str): Remote deck URL
        remote_deck_name (str): Remote deck name
        enabled_students (list, optional): List of enabled students
        debug_messages (list, optional): List for debug messages
    """
    from .config_manager import get_deck_local_id

    def add_debug_msg(message, category="NOTE_TYPE_IDS"):
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] [{category}] {message}"
        if debug_messages is not None:
            debug_messages.append(formatted_msg)

    try:
        # Get local deck ID
        local_deck_id = get_deck_local_id(url)

        if local_deck_id:
            add_debug_msg(
                f"Using intelligent capture for local deck ID: {local_deck_id}"
            )
            capture_deck_note_type_ids_from_cards(url, local_deck_id, debug_messages)
        else:
            add_debug_msg(
                "⚠️ Local deck not found - note types will be registered during creation"
            )

    except Exception as e:
        add_debug_msg(f"❌ ERROR: {e}")
        import traceback

        add_debug_msg(f"Details: {traceback.format_exc()}")
        import traceback

        error_details = traceback.format_exc()
        add_debug_msg(f"Error details: {error_details}")


def delete_deck_note_types_by_ids(url):
    """
    Deletes note types using stored IDs from deck configuration.
    This is a more robust alternative to searching for name patterns.

    Args:
        url (str): Remote deck URL

    Returns:
        int: Number of deleted note types
    """
    from .compat import mw
    from .config_manager import cleanup_invalid_note_type_ids
    from .config_manager import get_deck_note_type_ids
    from .config_manager import remove_note_type_id_from_deck

    if not mw or not mw.col:
        add_debug_message("Anki not available", "DELETE_BY_IDS")
        return 0

    try:
        # First cleanup invalid IDs
        cleanup_invalid_note_type_ids()

        # Get valid IDs
        note_type_ids = get_deck_note_type_ids(url)

        if not note_type_ids:
            add_debug_message("No note type IDs found for deck", "DELETE_BY_IDS")
            return 0

        deleted_count = 0

        for (
            note_type_id
        ) in note_type_ids.copy():  # Use copy to modify during iteration
            from anki.models import NotetypeId
            model = mw.col.models.get(NotetypeId(note_type_id))
            if model:
                model_name = model["name"]

                try:
                    # Check if there are notes using this note type
                    note_ids = mw.col.models.nids(note_type_id)
                    if note_ids:
                        add_debug_message(
                            f"Note type '{model_name}' has {len(note_ids)} notes, deleting them first...",
                            "DELETE_BY_IDS"
                        )
                        mw.col.remove_notes(note_ids)

                    # Delete note type
                    mw.col.models.rem(model)
                    deleted_count += 1

                    # Remove ID from configuration
                    remove_note_type_id_from_deck(url, note_type_id)

                    add_debug_message(
                        f"Note type '{model_name}' (ID: {note_type_id}) successfully deleted",
                        "DELETE_BY_IDS"
                    )

                except Exception as e:
                    add_debug_message(
                        f"Error deleting note type '{model_name}' (ID: {note_type_id}): {e}",
                        "DELETE_BY_IDS"
                    )
            else:
                # ID no longer exists, remove from configuration
                remove_note_type_id_from_deck(url, note_type_id)
                add_debug_message(
                    f"Note type ID {note_type_id} not found, removed from configuration",
                    "DELETE_BY_IDS"
                )

        if deleted_count > 0:
            mw.col.save()
            add_debug_message(
                f"Operation completed: {deleted_count} note types deleted",
                "DELETE_BY_IDS"
            )

        return deleted_count

    except Exception as e:
        add_debug_message(f"Error in deletion by IDs: {e}", "DELETE_BY_IDS")
        import traceback

        traceback.print_exc()
        return 0


def rename_note_type_in_anki(note_type_id, new_name):
    """
    Renames an existing note type in Anki without creating a new one.

    Args:
        note_type_id (int): ID of note type to be renamed
        new_name (str): New name for the note type

    Returns:
        bool: True if renamed successfully, False otherwise
    """
    try:
        from aqt import mw

        if not mw or not mw.col:
            add_debug_message("Anki is not available", "RENAME_NOTE_TYPE")
            return False

        # Get existing model
        from anki.models import NotetypeId
        model = mw.col.models.get(NotetypeId(note_type_id))  # type: ignore
        if not model:
            add_debug_message(f"Note type ID {note_type_id} not found", "RENAME_NOTE_TYPE")
            return False

        old_name = model["name"]

        # Only rename if name is different
        if old_name == new_name:
            add_debug_message(
                f"Note type {note_type_id} already has correct name: '{new_name}'",
                "RENAME_NOTE_TYPE"
            )
            return True

        add_debug_message(
            f"Renaming note type {note_type_id} from '{old_name}' to '{new_name}'",
            "RENAME_NOTE_TYPE"
        )

        # Change only the name of existing model
        model["name"] = new_name

        # Save changes
        mw.col.models.save(model)

        add_debug_message("✅ Note type successfully renamed!", "RENAME_NOTE_TYPE")
        return True

    except Exception as e:
        add_debug_message(f"❌ Error renaming note type {note_type_id}: {e}", "RENAME_NOTE_TYPE")
        import traceback

        traceback.print_exc()
        return False


def get_note_key(note):
    """
    Gets the key field of a note based on its type.

    Args:
        note: Anki note

    Returns:
        str: Key value or None if not found
    """
    if "Text" in note:
        return note["Text"]
    elif "Front" in note:
        return note["Front"]
    return None


def cleanup_orphaned_note_types():
    """
    Removes note types that no longer exist in Anki from the configuration.
    Useful for cleaning up references to deleted note types.

    Returns:
        int: Number of orphaned note types removed from configuration
    """
    try:
        from aqt import mw

        add_debug_message("Starting orphaned note type cleanup...", "CLEANUP_ORPHANED")

        if not mw or not mw.col:
            add_debug_message("Anki is not available", "CLEANUP_ORPHANED")
            return 0

        from .config_manager import get_meta
        from .config_manager import save_meta

        meta = get_meta()
        if not meta or "decks" not in meta:
            add_debug_message("No deck configuration found", "CLEANUP_ORPHANED")
            return 0

        cleaned_count = 0

        for publication_key, deck_info in meta["decks"].items():
            if "note_types" not in deck_info:
                continue

            orphaned_ids = []

            # Check which note types from the configuration no longer exist in Anki
            for note_type_id_str, note_type_name in deck_info["note_types"].items():
                try:
                    note_type_id = int(note_type_id_str)
                    # Use the same pattern as the rest of the code
                    from anki.models import NotetypeId
                    model = mw.col.models.get(NotetypeId(note_type_id))  # type: ignore

                    if not model:
                        orphaned_ids.append(note_type_id_str)
                        add_debug_message(
                            f"Orphan found: ID {note_type_id_str} - '{note_type_name}'",
                            "CLEANUP_ORPHANED"
                        )

                except (ValueError, TypeError):
                    # Invalid ID, also remove
                    orphaned_ids.append(note_type_id_str)
                    add_debug_message(
                        f"Invalid ID found: '{note_type_id_str}'",
                        "CLEANUP_ORPHANED"
                    )

            # Remove orphans from configuration
            for orphaned_id in orphaned_ids:
                del deck_info["note_types"][orphaned_id]
                cleaned_count += 1
                add_debug_message(f"Orphan removed: ID {orphaned_id}", "CLEANUP_ORPHANED")

        if cleaned_count > 0:
            save_meta(meta)
            add_debug_message(
                f"Cleanup completed: {cleaned_count} orphaned note types removed",
                "CLEANUP_ORPHANED"
            )
        else:
            add_debug_message("No orphaned note types found", "CLEANUP_ORPHANED")

        return cleaned_count

    except Exception as e:
        add_debug_message(f"Error in cleanup: {e}", "CLEANUP_ORPHANED")
        import traceback

        traceback.print_exc()
        return 0


# =============================================================================
# SHARED DECK OPTIONS MANAGEMENT
# =============================================================================


def _is_default_config(config, config_type="default"):
    """
    Checks if the configuration still has Sheets2Anki default values.

    Args:
        config (dict): Deck configuration
        config_type (str): Configuration type ("root" or "default")

    Returns:
        bool: True if it still has addon default values
    """
    try:
        if config_type == "root":
            # Default values for root deck
            expected_values = {
                "new_perDay": 20,
                "rev_perDay": 200,
                "new_delays": [1, 10],
                "lapse_delays": [10],
                "lapse_minInt": 1,
                "lapse_mult": 0.0,
            }
        else:
            # Default values for remote decks
            expected_values = {
                "new_perDay": 20,
                "rev_perDay": 200,
                "new_delays": [1, 10],
                "lapse_delays": [10],
                "lapse_minInt": 1,
                "lapse_mult": 0.0,
            }

        # Check each expected value
        checks = [
            config["new"]["perDay"] == expected_values["new_perDay"],
            config["rev"]["perDay"] == expected_values["rev_perDay"],
            config["new"]["delays"] == expected_values["new_delays"],
            config["lapse"]["delays"] == expected_values["lapse_delays"],
            config["lapse"]["minInt"] == expected_values["lapse_minInt"],
            config["lapse"]["mult"] == expected_values["lapse_mult"],
        ]

        return all(checks)
    except (KeyError, TypeError):
        # If there's an error accessing any field, consider it customized
        return False


def _should_update_config_version(config):
    """
    Checks if the configuration needs to be updated for a new version of the addon.
    This function can be used in the future to apply configuration updates
    without overwriting user customizations.

    Args:
        config (dict): Deck configuration

    Returns:
        bool: True if it needs to update to a new version
    """
    # For future versions, we can add logic here to detect
    # old configurations that need to be updated
    config_version = config.get("sheets2anki_version", "1.0.0")
    addon_version = "1.0.0"  # This would be obtained from manifest.json

    # For now, always returns False to not force updates
    return False


def get_or_create_sheets2anki_options_group(deck_name=None, deck_url=None):
    """
    Gets or creates the options group based on the configured mode and deck-specific configuration.

    Args:
        deck_name (str, optional): Remote deck name for individual mode
        deck_url (str, optional): Deck URL to get specific configuration

    Returns:
        int: Options group ID or None if in manual mode
    """
    from .config_manager import get_deck_options_mode, get_deck_configurations_package_name

    if not mw or not mw.col:
        add_debug_message("❌ Anki not available", "DECK_OPTIONS")
        return None

    # First, check if there's a specific configuration stored for this deck
    if deck_url:
        stored_package_name = get_deck_configurations_package_name(deck_url)
        if stored_package_name:
            options_group_name = stored_package_name
            add_debug_message(
                f"Using deck-specific configuration: '{options_group_name}'",
                "DECK_OPTIONS",
            )
        else:
            # Fallback to global mode if no specific configuration
            mode = get_deck_options_mode()
            if mode == "manual":
                add_debug_message(
                    "Manual mode active - not applying automatic options", "DECK_OPTIONS"
                )
                return None
            elif mode == "individual" and deck_name:
                options_group_name = f"Sheets2Anki - {deck_name}"
                add_debug_message(
                    f"Individual mode: creating/getting group '{options_group_name}'",
                    "DECK_OPTIONS",
                )
            else:  # mode == "shared" or fallback
                options_group_name = "Sheets2Anki - Default Options"
                add_debug_message(
                    f"Shared mode: creating/getting group '{options_group_name}'", "DECK_OPTIONS"
                )
    else:
        # Check configured mode (fallback when no URL)
        mode = get_deck_options_mode()

        if mode == "manual":
            add_debug_message(
                "Manual mode active - not applying automatic options", "DECK_OPTIONS"
            )
            return None
        elif mode == "individual" and deck_name:
            options_group_name = f"Sheets2Anki - {deck_name}"
            add_debug_message(
                f"Individual mode: creating/getting group '{options_group_name}'",
                "DECK_OPTIONS",
            )
        else:  # mode == "shared" or fallback
            options_group_name = "Sheets2Anki - Default Options"
            add_debug_message(
                f"Shared mode: creating/getting group '{options_group_name}'", "DECK_OPTIONS"
            )

    try:
        # Search for existing options group
        all_option_groups = mw.col.decks.all_config()

        add_debug_message(
            f"Searching for group '{options_group_name}' among {len(all_option_groups)} existing groups",
            "DECK_OPTIONS",
        )

        for group in all_option_groups:
            if group["name"] == options_group_name:
                add_debug_message(
                    f"✅ Group '{options_group_name}' already exists (ID: {group['id']})",
                    "DECK_OPTIONS",
                )

                # Check if configurations were customized by the user
                try:
                    existing_config = mw.col.decks.get_config(group["id"])
                    if existing_config and not _is_default_config(
                        existing_config, "default" if mode == "shared" else "default"
                    ):
                        add_debug_message(
                            f"🔒 Group '{options_group_name}' has customized settings - preserving",
                            "DECK_OPTIONS",
                        )
                    else:
                        add_debug_message(
                            f"📋 Group '{options_group_name}' still has default settings",
                            "DECK_OPTIONS",
                        )
                except Exception as check_error:
                    add_debug_message(
                        f"⚠️ Error checking existing group settings: {check_error}",
                        "DECK_OPTIONS",
                    )

                return group["id"]

        # If it doesn't exist, create a new group
        add_debug_message(
            f"Group does not exist, creating new one: '{options_group_name}'", "DECK_OPTIONS"
        )
        new_group = mw.col.decks.add_config_returning_id(options_group_name)
        add_debug_message(
            f"✅ New group '{options_group_name}' created (ID: {new_group})",
            "DECK_OPTIONS",
        )

        # IMPORTANT: We only apply default settings in NEW groups
        # Existing groups may have been customized by the user
        add_debug_message(
            f"🔧 Applying default settings to new group '{options_group_name}'",
            "DECK_OPTIONS",
        )

        # Configure optimized default options for spreadsheet flashcards
        try:
            config = mw.col.decks.get_config(new_group)
            if not config:
                add_debug_message(
                    f"❌ Could not get config for group {new_group}",
                    "DECK_OPTIONS",
                )
                return None

            # Optimized settings for spreadsheet study
            config["new"]["perDay"] = 20  # 20 new cards per day (good for spreadsheets)
            config["rev"]["perDay"] = 200  # 200 reviews per day
            config["new"]["delays"] = [1, 10]  # Short initial intervals
            config["lapse"]["delays"] = [10]  # Interval for forgotten cards
            config["lapse"]["minInt"] = 1  # Minimum interval after lapse
            config["lapse"]["mult"] = 0.0  # Interval reduction after lapse

            mw.col.decks.update_config(config)
            add_debug_message(
                f"✅ Default settings applied to new group '{options_group_name}'",
                "DECK_OPTIONS",
            )
            add_debug_message(
                f"📊 Applied values: new/day={config['new']['perDay']}, rev/day={config['rev']['perDay']}",
                "DECK_OPTIONS",
            )
        except Exception as config_error:
            add_debug_message(
                f"⚠️ Error configuring group {new_group}: {config_error}",
                "DECK_OPTIONS",
            )
            # We still return the group ID even if configuration failed
            add_debug_message(
                f"Returning group {new_group} even with configuration error",
                "DECK_OPTIONS",
            )

        return new_group

    except Exception as e:
        add_debug_message(
            f"❌ Error creating/getting options group: {e}", "DECK_OPTIONS"
        )
        import traceback

        traceback.print_exc()
        return None


def apply_sheets2anki_options_to_deck(deck_id, deck_name=None):
    """
    Applies the options group based on the configured mode to a specific deck.

    Args:
        deck_id (int): Anki deck ID
        deck_name (str, optional): Remote deck name for individual mode

    Returns:
        bool: True if successfully applied, False otherwise
    """
    from .config_manager import get_deck_options_mode

    if not mw or not mw.col or not deck_id:
        add_debug_message("❌ Anki or invalid deck_id", "DECK_OPTIONS")
        return False

    # Check if manual mode is active
    mode = get_deck_options_mode()
    if mode == "manual":
        add_debug_message(
            f"Manual mode active - not applying options to deck {deck_id}",
            "DECK_OPTIONS",
        )
        return False

    try:
        add_debug_message(
            f"Applying options to deck {deck_id} (name for options: {deck_name})",
            "DECK_OPTIONS",
        )

        # Get or create options group based on mode
        options_group_id = get_or_create_sheets2anki_options_group(deck_name)

        if not options_group_id:
            add_debug_message("❌ Failed to get options group", "DECK_OPTIONS")
            return False

        # Get deck information
        deck = mw.col.decks.get(deck_id)
        if not deck:
            add_debug_message(f"❌ Deck not found: {deck_id}", "DECK_OPTIONS")
            return False

        deck_full_name = deck["name"]

        add_debug_message(
            f"Options group obtained: {options_group_id} for deck '{deck_full_name}'",
            "DECK_OPTIONS",
        )

        # Apply options group to the deck
        deck["conf"] = options_group_id
        mw.col.decks.save(deck)

        add_debug_message(
            f"✅ Group applied to deck '{deck_full_name}' (ID: {deck_id})",
            "DECK_OPTIONS",
        )
        return True

    except Exception as e:
        add_debug_message(
            f"❌ Error applying options to deck {deck_id}: {e}", "DECK_OPTIONS"
        )
        import traceback

        traceback.print_exc()
        return False


def apply_sheets2anki_options_to_all_remote_decks():
    """
    Applies the options group based on the configured mode to all remote decks.

    Returns:
        dict: Operation statistics
    """
    from .config_manager import get_deck_options_mode
    from .config_manager import get_remote_decks

    if not mw or not mw.col:
        add_debug_message("❌ Anki not available", "DECK_OPTIONS")
        return {"success": False, "error": "Anki not available"}

    # Check if manual mode is active
    mode = get_deck_options_mode()
    if mode == "manual":
        add_debug_message(
            "Manual mode active - not applying options automatically", "DECK_OPTIONS"
        )
        return {
            "success": True,
            "total_decks": 0,
            "updated_decks": 0,
            "failed_decks": 0,
            "errors": [
                "Manual mode active - settings not applied automatically"
            ],
        }

    stats = {
        "success": True,
        "total_decks": 0,
        "updated_decks": 0,
        "failed_decks": 0,
        "errors": [],
    }

    try:
        # Get all remote decks
        remote_decks = get_remote_decks()
        stats["total_decks"] = len(remote_decks)

        add_debug_message(
            f"Remote decks found: {len(remote_decks)}", "DECK_OPTIONS"
        )

        if not remote_decks:
            add_debug_message("No remote decks found", "DECK_OPTIONS")
            return stats

        mode_desc = {
            "shared": "shared options (Default)",
            "individual": "individual options per deck",
        }

        add_debug_message(
            f"Applying {mode_desc.get(mode, 'options')} to {len(remote_decks)} remote decks...",
            "DECK_OPTIONS",
        )

        # Detailed log of found decks
        for spreadsheet_id, deck_info in remote_decks.items():
            add_debug_message(
                f"Deck ID: {spreadsheet_id}, Info: {deck_info}", "DECK_OPTIONS"
            )

        # Apply options to each remote deck
        for spreadsheet_id, deck_info in remote_decks.items():
            try:
                local_deck_id = deck_info.get("local_deck_id")
                local_deck_name = deck_info.get("local_deck_name", "Unknown")
                remote_deck_name = deck_info.get("remote_deck_name", "Unknown")

                add_debug_message(
                    f"Processing deck: {local_deck_name} (ID: {local_deck_id}, Remote: {remote_deck_name})",
                    "DECK_OPTIONS",
                )

                if not local_deck_id:
                    error_msg = f"Deck '{local_deck_name}' has no local_deck_id"
                    stats["errors"].append(error_msg)
                    stats["failed_decks"] += 1
                    add_debug_message(f"❌ {error_msg}", "DECK_OPTIONS")
                    continue

                # For individual mode, use remote deck name
                deck_name_for_options = (
                    remote_deck_name if mode == "individual" else None
                )

                add_debug_message(
                    f"Name for options: {deck_name_for_options} (mode: {mode})",
                    "DECK_OPTIONS",
                )

                # Apply options to the main deck
                if apply_sheets2anki_options_to_deck(
                    local_deck_id, deck_name_for_options
                ):
                    stats["updated_decks"] += 1
                    add_debug_message(
                        f"✅ Deck {local_deck_name} successfully configured",
                        "DECK_OPTIONS",
                    )

                    # Also apply to subdecks (if they exist)
                    apply_options_to_subdecks(
                        local_deck_name,
                        remote_deck_name if mode == "individual" else None,
                    )
                else:
                    stats["failed_decks"] += 1
                    add_debug_message(
                        f"❌ Failed to configure deck {local_deck_name}", "DECK_OPTIONS"
                    )

            except Exception as e:
                error_msg = f"Error in deck {spreadsheet_id}: {e}"
                stats["errors"].append(error_msg)
                stats["failed_decks"] += 1
                add_debug_message(f"❌ {error_msg}", "DECK_OPTIONS")

        add_debug_message(
            f"Operation completed: {stats['updated_decks']}/{stats['total_decks']} decks updated",
            "DECK_OPTIONS",
        )

        if stats["errors"]:
            add_debug_message(
                f"{len(stats['errors'])} errors found:", "DECK_OPTIONS"
            )
            for error in stats["errors"]:
                add_debug_message(f"  - {error}", "DECK_OPTIONS")

        return stats

    except Exception as e:
        error_msg = f"General error in applying options: {e}"
        stats["success"] = False
        stats["errors"].append(error_msg)
        add_debug_message(error_msg, "DECK_OPTIONS")
        return stats


def apply_options_to_subdecks(parent_deck_name, remote_deck_name=None):
    """
    Applies mode-based options to all subdecks of a parent deck.

    Args:
        parent_deck_name (str): Parent deck name
        remote_deck_name (str, optional): Remote deck name for individual mode
    """
    from .config_manager import get_deck_options_mode

    if not mw or not mw.col or not parent_deck_name:
        add_debug_message("❌ Invalid parameters for subdecks", "DECK_OPTIONS")
        return

    # Check if manual mode is active
    mode = get_deck_options_mode()
    if mode == "manual":
        add_debug_message(
            "Manual mode active - not applying options to subdecks", "DECK_OPTIONS"
        )
        return

    try:
        add_debug_message(f"Searching for subdecks of: {parent_deck_name}", "DECK_OPTIONS")

        # Search for all decks that start with parent deck name
        all_decks = mw.col.decks.all()
        subdeck_count = 0

        for deck in all_decks:
            deck_name = deck["name"]

            # Check if it's a subdeck (contains :: after parent name)
            if deck_name.startswith(parent_deck_name + "::"):
                add_debug_message(f"Subdeck found: {deck_name}", "DECK_OPTIONS")
                deck_name_for_options = (
                    remote_deck_name if mode == "individual" else None
                )

                if apply_sheets2anki_options_to_deck(deck["id"], deck_name_for_options):
                    add_debug_message(
                        f"✅ Options applied to subdeck: {deck_name}", "DECK_OPTIONS"
                    )
                    subdeck_count += 1
                else:
                    add_debug_message(
                        f"❌ Failed to apply options to subdeck: {deck_name}",
                        "DECK_OPTIONS",
                    )

        add_debug_message(
            f"Total subdecks processed: {subdeck_count}", "DECK_OPTIONS"
        )

    except Exception as e:
        add_debug_message(
            f"❌ Error applying options to subdecks of '{parent_deck_name}': {e}",
            "DECK_OPTIONS",
        )
        import traceback

        traceback.print_exc()


def cleanup_orphaned_deck_option_groups():
    """
    Removes orphaned deck options groups that start with "Sheets2Anki" and are not
    attached to any deck (total of zero attached decks).

    Returns:
        int: Number of removed orphaned options groups
    """
    if not mw or not mw.col:
        add_debug_message("Anki is not available", "DECK_OPTIONS_CLEANUP")
        return 0

    try:
        add_debug_message("Starting orphaned options group cleanup...", "DECK_OPTIONS_CLEANUP")

        # Get all options groups
        all_option_groups = mw.col.decks.all_config()
        sheets2anki_groups = []

        # Filter only groups that start with "Sheets2Anki"
        for group in all_option_groups:
            if group["name"].startswith("Sheets2Anki"):
                sheets2anki_groups.append(group)

        if not sheets2anki_groups:
            add_debug_message("No Sheets2Anki groups found", "DECK_OPTIONS_CLEANUP")
            return 0

        # Get all decks to check which groups are in use
        all_decks = mw.col.decks.all()
        groups_in_use = set()

        for deck in all_decks:
            conf_id = deck.get("conf", None)
            if conf_id:
                groups_in_use.add(conf_id)

        # Identify orphaned groups (not used by any deck)
        orphaned_groups = []
        for group in sheets2anki_groups:
            group_id = group["id"]
            if group_id not in groups_in_use:
                orphaned_groups.append(group)
                add_debug_message(
                    f"Orphaned group found: '{group['name']}' (ID: {group_id})",
                    "DECK_OPTIONS_CLEANUP"
                )

        # Remove orphaned groups
        removed_count = 0
        for group in orphaned_groups:
            try:
                mw.col.decks.remove_config(group["id"])
                add_debug_message(
                    f"Removed: '{group['name']}' (ID: {group['id']})",
                    "DECK_OPTIONS_CLEANUP"
                )
                removed_count += 1
            except Exception as e:
                add_debug_message(
                    f"Error removing group '{group['name']}': {e}",
                    "DECK_OPTIONS_CLEANUP"
                )

        if removed_count > 0:
            add_debug_message(
                f"Cleanup completed: {removed_count} orphaned groups removed",
                "DECK_OPTIONS_CLEANUP"
            )
        else:
            add_debug_message("No orphaned groups found", "DECK_OPTIONS_CLEANUP")

        return removed_count

    except Exception as e:
        add_debug_message(f"Error in orphaned group cleanup: {e}", "DECK_OPTIONS_CLEANUP")
        return 0


def apply_automatic_deck_options_system():
    """
    Applies the complete automatic deck options system.
    This function should be called at the end of synchronization and when the user
    clicks the "Apply" button in the deck settings.

    Performs the following actions (when automatic mode is active):
    1. Applies options to root deck "Sheets2Anki"
    2. Applies options to all remote decks and subdecks
    3. Removes orphaned options groups (cleanup)

    Returns:
        dict: Operation statistics
    """
    add_debug_message(
        "🚀 STARTING automatic deck options system...", "DECK_OPTIONS_SYSTEM"
    )

    from .config_manager import get_deck_options_mode

    if not mw or not mw.col:
        add_debug_message("❌ Anki not available", "DECK_OPTIONS_SYSTEM")
        return {"success": False, "error": "Anki not available"}

    try:
        mode = get_deck_options_mode()
        add_debug_message(f"📋 Current mode: '{mode}'", "DECK_OPTIONS_SYSTEM")
    except Exception as e:
        add_debug_message(f"❌ Error getting mode: {e}", "DECK_OPTIONS_SYSTEM")
        return {"success": False, "error": f"Error getting mode: {e}"}

    if mode == "manual":
        add_debug_message(
            "⏹️ Manual mode active - automatic system disabled", "DECK_OPTIONS_SYSTEM"
        )
        return {
            "success": True,
            "mode": "manual",
            "root_deck_updated": False,
            "remote_decks_updated": 0,
            "cleaned_groups": 0,
            "message": "Manual mode active - automatic system disabled",
        }

    add_debug_message(
        f"⚙️ Applying automatic system in mode: {mode}", "DECK_OPTIONS_SYSTEM"
    )

    try:
        stats = {
            "success": True,
            "mode": mode,
            "root_deck_updated": False,
            "remote_decks_updated": 0,
            "cleaned_groups": 0,
            "errors": [],
        }

        add_debug_message(
            "🎯 STEP 1: Configuring root deck...", "DECK_OPTIONS_SYSTEM"
        )
        # 1. Apply options to root deck
        try:
            root_result = ensure_root_deck_has_root_options()
            stats["root_deck_updated"] = root_result
            if root_result:
                add_debug_message(
                    "✅ Root deck successfully configured", "DECK_OPTIONS_SYSTEM"
                )
            else:
                add_debug_message(
                    "⚠️ Root deck was not configured", "DECK_OPTIONS_SYSTEM"
                )
        except Exception as e:
            error_msg = f"Error configuring root deck: {e}"
            stats["errors"].append(error_msg)
            add_debug_message(f"❌ {error_msg}", "DECK_OPTIONS_SYSTEM")
            import traceback

            traceback.print_exc()

        add_debug_message(
            "🎯 STEP 2: Configuring remote decks...", "DECK_OPTIONS_SYSTEM"
        )
        # 2. Apply options to all remote decks
        try:
            remote_result = apply_sheets2anki_options_to_all_remote_decks()
            if remote_result and remote_result.get("success", False):
                stats["remote_decks_updated"] = remote_result.get("updated_decks", 0)
                add_debug_message(
                    f"✅ {remote_result.get('updated_decks', 0)} remote decks configured",
                    "DECK_OPTIONS_SYSTEM",
                )
                if remote_result.get("errors"):
                    stats["errors"].extend(remote_result["errors"])
            else:
                error_detail = (
                    remote_result.get("error", "Unknown error in remote decks")
                    if remote_result
                    else "Empty result"
                )
                stats["errors"].append(error_detail)
                add_debug_message(
                    f"❌ Remote decks failure: {error_detail}", "DECK_OPTIONS_SYSTEM"
                )
        except Exception as e:
            error_msg = f"Error configuring remote decks: {e}"
            stats["errors"].append(error_msg)
            add_debug_message(f"❌ {error_msg}", "DECK_OPTIONS_SYSTEM")
            import traceback

            traceback.print_exc()

        add_debug_message(
            "🎯 STEP 3: Cleaning up orphaned groups...", "DECK_OPTIONS_SYSTEM"
        )
        # 3. Cleanup of orphaned groups (only when automatic system is active)
        try:
            cleaned_count = cleanup_orphaned_deck_option_groups()
            stats["cleaned_groups"] = cleaned_count
            if cleaned_count > 0:
                add_debug_message(
                    f"✅ {cleaned_count} orphaned groups removed", "DECK_OPTIONS_SYSTEM"
                )
            else:
                add_debug_message(
                    "ℹ️ No orphaned groups found", "DECK_OPTIONS_SYSTEM"
                )
        except Exception as e:
            error_msg = f"Error cleaning up orphaned groups: {e}"
            stats["errors"].append(error_msg)
            add_debug_message(f"❌ {error_msg}", "DECK_OPTIONS_SYSTEM")
            import traceback

            traceback.print_exc()

        add_debug_message("📊 Generating final summary...", "DECK_OPTIONS_SYSTEM")
        # Generate summary message
        messages = []
        if stats["root_deck_updated"]:
            messages.append("Root deck configured")
        if stats["remote_decks_updated"] > 0:
            messages.append(
                f"{stats['remote_decks_updated']} remote decks configured"
            )
        if stats["cleaned_groups"] > 0:
            messages.append(f"{stats['cleaned_groups']} orphaned groups removed")

        if messages:
            stats["message"] = f"Automatic system applied: {', '.join(messages)}"
        else:
            stats["message"] = "Automatic system executed without changes"

        if stats["errors"]:
            stats["message"] += f" ({len(stats['errors'])} errors)"
            add_debug_message(
                f"⚠️ Errors found: {stats['errors']}", "DECK_OPTIONS_SYSTEM"
            )

        add_debug_message(f"🎉 COMPLETED: {stats['message']}", "DECK_OPTIONS_SYSTEM")
        return stats

    except Exception as e:
        error_msg = f"General error in automatic system: {e}"
        add_debug_message(f"❌ GENERAL FAILURE: {error_msg}", "DECK_OPTIONS_SYSTEM")
        import traceback

        traceback.print_exc()
        return {
            "success": False,
            "mode": mode if "mode" in locals() else "unknown",
            "root_deck_updated": False,
            "remote_decks_updated": 0,
            "cleaned_groups": 0,
            "error": error_msg,
        }


def ensure_root_deck_has_root_options():
    """
    Ensures that the root deck 'Sheets2Anki' uses the specific options group
    "Sheets2Anki - Root Options".

    Returns:
        bool: True if successfully applied, False otherwise
    """
    from .config_manager import get_deck_options_mode

    if not mw or not mw.col:
        add_debug_message("Anki is not available", "DECK_OPTIONS")
        return False

    # Check if manual mode is active
    mode = get_deck_options_mode()
    if mode == "manual":
        add_debug_message(
            "Manual mode active - not applying options to root deck", "DECK_OPTIONS"
        )
        return False

    try:
        add_debug_message(
            f"Checking root deck: '{DEFAULT_PARENT_DECK_NAME}'", "DECK_OPTIONS"
        )

        # Get or create the root deck
        parent_deck = mw.col.decks.by_name(DEFAULT_PARENT_DECK_NAME)

        if not parent_deck:
            add_debug_message(
                f"Root deck '{DEFAULT_PARENT_DECK_NAME}' does not exist, creating...",
                "DECK_OPTIONS",
            )
            # Create root deck if it doesn't exist
            parent_deck_id = mw.col.decks.id(DEFAULT_PARENT_DECK_NAME)
            if parent_deck_id is not None:
                parent_deck = mw.col.decks.get(parent_deck_id)
                add_debug_message(
                    f"Root deck created with ID: {parent_deck_id}", "DECK_OPTIONS"
                )
            else:
                add_debug_message("❌ Failed to create root deck", "DECK_OPTIONS")
                return False
        else:
            add_debug_message(
                f"Root deck found: ID {parent_deck['id']}", "DECK_OPTIONS"
            )

        if parent_deck:
            # Get current root options group of the deck
            current_conf_id = parent_deck.get("conf", 1)  # 1 is Anki default
            add_debug_message(
                f"Current root deck configuration: {current_conf_id}", "DECK_OPTIONS"
            )

            # Apply specific root deck group
            add_debug_message(
                "Calling get_or_create_root_options_group()...", "DECK_OPTIONS"
            )
            root_options_group_id = get_or_create_root_options_group()
            add_debug_message(
                f"get_or_create_root_options_group() returned: {root_options_group_id}",
                "DECK_OPTIONS",
            )

            if root_options_group_id:
                if current_conf_id != root_options_group_id:
                    parent_deck["conf"] = root_options_group_id
                    mw.col.decks.save(parent_deck)
                    add_debug_message(
                        f"✅ Root options applied to deck '{DEFAULT_PARENT_DECK_NAME}' (ID: {root_options_group_id})",
                        "DECK_OPTIONS",
                    )
                else:
                    add_debug_message(
                        f"✅ Root deck already uses the correct options (ID: {root_options_group_id})",
                        "DECK_OPTIONS",
                    )
                return True
            else:
                add_debug_message(
                    "❌ Failed to get/create root options group", "DECK_OPTIONS"
                )
                return False
        else:
            add_debug_message("❌ Failed to get/create root deck", "DECK_OPTIONS")
            return False

    except Exception as e:
        add_debug_message(
            f"❌ Error applying root options to parent deck: {e}", "DECK_OPTIONS"
        )
        import traceback

        traceback.print_exc()
        return False


def get_or_create_root_options_group():
    """
    Gets or creates the specific options group for the root deck "Sheets2Anki - Root Options".

    Returns:
        int: Options group ID or None if error
    """
    if not mw or not mw.col:
        add_debug_message(
            "Anki not available to create root options group", "DECK_OPTIONS"
        )
        return None

    options_group_name = "Sheets2Anki - Root Options"
    add_debug_message(
        f"Searching/creating options group: '{options_group_name}'", "DECK_OPTIONS"
    )

    try:
        # Search for existing options group
        all_option_groups = mw.col.decks.all_config()
        add_debug_message(
            f"Total options groups found: {len(all_option_groups)}",
            "DECK_OPTIONS",
        )

        for group in all_option_groups:
            if group["name"] == options_group_name:
                add_debug_message(
                    f"✅ Root group '{options_group_name}' already exists (ID: {group['id']})",
                    "DECK_OPTIONS",
                )

                # Check if configurations were customized by the user
                try:
                    existing_config = mw.col.decks.get_config(group["id"])
                    if existing_config and not _is_default_config(
                        existing_config, "root"
                    ):
                        add_debug_message(
                            f"🔒 Root group '{options_group_name}' has customized settings - preserving",
                            "DECK_OPTIONS",
                        )
                    else:
                        add_debug_message(
                            f"📋 Root group '{options_group_name}' still has default settings",
                            "DECK_OPTIONS",
                        )
                except Exception as check_error:
                    add_debug_message(
                        f"⚠️ Error checking existing root group settings: {check_error}",
                        "DECK_OPTIONS",
                    )

                return group["id"]

        add_debug_message(
            f"Group '{options_group_name}' does not exist, creating new one...", "DECK_OPTIONS"
        )
        # If it doesn't exist, create new group
        new_group = mw.col.decks.add_config_returning_id(options_group_name)
        add_debug_message(
            f"✅ New root group '{options_group_name}' created (ID: {new_group})",
            "DECK_OPTIONS",
        )

        # IMPORTANT: We only apply default settings in NEW groups
        # Existing groups may have been customized by the user
        add_debug_message(
            f"🔧 Applying default settings to new root group '{options_group_name}'",
            "DECK_OPTIONS",
        )

        # Configure optimized default options for the root deck
        add_debug_message(
            f"📋 Configuring options for root group '{options_group_name}' (ID: {new_group})...",
            "DECK_OPTIONS",
        )

        # Use the correct API to configure the options group
        # In recent Anki versions, we use mw.col.decks.get_config() and mw.col.decks.update_config()
        try:
            # Get current group configuration
            config = mw.col.decks.get_config(new_group)
            if config is None:
                add_debug_message(
                    f"❌ Could not get configuration for group ID {new_group}",
                    "DECK_OPTIONS",
                )
                return new_group  # Returns group even without configuring

            add_debug_message(
                f"📋 Configuration obtained for group ID {new_group}", "DECK_OPTIONS"
            )

            # Specific settings for root deck - more conservative
            config["new"][
                "perDay"
            ] = 30  # 30 new cards per day (conservative for root deck)
            config["rev"]["perDay"] = 150  # 150 reviews per day
            config["new"]["delays"] = [1, 10]  # Short initial intervals
            config["lapse"]["delays"] = [10]  # Interval for forgotten cards
            config["lapse"]["minInt"] = 1  # Minimum interval after lapse
            config["lapse"]["mult"] = 0.0  # Interval reduction after lapse

            # Save configurations
            mw.col.decks.update_config(config)
            add_debug_message(
                f"💾 Configurations saved for group ID {new_group}", "DECK_OPTIONS"
            )
            add_debug_message(
                f"📊 Values applied to root group: new/day={config['new']['perDay']}, rev/day={config['rev']['perDay']}",
                "DECK_OPTIONS",
            )

        except (AttributeError, TypeError) as api_error:
            add_debug_message(
                f"⚠️ API get_config/update_config not available: {api_error}",
                "DECK_OPTIONS",
            )
            # Fallback to older method if available
            try:
                # Alternative method for older versions
                config = mw.col.decks.confForDid(new_group)
                if config is None:
                    add_debug_message(
                        f"❌ confForDid returned None for group ID {new_group}",
                        "DECK_OPTIONS",
                    )
                    return new_group

                add_debug_message(
                    f"📋 Using confForDid as fallback for group ID {new_group}",
                    "DECK_OPTIONS",
                )

                config["new"]["perDay"] = 30
                config["rev"]["perDay"] = 150
                config["new"]["delays"] = [1, 10]
                config["lapse"]["delays"] = [10]
                config["lapse"]["minInt"] = 1
                config["lapse"]["mult"] = 0.0

                mw.col.decks.save(config)
                add_debug_message(
                    f"💾 Configurations saved via fallback for group ID {new_group}",
                    "DECK_OPTIONS",
                )

            except Exception as fallback_error:
                add_debug_message(
                    f"❌ Fallback failed: {fallback_error}", "DECK_OPTIONS"
                )
                # If no method works, at least the group was created
                add_debug_message(
                    "⚠️ Group created but configurations not applied due to API incompatibility",
                    "DECK_OPTIONS",
                )
        add_debug_message(
            f"✅ Default settings applied to root group '{options_group_name}'",
            "DECK_OPTIONS",
        )

        return new_group

    except Exception as e:
        add_debug_message(
            f"❌ Error creating/getting root options group: {str(e)}", "DECK_OPTIONS"
        )
        return None


# =============================================================================
# DEBUG AND LOGGING SYSTEM (consolidated from debug_manager.py)
# =============================================================================


class DebugManager:
    """Centralized debug manager for Sheets2Anki."""

    def __init__(self):
        self.messages: List[str] = []
        self.is_debug_enabled = False
        self._update_debug_status()

    def _update_debug_status(self):
        """Updates debug status based on configuration."""
        try:
            from .config_manager import get_meta

            meta = get_meta()
            # Debug is in the config section of meta.json
            self.is_debug_enabled = meta.get("config", {}).get("debug", False)
        except Exception:
            self.is_debug_enabled = False

    def add_message(self, message: str, category: str = "DEBUG") -> None:
        """
        Adds a debug message.

        Args:
            message: Debug message
            category: Message category (SYNC, DECK, ERROR, etc.)
        """
        # Ensure we have the latest debug status
        self._update_debug_status()

        if not self.is_debug_enabled:
            return

        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]  # With milliseconds
        formatted_msg = f"[{timestamp}] [{category}] {message}"
        self.messages.append(formatted_msg)

        # Print to Anki console
        print(formatted_msg)

        # Save to file for easy access
        self._save_to_file(formatted_msg)

    def _save_to_file(self, message: str) -> None:
        """
        Saves debug message to file.

        Args:
            message: Formatted message to save
        """
        try:
            import os

            # Determine log file path
            addon_path = os.path.dirname(os.path.dirname(__file__))
            log_path = os.path.join(addon_path, "debug_sheets2anki.log")

            # Save to file
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(message + "\n")
                f.flush()  # Force immediate write

        except Exception as e:
            # We don't use add_debug_message here to avoid potential infinite recursion
            print(f"[DEBUG_FILE] Error saving log: {e}")

    def get_messages(self) -> List[str]:
        """Returns all debug messages."""
        return self.messages.copy()

    def clear_messages(self) -> None:
        """Clears all debug messages."""
        self.messages.clear()

    def initialize_log_file(self) -> None:
        """
        Initializes the log file with a header.
        """
        try:
            import os

            addon_path = os.path.dirname(os.path.dirname(__file__))
            log_path = os.path.join(addon_path, "debug_sheets2anki.log")

            # Create file if it doesn't exist or add session separator
            separator = f"\n{'='*60}\n=== NEW DEBUG SESSION - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n{'='*60}\n"

            mode = "w" if not os.path.exists(log_path) else "a"
            with open(log_path, mode, encoding="utf-8") as f:
                if mode == "w":
                    f.write(
                        f"=== SHEETS2ANKI DEBUG LOG - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n"
                    )
                else:
                    f.write(separator)
                f.flush()

            # print(f"[DEBUG_FILE] Log initialized: {log_path}")
            pass

        except Exception as e:
            # We don't use add_debug_message here to avoid potential infinite recursion
            print(f"[DEBUG_FILE] Error initializing log: {e}")

    def get_log_path(self) -> str:
        """
        Returns the log file path.

        Returns:
            str: Full path to the log file
        """
        import os

        addon_path = os.path.dirname(os.path.dirname(__file__))
        return os.path.join(addon_path, "debug_sheets2anki.log")

    def get_recent_messages(self, count: int = 10) -> List[str]:
        """
        Returns the most recent messages.

        Args:
            count: Number of recent messages to return
        """
        return self.messages[-count:] if self.messages else []


# Global instance of the debug manager
debug_manager = DebugManager()


def add_debug_message(message: str, category: str = "DEBUG") -> None:
    """
    Convenience function to add debug messages.

    Args:
        message: Debug message
        category: Message category
    """
    debug_manager.add_message(message, category)


def is_debug_enabled() -> bool:
    """Checks if debug is enabled."""
    debug_manager._update_debug_status()
    return debug_manager.is_debug_enabled


def get_debug_messages() -> List[str]:
    """Returns all debug messages."""
    return debug_manager.get_messages()


def clear_debug_messages() -> None:
    """Clears all debug messages."""
    debug_manager.clear_messages()


def initialize_debug_log() -> None:
    """Initializes the debug log file."""
    debug_manager.initialize_log_file()


def get_debug_log_path() -> str:
    """Returns the debug log file path."""
    return debug_manager.get_log_path()


def clear_debug_log():
    """
    Clears the debug log file and starts a new one.
    """
    try:
        from datetime import datetime

        log_path = debug_manager.get_log_path()

        with open(log_path, "w", encoding="utf-8") as f:
            f.write(
                f"=== SHEETS2ANKI DEBUG LOG - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n"
            )

        # add_debug_message(f"Log cleared: {log_path}", "DEBUG")
        pass

    except Exception as e:
        # We don't use add_debug_message here to avoid potential infinite recursion
        print(f"[DEBUG] Error clearing log: {e}")


# =============================================================================
# SHARED DECK OPTIONS MANAGEMENT
# =============================================================================


# Removed obsolete debug_log function as it is redundant with DebugManager


# ========================================================================================
# VALIDATION FUNCTIONS (consolidated from validation.py)
# ========================================================================================


def convert_edit_url_to_tsv(url):
    """
    Converts Google Sheets edit URLs to TSV download format.
    
    Args:
        url (str): Google Sheets edit URL
        
    Returns:
        str: URL in TSV format for download
        
    Raises:
        ValueError: If the URL is not a valid edit URL
    """
    import re
    
    if not url or not isinstance(url, str):
        raise ValueError("URL must be a non-empty string")
    
    # Check if it's a Google Sheets URL
    if "docs.google.com/spreadsheets" not in url:
        raise ValueError("URL must be from Google Sheets")
    
    # Extract spreadsheet ID for edit URLs
    edit_pattern = r"https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)/edit"
    match = re.search(edit_pattern, url)
    
    if match:
        spreadsheet_id = match.group(1)
        # Convert to TSV export format (without gid to automatically download the first tab)
        return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=tsv"
    
    # If it reached here, it's not a valid edit URL
    raise ValueError(
        "URL must be a Google Sheets edit URL in the format:\n"
        "https://docs.google.com/spreadsheets/d/{ID}/edit?usp=sharing"
    )


def validate_url(url):
    """
    Validates if the URL is a valid Google Sheets edit URL.

    Args:
        url (str): The URL to be validated

    Returns:
        str: URL in valid TSV format for download

    Raises:
        ValueError: If the URL is invalid or inaccessible
        URLError: If there are network connectivity issues
        HTTPError: If the server returns a status error
    """
    import socket
    import urllib.error
    import urllib.request

    # Check if URL is not empty
    if not url or not isinstance(url, str):
        raise ValueError("URL must be a non-empty string")

    # Validate URL format
    if not url.startswith(("http://", "https://")):
        raise ValueError("Invalid URL: Must start with http:// or https://")

    # If URL is already in TSV format, return it directly
    if "/export?format=tsv" in url:
        return url

    # Convert to TSV format
    try:
        tsv_url = convert_edit_url_to_tsv(url)
    except ValueError as e:
        raise ValueError(f"Invalid URL: {str(e)}")

    # Test TSV URL accessibility with timeout and proper error handling
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Sheets2Anki) AnkiAddon"  # More specific user agent
        }
        request = urllib.request.Request(tsv_url, headers=headers)

        # USE LOCAL TIMEOUT instead of global it to avoid conflicts
        response = urllib.request.urlopen(request, timeout=30)  # ✅ LOCAL TIMEOUT

        if response.getcode() != 200:
            raise ValueError(
                f"URL returned unexpected status code: {response.getcode()}"
            )

        # Validate content type
        content_type = response.headers.get("Content-Type", "").lower()
        if not any(
            valid_type in content_type
            for valid_type in ["text/tab-separated-values", "text/plain", "text/csv"]
        ):
            raise ValueError(f"URL does not return TSV content (received {content_type})")

        # Return valid TSV URL
        return tsv_url

    except socket.timeout:
        raise ValueError(
            "Connection timeout when accessing the URL (30s). Check your connection or try again."
        )
    except urllib.error.HTTPError as e:
        if e.code == 400:
            raise ValueError(
                f"HTTP Error 400: The spreadsheet is not publicly accessible.\n\n"
                f"To fix:\n"
                f"1. Open the spreadsheet in Google Sheets\n"
                f"2. Click 'Share'\n"
                f"3. Change access to 'Anyone with the link'\n"
                f"4. Set permission to 'Viewer'\n\n"
                f"Alternatively: File → Share → Publish to the web"
            )
        else:
            raise ValueError(f"HTTP Error {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        if isinstance(e.reason, socket.timeout):
            raise ValueError(
                "Connection timeout when accessing the URL. Check your connection or try again."
            )
        elif isinstance(e.reason, socket.gaierror):
            raise ValueError("DNS Error. Check your internet connection.")
        else:
            raise ValueError(
                f"Error accessing URL - Network or server problem: {str(e.reason)}"
            )
    except Exception as e:
        raise ValueError(f"Unexpected error accessing URL: {str(e)}")


# ========================================================================================
# CUSTOM EXCEPTIONS (consolidated from exceptions.py)
# ========================================================================================


class SyncError(Exception):
    """Base exception for sync-related errors."""

    pass


class NoteProcessingError(SyncError):
    """Exception raised when processing a note fails."""

    pass


class CollectionSaveError(SyncError):
    """Exception raised when saving the collection fails."""

    pass


class ConfigurationError(Exception):
    """Exception raised for configuration-related issues."""

    pass


# =============================================================================
# SUBDECK FUNCTIONS (moved to avoid circular import)
# =============================================================================


def get_subdeck_name(main_deck_name, fields, student=None):
    """
    Generates subdeck name based on main deck and IMPORTANCE, TOPIC, SUBTOPIC and CONCEPT fields.

    Args:
        main_deck_name (str): Main deck name
        fields (dict): Note fields with IMPORTANCE, TOPIC, SUBTOPIC and CONCEPT
        student (str, optional): Student name to include in hierarchy

    Returns:
        str: Full subdeck name in the format "MainDeck::[Student::]Importance::Topic::Subtopic::Concept"
    """
    from . import templates_and_definitions as cols

    # Get field values, using default values if empty
    importancia = fields.get(cols.hierarchy_1, "").strip() or cols.DEFAULT_IMPORTANCE
    topico = fields.get(cols.hierarchy_2, "").strip() or cols.DEFAULT_TOPIC
    subtopico = fields.get(cols.hierarchy_3, "").strip() or cols.DEFAULT_SUBTOPIC
    conceito = fields.get(cols.hierarchy_4, "").strip() or cols.DEFAULT_CONCEPT

    # Create full subdeck hierarchy
    if student:
        # With student: Deck::Student::Importance::Topic::Subtopic::Concept
        return f"{main_deck_name}::{student}::{importancia}::{topico}::{subtopico}::{conceito}"
    else:
        # Without student: Deck::Importance::Topic::Subtopic::Concept (compatibility)
        return f"{main_deck_name}::{importancia}::{topico}::{subtopico}::{conceito}"


def ensure_subdeck_exists(deck_name):
    """
    Ensures that a subdeck exists, creating it if necessary.

    This function supports hierarchical names like "Deck::Subdeck::Subsubdeck".

    Args:
        deck_name (str): Full deck/subdeck name

    Returns:
        int: Deck/subdeck ID

    Raises:
        RuntimeError: If mw is not available
    """
    if not mw or not hasattr(mw, "col") or not mw.col:
        raise RuntimeError("Anki main window (mw) is not available")

    # Check if deck already exists
    did = mw.col.decks.id_for_name(deck_name)
    if did is not None:
        return did

    # If it doesn't exist, create deck and all necessary parent decks
    return mw.col.decks.id(deck_name)


def move_note_to_subdeck(note_id, subdeck_id):
    """
    Moves a note to a specific subdeck.

    Args:
        note_id (int): ID of the note to move
        subdeck_id (int): Destination subdeck ID

    Returns:
        bool: True if operation was successful, False otherwise

    Raises:
        RuntimeError: If mw is not available
    """
    if not mw or not hasattr(mw, "col") or not mw.col:
        raise RuntimeError("Anki main window (mw) is not available")

    try:
        # Get note
        note = mw.col.get_note(note_id)

        # Get all cards of the note using note ID search
        card_ids = mw.col.find_cards(f"nid:{note_id}")

        # Move each card to subdeck
        for card_id in card_ids:
            card = mw.col.get_card(card_id)
            card.did = subdeck_id
            card.flush()

        return True
    except Exception as e:
        add_debug_message(f"Error moving note to subdeck: {e}", "SUBDECK")
        return False


def remove_empty_subdecks(remote_decks):
    """
    Removes empty subdecks after synchronization.

    This function checks all subdecks of remote decks and removes those
    that contain no notes or cards.

    Args:
        remote_decks (dict): Remote decks dictionary

    Returns:
        int: Number of removed empty subdecks
    """
    if not mw or not hasattr(mw, "col") or not mw.col:
        return 0

    removed_count = 0
    processed_decks = set()

    # Collect all main decks to check their subdecks
    main_deck_ids = []
    for deck_info in remote_decks.values():
        local_deck_id = deck_info.get("local_deck_id")
        if local_deck_id and local_deck_id not in processed_decks:
            main_deck_ids.append(local_deck_id)
            processed_decks.add(local_deck_id)

    # For each main deck, check its subdecks
    for local_deck_id in main_deck_ids:
        deck = mw.col.decks.get(local_deck_id)
        if not deck:
            continue

        main_deck_name = deck["name"]

        # Find all subdecks of this main deck
        all_decks = mw.col.decks.all_names_and_ids()
        subdecks = [d for d in all_decks if d.name.startswith(main_deck_name + "::")]

        # Sort subdecks from deepest to shallowest to avoid dependency problems
        subdecks.sort(key=lambda d: d.name.count("::"), reverse=True)

        # Check each subdeck
        for subdeck in subdecks:
            # Count cards in subdeck
            escaped_subdeck_name = subdeck.name.replace('"', '\\"')
            card_count = len(mw.col.find_cards(f'deck:"{escaped_subdeck_name}"'))

            # If subdeck is empty, remove it
            if card_count == 0:
                try:
                    # Convert ID to type expected by Anki
                    subdeck_id = mw.col.decks.id(subdeck.name)
                    if subdeck_id is not None:
                        mw.col.decks.remove([subdeck_id])
                        removed_count += 1
                except Exception as e:
                    # Ignore subdeck removal errors
                    add_debug_message(f"Error removing subdeck: {e}", "SUBDECK")

    return removed_count
