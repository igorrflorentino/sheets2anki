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
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

from . import templates_and_definitions as cols
from .compat import ButtonBox_Cancel
from .compat import ButtonBox_Ok
from .compat import DialogAccepted
from .compat import QCheckBox
from .compat import QDialog
from .compat import QDialogButtonBox
from .compat import QHBoxLayout
from .compat import QLabel
from .compat import QPushButton
from .compat import QScrollArea
from .compat import QTextEdit
from .compat import QVBoxLayout
from .compat import QWidget
from .compat import mw
from .compat import safe_exec_dialog
from .compat import showInfo
from .config_manager import get_enabled_students
from .config_manager import get_meta
from .config_manager import is_student_filter_active
from .config_manager import save_meta


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
    enabled_students_set = {
        student for student in enabled_students_raw if student and student.strip()
    }

    # Se não há alunos configurados, não sincronizar nenhum
    if not enabled_students_set:
        return set()

    # Interseção case-sensitive
    matched_students = all_students.intersection(enabled_students_set)

    print("🔍 SYNC: Filtro de alunos aplicado:")
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
        title_label.setStyleSheet(
            "font-weight: bold; font-size: 12px; margin-bottom: 10px;"
        )
        layout.addWidget(title_label)

        info_text = QTextEdit()
        info_text.setPlainText(
            "• Alunos selecionados terão suas notas sincronizadas em subdecks separados\n"
            "• Alunos desmarcados terão suas notas removidas dos decks locais\n"
            "• A estrutura será: Deck Raiz::Deck Remoto::Aluno::Importância::Tópico::Subtópico::Conceito\n"
            "• Cada aluno terá seu próprio Note Type personalizado"
        )
        info_text.setMaximumHeight(80)
        info_text.setStyleSheet(
            "background-color: #f0f0f0; border: 1px solid #ccc; padding: 5px;"
        )
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

    if not hasattr(remote_deck, "notes") or not remote_deck.notes:
        return students

    for note_data in remote_deck.notes:
        alunos_field = note_data.get(cols.ALUNOS, "").strip()

        if alunos_field:
            # Separar múltiplos alunos por vírgula
            alunos_list = [s.strip() for s in alunos_field.split(",") if s.strip()]
            for aluno in alunos_list:
                if aluno:
                    # Adicionar nome do estudante (case-sensitive)
                    students.add(aluno)

    return students


def get_selected_students_for_deck(deck_url: str) -> Set[str]:
    """
    Obtém os alunos selecionados para um deck específico.
    Se não houver seleção específica para o deck, usa a configuração global.
    
    IMPORTANTE: Inclui [MISSING A.] se a funcionalidade estiver ativada.

    Args:
        deck_url: URL do deck remoto

    Returns:
        Set[str]: Conjunto de alunos selecionados para este deck (incluindo [MISSING A.] se aplicável)
    """
    from .config_manager import get_deck_id
    from .config_manager import get_enabled_students
    from .config_manager import is_sync_missing_students_notes

    meta = get_meta()

    # Navegar pela estrutura: decks -> spreadsheet_id -> student_selection
    spreadsheet_id = get_deck_id(deck_url)
    deck_config = meta.get("decks", {}).get(spreadsheet_id, {})
    student_selection = deck_config.get("student_selection")

    # Se não há seleção específica para o deck, usar configuração global
    if student_selection is None:
        global_enabled = get_enabled_students()
        selected_students = set(global_enabled) if global_enabled else set()
    else:
        # Converter para set se for lista
        if isinstance(student_selection, list):
            selected_students = set(student_selection)
        else:
            selected_students = student_selection if isinstance(student_selection, set) else set()

    # NOVO: Incluir [MISSING A.] se a funcionalidade estiver ativada
    if is_sync_missing_students_notes():
        selected_students.add("[MISSING A.]")

    return selected_students


def save_selected_students_for_deck(deck_url: str, selected_students: Set[str]):
    """
    Salva a seleção de alunos para um deck específico.

    Args:
        deck_url: URL do deck remoto
        selected_students: Conjunto de alunos selecionados
    """
    from .config_manager import get_deck_id

    meta = get_meta()

    # Garantir estrutura do meta
    if "decks" not in meta:
        meta["decks"] = {}

    spreadsheet_id = get_deck_id(deck_url)
    if spreadsheet_id not in meta["decks"]:
        meta["decks"][spreadsheet_id] = {}

    # Converter set para lista para serialização JSON
    meta["decks"][spreadsheet_id]["student_selection"] = list(selected_students)

    save_meta(meta)


def show_student_selection_dialog(
    deck_url: str, available_students: Set[str]
) -> Optional[Set[str]]:
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
        list(available_students), deck_url, current_selection
    )

    if safe_exec_dialog(dialog) == DialogAccepted:
        selected = dialog.get_selected_students()
        save_selected_students_for_deck(deck_url, selected)
        return selected

    return None


