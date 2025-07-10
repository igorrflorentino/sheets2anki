"""
Exceções customizadas para o addon Sheets2Anki.

Este módulo define todas as exceções específicas utilizadas
no processo de sincronização de decks.
"""

class SyncError(Exception):
    """Base exception for sync-related errors."""
    pass

class NoteProcessingError(SyncError):
    """Exception raised when processing a note fails."""
    pass

class CollectionSaveError(SyncError):
    """Exception raised when saving the collection fails."""
    pass
