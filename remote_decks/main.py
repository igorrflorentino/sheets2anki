from aqt import mw
from aqt.utils import showInfo, qconnect
from aqt.qt import QAction, QMenu, QInputDialog, QLineEdit, QKeySequence

try:
    echo_mode_normal = QLineEdit.EchoMode.Normal
except AttributeError:
    echo_mode_normal = QLineEdit.Normal

import sys
import csv
import urllib.request

from .parseRemoteDeck import getRemoteDeck, has_cloze_deletion
from . import column_definitions
import hashlib

# URLs hardcoded para testes e simulações
TEST_SHEETS_URLS = [
    ("Mais importantes", "https://docs.google.com/spreadsheets/d/e/2PACX-1vSART0Xw_lDq5bn4bylNox7vxOmU6YkoOjOwqdS3kZ-O1JEBLR8paqDv_bcGTW55yXchaO0jzK2cB8x/pub?gid=334628680&output=tsv"),
    ("Menos importantes", "https://docs.google.com/spreadsheets/d/e/2PACX-1vSART0Xw_lDq5bn4bylNox7vxOmU6YkoOjOwqdS3kZ-O1JEBLR8paqDv_bcGTW55yXchaO0jzK2cB8x/pub?gid=1869088045&output=tsv"),
]

def import_test_deck():
    """Permite importar rapidamente um dos decks de teste hardcoded."""
    names = [name for name, url in TEST_SHEETS_URLS]
    selection, okPressed = QInputDialog.getItem(
        mw,
        "Importar Deck de Teste",
        "Escolha um deck de teste para importar:",
        names,
        0,
        False
    )
    if not okPressed or not selection:
        return

    # Busca a URL correspondente
    url = dict(TEST_SHEETS_URLS)[selection]

    # Sugere um nome padrão para o deck
    deckName = f"Deck de Teste do sheet2anki:: {selection}"

    # Cria ou obtém o deck
    deck_id = get_or_create_deck(mw.col, deckName)

    # Busca e importa o deck
    try:
        validate_url(url)
        deck = getRemoteDeck(url)
        deck.deckName = deckName
        deck.url = url

        # Atualiza configuração e sincroniza
        config = mw.addonManager.getConfig(__name__)
        if not config:
            config = {"remote-decks": {}}
        config["remote-decks"][url] = {
            "url": url,
            "deck_id": deck_id,
            "deck_name": deckName
        }
        mw.addonManager.writeConfig(__name__, config)
        syncDecks()
    except (ValueError, SyncError) as e:
        showInfo(f"Erro ao importar deck de teste:\n{str(e)}")
    except Exception as e:
        showInfo(f"Erro inesperado ao importar deck de teste:\n{str(e)}")

def validate_url(url):
    """
    Validate that the URL is a proper Google Sheets TSV URL.
    
    Args:
        url (str): The URL to validate
        
    Raises:
        ValueError: If the URL is invalid or inaccessible
        URLError: If there are network connectivity issues
        HTTPError: If the server returns an error status
    """
    # Check if URL is empty or None
    if not url or not isinstance(url, str):
        raise ValueError("URL must be a non-empty string")

    # Validate URL format
    if not url.startswith(('http://', 'https://')):
        raise ValueError("Invalid URL: Must start with http:// or https://")
    
    # Validate Google Sheets TSV format
    if not any(param in url.lower() for param in ['output=tsv', 'format=tsv']):
        raise ValueError("The provided URL does not appear to be a published TSV from Google Sheets. "
                        "Make sure to publish the sheet as TSV format.")
    
    # Test URL accessibility with proper timeout and error handling
    try:
        request = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0'}  # Some servers block default Python user agent
        )
        response = urllib.request.urlopen(request, timeout=10)
        
        if response.getcode() != 200:
            raise ValueError(f"URL returned unexpected status code: {response.getcode()}")
            
        # Validate content type
        content_type = response.headers.get('Content-Type', '').lower()
        if not any(valid_type in content_type for valid_type in ['text/tab-separated-values', 'text/plain']):
            raise ValueError(f"URL does not return TSV content (got {content_type})")
            
    except urllib.error.URLError as e:
        raise ValueError(f"Error accessing URL - Network or server issue: {str(e)}")
    except urllib.error.HTTPError as e:
        raise ValueError(f"HTTP Error {e.code}: {str(e)}")
    except TimeoutError:
        raise ValueError("Connection timed out while accessing the URL")
    except Exception as e:
        raise ValueError(f"Unexpected error accessing URL: {str(e)}")
    