def filter_questions_by_selected_students(
    questions: List[Dict], selected_students: Set[str]
) -> List[Dict]:
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

    print("🔍 FILTRO: Iniciando filtro de questões...")
    print(f"  • Total de questões: {len(questions)}")
    print(f"  • Alunos selecionados (norm): {sorted(selected_students)}")
    print(f"  • Incluir [MISSING A.]: {include_missing_students}")

    for i, question in enumerate(questions):
        fields = question.get("fields", {})
        alunos_field = fields.get(cols.ALUNOS, "").strip()

        if not alunos_field:
            # NOVO: Se funcionalidade [MISSING A.] estiver ativa, incluir nota
            if include_missing_students:
                filtered_questions.append(question)
                print(f"  📝 Questão {i+1}: SEM aluno → incluída ([MISSING A.] ativo)")
            else:
                print(
                    f"  ❌ Questão {i+1}: SEM aluno → ignorada ([MISSING A.] inativo)"
                )
            continue

        # Verificar se algum dos alunos selecionados está na lista de alunos da questão
        question_students = set()
        alunos_list = re.split(r"[,;|]", alunos_field)
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

    print(
        f"🎯 FILTRO: {len(filtered_questions)}/{len(questions)} questões selecionadas"
    )
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
    from .templates_and_definitions import DEFAULT_CONCEPT
    from .templates_and_definitions import DEFAULT_IMPORTANCE
    from .templates_and_definitions import DEFAULT_SUBTOPIC
    from .templates_and_definitions import DEFAULT_TOPIC

    # Obter valores dos campos, usando valores padrão se estiverem vazios
    importancia = fields.get(cols.IMPORTANCIA, "").strip() or DEFAULT_IMPORTANCE
    topico = fields.get(cols.TOPICO, "").strip() or DEFAULT_TOPIC
    subtopico = fields.get(cols.SUBTOPICO, "").strip() or DEFAULT_SUBTOPIC
    conceito = fields.get(cols.CONCEITO, "").strip() or DEFAULT_CONCEPT

    # Criar hierarquia completa incluindo o aluno
    return (
        f"{main_deck_name}::{student}::{importancia}::{topico}::{subtopico}::{conceito}"
    )


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
    from .templates_and_definitions import DEFAULT_CONCEPT
    from .templates_and_definitions import DEFAULT_IMPORTANCE
    from .templates_and_definitions import DEFAULT_SUBTOPIC
    from .templates_and_definitions import DEFAULT_TOPIC

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
    alunos_field = fields.get(cols.ALUNOS, "").strip()

    if alunos_field:
        alunos_list = re.split(r"[,;|]", alunos_field)
        for aluno in alunos_list:
            aluno = aluno.strip()
            if aluno:
                students.add(aluno)

    return students


def remove_notes_for_unselected_students(
    col,
    main_deck_name: str,
    selected_students: Set[str],
    all_students_in_sheet: Set[str],
) -> int:
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

    if not mw or not hasattr(mw, "col") or not mw.col:
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
        student_decks = [
            d for d in all_decks if d.name.startswith(student_deck_pattern)
        ]

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


def _convert_to_tsv_export_url(url: str) -> str:
    """
    Converte uma URL do Google Sheets para formato de export TSV.
    
    Args:
        url (str): URL original do Google Sheets
        
    Returns:
        str: URL formatada para export TSV
    """
    try:
        # Se já é uma URL de export TSV, retornar como está
        if "export?format=tsv" in url:
            print(f"✅ DEBUG TSV: URL já está em formato export: {url}")
            return url
        
        # Usar a função centralizada de conversão do utils.py
        from .utils import convert_edit_url_to_tsv
        
        try:
            tsv_url = convert_edit_url_to_tsv(url)
            print(f"🔄 DEBUG TSV: URL convertida para export: {tsv_url}")
            return tsv_url
        except ValueError as ve:
            print(f"⚠️ DEBUG TSV: Erro na conversão usando convert_edit_url_to_tsv: {ve}")
            # Fallback para método anterior se a URL não for uma URL de edição padrão
            return _fallback_url_conversion(url)
            
    except Exception as e:
        print(f"❌ DEBUG TSV: Erro ao converter URL: {e}")
        return url


def _fallback_url_conversion(url: str) -> str:
    """
    Método de fallback para conversão de URLs não-padrão.
    
    Args:
        url (str): URL original do Google Sheets
        
    Returns:
        str: URL formatada para export TSV ou URL original se falhar
    """
    try:
        import re
        
        # Padrões comuns de URLs do Google Sheets
        patterns = [
            r'/spreadsheets/d/([a-zA-Z0-9-_]+)',  # URL padrão
            r'[?&]id=([a-zA-Z0-9-_]+)',           # URL com parâmetro id
        ]
        
        sheet_id = None
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                sheet_id = match.group(1)
                break
        
        if sheet_id:
            # Construir URL de export TSV
            tsv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=tsv"
            print(f"🔄 DEBUG TSV: URL convertida via fallback: {tsv_url}")
            return tsv_url
        else:
            print(f"⚠️ DEBUG TSV: Não foi possível extrair ID da URL: {url}")
            return url
            
    except Exception as e:
        print(f"❌ DEBUG TSV: Erro no fallback de conversão: {e}")
        return url


