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

from .parseRemoteDeck import getRemoteDeck

def validate_url(url):
    """Validate that the URL is a proper Google Sheets TSV URL."""
    if not url.startswith(('http://', 'https://')):
        raise ValueError("Invalid URL: Must start with http:// or https://")
    
    if "output=tsv" not in url:
        raise ValueError("The provided URL does not appear to be a published TSV from Google Sheets.")
    
    # Test URL accessibility
    try:
        response = urllib.request.urlopen(url)
        if response.getcode() != 200:
            raise ValueError(f"URL returned status code {response.getcode()}")
    except Exception as e:
        raise ValueError(f"Error accessing URL: {str(e)}")

def syncDecks():
    """Synchronize all remote decks with their sources."""
    col = mw.col
    config = mw.addonManager.getConfig(__name__)
    if not config:
        config = {"remote-decks": {}}

    sync_errors = []
    decks_synced = 0

    for deckKey in config["remote-decks"].keys():
        try:
            currentRemoteInfo = config["remote-decks"][deckKey]
            deckName = currentRemoteInfo["deckName"]
            
            # Validate URL before attempting sync
            validate_url(currentRemoteInfo["url"])
            
            remoteDeck = getRemoteDeck(currentRemoteInfo["url"])
            remoteDeck.deckName = deckName
            deck_id = get_or_create_deck(col, deckName)
            create_or_update_notes(col, remoteDeck, deck_id)
            decks_synced += 1
            
        except Exception as e:
            error_msg = f"Failed to sync deck '{deckName}': {str(e)}"
            sync_errors.append(error_msg)
            continue

    # Show summary of sync results
    if sync_errors:
        error_summary = "\n".join(sync_errors)
        showInfo(f"Sync completed with errors:\n{error_summary}\n\nSuccessfully synced {decks_synced} deck(s).")
    else:
        showInfo(f"Successfully synced {decks_synced} deck(s).")

def get_or_create_deck(col, deckName):
    deck = col.decks.by_name(deckName)
    if deck is None:
        deck_id = col.decks.id(deckName)
    else:
        deck_id = deck["id"]
    return deck_id

def ensure_custom_model(col):
    """Ensure the custom model exists in Anki."""
    model_name = "CustomQuestionAnswer"
    model = col.models.by_name(model_name)
    
    if model is None:
        # Create new model
        model = col.models.new(model_name)
        
        # Define fields
        fields = [
            'ID', 'PERGUNTA', 'RESPOSTA_PROVA', 'RESPOSTA_RESUMIDA', 
            'RESPOSTA_COMPLETA', 'EXAMPLO1', 'EXAMPLO2', 'EXAMPLO3', 
            'TOPICO', 'SUBTOPICO', 'BANCAS', 'IMPORTANCIA', 'TAGS'
        ]
        
        for field in fields:
            template = col.models.new_field(field)
            col.models.add_field(model, template)
        
        # Add template
        template = col.models.new_template("Card 1")
        template['qfmt'] = """{{PERGUNTA}}
<hr>
<b>Tópico:</b> {{TOPICO}}<br>
<b>Subtópico:</b> {{SUBTOPICO}}<br>
<b>Bancas:</b> {{BANCAS}}<br>
<b>Importância:</b> {{IMPORTANCIA}}<br>
<b>Tags:</b> {{TAGS}}"""
        template['afmt'] = """{{FrontSide}}
<hr id="answer">
<b>Resposta da Prova:</b><br>
{{RESPOSTA_PROVA}}<br><br>
<b>Resposta Resumida:</b><br>
{{RESPOSTA_RESUMIDA}}<br><br>
<b>Resposta Completa:</b><br>
{{RESPOSTA_COMPLETA}}<br><br>
{{#EXAMPLO1}}
<b>Exemplo 1:</b><br>
{{EXAMPLO1}}<br><br>
{{/EXAMPLO1}}
{{#EXAMPLO2}}
<b>Exemplo 2:</b><br>
{{EXAMPLO2}}<br><br>
{{/EXAMPLO2}}
{{#EXAMPLO3}}
<b>Exemplo 3:</b><br>
{{EXAMPLO3}}<br><br>
{{/EXAMPLO3}}"""
        
        col.models.add_template(model, template)
        col.models.save(model)
    
    return model

