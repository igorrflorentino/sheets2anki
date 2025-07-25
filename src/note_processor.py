"""
Processamento de notas para o addon Sheets2Anki.

Este módulo contém funções para criar, atualizar e
processar notas do Anki.
"""

from .card_templates import ensure_custom_models
from .parseRemoteDeck import has_cloze_deletion
from .exceptions import NoteProcessingError, CollectionSaveError, SyncError
from . import column_definitions
from .subdeck_manager import get_subdeck_name, ensure_subdeck_exists, move_note_to_subdeck

# Importar mw de forma segura
try:
    from .compat import mw
except ImportError:
    # Fallback para importação direta
    try:
        from aqt import mw
    except ImportError:
        mw = None

def create_or_update_notes(col, remoteDeck, deck_id):
    """
    Cria ou atualiza notas no deck baseado nos dados remotos.
    
    Esta função sincroniza o deck do Anki com os dados remotos através de:
    1. Criação de novas notas para itens que não existem no Anki
    2. Atualização de notas existentes com novo conteúdo da fonte remota
    3. Remoção de notas que não existem mais na fonte remota
    
    IMPORTANTE: Notas não marcadas para sincronização (SYNC? = false/0) são ignoradas
    durante a sincronização, não sendo criadas, atualizadas ou excluídas.
    
    Args:
        col: Objeto de coleção do Anki
        remoteDeck (RemoteDeck): Objeto do deck remoto contendo os dados para sincronizar
        deck_id (int): ID do deck do Anki para sincronizar
        
    Returns:
        dict: Estatísticas de sincronização contendo contagens para notas criadas,
              atualizadas, deletadas e erros
        
    Raises:
        SyncError: Se houver erros críticos durante a sincronização
        CollectionSaveError: Se falhar ao salvar a coleção
    """
    def note_needs_update(note, fields, tags):
        """Verifica se uma nota precisa ser atualizada."""
        # Comparar apenas os campos que devem estar nas notas (excluindo campos de controle)
        for field_name, value in fields.items():
            if field_name in column_definitions.NOTE_FIELDS and field_name in note:
                # Anki armazena campos como string
                if str(note[field_name]).strip() != str(value).strip():
                    return True
        # Comparar tags (ordem não importa)
        note_tags = set(note.tags) if hasattr(note, 'tags') else set()
        tsv_tags = set(tags) if tags else set()
        if note_tags != tsv_tags:
            return True
        return False

    def get_update_details(note, fields, tags):
        """Detecta e retorna detalhes específicos do que foi atualizado."""
        changes = []
        
        # Verificar mudanças nos campos
        for field_name, new_value in fields.items():
            if field_name in column_definitions.NOTE_FIELDS and field_name in note:
                old_value = str(note[field_name]).strip()
                new_value_str = str(new_value).strip()
                
                if old_value != new_value_str:
                    # Truncar valores longos para exibição
                    old_display = old_value[:50] + "..." if len(old_value) > 50 else old_value
                    new_display = new_value_str[:50] + "..." if len(new_value_str) > 50 else new_value_str
                    
                    changes.append(f"{field_name}: '{old_display}' → '{new_display}'")
        
        # Verificar mudanças nas tags
        note_tags = set(note.tags) if hasattr(note, 'tags') else set()
        tsv_tags = set(tags) if tags else set()
        
        if note_tags != tsv_tags:
            added_tags = tsv_tags - note_tags
            removed_tags = note_tags - tsv_tags
            
            if added_tags:
                changes.append(f"Tags adicionadas: {', '.join(added_tags)}")
            if removed_tags:
                changes.append(f"Tags removidas: {', '.join(removed_tags)}")
        
        return changes
    
    try:
        # Garantir que os modelos customizados existam
        models = ensure_custom_models(col, remoteDeck.url if hasattr(remoteDeck, 'url') else "")
        
        # Rastrear estatísticas de sincronização
        stats = {
            'created': 0,
            'updated': 0,
            'deleted': 0,
            'ignored': 0,
            'errors': 0,
            'error_details': [],
            'updated_details': []  # Lista das primeiras 10 atualizações
        }
        
        # Construir índice de notas existentes
        existing_notes = {}
        existing_note_ids = {}
        for nid in col.find_notes(f'deck:"{remoteDeck.deckName}"'):
            note = col.get_note(nid)
            key = note[column_definitions.ID] if column_definitions.ID in note else None
            if key:
                existing_notes[key] = note
                existing_note_ids[key] = nid

        # Rastrear chaves processadas para identificar exclusões
        processed_keys = set()
        
        # Primeiro, identificar TODAS as questões que ainda existem na planilha
        # (incluindo as não sincronizadas) para evitar excluir notas que apenas
        # não devem ser sincronizadas
        all_existing_keys_in_sheet = _get_all_question_keys_from_sheet(remoteDeck)

        # Processar cada pergunta da fonte remota
        for question in remoteDeck.questions:
            try:
                fields = question['fields']
                
                # Validar campos obrigatórios
                key = fields.get(column_definitions.ID)
                if not key:
                    raise NoteProcessingError("Row missing required ID field")
                
                if not fields.get(column_definitions.PERGUNTA):
                    raise NoteProcessingError(f"Row with ID {key} missing required question field")
                
                processed_keys.add(key)
                
                # Processar tags
                tags = question.get('tags', [])

                if key in existing_notes:
                    # Atualizar nota existente SOMENTE SE houver diferença real
                    note = existing_notes[key]
                    if note_needs_update(note, fields, tags):
                        # Capturar detalhes das mudanças ANTES de atualizar
                        if len(stats['updated_details']) < 10:  # Limitar a 10 atualizações
                            changes = get_update_details(note, fields, tags)
                            if changes:
                                pergunta = fields.get(column_definitions.PERGUNTA, "")
                                pergunta_display = pergunta[:100] + "..." if len(pergunta) > 100 else pergunta
                                
                                update_info = {
                                    'id': key,
                                    'pergunta': pergunta_display,
                                    'changes': changes
                                }
                                stats['updated_details'].append(update_info)
                        
                        for field_name, value in fields.items():
                            if field_name in column_definitions.NOTE_FIELDS and field_name in note:
                                note[field_name] = value
                        note.tags = tags
                        try:
                            # Verificar se devemos mover a nota para um subdeck
                            main_deck_name = remoteDeck.deckName
                            subdeck_name = get_subdeck_name(main_deck_name, fields)
                            
                            # Se o nome do subdeck é diferente do deck principal, mover para o subdeck
                            if subdeck_name != main_deck_name:
                                subdeck_id = ensure_subdeck_exists(subdeck_name)
                                # Primeiro salvar as alterações na nota
                                note.flush()
                                # Depois mover para o subdeck correto
                                move_note_to_subdeck(note.id, subdeck_id)
                            else:
                                # Apenas salvar a nota se não há subdeck
                                note.flush()
                                
                            stats['updated'] += 1
                        except Exception as e:
                            raise NoteProcessingError(f"Error updating note {key}: {str(e)}")
                else:
                    # Criar nova nota
                    has_cloze = has_cloze_deletion(fields[column_definitions.PERGUNTA])
                    model_to_use = models['cloze'] if has_cloze else models['standard']
                    
                    col.models.set_current(model_to_use)
                    model_to_use['did'] = deck_id
                    col.models.save(model_to_use)

                    note = col.new_note(model_to_use)
                    for field_name, value in fields.items():
                        if field_name in column_definitions.NOTE_FIELDS and field_name in note:
                            note[field_name] = value
                    note.tags = tags
                    
                    try:
                        # Verificar se devemos criar subdecks baseados em TOPICO e SUBTOPICO
                        main_deck_name = remoteDeck.deckName
                        subdeck_name = get_subdeck_name(main_deck_name, fields)
                        
                        # Se o nome do subdeck é diferente do deck principal, criar o subdeck
                        if subdeck_name != main_deck_name:
                            subdeck_id = ensure_subdeck_exists(subdeck_name)
                            # Adicionar a nota ao subdeck em vez do deck principal
                            col.add_note(note, subdeck_id)
                        else:
                            # Adicionar ao deck principal se não há subdeck
                            col.add_note(note, deck_id)
                            
                        stats['created'] += 1
                    except Exception as e:
                        raise NoteProcessingError(f"Error creating note {key}: {str(e)}")

            except NoteProcessingError as e:
                stats['errors'] += 1
                stats['error_details'].append(str(e))
                continue

        # Lidar com exclusões - apenas remover notas que não existem mais na planilha
        # Notas que existem na planilha mas não estão sincronizadas devem ser preservadas
        notes_to_delete = set(existing_notes.keys()) - all_existing_keys_in_sheet
        stats['deleted'] = len(notes_to_delete)

        if notes_to_delete:
            try:
                note_ids_to_delete = [existing_note_ids[key] for key in notes_to_delete]
                col.remove_notes(note_ids_to_delete)
            except Exception as e:
                raise NoteProcessingError(f"Error deleting notes: {str(e)}")

        # Salvar mudanças
        try:
            col.save()
        except Exception as e:
            raise CollectionSaveError(f"Error saving collection: {str(e)}")

        # Adicionar contagem de cards ignorados às estatísticas
        if hasattr(remoteDeck, 'ignored_count'):
            stats['ignored'] = remoteDeck.ignored_count
            
        # Atualizar a interface do Anki para refletir os novos subdecks
        if mw is not None and hasattr(mw, 'reset'):
            mw.reset()

        # Retornar estatísticas sem mostrar info
        return stats

    except SyncError as e:
        error_msg = f"Critical sync error: {str(e)}"
        raise SyncError(error_msg)
    except Exception as e:
        error_msg = f"Unexpected error during sync: {str(e)}"
        raise SyncError(error_msg)


