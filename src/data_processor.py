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
    # Garantir valores padrão para campos importantes
    if not note_data.get(cols.TOPICO):
        note_data[cols.TOPICO] = DEFAULT_TOPIC
    
    if not note_data.get(cols.SUBTOPICO):
        note_data[cols.SUBTOPICO] = DEFAULT_SUBTOPIC
    
    if not note_data.get(cols.CONCEITO):
        note_data[cols.CONCEITO] = DEFAULT_CONCEPT
    
    # Criar tags hierárquicas
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
    
    if topico and topico != DEFAULT_TOPIC:
        tags.append(f"{TAG_ROOT}::{TAG_TOPICS}::{topico}")
    
    if subtopico and subtopico != DEFAULT_SUBTOPIC:
        tags.append(f"{TAG_ROOT}::{TAG_SUBTOPICS}::{subtopico}")
    
    if conceito and conceito != DEFAULT_CONCEPT:
        tags.append(f"{TAG_ROOT}::{TAG_CONCEPTS}::{conceito}")
    
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
    def add_debug_msg(message, category="NOTE_PROCESSOR"):
        """Helper para adicionar mensagens de debug com timestamp."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] [{category}] {message}"
        if debug_messages is not None:
            debug_messages.append(formatted_msg)
        print(formatted_msg)
    
    stats = {
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'errors': 0,
        'skipped': 0,
        'total_remote': len(remoteDeck.notes)
    }
    
    try:
        add_debug_msg(f"Iniciando sincronização de {stats['total_remote']} notas remotas")
        
        # 1. Identificar todos os alunos únicos nas notas E que estão habilitados
        from .config_manager import get_enabled_students, is_auto_remove_disabled_students, is_sync_missing_students_notes
        enabled_students = set(get_enabled_students() or [])
        
        # Incluir [MISSING A.] na lista de estudantes habilitados se a funcionalidade estiver ativa
        if is_sync_missing_students_notes():
            enabled_students.add("[MISSING A.]")
            add_debug_msg(f"Funcionalidade [MISSING A.] ativada, incluindo na lista de estudantes", "MISSING_STUDENTS")
        
        add_debug_msg(f"Alunos habilitados: {sorted(enabled_students)}")
        
        # 1.1 Limpar note types de alunos desabilitados se configurado
        if is_auto_remove_disabled_students():
            add_debug_msg(f"Auto-remove habilitado, verificando note types de alunos desabilitados...")
            cleanup_disabled_students_note_types(col, deck_url, enabled_students, debug_messages)
        
        all_students = set()
        for note_data in remoteDeck.notes:
            alunos_str = note_data.get(cols.ALUNOS, '').strip()
            if alunos_str:
                students_list = [s.strip() for s in alunos_str.split(',') if s.strip()]
                # Filtrar apenas alunos habilitados
                enabled_students_in_note = [s for s in students_list if s in enabled_students]
                all_students.update(enabled_students_in_note)
            elif is_sync_missing_students_notes():
                # Nota sem alunos específicos, incluir [MISSING A.] se funcionalidade ativa
                all_students.add("[MISSING A.]")
        
        # 2. Garantir que os note types existem APENAS para alunos habilitados
        add_debug_msg(f"Criando note types para {len(all_students)} alunos habilitados: {sorted(all_students)}")
        for student in all_students:
            ensure_custom_models(col, deck_url, student=student, debug_messages=debug_messages)
        
        # 3. Obter notas existentes no deck
        existing_notes = get_existing_notes_by_id(col, deck_id)
        add_debug_msg(f"Encontradas {len(existing_notes)} notas existentes no deck")
        
        # 4. Processar notas remotas - CRIAR UMA NOTA PARA CADA ALUNO HABILITADO
        remote_ids = set()
        
        for note_data in remoteDeck.notes:
            try:
                note_id = note_data.get(cols.ID, '').strip()
                if not note_id:
                    stats['errors'] += 1
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
                    from .config_manager import is_sync_missing_students_notes
                    if is_sync_missing_students_notes():
                        # Processar como [MISSING A.]
                        students_in_note = ["[MISSING A.]"]
                        enabled_students_in_note = ["[MISSING A.]"]
                        add_debug_msg(f"Nota {note_id}: sem alunos específicos, processando como [MISSING A.]", "MISSING_STUDENTS")
                    else:
                        # Pular nota sem alunos específicos
                        stats['skipped'] += 1
                        add_debug_msg(f"Nota {note_id}: sem alunos específicos, pulando (funcionalidade desabilitada)", "MISSING_STUDENTS")
                        continue
                else:
                    students_in_note = [s.strip() for s in alunos_str.split(',') if s.strip()]
                    enabled_students_in_note = [s for s in students_in_note if s in enabled_students]
                
                add_debug_msg(f"Nota {note_id}: alunos={students_in_note}, habilitados={enabled_students_in_note}")
                
                if not enabled_students_in_note:
                    # Nenhum aluno habilitado nesta nota
                    stats['skipped'] += 1
                    continue
                
                # Processar cada aluno habilitado individualmente
                for student in enabled_students_in_note:
                    # Criar ID único para esta combinação nota-aluno
                    student_note_id = f"{note_id}_{student}"
                    remote_ids.add(student_note_id)
                    
                    # Verificar se já existe nota para este aluno
                    if student_note_id in existing_notes:
                        if update_existing_note_for_student(col, existing_notes[student_note_id], note_data, student, deck_url, debug_messages):
                            stats['updated'] += 1
                        else:
                            stats['errors'] += 1
                    else:
                        if create_new_note_for_student(col, note_data, student, deck_id, deck_url, debug_messages):
                            stats['created'] += 1
                        else:
                            stats['errors'] += 1
                        
            except Exception as e:
                add_debug_msg(f"Erro ao processar nota {note_data.get(cols.ID, 'UNKNOWN')}: {e}")
                stats['errors'] += 1
        
        # 4. Remover notas que não existem mais na fonte remota
        notes_to_delete = set(existing_notes.keys()) - remote_ids
        for note_id in notes_to_delete:
            try:
                if delete_note_by_id(col, existing_notes[note_id]):
                    stats['deleted'] += 1
                else:
                    stats['errors'] += 1
            except Exception as e:
                add_debug_msg(f"Erro ao deletar nota {note_id}: {e}")
                stats['errors'] += 1
        
        # 5. Salvar alterações
        try:
            col.save()
            add_debug_msg("Coleção salva com sucesso")
        except Exception as e:
            raise CollectionSaveError(f"Falha ao salvar coleção: {e}")
        
        add_debug_msg(f"Sincronização concluída: +{stats['created']} ~{stats['updated']} -{stats['deleted']} !{stats['errors']}")
        
        return stats
        
    except Exception as e:
        add_debug_msg(f"Erro crítico na sincronização: {e}")
        raise SyncError(f"Falha na sincronização de notas: {e}")

def get_existing_notes_by_id(col, deck_id):
    """
    Obtém mapeamento de notas existentes no deck por ID único por aluno.
    Inclui notas em subdecks do deck principal.
    
    Args:
        col: Coleção do Anki
        deck_id (int): ID do deck
        
    Returns:
        dict: Mapeamento {student_note_id: note_object} onde student_note_id = "note_id_student"
    """
    existing_notes = {}
    
    try:
        # Obter o deck principal
        deck = col.decks.get(deck_id)
        if not deck:
            return existing_notes
            
        deck_name = deck['name']
        
        # Buscar cards no deck principal E em todos os subdecks
        # Usar o padrão "deck:{deck_name}*" para incluir subdecks
        search_query = f'deck:"{deck_name}" OR deck:"{deck_name}::*"'
        card_ids = col.find_cards(search_query)
        
        for card_id in card_ids:
            try:
                card = col.get_card(card_id)
                note = card.note()
                
                # Obter ID da nota do campo ID
                note_fields = note.keys()
                if cols.ID in note_fields:
                    note_id = note[cols.ID].strip()
                    if note_id:
                        # Extrair aluno do subdeck onde a nota está
                        card_deck = col.decks.get(card.did)
                        if card_deck:
                            subdeck_name = card_deck['name']
                            # Estrutura: Sheets2Anki::Remote::Aluno::Importancia::...
                            deck_parts = subdeck_name.split("::")
                            if len(deck_parts) >= 3:
                                student = deck_parts[2]  # Terceiro elemento é o aluno
                                student_note_id = f"{note_id}_{student}"
                                existing_notes[student_note_id] = note
                            else:
                                # Nota no deck principal, sem aluno específico - ignorar
                                pass
                        
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
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] [{category}] {message}"
        if debug_messages is not None:
            debug_messages.append(formatted_msg)
        print(formatted_msg)
    
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
        
        # Preencher campos
        fill_note_fields(note, note_data)
        
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

def update_existing_note_for_student(col, existing_note, new_data, student, deck_url, debug_messages=None):
    """
    Atualiza uma nota existente para um aluno específico.
    
    Args:
        col: Coleção do Anki
        existing_note: Nota existente no Anki
        new_data (dict): Novos dados da nota
        student (str): Nome do aluno
        deck_url (str): URL do deck
        debug_messages (list, optional): Lista para debug
        
    Returns:
        bool: True se atualizada com sucesso, False caso contrário
    """
    def add_debug_msg(message, category="UPDATE_NOTE_STUDENT"):
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] [{category}] {message}"
        if debug_messages is not None:
            debug_messages.append(formatted_msg)
        print(formatted_msg)
    
    try:
        note_id = new_data.get(cols.ID, '').strip()
        add_debug_msg(f"Atualizando nota existente para aluno {student}: {note_id}")
        
        # Preencher campos com novos dados
        fill_note_fields(existing_note, new_data)
        
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
        return True
        
    except Exception as e:
        add_debug_msg(f"❌ Erro ao atualizar nota para {student}: {e}")
        return False
    """
    Cria uma nova nota no Anki.
    
    Args:
        col: Coleção do Anki
        note_data (dict): Dados da nota
        deck_id (int): ID do deck
        deck_url (str): URL do deck
        debug_messages (list, optional): Lista para debug
        
    Returns:
        bool: True se criada com sucesso, False caso contrário
    """
    def add_debug_msg(message, category="CREATE_NOTE"):
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] [{category}] {message}"
        if debug_messages is not None:
            debug_messages.append(formatted_msg)
        print(formatted_msg)
    
    try:
        note_id = note_data.get(cols.ID, '').strip()
        add_debug_msg(f"Criando nova nota: {note_id}")
        
        # Determinar tipo de nota (cloze ou básica)
        pergunta = note_data.get(cols.PERGUNTA, '')
        is_cloze = has_cloze_deletion(pergunta)
        
        # Obter modelo apropriado - incluindo APENAS aluno habilitado no note type
        from .utils import get_note_type_name
        from .config_manager import get_deck_remote_name, get_enabled_students
        
        # Obter primeiro aluno HABILITADO para criar note type específico
        alunos_str = note_data.get(cols.ALUNOS, '').strip()
        students_list = [s.strip() for s in alunos_str.split(',') if s.strip()] if alunos_str else []
        
        # Filtrar apenas alunos habilitados
        enabled_students = set(get_enabled_students() or [])
        enabled_students_in_note = [s for s in students_list if s in enabled_students]
        first_enabled_student = enabled_students_in_note[0] if enabled_students_in_note else None
        
        add_debug_msg(f"Alunos na nota: {students_list}, Alunos habilitados na nota: {enabled_students_in_note}")
        add_debug_msg(f"Primeiro aluno habilitado selecionado: {first_enabled_student}")
        
        remote_deck_name = get_deck_remote_name(deck_url)
        note_type_name = get_note_type_name(deck_url, remote_deck_name, student=first_enabled_student, is_cloze=is_cloze)
        
        model = col.models.by_name(note_type_name)
        if not model:
            add_debug_msg(f"❌ ERRO: Modelo não encontrado: '{note_type_name}' para aluno: {first_enabled_student}")
            add_debug_msg(f"❌ Tentando criar note type para nota: {note_id}")
            # Tentar criar o modelo se não existir
            from .templates_and_definitions import ensure_custom_models
            models = ensure_custom_models(col, deck_url, student=first_enabled_student, debug_messages=debug_messages)
            model = models.get('cloze' if is_cloze else 'standard')
            if not model:
                add_debug_msg(f"❌ ERRO CRÍTICO: Não foi possível criar/encontrar modelo: {note_type_name}")
                return False
            add_debug_msg(f"✅ Modelo criado com sucesso: {note_type_name}")
        
        add_debug_msg(f"✅ Modelo encontrado: {note_type_name} (ID: {model['id'] if model else 'None'})")
        
        # Criar nota
        note = col.new_note(model)
        
        # Preencher campos
        fill_note_fields(note, note_data)
        
        # Adicionar tags
        tags = note_data.get('tags', [])
        if tags:
            note.tags = tags
        
        # Determinar deck de destino (considerando subdecks por aluno)
        add_debug_msg(f"Determinando deck de destino para nota: {note_id}")
        target_deck_id = determine_target_deck(col, deck_id, note_data, deck_url, debug_messages)
        add_debug_msg(f"Deck de destino determinado: {target_deck_id}")
        
        # Adicionar nota ao deck
        add_debug_msg(f"Adicionando nota {note_id} ao deck {target_deck_id}")
        col.add_note(note, target_deck_id)
        add_debug_msg(f"✅ Nota {note_id} adicionada com sucesso ao deck {target_deck_id}")
        
        add_debug_msg(f"Nota criada com sucesso: {note_id}")
        return True
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        add_debug_msg(f"❌ ERRO ao criar nota {note_data.get(cols.ID, 'UNKNOWN')}: {e}")
        add_debug_msg(f"❌ Stack trace: {error_details}")
        print(f"[CREATE_NOTE_ERROR] {note_data.get(cols.ID, 'UNKNOWN')}: {e}")
        print(f"[CREATE_NOTE_ERROR] Stack trace: {error_details}")
        return False

def update_existing_note(col, existing_note, new_data, deck_url, debug_messages=None):
    """
    Atualiza uma nota existente.
    
    Args:
        col: Coleção do Anki
        existing_note: Nota existente no Anki
        new_data (dict): Novos dados da nota
        deck_url (str): URL do deck
        debug_messages (list, optional): Lista para debug
        
    Returns:
        bool: True se atualizada com sucesso, False caso contrário
    """
    def add_debug_msg(message, category="UPDATE_NOTE"):
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] [{category}] {message}"
        if debug_messages is not None:
            debug_messages.append(formatted_msg)
        print(formatted_msg)
    
    try:
        note_id = new_data.get(cols.ID, '').strip()
        add_debug_msg(f"Atualizando nota existente: {note_id}")
        
        # Preencher campos com novos dados
        fill_note_fields(existing_note, new_data)
        
        # Atualizar tags
        tags = new_data.get('tags', [])
        if tags:
            existing_note.tags = tags
        
        # Verificar se precisa mover para subdeck diferente
        cards = existing_note.cards()
        if cards:
            current_deck_id = cards[0].did
            target_deck_id = determine_target_deck(col, current_deck_id, new_data, deck_url, debug_messages)
            
            if current_deck_id != target_deck_id:
                # Mover cards para novo deck
                for card in cards:
                    card.did = target_deck_id
                    col.update_card(card)
        
        # Salvar alterações da nota
        existing_note.flush()
        
        add_debug_msg(f"Nota atualizada com sucesso: {note_id}")
        return True
        
    except Exception as e:
        add_debug_msg(f"Erro ao atualizar nota {new_data.get(cols.ID, 'UNKNOWN')}: {e}")
        return False

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

def fill_note_fields(note, note_data):
    """
    Preenche os campos de uma nota com dados da planilha.
    
    Args:
        note: Nota do Anki
        note_data (dict): Dados da planilha
    """
    # Mapeamento direto de campos
    field_mappings = {
        cols.ID: cols.ID,
        cols.PERGUNTA: cols.PERGUNTA,
        cols.MATCH: cols.MATCH,
        cols.TOPICO: cols.TOPICO,
        cols.SUBTOPICO: cols.SUBTOPICO,
        cols.CONCEITO: cols.CONCEITO,
        cols.EXTRA_INFO_1: cols.EXTRA_INFO_1,
        cols.EXTRA_INFO_2: cols.EXTRA_INFO_2,
        cols.EXEMPLO_1: cols.EXEMPLO_1,
        cols.EXEMPLO_2: cols.EXEMPLO_2,
        cols.EXEMPLO_3: cols.EXEMPLO_3,
    }
    
    # Preencher campos disponíveis
    for field_name in note.keys():
        if field_name in field_mappings:
            source_field = field_mappings[field_name]
            value = note_data.get(source_field, '').strip()
            note[field_name] = value

def determine_target_deck(col, base_deck_id, note_data, deck_url, debug_messages=None):
    """
    Determina o deck de destino considerando subdecks por aluno.
    
    Args:
        col: Coleção do Anki
        base_deck_id (int): ID do deck base
        note_data (dict): Dados da nota
        deck_url (str): URL do deck
        debug_messages (list, optional): Lista para debug
        
    Returns:
        int: ID do deck de destino
    """
    def add_debug_msg(message, category="DECK_TARGET"):
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] [{category}] {message}"
        if debug_messages is not None:
            debug_messages.append(formatted_msg)
        print(formatted_msg)
    
    try:
        # Verificar se há configuração de alunos
        note_students = note_data.get(cols.ALUNOS, '').strip()
        
        if not note_students:
            # Sem alunos específicos, usar deck base
            return base_deck_id
        
        # Obter deck base
        base_deck = col.decks.get(base_deck_id)
        if not base_deck:
            return base_deck_id
        
        base_deck_name = base_deck['name']
        
        # Processar primeiro aluno HABILITADO da lista para determinar subdeck
        from .config_manager import get_enabled_students
        enabled_students = set(get_enabled_students() or [])
        
        students_list = [s.strip() for s in note_students.split(',')]
        # Filtrar apenas alunos habilitados
        enabled_students_in_note = [s for s in students_list if s in enabled_students]
        first_enabled_student = enabled_students_in_note[0] if enabled_students_in_note else None
        
        add_debug_msg(f"Todos os alunos: {students_list}, Habilitados: {enabled_students_in_note}")
        
        if first_enabled_student:
            # Precisamos dos campos da nota para gerar o subdeck corretamente
            # Obter campos da nota para estrutura completa do subdeck
            fields = note_data.get('fields', {})
            
            # Gerar nome do subdeck com estrutura completa: {deckraiz}::{remote_deck_name}::{aluno}::{importancia}::{topico}::{subtopico}::{conceito}
            from .config_manager import get_deck_remote_name
            remote_deck_name = get_deck_remote_name(deck_url)
            
            # Criar deck base seguindo o padrão: Sheets2Anki::{remote_deck_name}
            deck_with_remote_name = f"Sheets2Anki::{remote_deck_name}"
            subdeck_name = get_subdeck_name(deck_with_remote_name, fields, student=first_enabled_student)
            subdeck_id = ensure_subdeck_exists(subdeck_name)
            
            if subdeck_id:
                add_debug_msg(f"Nota direcionada para subdeck: {subdeck_name}")
                return subdeck_id
        
        return base_deck_id
        
    except Exception as e:
        add_debug_msg(f"Erro ao determinar deck de destino: {e}")
        return base_deck_id


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
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] [{category}] {message}"
        if debug_messages is not None:
            debug_messages.append(formatted_msg)
        print(formatted_msg)
    
    try:
        # Obter deck base
        base_deck = col.decks.get(base_deck_id)
        if not base_deck:
            return base_deck_id
        
        base_deck_name = base_deck['name']
        
        # Obter campos da nota para estrutura completa do subdeck
        fields = note_data
        
        # Gerar nome do subdeck com estrutura completa para o aluno específico
        from .config_manager import get_deck_remote_name
        remote_deck_name = get_deck_remote_name(deck_url)
        
        # Criar deck base seguindo o padrão: Sheets2Anki::{remote_deck_name}
        deck_with_remote_name = f"Sheets2Anki::{remote_deck_name}"
        subdeck_name = get_subdeck_name(deck_with_remote_name, fields, student=student)
        subdeck_id = ensure_subdeck_exists(subdeck_name)
        
        if subdeck_id:
            add_debug_msg(f"Nota direcionada para subdeck do aluno {student}: {subdeck_name}")
            return subdeck_id
        
        return base_deck_id
        
    except Exception as e:
        add_debug_msg(f"Erro ao determinar deck de destino para aluno {student}: {e}")
        return base_deck_id


def cleanup_disabled_students_note_types(col, deck_url, enabled_students, debug_messages=None):
    """
    Remove note types de alunos que não estão mais habilitados.
    Inclui também limpeza de note types [MISSING A.] se a funcionalidade estiver desabilitada.
    
    Args:
        col: Coleção do Anki
        deck_url (str): URL do deck
        enabled_students (set): Conjunto de alunos habilitados
        debug_messages (list, optional): Lista para debug
    """
    def add_debug_msg(message, category="CLEANUP_DISABLED"):
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] [{category}] {message}"
        if debug_messages is not None:
            debug_messages.append(formatted_msg)
        print(formatted_msg)
    
    try:
        from .config_manager import get_deck_note_type_ids, get_deck_remote_name, is_sync_missing_students_notes
        from .utils import unregister_note_type_from_deck
        
        # Obter note types existentes para este deck
        existing_note_types = get_deck_note_type_ids(deck_url) or {}
        remote_deck_name = get_deck_remote_name(deck_url)
        
        if not existing_note_types:
            add_debug_msg(f"Nenhum note type encontrado para limpeza")
            return
        
        add_debug_msg(f"Verificando {len(existing_note_types)} note types existentes")
        
        # Verificar se deve incluir [MISSING A.] na lista para remoção
        should_clean_missing_students = not is_sync_missing_students_notes()
        if should_clean_missing_students:
            add_debug_msg(f"Funcionalidade [MISSING A.] desabilitada, incluindo na limpeza", "MISSING_STUDENTS")
            # Adicionar [MISSING A.] à lista de estudantes a serem removidos
            students_to_remove = set()
            for student in enabled_students:
                students_to_remove.add(student)
            students_to_remove.add("[MISSING A.]")  # Incluir para remoção
            enabled_students_final = set(enabled_students)  # Manter apenas estudantes reais habilitados
        else:
            add_debug_msg(f"Funcionalidade [MISSING A.] habilitada, mantendo note types", "MISSING_STUDENTS")
            enabled_students_final = set(enabled_students) | {"[MISSING A.]"}  # Incluir [MISSING A.] como "habilitado"
        
        note_types_to_remove = []
        
        # Analisar cada note type
        for note_type_id_str, note_type_name in existing_note_types.items():
            # Padrão: "Sheets2Anki - {remote_deck_name} - {aluno} - {Basic|Cloze}"
            if f" - {remote_deck_name} - " in note_type_name:
                # Extrair nome do aluno
                parts = note_type_name.split(" - ")
                if len(parts) >= 4:  # ["Sheets2Anki", remote_deck_name, aluno, "Basic/Cloze"]
                    student_name = parts[2]
                    
                    if student_name not in enabled_students_final:
                        note_types_to_remove.append((note_type_id_str, note_type_name, student_name))
                        if student_name == "[MISSING A.]":
                            add_debug_msg(f"Note type [MISSING A.] marcado para remoção (funcionalidade desabilitada): '{note_type_name}'", "MISSING_STUDENTS")
                        else:
                            add_debug_msg(f"Note type marcado para remoção: '{note_type_name}' (aluno desabilitado: '{student_name}')")
        
        # Remover note types de alunos desabilitados
        if note_types_to_remove:
            add_debug_msg(f"Removendo {len(note_types_to_remove)} note types de alunos desabilitados...")
            
            for note_type_id_str, note_type_name, student_name in note_types_to_remove:
                try:
                    # Verificar se o note type ainda tem notas em uso
                    note_type_id = int(note_type_id_str)
                    notes_using_type = col.find_notes(f"note:{note_type_id}")
                    
                    if notes_using_type:
                        add_debug_msg(f"⚠️ Note type '{note_type_name}' tem {len(notes_using_type)} notas em uso, não removendo")
                        continue
                    
                    # Remover note type do Anki
                    if mw and mw.col:
                        from anki.notetypes import NotetypeId
                        model = col.models.get(NotetypeId(note_type_id))
                        if model:
                            col.models.remove(NotetypeId(note_type_id))
                            add_debug_msg(f"✅ Note type removido do Anki: '{note_type_name}'")
                    
                    # Tentar usar função de desregistro se existir, senão ignorar
                    try:
                        unregister_note_type_from_deck(deck_url, note_type_id)
                        add_debug_msg(f"✅ Note type desregistrado: '{note_type_name}'")
                    except:
                        # Se não existir função de desregistro, apenas remover do Anki
                        add_debug_msg(f"✅ Note type removido (apenas do Anki): '{note_type_name}'")
                    
                except Exception as e:
                    add_debug_msg(f"❌ Erro ao remover note type '{note_type_name}': {e}")
            
            add_debug_msg(f"✅ Limpeza de note types concluída")
        else:
            add_debug_msg(f"✅ Nenhum note type de aluno desabilitado encontrado")
            
    except Exception as e:
        add_debug_msg(f"❌ Erro durante limpeza: {e}")
