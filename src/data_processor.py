"""
Processamento de dados e notas para o addon Sheets2Anki.

Este módulo contém funcionalidades para:
- Download e análise de decks remotos de planilhas Google Sheets
- Processamento de dados TSV
- Criação e atualização de notas no Anki
- Gerenciamento de cards cloze e tags hierárquicas

Consolidado de:
- parseRemoteDeck.py: Análise de decks remotos
- note_processor.py: Processamento de notas
"""

# =============================================================================
# IMPORTS
# =============================================================================

import csv
import urllib.request
import urllib.error
import socket
import re  # Para expressões regulares
from . import templates_and_definitions as cols  # Definições centralizadas de colunas
from .utils import DEFAULT_IMPORTANCE, DEFAULT_TOPIC, DEFAULT_SUBTOPIC, DEFAULT_CONCEPT, TAG_ROOT, TAG_TOPICS, TAG_SUBTOPICS, TAG_CONCEPTS
from .utils import NoteProcessingError, CollectionSaveError, SyncError
from .utils import get_subdeck_name, ensure_subdeck_exists, move_note_to_subdeck
from .templates_and_definitions import ensure_custom_models

# Importar mw de forma segura
try:
    from .compat import mw
except ImportError:
    # Fallback para importação direta
    try:
        from aqt import mw
    except ImportError:
        mw = None

# =============================================================================
# CUSTOM EXCEPTIONS
# =============================================================================

class RemoteDeckError(Exception):
    """Exceção customizada para erros relacionados a decks remotos."""
    pass

# =============================================================================
# CLASSES DE DADOS
# =============================================================================

class RemoteDeck:
    """
    Classe que representa um deck carregado de uma fonte remota.
    
    Esta classe encapsula todos os dados de um deck remoto, incluindo:
    - Lista de notas com seus respectivos campos
    - Nome do deck remoto
    - Configurações e metadados
    """
    
    def __init__(self, nome="", url=""):
        """
        Inicializa um deck remoto vazio.
        
        Args:
            nome (str): Nome do deck
            url (str): URL de origem dos dados
        """
        self.nome = nome
        self.url = url
        self.notes = []  # Lista de dicionários representando as notas
        self.headers = []  # Lista dos headers da planilha
        self.total_notes = 0
        self.valid_notes = 0
        self.sync_notes = 0
        self.enabled_students = set()  # Conjunto de alunos habilitados
        
    def add_note(self, note_data):
        """
        Adiciona uma nota ao deck.
        
        Args:
            note_data (dict): Dados da nota
        """
        if note_data:
            self.notes.append(note_data)
            self.total_notes += 1
            
            # Contabilizar se é uma nota válida (tem ID e pergunta)
            if note_data.get(cols.ID) and note_data.get(cols.PERGUNTA):
                self.valid_notes += 1
                
                # Contabilizar se está marcada para sync
                sync_value = str(note_data.get(cols.SYNC, '')).strip().lower()
                if sync_value in ['true', '1', 'yes', 'sim']:
                    self.sync_notes += 1
    
    def get_statistics(self):
        """
        Retorna estatísticas do deck remoto.
        
        Returns:
            dict: Estatísticas do deck
        """
        return {
            'total_notes': self.total_notes,
            'valid_notes': self.valid_notes,
            'sync_notes': self.sync_notes,
            'enabled_students': len(self.enabled_students),
            'headers': self.headers
        }

# =============================================================================
# FUNÇÕES DE ANÁLISE DE DECKS REMOTOS
# =============================================================================

