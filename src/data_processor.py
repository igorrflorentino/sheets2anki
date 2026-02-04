"""
Data and note processing for the Sheets2Anki addon.

This module contains functionalities for:
- Downloading and analyzing remote decks from Google Sheets
- Processing TSV data
- Creating and updating notes in Anki
- Managing cloze cards and hierarchical tags

Consolidated from:
- parseRemoteDeck.py: Remote deck analysis
- note_processor.py: Note processing
"""

# =============================================================================
# IMPORTS
# =============================================================================

import csv
import re
import socket
import urllib.error
import urllib.request

from . import templates_and_definitions as cols  # Centralized column definitions
from .templates_and_definitions import DEFAULT_CONCEPT
from .templates_and_definitions import DEFAULT_SUBTOPIC
from .templates_and_definitions import DEFAULT_TOPIC
from .templates_and_definitions import DEFAULT_IMPORTANCE
from .templates_and_definitions import DEFAULT_STUDENT
from .templates_and_definitions import TAG_ADDITIONAL
from .templates_and_definitions import TAG_YEARS
from .templates_and_definitions import TAG_EXAM_BOARDS
from .templates_and_definitions import TAG_CAREERS
from .templates_and_definitions import TAG_CONCEPTS
from .templates_and_definitions import TAG_IMPORTANCE
from .templates_and_definitions import TAG_ROOT
from .templates_and_definitions import TAG_TOPICS
from .templates_and_definitions import ensure_custom_models
from .utils import CollectionSaveError
from .utils import ensure_subdeck_exists
from .utils import get_subdeck_name
from .utils import add_debug_message


def add_debug_msg(message, category="DATA_PROCESSOR"):
    """Local helper for debug messages."""
    add_debug_message(message, category)

# Import mw safely
try:
    from .compat import mw
except ImportError:
    # Fallback for direct import
    try:
        from aqt import mw
    except ImportError:
        mw = None

# =============================================================================
# CUSTOM EXCEPTIONS
# =============================================================================


class RemoteDeckError(Exception):
    """Custom exception for errors related to remote decks."""

    pass


# =============================================================================
# DATA CLASSES
# =============================================================================


class RemoteDeck:
    """
    Class representing a deck loaded from a remote source.

    This class encapsulates all data from a remote deck, including:
    - List of notes with their respective fields
    - Remote deck name
    - Settings and metadata
    """

    def __init__(self, name="", url=""):
        """
        Initializes an empty remote deck.

        Args:
            name (str): Deck name
            url (str): Data source URL
        """
        self.name = name
        self.url = url
        self.notes = []  # List of dictionaries representing notes
        self.headers = []  # List of spreadsheet headers

        # Refactored metrics per specification
        self.total_table_lines = 0  # 1. Total table lines
        self.valid_note_lines = 0  # 2. Lines with filled ID
        self.invalid_note_lines = 0  # 3. Lines with empty ID
        self.sync_marked_lines = 0  # 4. Lines marked for sync
        self.total_potential_anki_notes = 0  # 5. Total potential Anki notes
        self.potential_student_notes = 0  # 6. Notes for specific students
        self.potential_missing_students_notes = 0  # 7. Notes for [MISSING STUDENTS]
        self.unique_students = set()  # 8. Set of unique students
        self.notes_per_student = {}  # 9. Notes per individual student
        self.ignored_ghost_rows = 0  # 10. Ghost Rows (ignored)

        self.enabled_students = set()  # Set of enabled students

    def add_note(self, note_data):
        """
        Adds a note to the deck and updates metrics.

        Args:
            note_data (dict): Note data
        """
        if not note_data:
            return

        # Check for completely empty rows (ghost rows from Google Sheets)
        # If all fields are empty (or only contain default Sync values like "FALSE"), we ignore this row
        # This prevents "Invalid Rows" noise from checkbox columns extended down
        has_id = bool(note_data.get(cols.identifier, "").strip())
        
        if not has_id:
            # Check if there is any content in columns OTHER than SYNC
            # We ignore SYNC because checkboxes often default to FALSE in empty rows
            other_content = False
            for key, value in note_data.items():
                if key != cols.is_sync and value and value.strip():
                    other_content = True
                    break
            
            # If no ID and no other content, it's a ghost row -> Ignore
            if not other_content:
                self.ignored_ghost_rows += 1
                self.total_table_lines += 1 # Ghost rows are still lines in the table
                return

        self.notes.append(note_data)

        # 1. Total table lines (always increments)
        self.total_table_lines += 1

            # 2 and 3. Valid vs invalid lines (based on ID)
        note_id = note_data.get(cols.identifier, "").strip()
        if note_id:
            self.valid_note_lines += 1
        else:
            self.invalid_note_lines += 1
            # Debug log for invalid lines
            # Debug log for invalid lines removed to avoid log spam
            # add_debug_msg(f"Invalid line found...", category="METRICS")
            # For invalid lines, do not process additional metrics
            # but continue to allow other accounting if necessary
            return

        # 4. Lines marked for sync (only for valid lines)
        sync_value = str(note_data.get(cols.is_sync, "")).strip().lower()
        if sync_value in ["true", "1", "yes", "sim"]:
            self.sync_marked_lines += 1

        # Student analysis for metrics 5-9 (only for valid lines)
        alunos_str = note_data.get(cols.students, "").strip()

        if not alunos_str:
            # 7. Note for [MISSING STUDENTS]
            self.potential_missing_students_notes += 1
            self.total_potential_anki_notes += 1

            # Add [MISSING STUDENTS] to per-student statistics
            if DEFAULT_STUDENT not in self.notes_per_student:
                self.notes_per_student[DEFAULT_STUDENT] = 0
            self.notes_per_student[DEFAULT_STUDENT] += 1
        else:
            # Extract students from string
            students_in_note = [s.strip() for s in alunos_str.split(",") if s.strip()]

            # 8. Add unique students
            for student in students_in_note:
                self.unique_students.add(student)

                # 9. Count notes per individual student
                if student not in self.notes_per_student:
                    self.notes_per_student[student] = 0
                self.notes_per_student[student] += 1

            # 6. Total potential notes for specific students
            self.potential_student_notes += len(students_in_note)

            # 5. Add to total potential Anki notes
            self.total_potential_anki_notes += len(students_in_note)

    def finalize_metrics(self):
        """
        Finalizes metric calculation after all notes have been added.
        Should be called at the end of deck processing.
        """
        # Calculate derived metrics
        self.unique_students.discard(
            DEFAULT_STUDENT
        )  # Do not count [MISSING STUDENTS] as a real unique student

        # Validate automatically
        try:
            self.validate_metrics()
        except ValueError as e:
            # Warning log but not a failure
            add_debug_msg(f"⚠️ Warning: Inconsistency detected in remote deck metrics: {e}", category="METRICS")

    def get_statistics(self):
        """
        Returns remote deck statistics - REFACTORED.

        Returns:
            dict: Deck statistics according to new specification
        """
        return {
            # Basic table metrics
            "total_table_lines": self.total_table_lines,  # 1. Total lines
            "valid_note_lines": self.valid_note_lines,  # 2. Lines with filled ID
            "invalid_note_lines": self.invalid_note_lines,  # 3. Lines with empty ID
            "ignored_ghost_rows": self.ignored_ghost_rows,  # 10. Ghost Rows
            "sync_marked_lines": self.sync_marked_lines,  # 4. Lines marked for sync
            # Anki potential metrics
            "total_potential_anki_notes": self.total_potential_anki_notes,  # 5. Total potential in Anki
            "potential_student_notes": self.potential_student_notes,  # 6. Notes for specific students
            "potential_missing_students_notes": self.potential_missing_students_notes,  # 7. Notes for [MISSING STUDENTS]
            # Student metrics
            "unique_students_count": len(
                self.unique_students
            ),  # 8. Total unique students
            "notes_per_student": self.notes_per_student.copy(),  # 9. Notes per student
            # Additional info
            "unique_students_list": sorted(list(self.unique_students)),
            "enabled_students_count": len(self.enabled_students),
            "headers": self.headers,
        }

    def validate_metrics(self):
        """
        Validates the consistency of calculated metrics.

        Raises:
            ValueError: If there are inconsistencies in the metrics
        """
        # 1. Validate that valid lines + invalid lines + ghost rows = total
        total_calculated = self.valid_note_lines + self.invalid_note_lines + self.ignored_ghost_rows
        if total_calculated != self.total_table_lines:
            raise ValueError(
                f"Inconsistency: valid({self.valid_note_lines}) + invalid({self.invalid_note_lines}) + ghost({self.ignored_ghost_rows}) != total({self.total_table_lines})"
            )

        # 2. Validate that sync_marked_lines does not exceed valid_note_lines
        if self.sync_marked_lines > self.valid_note_lines:
            raise ValueError(
                f"Inconsistency: lines marked for sync({self.sync_marked_lines}) > valid lines({self.valid_note_lines})"
            )

        # 3. Validate that total potential = student notes + missing_a notes
        total_potential_calculated = (
            self.potential_student_notes + self.potential_missing_students_notes
        )
        if total_potential_calculated != self.total_potential_anki_notes:
            raise ValueError(
                f"Inconsistency: student({self.potential_student_notes}) + missing_students({self.potential_missing_students_notes}) != total_potential({self.total_potential_anki_notes})"
            )

        # 4. Validate sum of notes per student
        total_notes_per_student = sum(self.notes_per_student.values())
        if total_notes_per_student != self.total_potential_anki_notes:
            raise ValueError(
                f"Inconsistency: sum notes per student({total_notes_per_student}) != total_potential({self.total_potential_anki_notes})"
            )

        # 5. Validate unique student count
        expected_unique_count = len(self.unique_students)
        if expected_unique_count != len(self.notes_per_student):
            # Adjustment for [MISSING STUDENTS] which may be in notes_per_student but not in unique_students
            if (
                DEFAULT_STUDENT in self.notes_per_student
                and DEFAULT_STUDENT not in self.unique_students
            ):
                expected_unique_count += 1
            if expected_unique_count != len(self.notes_per_student):
                raise ValueError(
                    f"Inconsistency: unique students({len(self.unique_students)}) != students in dict({len(self.notes_per_student)})"
                )

        # 6. (Re-validation) Validate that sum of notes per individual student = total potential
        total_per_student = sum(self.notes_per_student.values())
        if total_per_student != self.total_potential_anki_notes:
            raise ValueError(
                f"Inconsistency: individual sum({total_per_student}) != total potential({self.total_potential_anki_notes})"
            )

        # 7. (Re-validation) Validate that unique student count matches the dictionary
        if len(self.unique_students) != len(self.notes_per_student):
            # Same check as above for [MISSING STUDENTS]
            check_count = len(self.unique_students)
            if DEFAULT_STUDENT in self.notes_per_student and DEFAULT_STUDENT not in self.unique_students:
                check_count += 1
            if check_count != len(self.notes_per_student):
                raise ValueError(
                    f"Inconsistency: unique students({len(self.unique_students)}) != dictionary keys({len(self.notes_per_student)})"
                )


