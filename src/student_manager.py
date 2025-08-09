"""
Gerenciamento de seleção de alunos para o addon Sheets2Anki.

Este módulo implementa funcionalidades para permitir ao usuário selecionar
quais alunos ele deseja sincroniz              if alunos_field:
            # Separar múltiplos alunos por vírgula, ponto e vírgula ou pipe
            alunos_list = re.split(r'[,;|]', alunos_field)
            for aluno in alunos_list: if alunos_field:
            # Separar múltiplos alunos por vírgula, ponto e vírgula ou pipe
            alunos_list = re.split(r'[,;|]', alunos_field)
            for aluno in alunos_list: if alunos_field:
            # Separar múltiplos alunos por vírgula, ponto e vírgula ou pipe
            alunos_list = re.split(r'[,;|]', alunos_field)
            for aluno in alunos_list: gerenciar a estrutura de subdecks por aluno.

Funcionalidades principais:
- Extração de alunos únicos das planilhas
- Interface para seleção de alunos
- Filtramento de notas por alunos selecionados
- Criação de subdecks hierárquicos por aluno
- Remoção de notas de alunos desmarcados
"""

import re
from typing import List, Set, Dict, Any, Optional
from .compat import (
    mw, showInfo, QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, 
    QLabel, QPushButton, QScrollArea, QWidget, QFrame, QGroupBox,
    QDialogButtonBox, QTextEdit, ButtonBox_Ok, ButtonBox_Cancel,
    safe_exec_dialog, DialogAccepted
)
from .config_manager import get_meta, save_meta, get_enabled_students, is_student_filter_active
from . import templates_and_definitions as cols

def get_students_to_sync(all_students: Set[str]) -> Set[str]:
    """
    Obtém os alunos que devem ser sincronizados baseado na configuração global.
    NOVA VERSÃO: Usa normalização consistente de nomes.
    
    Args:
        all_students (Set[str]): Todos os alunos encontrados na planilha (já normalizados)
        
    Returns:
        Set[str]: Alunos que devem ser sincronizados (nomes normalizados)
    """
    # Verificar se o filtro está ativo (baseado na lista de alunos habilitados)
    if not is_student_filter_active():
        # Filtro inativo - sincronizar todos (já normalizados)
        return all_students
    
    # Obter alunos habilitados globalmente (case-sensitive)
    enabled_students_raw = get_enabled_students()
    enabled_students_set = {student for student in enabled_students_raw if student and student.strip()}
    
    # Se não há alunos configurados, não sincronizar nenhum
    if not enabled_students_set:
        return set()
    
    # Interseção case-sensitive
    matched_students = all_students.intersection(enabled_students_set)
    
    print(f"🔍 SYNC: Filtro de alunos aplicado:")
    print(f"  • Alunos na planilha: {sorted(all_students)}")
    print(f"  • Alunos habilitados: {sorted(enabled_students_set)}")
    print(f"  • Alunos para sync: {sorted(matched_students)}")
    
    return matched_students