def syncDecks():
    """Synchronize all remote decks with their sources."""
    col = mw.col
    config = mw.addonManager.getConfig(__name__)
    if not config:
        config = {"remote-decks": {}}

    sync_errors = []
    decks_synced = 0

    # Use list to avoid RuntimeError (dict changed size during iteration)
    for deckKey in list(config["remote-decks"].keys()):
        try:
            currentRemoteInfo = config["remote-decks"][deckKey]
            deck_id = currentRemoteInfo["deck_id"]

            # Get deck name for display purposes
            deck = col.decks.get(deck_id)
            # If the deck does not exist or is now the Default deck, remove from config and skip sync
            if not deck or deck["name"].strip().lower() == "default":
                removed_name = currentRemoteInfo.get("deck_name", str(deck_id))
                del config["remote-decks"][deckKey]
                mw.addonManager.writeConfig(__name__, config)
                info_msg = f"A sincronização do deck '{removed_name}' foi encerrada automaticamente porque o deck foi excluído ou virou o deck padrão (Default)."
                showInfo(info_msg)
                continue
            deckName = deck["name"]

            # Validate URL before attempting sync
            validate_url(currentRemoteInfo["url"])

            remoteDeck = getRemoteDeck(currentRemoteInfo["url"])
            remoteDeck.deckName = deckName  # Set name for display purposes
            remoteDeck.url = currentRemoteInfo["url"]

            create_or_update_notes(col, remoteDeck, deck_id)
            decks_synced += 1

        except (ValueError, SyncError) as e:
            error_msg = f"Failed to sync deck '{deckName if 'deckName' in locals() else deck_id}': {str(e)}"
            sync_errors.append(error_msg)
            continue
        except Exception as e:
            error_msg = f"Unexpected error syncing deck '{deckName if 'deckName' in locals() else deck_id}': {str(e)}"
            sync_errors.append(error_msg)
            continue

    # Show summary of sync results
    if sync_errors:
        error_summary = "\n".join(sync_errors)
        showInfo(f"Sync completed with errors:\n{error_summary}\n\nSuccessfully synced {decks_synced} deck(s).")
    else:
        showInfo(f"Successfully synced {decks_synced} deck(s).")

def get_or_create_deck(col, deckName):
    if not deckName or not isinstance(deckName, str) or deckName.strip() == "" or deckName.strip().lower() == "default":
        raise ValueError("Nome de deck inválido ou proibido para sincronização: '%s'" % deckName)
    deck = col.decks.by_name(deckName)
    if deck is None:
        try:
            deck_id = col.decks.id(deckName)
        except Exception as e:
            raise ValueError(f"Não foi possível criar o deck '{deckName}': {str(e)}")
    else:
        deck_id = deck["id"]
    return deck_id

def get_model_suffix_from_url(url):
    """Gera um sufixo único e curto baseado na URL."""
    return hashlib.sha1(url.encode()).hexdigest()[:8]

# Template constants
CARD_SHOW_ALLWAYS_TEMPLATE = """
<b>{field_name}:</b><br>
{{{{{field_value}}}}}<br><br>
"""

CARD_SHOW_HIDE_TEMPLATE = """
{{{{#{field_value}}}}}
<b>{field_name}:</b><br>
{{{{{field_value}}}}}<br><br>
{{{{/{field_value}}}}}
"""