# =============================================================================
# REMOTE DECK ANALYSIS FUNCTIONS
# =============================================================================


def getRemoteDeck(url, enabled_students=None, debug_messages=None):
    """
    Main function to obtain and process a remote deck.

    This function coordinates the entire process of downloading, analyzing, and building
     the remote deck from a Google Sheets spreadsheet URL.

    Args:
        url (str): Spreadsheet URL in TSV format
        enabled_students (list, optional): List of enabled students
        debug_messages (list, optional): List to accumulate debug messages

    Returns:
        RemoteDeck: Processed remote deck object

    Raises:
        RemoteDeckError: If there's an error in deck processing
    """

    def add_debug_msg(message, category="REMOTE_DECK"):
        """Helper to add debug messages with timestamp."""
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] [{category}] {message}"
        if debug_messages is not None:
            debug_messages.append(formatted_msg)

    try:
        add_debug_msg(f"Starting remote deck download: {url}")

        # 1. Download TSV data
        tsv_data = download_tsv_data(url)
        add_debug_msg(f"Download complete: {len(tsv_data)} bytes")

        # 2. Parse TSV data
        parsed_data = parse_tsv_data(tsv_data, debug_messages)
        add_debug_msg(f"Parse complete: {len(parsed_data['rows'])} lines")

        # 3. Build remote deck
        remote_deck = build_remote_deck_from_tsv(
            parsed_data, url, enabled_students, debug_messages
        )

        stats = remote_deck.get_statistics()
        add_debug_msg(
            f"Deck built: {stats['sync_marked_lines']}/{stats['valid_note_lines']} lines marked for sync"
        )
        add_debug_msg(
            f"Final metrics: {stats['total_potential_anki_notes']} potential notes for {stats['unique_students_count']} unique students"
        )

        return remote_deck

    except Exception as e:
        add_debug_msg(f"Error processing remote deck: {e}")
        raise RemoteDeckError(f"Error obtaining remote deck: {str(e)}")


def download_tsv_data(url, timeout=30):
    """
    Downloads TSV data from a URL.
    
    Supports both edition and TSV format URLs, automatically converting when necessary.

    Args:
        url (str): URL for download (can be edition or TSV format)
        timeout (int): Timeout in seconds

    Returns:
        str: TSV data as string

    Raises:
        RemoteDeckError: If there's an error in download
    """
    from .utils import convert_edit_url_to_tsv
    
    try:
        # Convert edition URL to TSV format (if necessary)
        try:
            # If URL is already in TSV format, use directly
            if "/export?format=tsv" in url:
                tsv_url = url
            else:
                tsv_url = convert_edit_url_to_tsv(url)
        except ValueError as e:
            raise RemoteDeckError(f"Invalid URL: {str(e)}")
        
        headers = {"User-Agent": "Mozilla/5.0 (Sheets2Anki) AnkiAddon"}
        request = urllib.request.Request(tsv_url, headers=headers)

        with urllib.request.urlopen(request, timeout=timeout) as response:
            if response.getcode() != 200:
                raise RemoteDeckError(
                    f"HTTP {response.getcode()}: Failed to access URL"
                )

            # Read and decode data
            data = response.read().decode("utf-8")
            return data

    except socket.timeout:
        raise RemoteDeckError(f"Timeout of {timeout}s while accessing the URL")
    except urllib.error.HTTPError as e:
        if e.code == 400:
            raise RemoteDeckError(
                f"HTTP Error 400: The spreadsheet is not publicly accessible.\n\n"
                f"To fix:\n"
                f"1. Open spreadsheet in Google Sheets\n"
                f"2. Click 'Share'\n"
                f"3. Change access to 'Anyone with the link'\n"
                f"4. Set permission to 'Viewer'\n\n"
                f"Alternatively: File → Share → Publish to web"
            )
        else:
            raise RemoteDeckError(f"HTTP Error {e.code}: {e.reason}")
    except urllib.error.URLError as e:

        raise RemoteDeckError(f"URL Error: {str(e.reason)}")
    except Exception as e:
        raise RemoteDeckError(f"Unexpected download error: {str(e)}")


def parse_tsv_data(tsv_data, debug_messages=None):
    """
    Parses TSV data and returns processed structure.

    Args:
        tsv_data (str): TSV data as string
        debug_messages (list, optional): Debug list

    Returns:
        dict: Processed data with headers and rows

    Raises:
        RemoteDeckError: If there's an error in parsing
    """

    def add_debug_msg(message, category="TSV_PARSE"):
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] [{category}] {message}"
        if debug_messages is not None:
            debug_messages.append(formatted_msg)

    try:
        # Use csv.reader for TSV parsing
        lines = tsv_data.strip().split("\n")
        if not lines:
            raise RemoteDeckError("Empty TSV data")

        reader = csv.reader(lines, delimiter="\t")
        rows = list(reader)

        if not rows:
            raise RemoteDeckError("No rows found in TSV data")

        # First row is headers
        headers = rows[0]
        data_rows = rows[1:]

        add_debug_msg(f"Headers found: {len(headers)}")
        add_debug_msg(f"Data rows: {len(data_rows)}")

        # Validate mandatory headers (only ID and MATCH are really mandatory)
        required_headers = [cols.identifier, cols.answer]
        missing_headers = [h for h in required_headers if h not in headers]

        if missing_headers:
            raise RemoteDeckError(f"Mandatory headers missing: {missing_headers}")

        return {"headers": headers, "rows": data_rows}

    except csv.Error as e:
        raise RemoteDeckError(f"Error processing TSV data: {e}")
    except Exception as e:
        raise RemoteDeckError(f"Unexpected parsing error: {e}")