def getRemoteDeck(url, enabled_students=None, debug_messages=None):
    """
    Função principal para obter e processar um deck remoto.
    
    Esta função coordena todo o processo de download, análise e construção
    do deck remoto a partir de uma URL de planilha Google Sheets.
    
    Args:
        url (str): URL da planilha em formato TSV
        enabled_students (list, optional): Lista de alunos habilitados
        debug_messages (list, optional): Lista para acumular mensagens de debug
        
    Returns:
        RemoteDeck: Objeto deck remoto processado
        
    Raises:
        RemoteDeckError: Se houver erro no processamento do deck
    """
    def add_debug_msg(message, category="REMOTE_DECK"):
        """Helper para adicionar mensagens de debug com timestamp."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] [{category}] {message}"
        if debug_messages is not None:
            debug_messages.append(formatted_msg)
        print(formatted_msg)
    
    try:
        add_debug_msg(f"Iniciando download do deck remoto: {url}")
        
        # 1. Download dos dados TSV
        tsv_data = download_tsv_data(url)
        add_debug_msg(f"Download concluído: {len(tsv_data)} bytes")
        
        # 2. Parse dos dados TSV
        parsed_data = parse_tsv_data(tsv_data, debug_messages)
        add_debug_msg(f"Parse concluído: {len(parsed_data['rows'])} linhas")
        
        # 3. Construção do deck remoto
        remote_deck = build_remote_deck_from_tsv(
            parsed_data, 
            url, 
            enabled_students,
            debug_messages
        )
        
        stats = remote_deck.get_statistics()
        add_debug_msg(f"Deck construído: {stats['sync_notes']}/{stats['valid_notes']} notas para sync")
        
        return remote_deck
        
    except Exception as e:
        add_debug_msg(f"Erro ao processar deck remoto: {e}")
        raise RemoteDeckError(f"Erro ao obter deck remoto: {str(e)}")

def download_tsv_data(url, timeout=30):
    """
    Faz o download dos dados TSV de uma URL.
    
    Args:
        url (str): URL para download
        timeout (int): Timeout em segundos
        
    Returns:
        str: Dados TSV como string
        
    Raises:
        RemoteDeckError: Se houver erro no download
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Sheets2Anki) AnkiAddon'
        }
        request = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(request, timeout=timeout) as response:
            if response.getcode() != 200:
                raise RemoteDeckError(f"HTTP {response.getcode()}: Falha ao acessar URL")
            
            # Ler e decodificar os dados
            data = response.read().decode('utf-8')
            return data
            
    except socket.timeout:
        raise RemoteDeckError(f"Timeout de {timeout}s ao acessar a URL")
    except urllib.error.HTTPError as e:
        raise RemoteDeckError(f"Erro HTTP {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        raise RemoteDeckError(f"Erro de URL: {str(e.reason)}")
    except Exception as e:
        raise RemoteDeckError(f"Erro inesperado no download: {str(e)}")

def parse_tsv_data(tsv_data, debug_messages=None):
    """
    Analisa dados TSV e retorna estrutura processada.
    
    Args:
        tsv_data (str): Dados TSV como string
        debug_messages (list, optional): Lista para debug
        
    Returns:
        dict: Dados processados com headers e rows
        
    Raises:
        RemoteDeckError: Se houver erro no parsing
    """
    def add_debug_msg(message, category="TSV_PARSE"):
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] [{category}] {message}"
        if debug_messages is not None:
            debug_messages.append(formatted_msg)
        print(formatted_msg)
    
    try:
        # Usar csv.reader para parsing TSV
        lines = tsv_data.strip().split('\n')
        if not lines:
            raise RemoteDeckError("Dados TSV vazios")
        
        reader = csv.reader(lines, delimiter='\t')
        rows = list(reader)
        
        if not rows:
            raise RemoteDeckError("Nenhuma linha encontrada nos dados TSV")
        
        # Primeira linha são os headers
        headers = rows[0]
        data_rows = rows[1:]
        
        add_debug_msg(f"Headers encontrados: {len(headers)}")
        add_debug_msg(f"Linhas de dados: {len(data_rows)}")
        
        # Validar headers obrigatórios
        required_headers = [cols.ID, cols.PERGUNTA, cols.MATCH]
        missing_headers = [h for h in required_headers if h not in headers]
        
        if missing_headers:
            raise RemoteDeckError(f"Headers obrigatórios ausentes: {missing_headers}")
        
        return {
            'headers': headers,
            'rows': data_rows
        }
        
    except csv.Error as e:
        raise RemoteDeckError(f"Erro ao processar dados TSV: {e}")
    except Exception as e:
        raise RemoteDeckError(f"Erro inesperado no parsing: {e}")

def build_remote_deck_from_tsv(parsed_data, url, enabled_students=None, debug_messages=None):
    """
    Constrói objeto RemoteDeck a partir de dados TSV processados.
    
    Args:
        parsed_data (dict): Dados processados do TSV
        url (str): URL de origem
        enabled_students (list, optional): Lista de alunos habilitados
        debug_messages (list, optional): Lista para debug
        
    Returns:
        RemoteDeck: Objeto deck remoto construído
    """
    def add_debug_msg(message, category="DECK_BUILD"):
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] [{category}] {message}"
        if debug_messages is not None:
            debug_messages.append(formatted_msg)
        print(formatted_msg)
    
    headers = parsed_data['headers']
    rows = parsed_data['rows']
    
    # Criar deck remoto
    remote_deck = RemoteDeck(url=url)
    remote_deck.headers = headers
    
    # Processar cada linha
    for row_index, row in enumerate(rows):
        try:
            # Criar dicionário da nota
            note_data = {}
            
            # Preencher campos baseado nos headers
            for col_index, header in enumerate(headers):
                if col_index < len(row):
                    note_data[header] = row[col_index].strip()
                else:
                    note_data[header] = ""
            
            # Validar nota básica
            if not note_data.get(cols.ID) or not note_data.get(cols.PERGUNTA):
                add_debug_msg(f"Linha {row_index + 2}: nota inválida (ID ou PERGUNTA vazio)")
                continue
            
            # Verificar se deve sincronizar
            sync_value = str(note_data.get(cols.SYNC, '')).strip().lower()
            if sync_value not in ['true', '1', 'yes', 'sim']:
                add_debug_msg(f"Linha {row_index + 2}: nota não marcada para sync")
                # Ainda adiciona ao deck, mas não conta como sync
                remote_deck.add_note(note_data)
                continue
            
            # Verificar filtro de alunos
            if enabled_students:
                note_students = note_data.get(cols.ALUNOS, '').strip()
                if note_students:
                    # Verificar se algum aluno habilitado está na nota
                    students_list = [s.strip() for s in note_students.split(',')]
                    if not any(student in enabled_students for student in students_list):
                        add_debug_msg(f"Linha {row_index + 2}: nota filtrada por aluno")
                        continue
            
            # Processamento adicional dos campos
            process_note_fields(note_data)
            
            # Adicionar ao deck
            remote_deck.add_note(note_data)
            
        except Exception as e:
            add_debug_msg(f"Erro ao processar linha {row_index + 2}: {e}")
            continue
    
    # Atualizar informações dos alunos habilitados
    if enabled_students:
        remote_deck.enabled_students = set(enabled_students)
    
    stats = remote_deck.get_statistics()
    add_debug_msg(f"Deck final: {stats['sync_notes']} notas marcadas para sync")
    
    return remote_deck

def process_note_fields(note_data):
    """
    Processa campos especiais da nota.
    
    Args:
        note_data (dict): Dados da nota para processar
    """
    # IMPORTANTE: NÃO adicionar valores DEFAULT diretamente nos dados da nota
    # Os valores DEFAULT são usados apenas para lógica interna (ex: criação de subdecks)
    # mas não devem aparecer nas notas reais do Anki
    
    # Criar tags hierárquicas (usa os valores originais ou DEFAULT apenas para lógica interna)
    tags = create_tags_from_fields(note_data)
    note_data['tags'] = tags

