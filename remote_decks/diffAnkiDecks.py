
try:
    from aqt.utils import showInfo
except:
    pass

from .libs.org_to_anki.ankiConnectWrapper.AnkiNoteBuilder import AnkiNoteBuilder

# Determine which field to use as the key for a note ("Text" or "Front")
def determine_key_field(note):
    if not isinstance(note, dict):
        return None
    fields = note.get("fields", {})
    if "Text" in fields:
        return "Text"
    elif "Front" in fields:
        return "Front"
    return None

def diffAnkiDecks(orgAnkiDeck, ankiBaseDeck):

    if not isinstance(ankiBaseDeck, dict):
        raise TypeError("AnkiBaseDeck, 2nd param, must be a dict")

    storedNotes = {}
    potentialKeys = set()
    for question in ankiBaseDeck.get("result", []):
        keyField = determine_key_field(question)
        potentialKeys.add(keyField)
        fields = question.get("fields", {})
        keyFieldDict = fields.get(keyField, {})
        key = keyFieldDict.get("value")
        if key is not None:
            storedNotes[key] = question

    newQuestions = []
    questionsUpdated = []
    removedQuestions = []

    noteBuilder = AnkiNoteBuilder()

    for question in orgAnkiDeck.getQuestions():
        builtQuestion = noteBuilder.buildNote(question)
        keyField = determine_key_field(builtQuestion)
        fields = builtQuestion.get("fields", {})
        key = fields.get(keyField)

        savedQuestion = storedNotes.get(key, None)
        questionAdded = False
        if savedQuestion is None:
            noteId = -1
            newQuestions.append({"question": question, "noteId": noteId})
            questionAdded = True

        if not questionAdded and savedQuestion is not None:
            # Updated question
            savedFields = savedQuestion.get("fields", {})
            for field_name in savedFields.keys():
                saved_value = savedFields.get(field_name, {}).get("value")
                built_value = fields.get(field_name)
                # built_value pode ser dict ou valor direto
                if isinstance(built_value, dict):
                    built_value = built_value.get("value")
                if saved_value != built_value:
                    noteId = savedQuestion.get("noteId", -1)
                    questionsUpdated.append({"question": question, "noteId": noteId})
                    break

    # Find question in Anki that have been deleted from remote source
    remoteQuestionKeys = set()
    for question in orgAnkiDeck.getQuestions():
        builtQuestion = noteBuilder.buildNote(question)
        fields = builtQuestion.get("fields", {})
        remoteQuestionKeys.add(fields.get("Front", None))
        remoteQuestionKeys.add(fields.get("Text", None))

    for note in storedNotes:
        storedNote = storedNotes.get(note)
        keyField = determine_key_field(storedNote)
        fields = storedNote.get("fields", {})
        keyFieldDict = fields.get(keyField, {})
        key = keyFieldDict.get("value")
        if key not in remoteQuestionKeys:
            noteId = storedNote.get("noteId", -1)
            removedQuestions.append({"question": storedNote, "noteId": noteId})

    return {
        "newQuestions": newQuestions,
        "questionsUpdated": questionsUpdated,
        "removedQuestions": removedQuestions
    }