def create_card_template(is_cloze=False):
    """
    Create the HTML template for a card (either standard or cloze).
    
    Args:
        is_cloze (bool): Whether to create a cloze template
        
    Returns:
        dict: Dictionary with 'qfmt' and 'afmt' template strings
    """
    # Common header fields
    header_fields = [
        (column_definitions.TOPICO, column_definitions.TOPICO),
        (column_definitions.SUBTOPICO, column_definitions.SUBTOPICO),
    ]
    
    # Build header section
    header = ""
    for field_name, field_value in header_fields:
        header += CARD_SHOW_ALLWAYS_TEMPLATE.format(
            field_name=field_name.capitalize(),
            field_value=field_value
        )
    
    # Question format
    question = (
        "<hr><br>"
        f"<b>{column_definitions.PERGUNTA.capitalize()}:</b><br>"
        f"{{{{{'cloze:' if is_cloze else ''}{column_definitions.PERGUNTA}}}}}"
    )

    # Match format
    match = (
        "<br><br>"
        f"<b>{column_definitions.MATCH.capitalize()}:</b><br>"
        f"{{{{{'cloze:' if is_cloze else ''}{column_definitions.MATCH}}}}}"
        "<br><br><hr><br>"
    )

    # Extra Info format
    extra_info_fields = [
        column_definitions.EXTRA_INFO_1,
        column_definitions.EXTRA_INFO_2
    ]
    
    extra_info = ""
    for field in extra_info_fields:
        extra_info += CARD_SHOW_HIDE_TEMPLATE.format(
            field_name=field.capitalize(),
            field_value=field
        )
    
    # Example fields
    example_fields = [
        column_definitions.EXEMPLO_1,
        column_definitions.EXEMPLO_2,
        column_definitions.EXEMPLO_3
    ]
    
    examples = ""
    for field in example_fields:
        examples += CARD_SHOW_HIDE_TEMPLATE.format(
            field_name=field.capitalize(),
            field_value=field
        )

    # Footer fields
    footer_fields = [
        (column_definitions.BANCAS, column_definitions.BANCAS),
        (column_definitions.ANO, column_definitions.ANO),
        (column_definitions.MORE_TAGS, column_definitions.MORE_TAGS)
    ]

    # Build footer section
    footer = ""
    for field_name, field_value in footer_fields:
        footer += CARD_SHOW_HIDE_TEMPLATE.format(
            field_name=field_name.capitalize(),
            field_value=field_value
        )
    
    # Build complete templates
    qfmt = header + question
    afmt = (header + 
            question + 
            match + 
            extra_info + 
            examples + 
            "<hr><br>" + 
            footer) if is_cloze else ("{{FrontSide}}" + 
                                      match + 
                                      extra_info + 
                                      examples + 
                                      "<hr><br>" + 
                                      footer)

    return {'qfmt': qfmt, 'afmt': afmt}

def create_model(col, model_name, is_cloze=False):
    """
    Create a new Anki note model.
    
    Args:
        col: Anki collection object
        model_name (str): Name for the new model
        is_cloze (bool): Whether to create a cloze model
        
    Returns:
        object: The created Anki model
    """
    model = col.models.new(model_name)
    if is_cloze:
        model['type'] = 1  # Set as cloze type
    
    # Add fields
    for field in column_definitions.REQUIRED_COLUMNS:
        template = col.models.new_field(field)
        col.models.add_field(model, template)
    
    # Add card template
    template = col.models.new_template("Cloze" if is_cloze else "Card 1")
    card_template = create_card_template(is_cloze)
    template['qfmt'] = card_template['qfmt']
    template['afmt'] = card_template['afmt']
    
    col.models.add_template(model, template)
    col.models.save(model)
    return model

def ensure_custom_models(col, url):
    """
    Ensure both standard and cloze models exist in Anki.
    
    Args:
        col: Anki collection object
        url (str): URL of the remote deck
        
    Returns:
        dict: Dictionary containing both 'standard' and 'cloze' models
    """
    models = {}
    suffix = get_model_suffix_from_url(url)
    
    # Standard model
    model_name = f"CadernoErrosConcurso_{suffix}_Basic"
    model = col.models.by_name(model_name)
    if model is None:
        model = create_model(col, model_name)
    models['standard'] = model
    
    # Cloze model
    cloze_model_name = f"CadernoErrosConcurso_{suffix}_Cloze"
    cloze_model = col.models.by_name(cloze_model_name)
    if cloze_model is None:
        cloze_model = create_model(col, cloze_model_name, is_cloze=True)
    models['cloze'] = cloze_model
    
    return models
        
class SyncError(Exception):
    """Base exception for sync-related errors."""
    pass

class NoteProcessingError(SyncError):
    """Exception raised when processing a note fails."""
    pass