def create_or_update_notes(col, remoteDeck, deck_id):
    """Create or update notes in the deck based on remote data."""
    # Ensure custom model exists
    model = ensure_custom_model(col)
    
    # Dictionaries for existing notes
    existing_notes = {}
    existing_note_ids = {}

    # Fetch existing notes in the deck
    for nid in col.find_notes(f'deck:"{remoteDeck.deckName}"'):
        note = col.get_note(nid)
        key = note['ID'] if 'ID' in note else None
        if key:
            existing_notes[key] = note
            existing_note_ids[key] = nid

    # Set to keep track of keys from Google Sheets
    gs_keys = set()
    update_count = 0
    create_count = 0
    error_count = 0

    for question in remoteDeck.questions:
        try:
            fields = question['fields']
            tags = []
            
            # Extract tags from the TAGS field and process them
            if 'TAGS' in fields and fields['TAGS']:
                tags = [tag.strip() for tag in fields['TAGS'].split('::') if tag.strip()]
            
            # Use ID as the key for tracking
            key = fields.get('ID')
            if not key:
                raise ValueError("Row missing required ID field")
                
            gs_keys.add(key)

            if key in existing_notes:
                # Update existing note
                note = existing_notes[key]
                for field_name in fields:
                    if field_name in note:
                        note[field_name] = fields[field_name]
                note.tags = tags
                try:
                    note.flush()
                    update_count += 1
                except Exception as e:
                    error_count += 1
                    raise ValueError(f"Error updating note: {str(e)}")
            else:
                # Create new note
                col.models.set_current(model)
                model['did'] = deck_id
                col.models.save(model)

                note = col.new_note(model)
                for field_name in fields:
                    if field_name in note:
                        note[field_name] = fields[field_name]
                note.tags = tags
                
                try:
                    col.add_note(note, deck_id)
                    create_count += 1
                except Exception as e:
                    error_count += 1
                    raise ValueError(f"Error creating note: {str(e)}")

        except Exception as e:
            error_count += 1
            showInfo(f"Error processing card: {str(e)}")
            continue

    # Find and remove notes that are in Anki but not in Google Sheets
    notes_to_delete = set(existing_notes.keys()) - gs_keys
    delete_count = len(notes_to_delete)

    if notes_to_delete:
        note_ids_to_delete = [existing_note_ids[key] for key in notes_to_delete]
        try:
            col.remove_notes(note_ids_to_delete)
        except Exception as e:
            error_count += 1
            showInfo(f"Error deleting notes: {str(e)}")

    # Save changes
    try:
        col.save()
    except Exception as e:
        error_count += 1
        showInfo(f"Error saving collection: {str(e)}")

    # Show summary
    summary = (f"Sync Summary:\n"
              f"Created: {create_count}\n"
              f"Updated: {update_count}\n"
              f"Deleted: {delete_count}\n"
              f"Errors: {error_count}")
    showInfo(summary)

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

    # Validate deck can be fetched
    try:
        deck = getRemoteDeck(url)
        deck.deckName = deckName
    except Exception as e:
        showInfo(f"Error fetching the remote deck:\n{str(e)}")
        return

    # Save configuration and sync
    try:
        config["remote-decks"][url] = {"url": url, "deckName": deckName}
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
    for url, info in remoteDecks.items():
        deck_name = info["deckName"]
        # Check if the deck still exists in Anki
        deck = mw.col.decks.by_name(deck_name)
        status = "Available" if deck else "Not found in Anki"
        deck_info.append(f"{deck_name} ({status})")

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
            # Extract deck name from selection (remove status)
            selected_deck_name = selection.split(" (")[0]

            # Find and remove the deck from config
            for url in list(remoteDecks.keys()):
                if selected_deck_name == remoteDecks[url]["deckName"]:
                    del remoteDecks[url]
                    break

            # Save the updated configuration
            mw.addonManager.writeConfig(__name__, config)

            # Show success message with instructions
            message = (
                f"The deck '{selected_deck_name}' has been unlinked from its remote source.\n\n"
                f"The local deck remains in Anki and can now be managed normally.\n"
                f"Future updates from the Google Sheet will no longer affect this deck."
            )
            showInfo(message)

        except Exception as e:
            showInfo(f"Error unlinking deck: {str(e)}")
            return
