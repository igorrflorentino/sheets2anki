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

def create_or_update_notes(col, remoteDeck, deck_id, deck_url=None, debug_messages=None):
    """
    Cria ou atualiza notas no deck baseado nos dados remotos.
    
    Esta função sincroniza o deck do Anki com os dados remotos através de:
    1. Criação de novas notas para itens que não existem no Anki
    2. Atualização de notas existentes com novo conteúdo da fonte remota
    3. Remoção de notas que não existem mais na fonte remota
    4. Gerenciamento de alunos selecionados e subdecks por aluno
    
    IMPORTANTE: Notas não marcadas para sincronização (SYNC? = false/0) são ignoradas
    durante a sincronização, não sendo criadas, atualizadas ou excluídas.
    
    Args:
        col: Objeto de coleção do Anki
        remoteDeck (RemoteDeck): Objeto do deck remoto contendo os dados para sincronizar
        deck_id (int): ID do deck do Anki para sincronizar
        deck_url (str, optional): URL do deck para gerenciar alunos
        
    Returns:
        dict: Estatísticas de sincronização contendo contagens para notas criadas,
              atualizadas, deletadas e erros
        
    Raises:
        SyncError: Se houver erros críticos durante a sincronização
        CollectionSaveError: Se falhar ao salvar a coleção
    """
    
    print(f"🚀 CREATE_OR_UPDATE_NOTES: Processando {len(remoteDeck.questions) if hasattr(remoteDeck, 'questions') and remoteDeck.questions else 0} questões para deck {deck_id}")
    
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
        # Gerenciar seleção de alunos usando configuração global
        selected_students = set()
        all_students_in_sheet = set()
        use_student_management = False
        
        print(f"🔍 NOTE_PROCESSOR: Iniciando gerenciamento de alunos...")
        print(f"  • deck_url: {deck_url}")
        print(f"  • Total questões inicial: {len(remoteDeck.questions) if hasattr(remoteDeck, 'questions') else 'N/A'}")
        
        if deck_url:
            try:
                print(f"🔍 NOTE_PROCESSOR: Importando funções do student_manager...")
                from .student_manager import (
                    extract_students_from_remote_data, 
                    filter_questions_by_selected_students,
                    remove_notes_for_unselected_students,
                    get_students_to_sync
                )
                
                print(f"🔍 NOTE_PROCESSOR: Extraindo alunos do deck remoto...")
                # Extrair todos os alunos da planilha
                all_students_in_sheet = extract_students_from_remote_data(remoteDeck)
                print(f"  • Alunos encontrados na planilha: {sorted(all_students_in_sheet)}")
                
                if all_students_in_sheet:
                    use_student_management = True
                    print(f"🔍 NOTE_PROCESSOR: Ativando gerenciamento de alunos...")
                    
                    # Usar configuração global para determinar alunos a sincronizar
                    print(f"🔍 NOTE_PROCESSOR: Obtendo alunos para sync...")
                    selected_students = get_students_to_sync(all_students_in_sheet)
                    print(f"  • Alunos selecionados para sync: {sorted(selected_students)}")
                    
                    # Filtrar questões por alunos selecionados
                    if selected_students:
                        print(f"🔍 NOTE_PROCESSOR: Filtrando questões por alunos selecionados...")
                        original_count = len(remoteDeck.questions)
                        remoteDeck.questions = filter_questions_by_selected_students(
                            remoteDeck.questions, selected_students
                        )
                        filtered_count = len(remoteDeck.questions)
                        print(f"✅ NOTE_PROCESSOR: Filtrou questões por configuração global: {original_count} -> {filtered_count} (alunos: {', '.join(sorted(selected_students))})")
                    else:
                        # Se filtro está ativo mas não há alunos selecionados, não sincronizar nada
                        print(f"🔍 NOTE_PROCESSOR: Nenhum aluno selecionado, verificando se filtro está ativo...")
                        from .config_manager import is_student_sync_enabled
                        if is_student_sync_enabled():
                            remoteDeck.questions = []
                            print(f"⚠️ NOTE_PROCESSOR: Filtro de alunos ativo mas nenhum aluno selecionado - nenhuma questão será sincronizada")
                        else:
                            print(f"📝 NOTE_PROCESSOR: Filtro de alunos desativo - mantendo todas as questões")
                else:
                    print(f"📝 NOTE_PROCESSOR: Nenhum aluno encontrado na planilha - desativando gerenciamento de alunos")
            except ImportError as e:
                print(f"[INFO] Funcionalidade de alunos não disponível: {e}")
                use_student_management = False
            except Exception as e:
                print(f"[WARNING] Erro no gerenciamento de alunos, continuando sem filtros: {e}")
                import traceback
                traceback.print_exc()
                use_student_management = False
        
        # Para cada aluno selecionado, garantir que os modelos existam
        student_models = {}
        missing_students_models = {}  # NOVO: Models para [MISSING A.]
        
        if use_student_management and selected_students:
            try:
                for student in selected_students:
                    student_models[student] = ensure_custom_models(col, deck_url, student=student, debug_messages=debug_messages)
            except Exception as e:
                print(f"[WARNING] Erro ao criar modelos para alunos: {e}")
                use_student_management = False  # Fallback para modo sem alunos
        
        # NOVO: Criar models para [MISSING A.] se funcionalidade estiver ativa
        if use_student_management:
            try:
                from .config_manager import is_sync_missing_students_notes
                if is_sync_missing_students_notes():
                    missing_students_models = ensure_custom_models(col, deck_url, student="[MISSING A.]", debug_messages=debug_messages)
                    print(f"[INFO] Models criados para notas [MISSING A.]")
                else:
                    missing_students_models = {}  # Vazio se funcionalidade desabilitada
            except Exception as e:
                print(f"[WARNING] Erro ao criar modelos para [MISSING A.]: {e}")
                missing_students_models = {}  # Fallback para dict vazio
        
        if not use_student_management:
            # Usar modelos padrão sem alunos
            models = ensure_custom_models(col, remoteDeck.url if hasattr(remoteDeck, 'url') else deck_url or "", debug_messages=debug_messages)
        
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
                
                # Determinar alunos para esta questão
                question_students = set()
                is_missing_students_note = False  # NOVO: flag para notas [MISSING A.]
                
                if use_student_management:
                    from .student_manager import get_students_from_question
                    question_students = get_students_from_question(fields)
                    # Filtrar apenas alunos selecionados (garantir que selected_students não seja None)
                    if selected_students:
                        question_students = question_students.intersection(selected_students)
                    
                    # NOVO: Verificar se é uma nota sem alunos específicos ([MISSING A.])
                    alunos_field = fields.get(column_definitions.ALUNOS, '').strip()
                    if not alunos_field:
                        from .config_manager import is_sync_missing_students_notes
                        if is_sync_missing_students_notes():
                            is_missing_students_note = True
                
                if use_student_management and question_students:
                    # Processar para cada aluno
                    for student in question_students:
                        _process_question_for_student(
                            col, question, fields, tags, key, student, 
                            existing_notes, remoteDeck, student_models[student], 
                            stats, deck_id
                        )
                elif is_missing_students_note:
                    # NOVO: Processar para [MISSING A.] quando não há alunos específicos
                    _process_question_for_missing_students(
                        col, question, fields, tags, key, 
                        existing_notes, remoteDeck, missing_students_models, 
                        stats, deck_id
                    )
                else:
                    # Processar sem aluno específico (compatibilidade)
                    _process_question_without_student(
                        col, question, fields, tags, key, 
                        existing_notes, remoteDeck, models, 
                        stats, deck_id
                    )

            except NoteProcessingError as e:
                stats['errors'] += 1
                stats['error_details'].append(f"ID {key}: {str(e)}")
                continue
            except Exception as e:
                stats['errors'] += 1
                stats['error_details'].append(f"ID {key}: Unexpected error: {str(e)}")
                continue

        # REMOVIDO: Lógica duplicada de remoção de alunos desabilitados 
        # A limpeza de alunos desabilitados agora é feita APENAS no início da sincronização
        # via _handle_consolidated_cleanup() para evitar duplicação e inconsistências
        
        # Remover notas de alunos não selecionados (apenas se auto-remoção estiver habilitada)
        # NOTA: Esta lógica foi movida para _handle_consolidated_cleanup em sync.py
        # para evitar conflitos e duplicação de remoções

        # Identificar e remover notas que não existem mais na fonte remota
        notes_to_delete = set(existing_notes.keys()) - all_existing_keys_in_sheet
        for key in notes_to_delete:
            try:
                nid = existing_note_ids[key]
                col.remove_notes([nid])
                stats['deleted'] += 1
            except Exception as e:
                stats['errors'] += 1
                stats['error_details'].append(f"Error removing note {key}: {str(e)}")

        return stats

    except SyncError as e:
        error_msg = f"Critical sync error: {str(e)}"
        raise SyncError(error_msg)
    except Exception as e:
        error_msg = f"Unexpected error during sync: {str(e)}"
        raise SyncError(error_msg)