def build_remote_deck_from_tsv(
    parsed_data, url, enabled_students=None, debug_messages=None
):
    """
    Builds RemoteDeck object from processed TSV data.

    Args:
        parsed_data (dict): Processed TSV data
        url (str): Source URL
        enabled_students (list, optional): List of enabled students
        debug_messages (list, optional): Debug list

    Returns:
        RemoteDeck: Built remote deck object
    """

    def add_debug_msg(message, category="DECK_BUILD"):
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] [{category}] {message}"
        if debug_messages is not None:
            debug_messages.append(formatted_msg)

    headers = parsed_data["headers"]
    rows = parsed_data["rows"]

    # Create remote deck
    remote_deck = RemoteDeck(url=url)
    remote_deck.headers = headers

    # Process each row
    for row_index, row in enumerate(rows):
        try:
            # Create note dictionary
            note_data = {}

            # Fill fields based on headers
            for col_index, header in enumerate(headers):
                if col_index < len(row):
                    note_data[header] = row[col_index].strip()
                else:
                    note_data[header] = ""

            # ALWAYS add to deck for correct metrics accounting
            # Empty ID validation will be done inside add_note() method
            remote_deck.add_note(note_data)

            # Validate if it's a processable note (only ID is mandatory)
            if not note_data.get(cols.identifier):
                add_debug_msg(
                    f"Row {row_index + 2}: invalid note (empty ID)"
                )
                continue

            # Check if it should sync
            sync_value = str(note_data.get(cols.is_sync, "")).strip().lower()
            if sync_value not in ["true", "1", "yes", "sim"]:
                add_debug_msg(f"Row {row_index + 2}: note not marked for sync")
                continue

            # Check student filter
            if enabled_students:
                note_students = note_data.get(cols.students, "").strip()
                if note_students:
                    # Check if any enabled student is in the note
                    students_list = [s.strip() for s in note_students.split(",")]
                    if not any(
                        student in enabled_students for student in students_list
                    ):
                        add_debug_msg(f"Row {row_index + 2}: note filtered by student")
                        continue

            # Additional processing of fields for valid notes
            process_note_fields(note_data)

        except Exception as e:
            add_debug_msg(f"Error processing row {row_index + 2}: {e}")
            continue

    # Update enabled students information
    if enabled_students:
        remote_deck.enabled_students = set(enabled_students)

    # Finalize calculation of metrics
    remote_deck.finalize_metrics()

    # Validate consistency of calculated metrics
    try:
        remote_deck.validate_metrics()
        add_debug_msg("✅ Metrics validated - all consistent")
    except ValueError as e:
        add_debug_msg(f"⚠️ Metrics inconsistency: {e}")

    stats = remote_deck.get_statistics()
    add_debug_msg(
        f"Final deck: {stats['sync_marked_lines']} lines marked for sync, {stats['total_potential_anki_notes']} potential Anki notes"
    )

    return remote_deck


def process_note_fields(note_data):
    """
    Processes special note fields.

    Args:
        note_data (dict): Note data to process
    """
    # IMPORTANT: DO NOT add DEFAULT values directly to note data
    # DEFAULT values are used only for internal logic (ex: subdeck creation)
    # but should not appear on real Anki notes

    # Create hierarchical tags (uses original values or DEFAULT only for internal logic)
    tags = create_tags_from_fields(note_data)
    note_data["tags"] = tags


def create_tags_from_fields(note_data):
    """
    Creates hierarchical tag system from note fields.

    Structure of created tags (all nested under 'Sheets2Anki'):
    1. topics::topic::subtopic::concept: Full nested hierarchy
    2. concepts: Direct concept tags (for easy search)
    3. examination_boards: Tags for each examination board
    4. years: Tags for each test year
    5. careers: Tags for each career
    6. importance: Importance level tag
    7. additionals: Extra tags from the ADDITIONAL TAGS field

    Note: Student tags were removed to simplify logic

    Args:
        note_data (dict): Note data

    Returns:
        list: List of hierarchical tags
    """
    tags = []

    # Root tag
    tags.append(TAG_ROOT)

    def clean_tag_text(text):
        """Cleans text for use as Anki tag - always returns lowercase"""
        if not text or not isinstance(text, str):
            return ""
        # Remove extra spaces, replace spaces with underscores and problematic characters
        cleaned = text.strip().replace(" ", "_").replace(":", "_").replace(";", "_")
        # Remove special characters that may cause issues in Anki, but allow brackets
        cleaned = re.sub(r"[^\w\-_\[\]]", "", cleaned)
        # Always return lowercase for consistency (Anki tags are case-insensitive)
        return cleaned.lower()

    # 1. STUDENT tags - REMOVED to simplify logic
    # (Student tags were eliminated as requested)

    # 2. TOPIC::SUBTOPIC::CONCEPT hierarchical tags (single values, NOT lists)
    topico = note_data.get(cols.hierarchy_2, "").strip()
    subtopico = note_data.get(cols.hierarchy_3, "").strip()
    conceito = note_data.get(cols.hierarchy_4, "").strip()

    # Use default values if empty
    if not topico:
        topico = DEFAULT_TOPIC
    if not subtopico:
        subtopico = DEFAULT_SUBTOPIC
    if not conceito:
        conceito = DEFAULT_CONCEPT

    # Clean for tag use (single values, not lists)
    topico_clean = clean_tag_text(topico)
    subtopico_clean = clean_tag_text(subtopico)
    conceito_clean = clean_tag_text(conceito)
    
    # If cleaning results in empty string (e.g., field had only invalid characters),
    # use the default placeholder to ensure tags are always generated
    if not topico_clean:
        topico_clean = clean_tag_text(DEFAULT_TOPIC)
    if not subtopico_clean:
        subtopico_clean = clean_tag_text(DEFAULT_SUBTOPIC)
    if not conceito_clean:
        conceito_clean = clean_tag_text(DEFAULT_CONCEPT)

    # Generate hierarchical tag - format: Sheets2Anki::Topics::topic::subtopic::concept
    tags.append(
        f"{TAG_ROOT}::{TAG_TOPICS}::{topico_clean}::{subtopico_clean}::{conceito_clean}"
    )

    # 3. Direct CONCEPT tag (for easy search)
    tags.append(f"{TAG_ROOT}::{TAG_CONCEPTS}::{conceito_clean}")

    # 4. EXAMINATION BOARD tags (supports comma-separated list)
    bancas = note_data.get(cols.tags_1, "").strip()
    if bancas:
        for banca in bancas.split(","):
            banca_clean = clean_tag_text(banca)
            if banca_clean:
                tags.append(f"{TAG_ROOT}::{TAG_EXAM_BOARDS}::{banca_clean}")

    # 5. YEAR tag (single value, NOT list - represents LAST year in exam)
    ano = note_data.get(cols.tags_2, "").strip()
    if ano:
        ano_clean = clean_tag_text(ano)
        if ano_clean:
            tags.append(f"{TAG_ROOT}::{TAG_YEARS}::{ano_clean}")

    # 6. CAREER tags (supports comma-separated list)
    carreira = note_data.get(cols.tags_3, "").strip()
    if carreira:
        for carr in carreira.split(","):
            carr_clean = clean_tag_text(carr)
            if carr_clean:
                tags.append(f"{TAG_ROOT}::{TAG_CAREERS}::{carr_clean}")

    # 7. IMPORTANCE tags (single value, NOT list)
    importancia = note_data.get(cols.hierarchy_1, "").strip()
    
    if not importancia:
        importancia = DEFAULT_IMPORTANCE
        
    importancia_clean = clean_tag_text(importancia)
    
    # If cleaning results in empty string (e.g., field had only invalid characters),
    # use the default placeholder to ensure importance tag is always generated
    if not importancia_clean:
        importancia_clean = clean_tag_text(DEFAULT_IMPORTANCE)
        
    tags.append(f"{TAG_ROOT}::{TAG_IMPORTANCE}::{importancia_clean}")

    # 8. ADDITIONAL tags (supports comma and semicolon separated list)
    tags_adicionais = note_data.get(cols.tags_4, "").strip()
    if tags_adicionais:
        # Supports both comma and semicolon separation
        separadores = [",", ";"]
        for sep in separadores:
            if sep in tags_adicionais:
                tags_list = tags_adicionais.split(sep)
                break
        else:
            tags_list = [tags_adicionais]

        for tag in tags_list:
            tag_clean = clean_tag_text(tag)
            if tag_clean:
                tags.append(f"{TAG_ROOT}::{TAG_ADDITIONAL}::{tag_clean}")

    return tags