def create_tags_from_fields(note_data):
    """
    Cria sistema hierárquico de tags a partir dos campos da nota.
    
    Args:
        note_data (dict): Dados da nota
        
    Returns:
        list: Lista de tags hierárquicas
    """
    tags = []
    
    # Tag raiz
    tags.append(TAG_ROOT)
    
    # Tags hierárquicas baseadas nos campos
    topico = note_data.get(cols.TOPICO, '').strip()
    subtopico = note_data.get(cols.SUBTOPICO, '').strip()
    conceito = note_data.get(cols.CONCEITO, '').strip()
    
    # Converter espaços em underscores para compatibilidade com Anki
    if topico and topico != DEFAULT_TOPIC:
        topico_safe = topico.replace(' ', '_')
        tags.append(f"{TAG_ROOT}::{TAG_TOPICS}::{topico_safe}")
    
    if subtopico and subtopico != DEFAULT_SUBTOPIC:
        subtopico_safe = subtopico.replace(' ', '_')
        tags.append(f"{TAG_ROOT}::{TAG_SUBTOPICS}::{subtopico_safe}")
    
    if conceito and conceito != DEFAULT_CONCEPT:
        conceito_safe = conceito.replace(' ', '_')
        tags.append(f"{TAG_ROOT}::{TAG_CONCEPTS}::{conceito_safe}")
    
    return tags

def has_cloze_deletion(text):
    """
    Verifica se um texto contém formatação cloze do Anki.
    
    Args:
        text (str): Texto a ser verificado
        
    Returns:
        bool: True se contém cloze, False caso contrário
    """
    if not text or not isinstance(text, str):
        return False
    
    # Padrão para detectar cloze: {{c1::texto}} ou {{c1::texto::hint}}
    cloze_pattern = r'\{\{c\d+::[^}]+\}\}'
    return bool(re.search(cloze_pattern, text))

# =============================================================================
# FUNÇÕES DE PROCESSAMENTO DE NOTAS
# =============================================================================

