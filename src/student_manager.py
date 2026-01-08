"""
Student selection management for the Sheets2Anki addon.

This module implements functionalities to allow the user to select
which students they want to synchronize and manage the subdeck structure by student.

Main features:
- Extraction of unique students from spreadsheets
- Interface for student selection
- Filtering of notes by selected students
- Creation of hierarchical subdecks by student
- Removal of notes for unselected students
"""

import re
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

from .templates_and_definitions import DEFAULT_STUDENT
from . import templates_and_definitions as cols
from .compat import ButtonBox_Cancel
from .compat import ButtonBox_Ok
from .compat import DialogAccepted
from .compat import MessageBox_Yes, MessageBox_No, MessageBox_Cancel
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
from .styled_messages import StyledMessageBox
from .config_manager import get_enabled_students
from .config_manager import get_meta
from .config_manager import is_student_filter_active
from .config_manager import save_meta
from .utils import add_debug_message


def add_debug_msg(message, category="STUDENT_MANAGER"):
    """Local helper for debug messages."""
    add_debug_message(message, category)


def get_students_to_sync(all_students: Set[str]) -> Set[str]:
    """
    Gets the students that should be synchronized based on the global configuration.
    NEW VERSION: Uses consistent name normalization.

    Args:
        all_students (Set[str]): All students found in the spreadsheet (already normalized)

    Returns:
        Set[str]: Students that should be synchronized (normalized names)
    """
    # Check if the filter is active (based on the list of enabled students)
    if not is_student_filter_active():
        # Filter inactive - sync all (already normalized)
        return all_students

    # Get globally enabled students (case-sensitive)
    enabled_students_raw = get_enabled_students()
    enabled_students_set = {
        student for student in enabled_students_raw if student and student.strip()
    }

    # If no students are configured, sync none
    if not enabled_students_set:
        return set()

    # Case-sensitive intersection
    matched_students = all_students.intersection(enabled_students_set)

    add_debug_msg("🔍 SYNC: Student filter applied:")
    add_debug_msg(f"  • Students in spreadsheet: {sorted(all_students)}")
    add_debug_msg(f"  • Enabled students: {sorted(enabled_students_set)}")
    add_debug_msg(f"  • Students for sync: {sorted(matched_students)}")

    return matched_students


class StudentSelectionDialog(QDialog):
    """
    Dialog for selecting the students the user wants to synchronize.
    """

    def __init__(self, students: List[str], deck_url: str, current_selection: Set[str]):
        super().__init__()
        self.students = sorted(students)  # Alphabetical order
        self.deck_url = deck_url
        self.current_selection = current_selection.copy()
        self.checkboxes = {}

        self.setWindowTitle("Student Selection - Sheets2Anki")
        self.setMinimumSize(500, 400)
        self.resize(600, 500)

        self._setup_ui()

    def _setup_ui(self):
        """Configures the user interface."""
        layout = QVBoxLayout()

        # Title and explanation
        title_label = QLabel("Select the students you want to synchronize:")
        title_label.setStyleSheet(
            "font-weight: bold; font-size: 12px; margin-bottom: 10px;"
        )
        layout.addWidget(title_label)

        info_text = QTextEdit()
        info_text.setPlainText(
            "• Selected students will have their notes synchronized into separate subdecks\n"
            "• Unselected students will have their notes removed from local decks\n"
            "• The structure will be: Root Deck::Remote Deck::Student::Importance::Topic::Subtopic::Concept\n"
            "• Each student will have their own custom Note Type"
        )
        info_text.setMaximumHeight(80)
        info_text.setStyleSheet(
            "background-color: #f0f0f0; border: 1px solid #ccc; padding: 5px;"
        )
        layout.addWidget(info_text)

        # Quick select buttons
        quick_select_layout = QHBoxLayout()
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self._select_all)
        select_none_btn = QPushButton("Deselect All")
        select_none_btn.clicked.connect(self._select_none)

        quick_select_layout.addWidget(select_all_btn)
        quick_select_layout.addWidget(select_none_btn)
        quick_select_layout.addStretch()

        layout.addLayout(quick_select_layout)

        # Scroll area for checkboxes
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        # Create checkboxes for each student
        for student in self.students:
            checkbox = QCheckBox(student)
            checkbox.setChecked(student in self.current_selection)
            self.checkboxes[student] = checkbox
            scroll_layout.addWidget(checkbox)

        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        layout.addWidget(scroll_area)

        # Action buttons
        button_box = QDialogButtonBox(ButtonBox_Ok | ButtonBox_Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)

        self.setLayout(layout)

    def _select_all(self):
        """Selects all students."""
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(True)

    def _select_none(self):
        """Deselects all students."""
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(False)

    def get_selected_students(self) -> Set[str]:
        """Returns the set of selected students."""
        selected = set()
        for student, checkbox in self.checkboxes.items():
            if checkbox.isChecked():
                selected.add(student)
        return selected


def extract_students_from_remote_data(remote_deck) -> Set[str]:
    """
    Extracts all unique students present in the remote data.

    REFATURED LOGIC:
    - Uses the new RemoteDeck.notes structure
    - Extracts students from the STUDENTS column of each note
    - Returns set with case-sensitive names

    Args:
        remote_deck: RemoteDeck object with spreadsheet data

    Returns:
        Set[str]: Set of unique students found
    """
    students = set()

    if not hasattr(remote_deck, "notes") or not remote_deck.notes:
        return students

    for note_data in remote_deck.notes:
        students_field = note_data.get(cols.students, "").strip()

        if students_field:
            # Separate multiple students by comma
            students_list = [s.strip() for s in students_field.split(",") if s.strip()]
            for student in students_list:
                if student:
                    # Add student name (case-sensitive)
                    students.add(student)

    return students