class CollectionSaveError(SyncError):
    """Exception raised when saving the collection fails."""
    pass

def create_or_update_notes(col, remoteDeck, deck_id):
    """
    Create or update notes in the deck based on remote data.
    
    This function synchronizes the Anki deck with the remote data by:
    1. Creating new notes for items that don't exist in Anki
    2. Updating existing notes with new content from the remote source
    3. Removing notes that no longer exist in the remote source
    
    Args:
        col: Anki collection object
        remoteDeck (RemoteDeck): Remote deck object containing the data to sync
        deck_id (int): ID of the Anki deck to sync with
        
    Returns:
        dict: Sync statistics containing counts for created, updated, deleted notes and errors
        
    Raises:
        SyncError: If there are critical errors during synchronization
        CollectionSaveError: If saving the collection fails
    """
    try:
        # Ensure custom models exist
        models = ensure_custom_models(col, remoteDeck.url)
        
        # Track sync statistics
        stats = {
            'created': 0,
            'updated': 0,
            'deleted': 0,
            'errors': 0,
            'error_details': []
        }
        
        # Build index of existing notes
        existing_notes = {}
        existing_note_ids = {}
        for nid in col.find_notes(f'deck:"{remoteDeck.deckName}"'):
            note = col.get_note(nid)
            key = note[column_definitions.ID] if column_definitions.ID in note else None
            if key:
                existing_notes[key] = note
                existing_note_ids[key] = nid

        # Track processed keys to identify deletions
        processed_keys = set()

        # Process each question from remote source
        for question in remoteDeck.questions:
            try:
                fields = question['fields']
                
                # Validate required fields
                key = fields.get(column_definitions.ID)
                if not key:
                    raise NoteProcessingError("Row missing required ID field")
                
                if not fields.get(column_definitions.PERGUNTA):
                    raise NoteProcessingError(f"Row with ID {key} missing required question field")
                
                processed_keys.add(key)
                
                # Process tags
                tags = question.get('tags', [])

                if key in existing_notes:
                    # Update existing note
                    note = existing_notes[key]
                    for field_name, value in fields.items():
                        if field_name in note:
                            note[field_name] = value
                    note.tags = tags
                    try:
                        note.flush()
                        stats['updated'] += 1
                    except Exception as e:
                        raise NoteProcessingError(f"Error updating note {key}: {str(e)}")
                else:
                    # Create new note
                    has_cloze = has_cloze_deletion(fields[column_definitions.PERGUNTA])
                    model_to_use = models['cloze'] if has_cloze else models['standard']
                    
                    col.models.set_current(model_to_use)
                    model_to_use['did'] = deck_id
                    col.models.save(model_to_use)

                    note = col.new_note(model_to_use)
                    for field_name, value in fields.items():
                        if field_name in note:
                            note[field_name] = value
                    note.tags = tags
                    
                    try:
                        col.add_note(note, deck_id)
                        stats['created'] += 1
                    except Exception as e:
                        raise NoteProcessingError(f"Error creating note {key}: {str(e)}")

            except NoteProcessingError as e:
                stats['errors'] += 1
                stats['error_details'].append(str(e))
                continue

        # Handle deletions
        notes_to_delete = set(existing_notes.keys()) - processed_keys
        stats['deleted'] = len(notes_to_delete)

        if notes_to_delete:
            try:
                note_ids_to_delete = [existing_note_ids[key] for key in notes_to_delete]
                col.remove_notes(note_ids_to_delete)
            except Exception as e:
                raise NoteProcessingError(f"Error deleting notes: {str(e)}")

        # Save changes
        try:
            col.save()
        except Exception as e:
            raise CollectionSaveError(f"Error saving collection: {str(e)}")

        # Show summary
        summary = (
            f"Sync Summary:\n"
            f"Created: {stats['created']}\n"
            f"Updated: {stats['updated']}\n"
            f"Deleted: {stats['deleted']}\n"
            f"Errors: {stats['errors']}"
        )
        if stats['error_details']:
            summary += "\n\nError Details:\n" + "\n".join(stats['error_details'])
        
        showInfo(summary)
        return stats

    except SyncError as e:
        error_msg = f"Critical sync error: {str(e)}"
        showInfo(error_msg)
        raise
    except Exception as e:
        error_msg = f"Unexpected error during sync: {str(e)}"
        showInfo(error_msg)
        raise SyncError(error_msg)

