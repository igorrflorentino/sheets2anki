# NameConsistencyManager - Automatic Name Consistency System
# This module ensures that all names (decks, note types, deck options) are
# always consistent with the remote_deck_name throughout Anki.

from typing import Dict, List, Tuple, Optional, Any
from aqt import mw
from anki.decks import DeckId
from anki.models import NotetypeId
from .templates_and_definitions import DEFAULT_STUDENT

class NameConsistencyManager:
    """
    Class responsible for ensuring automatic name consistency during synchronization.
    
    Implements the specified logic for:
    1. Recreating reference strings based on remote_deck_name
    2. Comparing with actual names saved in Anki
    3. Automatically updating if necessary
    """
    
    @staticmethod
    def generate_standard_names(remote_deck_name: str) -> Dict[str, Any]:
        """
        Generates all standard reference strings based on remote_deck_name.
        
        Args:
            remote_deck_name: Name of the remote deck (source of truth)
            
        Returns:
            Dict with all standard strings: local_deck_name, note_types, deck_option_name
        """
        # 2. recreate local_deck_name in the pattern "Sheets2Anki::{remote_deck_name}"
        local_deck_name = f"Sheets2Anki::{remote_deck_name}"
        
        # 3. recreate note_types in the pattern "Sheets2Anki - {remote_deck_name} - {student} - Basic/Cloze"
        note_type_patterns = {
            'basic_template': f"Sheets2Anki - {remote_deck_name} - {{student}} - Basic",
            'cloze_template': f"Sheets2Anki - {remote_deck_name} - {{student}} - Cloze"
        }
        
        # 4. recreate deck_option_name in the pattern "Sheets2Anki - {remote_deck_name}"
        deck_option_name = f"Sheets2Anki - {remote_deck_name}"
        
        return {
            'local_deck_name': local_deck_name,
            'note_type_patterns': note_type_patterns,
            'deck_option_name': deck_option_name
        }
    
    @staticmethod
    def enforce_name_consistency(
        deck_url: str, 
        remote_deck_name: str,
        local_deck_id: int,
        note_types_config: Dict[str, str],
        remote_decks: Optional[Dict] = None,
        debug_callback=None
    ) -> Dict[str, Any]:
        """
        Enforces name consistency according to the specified logic.
        
        Args:
            deck_url: URL of the remote deck
            remote_deck_name: Remote name (source of truth)
            local_deck_id: ID of the local deck in Anki
            note_types_config: Dict {note_type_id: current_name}
            debug_callback: Function for debug messages
            
        Returns:
            Dict with operation results
        """
        def debug(message: str):
            if debug_callback:
                debug_callback(f"[NAME_CONSISTENCY] {message}")
        
        try:
            debug(f"🔧 Starting name consistency for: '{remote_deck_name}'")
            
            # 1. Save remote_deck_name (already done by caller)
            # 2-4. Generate standard reference strings
            standard_names = NameConsistencyManager.generate_standard_names(remote_deck_name)
            
            results = {
                'deck_updated': False,
                'note_types_updated': [],
                'deck_options_updated': False,
                'errors': []
            }
            
            # 5-6. Check and update local deck name
            deck_result = NameConsistencyManager._enforce_deck_name_consistency(
                local_deck_id, 
                standard_names['local_deck_name'],
                debug
            )
            results['deck_updated'] = deck_result['updated']
            if deck_result.get('error'):
                results['errors'].append(deck_result['error'])
            
            # 7. Check and update note type names
            note_types_result = NameConsistencyManager._enforce_note_types_consistency(
                deck_url,
                note_types_config,
                standard_names['note_type_patterns'],
                debug
            )
            results['note_types_updated'] = note_types_result['updated_types']
            results['errors'].extend(note_types_result.get('errors', []))
            
            # 8. Check and update deck options (if individual mode)
            deck_options_result = NameConsistencyManager._enforce_deck_options_consistency(
                local_deck_id,
                standard_names['deck_option_name'],
                debug
            )
            results['deck_options_updated'] = deck_options_result['updated']
            if deck_options_result.get('error'):
                results['errors'].append(deck_options_result['error'])
            
            # Save changes to configuration
            # FIX: Save if note types were updated OR if meta.json was updated
            meta_json_changed = (
                note_types_result.get('final_note_types') and 
                any(note_types_result['final_note_types'].get(id_) != note_types_config.get(id_) 
                    for id_ in note_types_config.keys())
            )
            
            if results['note_types_updated'] or meta_json_changed:
                NameConsistencyManager._update_config_with_new_names(
                    deck_url,
                    standard_names['local_deck_name'],
                    note_types_result['final_note_types'],
                    debug
                )
                
                # CRITICAL: Also update remote_decks in memory to avoid reversion
                if remote_decks is not None:
                    NameConsistencyManager.update_remote_decks_in_memory(
                        deck_url,
                        remote_decks,
                        standard_names['local_deck_name'],
                        note_types_result['final_note_types'],
                        debug
                    )
                
                if meta_json_changed and not results['note_types_updated']:
                    debug(f"📋 Meta.json updated to sync with Anki")
            
            debug(f"✅ Consistency applied: deck={results['deck_updated']}, "
                  f"note_types={len(results['note_types_updated'])}, "
                  f"options={results['deck_options_updated']}")
            
            return results
            
        except Exception as e:
            error_msg = f"❌ Error in name consistency: {e}"
            debug(error_msg)
            return {'errors': [error_msg]}
    
    @staticmethod
    def _enforce_deck_name_consistency(
        local_deck_id: int, 
        expected_name: str,
        debug_callback
    ) -> Dict[str, Any]:
        """
        6. If the local deck name is different from local_deck_name, update it.
        """
        try:
            if not mw or not mw.col:
                return {'updated': False, 'error': 'Anki not available'}
            
            deck = mw.col.decks.get(DeckId(local_deck_id))
            if not deck:
                return {'updated': False, 'error': f'Deck ID {local_deck_id} not found'}
            
            current_name = deck['name']
            debug_callback(f"Current deck: '{current_name}' vs expected: '{expected_name}'")
            
            if current_name != expected_name:
                debug_callback(f"📝 Updating deck name: '{current_name}' → '{expected_name}'")
                deck['name'] = expected_name
                mw.col.decks.save(deck)
                debug_callback("✅ Deck name updated")
                return {'updated': True, 'old_name': current_name, 'new_name': expected_name}
            else:
                debug_callback("✅ Deck name is already correct")
                return {'updated': False}
                
        except Exception as e:
            return {'updated': False, 'error': f'Error updating deck: {e}'}
    
    @staticmethod
    def _enforce_note_types_consistency(
        deck_url: str,
        current_note_types: Dict[str, str],
        name_patterns: Dict[str, str],
        debug_callback
    ) -> Dict[str, Any]:
        """
        7. If note type names are different from saved strings for each ID, update them.
        """
        try:
            if not mw or not mw.col:
                return {'updated_types': [], 'errors': ['Anki not available']}
            
            # Get list of enabled students
            from .config_manager import get_enabled_students
            enabled_students = get_enabled_students()
            
            updated_types = []
            final_note_types = {}
            errors = []
            
            for note_type_id_str, current_name in current_note_types.items():
                try:
                    note_type_id = int(note_type_id_str)
                    model = mw.col.models.get(NotetypeId(note_type_id))
                    
                    if not model:
                        errors.append(f"Note type ID {note_type_id} not found")
                        continue
                    
                    # Determine expected name based on pattern
                    expected_name = NameConsistencyManager._determine_expected_note_type_name(
                        current_name, name_patterns, enabled_students
                    )
                    
                    if not expected_name:
                        # Keep current name if pattern cannot be determined
                        final_note_types[note_type_id_str] = current_name
                        continue
                    
                    debug_callback(f"Note type {note_type_id}: '{current_name}' vs '{expected_name}'")
                    
                    # Update if necessary
                    if model['name'] != expected_name:
                        debug_callback(f"📝 Updating note type: '{model['name']}' → '{expected_name}'")
                        model['name'] = expected_name
                        mw.col.models.save(model)
                        updated_types.append({
                            'id': note_type_id,
                            'old_name': current_name,
                            'new_name': expected_name
                        })
                        final_note_types[note_type_id_str] = expected_name
                        debug_callback(f"✅ Note type {note_type_id} updated")
                    else:
                        # FIX: Use model['name'] instead of current_name to sync meta.json with Anki
                        actual_anki_name = model['name']
                        final_note_types[note_type_id_str] = actual_anki_name
                        
                        # Additional debug to show if meta.json needs updating
                        if current_name != actual_anki_name:
                            debug_callback(f"📋 Note type {note_type_id} correct in Anki, updating meta.json: '{current_name}' → '{actual_anki_name}'")
                        else:
                            debug_callback(f"✅ Note type {note_type_id} is already correct")
                        
                except Exception as e:
                    error_msg = f"Error processing note type {note_type_id_str}: {e}"
                    errors.append(error_msg)
                    debug_callback(f"❌ {error_msg}")
                    # Keep current name in case of error
                    final_note_types[note_type_id_str] = current_name
            
            return {
                'updated_types': updated_types,
                'final_note_types': final_note_types,
                'errors': errors
            }
            
        except Exception as e:
            return {'updated_types': [], 'errors': [f'General error in note types: {e}']}
    
    @staticmethod
    def _determine_expected_note_type_name(
        current_name: str,
        patterns: Dict[str, str],
        enabled_students: List[str]
    ) -> Optional[str]:
        """
        Determines the expected name of a note type based on pattern and student.
        """
        # Extract student and type from current name
        if " - " not in current_name:
            return None
        
        parts = current_name.split(" - ")
        if len(parts) < 4:
            return None
        
        # Format is: "Sheets2Anki - {remote_name} - {student} - {type}"
        # But remote_name may contain hyphens, so we need to work backwards
        
        # Last element is always the type (Basic/Cloze)
        note_type = parts[-1]
        
        # Second to last element is always the student
        student = parts[-2]
        
        # Check if it's a valid student
        all_students = enabled_students + [DEFAULT_STUDENT]
        if student not in all_students:
            return None
        
        # Determine correct pattern
        if note_type == "Basic":
            pattern = patterns.get('basic_template')
        elif note_type == "Cloze":
            pattern = patterns.get('cloze_template')
        else:
            return None
        
        if pattern:
            return pattern.format(student=student)
        
        return None
    
    @staticmethod
    def _enforce_deck_options_consistency(
        local_deck_id: int,
        expected_options_name: str,
        debug_callback
    ) -> Dict[str, Any]:
        """
        8. If deck options name is different and mode is "individual", update it.
        """
        try:
            # Check if mode is "individual"
            from .config_manager import get_deck_options_mode
            
            if get_deck_options_mode() != "individual":
                debug_callback("🔄 Options mode is not 'individual', skipping update")
                return {'updated': False, 'reason': 'mode_not_individual'}
            
            if not mw or not mw.col:
                return {'updated': False, 'error': 'Anki not available'}
            
            deck = mw.col.decks.get(DeckId(local_deck_id))
            if not deck:
                return {'updated': False, 'error': f'Deck ID {local_deck_id} not found'}
            
            # Get current options configuration
            deck_config_id = deck.get('conf')
            if not deck_config_id or deck_config_id == 1:  # 1 = default config
                debug_callback("🔄 Deck uses default configuration, skipping update")
                return {'updated': False, 'reason': 'using_default_config'}
            
            deck_config = mw.col.decks.get_config(deck_config_id)
            if not deck_config:
                return {'updated': False, 'error': 'Deck configuration not found'}
            
            current_options_name = deck_config.get('name', '')
            debug_callback(f"Current options: '{current_options_name}' vs expected: '{expected_options_name}'")
            
            if current_options_name != expected_options_name:
                debug_callback(f"📝 Updating deck options: '{current_options_name}' → '{expected_options_name}'")
                deck_config['name'] = expected_options_name
                mw.col.decks.save(deck_config)
                debug_callback("✅ Deck options updated")
                return {
                    'updated': True,
                    'old_name': current_options_name,
                    'new_name': expected_options_name
                }
            else:
                debug_callback("✅ Deck options are already correct")
                return {'updated': False}
                
        except Exception as e:
            return {'updated': False, 'error': f'Error updating options: {e}'}
    
    @staticmethod
    def _update_config_with_new_names(
        deck_url: str,
        local_deck_name: str,
        note_types: Dict[str, str],
        debug_callback
    ):
        """
        Updates meta.json with the new applied names.
        """
        try:
            from .config_manager import get_meta, save_meta, get_deck_id
            
            meta = get_meta()
            spreadsheet_id = get_deck_id(deck_url)
            
            if "decks" in meta and spreadsheet_id in meta["decks"]:
                # Update local_deck_name
                meta["decks"][spreadsheet_id]["local_deck_name"] = local_deck_name
                
                # Update note_types
                meta["decks"][spreadsheet_id]["note_types"] = note_types
                
                save_meta(meta)
                debug_callback("✅ Configuration updated in meta.json")
            else:
                debug_callback("❌ Deck not found in configuration")
                
        except Exception as e:
            debug_callback(f"❌ Error updating configuration: {e}")
    
    @staticmethod
    def update_remote_decks_in_memory(
        deck_url: str,
        remote_decks: Dict,
        local_deck_name: str,
        note_types: Dict[str, str],
        debug_callback
    ):
        """
        CRITICAL: Also updates the remote_decks dictionary in memory
        to prevent save_remote_decks() from later reverting changes.
        """
        try:
            from .config_manager import get_deck_id
            
            spreadsheet_id = get_deck_id(deck_url)
            
            if spreadsheet_id in remote_decks:
                # Update local_deck_name in memory dictionary
                remote_decks[spreadsheet_id]["local_deck_name"] = local_deck_name
                
                # Update note_types in memory dictionary
                remote_decks[spreadsheet_id]["note_types"] = note_types
                
                debug_callback("💾 In-memory remote_decks dictionary updated to avoid reversion")
            else:
                debug_callback("❌ Deck hash not found in in-memory remote_decks")
                
        except Exception as e:
            debug_callback(f"❌ Error updating in-memory remote_decks: {e}")
    
    @staticmethod
    def ensure_consistency_during_sync(deck_url: str, remote_decks: Optional[Dict] = None, debug_callback=None) -> Dict[str, Any]:
        """
        Main function to ensure consistency during synchronization.
        Now also checks deck configurations.
        
        Args:
            deck_url: URL of the remote deck
            remote_decks: In-memory decks dictionary (to update and avoid reversion)
            debug_callback: Function for debug messages
            
        Returns:
            Dict with operation results
        """
        def debug(message: str):
            if debug_callback:
                debug_callback(f"[SYNC_CONSISTENCY] {message}")
        
        try:
            from .config_manager import (
                get_deck_remote_name, get_deck_local_id, get_deck_note_type_ids,
                ensure_deck_configurations_consistency
            )
            
            # 1. Check deck configurations first
            try:
                config_corrections = ensure_deck_configurations_consistency()
                if config_corrections > 0:
                    debug(f"🔧 Corrected {config_corrections} missing deck configurations")
            except Exception as e:
                debug(f"⚠️ Error checking deck configurations: {e}")
            
            # 2. Get current data from configuration
            remote_deck_name = get_deck_remote_name(deck_url)
            local_deck_id = get_deck_local_id(deck_url)
            note_types_config = get_deck_note_type_ids(deck_url)
            
            if not remote_deck_name:
                return {'errors': ['remote_deck_name not found in configuration']}
            
            if not local_deck_id:
                return {'errors': ['local_deck_id not found in configuration']}
            
            if not note_types_config:
                debug("⚠️ No note types configured, skipping note type consistency")
                note_types_config = {}
            
            debug(f"🔧 Ensuring consistency for: {remote_deck_name}")
            
            # 3. Apply name consistency
            return NameConsistencyManager.enforce_name_consistency(
                deck_url=deck_url,
                remote_deck_name=remote_deck_name,
                local_deck_id=local_deck_id,
                note_types_config=note_types_config,
                remote_decks=remote_decks,
                debug_callback=debug
            )
            
        except Exception as e:
            error_msg = f"❌ Error in consistency during sync: {e}"
            debug(error_msg)
            return {'errors': [error_msg]}