def _process_question_for_student(col, question, fields, tags, key, student, 
                                existing_notes, remoteDeck, models, stats, deck_id):
    """
    Processa uma questão para um aluno específico.
    
    Mantém o ID original da questão e cria/atualiza nota no subdeck do aluno.
    """
    from .student_manager import get_student_subdeck_name
    
    # Usar o ID original, mas buscar nota específica no subdeck do aluno
    main_deck_name = remoteDeck.deckName
    subdeck_name = get_student_subdeck_name(main_deck_name, student, fields)
    
    # Procurar nota existente neste subdeck específico com o ID original
    existing_note = None
    existing_nid = None
    
    # Buscar notas no subdeck do aluno com o ID original
    subdeck_search = f'deck:"{subdeck_name}" {column_definitions.ID}:"{key}"'
    note_ids = col.find_notes(subdeck_search)
    
    if note_ids:
        existing_nid = note_ids[0]  # Pegar primeira nota encontrada
        existing_note = col.get_note(existing_nid)
    
    if existing_note:
        # Atualizar nota existente mantendo ID original
        if note_needs_update(existing_note, fields, tags):
            # Capturar detalhes das mudanças
            if len(stats['updated_details']) < 10:
                changes = get_update_details(existing_note, fields, tags)
                if changes:
                    pergunta = fields.get(column_definitions.PERGUNTA, "")
                    pergunta_display = pergunta[:100] + "..." if len(pergunta) > 100 else pergunta
                    
                    update_info = {
                        'id': key,
                        'pergunta': f"[{student}] {pergunta_display}",
                        'changes': changes
                    }
                    stats['updated_details'].append(update_info)
            
            # Atualizar campos
            for field_name, value in fields.items():
                if field_name in column_definitions.NOTE_FIELDS and field_name in existing_note:
                    existing_note[field_name] = value
            existing_note.tags = tags
            
            try:
                existing_note.flush()
                stats['updated'] += 1
            except Exception as e:
                raise NoteProcessingError(f"Error updating note {key} for student {student}: {str(e)}")
    else:
        # Criar nova nota mantendo ID original
        has_cloze = has_cloze_deletion(fields[column_definitions.PERGUNTA])
        model_to_use = models['cloze'] if has_cloze else models['standard']
        
        col.models.set_current(model_to_use)
        model_to_use['did'] = deck_id
        col.models.save(model_to_use)

        note = col.new_note(model_to_use)
        
        # Usar campos originais SEM modificar o ID
        for field_name, value in fields.items():
            if field_name in column_definitions.NOTE_FIELDS and field_name in note:
                note[field_name] = value
        note.tags = tags
        
        try:
            # Criar nota no subdeck do aluno
            if subdeck_name != main_deck_name:
                from .subdeck_manager import ensure_subdeck_exists
                subdeck_id = ensure_subdeck_exists(subdeck_name)
                col.add_note(note, subdeck_id)
            else:
                col.add_note(note, deck_id)
                
            stats['created'] += 1
        except Exception as e:
            raise NoteProcessingError(f"Error creating note {key} for student {student}: {str(e)}")