def has_cloze_deletion(text):
    """
    Checks if a text contains Anki cloze formatting.

    Args:
        text (str): Text to check

    Returns:
        bool: True if it contains cloze, False otherwise
    """
    if not text or not isinstance(text, str):
        return False

    # Pattern to detect cloze: {{c1::text}} or {{c1::text::hint}}
    cloze_pattern = r"\{\{c\d+::[^}]+\}\}"
    return bool(re.search(cloze_pattern, text))


# =============================================================================
# NOTE PROCESSING FUNCTIONS
# =============================================================================


def create_or_update_notes(
    col, remoteDeck, deck_id, deck_url=None, debug_messages=None
):
    """
    Creates or updates notes in the deck based on remote data.

    REFACTORED LOGIC:
    - Each remote spreadsheet row with unique ID generates a note for each student in the STUDENTS column
    - The unique identifier for each note is formed by "{student}_{id}"
    - This string should never be modified after note creation
    - The user controls which students should have their notes synchronized

    Args:
        col: Anki collection object
        remoteDeck (RemoteDeck): Remote deck object containing sync data
        deck_id (int): Anki deck ID to sync
        deck_url (str, optional): Deck URL to manage students

    Returns:
        dict: Sync statistics containing counts for created, updated,
              deleted notes and errors

    Raises:
        SyncError: If there are critical errors during synchronization
        CollectionSaveError: If saving collection fails
    """

    def add_debug_msg(message, category="NOTE_PROCESSOR"):
        """Helper to add debug messages using global system."""
        from .utils import add_debug_message

        add_debug_message(message, category)

    add_debug_msg("🔧 Starting note synchronization with refactored logic")
    add_debug_msg(f"🔧 remoteDeck contains {len(remoteDeck.notes)} notes")

    # Import SyncStats
    from .sync import SyncStats

    # Create statistics object with refactored metrics
    stats = SyncStats()

    # Copy metrics already calculated from RemoteDeck
    deck_stats = remoteDeck.get_statistics()
    stats.remote_total_table_lines = deck_stats["total_table_lines"]
    stats.remote_valid_note_lines = deck_stats["valid_note_lines"]
    stats.remote_invalid_note_lines = deck_stats["invalid_note_lines"]
    stats.remote_ignored_ghost_rows = deck_stats.get("ignored_ghost_rows", 0)
    stats.remote_sync_marked_lines = deck_stats["sync_marked_lines"]
    stats.remote_total_potential_anki_notes = deck_stats["total_potential_anki_notes"]
    stats.remote_potential_student_notes = deck_stats["potential_student_notes"]
    stats.remote_potential_missing_students_notes = deck_stats["potential_missing_students_notes"]
    stats.remote_unique_students_count = deck_stats["unique_students_count"]
    stats.remote_notes_per_student = deck_stats["notes_per_student"].copy()

    try:
        # 1. Obtain enabled students from configuration system
        from .config_manager import get_enabled_students
        from .config_manager import is_sync_missing_students_notes

        enabled_students = set(get_enabled_students() or [])

        # 2. Check if [MISSING STUDENTS] feature should be included
        sync_missing_students = is_sync_missing_students_notes()

        add_debug_msg(f"Enabled students in system: {sorted(enabled_students)}")
        add_debug_msg(
            f"Synchronize notes without specific students ({DEFAULT_STUDENT}): {sync_missing_students}"
        )

        # 3. Include [MISSING S.] in "students" list if feature is active
        effective_students = enabled_students.copy()
        if sync_missing_students:
            effective_students.add(DEFAULT_STUDENT)
            add_debug_msg(
                f"Including {DEFAULT_STUDENT} as effective student for synchronization"
            )

        if not enabled_students and not sync_missing_students:
            add_debug_msg(
                f"⚠️ No enabled students and {DEFAULT_STUDENT} disabled - no notes will be synchronized"
            )
            return stats

        # 4. Create set of all expected student_note_ids for synchronization
        expected_student_note_ids = set()

        for note_data in remoteDeck.notes:
            note_id = note_data.get(cols.identifier, "").strip()

            # Skip invalid lines (empty ID)
            if not note_id:
                continue

            # Check if this note should sync
            sync_value = str(note_data.get(cols.is_sync, "")).strip().lower()
            if sync_value not in ["true", "1", "yes", "sim"]:
                continue

            # Obtain students list for this note
            alunos_str = note_data.get(cols.students, "").strip()
            if not alunos_str:
                # Note without specific students - check [MISSING S.]
                if sync_missing_students:
                    student_note_id = f"{DEFAULT_STUDENT}_{note_id}"
                    expected_student_note_ids.add(student_note_id)
                    add_debug_msg(
                        f"Note {note_id}: no specific students, including as {DEFAULT_STUDENT}"
                    )
                else:
                    add_debug_msg(
                        f"Note {note_id}: no specific students, skipping (feature disabled)"
                    )
                continue

            # Extract individual students (comma separated)
            students_in_note = [s.strip() for s in alunos_str.split(",") if s.strip()]

            # For each enabled student in this note
            for student in students_in_note:
                if student in enabled_students:
                    # Create unique ID student_id
                    student_note_id = f"{student}_{note_id}"
                    expected_student_note_ids.add(student_note_id)

        add_debug_msg("=== REMOTE DECK METRICS - REFACTORED ===")
        add_debug_msg(f"📊 Total table lines: {stats.remote_total_table_lines}")
        add_debug_msg(
            f"✅ Valid lines (filled ID): {stats.remote_valid_note_lines}"
        )
        add_debug_msg(
            f"❌ Invalid lines (empty ID): {stats.remote_invalid_note_lines}"
        )
        add_debug_msg(f"🔄 Lines marked for sync: {stats.remote_sync_marked_lines}")
        add_debug_msg(
            f"🚀 Total potential notes in Anki: {stats.remote_total_potential_anki_notes}"
        )
        add_debug_msg(
            f"🎓 Potential notes for specific students: {stats.remote_potential_student_notes}"
        )
        add_debug_msg(
            f"👤 Potential notes for [MISSING STUDENTS]: {stats.remote_potential_missing_students_notes}"
        )
        add_debug_msg(
            f"👥 Total unique students: {stats.remote_unique_students_count}"
        )
        add_debug_msg(f"📋 Notes per student: {dict(stats.remote_notes_per_student)}")
        add_debug_msg(
            f"🎯 Total student_note_ids for synchronization: {len(expected_student_note_ids)}"
        )

        # 3. Ensure note types exist for all necessary students
        students_to_create_note_types = set()
        for student_note_id in expected_student_note_ids:
            if student_note_id.startswith(DEFAULT_STUDENT + "_"):
                student = DEFAULT_STUDENT
            else:
                student = student_note_id.split("_")[0]  # First element before "_"
            students_to_create_note_types.add(student)

        add_debug_msg(
            f"Creating note types for students: {sorted(students_to_create_note_types)}"
        )
        for student in students_to_create_note_types:
            ensure_custom_models(
                col, deck_url, student=student, debug_messages=debug_messages
            )

        # 4. Get existing notes by student_note_id
        existing_notes = get_existing_notes_by_student_id(col, deck_id)
        add_debug_msg(f"Found {len(existing_notes)} existing notes in deck")

        # 5. Process each remote note for each student
        for note_data in remoteDeck.notes:
            note_id = note_data.get(cols.identifier, "").strip()
            if not note_id:
                # Empty ID line is not an error, it's a normal situation already accounted for in metrics
                continue

            # Check if it should sync
            sync_value = str(note_data.get(cols.is_sync, "")).strip().lower()
            if sync_value not in ["true", "1", "yes", "sim"]:
                stats.skipped += 1
                continue

            # Obtain note students list
            alunos_str = note_data.get(cols.students, "").strip()

            if not alunos_str:
                # Note without specific students - check if it should process as [MISSING S.]
                if sync_missing_students:
                    # Process as [MISSING STUDENTS]
                    student = DEFAULT_STUDENT
                    student_note_id = f"{student}_{note_id}"
                    add_debug_msg(
                        f"Note {note_id}: no specific students, processing as {DEFAULT_STUDENT}"
                    )

                    try:
                        if student_note_id in existing_notes:
                            # Update existing note
                            success, was_updated, changes = (
                                update_existing_note_for_student(
                                    col,
                                    existing_notes[student_note_id],
                                    note_data,
                                    student,
                                    deck_url,
                                    debug_messages,
                                )
                            )
                            if success:
                                if was_updated:
                                    stats.updated += 1
                                    # Capture update details
                                    update_detail = {
                                        "student_note_id": student_note_id,
                                        "student": student,
                                        "note_id": note_data.get(cols.identifier, "").strip(),
                                        "changes": changes,
                                    }
                                    stats.update_details.append(update_detail)
                                    add_debug_msg(
                                        f"✅ [MISSING STUDENTS] note updated: {student_note_id}"
                                    )
                                else:
                                    stats.unchanged += 1
                                    add_debug_msg(
                                        f"⏭️ [MISSING STUDENTS] note unchanged: {student_note_id}"
                                    )
                            else:
                                stats.add_error(f"Error updating [MISSING STUDENTS] note: {student_note_id}")
                                add_debug_msg(
                                    f"❌ Error updating [MISSING STUDENTS] note: {student_note_id}"
                                )
                        else:
                            # Create new note
                            if create_new_note_for_student(
                                col,
                                note_data,
                                student,
                                deck_id,
                                deck_url,
                                debug_messages,
                            ):
                                stats.created += 1
                                # Capture creation details
                                creation_detail = {
                                    "student_note_id": f"{student}_{note_data.get(cols.identifier, '').strip()}",
                                    "student": student,
                                    "note_id": note_data.get(cols.identifier, "").strip(),
                                    "pergunta": note_data.get(cols.question, "")[:100]
                                    + (
                                        "..."
                                        if len(note_data.get(cols.question, "")) > 100
                                        else ""
                                    ),
                                }
                                stats.creation_details.append(creation_detail)
                                add_debug_msg(
                                    f"✅ [MISSING STUDENTS] note created: {student_note_id}"
                                )
                            else:
                                stats.add_error(f"Error creating [MISSING STUDENTS] note: {student_note_id}")
                                add_debug_msg(
                                    f"❌ Error creating [MISSING STUDENTS] note: {student_note_id}"
                                )

                    except Exception as e:
                        import traceback

                        error_details = traceback.format_exc()
                        add_debug_msg(f"❌ Error processing {student_note_id}: {e}")
                        add_debug_msg(f"❌ Stack trace: {error_details}")
                        stats.add_error(f"Exception processing {student_note_id}: {str(e)}")
                else:
                    # [MISSING STUDENTS] feature disabled
                    stats.skipped += 1
                    add_debug_msg(
                        f"Note {note_id}: no students defined, skipping ([MISSING STUDENTS] feature disabled)"
                    )
                continue

            # Process notes with specific students
            students_in_note = [s.strip() for s in alunos_str.split(",") if s.strip()]

            # Process each enabled student
            for student in students_in_note:
                if student not in enabled_students:
                    continue  # Student not enabled

                # Create unique ID for this combination
                student_note_id = f"{student}_{note_id}"

                try:
                    if student_note_id in existing_notes:
                        # Update existing note
                        success, was_updated, changes = (
                            update_existing_note_for_student(
                                col,
                                existing_notes[student_note_id],
                                note_data,
                                student,
                                deck_url,
                                debug_messages,
                            )
                        )
                        if success:
                            if was_updated:
                                stats.updated += 1
                                # Capture update details
                                update_detail = {
                                    "student_note_id": student_note_id,
                                    "student": student,
                                    "note_id": note_data.get(cols.identifier, "").strip(),
                                    "changes": changes,
                                }
                                stats.update_details.append(update_detail)
                                add_debug_msg(f"✅ Note updated: {student_note_id}")
                            else:
                                stats.unchanged += 1
                                add_debug_msg(f"⏭️ Note unchanged: {student_note_id}")
                        else:
                            stats.add_error(f"Error updating note: {student_note_id}")
                            add_debug_msg(
                                f"❌ Error updating note: {student_note_id}"
                            )
                    else:
                        # Create new note
                        if create_new_note_for_student(
                            col, note_data, student, deck_id, deck_url, debug_messages
                        ):
                            stats.created += 1
                            # Capture creation details
                            creation_detail = {
                                "student_note_id": student_note_id,
                                "student": student,
                                "note_id": note_data.get(cols.identifier, "").strip(),
                                "pergunta": note_data.get(cols.question, "")[:100]
                                + (
                                    "..."
                                    if len(note_data.get(cols.question, "")) > 100
                                    else ""
                                ),
                            }
                            stats.creation_details.append(creation_detail)
                            add_debug_msg(f"✅ Note created: {student_note_id}")
                        else:
                            stats.add_error(f"Error creating note: {student_note_id}")
                            add_debug_msg(f"❌ Error creating note: {student_note_id}")

                except Exception as e:
                    import traceback

                    error_details = traceback.format_exc()
                    add_debug_msg(f"❌ Error processing {student_note_id}: {e}")
                    add_debug_msg(f"❌ Stack trace: {error_details}")
                    stats.add_error(f"Exception processing {student_note_id}: {str(e)}")

        # 6. Separate obsolete notes from disabled students' notes and sync-disabled notes
        all_existing_note_ids = set(existing_notes.keys())
        
        # 6.1. Identify truly obsolete notes (no longer in spreadsheet)
        notes_really_obsolete = set()
        notes_from_disabled_students = set()
        notes_with_sync_disabled = set()  # NEW: Notes with SYNC=false should be preserved
        
        for student_note_id in all_existing_note_ids - expected_student_note_ids:
            # Extract note information
            if "_" not in student_note_id:
                notes_really_obsolete.add(student_note_id)
                continue
                
            if student_note_id.startswith(DEFAULT_STUDENT + "_"):
                student_name = DEFAULT_STUDENT
                note_id = student_note_id[len(DEFAULT_STUDENT) + 1:]
            else:
                student_name = student_note_id.split("_")[0]
                note_id = "_".join(student_note_id.split("_")[1:])
            
            # Check if note still exists in remote spreadsheet and get its sync status
            note_exists_in_remote = False
            note_has_sync_disabled = False
            for note_data in remoteDeck.notes:
                remote_note_id = note_data.get(cols.identifier, "").strip()
                if remote_note_id == note_id:
                    note_exists_in_remote = True
                    # Check if SYNC is explicitly disabled for this note
                    sync_value = str(note_data.get(cols.is_sync, "")).strip().lower()
                    if sync_value not in ["true", "1", "yes", "sim"]:
                        note_has_sync_disabled = True
                    break
            
            if not note_exists_in_remote:
                # Note truly no longer exists in spreadsheet
                notes_really_obsolete.add(student_note_id)
                add_debug_msg(f"📝 Obsolete note (removed from spreadsheet): {student_note_id}")
            elif note_has_sync_disabled:
                # Note exists but SYNC=false - ALWAYS preserve (user intentionally disabled sync)
                notes_with_sync_disabled.add(student_note_id)
                add_debug_msg(f"⏸️ Note with SYNC disabled (preserving): {student_note_id}")
            else:
                # Note exists in spreadsheet with SYNC=true, but student was disabled
                notes_from_disabled_students.add(student_note_id)
                add_debug_msg(f"👤 Note from disabled student: {student_note_id} (student: {student_name})")
        
        # 6.2. Remove truly obsolete notes (always removes)
        add_debug_msg(f"🗑️ Removing {len(notes_really_obsolete)} obsolete notes (no longer in spreadsheet)")
        for student_note_id in notes_really_obsolete:
            try:
                note_to_delete = existing_notes[student_note_id]
                if delete_note_by_id(col, note_to_delete):
                    stats.deleted += 1
                    # Extract question text for better logging
                    pergunta = ""
                    try:
                        if cols.question in note_to_delete.keys():
                            full_pergunta = note_to_delete[cols.question]
                            pergunta = full_pergunta[:100] + ("..." if len(full_pergunta) > 100 else "")
                    except:
                        pass
                    # Capture deletion details
                    deletion_detail = {
                        "student_note_id": student_note_id,
                        "student": (
                            DEFAULT_STUDENT 
                            if student_note_id.startswith(DEFAULT_STUDENT + "_")
                            else (
                                student_note_id.split("_")[0]
                                if "_" in student_note_id
                                else "Unknown"
                            )
                        ),
                        "note_id": (
                            student_note_id[len(DEFAULT_STUDENT) + 1:]
                            if student_note_id.startswith(DEFAULT_STUDENT + "_")
                            else (
                                "_".join(student_note_id.split("_")[1:])
                                if "_" in student_note_id
                                else student_note_id
                            )
                        ),
                        "reason": "obsolete",
                        "pergunta": pergunta
                    }
                    stats.deletion_details.append(deletion_detail)
                    add_debug_msg(f"✅ Obsolete note removed: {student_note_id}")
            except Exception as e:
                add_debug_msg(f"❌ Error removing obsolete note {student_note_id}: {e}")
                stats.add_error(f"Error removing obsolete note {student_note_id}: {str(e)}")
        
        # 6.3. Check if disabled students' notes should be removed
        from .config_manager import is_auto_remove_disabled_students
        
        if notes_from_disabled_students:
            if is_auto_remove_disabled_students():
                add_debug_msg(f"🔧 Auto-removal ON: removing {len(notes_from_disabled_students)} notes from disabled students")
                for student_note_id in notes_from_disabled_students:
                    try:
                        note_to_delete = existing_notes[student_note_id]
                        if delete_note_by_id(col, note_to_delete):
                            stats.deleted += 1
                            # Extract question text for better logging
                            pergunta = ""
                            try:
                                if cols.question in note_to_delete.keys():
                                    full_pergunta = note_to_delete[cols.question]
                                    pergunta = full_pergunta[:100] + ("..." if len(full_pergunta) > 100 else "")
                            except:
                                pass
                            # Capture deletion details
                            deletion_detail = {
                                "student_note_id": student_note_id,
                                "student": (
                                    DEFAULT_STUDENT 
                                    if student_note_id.startswith(DEFAULT_STUDENT + "_")
                                    else (
                                        student_note_id.split("_")[0]
                                        if "_" in student_note_id
                                        else "Unknown"
                                    )
                                ),
                                "note_id": (
                                    student_note_id[len(DEFAULT_STUDENT) + 1:]
                                    if student_note_id.startswith(DEFAULT_STUDENT + "_")
                                    else (
                                        "_".join(student_note_id.split("_")[1:])
                                        if "_" in student_note_id
                                        else student_note_id
                                    )
                                ),
                                "reason": "disabled_student",
                                "pergunta": pergunta
                            }
                            stats.deletion_details.append(deletion_detail)
                            add_debug_msg(f"✅ Note from disabled student removed: {student_note_id}")
                    except Exception as e:
                        add_debug_msg(f"❌ Error removing note from disabled student {student_note_id}: {e}")
                        stats.add_error(f"Error removing note from disabled student {student_note_id}: {str(e)}")
            else:
                add_debug_msg(f"🛡️ Auto-removal OFF: preserving {len(notes_from_disabled_students)} notes from disabled students")
                for student_note_id in notes_from_disabled_students:
                    if student_note_id.startswith(DEFAULT_STUDENT + "_"):
                        student_name = DEFAULT_STUDENT
                    else:
                        student_name = student_note_id.split("_")[0] if "_" in student_note_id else "Unknown"
                    add_debug_msg(f"🛡️ Preserving note: {student_note_id} (student: {student_name})")

        # 6.4. Log sync-disabled notes (always preserved)
        if notes_with_sync_disabled:
            add_debug_msg(f"⏸️ Preserving {len(notes_with_sync_disabled)} notes with SYNC disabled (user choice)")
            for student_note_id in notes_with_sync_disabled:
                add_debug_msg(f"⏸️ SYNC disabled, preserving: {student_note_id}")

        # 7. Final statistics
        add_debug_msg("=== FINAL STATISTICS ===")
        add_debug_msg(f"✅ Notes created: {stats.created}")
        add_debug_msg(f"🔄 Notes updated: {stats.updated}")
        add_debug_msg(f"🗑️ Notes removed: {stats.deleted}")
        add_debug_msg(f"⏭️ Notes unchanged: {stats.unchanged}")
        add_debug_msg(f"⏸️ Notes ignored: {stats.skipped}")
        add_debug_msg(f"❌ Errors: {stats.errors}")

        # 8. Save changes
        try:
            col.save()
            add_debug_msg("Collection saved successfully")
        except Exception as e:
            raise CollectionSaveError(f"Failed to save collection: {e}")

        add_debug_msg(
            f"🎯 Synchronization complete: +{stats.created} ~{stats.updated} ={stats.unchanged} -{stats.deleted} !{stats.errors}"
        )

        return stats

    except Exception as e:
        import traceback

        error_details = traceback.format_exc()
        add_debug_msg(f"❌ CRITICAL ERROR in synchronization: {e}")
        add_debug_msg(f"❌ Full stack trace: {error_details}")

        # Return stats with error
        if stats.remote_total_table_lines == 0:
            stats.remote_total_table_lines = (
                len(remoteDeck.notes) if remoteDeck and remoteDeck.notes else 0
            )
        stats.add_error(f"Critical error in synchronization: {str(e)}")
        # Ensure at least 1 error is counted even if add_error logic changes
        if stats.errors == 0:
            stats.errors = 1
        return stats