def discover_students_from_tsv_url(url: str) -> Set[str]:
    """
    Descobre alunos únicos de uma URL de TSV do Google Sheets.

    Args:
        url (str): URL do TSV do Google Sheets

    Returns:
        Set[str]: Conjunto de nomes de alunos únicos encontrados
    """
    try:
        print(f"🔍 DEBUG TSV: Iniciando descoberta de alunos para URL: {url}")
        
        # Primeiro, validar e converter a URL usando a função centralizada
        from .utils import validate_url
        
        try:
            tsv_url = validate_url(url)
            print(f"✅ DEBUG TSV: URL validada e convertida: {tsv_url}")
        except ValueError as ve:
            print(f"❌ DEBUG TSV: Erro na validação da URL: {ve}")
            # Fallback para o método anterior se a validação falhar
            tsv_url = _convert_to_tsv_export_url(url)
            print(f"🔄 DEBUG TSV: Usando fallback, URL convertida: {tsv_url}")

        print(f"🌐 DEBUG TSV: Fazendo download de {tsv_url}")

        # Imports necessários
        try:
            import csv
            import urllib.request
            from io import StringIO
        except ImportError as e:
            print(f"❌ Erro ao importar módulos necessários: {e}")
            return set()

        # Fazer download dos dados TSV com headers apropriados
        headers = {
            "User-Agent": "Mozilla/5.0 (Sheets2Anki) AnkiAddon"
        }
        request = urllib.request.Request(tsv_url, headers=headers)
        
        with urllib.request.urlopen(request, timeout=30) as response:
            data = response.read().decode("utf-8")

        print(f"📄 DEBUG TSV: Downloaded {len(data)} characters")
        print(f"🔍 DEBUG TSV: First 200 chars: {repr(data[:200])}")

        # Parse CSV/TSV
        csv_reader = csv.DictReader(StringIO(data), delimiter="\t")

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
                    print(
                        f"👥 DEBUG TSV: Linha {row_count} - Alunos encontrados: '{alunos_str}'"
                    )
                    # Split por vírgula e limpar espaços
                    for aluno in alunos_str.split(","):
                        aluno = aluno.strip()
                        if aluno:
                            students.add(aluno)
                            print(f"✅ DEBUG TSV: Adicionado aluno: '{aluno}'")

        print(f"📊 DEBUG TSV: Processadas {row_count} linhas")
        print(f"🎓 DEBUG TSV: Total de estudantes únicos encontrados: {len(students)}")
        print(f"📝 DEBUG TSV: Lista final: {sorted(students)}")

        return students

    except urllib.error.HTTPError as http_err:
        if http_err.code == 400:
            print(f"❌ DEBUG TSV: Erro HTTP 400 - A planilha não está acessível publicamente")
            print(f"💡 SOLUÇÃO: Configurar compartilhamento público da planilha:")
            print(f"   1. Abra a planilha no Google Sheets")
            print(f"   2. Clique em 'Compartilhar'")
            print(f"   3. Mude o acesso para 'Qualquer pessoa com o link'")
            print(f"   4. Defina a permissão como 'Visualizador'")
        elif http_err.code == 404:
            print(f"❌ DEBUG TSV: Erro HTTP 404 - Planilha não encontrada")
            print(f"💡 VERIFICAR: URL da planilha está correta?")
        else:
            print(f"❌ DEBUG TSV: Erro HTTP {http_err.code}: {http_err.reason}")
        
        print(f"🔍 DEBUG TSV: Traceback HTTP Error:")
        import traceback
        traceback.print_exc()
        return set()
        
    except urllib.error.URLError as url_err:
        print(f"❌ DEBUG TSV: Erro de conectividade: {url_err.reason}")
        print(f"💡 VERIFICAR: Conexão com internet ativa?")
        print(f"🔍 DEBUG TSV: Traceback URL Error:")
        import traceback
        traceback.print_exc()
        return set()
        
    except Exception as e:
        print(f"❌ Erro ao descobrir alunos da URL {url}: {e}")
        import traceback

        print("🔍 DEBUG TSV: Traceback completo:")
        traceback.print_exc()
        return set()


