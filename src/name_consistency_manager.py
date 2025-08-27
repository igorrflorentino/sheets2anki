# NameConsistencyManager - Sistema de Consistência Automática de Nomes
# Este módulo garante que todos os nomes (decks, note types, deck options) estejam
# sempre consistentes com o remote_deck_name em todo o Anki.

from typing import Dict, List, Tuple, Optional, Any
from aqt import mw
from anki.decks import DeckId
from anki.models import NotetypeId

class NameConsistencyManager:
    """
    Classe responsável por garantir a consistência automática de nomes durante a sincronização.
    
    Implementa a lógica especificada para:
    1. Recriar strings de referência baseadas no remote_deck_name
    2. Comparar com nomes reais salvos no Anki
    3. Atualizar automaticamente se necessário
    """
    
    @staticmethod
    def generate_standard_names(remote_deck_name: str) -> Dict[str, Any]:
        """
        Gera todas as strings de referência padrão baseadas no remote_deck_name.
        
        Args:
            remote_deck_name: Nome do deck remoto (source of truth)
            
        Returns:
            Dict com todas as strings padrão: local_deck_name, note_types, deck_option_name
        """
        # 2. recriar local_deck_name no padrão "Sheets2Anki::{remote_deck_name}"
        local_deck_name = f"Sheets2Anki::{remote_deck_name}"
        
        # 3. recriar note_types no padrão "Sheets2Anki - {remote_deck_name} - {aluno} - Basic/Cloze"
        note_type_patterns = {
            'basic_template': f"Sheets2Anki - {remote_deck_name} - {{student}} - Basic",
            'cloze_template': f"Sheets2Anki - {remote_deck_name} - {{student}} - Cloze"
        }
        
        # 4. recriar deck_option_name no padrão "Sheets2Anki - {remote_deck_name}"
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
        Força a consistência de nomes conforme a lógica especificada.
        
        Args:
            deck_url: URL do deck remoto
            remote_deck_name: Nome remoto (source of truth)
            local_deck_id: ID do deck local no Anki
            note_types_config: Dict {note_type_id: current_name}
            debug_callback: Função para debug messages
            
        Returns:
            Dict com resultados da operação
        """
        def debug(message: str):
            if debug_callback:
                debug_callback(f"[NAME_CONSISTENCY] {message}")
        
        try:
            debug(f"🔧 Iniciando consistência de nomes para: '{remote_deck_name}'")
            
            # 1. Salvar remote_deck_name (já feito pelo chamador)
            # 2-4. Gerar strings de referência padrão
            standard_names = NameConsistencyManager.generate_standard_names(remote_deck_name)
            
            results = {
                'deck_updated': False,
                'note_types_updated': [],
                'deck_options_updated': False,
                'errors': []
            }
            
            # 5-6. Verificar e atualizar nome do deck local
            deck_result = NameConsistencyManager._enforce_deck_name_consistency(
                local_deck_id, 
                standard_names['local_deck_name'],
                debug
            )
            results['deck_updated'] = deck_result['updated']
            if deck_result.get('error'):
                results['errors'].append(deck_result['error'])
            
            # 7. Verificar e atualizar nomes dos note types
            note_types_result = NameConsistencyManager._enforce_note_types_consistency(
                deck_url,
                note_types_config,
                standard_names['note_type_patterns'],
                debug
            )
            results['note_types_updated'] = note_types_result['updated_types']
            results['errors'].extend(note_types_result.get('errors', []))
            
            # 8. Verificar e atualizar opções do deck (se modo individual)
            deck_options_result = NameConsistencyManager._enforce_deck_options_consistency(
                local_deck_id,
                standard_names['deck_option_name'],
                debug
            )
            results['deck_options_updated'] = deck_options_result['updated']
            if deck_options_result.get('error'):
                results['errors'].append(deck_options_result['error'])
            
            # Salvar mudanças na configuração
            # CORREÇÃO: Salvar se houve note types atualizados OU se meta.json foi atualizado
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
                
                # CRÍTICO: Também atualizar remote_decks em memória para evitar reversão
                if remote_decks is not None:
                    NameConsistencyManager.update_remote_decks_in_memory(
                        deck_url,
                        remote_decks,
                        standard_names['local_deck_name'],
                        note_types_result['final_note_types'],
                        debug
                    )
                
                if meta_json_changed and not results['note_types_updated']:
                    debug(f"📋 Meta.json atualizado para sincronizar com Anki")
            
            debug(f"✅ Consistência aplicada: deck={results['deck_updated']}, "
                  f"note_types={len(results['note_types_updated'])}, "
                  f"options={results['deck_options_updated']}")
            
            return results
            
        except Exception as e:
            error_msg = f"❌ Erro na consistência de nomes: {e}"
            debug(error_msg)
            return {'errors': [error_msg]}
    
    @staticmethod
    def _enforce_deck_name_consistency(
        local_deck_id: int, 
        expected_name: str,
        debug_callback
    ) -> Dict[str, Any]:
        """
        6. Caso o nome do deck local esteja diferente de local_deck_name, atualize.
        """
        try:
            if not mw or not mw.col:
                return {'updated': False, 'error': 'Anki não disponível'}
            
            deck = mw.col.decks.get(DeckId(local_deck_id))
            if not deck:
                return {'updated': False, 'error': f'Deck ID {local_deck_id} não encontrado'}
            
            current_name = deck['name']
            debug_callback(f"Deck atual: '{current_name}' vs esperado: '{expected_name}'")
            
            if current_name != expected_name:
                debug_callback(f"📝 Atualizando nome do deck: '{current_name}' → '{expected_name}'")
                deck['name'] = expected_name
                mw.col.decks.save(deck)
                debug_callback("✅ Nome do deck atualizado")
                return {'updated': True, 'old_name': current_name, 'new_name': expected_name}
            else:
                debug_callback("✅ Nome do deck já está correto")
                return {'updated': False}
                
        except Exception as e:
            return {'updated': False, 'error': f'Erro ao atualizar deck: {e}'}
    
    @staticmethod
    def _enforce_note_types_consistency(
        deck_url: str,
        current_note_types: Dict[str, str],
        name_patterns: Dict[str, str],
        debug_callback
    ) -> Dict[str, Any]:
        """
        7. Caso os nomes dos note types estejam diferentes das strings salvas para cada ID, atualize.
        """
        try:
            if not mw or not mw.col:
                return {'updated_types': [], 'errors': ['Anki não disponível']}
            
            # Obter lista de alunos habilitados
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
                        errors.append(f"Note type ID {note_type_id} não encontrado")
                        continue
                    
                    # Determinar nome esperado baseado no padrão
                    expected_name = NameConsistencyManager._determine_expected_note_type_name(
                        current_name, name_patterns, enabled_students
                    )
                    
                    if not expected_name:
                        # Manter nome atual se não conseguir determinar padrão
                        final_note_types[note_type_id_str] = current_name
                        continue
                    
                    debug_callback(f"Note type {note_type_id}: '{current_name}' vs '{expected_name}'")
                    
                    # Atualizar se necessário
                    if model['name'] != expected_name:
                        debug_callback(f"📝 Atualizando note type: '{model['name']}' → '{expected_name}'")
                        model['name'] = expected_name
                        mw.col.models.save(model)
                        updated_types.append({
                            'id': note_type_id,
                            'old_name': current_name,
                            'new_name': expected_name
                        })
                        final_note_types[note_type_id_str] = expected_name
                        debug_callback(f"✅ Note type {note_type_id} atualizado")
                    else:
                        # CORREÇÃO: Usar model['name'] em vez de current_name para sincronizar meta.json com Anki
                        actual_anki_name = model['name']
                        final_note_types[note_type_id_str] = actual_anki_name
                        
                        # Debug adicional para mostrar se meta.json precisa ser atualizado
                        if current_name != actual_anki_name:
                            debug_callback(f"📋 Note type {note_type_id} correto no Anki, atualizando meta.json: '{current_name}' → '{actual_anki_name}'")
                        else:
                            debug_callback(f"✅ Note type {note_type_id} já está correto")
                        
                except Exception as e:
                    error_msg = f"Erro ao processar note type {note_type_id_str}: {e}"
                    errors.append(error_msg)
                    debug_callback(f"❌ {error_msg}")
                    # Manter nome atual em caso de erro
                    final_note_types[note_type_id_str] = current_name
            
            return {
                'updated_types': updated_types,
                'final_note_types': final_note_types,
                'errors': errors
            }
            
        except Exception as e:
            return {'updated_types': [], 'errors': [f'Erro geral nos note types: {e}']}
    
    @staticmethod
    def _determine_expected_note_type_name(
        current_name: str,
        patterns: Dict[str, str],
        enabled_students: List[str]
    ) -> Optional[str]:
        """
        Determina o nome esperado de um note type baseado no padrão e aluno.
        """
        # Extrair aluno e tipo do nome atual
        if " - " not in current_name:
            return None
        
        parts = current_name.split(" - ")
        if len(parts) < 4:
            return None
        
        # O formato é: "Sheets2Anki - {remote_name} - {student} - {type}"
        # Mas remote_name pode conter hífens, então precisamos trabalhar de trás para frente
        
        # O último elemento é sempre o tipo (Basic/Cloze)
        note_type = parts[-1]
        
        # O penúltimo elemento é sempre o aluno
        student = parts[-2]
        
        # Verificar se é um aluno válido
        all_students = enabled_students + ["[MISSING A.]"]
        if student not in all_students:
            return None
        
        # Determinar padrão correto
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
        8. Caso o nome das opções do deck esteja diferente e modo seja "individual", atualize.
        """
        try:
            # Verificar se o modo é "individual"
            from .config_manager import get_deck_options_mode
            
            if get_deck_options_mode() != "individual":
                debug_callback("🔄 Modo de opções não é 'individual', pulando atualização")
                return {'updated': False, 'reason': 'mode_not_individual'}
            
            if not mw or not mw.col:
                return {'updated': False, 'error': 'Anki não disponível'}
            
            deck = mw.col.decks.get(DeckId(local_deck_id))
            if not deck:
                return {'updated': False, 'error': f'Deck ID {local_deck_id} não encontrado'}
            
            # Obter configuração atual das opções
            deck_config_id = deck.get('conf')
            if not deck_config_id or deck_config_id == 1:  # 1 = default config
                debug_callback("🔄 Deck usa configuração padrão, pulando atualização")
                return {'updated': False, 'reason': 'using_default_config'}
            
            deck_config = mw.col.decks.get_config(deck_config_id)
            if not deck_config:
                return {'updated': False, 'error': 'Configuração do deck não encontrada'}
            
            current_options_name = deck_config.get('name', '')
            debug_callback(f"Opções atuais: '{current_options_name}' vs esperado: '{expected_options_name}'")
            
            if current_options_name != expected_options_name:
                debug_callback(f"📝 Atualizando opções do deck: '{current_options_name}' → '{expected_options_name}'")
                deck_config['name'] = expected_options_name
                mw.col.decks.save(deck_config)
                debug_callback("✅ Opções do deck atualizadas")
                return {
                    'updated': True,
                    'old_name': current_options_name,
                    'new_name': expected_options_name
                }
            else:
                debug_callback("✅ Opções do deck já estão corretas")
                return {'updated': False}
                
        except Exception as e:
            return {'updated': False, 'error': f'Erro ao atualizar opções: {e}'}
    
    @staticmethod
    def _update_config_with_new_names(
        deck_url: str,
        local_deck_name: str,
        note_types: Dict[str, str],
        debug_callback
    ):
        """
        Atualiza o meta.json com os novos nomes aplicados.
        """
        try:
            from .config_manager import get_meta, save_meta, get_deck_hash
            
            meta = get_meta()
            deck_hash = get_deck_hash(deck_url)
            
            if "decks" in meta and deck_hash in meta["decks"]:
                # Atualizar local_deck_name
                meta["decks"][deck_hash]["local_deck_name"] = local_deck_name
                
                # Atualizar note_types
                meta["decks"][deck_hash]["note_types"] = note_types
                
                save_meta(meta)
                debug_callback("✅ Configuração atualizada no meta.json")
            else:
                debug_callback("❌ Deck não encontrado na configuração")
                
        except Exception as e:
            debug_callback(f"❌ Erro ao atualizar configuração: {e}")
    
    @staticmethod
    def update_remote_decks_in_memory(
        deck_url: str,
        remote_decks: Dict,
        local_deck_name: str,
        note_types: Dict[str, str],
        debug_callback
    ):
        """
        CRÍTICO: Atualiza também o dicionário remote_decks em memória
        para evitar que save_remote_decks() posterior reverta as mudanças.
        """
        try:
            from .config_manager import get_deck_hash
            
            deck_hash = get_deck_hash(deck_url)
            
            if deck_hash in remote_decks:
                # Atualizar local_deck_name no dicionário em memória
                remote_decks[deck_hash]["local_deck_name"] = local_deck_name
                
                # Atualizar note_types no dicionário em memória
                remote_decks[deck_hash]["note_types"] = note_types
                
                debug_callback("💾 Dicionário remote_decks em memória atualizado para evitar reversão")
            else:
                debug_callback("❌ Deck hash não encontrado no remote_decks em memória")
                
        except Exception as e:
            debug_callback(f"❌ Erro ao atualizar remote_decks em memória: {e}")
    
    @staticmethod
    def ensure_consistency_during_sync(deck_url: str, remote_decks: Optional[Dict] = None, debug_callback=None) -> Dict[str, Any]:
        """
        Função principal para garantir consistência durante a sincronização.
        Agora também verifica configurações de deck.
        
        Args:
            deck_url: URL do deck remoto
            remote_decks: Dicionário de decks em memória (para atualizar e evitar reversão)
            debug_callback: Função para debug messages
            
        Returns:
            Dict com resultados da operação
        """
        def debug(message: str):
            if debug_callback:
                debug_callback(f"[SYNC_CONSISTENCY] {message}")
        
        try:
            from .config_manager import (
                get_deck_remote_name, get_deck_local_id, get_deck_note_type_ids,
                ensure_deck_configurations_consistency
            )
            
            # 1. Verificar configurações de deck primeiro
            try:
                config_corrections = ensure_deck_configurations_consistency()
                if config_corrections > 0:
                    debug(f"🔧 Corrigidas {config_corrections} configurações de deck ausentes")
            except Exception as e:
                debug(f"⚠️ Erro ao verificar configurações de deck: {e}")
            
            # 2. Obter dados atuais da configuração
            remote_deck_name = get_deck_remote_name(deck_url)
            local_deck_id = get_deck_local_id(deck_url)
            note_types_config = get_deck_note_type_ids(deck_url)
            
            if not remote_deck_name:
                return {'errors': ['remote_deck_name não encontrado na configuração']}
            
            if not local_deck_id:
                return {'errors': ['local_deck_id não encontrado na configuração']}
            
            if not note_types_config:
                debug("⚠️ Nenhum note type configurado, pulando consistência de note types")
                note_types_config = {}
            
            debug(f"🔧 Garantindo consistência para: {remote_deck_name}")
            
            # 3. Aplicar consistência de nomes
            return NameConsistencyManager.enforce_name_consistency(
                deck_url=deck_url,
                remote_deck_name=remote_deck_name,
                local_deck_id=local_deck_id,
                note_types_config=note_types_config,
                remote_decks=remote_decks,
                debug_callback=debug
            )
            
        except Exception as e:
            error_msg = f"❌ Erro na consistência durante sync: {e}"
            debug(error_msg)
            return {'errors': [error_msg]}