def get_existing_notes_by_student_id(col, deck_id):
    """
    Obtains mapping of existing notes in the deck by student_note_id.

    REFACTORED LOGIC:
    - Search for all notes in the deck and subdecks
    - For each note, extract the note ID from the ID field
    - Derives the student from the name of the subdeck where the note is located
    - Creates the student_note_id as "{student}_{note_id}"
    - Returns mapping {student_note_id: note_object}

    Args:
        col: Anki collection
        deck_id (int): Deck ID

    Returns:
        dict: Mapping {student_note_id: note_object} where student_note_id = "student_note_id"
    """
    existing_notes = {}

    try:
        # Get the main deck
        deck = col.decks.get(deck_id)
        if not deck:
            return existing_notes

        deck_name = deck["name"]

        # Search for cards in the main deck AND in all subdecks
        # Escape double quotes in deck name to avoid search errors
        escaped_deck_name = deck_name.replace('"', '\\"')
        search_query = f'deck:"{escaped_deck_name}" OR deck:"{escaped_deck_name}::*"'
        
        # Check if query is not empty or malformed
        if not deck_name.strip():
            add_debug_msg(f"[DECK_SEARCH] Error: Deck name is empty, using ID search", category="DECK_BUILD")
            search_query = f'deck:{deck_id}'
        
        card_ids = col.find_cards(search_query)

        for card_id in card_ids:
            try:
                card = col.get_card(card_id)
                note = card.note()

                # Get note ID from ID field
                note_fields = note.keys()
                if cols.identifier in note_fields:
                    full_note_id = note[cols.identifier].strip()
                    if full_note_id:
                        # The ID field already contains the "{student}_{note_id}" format after refactoring
                        # Check if it has the expected format
                        if "_" in full_note_id:
                            # Use note ID directly as student_note_id
                            student_note_id = full_note_id
                            existing_notes[student_note_id] = note
                        else:
                            # Old format - try to extract from subdeck as fallback
                            card_deck = col.decks.get(card.did)
                            if card_deck:
                                subdeck_name = card_deck["name"]
                                # Expected structure: Sheets2Anki::Remote::Student::Importance::...
                                deck_parts = subdeck_name.split("::")
                                if len(deck_parts) >= 3:
                                    student = deck_parts[
                                        2
                                    ]  # Third element is the student
                                    student_note_id = f"{student}_{full_note_id}"
                                    existing_notes[student_note_id] = note

            except Exception as e:
                add_debug_msg(f"Error processing card {card_id}: {e}", category="DECK_SEARCH")
                continue

    except Exception as e:
        add_debug_msg(f"Error obtaining existing notes: {e}", category="DECK_SEARCH")

    return existing_notes