def get_selected_students_for_deck(deck_url: str) -> Set[str]:
    """
    Gets the selected students for a specific deck.
    If there is no specific selection for the deck, uses the global configuration.
    
    IMPORTANT: Includes [MISSING S.] if the feature is activated.

    Args:
        deck_url: URL of the remote deck

    Returns:
        Set[str]: Set of selected students for this deck (including [MISSING S.] if applicable)
    """
    from .config_manager import get_deck_id
    from .config_manager import get_enabled_students
    from .config_manager import is_sync_missing_students_notes

    meta = get_meta()

    # Navigate through structure: decks -> spreadsheet_id -> student_selection
    spreadsheet_id = get_deck_id(deck_url)
    deck_config = meta.get("decks", {}).get(spreadsheet_id, {})
    student_selection = deck_config.get("student_selection")

    # If no specific selection for the deck, use global configuration
    if student_selection is None:
        global_enabled = get_enabled_students()
        selected_students = set(global_enabled) if global_enabled else set()
    else:
        # Convert to set if it's a list
        if isinstance(student_selection, list):
            selected_students = set(student_selection)
        else:
            selected_students = student_selection if isinstance(student_selection, set) else set()

    # NEW: Include [MISSING STUDENTS] if the feature is activated
    if is_sync_missing_students_notes():
        selected_students.add(DEFAULT_STUDENT)

    return selected_students


def save_selected_students_for_deck(deck_url: str, selected_students: Set[str]):
    """
    Saves the student selection for a specific deck.

    Args:
        deck_url: URL of the remote deck
        selected_students: Set of selected students
    """
    from .config_manager import get_deck_id

    meta = get_meta()

    # Ensure meta structure
    if "decks" not in meta:
        meta["decks"] = {}

    spreadsheet_id = get_deck_id(deck_url)
    if spreadsheet_id not in meta["decks"]:
        meta["decks"][spreadsheet_id] = {}

    # Convert set to list for JSON serialization
    meta["decks"][spreadsheet_id]["student_selection"] = list(selected_students)

    save_meta(meta)