def create_or_update_notes(col, remoteDeck, deck_id, deck_url=None, debug_messages=None):
    """
    Cria ou atualiza notas no deck baseado nos dados remotos.
    
    LÓGICA REFATORADA:
    - Cada linha da planilha remota com ID único gera uma nota para cada aluno na coluna ALUNOS
    - O identificador único de cada nota é formado por "{aluno}_{id}"
    - Essa string nunca deve ser modificada após a criação da nota
    - O usuário controla quais alunos devem ter suas notas sincronizadas
    
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
    def add_debug_msg(message, category="NOTE_PROCESSOR"):
        """Helper para adicionar mensagens de debug usando o sistema global."""
        from .utils import add_debug_message
        add_debug_message(message, category)
    
    add_debug_msg(f"🔧 Iniciando sincronização de notas com lógica refatorada")
    add_debug_msg(f"🔧 remoteDeck contém {len(remoteDeck.notes)} notas")
    
    stats = {
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'errors': 0,
        'skipped': 0,
        'unchanged': 0,
        'total_remote': len(remoteDeck.notes),
        # Detalhes das mudanças para relatório ao usuário
        'update_details': [],  # Lista com detalhes de cada nota atualizada
        'creation_details': [],  # Lista com detalhes de cada nota criada
        'deletion_details': []  # Lista com detalhes de cada nota removida
    }
    
    try:
        # 1. Obter alunos habilitados do sistema de configuração
        from .config_manager import get_enabled_students, is_auto_remove_disabled_students, is_sync_missing_students_notes
        enabled_students = set(get_enabled_students() or [])
        
        # 2. Verificar se deve incluir funcionalidade [MISSING A.]
        sync_missing_students = is_sync_missing_students_notes()
        
        add_debug_msg(f"Alunos habilitados no sistema: {sorted(enabled_students)}")
        add_debug_msg(f"Sincronizar notas sem alunos específicos ([MISSING A.]): {sync_missing_students}")
        
        # 3. Incluir [MISSING A.] na lista de "alunos" se a funcionalidade estiver ativa
        effective_students = enabled_students.copy()
        if sync_missing_students:
            effective_students.add("[MISSING A.]")
            add_debug_msg("Incluindo [MISSING A.] como aluno efetivo para sincronização")
        
        if not enabled_students and not sync_missing_students:
            add_debug_msg("⚠️ Nenhum aluno habilitado e [MISSING A.] desabilitado - nenhuma nota será sincronizada")
            return stats
        
        # 4. Criar conjunto de todos os student_note_ids esperados
        expected_student_note_ids = set()
        
        for note_data in remoteDeck.notes:
            note_id = note_data.get(cols.ID, '').strip()
            if not note_id:
                continue
                
            # Verificar se deve sincronizar esta nota
            sync_value = str(note_data.get(cols.SYNC, '')).strip().lower()
            if sync_value not in ['true', '1', 'yes', 'sim']:
                continue
            
            # Obter lista de alunos desta nota
            alunos_str = note_data.get(cols.ALUNOS, '').strip()
            
            if not alunos_str:
                # Nota sem alunos específicos - verificar se deve processar como [MISSING A.]
                if sync_missing_students:
                    student_note_id = f"[MISSING A.]_{note_id}"
                    expected_student_note_ids.add(student_note_id)
                    add_debug_msg(f"Nota {note_id}: sem alunos específicos, incluindo como [MISSING A.]")
                else:
                    add_debug_msg(f"Nota {note_id}: sem alunos específicos, pulando (funcionalidade desabilitada)")
                continue
                
            # Extrair alunos individuais (separados por vírgula)
            students_in_note = [s.strip() for s in alunos_str.split(',') if s.strip()]
            
            # Para cada aluno habilitado que está nesta nota
            for student in students_in_note:
                if student in enabled_students:
                    # Criar ID único aluno_id
                    student_note_id = f"{student}_{note_id}"
                    expected_student_note_ids.add(student_note_id)
        
        add_debug_msg(f"Total de notas esperadas (student_note_id): {len(expected_student_note_ids)}")
        
        # 3. Garantir que os note types existem para todos os alunos necessários
        students_to_create_note_types = set()
        for student_note_id in expected_student_note_ids:
            student = student_note_id.split('_')[0]  # Primeiro elemento antes do "_"
            students_to_create_note_types.add(student)
        
        add_debug_msg(f"Criando note types para alunos: {sorted(students_to_create_note_types)}")
        for student in students_to_create_note_types:
            ensure_custom_models(col, deck_url, student=student, debug_messages=debug_messages)
        
        # 4. Obter notas existentes por student_note_id
        existing_notes = get_existing_notes_by_student_id(col, deck_id)
        add_debug_msg(f"Encontradas {len(existing_notes)} notas existentes no deck")
        
        # 5. Processar cada nota remota para cada aluno
        for note_data in remoteDeck.notes:
            note_id = note_data.get(cols.ID, '').strip()
            if not note_id:
                stats['errors'] += 1
                add_debug_msg(f"❌ Nota sem ID válido")
                continue
            
            # Verificar se deve sincronizar
            sync_value = str(note_data.get(cols.SYNC, '')).strip().lower()
            if sync_value not in ['true', '1', 'yes', 'sim']:
                stats['skipped'] += 1
                continue
            
            # Obter lista de alunos da nota
            alunos_str = note_data.get(cols.ALUNOS, '').strip()
            
            if not alunos_str:
                # Nota sem alunos específicos - verificar se deve processar como [MISSING A.]
                if sync_missing_students:
                    # Processar como [MISSING A.]
                    student = "[MISSING A.]"
                    student_note_id = f"{student}_{note_id}"
                    add_debug_msg(f"Nota {note_id}: sem alunos específicos, processando como [MISSING A.]")
                    
                    try:
                        if student_note_id in existing_notes:
                            # Atualizar nota existente
                            success, was_updated, changes = update_existing_note_for_student(
                                col, existing_notes[student_note_id], note_data, student, deck_url, debug_messages
                            )
                            if success:
                                if was_updated:
                                    stats['updated'] += 1
                                    # Capturar detalhes da mudança
                                    update_detail = {
                                        'student_note_id': student_note_id,
                                        'student': student,
                                        'note_id': note_data.get(cols.ID, '').strip(),
                                        'changes': changes
                                    }
                                    stats['update_details'].append(update_detail)
                                    add_debug_msg(f"✅ Nota [MISSING A.] atualizada: {student_note_id}")
                                else:
                                    stats['unchanged'] += 1
                                    add_debug_msg(f"⏭️ Nota [MISSING A.] inalterada: {student_note_id}")
                            else:
                                stats['errors'] += 1
                                add_debug_msg(f"❌ Erro ao atualizar nota [MISSING A.]: {student_note_id}")
                        else:
                            # Criar nova nota
                            if create_new_note_for_student(col, note_data, student, deck_id, deck_url, debug_messages):
                                stats['created'] += 1
                                # Capturar detalhes da criação
                                creation_detail = {
                                    'student_note_id': f"{student}_{note_data.get(cols.ID, '').strip()}",
                                    'student': student,
                                    'note_id': note_data.get(cols.ID, '').strip(),
                                    'pergunta': note_data.get(cols.PERGUNTA, '')[:100] + ('...' if len(note_data.get(cols.PERGUNTA, '')) > 100 else '')
                                }
                                stats['creation_details'].append(creation_detail)
                                add_debug_msg(f"✅ Nota [MISSING A.] criada: {student_note_id}")
                            else:
                                stats['errors'] += 1
                                add_debug_msg(f"❌ Erro ao criar nota [MISSING A.]: {student_note_id}")
                                
                    except Exception as e:
                        import traceback
                        error_details = traceback.format_exc()
                        add_debug_msg(f"❌ Erro ao processar {student_note_id}: {e}")
                        add_debug_msg(f"❌ Stack trace: {error_details}")
                        stats['errors'] += 1
                else:
                    # Funcionalidade [MISSING A.] desabilitada
                    stats['skipped'] += 1
                    add_debug_msg(f"Nota {note_id}: sem alunos definidos, pulando (funcionalidade [MISSING A.] desabilitada)")
                continue
            
            # Processar notas com alunos específicos
            students_in_note = [s.strip() for s in alunos_str.split(',') if s.strip()]
            
            # Processar cada aluno habilitado
            for student in students_in_note:
                if student not in enabled_students:
                    continue  # Aluno não habilitado
                
                # Criar ID único para esta combinação
                student_note_id = f"{student}_{note_id}"
                
                try:
                    if student_note_id in existing_notes:
                        # Atualizar nota existente
                        success, was_updated, changes = update_existing_note_for_student(
                            col, existing_notes[student_note_id], note_data, student, deck_url, debug_messages
                        )
                        if success:
                            if was_updated:
                                stats['updated'] += 1
                                # Capturar detalhes da mudança
                                update_detail = {
                                    'student_note_id': student_note_id,
                                    'student': student,
                                    'note_id': note_data.get(cols.ID, '').strip(),
                                    'changes': changes
                                }
                                stats['update_details'].append(update_detail)
                                add_debug_msg(f"✅ Nota atualizada: {student_note_id}")
                            else:
                                stats['unchanged'] += 1
                                add_debug_msg(f"⏭️ Nota inalterada: {student_note_id}")
                        else:
                            stats['errors'] += 1
                            add_debug_msg(f"❌ Erro ao atualizar nota: {student_note_id}")
                    else:
                        # Criar nova nota
                        if create_new_note_for_student(col, note_data, student, deck_id, deck_url, debug_messages):
                            stats['created'] += 1
                            # Capturar detalhes da criação
                            creation_detail = {
                                'student_note_id': student_note_id,
                                'student': student,
                                'note_id': note_data.get(cols.ID, '').strip(),
                                'pergunta': note_data.get(cols.PERGUNTA, '')[:100] + ('...' if len(note_data.get(cols.PERGUNTA, '')) > 100 else '')
                            }
                            stats['creation_details'].append(creation_detail)
                            add_debug_msg(f"✅ Nota criada: {student_note_id}")
                        else:
                            stats['errors'] += 1
                            add_debug_msg(f"❌ Erro ao criar nota: {student_note_id}")
                            
                except Exception as e:
                    import traceback
                    error_details = traceback.format_exc()
                    add_debug_msg(f"❌ Erro ao processar {student_note_id}: {e}")
                    add_debug_msg(f"❌ Stack trace: {error_details}")
                    stats['errors'] += 1
        
        # 6. Remover notas que não existem mais na fonte remota
        # NOVA LÓGICA: Só remover notas realmente obsoletas, não de alunos desabilitados
        notes_to_delete = set(existing_notes.keys()) - expected_student_note_ids
        
        # Filtrar para não remover notas de alunos desabilitados se auto-remove estiver ativo
        # (essas serão tratadas pelo sistema de limpeza com confirmação)
        from .config_manager import is_auto_remove_disabled_students
        if is_auto_remove_disabled_students():
            # Se auto-remove estiver ativo, preservar notas de alunos desabilitados 
            # para serem tratadas pelo processo de confirmação
            filtered_notes_to_delete = set()
            all_available_students = set(get_enabled_students() or [])
            
            # Adicionar alunos disponíveis (mesmo se não habilitados) para evitar remoção prematura
            from .config_manager import get_global_student_config
            config = get_global_student_config()
            available_students = set(config.get("available_students", []))
            all_known_students = enabled_students.union(available_students)
            
            for student_note_id in notes_to_delete:
                student = student_note_id.split('_')[0] 
                # Só remover se não for de nenhum aluno conhecido (realmente obsoleta)
                if student not in all_known_students and student != "[MISSING A.]":
                    filtered_notes_to_delete.add(student_note_id)
                    add_debug_msg(f"Nota {student_note_id}: marcada para remoção (aluno desconhecido)")
                else:
                    add_debug_msg(f"Nota {student_note_id}: preservada (aluno conhecido ou [MISSING A.])")
            
            notes_to_delete = filtered_notes_to_delete
            add_debug_msg(f"Auto-remove ativo: preservando notas de alunos conhecidos, removendo apenas {len(notes_to_delete)} realmente obsoletas")
        else:
            add_debug_msg(f"Auto-remove inativo: removendo {len(notes_to_delete)} notas obsoletas normalmente")
        
        add_debug_msg(f"Removendo {len(notes_to_delete)} notas obsoletas")
        
        for student_note_id in notes_to_delete:
            try:
                note_to_delete = existing_notes[student_note_id]
                if delete_note_by_id(col, note_to_delete):
                    stats['deleted'] += 1
                    # Capturar detalhes da exclusão
                    deletion_detail = {
                        'student_note_id': student_note_id,
                        'student': student_note_id.split('_')[0] if '_' in student_note_id else 'Unknown',
                        'note_id': student_note_id.split('_', 1)[1] if '_' in student_note_id else student_note_id,
                        'pergunta': note_to_delete[cols.PERGUNTA][:100] + ('...' if len(note_to_delete[cols.PERGUNTA]) > 100 else '') if cols.PERGUNTA in note_to_delete else 'N/A'
                    }
                    stats['deletion_details'].append(deletion_detail)
                    add_debug_msg(f"🗑️ Nota removida: {student_note_id}")
                else:
                    stats['errors'] += 1
                    add_debug_msg(f"❌ Erro ao remover nota: {student_note_id}")
            except Exception as e:
                add_debug_msg(f"❌ Erro ao deletar nota {student_note_id}: {e}")
                stats['errors'] += 1
        
        # 7. Salvar alterações
        try:
            col.save()
            add_debug_msg("Coleção salva com sucesso")
        except Exception as e:
            raise CollectionSaveError(f"Falha ao salvar coleção: {e}")
        
        add_debug_msg(f"🎯 Sincronização concluída: +{stats['created']} ~{stats['updated']} ={stats['unchanged']} -{stats['deleted']} !{stats['errors']}")
        
        return stats
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        add_debug_msg(f"❌ ERRO CRÍTICO na sincronização: {e}")
        add_debug_msg(f"❌ Stack trace completo: {error_details}")
        
        # Retornar stats com erro
        stats['errors'] = stats.get('total_remote', 1)
        return stats

def get_existing_notes_by_student_id(col, deck_id):
    """
    Obtém mapeamento de notas existentes no deck por student_note_id.
    
    LÓGICA REFATORADA:
    - Busca todas as notas no deck e subdecks
    - Para cada nota, extrai o ID da nota do campo ID
    - Deriva o aluno do nome do subdeck onde a nota está localizada
    - Cria o student_note_id como "{aluno}_{note_id}"
    - Retorna mapeamento {student_note_id: note_object}
    
    Args:
        col: Coleção do Anki
        deck_id (int): ID do deck
        
    Returns:
        dict: Mapeamento {student_note_id: note_object} onde student_note_id = "aluno_note_id"
    """
    existing_notes = {}
    
    try:
        # Obter o deck principal
        deck = col.decks.get(deck_id)
        if not deck:
            return existing_notes
            
        deck_name = deck['name']
        
        # Buscar cards no deck principal E em todos os subdecks
        search_query = f'deck:"{deck_name}" OR deck:"{deck_name}::*"'
        card_ids = col.find_cards(search_query)
        
        for card_id in card_ids:
            try:
                card = col.get_card(card_id)
                note = card.note()
                
                # Obter ID da nota do campo ID
                note_fields = note.keys()
                if cols.ID in note_fields:
                    full_note_id = note[cols.ID].strip()
                    if full_note_id:
                        # O campo ID já contém o formato "{aluno}_{note_id}" após a refatoração
                        # Verificar se tem o formato esperado
                        if '_' in full_note_id:
                            # Usar diretamente o ID da nota como student_note_id
                            student_note_id = full_note_id
                            existing_notes[student_note_id] = note
                        else:
                            # Formato antigo - tentar extrair do subdeck como fallback
                            card_deck = col.decks.get(card.did)
                            if card_deck:
                                subdeck_name = card_deck['name']
                                # Estrutura esperada: Sheets2Anki::Remote::Aluno::Importancia::...
                                deck_parts = subdeck_name.split("::")
                                if len(deck_parts) >= 3:
                                    student = deck_parts[2]  # Terceiro elemento é o aluno
                                    student_note_id = f"{student}_{full_note_id}"
                                    existing_notes[student_note_id] = note
                        
            except Exception as e:
                print(f"Erro ao processar card {card_id}: {e}")
                continue
                
    except Exception as e:
        print(f"Erro ao obter notas existentes: {e}")
    
    return existing_notes

def create_new_note_for_student(col, note_data, student, deck_id, deck_url, debug_messages=None):
    """
    Cria uma nova nota no Anki para um aluno específico.
    
    Args:
        col: Coleção do Anki
        note_data (dict): Dados da nota da planilha
        student (str): Nome do aluno
        deck_id (int): ID do deck base
        deck_url (str): URL do deck remoto
        debug_messages (list, optional): Lista para debug
        
    Returns:
        bool: True se criada com sucesso, False caso contrário
    """
    def add_debug_msg(message, category="CREATE_NOTE_STUDENT"):
        """Helper para adicionar mensagens de debug usando o sistema global."""
        from .utils import add_debug_message
        add_debug_message(message, category)
    
    try:
        note_id = note_data.get(cols.ID, '').strip()
        add_debug_msg(f"Criando nova nota para aluno {student}: {note_id}")
        
        # Determinar tipo de nota (cloze ou básica)
        pergunta = note_data.get(cols.PERGUNTA, '')
        is_cloze = has_cloze_deletion(pergunta)
        
        # Obter modelo apropriado para o aluno específico
        from .utils import get_note_type_name
        from .config_manager import get_deck_remote_name
        
        remote_deck_name = get_deck_remote_name(deck_url)
        note_type_name = get_note_type_name(deck_url, remote_deck_name, student=student, is_cloze=is_cloze)
        
        add_debug_msg(f"Note type para {student}: {note_type_name}")
        
        model = col.models.by_name(note_type_name)
        if not model:
            add_debug_msg(f"❌ ERRO: Modelo não encontrado: '{note_type_name}' para aluno: {student}")
            add_debug_msg(f"❌ Tentando criar note type para nota: {note_id}")
            # Tentar criar o modelo se não existir
            from .templates_and_definitions import ensure_custom_models
            models = ensure_custom_models(col, deck_url, student=student, debug_messages=debug_messages)
            model = models.get('cloze' if is_cloze else 'standard')
            if not model:
                add_debug_msg(f"❌ ERRO CRÍTICO: Não foi possível criar/encontrar modelo: {note_type_name}")
                return False
            add_debug_msg(f"✅ Modelo criado com sucesso: {note_type_name}")
        
        add_debug_msg(f"✅ Modelo encontrado: {note_type_name} (ID: {model['id'] if model else 'None'})")
        
        # Criar nota
        note = col.new_note(model)
        
        # Preencher campos com identificador único para o aluno
        fill_note_fields_for_student(note, note_data, student)
        
        # Adicionar tags
        tags = note_data.get('tags', [])
        if tags:
            note.tags = tags
        
        # Determinar deck de destino para o aluno específico
        add_debug_msg(f"Determinando deck de destino para nota: {note_id}, aluno: {student}")
        target_deck_id = determine_target_deck_for_student(col, deck_id, note_data, student, deck_url, debug_messages)
        add_debug_msg(f"Deck de destino determinado: {target_deck_id}")
        
        # Adicionar nota ao deck
        add_debug_msg(f"Adicionando nota {note_id} do aluno {student} ao deck {target_deck_id}")
        col.add_note(note, target_deck_id)
        add_debug_msg(f"✅ Nota {note_id} do aluno {student} adicionada com sucesso ao deck {target_deck_id}")
        
        add_debug_msg(f"✅ Nota criada com sucesso para {student}: {note_id}")
        return True
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        add_debug_msg(f"❌ ERRO ao criar nota {note_data.get(cols.ID, 'UNKNOWN')} para {student}: {e}")
        add_debug_msg(f"❌ Stack trace: {error_details}")
        print(f"[CREATE_NOTE_ERROR] {note_data.get(cols.ID, 'UNKNOWN')} para {student}: {e}")
        print(f"[CREATE_NOTE_ERROR] Stack trace: {error_details}")
        return False

def note_fields_need_update(existing_note, new_data, debug_messages=None, student=None):
    """
    Verifica se uma nota precisa ser atualizada comparando campos e tags.
    
    LÓGICA REFATORADA:
    - Considera que o ID na nota já está no formato "{aluno}_{id}"
    - Para comparação, usa os dados originais da planilha para os outros campos
    - Não compara o campo ID pois ele é derivado e deve permanecer inalterado
    
    Args:
        existing_note: Nota existente no Anki
        new_data (dict): Novos dados da nota
        debug_messages (list, optional): Lista para debug
        student (str, optional): Nome do aluno para formar ID único na comparação
        
    Returns:
        tuple: (needs_update: bool, changes: list)
    """
    def add_debug_msg(message, category="NOTE_COMPARISON"):
        """Helper para adicionar mensagens de debug usando o sistema global."""
        from .utils import add_debug_message
        add_debug_message(message, category)
    
    changes = []
    
    # Comparar campos (excluindo ID que é derivado)
    # O ID na nota existente já está no formato "{aluno}_{id}" e não deve ser comparado
    # CORREÇÃO: Usar os nomes reais dos campos no Anki (que são iguais aos da planilha)
    for field_key, field_anki_name in [(cols.PERGUNTA, cols.PERGUNTA), (cols.MATCH, cols.MATCH),
                                       (cols.EXTRA_INFO_1, cols.EXTRA_INFO_1), (cols.EXTRA_INFO_2, cols.EXTRA_INFO_2),
                                       (cols.EXEMPLO_1, cols.EXEMPLO_1), (cols.EXEMPLO_2, cols.EXEMPLO_2), 
                                       (cols.EXEMPLO_3, cols.EXEMPLO_3), (cols.TOPICO, cols.TOPICO), 
                                       (cols.SUBTOPICO, cols.SUBTOPICO), (cols.CONCEITO, cols.CONCEITO), 
                                       (cols.BANCAS, cols.BANCAS), (cols.ANO, cols.ANO),
                                       (cols.CARREIRA, cols.CARREIRA), (cols.IMPORTANCIA, cols.IMPORTANCIA), 
                                       (cols.MORE_TAGS, cols.MORE_TAGS)]:
        if field_anki_name in existing_note:
            old_value = str(existing_note[field_anki_name]).strip()
            new_value = str(new_data.get(field_key, '')).strip()
            
            if old_value != new_value:
                # Truncar para log se muito longo
                old_display = old_value[:50] + "..." if len(old_value) > 50 else old_value
                new_display = new_value[:50] + "..." if len(new_value) > 50 else new_value
                changes.append(f"{field_anki_name}: '{old_display}' → '{new_display}'")
    
    # Comparar tags
    existing_tags = set(existing_note.tags) if hasattr(existing_note, 'tags') else set()
    new_tags = set(new_data.get('tags', []))
    
    # Debug detalhado das tags
    add_debug_msg(f"🏷️ Tags existentes: {sorted(existing_tags)}")
    add_debug_msg(f"🏷️ Tags novas: {sorted(new_tags)}")
    
    if existing_tags != new_tags:
        added_tags = new_tags - existing_tags
        removed_tags = existing_tags - new_tags
        
        add_debug_msg(f"🏷️ Tags diferentes detectadas!")
        if added_tags:
            changes.append(f"Tags adicionadas: {', '.join(added_tags)}")
            add_debug_msg(f"🏷️ Adicionadas: {sorted(added_tags)}")
        if removed_tags:
            changes.append(f"Tags removidas: {', '.join(removed_tags)}")
            add_debug_msg(f"🏷️ Removidas: {sorted(removed_tags)}")
    else:
        add_debug_msg(f"🏷️ Tags são idênticas")
    
    needs_update = len(changes) > 0
    
    if needs_update:
        add_debug_msg(f"Nota precisa ser atualizada. Mudanças detectadas: {'; '.join(changes)}")
    else:
        add_debug_msg(f"Nota NÃO precisa ser atualizada - conteúdo idêntico")
    
    return needs_update, changes


def update_existing_note_for_student(col, existing_note, new_data, student, deck_url, debug_messages=None):
    """
    Atualiza uma nota existente para um aluno específico.
    IMPORTANTE: Só atualiza se houver diferenças reais entre o conteúdo local e remoto.
    
    Args:
        col: Coleção do Anki
        existing_note: Nota existente no Anki
        new_data (dict): Novos dados da nota
        student (str): Nome do aluno
        deck_url (str): URL do deck
        debug_messages (list, optional): Lista para debug
        
    Returns:
        tuple: (success: bool, was_updated: bool, changes: list) - (processo bem-sucedido, nota foi realmente atualizada, lista de mudanças)
    """
    def add_debug_msg(message, category="UPDATE_NOTE_STUDENT"):
        """Helper para adicionar mensagens de debug usando o sistema global."""
        from .utils import add_debug_message
        add_debug_message(message, category)
    
    try:
        note_id = new_data.get(cols.ID, '').strip()
        add_debug_msg(f"Verificando se nota {note_id} precisa ser atualizada para aluno {student}")
        
        # Verificar se há diferenças reais entre nota existente e dados novos
        needs_update, changes = note_fields_need_update(existing_note, new_data, debug_messages, student=student)
        
        if not needs_update:
            add_debug_msg(f"⏭️ Nota {note_id} não foi atualizada - conteúdo idêntico")
            return True, False, []  # Sucesso, mas não foi atualizada, sem mudanças
        
        add_debug_msg(f"📝 Atualizando nota {note_id} com mudanças: {'; '.join(changes[:3])}...")
        
        # Preencher campos com novos dados (usando identificador único para o aluno)
        fill_note_fields_for_student(existing_note, new_data, student)
        
        # Atualizar tags
        tags = new_data.get('tags', [])
        if tags:
            existing_note.tags = tags
        
        # Verificar se precisa mover para subdeck diferente
        cards = existing_note.cards()
        if cards:
            current_deck_id = cards[0].did
            target_deck_id = determine_target_deck_for_student(col, current_deck_id, new_data, student, deck_url, debug_messages)
            
            if current_deck_id != target_deck_id:
                # Mover cards para novo deck
                for card in cards:
                    card.did = target_deck_id
                    col.update_card(card)
        
        # Salvar alterações da nota
        existing_note.flush()
        
        add_debug_msg(f"✅ Nota atualizada com sucesso para {student}: {note_id}")
        return True, True, changes  # Sucesso, foi atualizada, com lista de mudanças
        
    except Exception as e:
        add_debug_msg(f"❌ Erro ao atualizar nota para {student}: {e}")
        return False, False, []  # Erro, sem mudanças


def delete_note_by_id(col, note):
    """
    Remove uma nota do Anki.
    
    Args:
        col: Coleção do Anki
        note: Nota a ser removida
        
    Returns:
        bool: True se removida com sucesso, False caso contrário
    """
    try:
        col.remove_notes([note.id])
        return True
    except Exception as e:
        print(f"Erro ao deletar nota {note.id}: {e}")
        return False


def fill_note_fields_for_student(note, note_data, student):
    """
    Preenche os campos de uma nota com dados da planilha para um aluno específico.
    
    LÓGICA REFATORADA:
    - O campo ID da nota no Anki será preenchido com "{aluno}_{id}" 
    - Este identificador único nunca deve ser modificado após a criação
    - Todos os outros campos são preenchidos normalmente dos dados da planilha
    
    Args:
        note: Nota do Anki
        note_data (dict): Dados da planilha
        student (str): Nome do aluno para formar o ID único
    """
    # Obter o ID original da planilha
    original_id = note_data.get(cols.ID, '').strip()
    
    # Criar identificador único para esta combinação aluno-nota
    unique_student_note_id = f"{student}_{original_id}"
    
    # Mapeamento de campos com tratamento especial para ID
    field_mappings = {
        cols.ID: unique_student_note_id,  # ID único por aluno
        cols.PERGUNTA: note_data.get(cols.PERGUNTA, '').strip(),
        cols.MATCH: note_data.get(cols.MATCH, '').strip(),
        cols.TOPICO: note_data.get(cols.TOPICO, '').strip(),
        cols.SUBTOPICO: note_data.get(cols.SUBTOPICO, '').strip(),
        cols.CONCEITO: note_data.get(cols.CONCEITO, '').strip(),
        cols.EXTRA_INFO_1: note_data.get(cols.EXTRA_INFO_1, '').strip(),
        cols.EXTRA_INFO_2: note_data.get(cols.EXTRA_INFO_2, '').strip(),
        cols.EXEMPLO_1: note_data.get(cols.EXEMPLO_1, '').strip(),
        cols.EXEMPLO_2: note_data.get(cols.EXEMPLO_2, '').strip(),
        cols.EXEMPLO_3: note_data.get(cols.EXEMPLO_3, '').strip(),
        # Campos de metadados
        cols.BANCAS: note_data.get(cols.BANCAS, '').strip(),
        cols.ANO: note_data.get(cols.ANO, '').strip(),
        cols.CARREIRA: note_data.get(cols.CARREIRA, '').strip(),
        cols.IMPORTANCIA: note_data.get(cols.IMPORTANCIA, '').strip(),
        cols.MORE_TAGS: note_data.get(cols.MORE_TAGS, '').strip(),
    }
    
    # Preencher campos disponíveis na nota
    for field_name in note.keys():
        if field_name in field_mappings:
            note[field_name] = field_mappings[field_name]


def determine_target_deck_for_student(col, base_deck_id, note_data, student, deck_url, debug_messages=None):
    """
    Determina o deck de destino para um aluno específico.
    
    Args:
        col: Coleção do Anki
        base_deck_id (int): ID do deck base
        note_data (dict): Dados da nota
        student (str): Nome do aluno
        deck_url (str): URL do deck
        debug_messages (list, optional): Lista para debug
        
    Returns:
        int: ID do deck de destino
    """
    def add_debug_msg(message, category="DECK_TARGET_STUDENT"):
        """Helper para adicionar mensagens de debug usando o sistema global."""
        from .utils import add_debug_message
        add_debug_message(message, category)
    
    try:
        # Obter deck base
        base_deck = col.decks.get(base_deck_id)
        if not base_deck:
            return base_deck_id
        
        # Gerar nome do subdeck com estrutura completa para o aluno específico
        from .config_manager import get_deck_remote_name
        remote_deck_name = get_deck_remote_name(deck_url)
        
        # Criar deck base seguindo o padrão: Sheets2Anki::{remote_deck_name}
        deck_with_remote_name = f"Sheets2Anki::{remote_deck_name}"
        subdeck_name = get_subdeck_name(deck_with_remote_name, note_data, student=student)
        subdeck_id = ensure_subdeck_exists(subdeck_name)
        
        if subdeck_id:
            add_debug_msg(f"Nota direcionada para subdeck do aluno {student}: {subdeck_name}")
            return subdeck_id
        
        return base_deck_id
        
    except Exception as e:
        add_debug_msg(f"Erro ao determinar deck de destino para aluno {student}: {e}")
        return base_deck_id