def create_new_note_for_student(
    col, note_data, student, deck_id, deck_url, debug_messages=None
):
    """
    Creates a new Anki note for a specific student.

    Args:
        col: Anki collection
        note_data (dict): Spreadsheet note data
        student (str): Student name
        deck_id (int): Base deck ID
        deck_url (str): Remote deck URL
        debug_messages (list, optional): Debug list

    Returns:
        bool: True if created successfully, False otherwise
    """

    def add_debug_msg(message, category="CREATE_NOTE_STUDENT"):
        """Helper to add debug messages using global system."""
        from .utils import add_debug_message

        add_debug_message(message, category)

    try:
        note_id = note_data.get(cols.identifier, "").strip()
        add_debug_msg(f"Creating new note for student {student}: {note_id}")

        # Determine note type (cloze or basic)
        pergunta = note_data.get(cols.question, "")
        is_cloze = has_cloze_deletion(pergunta)

        # Get appropriate model for the specific student
        from .config_manager import get_deck_remote_name
        from .utils import get_note_type_name

        remote_deck_name = get_deck_remote_name(deck_url)
        note_type_name = get_note_type_name(
            deck_url, remote_deck_name, student=student, is_cloze=is_cloze
        )

        add_debug_msg(f"Note type for {student}: {note_type_name}")

        model = col.models.by_name(note_type_name)
        if not model:
            add_debug_msg(
                f"❌ ERROR: Model not found: '{note_type_name}' for student: {student}"
            )
            add_debug_msg(f"❌ Attempting to create note type for note: {note_id}")
            # Attempt to create model if it doesn't exist
            from .templates_and_definitions import ensure_custom_models

            models = ensure_custom_models(
                col, deck_url, student=student, debug_messages=debug_messages
            )
            model = models.get("cloze" if is_cloze else "standard")
            if not model:
                add_debug_msg(
                    f"❌ CRITICAL ERROR: Could not create/find model: {note_type_name}"
                )
                return False
            add_debug_msg(f"✅ Model created successfully: {note_type_name}")

        add_debug_msg(
            f"✅ Model found: {note_type_name} (ID: {model['id'] if model else 'None'})"
        )

        # Create note
        note = col.new_note(model)

        # Fill fields with unique identifier for student
        fill_note_fields_for_student(note, note_data, student)

        # Add tags
        tags = note_data.get("tags", [])
        if tags:
            note.tags = tags

        # Determine target deck for specific student
        add_debug_msg(
            f"Determining target deck for note: {note_id}, student: {student}"
        )
        target_deck_id = determine_target_deck_for_student(
            col, deck_id, note_data, student, deck_url, debug_messages
        )
        add_debug_msg(f"Target deck determined: {target_deck_id}")

        # Add note to deck
        add_debug_msg(
            f"Adding note {note_id} of student {student} to deck {target_deck_id}"
        )
        col.add_note(note, target_deck_id)
        add_debug_msg(
            f"✅ Note {note_id} of student {student} successfully added to deck {target_deck_id}"
        )

        add_debug_msg(f"✅ Note successfully created for {student}: {note_id}")
        return True

    except Exception as e:
        import traceback

        error_details = traceback.format_exc()
        add_debug_msg(
            f"❌ ERROR creating note {note_data.get(cols.identifier, 'UNKNOWN')} for {student}: {e}"
        )
        add_debug_msg(f"❌ Stack trace: {error_details}")
        add_debug_msg(
            f"[CREATE_NOTE_ERROR] {note_data.get(cols.identifier, 'UNKNOWN')} for {student}: {e}",
            category="CREATE_NOTE"
        )
        add_debug_msg(f"[CREATE_NOTE_ERROR] Stack trace: {error_details}", category="CREATE_NOTE")
        return False