def show_student_selection_dialog(
    deck_url: str, available_students: Set[str]
) -> Optional[Set[str]]:
    """
    Shows student selection dialog and returns user selection.

    Args:
        deck_url: URL of the remote deck
        available_students: Set of available students in the spreadsheet

    Returns:
        Optional[Set[str]]: Set of selected students or None if canceled
    """
    if not available_students:
        StyledMessageBox.warning(None, "No Students", "No students were found in the STUDENTS column of the spreadsheet.")
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
    Filters questions based on selected students.
    NEW VERSION: Uses consistent name normalization.

    NEW: If sync_missing_students_notes is activated, includes questions with empty STUDENTS
    for synchronization into the [MISSING S.] deck

    Args:
        questions: List of questions from remote deck
        selected_students: Set of selected students (already normalized)

    Returns:
        List[Dict]: Filtered list of questions
    """
    if not selected_students:
        return []

    # Check if notes without specific students should be included
    from .config_manager import is_sync_missing_students_notes

    include_missing_students = is_sync_missing_students_notes()

    filtered_questions = []

    add_debug_msg("🔍 FILTER: Starting question filtering...")
    add_debug_msg(f"  • Total questions: {len(questions)}")
    add_debug_msg(f"  • Selected students (norm): {sorted(selected_students)}")
    add_debug_msg(f"  • Include [MISSING S.]: {include_missing_students}")

    for i, question in enumerate(questions):
        fields = question.get("fields", {})
        students_field = fields.get(cols.students, "").strip()

        if not students_field:
            # NEW: If [MISSING STUDENTS] feature is active, include note
            if include_missing_students:
                filtered_questions.append(question)
                add_debug_msg(
                    f"  📝 Question {i+1}: NO student → included ([MISSING STUDENTS] active)"
                )
            else:
                add_debug_msg(
                    f"  ❌ Question {i+1}: NO student → ignored ([MISSING STUDENTS] inactive)"
                )
            continue

        # Check if any of the selected students are in the question's student list
        question_students = set()
        students_list = re.split(r"[,;|]", students_field)
        for student in students_list:
            student = student.strip()
            if student:
                # Add student name (case-sensitive)
                question_students.add(student)

        # DEBUG: Show comparison
        add_debug_msg(
            f"  📝 Question {i+1}: '{students_field}' → {sorted(question_students)}"
        )

        # If there is intersection between question students and selected students (case-sensitive)
        intersection = question_students.intersection(selected_students)
        if intersection:
            filtered_questions.append(question)
            add_debug_msg(f"  ✅ Question {i+1}: INCLUDED (match: {sorted(intersection)})")
        else:
            add_debug_msg(f"  ❌ Question {i+1}: IGNORED (no match)")

    add_debug_msg(
        f"🎯 FILTER: {len(filtered_questions)}/{len(questions)} questions selected"
    )
    return filtered_questions


def get_student_subdeck_name(main_deck_name: str, student: str, fields: Dict) -> str:
    """
    Generates subdeck name for a specific student.

    Structure will be: "root deck::remote deck::student::importance::topic::subtopic::concept"

    Args:
        main_deck_name: Main deck name
        student: Student name
        fields: Note fields with IMPORTANCE, TOPIC, SUBTOPIC and CONCEPT

    Returns:
        str: Full student subdeck name
    """
    from .templates_and_definitions import DEFAULT_CONCEPT
    from .templates_and_definitions import DEFAULT_IMPORTANCE
    from .templates_and_definitions import DEFAULT_SUBTOPIC
    from .templates_and_definitions import DEFAULT_TOPIC

    # Get field values, using default values if empty
    importance = fields.get(cols.hierarchy_1, "").strip() or DEFAULT_IMPORTANCE
    topic = fields.get(cols.hierarchy_2, "").strip() or DEFAULT_TOPIC
    subtopic = fields.get(cols.hierarchy_3, "").strip() or DEFAULT_SUBTOPIC
    concept = fields.get(cols.hierarchy_4, "").strip() or DEFAULT_CONCEPT

    # Create full hierarchy including the student
    return (
        f"{main_deck_name}::{student}::{importance}::{topic}::{subtopic}::{concept}"
    )


def get_missing_students_subdeck_name(main_deck_name: str, fields: Dict) -> str:
    """
    Generates subdeck name for notes without specific students ([MISSING STUDENTS]).

    Structure will be: "root deck::remote deck::[MISSING STUDENTS]::importance::topic::subtopic::concept"

    Args:
        main_deck_name: Main deck name
        fields: Note fields with IMPORTANCE, TOPIC, SUBTOPIC and CONCEPT

    Returns:
        str: Full [MISSING S.] subdeck name
    """
    from .templates_and_definitions import DEFAULT_CONCEPT
    from .templates_and_definitions import DEFAULT_IMPORTANCE
    from .templates_and_definitions import DEFAULT_SUBTOPIC
    from .templates_and_definitions import DEFAULT_TOPIC

    # Get field values, using default values if empty
    importance = fields.get(cols.hierarchy_1, "").strip() or DEFAULT_IMPORTANCE
    topic = fields.get(cols.hierarchy_2, "").strip() or DEFAULT_TOPIC
    subtopic = fields.get(cols.hierarchy_3, "").strip() or DEFAULT_SUBTOPIC
    concept = fields.get(cols.hierarchy_4, "").strip() or DEFAULT_CONCEPT

    # Create full hierarchy with [MISSING STUDENTS] as "student"
    return f"{main_deck_name}::{DEFAULT_STUDENT}::{importance}::{topic}::{subtopic}::{concept}"


def get_students_from_question(fields: Dict) -> Set[str]:
    """
    Extracts all students from a specific question.

    Args:
        fields: Question fields

    Returns:
        Set[str]: Set of students for this question
    """
    students = set()
    students_field = fields.get(cols.students, "").strip()

    if students_field:
        students_list = re.split(r"[,;|]", students_field)
        for student in students_list:
            student = student.strip()
            if student:
                students.add(student)

    return students


def remove_notes_for_unselected_students(
    col,
    main_deck_name: str,
    selected_students: Set[str],
    all_students_in_sheet: Set[str],
) -> int:
    """
    Removes notes for students that are no longer selected.

    Args:
        col: Anki collection
        main_deck_name: Main deck name
        selected_students: Selected students
        all_students_in_sheet: All students present in the spreadsheet

    Returns:
        int: Number of removed notes
    """
    removed_count = 0

    if not mw or not hasattr(mw, "col") or not mw.col:
        return removed_count

    # Find students who should have their notes removed
    unselected_students = all_students_in_sheet - selected_students

    if not unselected_students:
        return removed_count

    # For each unselected student, find and remove their notes
    for student in unselected_students:
        # Search for student subdecks
        student_deck_pattern = f"{main_deck_name}::{student}::"

        # Find all decks that start with this pattern
        all_decks = mw.col.decks.all_names_and_ids()
        student_decks = [
            d for d in all_decks if d.name.startswith(student_deck_pattern)
        ]

        for deck in student_decks:
            # Find all notes in this deck
            note_ids = mw.col.find_notes(f'deck:"{deck.name}"')

            for note_id in note_ids:
                try:
                    mw.col.remove_notes([note_id])
                    removed_count += 1
                except Exception as e:
                    add_debug_msg(f"Error removing note {note_id} from deck {deck.name}: {e}")

    return removed_count


def _convert_to_tsv_export_url(url: str) -> str:
    """
    Converts a Google Sheets URL to TSV export format.
    
    Args:
        url (str): Original Google Sheets URL
        
    Returns:
        str: Formatted URL for TSV export
    """
    try:
        # If it's already a TSV export URL, return as is
        if "export?format=tsv" in url:
            return url
        
        # Use centralized conversion function from utils.py
        from .utils import convert_edit_url_to_tsv
        
        try:
            tsv_url = convert_edit_url_to_tsv(url)
            return tsv_url
        except ValueError:
            # Fallback to previous method if the URL is not a standard edit URL
            return _fallback_url_conversion(url)
            
    except Exception:
        return url


def _fallback_url_conversion(url: str) -> str:
    """
    Fallback method for non-standard URL conversion.
    
    Args:
        url (str): Original Google Sheets URL
        
    Returns:
        str: TSV export formatted URL or original URL if failed
    """
    try:
        import re
        
        # Common Google Sheets URL patterns
        patterns = [
            r'/spreadsheets/d/([a-zA-Z0-9-_]+)',  # Standard URL
            r'[?&]id=([a-zA-Z0-9-_]+)',           # URL with id parameter
        ]
        
        sheet_id = None
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                sheet_id = match.group(1)
                break
        
        if sheet_id:
            # Construct TSV export URL
            tsv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=tsv"
            return tsv_url
        else:
            return url
            
    except Exception:
        return url


def discover_students_from_tsv_url(url: str) -> Set[str]:
    """
    Discovers unique students from a Google Sheets TSV URL.

    Args:
        url (str): Google Sheets TSV URL

    Returns:
        Set[str]: Set of unique student names found
    """
    try:
        
        # First, validate and convert URL using centralized function
        from .utils import validate_url
        
        try:
            tsv_url = validate_url(url)
        except ValueError:
            # Fallback to previous method if validation fails
            tsv_url = _convert_to_tsv_export_url(url)

        # Necessary imports
        try:
            import csv
            import urllib.request
            from io import StringIO
        except ImportError:
            return set()

        # Download TSV data with appropriate headers
        headers = {
            "User-Agent": "Mozilla/5.0 (Sheets2Anki) AnkiAddon"
        }
        request = urllib.request.Request(tsv_url, headers=headers)
        
        with urllib.request.urlopen(request, timeout=30) as response:
            data = response.read().decode("utf-8")

        # Parse CSV/TSV
        csv_reader = csv.DictReader(StringIO(data), delimiter="\t")

        students = set()
        row_count = 0

        # Check headers first
        fieldnames = csv_reader.fieldnames

        if not fieldnames or cols.students not in fieldnames:
            return set()

        # Search for STUDENTS column
        for row in csv_reader:
            row_count += 1

            # Check if STUDENTS column exists and has content
            if cols.students in row and row[cols.students]:
                # Extract students (may be comma separated)
                students_str = row[cols.students].strip()
                if students_str:
                    # Split by comma and clean spaces
                    for student in students_str.split(","):
                        student = student.strip()
                        if student:
                            students.add(student)

        return students

    except urllib.error.HTTPError:
        return set()
        
    except urllib.error.URLError:
        return set()
        
    except Exception:
        return set()


def cleanup_disabled_students_data(
    disabled_students: Set[str], deck_names: List[str]
) -> Dict[str, int]:
    """
    Removes all data for disabled students: notes, cards, note types and decks.

    REFATURED LOGIC to work with unique IDs {student}_{id}:
    - Searches for notes by unique ID using {student}_{id} format
    - Removes notes based on the ID field of the notes, no longer by deck location
    - Removes empty decks after note removal
    - Removes unused note types

    Args:
        disabled_students (Set[str]): Set of students that were disabled
        deck_names (List[str]): List of remote deck names to filter operations

    Returns:
        Dict[str, int]: Removal statistics {
            'notes_removed': int,
            'decks_removed': int,
            'note_types_removed': int
        }
    """
    if not disabled_students or not mw or not hasattr(mw, "col") or not mw.col:
        return {"notes_removed": 0, "decks_removed": 0, "note_types_removed": 0}

    add_debug_msg(
        f"🗑️ CLEANUP: Starting data cleanup for students: {sorted(disabled_students)}"
    )

    stats = {"notes_removed": 0, "decks_removed": 0, "note_types_removed": 0}
    col = mw.col

    try:
        # 1. First, find and remove all notes of disabled students
        notes_to_remove = []

        for student in disabled_students:
            add_debug_msg(f"🧹 CLEANUP: Processing student '{student}'...")

            # Search for notes by unique ID in {student}_{id} or [MISSING STUDENTS]_{id} format
            # Use ID field search containing student_note_id
            student_pattern = f"{student}_*"

            # Find all notes in Anki that have this student in the ID field
            # Since we cannot direct search by custom field, let's iterate
            all_note_ids = col.find_notes("*")  # All notes - use wildcard
            student_note_ids = []

            for note_id in all_note_ids:
                try:
                    note = col.get_note(note_id)
                    # Check if note has ID field and if it matches the student
                    if "ID" in note.keys():
                        note_unique_id = note["ID"].strip()
                        # Check if note ID starts with "{student}_"
                        if note_unique_id.startswith(f"{student}_"):
                            student_note_ids.append(note_id)
                            add_debug_msg(
                                f"   🚀 Found note for student '{student}': {note_unique_id}"
                            )
                except:
                    continue

            notes_to_remove.extend(student_note_ids)
            add_debug_msg(
                f"   📊 Total notes found for '{student}': {len(student_note_ids)}"
            )

        # 2. Remove all found notes
        if notes_to_remove:
            add_debug_msg(f"🗑️ CLEANUP: Removing {len(notes_to_remove)} notes...")
            col.remove_notes(notes_to_remove)
            stats["notes_removed"] = len(notes_to_remove)
            add_debug_msg(f"✅ CLEANUP: {len(notes_to_remove)} notes removed")

        # 3. Find and remove empty decks of disabled students
        for student in disabled_students:
            for deck_name in deck_names:
                # Student deck pattern: "Sheets2Anki::{deck_name}::{student}::"
                student_deck_pattern = f"Sheets2Anki::{deck_name}::{student}::"

                # Find all decks that start with this pattern
                all_decks = col.decks.all_names_and_ids()
                matching_decks = [
                    d for d in all_decks if d.name.startswith(student_deck_pattern)
                ]

                for deck in matching_decks:
                    try:
                        # Check if deck is empty
                        remaining_notes = col.find_notes(f'deck:"{deck.name}"')
                        if not remaining_notes:
                            # Empty deck, can remove
                            from anki.decks import DeckId

                            deck_id = DeckId(deck.id)
                            col.decks.remove([deck_id])
                            stats["decks_removed"] += 1
                            add_debug_msg(f"   🗑️ Empty deck removed: '{deck.name}'")
                        else:
                            add_debug_msg(
                                f"   📁 Deck '{deck.name}' still has {len(remaining_notes)} notes, keeping"
                            )
                    except Exception as e:
                        add_debug_msg(f"   ❌ Error processing deck '{deck.name}': {e}")
                        continue

            # Remove student note types
            removed_note_types = _remove_student_note_types(student, deck_names)
            stats["note_types_removed"] += removed_note_types

        # NEW: Update meta.json after cleanup to remove references of deleted note types
        _update_meta_after_cleanup(disabled_students, deck_names)
        
        # NEW: Remove students from sync history after successful cleanup
        from .config_manager import remove_student_from_sync_history
        for student in disabled_students:
            remove_student_from_sync_history(student)
        add_debug_msg(f"📝 CLEANUP: {len(disabled_students)} students removed from sync history")

        # Save changes
        col.save()

        add_debug_msg(f"✅ CLEANUP: Completed! Stats: {stats}")
        return stats

    except Exception as e:
        add_debug_msg(f"❌ CLEANUP: Error during cleanup: {e}")
        import traceback

        traceback.print_exc()
        return stats


def _remove_student_note_types(student: str, deck_names: List[str]) -> int:
    """
    Removes specific note types of a student.
    
    CORRECTED VERSION WITH IMPROVED DEBUG:
    - Checks all note types in Anki, not just those based on deck_names
    - Removes orphaned note types that may exist due to old configurations
    - Detects varied naming patterns
    - Adds detailed debug logs
    - Uses proper addon logging system

    Args:
        student (str): Student name
        deck_names (List[str]): List of remote deck names (used as preferred filter)

    Returns:
        int: Number of removed note types
    """
    # Use proper logging when possible
    try:
        from .utils import add_debug_message
        log_func = lambda msg: add_debug_message(msg, "CLEANUP_NOTE_TYPES")
    except:
        log_func = print
    
    if not mw or not hasattr(mw, "col") or not mw.col:
        log_func(f"❌ Anki not available to remove note types for student '{student}'")
        return 0

    col = mw.col
    removed_count = 0

    try:
        # Get all note types
        note_types = col.models.all()
        log_func(f"🔍 Checking {len(note_types)} note types for student '{student}'")

        student_note_types_found = []
        
        for note_type in note_types:
            note_type_name = note_type.get("name", "")
            note_type_id = note_type.get("id")

            if not note_type_id:
                continue

            should_remove = False
            match_reason = ""

            # METHOD 1: Check patterns based on provided deck_names
            for deck_name in deck_names:
                student_pattern_basic = f"Sheets2Anki - {deck_name} - {student} - Basic"
                student_pattern_cloze = f"Sheets2Anki - {deck_name} - {student} - Cloze"

                if note_type_name == student_pattern_basic or note_type_name == student_pattern_cloze:
                    should_remove = True
                    match_reason = f"deck pattern for '{student}'"
                    break

            # METHOD 2: Check general pattern for orphaned note types (robust fallback)
            if not should_remove and note_type_name.startswith("Sheets2Anki - "):
                # General format: "Sheets2Anki - {any_deck} - {student} - {Basic|Cloze}"
                parts = note_type_name.split(" - ")
                if len(parts) >= 4:
                    # Student is in the third part (index 2)
                    note_student = parts[2]
                    note_type_suffix = parts[-1]  # Basic or Cloze
                    
                    if (note_student == student and 
                        note_type_suffix in ["Basic", "Cloze"]):
                        should_remove = True
                        match_reason = f"orphaned note type for student '{student}'"

            if should_remove:
                student_note_types_found.append((note_type_name, note_type_id, match_reason))

        log_func(f"🎯 Found {len(student_note_types_found)} note types for student '{student}':")
        for nt_name, nt_id, reason in student_note_types_found:
            log_func(f"   • '{nt_name}' (ID: {nt_id}) - {reason}")

        # Try to remove found note types
        for note_type_name, note_type_id, match_reason in student_note_types_found:
            try:
                # Check if note type is in use with defensive approach
                from anki.models import NotetypeId
                use_count = 0
                
                try:
                    # Method 1: Try with NotetypeId
                    use_count = col.models.useCount(NotetypeId(note_type_id))
                except (TypeError, AttributeError) as e:
                    log_func(f"⚠️ NotetypeId method failed for {note_type_id}: {e}")
                    try:
                        # Method 2: Try with int directly (older versions)
                        use_count = col.models.useCount(note_type_id)
                    except Exception as e2:
                        log_func(f"⚠️ int method also failed for {note_type_id}: {e2}")
                        try:
                            # Method 3: Search for notes using this note type manually
                            note_ids = col.find_notes(f"mid:{note_type_id}")
                            use_count = len(note_ids)
                            log_func(f"ℹ️ Using manual search: {use_count} notes found for note type {note_type_id}")
                        except Exception as e3:
                            log_func(f"❌ All methods failed for {note_type_id}: {e3}")
                            # If we cannot check, assume it's in use for safety
                            use_count = 1
                
                if use_count > 0:
                    log_func(f"⚠️ Note type '{note_type_name}' still has {use_count} notes, skipping removal")
                    continue

                # Note type is not in use, can remove
                log_func(f"🗑️ REMOVING note type '{note_type_name}' (ID: {note_type_id})...")
                
                try:
                    # Try removal with NotetypeId
                    col.models.remove(NotetypeId(note_type_id))
                except (TypeError, AttributeError) as e:
                    log_func(f"⚠️ Removal with NotetypeId failed: {e}")
                    try:
                        # Fallback: try with int directly
                        col.models.remove(note_type_id)
                    except Exception as e2:
                        log_func(f"❌ Removal failed completely: {e2}")
                        continue
                
                removed_count += 1
                log_func(f"✅ Note type '{note_type_name}' removed successfully")

            except Exception as e:
                log_func(f"❌ Error removing note type '{note_type_name}': {e}")
                import traceback
                traceback.print_exc()
                continue

        if removed_count == 0 and len(student_note_types_found) > 0:
            log_func(f"⚠️ ATTENTION: {len(student_note_types_found)} note types found but none were removed")
        elif removed_count > 0:
            log_func(f"✅ SUCCESS: {removed_count} note types removed for student '{student}'")
        else:
            log_func(f"ℹ️ No note type found for student '{student}'")

        return removed_count

    except Exception as e:
        log_func(f"❌ Error removing note types for student '{student}': {e}")
        import traceback
        traceback.print_exc()
        return 0


def _update_meta_after_cleanup(
    disabled_students: Set[str], deck_names: List[str]
) -> None:
    """
    Updates meta.json removing references of note types that were deleted during cleanup.

    Args:
        disabled_students (Set[str]): Set of students that were disabled
        deck_names (List[str]): List of remote deck names
    """
    # Use proper logging when possible
    try:
        from .utils import add_debug_message
        log_func = lambda msg: add_debug_message(msg, "CLEANUP_META")
    except:
        log_func = print
        
    try:
        from .config_manager import get_meta
        from .config_manager import save_meta

        log_func(
            f"📝 META UPDATE: Updating meta.json after cleanup of {len(disabled_students)} students"
        )

        meta = get_meta()
        updates_made = False

        # For each configured deck
        for deck_info in meta.get("decks", {}).values():
            deck_name = deck_info.get("remote_deck_name", "")
            if deck_name in deck_names:
                note_types_dict = deck_info.get("note_types", {})
                note_types_to_remove = []

                # Find note types of disabled students
                for note_type_id, note_type_name in note_types_dict.items():
                    for student in disabled_students:
                        # Format: "Sheets2Anki - {remote_deck_name} - {student} - {Basic|Cloze}"
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
                                f"🗑️ META: Removing note type reference '{note_type_name}' (ID: {note_type_id})"
                            )

                # Remove found note types
                for note_type_id in note_types_to_remove:
                    if note_type_id in note_types_dict:
                        del note_types_dict[note_type_id]
                        updates_made = True

        # Save updated meta.json if there were changes
        if updates_made:
            save_meta(meta)
            log_func(
                f"✅ META UPDATE: meta.json updated with {len([nt for deck in meta.get('decks', {}).values() for nt in deck.get('note_types', {}).keys()])} note types remaining"
            )
        else:
            log_func("ℹ️ META UPDATE: No update necessary in meta.json")

    except Exception as e:
        log_func(f"❌ META UPDATE: Error updating meta.json after cleanup: {e}")
        import traceback

        traceback.print_exc()


def _update_meta_after_missing_cleanup(deck_names: List[str]) -> None:
    """
    Updates meta.json by removing missing student note type references that were deleted.
    Handles DEFAULT_STUDENT, [MISSING STUDENTS] and [MISSING S.].

    Args:
        deck_names (List[str]): List of remote deck names
    """
    # Use proper logging when possible
    try:
        from .utils import add_debug_message
        log_func = lambda msg: add_debug_message(msg, "CLEANUP_MISSING_META")
    except:
        log_func = print
        
    try:
        from .config_manager import get_meta
        from .config_manager import save_meta

        log_func(
            f"📝 META UPDATE: Updating meta.json after missing student cleanup for {len(deck_names)} decks"
        )

        meta = get_meta()
        updates_made = False
        
        # Legacy missing placeholders
        missing_placeholders = [
            DEFAULT_STUDENT,
            "[MISSING STUDENTS]",
            "[MISSING S.]"
        ]

        # For each configured deck
        for deck_info in meta.get("decks", {}).values():
            deck_name = deck_info.get("remote_deck_name", "")
            if deck_name in deck_names:
                note_types_dict = deck_info.get("note_types", {})
                note_types_to_remove = []

                # Find missing student note types
                for note_type_id, note_type_name in note_types_dict.items():
                    # Check against all placeholders
                    is_missing_type = False
                    for placeholder in missing_placeholders:
                        pattern_basic = f"Sheets2Anki - {deck_name} - {placeholder} - Basic"
                        pattern_cloze = f"Sheets2Anki - {deck_name} - {placeholder} - Cloze"
                        
                        if note_type_name == pattern_basic or note_type_name == pattern_cloze:
                            is_missing_type = True
                            break
                    
                    if is_missing_type:
                        note_types_to_remove.append(note_type_id)
                        log_func(
                            f"🗑️ META: Removing missing student note type reference: '{note_type_name}' (ID: {note_type_id})"
                        )

                # Remove found note types
                for note_type_id in note_types_to_remove:
                    if note_type_id in note_types_dict:
                        del note_types_dict[note_type_id]
                        updates_made = True

        # Save updated meta.json if there were changes
        if updates_made:
            save_meta(meta)
            log_func("✅ META UPDATE: meta.json updated after missing student cleanup")
        else:
            log_func(
                "ℹ️ META UPDATE: No missing student references found in meta.json"
            )

    except Exception as e:
        log_func(
            f"❌ META UPDATE: Error updating meta.json after [MISSING S.] cleanup: {e}"
        )
        import traceback

        traceback.print_exc()


def get_disabled_students_for_cleanup(
    current_enabled: Set[str], previous_enabled: Set[str]
) -> Set[str]:
    """
    Identifies students who were removed from the enabled list and need data cleanup.
    
    CORRECTED VERSION FOR PROPER LOGIC:
    - Only considers students who were SYNCHRONIZED at least once
    - A student can only have data for cleanup if data was created previously
    - Students in available_students that were never synchronized SHOULD NOT be cleaned up
    - Detects existing note types in Anki as secondary source
    
    NOTE: DEFAULT_STUDENT is not considered a "real student" for cleanup purposes.
    Its presence depends on the sync_missing_students_notes configuration, not the enabled student list.

    Args:
        current_enabled (Set[str]): Currently enabled students
        previous_enabled (Set[str]): Previously enabled students (can be used as additional source)

    Returns:
        Set[str]: Students that were disabled and need data removed
    """
    # Use proper logging when possible
    try:
        from .utils import add_debug_message
        log_func = lambda msg: add_debug_message(msg, "CLEANUP")
    except:
        log_func = print
    
    log_func("🔍 CLEANUP: Identifying disabled students for cleanup...")
    
    # MAIN SOURCE: Only students who were synchronized at least once
    from .config_manager import get_students_with_sync_history
    historically_synced_students = get_students_with_sync_history()
    log_func(f"📚 Students already synchronized: {sorted(historically_synced_students)}")
    
    # ADDITIONAL SOURCE: Existing note types in Anki (for inconsistency cases)
    anki_detected_students = set()
    if hasattr(mw, "col") and mw.col:
        try:
            note_types = mw.col.models.all()
            for note_type in note_types:
                note_type_name = note_type.get("name", "")
                # Format: "Sheets2Anki - {remote_deck_name} - {student} - {Basic|Cloze}"
                if note_type_name.startswith("Sheets2Anki - ") and " - " in note_type_name:
                    parts = note_type_name.split(" - ")
                    if len(parts) >= 4:
                        # Student is in the third part (index 2)
                        student_name = parts[2]
                        if student_name and student_name != "[MISSING S.]":
                            anki_detected_students.add(student_name)
            
            log_func(f"🔍 Students found in Anki via note types: {sorted(anki_detected_students)}")
        except Exception as e:
            log_func(f"⚠️ Error checking note types in Anki: {e}")
    
    # COMBINE: Students who had data created (sync_history + existing note types)
    students_with_created_data = historically_synced_students.union(anki_detected_students)
    
    # INCLUDE available_students only if they are also in history or have note types
    from .config_manager import get_global_student_config
    config = get_global_student_config()
    available_students = set(config.get("available_students", []))
    
    # Students in available_students that also have sync evidence
    available_and_synced = available_students.intersection(students_with_created_data)
    
    # Combine all student sources where data was created
    all_students_with_data = students_with_created_data.union(available_and_synced)
    
    log_func(f"📊 Source report:")
    log_func(f"   • Sync history: {sorted(historically_synced_students)}")
    log_func(f"   • Note types in Anki: {sorted(anki_detected_students)}")
    log_func(f"   • Available students: {sorted(available_students)}")
    log_func(f"   • Available + with data: {sorted(available_and_synced)}")
    log_func(f"   • TOTAL with created data: {sorted(all_students_with_data)}")
    
    # Remove DEFAULT_STUDENT from comparison, since it's not a "real student"
    current_real_students = {s for s in current_enabled if s != DEFAULT_STUDENT}
    students_with_data_real = {s for s in all_students_with_data if s != DEFAULT_STUDENT}

    log_func(f"✅ Real students currently enabled: {sorted(current_real_students)}")
    log_func(f"📖 Real students with created data: {sorted(students_with_data_real)}")

    # MAIN DETECTION: Students who had data but are no longer enabled
    disabled_students = students_with_data_real - current_real_students

    if disabled_students:
        log_func(f"🎯 CLEANUP: Detected students for cleanup: {sorted(disabled_students)}")
        log_func(f"   • Currently enabled: {sorted(current_real_students)}")
        log_func(f"   • With created data: {sorted(students_with_data_real)}")
        log_func(f"   • Students to remove: {sorted(disabled_students)}")
    else:
        log_func("✅ CLEANUP: No student was disabled")

    log_func(f"🔍 CLEANUP: {DEFAULT_STUDENT} excluded from comparison (not a real student)")

    return disabled_students


def show_cleanup_confirmation_dialog(disabled_students: Set[str]) -> int:
    """
    Shows a confirmation dialog before removing data of disabled students.
    
    REFATURED: Now uses centralized function to ensure consistency.

    Args:
        disabled_students (Set[str]): Set of students that will have data removed

    Returns:
        int: Dialog result code (MessageBox_Yes, MessageBox_No, MessageBox_Cancel)
    """
    from .data_removal_confirmation import confirm_students_removal

    if not disabled_students:
        return MessageBox_No

    # Convert set to list and use centralized function
    disabled_students_list = list(disabled_students)
    
    # Use centralized function to confirm removal
    result = confirm_students_removal(
        disabled_students=disabled_students_list,
        missing_functionality_disabled=False,  # Students only, no [MISSING S.]
        window_title="Confirm Permanent Data Removal"
    )

    if result == MessageBox_Yes:
        add_debug_msg(
            f"⚠️ CLEANUP: User confirmed data removal for {len(disabled_students)} students"
        )
    elif result == MessageBox_Cancel:
        add_debug_msg("🛡️ CLEANUP: User CANCELLED sync operation")
    else:
        add_debug_msg("🛡️ CLEANUP: User chose to KEEP data")

    return result


def cleanup_missing_students_data(deck_names: List[str]) -> Dict[str, int]:
    """
    Removes all "{DEFAULT_STUDENT}" note data when the feature is disabled.
    
    CORRECTED VERSION:
    - Detects {DEFAULT_STUDENT} note types using multiple patterns
    - Searches for orphaned note types even if deck_name doesn't match exactly
    - Removes data more robustly

    Args:
        deck_names (List[str]): List of remote deck names to filter operations

    Returns:
        Dict[str, int]: Removal statistics {
            'notes_removed': int,
            'decks_removed': int,
            'note_types_removed': int
        }
    """
    if not mw or not hasattr(mw, "col") or not mw.col:
        return {"notes_removed": 0, "decks_removed": 0, "note_types_removed": 0}

    add_debug_msg(
        f"🗑️ CLEANUP: Starting {DEFAULT_STUDENT} data cleanup for decks: {deck_names}"
    )

    stats = {"notes_removed": 0, "decks_removed": 0, "note_types_removed": 0}
    col = mw.col

    # Legacy missing placeholders
    missing_placeholders = [
        DEFAULT_STUDENT,
        "[MISSING STUDENTS]",
        "[MISSING S.]"
    ]

    try:
        # 1. Search and remove all notes with ID {placeholder}_{any_id}
        all_note_ids = col.find_notes("*")
        missing_note_ids = []

        for note_id in all_note_ids:
            try:
                note = col.get_note(note_id)
                if "ID" in note.keys():
                    note_unique_id = note["ID"].strip()
                    if any(note_unique_id.startswith(f"{p}_") for p in missing_placeholders):
                        missing_note_ids.append(note_id)
                        add_debug_msg(f"   📝 Found missing student note: {note_unique_id}")
            except:
                continue

        # Remove all found missing notes
        if missing_note_ids:
            add_debug_msg(f"🗑️ CLEANUP: Removing {len(missing_note_ids)} missing student notes...")
            col.remove_notes(missing_note_ids)
            stats["notes_removed"] = len(missing_note_ids)

        # 2. Remove missing student decks (using multiple patterns)
        all_decks = col.decks.all_names_and_ids()
        
        # Patterns to search for:
        # - "Sheets2Anki::{deck_name}::{placeholder}::"
        # - Any deck containing "::{placeholder}::"
        missing_decks_found = []
        
        for deck in all_decks:
            deck_name = deck.name
            
            # Check if it's a missing student deck
            is_missing_deck = False
            for placeholder in missing_placeholders:
                if f"::{placeholder}::" in deck_name:
                    is_missing_deck = True
                    break
            
            if is_missing_deck:
                # Check if it corresponds to any provided decks (if provided)
                if deck_names:
                    deck_matches = False
                    for remote_deck_name in deck_names:
                        for placeholder in missing_placeholders:
                            expected_pattern = f"Sheets2Anki::{remote_deck_name}::{placeholder}::"
                            if deck_name.startswith(expected_pattern):
                                deck_matches = True
                                break
                        if deck_matches:
                            break
                    
                    if deck_matches:
                        missing_decks_found.append(deck)
                        add_debug_msg(f"   📁 Missing student deck found: {deck_name}")
                else:
                    # If no deck_names specified, remove any missing student deck
                    missing_decks_found.append(deck)
                    add_debug_msg(f"   📁 Generic missing student deck found: {deck_name}")

        # Remove empty missing student decks
        for deck in missing_decks_found:
            try:
                remaining_notes = col.find_notes(f'deck:"{deck.name}"')
                if not remaining_notes:
                    from anki.decks import DeckId
                    col.decks.remove([DeckId(deck.id)])
                    stats["decks_removed"] += 1
                    add_debug_msg(f"   🗑️ Empty missing student deck removed: '{deck.name}'")
                else:
                    add_debug_msg(f"   📁 Missing student deck '{deck.name}' still has {len(remaining_notes)} notes, keeping")
            except Exception as e:
                add_debug_msg(f"   ❌ Error processing missing student deck '{deck.name}': {e}")

        # 3. Remove missing student note types (using robust detection)
        note_types = col.models.all()
        
        for note_type in note_types:
            note_type_name = note_type.get("name", "")
            note_type_id = note_type.get("id")
            
            if not note_type_id:
                continue
            
            should_remove = False
            
            # METHOD 1: Check patterns based on provided deck_names
            if deck_names:
                for deck_name in deck_names:
                    for placeholder in missing_placeholders:
                        pattern_basic = f"Sheets2Anki - {deck_name} - {placeholder} - Basic"
                        pattern_cloze = f"Sheets2Anki - {deck_name} - {placeholder} - Cloze"
                        
                        if note_type_name == pattern_basic or note_type_name == pattern_cloze:
                            should_remove = True
                            add_debug_msg(f"   🎯 Missing student note type '{note_type_name}' matched deck pattern")
                            break
                    if should_remove:
                        break
            
            # METHOD 2: Check general pattern for orphaned missing student note types
            if not should_remove and note_type_name.startswith("Sheets2Anki - "):
                parts = note_type_name.split(" - ")
                if len(parts) >= 4:
                    note_student = parts[2]
                    note_type_suffix = parts[-1]
                    
                    if (note_student in missing_placeholders and 
                        note_type_suffix in ["Basic", "Cloze"]):
                        should_remove = True
                        add_debug_msg(f"   🔍 Orphaned missing student note type '{note_type_name}' found", "CLEANUP_MISSING")
            
            if should_remove:
                try:
                    # Check if note type is in use with defensive approach
                    from anki.models import NotetypeId
                    use_count = 0
                    
                    try:
                        # Method 1: Try with NotetypeId
                        use_count = col.models.useCount(NotetypeId(note_type_id))
                    except (TypeError, AttributeError) as e:
                        add_debug_msg(f"   ⚠️ NotetypeId method failed for missing student {note_type_id}: {e}", "CLEANUP_MISSING")
                        try:
                            # Method 2: Try with int directly
                            use_count = col.models.useCount(note_type_id)
                        except Exception as e2:
                            try:
                                # Method 3: Search for notes manually
                                note_ids = col.find_notes(f"mid:{note_type_id}")
                                use_count = len(note_ids)
                                add_debug_msg(f"ℹ️ Using manual search for missing student: {use_count} notes", "CLEANUP_MISSING")
                            except Exception as e3:
                                # If all fails, assume it's in use for safety
                                use_count = 1
                    
                    if use_count > 0:
                        add_debug_msg(f"⚠️ Missing student note type '{note_type_name}' still has {use_count} notes, skipping", "CLEANUP_MISSING")
                        continue
                    
                    # Note type is not in use, can remove
                    try:
                        # Try removal with NotetypeId
                        col.models.remove(NotetypeId(note_type_id))
                    except (TypeError, AttributeError) as e:
                        add_debug_msg(f"⚠️ Removal with NotetypeId failed for missing student: {e}", "CLEANUP_MISSING")
                        try:
                            # Fallback: try with int directly
                            col.models.remove(note_type_id)
                        except Exception as e2:
                            add_debug_msg(f"❌ Removal failed completely for missing student: {e2}", "CLEANUP_MISSING")
                            continue
                    
                    stats["note_types_removed"] += 1
                    add_debug_msg(f"🗑️ Missing student note type '{note_type_name}' removed", "CLEANUP_MISSING")
                    
                except Exception as e:
                    add_debug_msg(f"❌ Error removing missing student note type '{note_type_name}': {e}", "CLEANUP_MISSING")

        # NEW: Update meta.json after cleanup
        _update_meta_after_missing_cleanup(deck_names)

        # Save changes
        col.save()

        add_debug_msg(f"✅ CLEANUP: Missing student cleanup completed - Statistics: {stats}")
        return stats

    except Exception as e:
        add_debug_msg(f"❌ CLEANUP: Error during [MISSING STUDENTS] cleanup: {e}")
        return stats


def show_missing_cleanup_confirmation_dialog() -> int:
    """
    Shows confirmation dialog for missing student data cleanup.
    REFATURED: Uses centralized module for message generation and confirmation.

    Returns:
        int: Dialog result code (MessageBox_Yes, MessageBox_No, MessageBox_Cancel)
    """
    from .data_removal_confirmation import show_data_removal_confirmation_dialog
    
    # Use centralized dialog only for missing student placeholder
    # Now returns int result
    result = show_data_removal_confirmation_dialog(
        students_to_remove=[DEFAULT_STUDENT],
        window_title=f"⚠️ Removal Confirmation - {DEFAULT_STUDENT} Notes"
    )
    
    if result == MessageBox_Yes:
        add_debug_msg(f"⚠️ CLEANUP: User confirmed {DEFAULT_STUDENT} data removal")
    elif result == MessageBox_Cancel:
        add_debug_msg(f"🛡️ CLEANUP: User CANCELLED sync (during {DEFAULT_STUDENT} check)")
    else:
        add_debug_msg(f"🛡️ CLEANUP: User chose to KEEP {DEFAULT_STUDENT} data")

    return result