def get_note_key(note):
    """Get the key field from a note based on its type."""
    if "Text" in note:
        return note["Text"]
    elif "Front" in note:
        return note["Front"]
    return None

def addNewDeck():
    """Add a new remote deck from a Google Sheets TSV URL."""
    url, okPressed = QInputDialog.getText(
        mw, "Add New Remote Deck", "URL of published TSV:", echo_mode_normal, ""
    )
    if not okPressed or not url.strip():
        return

    url = url.strip()

    try:
        # Validate URL format and accessibility
        validate_url(url)
    except ValueError as e:
        showInfo(str(e))
        return

    # Get deck name
    deckName, okPressed = QInputDialog.getText(
        mw, "Deck Name", "Enter the name of the deck:", echo_mode_normal, ""
    )
    if not okPressed:
        return
    
    deckName = deckName.strip()
    if not deckName:
        deckName = "Deck from CSV"

    # Check configuration
    config = mw.addonManager.getConfig(__name__)
    if not config:
        config = {"remote-decks": {}}

    # Check if URL is already in use
    if url in config["remote-decks"]:
        showInfo(f"This URL has already been added as a remote deck.")
        return

    # Create or get deck ID
    deck_id = get_or_create_deck(mw.col, deckName)

    # Validate deck can be fetched
    try:
        deck = getRemoteDeck(url)
        deck.deckName = deckName
        deck.url = url
    except Exception as e:
        showInfo(f"Error fetching the remote deck:\n{str(e)}")
        return

    # Save configuration and sync
    try:
        config["remote-decks"][url] = {
            "url": url,
            "deck_id": deck_id,
            "deck_name": deckName
        }
        mw.addonManager.writeConfig(__name__, config)
        syncDecks()
    except Exception as e:
        showInfo(f"Error saving deck configuration:\n{str(e)}")
        # Remove failed configuration
        if url in config["remote-decks"]:
            del config["remote-decks"][url]
            mw.addonManager.writeConfig(__name__, config)

def removeRemoteDeck():
    """Remove a remote deck from the configuration while keeping the local deck."""
    config = mw.addonManager.getConfig(__name__)
    if not config:
        config = {"remote-decks": {}}

    remoteDecks = config["remote-decks"]

    # Check if there are any remote decks
    if not remoteDecks:
        showInfo("There are currently no remote decks configured.")
        return

    # Get all deck names and their URLs
    deck_info = []
    deck_map = {}  # Map display strings to URL keys
    for url, info in remoteDecks.items():
        deck_id = info["deck_id"]
        # Check if the deck still exists in Anki
        deck = mw.col.decks.get(deck_id)
        if deck:
            deck_name = deck["name"]
            status = "Available"
        else:
            deck_name = f"Unknown (ID: {deck_id})"
            status = "Not found in Anki"
            
        display_str = f"{deck_name} ({status})"
        deck_info.append(display_str)
        deck_map[display_str] = url

    # Ask user to select a deck
    selection, okPressed = QInputDialog.getItem(
        mw,
        "Select a Deck to Unlink",
        "Select a deck to unlink from remote source:\n(The local deck will remain in Anki)",
        deck_info,
        0,
        False
    )

    if okPressed and selection:
        try:
            # Get URL from selection using our map
            url = deck_map[selection]
            
            # Get deck name for display
            deck_id = remoteDecks[url]["deck_id"]
            deck = mw.col.decks.get(deck_id)
            deck_name = deck["name"] if deck else f"Unknown (ID: {deck_id})"
            
            # Remove the deck from config
            del remoteDecks[url]

            # Save the updated configuration
            mw.addonManager.writeConfig(__name__, config)

            # Show success message with instructions
            message = (
                f"The deck '{deck_name}' has been unlinked from its remote source.\n\n"
                f"The local deck remains in Anki and can now be managed normally.\n"
                f"Future updates from the Google Sheet will no longer affect this deck."
            )
            showInfo(message)

        except Exception as e:
            showInfo(f"Error unlinking deck: {str(e)}")
            return