def note_fields_need_update(existing_note, new_data, debug_messages=None, student=None):
    """
    Checks if a note needs update by comparing fields and tags.

    REFACTORED LOGIC:
    - Considers that the note ID is already in the "{student}_{id}" format
    - For comparison, uses original spreadsheet data for other fields
    - Does not compare the ID field as it is derived and should remain unchanged

    Args:
        existing_note: Existing Anki note
        new_data (dict): New note data
        debug_messages (list, optional): Debug list
        student (str, optional): Student name to form unique ID for comparison

    Returns:
        tuple: (needs_update: bool, changes: list)
    """

    def add_debug_msg(message, category="NOTE_COMPARISON"):
        """Helper to add debug messages using global system."""
        from .utils import add_debug_message

        add_debug_message(message, category)

    changes = []

    # Compare fields (excluding derived ID)
    # The ID in existing note is already in the "{student}_{id}" format and should not be compared
    # CORRECTION: Use real field names in Anki (which are the same as spreadsheet)
    for field_key, field_anki_name in [
        (cols.question, cols.question),
        (cols.answer, cols.answer),
        (cols.info_1, cols.info_1),
        (cols.info_2, cols.info_2),
        (cols.multimedia_1, cols.multimedia_1),
        (cols.multimedia_2, cols.multimedia_2),
        (cols.example_1, cols.example_1),
        (cols.example_2, cols.example_2),
        (cols.mnemonic, cols.mnemonic),
        (cols.hierarchy_1, cols.hierarchy_1),
        (cols.hierarchy_2, cols.hierarchy_2),
        (cols.hierarchy_3, cols.hierarchy_3),
        (cols.hierarchy_4, cols.hierarchy_4),
        (cols.tags_1, cols.tags_1),
        (cols.tags_2, cols.tags_2),
        (cols.tags_3, cols.tags_3),
        (cols.tags_4, cols.tags_4),
        (cols.extra_field_1, cols.extra_field_1),
        (cols.extra_field_2, cols.extra_field_2),
        (cols.extra_field_3, cols.extra_field_3),
    ]:
        if field_anki_name in existing_note:
            old_value = str(existing_note[field_anki_name]).strip()
            new_value = str(new_data.get(field_key, "")).strip()

            if old_value != new_value:
                # Truncate for log if too long
                old_display = (
                    old_value[:50] + "..." if len(old_value) > 50 else old_value
                )
                new_display = (
                    new_value[:50] + "..." if len(new_value) > 50 else new_value
                )
                changes.append(f"{field_anki_name}: '{old_display}' → '{new_display}'")

    # Compare tags (case-insensitive, since Anki treats tags as case-insensitive)
    # This prevents infinite update loops when only the case of a tag changes
    existing_tags = set(existing_note.tags) if hasattr(existing_note, "tags") else set()
    new_tags = set(new_data.get("tags", []))
    
    # Create case-insensitive versions for comparison
    existing_tags_lower = {tag.lower() for tag in existing_tags}
    new_tags_lower = {tag.lower() for tag in new_tags}

    # Detailed tag debug
    add_debug_msg(f"🏷️ Existing tags: {sorted(existing_tags)}")
    add_debug_msg(f"🏷️ New tags: {sorted(new_tags)}")

    # Compare case-insensitively to avoid false positives from case-only changes
    if existing_tags_lower != new_tags_lower:
        # Find truly added tags (not just case changes)
        added_tags_lower = new_tags_lower - existing_tags_lower
        removed_tags_lower = existing_tags_lower - new_tags_lower
        
        # Get the original-cased tags for display
        added_tags = {tag for tag in new_tags if tag.lower() in added_tags_lower}
        removed_tags = {tag for tag in existing_tags if tag.lower() in removed_tags_lower}

        add_debug_msg("🏷️ Different tags detected!")
        if added_tags:
            changes.append(f"Tags added: {', '.join(added_tags)}")
            add_debug_msg(f"🏷️ Added: {sorted(added_tags)}")
        if removed_tags:
            changes.append(f"Tags removed: {', '.join(removed_tags)}")
            add_debug_msg(f"🏷️ Removed: {sorted(removed_tags)}")
    else:
        # Check if there are case-only differences (for logging purposes only)
        if existing_tags != new_tags:
            add_debug_msg("🏷️ Tags differ only in case - treating as identical (Anki is case-insensitive)")
        else:
            add_debug_msg("🏷️ Tags are identical")

    needs_update = len(changes) > 0

    if needs_update:
        add_debug_msg(
            f"Note needs update. Changes detected: {'; '.join(changes)}"
        )
    else:
        add_debug_msg("Note does NOT need update - identical content")

    return needs_update, changes