class StudentSelectionDialog(QDialog):
    """
    Dialog para seleção de alunos que o usuário deseja sincronizar.
    """
    
    def __init__(self, students: List[str], deck_url: str, current_selection: Set[str]):
        super().__init__()
        self.students = sorted(students)  # Ordenar alfabeticamente
        self.deck_url = deck_url
        self.current_selection = current_selection.copy()
        self.checkboxes = {}
        
        self.setWindowTitle("Seleção de Alunos - Sheets2Anki")
        self.setMinimumSize(500, 400)
        self.resize(600, 500)
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Configura a interface do usuário."""
        layout = QVBoxLayout()
        
        # Título e explicação
        title_label = QLabel("Selecione os alunos que deseja sincronizar:")
        title_label.setStyleSheet("font-weight: bold; font-size: 12px; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        info_text = QTextEdit()
        info_text.setPlainText(
            "• Alunos selecionados terão suas notas sincronizadas em subdecks separados\n"
            "• Alunos desmarcados terão suas notas removidas dos decks locais\n"
            "• A estrutura será: Deck Raiz::Deck Remoto::Aluno::Importância::Tópico::Subtópico::Conceito\n"
            "• Cada aluno terá seu próprio Note Type personalizado"
        )
        info_text.setMaximumHeight(80)
        info_text.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc; padding: 5px;")
        layout.addWidget(info_text)
        
        # Botões de seleção rápida
        quick_select_layout = QHBoxLayout()
        select_all_btn = QPushButton("Selecionar Todos")
        select_all_btn.clicked.connect(self._select_all)
        select_none_btn = QPushButton("Desmarcar Todos")
        select_none_btn.clicked.connect(self._select_none)
        
        quick_select_layout.addWidget(select_all_btn)
        quick_select_layout.addWidget(select_none_btn)
        quick_select_layout.addStretch()
        
        layout.addLayout(quick_select_layout)
        
        # Área de scroll para os checkboxes
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        
        # Criar checkboxes para cada aluno
        for student in self.students:
            checkbox = QCheckBox(student)
            checkbox.setChecked(student in self.current_selection)
            self.checkboxes[student] = checkbox
            scroll_layout.addWidget(checkbox)
        
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        
        layout.addWidget(scroll_area)
        
        # Botões de ação
        button_box = QDialogButtonBox(ButtonBox_Ok | ButtonBox_Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def _select_all(self):
        """Seleciona todos os alunos."""
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(True)
    
    def _select_none(self):
        """Desmarca todos os alunos."""
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(False)
    
    def get_selected_students(self) -> Set[str]:
        """Retorna o conjunto de alunos selecionados."""
        selected = set()
        for student, checkbox in self.checkboxes.items():
            if checkbox.isChecked():
                selected.add(student)
        return selected


def extract_students_from_remote_data(remote_deck) -> Set[str]:
    """
    Extrai todos os alunos únicos presentes nos dados remotos.
    
    LÓGICA REFATORADA:
    - Usa a nova estrutura RemoteDeck.notes
    - Extrai alunos da coluna ALUNOS de cada nota
    - Retorna conjunto com nomes case-sensitive
    
    Args:
        remote_deck: Objeto RemoteDeck com os dados da planilha
        
    Returns:
        Set[str]: Conjunto de alunos únicos encontrados
    """
    students = set()
    
    if not hasattr(remote_deck, 'notes') or not remote_deck.notes:
        return students
    
    for note_data in remote_deck.notes:
        alunos_field = note_data.get(cols.ALUNOS, '').strip()
        
        if alunos_field:
            # Separar múltiplos alunos por vírgula
            alunos_list = [s.strip() for s in alunos_field.split(',') if s.strip()]
            for aluno in alunos_list:
                if aluno:
                    # Adicionar nome do estudante (case-sensitive)
                    students.add(aluno)
    
    return students


def get_selected_students_for_deck(deck_url: str) -> Set[str]:
    """
    Obtém os alunos selecionados para um deck específico.
    Se não houver seleção específica para o deck, usa a configuração global.
    
    Args:
        deck_url: URL do deck remoto
        
    Returns:
        Set[str]: Conjunto de alunos selecionados para este deck
    """
    from .config_manager import get_meta, get_deck_hash, get_enabled_students
    
    meta = get_meta()
    
    # Navegar pela estrutura: decks -> deck_hash -> student_selection
    deck_hash = get_deck_hash(deck_url)
    deck_config = meta.get('decks', {}).get(deck_hash, {})
    student_selection = deck_config.get('student_selection')
    
    # Se não há seleção específica para o deck, usar configuração global
    if student_selection is None:
        global_enabled = get_enabled_students()
        return set(global_enabled) if global_enabled else set()
    
    # Converter para set se for lista
    if isinstance(student_selection, list):
        return set(student_selection)
    
    return student_selection if isinstance(student_selection, set) else set()


def save_selected_students_for_deck(deck_url: str, selected_students: Set[str]):
    """
    Salva a seleção de alunos para um deck específico.
    
    Args:
        deck_url: URL do deck remoto
        selected_students: Conjunto de alunos selecionados
    """
    from .config_manager import get_meta, save_meta, get_deck_hash
    
    meta = get_meta()
    
    # Garantir estrutura do meta
    if 'decks' not in meta:
        meta['decks'] = {}
    
    deck_hash = get_deck_hash(deck_url)
    if deck_hash not in meta['decks']:
        meta['decks'][deck_hash] = {}
    
    # Converter set para lista para serialização JSON
    meta['decks'][deck_hash]['student_selection'] = list(selected_students)
    
    save_meta(meta)


def show_student_selection_dialog(deck_url: str, available_students: Set[str]) -> Optional[Set[str]]:
    """
    Mostra o dialog de seleção de alunos e retorna a seleção do usuário.
    
    Args:
        deck_url: URL do deck remoto
        available_students: Conjunto de alunos disponíveis na planilha
        
    Returns:
        Optional[Set[str]]: Conjunto de alunos selecionados ou None se cancelado
    """
    if not available_students:
        showInfo("Não foram encontrados alunos na coluna ALUNOS da planilha.")
        return None
    
    current_selection = get_selected_students_for_deck(deck_url)
    
    dialog = StudentSelectionDialog(
        list(available_students), 
        deck_url, 
        current_selection
    )
    
    if safe_exec_dialog(dialog) == DialogAccepted:
        selected = dialog.get_selected_students()
        save_selected_students_for_deck(deck_url, selected)
        return selected
    
    return None


def filter_questions_by_selected_students(questions: List[Dict], selected_students: Set[str]) -> List[Dict]:
    """
    Filtra questões baseado nos alunos selecionados.
    NOVA VERSÃO: Usa normalização consistente de nomes.
    
    NOVO: Se sync_missing_students_notes estiver ativado, inclui questões com ALUNOS vazio
    para sincronização no deck [MISSING A.]
    
    Args:
        questions: Lista de questões do deck remoto
        selected_students: Conjunto de alunos selecionados (já normalizados)
        
    Returns:
        List[Dict]: Lista filtrada de questões
    """
    if not selected_students:
        return []
    
    # Verificar se deve incluir notas sem alunos específicos
    from .config_manager import is_sync_missing_students_notes
    include_missing_students = is_sync_missing_students_notes()
    
    filtered_questions = []
    
    print(f"🔍 FILTRO: Iniciando filtro de questões...")
    print(f"  • Total de questões: {len(questions)}")
    print(f"  • Alunos selecionados (norm): {sorted(selected_students)}")
    print(f"  • Incluir [MISSING A.]: {include_missing_students}")
    
    for i, question in enumerate(questions):
        fields = question.get('fields', {})
        alunos_field = fields.get(cols.ALUNOS, '').strip()
        
        if not alunos_field:
            # NOVO: Se funcionalidade [MISSING A.] estiver ativa, incluir nota
            if include_missing_students:
                filtered_questions.append(question)
                print(f"  📝 Questão {i+1}: SEM aluno → incluída ([MISSING A.] ativo)")
            else:
                print(f"  ❌ Questão {i+1}: SEM aluno → ignorada ([MISSING A.] inativo)")
            continue
        
        # Verificar se algum dos alunos selecionados está na lista de alunos da questão
        question_students = set()
        alunos_list = re.split(r'[,;|]', alunos_field)
        for aluno in alunos_list:
            aluno = aluno.strip()
            if aluno:
                # Adicionar nome do estudante (case-sensitive)
                question_students.add(aluno)
        
        # DEBUG: Mostrar comparação
        print(f"  📝 Questão {i+1}: '{alunos_field}' → {sorted(question_students)}")
        
        # Se há interseção entre alunos da questão e alunos selecionados (case-sensitive)
        intersection = question_students.intersection(selected_students)
        if intersection:
            filtered_questions.append(question)
            print(f"  ✅ Questão {i+1}: INCLUÍDA (match: {sorted(intersection)})")
        else:
            print(f"  ❌ Questão {i+1}: IGNORADA (sem match)")
    
    print(f"🎯 FILTRO: {len(filtered_questions)}/{len(questions)} questões selecionadas")
    return filtered_questions


def get_student_subdeck_name(main_deck_name: str, student: str, fields: Dict) -> str:
    """
    Gera o nome do subdeck para um aluno específico.
    
    A estrutura será: "deck raiz::deck remoto::aluno::importancia::topico::subtopico::conceito"
    
    Args:
        main_deck_name: Nome do deck principal
        student: Nome do aluno
        fields: Campos da nota com IMPORTANCIA, TOPICO, SUBTOPICO e CONCEITO
        
    Returns:
        str: Nome completo do subdeck do aluno
    """
    from .utils import DEFAULT_IMPORTANCE, DEFAULT_TOPIC, DEFAULT_SUBTOPIC, DEFAULT_CONCEPT
    
    # Obter valores dos campos, usando valores padrão se estiverem vazios
    importancia = fields.get(cols.IMPORTANCIA, "").strip() or DEFAULT_IMPORTANCE
    topico = fields.get(cols.TOPICO, "").strip() or DEFAULT_TOPIC
    subtopico = fields.get(cols.SUBTOPICO, "").strip() or DEFAULT_SUBTOPIC
    conceito = fields.get(cols.CONCEITO, "").strip() or DEFAULT_CONCEPT
    
    # Criar hierarquia completa incluindo o aluno
    return f"{main_deck_name}::{student}::{importancia}::{topico}::{subtopico}::{conceito}"


def get_missing_students_subdeck_name(main_deck_name: str, fields: Dict) -> str:
    """
    Gera o nome do subdeck para notas sem alunos específicos ([MISSING A.]).
    
    A estrutura será: "deck raiz::deck remoto::[MISSING A.]::importancia::topico::subtopico::conceito"
    
    Args:
        main_deck_name: Nome do deck principal  
        fields: Campos da nota com IMPORTANCIA, TOPICO, SUBTOPICO e CONCEITO
        
    Returns:
        str: Nome completo do subdeck [MISSING A.]
    """
    from .utils import DEFAULT_IMPORTANCE, DEFAULT_TOPIC, DEFAULT_SUBTOPIC, DEFAULT_CONCEPT
    
    # Obter valores dos campos, usando valores padrão se estiverem vazios
    importancia = fields.get(cols.IMPORTANCIA, "").strip() or DEFAULT_IMPORTANCE
    topico = fields.get(cols.TOPICO, "").strip() or DEFAULT_TOPIC
    subtopico = fields.get(cols.SUBTOPICO, "").strip() or DEFAULT_SUBTOPIC
    conceito = fields.get(cols.CONCEITO, "").strip() or DEFAULT_CONCEPT
    
    # Criar hierarquia completa com [MISSING A.] como "aluno"
    return f"{main_deck_name}::[MISSING A.]::{importancia}::{topico}::{subtopico}::{conceito}"


def get_students_from_question(fields: Dict) -> Set[str]:
    """
    Extrai todos os alunos de uma questão específica.
    
    Args:
        fields: Campos da questão
        
    Returns:
        Set[str]: Conjunto de alunos desta questão
    """
    students = set()
    alunos_field = fields.get(cols.ALUNOS, '').strip()
    
    if alunos_field:
        alunos_list = re.split(r'[,;|]', alunos_field)
        for aluno in alunos_list:
            aluno = aluno.strip()
            if aluno:
                students.add(aluno)
    
    return students


def remove_notes_for_unselected_students(col, main_deck_name: str, selected_students: Set[str], 
                                       all_students_in_sheet: Set[str]) -> int:
    """
    Remove notas de alunos que não estão mais selecionados.
    
    Args:
        col: Coleção do Anki
        main_deck_name: Nome do deck principal
        selected_students: Alunos selecionados
        all_students_in_sheet: Todos os alunos presentes na planilha
        
    Returns:
        int: Número de notas removidas
    """
    removed_count = 0
    
    if not mw or not hasattr(mw, 'col') or not mw.col:
        return removed_count
    
    # Encontrar alunos que devem ter suas notas removidas
    unselected_students = all_students_in_sheet - selected_students
    
    if not unselected_students:
        return removed_count
    
    # Para cada aluno não selecionado, encontrar e remover suas notas
    for student in unselected_students:
        # Buscar subdecks do aluno
        student_deck_pattern = f"{main_deck_name}::{student}::"
        
        # Encontrar todos os decks que começam com este padrão
        all_decks = mw.col.decks.all_names_and_ids()
        student_decks = [d for d in all_decks if d.name.startswith(student_deck_pattern)]
        
        for deck in student_decks:
            # Encontrar todas as notas neste deck
            note_ids = mw.col.find_notes(f'deck:"{deck.name}"')
            
            for note_id in note_ids:
                try:
                    mw.col.remove_notes([note_id])
                    removed_count += 1
                except Exception as e:
                    print(f"Erro ao remover nota {note_id} do deck {deck.name}: {e}")
    
    return removed_count

def discover_students_from_tsv_url(url: str) -> Set[str]:
    """
    Descobre alunos únicos de uma URL de TSV do Google Sheets.
    
    Args:
        url (str): URL do TSV do Google Sheets
        
    Returns:
        Set[str]: Conjunto de nomes de alunos únicos encontrados
    """
    try:
        print(f"🌐 DEBUG TSV: Fazendo download de {url}")
        
        # Imports necessários
        try:
            import urllib.request
            import csv
            from io import StringIO
        except ImportError as e:
            print(f"❌ Erro ao importar módulos necessários: {e}")
            return set()
        
        # Fazer download dos dados TSV
        with urllib.request.urlopen(url) as response:
            data = response.read().decode('utf-8')
        
        print(f"📄 DEBUG TSV: Downloaded {len(data)} characters")
        print(f"🔍 DEBUG TSV: First 200 chars: {repr(data[:200])}")
        
        # Parse CSV/TSV
        csv_reader = csv.DictReader(StringIO(data), delimiter='\t')
        
        students = set()
        row_count = 0
        
        # Verificar cabeçalhos primeiro
        fieldnames = csv_reader.fieldnames
        print(f"📋 DEBUG TSV: Fieldnames encontrados: {fieldnames}")
        print(f"🎯 DEBUG TSV: Procurando por coluna '{cols.ALUNOS}'")
        
        if not fieldnames or cols.ALUNOS not in fieldnames:
            print(f"⚠️ DEBUG TSV: Coluna '{cols.ALUNOS}' não encontrada nos cabeçalhos")
            available_cols = [col for col in fieldnames if col] if fieldnames else []
            print(f"📝 DEBUG TSV: Colunas disponíveis: {available_cols}")
            return set()
        
        # Procurar pela coluna ALUNOS
        for row in csv_reader:
            row_count += 1
            
            if row_count <= 3:  # Debug das primeiras 3 linhas
                print(f"📊 DEBUG TSV: Linha {row_count}: {dict(row)}")
            
            # Verificar se a coluna ALUNOS existe e tem conteúdo
            if cols.ALUNOS in row and row[cols.ALUNOS]:
                # Extrair alunos (podem estar separados por vírgula)
                alunos_str = row[cols.ALUNOS].strip()
                if alunos_str:
                    print(f"👥 DEBUG TSV: Linha {row_count} - Alunos encontrados: '{alunos_str}'")
                    # Split por vírgula e limpar espaços
                    for aluno in alunos_str.split(','):
                        aluno = aluno.strip()
                        if aluno:
                            students.add(aluno)
                            print(f"✅ DEBUG TSV: Adicionado aluno: '{aluno}'")
        
        print(f"📊 DEBUG TSV: Processadas {row_count} linhas")
        print(f"🎓 DEBUG TSV: Total de estudantes únicos encontrados: {len(students)}")
        print(f"📝 DEBUG TSV: Lista final: {sorted(students)}")
        
        return students
        
    except Exception as e:
        print(f"❌ Erro ao descobrir alunos da URL {url}: {e}")
        import traceback
        print(f"🔍 DEBUG TSV: Traceback completo:")
        traceback.print_exc()
        return set()


def cleanup_disabled_students_data(disabled_students: Set[str], deck_names: List[str]) -> Dict[str, int]:
    """
    Remove todos os dados de alunos desabilitados: notas, cards, note types e decks.
    
    LÓGICA REFATORADA para funcionar com IDs únicos {student}_{id}:
    - Busca notas por ID único usando o formato {student}_{id}
    - Remove notas baseado no campo ID das notas, não mais por localização em deck
    - Remove decks vazios após remoção das notas
    - Remove note types não utilizados
    
    Args:
        disabled_students (Set[str]): Conjunto de alunos que foram desabilitados
        deck_names (List[str]): Lista de nomes de decks remotos para filtrar operações
        
    Returns:
        Dict[str, int]: Estatísticas de remoção {
            'notes_removed': int,
            'decks_removed': int, 
            'note_types_removed': int
        }
    """
    if not disabled_students or not mw or not hasattr(mw, 'col') or not mw.col:
        return {'notes_removed': 0, 'decks_removed': 0, 'note_types_removed': 0}
    
    print(f"🗑️ CLEANUP: Iniciando limpeza de dados para alunos: {sorted(disabled_students)}")
    
    stats = {'notes_removed': 0, 'decks_removed': 0, 'note_types_removed': 0}
    col = mw.col
    
    try:
        # 1. Primeiro, encontrar e remover todas as notas dos alunos desabilitados
        notes_to_remove = []
        
        for student in disabled_students:
            print(f"🧹 CLEANUP: Processando aluno '{student}'...")
            
            # Buscar notas por ID único no formato {student}_{id} ou [MISSING A.]_{id}
            # Usar busca por campo ID que contém o student_note_id
            student_pattern = f"{student}_*"
            
            # Buscar todas as notas no Anki que tenham esse aluno no campo ID
            # Como não podemos fazer busca direta por campo personalizado, vamos iterar
            all_note_ids = col.find_notes("")  # Todas as notas
            student_note_ids = []
            
            for note_id in all_note_ids:
                try:
                    note = col.get_note(note_id)
                    # Verificar se a nota tem o campo ID e se corresponde ao aluno
                    if 'ID' in note.keys():
                        note_unique_id = note['ID'].strip()
                        # Verificar se o ID da nota começa com "{student}_"
                        if note_unique_id.startswith(f"{student}_"):
                            student_note_ids.append(note_id)
                            print(f"   � Encontrada nota do aluno '{student}': {note_unique_id}")
                except:
                    continue
            
            notes_to_remove.extend(student_note_ids)
            print(f"   📊 Total de notas encontradas para '{student}': {len(student_note_ids)}")
        
        # 2. Remover todas as notas encontradas
        if notes_to_remove:
            print(f"🗑️ CLEANUP: Removendo {len(notes_to_remove)} notas...")
            col.remove_notes(notes_to_remove)
            stats['notes_removed'] = len(notes_to_remove)
            print(f"✅ CLEANUP: {len(notes_to_remove)} notas removidas")
        
        # 3. Encontrar e remover decks vazios dos alunos desabilitados
        for student in disabled_students:
            for deck_name in deck_names:
                # Padrão de deck do aluno: "Sheets2Anki::{deck_name}::{student}::"
                student_deck_pattern = f"Sheets2Anki::{deck_name}::{student}::"
                
                # Encontrar todos os decks que começam com este padrão
                all_decks = col.decks.all_names_and_ids()
                matching_decks = [d for d in all_decks if d.name.startswith(student_deck_pattern)]
                
                for deck in matching_decks:
                    try:
                        # Verificar se o deck está vazio
                        remaining_notes = col.find_notes(f'deck:"{deck.name}"')
                        if not remaining_notes:
                            # Deck vazio, pode remover
                            from anki.decks import DeckId
                            deck_id = DeckId(deck.id)
                            col.decks.remove([deck_id])
                            stats['decks_removed'] += 1
                            print(f"   🗑️ Deck vazio removido: '{deck.name}'")
                        else:
                            print(f"   📁 Deck '{deck.name}' ainda tem {len(remaining_notes)} notas, mantendo")
                    except Exception as e:
                        print(f"   ❌ Erro ao processar deck '{deck.name}': {e}")
                        continue
            
            # Remover note types do aluno
            removed_note_types = _remove_student_note_types(student, deck_names)
            stats['note_types_removed'] += removed_note_types
        
        # NOVO: Atualizar meta.json após limpeza para remover referências de note types deletados
        _update_meta_after_cleanup(disabled_students, deck_names)
        
        # Salvar mudanças
        col.save()
        
        print(f"✅ CLEANUP: Concluído! Stats: {stats}")
        return stats
        
    except Exception as e:
        print(f"❌ CLEANUP: Erro durante limpeza: {e}")
        import traceback
        traceback.print_exc()
        return stats


def _remove_student_note_types(student: str, deck_names: List[str]) -> int:
    """
    Remove note types específicos de um aluno.
    
    Args:
        student (str): Nome do aluno
        deck_names (List[str]): Lista de nomes de decks remotos
        
    Returns:
        int: Número de note types removidos
    """
    if not mw or not hasattr(mw, 'col') or not mw.col:
        return 0
    
    col = mw.col
    removed_count = 0
    
    try:
        # Obter todos os note types
        note_types = col.models.all()
        
        for note_type in note_types:
            note_type_name = note_type.get('name', '')
            
            # Verificar se o note type pertence ao aluno
            # Formato: "Sheets2Anki - {remote_deck_name} - {student} - {Basic|Cloze}"
            for deck_name in deck_names:
                student_pattern_basic = f"Sheets2Anki - {deck_name} - {student} - Basic"
                student_pattern_cloze = f"Sheets2Anki - {deck_name} - {student} - Cloze"
                
                if note_type_name == student_pattern_basic or note_type_name == student_pattern_cloze:
                    try:
                        # Verificar se há notas usando este note type
                        note_ids = col.find_notes(f'note:{note_type_name}')
                        if note_ids:
                            print(f"   ⚠️ Note type '{note_type_name}' ainda tem {len(note_ids)} notas, pulando remoção")
                            continue
                        
                        # Remover o note type
                        col.models.remove(note_type['id'])
                        removed_count += 1
                        print(f"   🗑️ Note type '{note_type_name}' removido")
                        
                    except Exception as e:
                        print(f"   ❌ Erro ao remover note type '{note_type_name}': {e}")
                        continue
        
        return removed_count
        
    except Exception as e:
        print(f"❌ Erro ao remover note types do aluno '{student}': {e}")
        return 0


def _update_meta_after_cleanup(disabled_students: Set[str], deck_names: List[str]) -> None:
    """
    Atualiza o meta.json removendo referências de note types que foram deletados durante cleanup.
    
    Args:
        disabled_students (Set[str]): Conjunto de alunos que foram desabilitados
        deck_names (List[str]): Lista de nomes de decks remotos
    """
    try:
        from .config_manager import get_meta, save_meta, get_deck_hash
        
        print(f"📝 META UPDATE: Atualizando meta.json após limpeza de {len(disabled_students)} alunos")
        
        meta = get_meta()
        updates_made = False
        
        # Para cada deck configurado
        for deck_info in meta.get('decks', {}).values():
            deck_name = deck_info.get('remote_deck_name', '')
            if deck_name in deck_names:
                note_types_dict = deck_info.get('note_types', {})
                note_types_to_remove = []
                
                # Encontrar note types dos alunos desabilitados
                for note_type_id, note_type_name in note_types_dict.items():
                    for student in disabled_students:
                        # Formato: "Sheets2Anki - {remote_deck_name} - {student} - {Basic|Cloze}"
                        student_pattern_basic = f"Sheets2Anki - {deck_name} - {student} - Basic"
                        student_pattern_cloze = f"Sheets2Anki - {deck_name} - {student} - Cloze"
                        
                        if note_type_name == student_pattern_basic or note_type_name == student_pattern_cloze:
                            note_types_to_remove.append(note_type_id)
                            print(f"   🗑️ META: Removendo referência do note type '{note_type_name}' (ID: {note_type_id})")
                
                # Remover os note types encontrados
                for note_type_id in note_types_to_remove:
                    if note_type_id in note_types_dict:
                        del note_types_dict[note_type_id]
                        updates_made = True
        
        # Salvar meta.json atualizado se houve mudanças
        if updates_made:
            save_meta(meta)
            print(f"✅ META UPDATE: meta.json atualizado com {len([nt for deck in meta.get('decks', {}).values() for nt in deck.get('note_types', {}).keys()])} note types restantes")
        else:
            print(f"ℹ️ META UPDATE: Nenhuma atualização necessária no meta.json")
            
    except Exception as e:
        print(f"❌ META UPDATE: Erro ao atualizar meta.json após cleanup: {e}")
        import traceback
        traceback.print_exc()


def _update_meta_after_missing_cleanup(deck_names: List[str]) -> None:
    """
    Atualiza o meta.json removendo referências de note types [MISSING A.] que foram deletados.
    
    Args:
        deck_names (List[str]): Lista de nomes de decks remotos
    """
    try:
        from .config_manager import get_meta, save_meta
        
        print(f"📝 META UPDATE: Atualizando meta.json após limpeza [MISSING A.] para {len(deck_names)} decks")
        
        meta = get_meta()
        updates_made = False
        
        # Para cada deck configurado
        for deck_info in meta.get('decks', {}).values():
            deck_name = deck_info.get('remote_deck_name', '')
            if deck_name in deck_names:
                note_types_dict = deck_info.get('note_types', {})
                note_types_to_remove = []
                
                # Encontrar note types [MISSING A.]
                for note_type_id, note_type_name in note_types_dict.items():
                    # Formato: "Sheets2Anki - {remote_deck_name} - [MISSING A.] - {Basic|Cloze}"
                    missing_pattern_basic = f"Sheets2Anki - {deck_name} - [MISSING A.] - Basic"
                    missing_pattern_cloze = f"Sheets2Anki - {deck_name} - [MISSING A.] - Cloze"
                    
                    if note_type_name == missing_pattern_basic or note_type_name == missing_pattern_cloze:
                        note_types_to_remove.append(note_type_id)
                        print(f"   🗑️ META: Removendo referência do note type '[MISSING A.]': '{note_type_name}' (ID: {note_type_id})")
                
                # Remover os note types encontrados
                for note_type_id in note_types_to_remove:
                    if note_type_id in note_types_dict:
                        del note_types_dict[note_type_id]
                        updates_made = True
        
        # Salvar meta.json atualizado se houve mudanças
        if updates_made:
            save_meta(meta)
            print(f"✅ META UPDATE: meta.json atualizado após limpeza [MISSING A.]")
        else:
            print(f"ℹ️ META UPDATE: Nenhuma referência [MISSING A.] encontrada no meta.json")
            
    except Exception as e:
        print(f"❌ META UPDATE: Erro ao atualizar meta.json após limpeza [MISSING A.]: {e}")
        import traceback
        traceback.print_exc()


def get_disabled_students_for_cleanup(current_enabled: Set[str], previous_enabled: Set[str]) -> Set[str]:
    """
    Identifica alunos que foram removidos da lista de habilitados e precisam ter dados limpos.
    
    NOTA: [MISSING A.] não é considerado um "aluno" para propósitos de limpeza.
    Sua presença depende da configuração sync_missing_students_notes, não da lista de alunos habilitados.
    
    Args:
        current_enabled (Set[str]): Alunos atualmente habilitados
        previous_enabled (Set[str]): Alunos habilitados anteriormente
        
    Returns:
        Set[str]: Alunos que foram desabilitados e precisam ter dados removidos
    """
    # Remover [MISSING A.] da comparação, pois não é um "aluno real"
    current_real_students = {s for s in current_enabled if s != "[MISSING A.]"}
    previous_real_students = {s for s in previous_enabled if s != "[MISSING A.]"}
    
    disabled_students = previous_real_students - current_real_students
    
    if disabled_students:
        print(f"🔍 CLEANUP: Detectados alunos desabilitados: {sorted(disabled_students)}")
    else:
        print(f"✅ CLEANUP: Nenhum aluno foi desabilitado")
    
    print(f"🔍 CLEANUP: [MISSING A.] excluído da comparação (não é aluno real)")
    
    return disabled_students


def show_cleanup_confirmation_dialog(disabled_students: Set[str]) -> bool:
    """
    Mostra um diálogo de confirmação antes de remover dados de alunos desabilitados.
    
    Args:
        disabled_students (Set[str]): Conjunto de alunos que terão dados removidos
        
    Returns:
        bool: True se o usuário confirmou a remoção, False caso contrário
    """
    from .compat import QMessageBox, MessageBox_Warning, MessageBox_Yes, MessageBox_No
    
    if not disabled_students:
        return False
    
    students_list = '\n'.join([f"• {student}" for student in sorted(disabled_students)])
    
    message = (
        f"⚠️ ATENÇÃO: REMOÇÃO PERMANENTE DE DADOS ⚠️\n\n"
        f"Os seguintes alunos foram removidos da lista de sincronização:\n\n"
        f"{students_list}\n\n"
        f"🗑️ DADOS QUE SERÃO DELETADOS PERMANENTEMENTE:\n"
        f"• Todas as notas dos alunos\n"
        f"• Todos os cards dos alunos\n"
        f"• Todos os decks dos alunos\n"
        f"• Todos os note types dos alunos\n\n"
        f"❌ ESTA AÇÃO É IRREVERSÍVEL!\n\n"
        f"Deseja continuar com a remoção dos dados?"
    )
    
    # Criar MessageBox customizado
    msg_box = QMessageBox()
    msg_box.setIcon(MessageBox_Warning)
    msg_box.setWindowTitle("Confirmar Remoção Permanente de Dados")
    msg_box.setText(message)
    msg_box.setStandardButtons(MessageBox_Yes | MessageBox_No)
    msg_box.setDefaultButton(MessageBox_No)  # Default é NOT remover
    
    # Customizar botões
    yes_btn = msg_box.button(MessageBox_Yes)
    no_btn = msg_box.button(MessageBox_No)
    
    if yes_btn:
        yes_btn.setText("🗑️ SIM, DELETAR DADOS")
        yes_btn.setStyleSheet("QPushButton { background-color: #d73027; color: white; font-weight: bold; }")
    
    if no_btn:
        no_btn.setText("🛡️ NÃO, MANTER DADOS")
        no_btn.setStyleSheet("QPushButton { background-color: #4575b4; color: white; font-weight: bold; }")
    
    # Executar diálogo
    from .compat import safe_exec_dialog
    result = safe_exec_dialog(msg_box)
    
    confirmed = result == MessageBox_Yes
    
    if confirmed:
        print(f"⚠️ CLEANUP: Usuário confirmou remoção de dados de {len(disabled_students)} alunos")
    else:
        print(f"🛡️ CLEANUP: Usuário cancelou remoção de dados")
    
    return confirmed


def cleanup_missing_students_data(deck_names: List[str]) -> Dict[str, int]:
    """
    Remove todos os dados de notas "[MISSING A.]" quando a funcionalidade for desativada.
    
    Args:
        deck_names (List[str]): Lista de nomes de decks remotos para filtrar operações
        
    Returns:
        Dict[str, int]: Estatísticas de remoção {
            'notes_removed': int,
            'decks_removed': int, 
            'note_types_removed': int
        }
    """
    if not deck_names or not mw or not hasattr(mw, 'col') or not mw.col:
        return {'notes_removed': 0, 'decks_removed': 0, 'note_types_removed': 0}
    
    print(f"🗑️ CLEANUP: Iniciando limpeza de dados [MISSING A.] para decks: {deck_names}")
    
    stats = {'notes_removed': 0, 'decks_removed': 0, 'note_types_removed': 0}
    col = mw.col
    
    try:
        # Para cada deck remoto
        for deck_name in deck_names:
            print(f"🧹 CLEANUP: Processando deck '{deck_name}' para [MISSING A.]...")
            
            # Padrão: "Deck Remoto::[MISSING A.]::"
            missing_deck_pattern = f"{deck_name}::[MISSING A.]::"
            
            # Encontrar todos os decks que correspondem ao padrão [MISSING A.]
            missing_decks_found = []
            all_decks = col.decks.all()
            for deck in all_decks:
                deck_name = deck.get("name", "")
                deck_id = deck.get("id")
                if deck_name.startswith(missing_deck_pattern):
                    missing_decks_found.append((deck_id, deck_name))
                    print(f"  📁 Encontrado deck [MISSING A.]: {deck_name}")
            
            # Remover notas dos decks [MISSING A.]
            for deck_id, deck_name in missing_decks_found:
                try:
                    # Encontrar todas as notas neste deck
                    note_ids = col.find_notes(f'deck:"{deck_name}"')
                    
                    if note_ids:
                        print(f"  📝 Removendo {len(note_ids)} notas do deck '{deck_name}'...")
                        col.remove_notes(note_ids)
                        stats['notes_removed'] += len(note_ids)
                    
                    # Remover o deck vazio
                    print(f"  📁 Removendo deck '[MISSING A.]': {deck_name}")
                    col.decks.remove([deck_id])
                    stats['decks_removed'] += 1
                    
                except Exception as e:
                    print(f"  ❌ Erro ao processar deck '{deck_name}': {e}")
                    continue
            
            # Encontrar e remover note types específicos para [MISSING A.]
            # Padrão: "Sheets2Anki - {remote_deck_name} - [MISSING A.] - {Basic|Cloze}"
            try:
                note_types = col.models.all()
                for note_type in note_types:
                    note_type_name = note_type.get('name', '')
                    
                    # Verificar se é um note type do [MISSING A.] para este deck
                    missing_pattern = f"Sheets2Anki - {deck_name} - [MISSING A.] -"
                    
                    if note_type_name.startswith(missing_pattern):
                        print(f"  🏷️ Removendo note type '[MISSING A.]': {note_type_name}")
                        col.models.rem(note_type)
                        stats['note_types_removed'] += 1
                        
            except Exception as e:
                print(f"  ❌ Erro ao processar note types para deck '{deck_name}': {e}")
        
        # NOVO: Atualizar meta.json após limpeza para remover referências de note types [MISSING A.] deletados
        _update_meta_after_missing_cleanup(deck_names)
        
        print(f"✅ CLEANUP: Limpeza [MISSING A.] concluída - Estatísticas: {stats}")
        return stats
        
    except Exception as e:
        print(f"❌ CLEANUP: Erro durante limpeza [MISSING A.]: {e}")
        return stats


def show_missing_cleanup_confirmation_dialog() -> bool:
    """
    Mostra diálogo de confirmação para limpeza de dados [MISSING A.].
    
    Returns:
        bool: True se usuário confirmou a remoção
    """
    from .compat import QMessageBox, MessageBox_Yes, MessageBox_No
    
    msg_box = QMessageBox(mw)
    msg_box.setWindowTitle("⚠️ Confirmação de Remoção - Notas [MISSING A.]")
    msg_box.setIcon(QMessageBox.Icon.Warning)
    
    text = (
        f"🗑️ REMOÇÃO DE NOTAS SEM ALUNOS ESPECÍFICOS\n\n"
        f"Você desativou a sincronização de notas sem alunos específicos.\n\n"
        f"📋 O que será removido:\n"
        f"• Todas as notas em subdecks [MISSING A.]\n"
        f"• Todos os subdecks [MISSING A.] e seus conteúdos\n"
        f"• Note types específicos para [MISSING A.]\n\n"
        f"⚠️ ESTA AÇÃO É IRREVERSÍVEL!\n"
        f"Os dados removidos não podem ser recuperados.\n\n"
        f"Deseja continuar com a remoção?"
    )
    
    msg_box.setText(text)
    msg_box.setStandardButtons(MessageBox_Yes | MessageBox_No)
    msg_box.setDefaultButton(MessageBox_No)  # Botão seguro como padrão
    
    # Customizar botões
    yes_btn = msg_box.button(MessageBox_Yes)
    no_btn = msg_box.button(MessageBox_No)
    
    if yes_btn:
        yes_btn.setText("🗑️ SIM, DELETAR [MISSING A.]")
        yes_btn.setStyleSheet("QPushButton { background-color: #d73027; color: white; font-weight: bold; }")
    
    if no_btn:
        no_btn.setText("🛡️ NÃO, MANTER DADOS")
        no_btn.setStyleSheet("QPushButton { background-color: #4575b4; color: white; font-weight: bold; }")
    
    # Executar diálogo
    from .compat import safe_exec_dialog
    result = safe_exec_dialog(msg_box)
    
    confirmed = result == MessageBox_Yes
    
    if confirmed:
        print(f"⚠️ CLEANUP: Usuário confirmou remoção de dados [MISSING A.]")
    else:
        print(f"🛡️ CLEANUP: Usuário cancelou remoção de dados [MISSING A.]")
    
    return confirmed