def _process_question_for_missing_students(col, question, fields, tags, key, 
                                         existing_notes, remoteDeck, models, stats, deck_id):
    """
    Processa uma questão para notas sem alunos específicos ([MISSING A.]).
    
    Mantém o ID original da questão e cria/atualiza nota no subdeck [MISSING A.].
    """
    from .student_manager import get_missing_students_subdeck_name
    
    # Usar o ID original, mas buscar nota específica no subdeck [MISSING A.]
    main_deck_name = remoteDeck.deckName
    subdeck_name = get_missing_students_subdeck_name(main_deck_name, fields)
    
    # Procurar nota existente neste subdeck específico com o ID original
    existing_note = None
    existing_nid = None
    
    # Buscar notas no subdeck [MISSING A.] com o ID original
    subdeck_search = f'deck:"{subdeck_name}" {column_definitions.ID}:"{key}"'
    note_ids = col.find_notes(subdeck_search)
    
    if note_ids:
        existing_nid = note_ids[0]  # Pegar primeira nota encontrada
        existing_note = col.get_note(existing_nid)
    
    if existing_note:
        # Atualizar nota existente mantendo ID original
        if note_needs_update(existing_note, fields, tags):
            # Capturar detalhes das mudanças
            if len(stats['updated_details']) < 10:
                changes = get_update_details(existing_note, fields, tags)
                stats['updated_details'].append(f"[MISSING A.] ID {key}: {changes}")
            
            # Atualizar campos da nota
            for field_name, value in fields.items():
                if field_name in column_definitions.NOTE_FIELDS and field_name in existing_note:
                    existing_note[field_name] = value
                    
            existing_note.tags = tags
            
            try:
                existing_note.flush()
                stats['updated'] += 1
            except Exception as e:
                raise NoteProcessingError(f"Error updating note {key} for [MISSING A.]: {str(e)}")
    else:
        # Criar nova nota
        has_cloze = has_cloze_deletion(fields[column_definitions.PERGUNTA])
        model_to_use = models['cloze'] if has_cloze else models['standard']
        
        if not model_to_use:
            note_type_name = 'cloze' if has_cloze else 'standard'
            raise NoteProcessingError(f"Note type {note_type_name} not found in models for [MISSING A.]")
        
        note = col.new_note(model_to_use)
        
        # Usar campos originais SEM modificar o ID
        for field_name, value in fields.items():
            if field_name in column_definitions.NOTE_FIELDS and field_name in note:
                note[field_name] = value
        note.tags = tags
        
        try:
            # Criar nota no subdeck [MISSING A.]
            if subdeck_name != main_deck_name:
                from .subdeck_manager import ensure_subdeck_exists
                subdeck_id = ensure_subdeck_exists(subdeck_name)
                col.add_note(note, subdeck_id)
            else:
                col.add_note(note, deck_id)
                
            stats['created'] += 1
        except Exception as e:
            raise NoteProcessingError(f"Error creating note {key} for [MISSING A.]: {str(e)}")