def update_existing_note_for_student(
    col, existing_note, new_data, student, deck_url, debug_messages=None
):
    """
    Updates an existing note for a specific student.
    IMPORTANT: Only updates if there are real differences between local and remote content.

    Args:
        col: Anki collection
        existing_note: Existing Anki note
        new_data (dict): New note data
        student (str): Student name
        deck_url (str): Deck URL
        debug_messages (list, optional): Debug list

    Returns:
        tuple: (success: bool, was_updated: bool, changes: list)
    """

    def add_debug_msg(message, category="UPDATE_NOTE_STUDENT"):
        """Helper to add debug messages using global system."""
        from .utils import add_debug_message

        add_debug_message(message, category)

    try:
        note_id = new_data.get(cols.identifier, "").strip()
        add_debug_msg(
            f"Checking if note {note_id} needs update for student {student}"
        )

        # Check for real differences between existing note and new data
        needs_update, changes = note_fields_need_update(
            existing_note, new_data, debug_messages, student=student
        )

        if not needs_update:
            add_debug_msg(f"⏭️ Note {note_id} was not updated - identical content")
            return True, False, []  # Success, but not updated, no changes

        add_debug_msg(
            f"📝 Updating note {note_id} with changes: {'; '.join(changes[:3])}..."
        )

        # Fill fields with new data (using unique identifier for student)
        fill_note_fields_for_student(existing_note, new_data, student)

        # Update tags
        tags = new_data.get("tags", [])
        if tags:
            existing_note.tags = tags

        # Check if needs moving to different subdeck
        cards = existing_note.cards()
        if cards:
            current_deck_id = cards[0].did
            target_deck_id = determine_target_deck_for_student(
                col, current_deck_id, new_data, student, deck_url, debug_messages
            )

            if current_deck_id != target_deck_id:
                # Move cards to new deck
                for card in cards:
                    card.did = target_deck_id
                    col.update_card(card)

        # Save note changes
        existing_note.flush()

        add_debug_msg(f"✅ Note successfully updated for {student}: {note_id}")
        return True, True, changes  # Success, was updated, with changes list

    except Exception as e:
        add_debug_msg(f"❌ Error updating note for {student}: {e}")
        return False, False, []  # Error, no changes


def delete_note_by_id(col, note):
    """
    Removes a note from Anki.

    Args:
        col: Anki collection
        note: Note to be removed

    Returns:
        bool: True if removed successfully, False otherwise
    """
    try:
        col.remove_notes([note.id])
        return True
    except Exception as e:
        add_debug_msg(f"Error deleting note {note.id}: {e}", category="NOTE_PROCESSOR")
        return False


def fill_note_fields_for_student(note, note_data, student):
    """
    Fills note fields with spreadsheet data for a specific student.

    REFACTORED LOGIC:
    - Anki note ID field will be filled with "{student}_{id}"
    - This unique identifier should never be modified after creation
    - All other fields are filled normally from spreadsheet data

    Args:
        note: Anki note
        note_data (dict): Spreadsheet data
        student (str): Student name to form unique ID
    """
    # Get original spreadsheet ID
    original_id = note_data.get(cols.identifier, "").strip()

    # Create unique identifier for this student-note combination
    unique_student_note_id = f"{student}_{original_id}"

    # Field mapping with special treatment for ID
    field_mappings = {
        cols.identifier: unique_student_note_id,  # Unique ID per student
        cols.question: note_data.get(cols.question, "").strip(),
        cols.answer: note_data.get(cols.answer, "").strip(),
        cols.hierarchy_1: note_data.get(cols.hierarchy_1, "").strip(),
        cols.hierarchy_2: note_data.get(cols.hierarchy_2, "").strip(),
        cols.hierarchy_3: note_data.get(cols.hierarchy_3, "").strip(),
        cols.hierarchy_4: note_data.get(cols.hierarchy_4, "").strip(),
        cols.info_1: note_data.get(cols.info_1, "").strip(),
        cols.info_2: note_data.get(cols.info_2, "").strip(),
        cols.multimedia_1: note_data.get(cols.multimedia_1, "").strip(),
        cols.multimedia_2: note_data.get(cols.multimedia_2, "").strip(),
        cols.example_1: note_data.get(cols.example_1, "").strip(),
        cols.example_2: note_data.get(cols.example_2, "").strip(),
        cols.mnemonic: note_data.get(cols.mnemonic, "").strip(),
        # Metadata fields
        cols.tags_1: note_data.get(cols.tags_1, "").strip(),
        cols.tags_2: note_data.get(cols.tags_2, "").strip(),
        cols.tags_3: note_data.get(cols.tags_3, "").strip(),
        cols.tags_4: note_data.get(cols.tags_4, "").strip(),
        # Personalized extra fields
        cols.extra_field_1: note_data.get(cols.extra_field_1, "").strip(),
        cols.extra_field_2: note_data.get(cols.extra_field_2, "").strip(),
        cols.extra_field_3: note_data.get(cols.extra_field_3, "").strip(),
    }

    # Fill available note fields
    for field_name in note.keys():
        if field_name in field_mappings:
            note[field_name] = field_mappings[field_name]


def determine_target_deck_for_student(
    col, base_deck_id, note_data, student, deck_url, debug_messages=None
):
    """
    Determines the target deck for a specific student.

    Args:
        col: Anki collection
        base_deck_id (int): Base deck ID
        note_data (dict): Note data
        student (str): Student name
        deck_url (str): Deck URL
        debug_messages (list, optional): Debug list

    Returns:
        int: Target deck ID
    """

    def add_debug_msg(message, category="DECK_TARGET_STUDENT"):
        """Helper to add debug messages using global system."""
        from .utils import add_debug_message

        add_debug_message(message, category)

    try:
        # Get base deck
        base_deck = col.decks.get(base_deck_id)
        if not base_deck:
            return base_deck_id

        # Generate subdeck name with full structure for specific student
        from .config_manager import get_deck_remote_name

        remote_deck_name = get_deck_remote_name(deck_url)

        # Create base deck following pattern: Sheets2Anki::{remote_deck_name}
        deck_with_remote_name = f"Sheets2Anki::{remote_deck_name}"
        subdeck_name = get_subdeck_name(
            deck_with_remote_name, note_data, student=student
        )
        subdeck_id = ensure_subdeck_exists(subdeck_name)

        if subdeck_id:
            add_debug_msg(
                f"Note directed to student {student} subdeck: {subdeck_name}"
            )
            return subdeck_id

        return base_deck_id

    except Exception as e:
        add_debug_msg(f"Error determining target deck for student {student}: {e}")
        return base_deck_id