def _get_all_question_keys_from_sheet(remoteDeck):
    """
    Extrai todas as chaves (IDs) de questões da planilha, incluindo
    as que não estão marcadas para sincronização.
    
    Args:
        remoteDeck: Objeto RemoteDeck contendo dados da planilha
        
    Returns:
        set: Conjunto de todas as chaves de questões que existem na planilha
    """
    from .parseRemoteDeck import getRemoteDeck
    from . import column_definitions as cols
    
    # Precisamos acessar os dados brutos da planilha, não apenas as questões filtradas
    # Para isso, vamos reprocessar a URL original sem filtros
    try:
        url = getattr(remoteDeck, 'url', None)
        if not url:
            return set()
        
        # Obter dados brutos da planilha
        import urllib.request
        import csv
        
        with urllib.request.urlopen(url) as response:
            content = response.read().decode('utf-8')
        
        # Processar TSV
        lines = content.strip().split('\n')
        if not lines:
            return set()
            
        # Detectar delimitador (TSV é o padrão)
        delimiter = '\t' if '\t' in lines[0] else ','
        reader = csv.reader(lines, delimiter=delimiter)
        
        # Processar headers
        headers = next(reader)
        if cols.ID not in headers:
            return set()
            
        id_index = headers.index(cols.ID)
        
        # Extrair todas as chaves (IDs) da planilha
        all_keys = set()
        for row in reader:
            if len(row) > id_index and row[id_index].strip():
                all_keys.add(row[id_index].strip())
        
        return all_keys
        
    except Exception:
        # Em caso de erro, retornar conjunto vazio para evitar exclusões acidentais
        return set()