def cleanup_disabled_students_data(
    disabled_students: Set[str], deck_names: List[str]
) -> Dict[str, int]:
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
    if not disabled_students or not mw or not hasattr(mw, "col") or not mw.col:
        return {"notes_removed": 0, "decks_removed": 0, "note_types_removed": 0}

    print(
        f"🗑️ CLEANUP: Iniciando limpeza de dados para alunos: {sorted(disabled_students)}"
    )

    stats = {"notes_removed": 0, "decks_removed": 0, "note_types_removed": 0}
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
            all_note_ids = col.find_notes("*")  # Todas as notas - usar wildcard
            student_note_ids = []

            for note_id in all_note_ids:
                try:
                    note = col.get_note(note_id)
                    # Verificar se a nota tem o campo ID e se corresponde ao aluno
                    if "ID" in note.keys():
                        note_unique_id = note["ID"].strip()
                        # Verificar se o ID da nota começa com "{student}_"
                        if note_unique_id.startswith(f"{student}_"):
                            student_note_ids.append(note_id)
                            print(
                                f"   � Encontrada nota do aluno '{student}': {note_unique_id}"
                            )
                except:
                    continue

            notes_to_remove.extend(student_note_ids)
            print(
                f"   📊 Total de notas encontradas para '{student}': {len(student_note_ids)}"
            )

        # 2. Remover todas as notas encontradas
        if notes_to_remove:
            print(f"🗑️ CLEANUP: Removendo {len(notes_to_remove)} notas...")
            col.remove_notes(notes_to_remove)
            stats["notes_removed"] = len(notes_to_remove)
            print(f"✅ CLEANUP: {len(notes_to_remove)} notas removidas")

        # 3. Encontrar e remover decks vazios dos alunos desabilitados
        for student in disabled_students:
            for deck_name in deck_names:
                # Padrão de deck do aluno: "Sheets2Anki::{deck_name}::{student}::"
                student_deck_pattern = f"Sheets2Anki::{deck_name}::{student}::"

                # Encontrar todos os decks que começam com este padrão
                all_decks = col.decks.all_names_and_ids()
                matching_decks = [
                    d for d in all_decks if d.name.startswith(student_deck_pattern)
                ]

                for deck in matching_decks:
                    try:
                        # Verificar se o deck está vazio
                        remaining_notes = col.find_notes(f'deck:"{deck.name}"')
                        if not remaining_notes:
                            # Deck vazio, pode remover
                            from anki.decks import DeckId

                            deck_id = DeckId(deck.id)
                            col.decks.remove([deck_id])
                            stats["decks_removed"] += 1
                            print(f"   🗑️ Deck vazio removido: '{deck.name}'")
                        else:
                            print(
                                f"   📁 Deck '{deck.name}' ainda tem {len(remaining_notes)} notas, mantendo"
                            )
                    except Exception as e:
                        print(f"   ❌ Erro ao processar deck '{deck.name}': {e}")
                        continue

            # Remover note types do aluno
            removed_note_types = _remove_student_note_types(student, deck_names)
            stats["note_types_removed"] += removed_note_types

        # NOVO: Atualizar meta.json após limpeza para remover referências de note types deletados
        _update_meta_after_cleanup(disabled_students, deck_names)
        
        # NOVO: Remover alunos do histórico de sincronização após limpeza bem-sucedida
        from .config_manager import remove_student_from_sync_history
        for student in disabled_students:
            remove_student_from_sync_history(student)
        print(f"📝 CLEANUP: {len(disabled_students)} alunos removidos do histórico de sincronização")

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
    
    VERSÃO CORRIGIDA COM DEBUG MELHORADO:
    - Verifica todos os note types no Anki, não apenas os baseados em deck_names
    - Remove note types órfãos que podem existir por configurações antigas
    - Detecta padrões variados de nomenclatura
    - Adiciona logs detalhados para debug
    - Usa sistema de logging adequado do addon

    Args:
        student (str): Nome do aluno
        deck_names (List[str]): Lista de nomes de decks remotos (usado como filtro preferencial)

    Returns:
        int: Número de note types removidos
    """
    # Usar logging adequado quando possível
    try:
        from .utils import add_debug_message
        log_func = lambda msg: add_debug_message(msg, "CLEANUP_NOTE_TYPES")
    except:
        log_func = print
    
    if not mw or not hasattr(mw, "col") or not mw.col:
        log_func(f"❌ Anki não disponível para remover note types do aluno '{student}'")
        return 0

    col = mw.col
    removed_count = 0

    try:
        # Obter todos os note types
        note_types = col.models.all()
        log_func(f"🔍 Verificando {len(note_types)} note types para aluno '{student}'")

        student_note_types_found = []
        
        for note_type in note_types:
            note_type_name = note_type.get("name", "")
            note_type_id = note_type.get("id")

            if not note_type_id:
                continue

            should_remove = False
            match_reason = ""

            # MÉTODO 1: Verificar padrões baseados nos deck_names fornecidos
            for deck_name in deck_names:
                student_pattern_basic = f"Sheets2Anki - {deck_name} - {student} - Basic"
                student_pattern_cloze = f"Sheets2Anki - {deck_name} - {student} - Cloze"

                if note_type_name == student_pattern_basic or note_type_name == student_pattern_cloze:
                    should_remove = True
                    match_reason = f"deck pattern for '{student}'"
                    break

            # MÉTODO 2: Verificar padrão geral para note types órfãos (fallback robusto)
            if not should_remove and note_type_name.startswith("Sheets2Anki - "):
                # Formato geral: "Sheets2Anki - {qualquer_deck} - {student} - {Basic|Cloze}"
                parts = note_type_name.split(" - ")
                if len(parts) >= 4:
                    # O aluno está na terceira parte (índice 2)
                    note_student = parts[2]
                    note_type_suffix = parts[-1]  # Basic ou Cloze
                    
                    if (note_student == student and 
                        note_type_suffix in ["Basic", "Cloze"]):
                        should_remove = True
                        match_reason = f"orphaned note type for student '{student}'"

            if should_remove:
                student_note_types_found.append((note_type_name, note_type_id, match_reason))

        log_func(f"🎯 Encontrados {len(student_note_types_found)} note types para aluno '{student}':")
        for nt_name, nt_id, reason in student_note_types_found:
            log_func(f"   • '{nt_name}' (ID: {nt_id}) - {reason}")

        # Tentar remover os note types encontrados
        for note_type_name, note_type_id, match_reason in student_note_types_found:
            try:
                # Verificar se o note type está em uso com abordagem defensiva
                from anki.models import NotetypeId
                use_count = 0
                
                try:
                    # Método 1: Tentar com NotetypeId
                    use_count = col.models.useCount(NotetypeId(note_type_id))
                except (TypeError, AttributeError) as e:
                    log_func(f"⚠️ Método NotetypeId falhou para {note_type_id}: {e}")
                    try:
                        # Método 2: Tentar com int diretamente (versões antigas)
                        use_count = col.models.useCount(note_type_id)
                    except Exception as e2:
                        log_func(f"⚠️ Método int também falhou para {note_type_id}: {e2}")
                        try:
                            # Método 3: Buscar notas que usam este note type manualmente
                            note_ids = col.find_notes(f"mid:{note_type_id}")
                            use_count = len(note_ids)
                            log_func(f"ℹ️ Usando busca manual: {use_count} notas encontradas para note type {note_type_id}")
                        except Exception as e3:
                            log_func(f"❌ Todos os métodos falharam para {note_type_id}: {e3}")
                            # Se não conseguimos verificar, assumimos que está em uso para segurança
                            use_count = 1
                
                if use_count > 0:
                    log_func(f"⚠️ Note type '{note_type_name}' ainda tem {use_count} notas, pulando remoção")
                    continue

                # Note type não está em uso, pode remover
                log_func(f"🗑️ REMOVENDO note type '{note_type_name}' (ID: {note_type_id})...")
                
                try:
                    # Tentar remoção com NotetypeId
                    col.models.remove(NotetypeId(note_type_id))
                except (TypeError, AttributeError) as e:
                    log_func(f"⚠️ Remoção com NotetypeId falhou: {e}")
                    try:
                        # Fallback: tentar com int diretamente
                        col.models.remove(note_type_id)
                    except Exception as e2:
                        log_func(f"❌ Remoção falhou completamente: {e2}")
                        continue
                
                removed_count += 1
                log_func(f"✅ Note type '{note_type_name}' removido com sucesso")

            except Exception as e:
                log_func(f"❌ Erro ao remover note type '{note_type_name}': {e}")
                import traceback
                traceback.print_exc()
                continue

        if removed_count == 0 and len(student_note_types_found) > 0:
            log_func(f"⚠️ ATENÇÃO: {len(student_note_types_found)} note types encontrados mas nenhum foi removido")
        elif removed_count > 0:
            log_func(f"✅ SUCESSO: {removed_count} note types removidos para aluno '{student}'")
        else:
            log_func(f"ℹ️ Nenhum note type encontrado para aluno '{student}'")

        return removed_count

    except Exception as e:
        log_func(f"❌ Erro ao remover note types do aluno '{student}': {e}")
        import traceback
        traceback.print_exc()
        return 0


def _update_meta_after_cleanup(
    disabled_students: Set[str], deck_names: List[str]
) -> None:
    """
    Atualiza o meta.json removendo referências de note types que foram deletados durante cleanup.

    Args:
        disabled_students (Set[str]): Conjunto de alunos que foram desabilitados
        deck_names (List[str]): Lista de nomes de decks remotos
    """
    # Usar logging adequado quando possível
    try:
        from .utils import add_debug_message
        log_func = lambda msg: add_debug_message(msg, "CLEANUP_META")
    except:
        log_func = print
        
    try:
        from .config_manager import get_meta
        from .config_manager import save_meta

        log_func(
            f"📝 META UPDATE: Atualizando meta.json após limpeza de {len(disabled_students)} alunos"
        )

        meta = get_meta()
        updates_made = False

        # Para cada deck configurado
        for deck_info in meta.get("decks", {}).values():
            deck_name = deck_info.get("remote_deck_name", "")
            if deck_name in deck_names:
                note_types_dict = deck_info.get("note_types", {})
                note_types_to_remove = []

                # Encontrar note types dos alunos desabilitados
                for note_type_id, note_type_name in note_types_dict.items():
                    for student in disabled_students:
                        # Formato: "Sheets2Anki - {remote_deck_name} - {student} - {Basic|Cloze}"
                        student_pattern_basic = (
                            f"Sheets2Anki - {deck_name} - {student} - Basic"
                        )
                        student_pattern_cloze = (
                            f"Sheets2Anki - {deck_name} - {student} - Cloze"
                        )

                        if (
                            note_type_name == student_pattern_basic
                            or note_type_name == student_pattern_cloze
                        ):
                            note_types_to_remove.append(note_type_id)
                            log_func(
                                f"🗑️ META: Removendo referência do note type '{note_type_name}' (ID: {note_type_id})"
                            )

                # Remover os note types encontrados
                for note_type_id in note_types_to_remove:
                    if note_type_id in note_types_dict:
                        del note_types_dict[note_type_id]
                        updates_made = True

        # Salvar meta.json atualizado se houve mudanças
        if updates_made:
            save_meta(meta)
            log_func(
                f"✅ META UPDATE: meta.json atualizado com {len([nt for deck in meta.get('decks', {}).values() for nt in deck.get('note_types', {}).keys()])} note types restantes"
            )
        else:
            log_func("ℹ️ META UPDATE: Nenhuma atualização necessária no meta.json")

    except Exception as e:
        log_func(f"❌ META UPDATE: Erro ao atualizar meta.json após cleanup: {e}")
        import traceback

        traceback.print_exc()


def _update_meta_after_missing_cleanup(deck_names: List[str]) -> None:
    """
    Atualiza o meta.json removendo referências de note types [MISSING A.] que foram deletados.

    Args:
        deck_names (List[str]): Lista de nomes de decks remotos
    """
    # Usar logging adequado quando possível
    try:
        from .utils import add_debug_message
        log_func = lambda msg: add_debug_message(msg, "CLEANUP_MISSING_META")
    except:
        log_func = print
        
    try:
        from .config_manager import get_meta
        from .config_manager import save_meta

        log_func(
            f"📝 META UPDATE: Atualizando meta.json após limpeza [MISSING A.] para {len(deck_names)} decks"
        )

        meta = get_meta()
        updates_made = False

        # Para cada deck configurado
        for deck_info in meta.get("decks", {}).values():
            deck_name = deck_info.get("remote_deck_name", "")
            if deck_name in deck_names:
                note_types_dict = deck_info.get("note_types", {})
                note_types_to_remove = []

                # Encontrar note types [MISSING A.]
                for note_type_id, note_type_name in note_types_dict.items():
                    # Formato: "Sheets2Anki - {remote_deck_name} - [MISSING A.] - {Basic|Cloze}"
                    missing_pattern_basic = (
                        f"Sheets2Anki - {deck_name} - [MISSING A.] - Basic"
                    )
                    missing_pattern_cloze = (
                        f"Sheets2Anki - {deck_name} - [MISSING A.] - Cloze"
                    )

                    if (
                        note_type_name == missing_pattern_basic
                        or note_type_name == missing_pattern_cloze
                    ):
                        note_types_to_remove.append(note_type_id)
                        log_func(
                            f"🗑️ META: Removendo referência do note type '[MISSING A.]': '{note_type_name}' (ID: {note_type_id})"
                        )

                # Remover os note types encontrados
                for note_type_id in note_types_to_remove:
                    if note_type_id in note_types_dict:
                        del note_types_dict[note_type_id]
                        updates_made = True

        # Salvar meta.json atualizado se houve mudanças
        if updates_made:
            save_meta(meta)
            log_func("✅ META UPDATE: meta.json atualizado após limpeza [MISSING A.]")
        else:
            log_func(
                "ℹ️ META UPDATE: Nenhuma referência [MISSING A.] encontrada no meta.json"
            )

    except Exception as e:
        log_func(
            f"❌ META UPDATE: Erro ao atualizar meta.json após limpeza [MISSING A.]: {e}"
        )
        import traceback

        traceback.print_exc()


def get_disabled_students_for_cleanup(
    current_enabled: Set[str], previous_enabled: Set[str]
) -> Set[str]:
    """
    Identifica alunos que foram removidos da lista de habilitados e precisam ter dados limpos.
    
    VERSÃO CORRIGIDA PARA LÓGICA ADEQUADA:
    - Considera apenas alunos que foram SINCRONIZADOS pelo menos uma vez
    - Um aluno só pode ter dados para limpeza se já teve dados criados anteriormente
    - Alunos que estão em available_students mas nunca foram sincronizados NÃO devem ser limpos
    - Detecta note types existentes no Anki como fonte secundária
    
    NOTA: [MISSING A.] não é considerado um "aluno" para propósitos de limpeza.
    Sua presença depende da configuração sync_missing_students_notes, não da lista de alunos habilitados.

    Args:
        current_enabled (Set[str]): Alunos atualmente habilitados
        previous_enabled (Set[str]): Alunos habilitados anteriormente (pode ser usado como fonte adicional)

    Returns:
        Set[str]: Alunos que foram desabilitados e precisam ter dados removidos
    """
    # Usar logging adequado quando possível
    try:
        from .utils import add_debug_message
        log_func = lambda msg: add_debug_message(msg, "CLEANUP")
    except:
        log_func = print
    
    log_func("🔍 CLEANUP: Identificando alunos desabilitados para limpeza...")
    
    # FONTE PRINCIPAL: Apenas alunos que foram sincronizados pelo menos uma vez
    from .config_manager import get_students_with_sync_history
    historically_synced_students = get_students_with_sync_history()
    log_func(f"📚 Alunos que já foram sincronizados: {sorted(historically_synced_students)}")
    
    # FONTE ADICIONAL: Note types existentes no Anki (para casos de inconsistência)
    anki_detected_students = set()
    if hasattr(mw, "col") and mw.col:
        try:
            note_types = mw.col.models.all()
            for note_type in note_types:
                note_type_name = note_type.get("name", "")
                # Formato: "Sheets2Anki - {remote_deck_name} - {student} - {Basic|Cloze}"
                if note_type_name.startswith("Sheets2Anki - ") and " - " in note_type_name:
                    parts = note_type_name.split(" - ")
                    if len(parts) >= 4:
                        # O aluno está na terceira parte (índice 2)
                        student_name = parts[2]
                        if student_name and student_name != "[MISSING A.]":
                            anki_detected_students.add(student_name)
            
            log_func(f"🔍 Alunos encontrados no Anki via note types: {sorted(anki_detected_students)}")
            log_func(f"🔍 Alunos encontrados no Anki via note types: {sorted(anki_detected_students)}")
        except Exception as e:
            log_func(f"⚠️ Erro ao verificar note types no Anki: {e}")
    
    # COMBINAR: Alunos que tiveram dados criados (sync_history + note types existentes)
    students_with_created_data = historically_synced_students.union(anki_detected_students)
    
    # INCLUIR available_students apenas se também estão no histórico ou têm note types
    from .config_manager import get_global_student_config
    config = get_global_student_config()
    available_students = set(config.get("available_students", []))
    
    # Alunos em available_students que também têm evidência de sincronização
    available_and_synced = available_students.intersection(students_with_created_data)
    
    # Combinar todas as fontes de alunos que tiveram dados criados
    all_students_with_data = students_with_created_data.union(available_and_synced)
    
    log_func(f"📊 Relatório de fontes:")
    log_func(f"   • Histórico de sincronização: {sorted(historically_synced_students)}")
    log_func(f"   • Note types no Anki: {sorted(anki_detected_students)}")
    log_func(f"   • Available students: {sorted(available_students)}")
    log_func(f"   • Available + com dados: {sorted(available_and_synced)}")
    log_func(f"   • TOTAL com dados criados: {sorted(all_students_with_data)}")
    
    # Remover [MISSING A.] da comparação, pois não é um "aluno real"
    current_real_students = {s for s in current_enabled if s != "[MISSING A.]"}
    students_with_data_real = {s for s in all_students_with_data if s != "[MISSING A.]"}

    log_func(f"✅ Alunos reais atualmente habilitados: {sorted(current_real_students)}")
    log_func(f"📖 Alunos reais com dados criados: {sorted(students_with_data_real)}")

    # DETECÇÃO PRINCIPAL: Alunos que tinham dados mas não estão mais habilitados
    disabled_students = students_with_data_real - current_real_students

    if disabled_students:
        log_func(f"🎯 CLEANUP: Detectados alunos para limpeza: {sorted(disabled_students)}")
        log_func(f"   • Atualmente habilitados: {sorted(current_real_students)}")
        log_func(f"   • Com dados criados: {sorted(students_with_data_real)}")
        log_func(f"   • Alunos a remover: {sorted(disabled_students)}")
    else:
        log_func("✅ CLEANUP: Nenhum aluno foi desabilitado")

    log_func("🔍 CLEANUP: [MISSING A.] excluído da comparação (não é aluno real)")

    return disabled_students
def show_cleanup_confirmation_dialog(disabled_students: Set[str]) -> bool:
    """
    Mostra um diálogo de confirmação antes de remover dados de alunos desabilitados.
    
    REFATORADO: Agora usa função centralizada para garantir consistência.

    Args:
        disabled_students (Set[str]): Conjunto de alunos que terão dados removidos

    Returns:
        bool: True se o usuário confirmou a remoção, False caso contrário
    """
    from .data_removal_confirmation import confirm_students_removal

    if not disabled_students:
        return False

    # Converter set para list e usar função centralizada
    disabled_students_list = list(disabled_students)
    
    # Usar função centralizada para confirmar remoção
    confirmed = confirm_students_removal(
        disabled_students=disabled_students_list,
        missing_functionality_disabled=False,  # Apenas alunos, sem [MISSING A.]
        window_title="Confirmar Remoção Permanente de Dados"
    )

    if confirmed:
        print(
            f"⚠️ CLEANUP: Usuário confirmou remoção de dados de {len(disabled_students)} alunos"
        )
    else:
        print("🛡️ CLEANUP: Usuário cancelou remoção de dados")

    return confirmed


def cleanup_missing_students_data(deck_names: List[str]) -> Dict[str, int]:
    """
    Remove todos os dados de notas "[MISSING A.]" quando a funcionalidade for desativada.
    
    VERSÃO CORRIGIDA:
    - Detecta note types [MISSING A.] usando múltiplos padrões
    - Busca por note types órfãos mesmo que o deck_name não corresponda exatamente
    - Remove dados de forma mais robusta

    Args:
        deck_names (List[str]): Lista de nomes de decks remotos para filtrar operações

    Returns:
        Dict[str, int]: Estatísticas de remoção {
            'notes_removed': int,
            'decks_removed': int,
            'note_types_removed': int
        }
    """
    if not mw or not hasattr(mw, "col") or not mw.col:
        return {"notes_removed": 0, "decks_removed": 0, "note_types_removed": 0}

    print(
        f"🗑️ CLEANUP: Iniciando limpeza de dados [MISSING A.] para decks: {deck_names}"
    )

    stats = {"notes_removed": 0, "decks_removed": 0, "note_types_removed": 0}
    col = mw.col

    try:
        # 1. Buscar e remover todas as notas com ID [MISSING A.]_{qualquer_id}
        all_note_ids = col.find_notes("*")
        missing_note_ids = []

        for note_id in all_note_ids:
            try:
                note = col.get_note(note_id)
                if "ID" in note.keys():
                    note_unique_id = note["ID"].strip()
                    if note_unique_id.startswith("[MISSING A.]_"):
                        missing_note_ids.append(note_id)
                        print(f"   📝 Encontrada nota [MISSING A.]: {note_unique_id}")
            except:
                continue

        # Remover todas as notas [MISSING A.] encontradas
        if missing_note_ids:
            print(f"🗑️ CLEANUP: Removendo {len(missing_note_ids)} notas [MISSING A.]...")
            col.remove_notes(missing_note_ids)
            stats["notes_removed"] = len(missing_note_ids)

        # 2. Remover decks [MISSING A.] (usando múltiplos padrões)
        all_decks = col.decks.all_names_and_ids()
        
        # Padrões a procurar:
        # - "Sheets2Anki::{deck_name}::[MISSING A.]::"
        # - Qualquer deck que contenha "::[MISSING A.]::"
        missing_decks_found = []
        
        for deck in all_decks:
            deck_name = deck.name
            
            # Verificar se é um deck [MISSING A.]
            if "::[MISSING A.]::" in deck_name:
                # Verificar se corresponde a algum dos decks especificados (se fornecidos)
                if deck_names:
                    deck_matches = False
                    for remote_deck_name in deck_names:
                        expected_pattern = f"Sheets2Anki::{remote_deck_name}::[MISSING A.]::"
                        if deck_name.startswith(expected_pattern):
                            deck_matches = True
                            break
                    
                    if deck_matches:
                        missing_decks_found.append(deck)
                        print(f"   📁 Deck [MISSING A.] encontrado: {deck_name}")
                else:
                    # Se não há deck_names especificados, remover qualquer deck [MISSING A.]
                    missing_decks_found.append(deck)
                    print(f"   📁 Deck [MISSING A.] genérico encontrado: {deck_name}")

        # Remover decks [MISSING A.] vazios
        for deck in missing_decks_found:
            try:
                remaining_notes = col.find_notes(f'deck:"{deck.name}"')
                if not remaining_notes:
                    from anki.decks import DeckId
                    col.decks.remove([DeckId(deck.id)])
                    stats["decks_removed"] += 1
                    print(f"   🗑️ Deck [MISSING A.] vazio removido: '{deck.name}'")
                else:
                    print(f"   � Deck [MISSING A.] '{deck.name}' ainda tem {len(remaining_notes)} notas, mantendo")
            except Exception as e:
                print(f"   ❌ Erro ao processar deck [MISSING A.] '{deck.name}': {e}")

        # 3. Remover note types [MISSING A.] (usando detecção robusta)
        note_types = col.models.all()
        
        for note_type in note_types:
            note_type_name = note_type.get("name", "")
            note_type_id = note_type.get("id")
            
            if not note_type_id:
                continue
            
            should_remove = False
            
            # MÉTODO 1: Verificar padrões baseados nos deck_names fornecidos
            if deck_names:
                for deck_name in deck_names:
                    missing_pattern_basic = f"Sheets2Anki - {deck_name} - [MISSING A.] - Basic"
                    missing_pattern_cloze = f"Sheets2Anki - {deck_name} - [MISSING A.] - Cloze"
                    
                    if note_type_name == missing_pattern_basic or note_type_name == missing_pattern_cloze:
                        should_remove = True
                        print(f"   🎯 Note type [MISSING A.] '{note_type_name}' matched deck pattern")
                        break
            
            # MÉTODO 2: Verificar padrão geral para note types [MISSING A.] órfãos
            if not should_remove and note_type_name.startswith("Sheets2Anki - "):
                parts = note_type_name.split(" - ")
                if len(parts) >= 4:
                    note_student = parts[2]
                    note_type_suffix = parts[-1]
                    
                    if (note_student == "[MISSING A.]" and 
                        note_type_suffix in ["Basic", "Cloze"]):
                        should_remove = True
                        try:
                            from .utils import add_debug_message
                            add_debug_message(f"🔍 Note type [MISSING A.] órfão '{note_type_name}' found", "CLEANUP_MISSING")
                        except:
                            print(f"   🔍 Note type [MISSING A.] órfão '{note_type_name}' found")
            
            if should_remove:
                try:
                    # Verificar se o note type está em uso com abordagem defensiva
                    from anki.models import NotetypeId
                    use_count = 0
                    
                    try:
                        # Método 1: Tentar com NotetypeId
                        use_count = col.models.useCount(NotetypeId(note_type_id))
                    except (TypeError, AttributeError) as e:
                        try:
                            from .utils import add_debug_message
                            add_debug_message(f"⚠️ Método NotetypeId falhou para [MISSING A.] {note_type_id}: {e}", "CLEANUP_MISSING")
                        except:
                            print(f"   ⚠️ Método NotetypeId falhou para [MISSING A.] {note_type_id}: {e}")
                        try:
                            # Método 2: Tentar com int diretamente
                            use_count = col.models.useCount(note_type_id)
                        except Exception as e2:
                            try:
                                # Método 3: Buscar notas manualmente
                                note_ids = col.find_notes(f"mid:{note_type_id}")
                                use_count = len(note_ids)
                                try:
                                    from .utils import add_debug_message
                                    add_debug_message(f"ℹ️ Usando busca manual para [MISSING A.]: {use_count} notas", "CLEANUP_MISSING")
                                except:
                                    print(f"   ℹ️ Usando busca manual para [MISSING A.]: {use_count} notas")
                            except Exception as e3:
                                # Se falhar tudo, assumir que está em uso por segurança
                                use_count = 1
                    
                    if use_count > 0:
                        try:
                            from .utils import add_debug_message
                            add_debug_message(f"⚠️ Note type [MISSING A.] '{note_type_name}' ainda tem {use_count} notas, pulando", "CLEANUP_MISSING")
                        except:
                            print(f"   ⚠️ Note type [MISSING A.] '{note_type_name}' ainda tem {use_count} notas, pulando")
                        continue
                    
                    # Note type não está em uso, pode remover
                    try:
                        # Tentar remoção com NotetypeId
                        col.models.remove(NotetypeId(note_type_id))
                    except (TypeError, AttributeError) as e:
                        try:
                            from .utils import add_debug_message
                            add_debug_message(f"⚠️ Remoção com NotetypeId falhou para [MISSING A.]: {e}", "CLEANUP_MISSING")
                        except:
                            print(f"   ⚠️ Remoção com NotetypeId falhou para [MISSING A.]: {e}")
                        try:
                            # Fallback: tentar com int diretamente
                            col.models.remove(note_type_id)
                        except Exception as e2:
                            try:
                                from .utils import add_debug_message
                                add_debug_message(f"❌ Remoção falhou completamente para [MISSING A.]: {e2}", "CLEANUP_MISSING")
                            except:
                                print(f"   ❌ Remoção falhou completamente para [MISSING A.]: {e2}")
                            continue
                    
                    stats["note_types_removed"] += 1
                    try:
                        from .utils import add_debug_message
                        add_debug_message(f"🗑️ Note type [MISSING A.] '{note_type_name}' removido", "CLEANUP_MISSING")
                    except:
                        print(f"   🗑️ Note type [MISSING A.] '{note_type_name}' removido")
                    
                except Exception as e:
                    try:
                        from .utils import add_debug_message
                        add_debug_message(f"❌ Erro ao remover note type [MISSING A.] '{note_type_name}': {e}", "CLEANUP_MISSING")
                    except:
                        print(f"   ❌ Erro ao remover note type [MISSING A.] '{note_type_name}': {e}")

        # NOVO: Atualizar meta.json após limpeza
        _update_meta_after_missing_cleanup(deck_names)

        # Salvar mudanças
        col.save()

        print(f"✅ CLEANUP: Limpeza [MISSING A.] concluída - Estatísticas: {stats}")
        return stats

    except Exception as e:
        print(f"❌ CLEANUP: Erro durante limpeza [MISSING A.]: {e}")
        import traceback
        traceback.print_exc()
        return stats


def show_missing_cleanup_confirmation_dialog() -> bool:
    """
    Mostra diálogo de confirmação para limpeza de dados [MISSING A.].
    REFATORADO: Usa módulo centralizado para geração de mensagens e confirmação.

    Returns:
        bool: True se usuário confirmou a remoção
    """
    from .data_removal_confirmation import show_data_removal_confirmation_dialog
    
    # Usar diálogo centralizado apenas para [MISSING A.]
    confirmed = show_data_removal_confirmation_dialog(
        students_to_remove=["[MISSING A.]"],
        window_title="⚠️ Confirmação de Remoção - Notas [MISSING A.]"
    )
    
    if confirmed:
        print("⚠️ CLEANUP: Usuário confirmou remoção de dados [MISSING A.]")
    else:
        print("🛡️ CLEANUP: Usuário cancelou remoção de dados [MISSING A.]")

    return confirmed