def _process_question_without_student(col, question, fields, tags, key, 
                                    existing_notes, remoteDeck, models, stats, deck_id):
    """
    Processa uma questão sem aluno específico (modo de compatibilidade).
    """
    if key in existing_notes:
        # Atualizar nota existente
        note = existing_notes[key]
        if note_needs_update(note, fields, tags):
            # Capturar detalhes das mudanças
            if len(stats['updated_details']) < 10:
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
                
                if subdeck_name != main_deck_name:
                    from .subdeck_manager import ensure_subdeck_exists, move_note_to_subdeck
                    subdeck_id = ensure_subdeck_exists(subdeck_name)
                    note.flush()
                    move_note_to_subdeck(note.id, subdeck_id)
                else:
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
            # Criar subdeck baseado em TOPICO e SUBTOPICO
            main_deck_name = remoteDeck.deckName
            subdeck_name = get_subdeck_name(main_deck_name, fields)
            
            if subdeck_name != main_deck_name:
                from .subdeck_manager import ensure_subdeck_exists
                subdeck_id = ensure_subdeck_exists(subdeck_name)
                col.add_note(note, subdeck_id)
            else:
                col.add_note(note, deck_id)
                
            stats['created'] += 1
        except Exception as e:
            raise NoteProcessingError(f"Error creating note {key}: {str(e)}")


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
