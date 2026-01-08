"""
Templates and column definitions for the Sheets2Anki addon.

This module centralizes:
- Standardized spreadsheet column name definitions
- HTML templates for Anki cards
- Functions for creating note models
- Data structure validation

Consolidated from:
- card_templates.py: Card templates and models
- column_definitions.py: Spreadsheet column definitions
"""

# =============================================================================
# CONTROL FIELDS
# =============================================================================

# Basic system fields
identifier = "ID"  # Unique question identifier (required)
students = "ALUNOS"  # Indicates which students are interested in studying this note
is_sync = "SYNC"  # Synchronization control field (true/false/1/0)

# =============================================================================
# MAIN FIELDS
# =============================================================================

# Main question fields
question = "PERGUNTA"  # Main question text / front of card
answer = "LEVAR PARA PROVA"  # Succinct and atomic answer to the question

# =============================================================================
# DETAIL FIELDS
# =============================================================================

# Additional information about the question
info_1 = "INFO COMPLEMENTAR"  # Basic complementary information
info_2 = "INFO DETALHADA"  # Additional detailed information

# =============================================================================
# EXAMPLE FIELDS
# =============================================================================

# Examples related to the question (up to 3 examples)
example_1 = "EXEMPLO 1"  # First example
example_2 = "EXEMPLO 2"  # Second example
example_3 = "EXEMPLO 3"  # Third example

# =============================================================================
# MULTIMEDIA FIELDS
# =============================================================================

# Helps make information visually more attractive
multimedia_1 = "IMAGEM HTML"  # HTML code for renderable images and illustrations
multimedia_2 = "VIDEO HTML"  # HTML code for embedded videos (YouTube, Vimeo, etc.)

# =============================================================================
# CATEGORIZATION FIELDS
# =============================================================================

# Hierarchical content categorization
hierarchy_1 = "IMPORTANCIA"  # Question importance level
hierarchy_2 = "TOPICO"  # Main question topic
hierarchy_3 = "SUBTOPICO"  # Specific subtopic
hierarchy_4 = "CONCEITO"  # Atomic concept being asked (more refined than subtopic)

# =============================================================================
# METADATA FIELDS
# =============================================================================

# Context and source information
tags_1 = "BANCAS"  # Related exam boards
tags_2 = "ULTIMO ANO EM PROVA"  # Last year appeared in exam
tags_3 = "CARREIRAS"  # Related careers or professional areas
tags_4 = "TAGS ADICIONAIS"  # Additional tags for organization

# =============================================================================
# CUSTOMIZABLE EXTRA FIELDS
# =============================================================================

# Extra fields for user customization
extra_field_1 = "CAMPO EXTRA 1"  # Extra field 1 - free use
extra_field_2 = "CAMPO EXTRA 2"  # Extra field 2 - free use
extra_field_3 = "CAMPO EXTRA 3"  # Extra field 3 - free use

# =============================================================================
# VALIDATION CONFIGURATIONS
# =============================================================================

# Complete list of all available spreadsheet columns
ALL_AVAILABLE_COLUMNS = [
    identifier,  # Unique identifier
    students,  # Interested students control
    is_sync,  # Synchronization control

    hierarchy_1,  # Importance level
    hierarchy_2,  # Main topic
    hierarchy_3,  # Subtopic
    hierarchy_4,  # Atomic concept

    question,  # Main question text / front of card
    answer,  # Succinct answer (core of response)

    info_1,  # Complementary info
    info_2,  # Detailed info

    example_1,  # First example
    example_2,  # Second example
    example_3,  # Third example

    multimedia_1,  # HTML code for images and illustrations
    multimedia_2,  # HTML code for embedded videos

    tags_1,  # Related exam boards
    tags_2,  # Exam year
    tags_3,  # Careers or professional areas
    tags_4,  # Additional tags

    extra_field_1,  # Extra field 1
    extra_field_2,  # Extra field 2
    extra_field_3,  # Extra field 3
]

# Fields considered mandatory for note creation
# Fields considered mandatory for note creation
ESSENTIAL_FIELDS = [identifier]

# Fields required in spreadsheet headers (for parsing to work)
# Fields required in spreadsheet headers (for parsing to work)
REQUIRED_HEADERS = [identifier, question, answer]

# Fields that can be used for filtering/selection
# Fields that can be used for filtering/selection
FILTER_FIELDS = [hierarchy_1, hierarchy_2, hierarchy_3, hierarchy_4,
                 tags_1, tags_2, tags_3, tags_4]

# Fields containing extensive text information
TEXT_FIELDS = [
    question,
    answer,
    info_1,
    info_2,
    example_1,
    example_2,
    example_3,
    extra_field_1,
    extra_field_2,
    extra_field_3,
]

# Fields containing media (images, videos, etc.)
MEDIA_FIELDS = [
    multimedia_1,
    multimedia_2,
]

# Fields that should be included in Anki notes
NOTE_FIELDS = [
    identifier,  # Unique identifier
    
    hierarchy_1,  # Importance level
    hierarchy_2,  # Main topic
    hierarchy_3,  # Subtopic
    hierarchy_4,  # Atomic concept
    
    question,  # Question text
    answer,  # Succinct answer (core of response)
    
    info_1,  # Complementary info
    info_2,  # Detailed info
    
    example_1,  # First example
    example_2,  # Second example
    example_3,  # Third example
    
    multimedia_1,  # HTML code for images and illustrations
    multimedia_2,  # HTML code for embedded videos

    extra_field_1,  # Extra field 1
    extra_field_2,  # Extra field 2
    extra_field_3,  # Extra field 3
    
    tags_1,  # Related exam boards
    tags_2,  # Exam year
    tags_3,  # Careers or professional areas
    tags_4,  # Additional tags
]

# Fields containing metadata
METADATA_FIELDS = [
    hierarchy_1,
    hierarchy_2,
    hierarchy_3,
    hierarchy_4,
    tags_1,
    tags_2,
    tags_3,
    tags_4,
]

# =============================================================================
# CONSTANTS AND TEMPLATES
# =============================================================================

# Constant to identify if we are in development mode
# This constant will be changed to False during the build process
IS_DEVELOPMENT_MODE = True

# Hardcoded URLs for testing and simulations
TEST_SHEETS_URLS = [
    (
        "Sheets2Anki Template (Edit Link)",
        "https://docs.google.com/spreadsheets/d/1N-Va4ZzLUJBsD6wBaOkoeFTE6EnbZdaPBB88FYl2hrs/edit?usp=sharing",
    )
]

# Template constants for card generation
CARD_SHOW_ALLWAYS_TEMPLATE = """
<b>➡️ {field_name}</b><br>
{{{{{field_value}}}}}<br><br>
"""

CARD_SHOW_HIDE_TEMPLATE = """
{{{{#{field_value}}}}}
<b>➡️ {field_name}</b><br>
{{{{{field_value}}}}}<br><br>
{{{{/{field_value}}}}}
"""

MARKERS_TEMPLATE = """
<h2 style="color: orange; text-align: center; margin-bottom: 0;">{text}</h2>
<div style="text-align: center; font-size: 0.8em; color: gray;">{observation}</div>
<hr>
"""

# Default values for empty fields
DEFAULT_IMPORTANCE = "[MISSING IMPORTANCE]"
DEFAULT_TOPIC = "[MISSING TOPIC]"
DEFAULT_SUBTOPIC = "[MISSING SUBTOPIC]"
DEFAULT_CONCEPT = "[MISSING CONCEPT]"
DEFAULT_STUDENT = "[MISSING STUDENT]"

# Root deck name - non-modifiable constant by user
DEFAULT_PARENT_DECK_NAME = "Sheets2Anki"

# Tag prefixes
TAG_ROOT = "Sheets2Anki"
TAG_TOPICS = "topics"
TAG_SUBTOPICS = "subtopics"
TAG_CONCEPTS = "concepts"
TAG_EXAM_BOARDS = "exam_boards"
TAG_YEARS = "years"
TAG_CAREERS = "careers"
TAG_IMPORTANCE = "importance"
TAG_ADDITIONAL = "additional"

# =============================================================================
# COLUMN VALIDATION FUNCTIONS
# =============================================================================


def validate_required_columns(columns):
    """
    Validates if all required columns are present in the spreadsheet.

    Args:
        columns (list): List of spreadsheet column names

    Returns:
        tuple: (is_valid, missing_columns) where:
            - is_valid: bool indicating if all columns are present
            - missing_columns: list of missing columns
    """
    missing_columns = [col for col in ALL_AVAILABLE_COLUMNS if col not in columns]
    return len(missing_columns) == 0, missing_columns


def is_essential_field(field_name):
    """
    Checks if a field is considered essential for note creation.

    Args:
        field_name (str): Field name to check

    Returns:
        bool: True if field is essential, False otherwise
    """
    return field_name in ESSENTIAL_FIELDS


def is_filter_field(field_name):
    """
    Checks if a field can be used for filtering/selection.

    Args:
        field_name (str): Field name to check

    Returns:
        bool: True if field can be used for filtering, False otherwise
    """
    return field_name in FILTER_FIELDS


def get_field_category(field_name):
    """
    Returns the category of a specific field.

    Args:
        field_name (str): Field name

    Returns:
        str: Field category ('essential', 'text', 'metadata', 'filter', 'unknown')
    """
    if field_name in ESSENTIAL_FIELDS:
        return "essential"
    elif field_name in TEXT_FIELDS:
        return "text"
    elif field_name in METADATA_FIELDS:
        return "metadata"
    elif field_name in FILTER_FIELDS:
        return "filter"
    else:
        return "unknown"


def should_sync_question(fields):
    """
    Checks if a question should be synchronized based on the SYNC field.

    Args:
        fields (dict): Dictionary with question fields

    Returns:
        bool: True if should synchronize, False otherwise
    """
    sync_value = fields.get(is_sync, "").strip().lower()

    # Consider positive values: true, 1, sim, yes, verdadeiro
    # Consider positive values: true, 1, yes
    positive_values = ["true", "1", "yes", "sim", "v"]

    if sync_value in positive_values:
        return True
    else:
        # If value is not recognized or empty, do NOT synchronize
        # Synchronization must be explicitly marked
        return False


def get_all_column_info():
    """
    Returns complete information about all defined columns.

    Returns:
        dict: Dictionary with detailed information for each column
    """
    column_info = {}

    for column in ALL_AVAILABLE_COLUMNS:
        column_info[column] = {
            "name": column,
            "category": get_field_category(column),
            "is_essential": is_essential_field(column),
            "is_filter": is_filter_field(column),
            "is_text": column in TEXT_FIELDS,
            "is_metadata": column in METADATA_FIELDS,
        }

    return column_info


# =============================================================================
# CARD TEMPLATES
# =============================================================================


def create_card_template(is_cloze=False):
    """
    Creates the HTML template for a card (standard or cloze).

    Args:
        is_cloze (bool): Whether to create a cloze template

    Returns:
        dict: Dictionary with 'qfmt' and 'afmt' template strings
    """

    # Common header fields
    header_fields = [
        (hierarchy_1, hierarchy_1),
        (hierarchy_2, hierarchy_2),
        (hierarchy_3, hierarchy_3),
        (hierarchy_4, hierarchy_4),
    ]

    # Build header section
    header = ""
    for field_name, field_value in header_fields:
        header += CARD_SHOW_ALLWAYS_TEMPLATE.format(
            field_name=field_name.capitalize(), field_value=field_value
        )

    # Question format
    question_html = (
        f"<b>❓ {question.capitalize()}</b><br>"
        f"{{{{{'cloze:' if is_cloze else ''}{question}}}}}<br><br>"
    )

    # Answer format
    answer_html = (
        f"<b>❗️ {answer.capitalize()}</b><br>"
        f"{{{{{'cloze:' if is_cloze else ''}{answer}}}}}<br><br>"
    )

    # Information fields
    info_fields = [info_1, info_2]

    extra_infos = ""
    for info_field in info_fields:
        extra_infos += CARD_SHOW_HIDE_TEMPLATE.format(
            field_name=info_field.capitalize(), field_value=info_field
        )

    # Image multimedia field
    image_html = CARD_SHOW_HIDE_TEMPLATE.format(
        field_name=multimedia_1.capitalize(), field_value=multimedia_1
    )

    # Video multimedia field
    video_html = CARD_SHOW_HIDE_TEMPLATE.format(
        field_name=multimedia_2.capitalize(), field_value=multimedia_2
    )

    # Example fields
    example_fields = [example_1, example_2, example_3]

    examples = ""
    for field in example_fields:
        examples += CARD_SHOW_HIDE_TEMPLATE.format(
            field_name=field.capitalize(), field_value=field
        )

    # Customizable extra fields
    extra_fields = [extra_field_1, extra_field_2, extra_field_3]

    extras = ""
    for field in extra_fields:
        extras += CARD_SHOW_HIDE_TEMPLATE.format(
            field_name=field.capitalize(), field_value=field
        )

    # Footer fields
    footer_fields = [
        (tags_1, tags_1),
        (tags_2, tags_2),
        (tags_3, tags_3),
        (tags_4, tags_4),
    ]

    # Build footer section
    footer = ""
    for field_name, field_value in footer_fields:
        footer += CARD_SHOW_HIDE_TEMPLATE.format(
            field_name=field_name.capitalize(), field_value=field_value
        )

    # Build complete templates
    qfmt = (
        MARKERS_TEMPLATE.format(text="CONTEXT", observation="") +
        header +        
        MARKERS_TEMPLATE.format(text="CARD", observation="") +
        question_html  # Front: only header and question
    )
    afmt = (
        MARKERS_TEMPLATE.format(text="CONTEXT", observation="") +
        (header + 
        MARKERS_TEMPLATE.format(text="CARD", observation="") +
         question_html +
        MARKERS_TEMPLATE.format(text="INFORMATION", observation="May be empty") +
         extra_infos + 
         examples + 
         image_html + 
         video_html + 
         extras + 
         MARKERS_TEMPLATE.format(text="TAGS", observation="May be empty") + 
         footer)
        if is_cloze
        else (
            "{{FrontSide}}" + 
            answer_html +
            MARKERS_TEMPLATE.format(text="INFORMATION", observation="May be empty") +
            extra_infos + 
            examples + 
            image_html + 
            video_html + 
            extras + 
            MARKERS_TEMPLATE.format(text="TAGS", observation="May be empty") +
            footer)
    )

    return {"qfmt": qfmt, "afmt": afmt}


def create_model(col, model_name, is_cloze=False, url=None, debug_messages=None):
    """
    Creates a new Anki note model.

    Args:
        col: Anki collection object
        model_name (str): Name for the new model
        is_cloze (bool): Whether to create a cloze model
        url (str, optional): Remote deck URL for automatic registration
        debug_messages (list, optional): List for debug

    Returns:
        object: The created Anki model
    """
    from .utils import register_note_type_for_deck

    model = col.models.new(model_name)
    if is_cloze:
        model["type"] = 1  # Set as cloze type

    # Add fields (excluding internal control fields like SYNC)
    for field in NOTE_FIELDS:
        template = col.models.new_field(field)
        col.models.add_field(model, template)

    # Add card template
    template = col.models.new_template("Cloze" if is_cloze else "Card 1")
    card_template = create_card_template(is_cloze)
    template["qfmt"] = card_template["qfmt"]
    template["afmt"] = card_template["afmt"]

    col.models.add_template(model, template)
    col.models.save(model)

    # Automatically register note type if URL was provided
    if url and model.get("id"):
        try:
            register_note_type_for_deck(url, model["id"], model_name, debug_messages)
        except Exception as e:
            if debug_messages:
                debug_messages.append(f"Error registering note type {model['id']}: {e}")

    return model


def ensure_custom_models(col, url, student=None, debug_messages=None):
    """
    Ensures both models (standard and cloze) exist in Anki.
    Uses IDs stored in meta.json to find existing note types,
    instead of searching only by name.

    Args:
        col: Anki collection object
        url (str): Remote deck URL
        student (str, optional): Student name for creating specific models
        debug_messages (list, optional): List for debug

    Returns:
        dict: Dictionary containing 'standard' and 'cloze' models
    """
    from .config_manager import get_deck_note_type_ids
    from .config_manager import get_deck_remote_name
    from .utils import get_note_type_name
    from .utils import register_note_type_for_deck

    def add_debug_msg(message):
        if debug_messages:
            debug_messages.append(f"[ENSURE_MODELS] {message}")

    models = {}

    # Get remote deck name and existing note types
    remote_deck_name = get_deck_remote_name(url) or "RemoteDeck"
    existing_note_types = get_deck_note_type_ids(url) or {}

    add_debug_msg(
        f"Searching note types for student='{student}', remote_deck_name='{remote_deck_name}'"
    )
    add_debug_msg(f"Existing note types: {len(existing_note_types)} found")

    # Helper function to find note type by pattern
    def find_existing_note_type(is_cloze):
        target_type = "Cloze" if is_cloze else "Basic"
        target_pattern = (
            f" - {student} - {target_type}" if student else f" - {target_type}"
        )

        # Search in existing note types
        for note_type_id_str, note_type_name in existing_note_types.items():
            if note_type_name.endswith(target_pattern):
                try:
                    note_type_id = int(note_type_id_str)
                    from anki.models import NotetypeId
                    model = col.models.get(NotetypeId(note_type_id))
                    if model:
                        add_debug_msg(
                            f"Found existing note type: ID {note_type_id} - '{note_type_name}'"
                        )
                        return model, note_type_name
                except (ValueError, TypeError):
                    continue
        return None, None

    # Standard model (Basic)
    expected_name = get_note_type_name(
        url, remote_deck_name, student=student, is_cloze=False
    )
    existing_model, existing_name = find_existing_note_type(is_cloze=False)

    if existing_model:
        # Use existing model and do NOT force new name if already registered
        current_registered_name = None
        for note_type_id_str, note_type_name in existing_note_types.items():
            try:
                if int(note_type_id_str) == existing_model["id"]:
                    current_registered_name = note_type_name
                    break
            except ValueError:
                continue

        if current_registered_name:
            # Already registered, use current config name
            add_debug_msg(
                f"Using existing (Basic) model ALREADY REGISTERED: '{existing_name}' with config name: '{current_registered_name}'"
            )
            models["standard"] = existing_model
        else:
            # Not registered, register with expected name
            register_note_type_for_deck(
                url, existing_model["id"], expected_name, debug_messages
            )
            models["standard"] = existing_model
            add_debug_msg(
                f"Existing (Basic) model registered: '{existing_name}' → expected: '{expected_name}'"
            )
    else:
        # Create new model only if it really doesn't exist
        add_debug_msg(f"Creating new (Basic) model: '{expected_name}'")
        model = create_model(
            col, expected_name, is_cloze=False, url=url, debug_messages=debug_messages
        )
        models["standard"] = model

    # Cloze model
    expected_cloze_name = get_note_type_name(
        url, remote_deck_name, student=student, is_cloze=True
    )
    existing_cloze_model, existing_cloze_name = find_existing_note_type(is_cloze=True)

    if existing_cloze_model:
        # Use existing model and do NOT force new name if already registered
        current_registered_cloze_name = None
        for note_type_id_str, note_type_name in existing_note_types.items():
            try:
                if int(note_type_id_str) == existing_cloze_model["id"]:
                    current_registered_cloze_name = note_type_name
                    break
            except ValueError:
                continue

        if current_registered_cloze_name:
            # Already registered, use current config name
            add_debug_msg(
                f"Using existing (Cloze) model ALREADY REGISTERED: '{existing_cloze_name}' with config name: '{current_registered_cloze_name}'"
            )
            models["cloze"] = existing_cloze_model
        else:
            # Not registered, register with expected name
            register_note_type_for_deck(
                url, existing_cloze_model["id"], expected_cloze_name, debug_messages
            )
            models["cloze"] = existing_cloze_model
            add_debug_msg(
                f"Existing (Cloze) model registered: '{existing_cloze_name}' → expected: '{expected_cloze_name}'"
            )
    else:
        # Create new model only if it really doesn't exist
        add_debug_msg(f"Creating new (Cloze) model: '{expected_cloze_name}'")
        cloze_model = create_model(
            col,
            expected_cloze_name,
            is_cloze=True,
            url=url,
            debug_messages=debug_messages,
        )
        models["cloze"] = cloze_model

    return models

def update_existing_note_type_templates(col, debug_messages=None):
    """
    Updates templates of all existing Sheets2Anki note types
    to include the new IMAGE HTML column.
    
    Args:
        col: Anki collection object
        debug_messages (list, optional): List for debug
    
    Returns:
        int: Number of updated note types
    """
    if debug_messages is None:
        debug_messages = []
    
    updated_count = 0
    
    # Search all note types that start with "Sheets2Anki"
    all_models = col.models.all()
    sheets2anki_models = [
        model for model in all_models 
        if model.get("name", "").startswith("Sheets2Anki")
    ]
    
    debug_messages.append(f"[UPDATE_TEMPLATES] Found {len(sheets2anki_models)} Sheets2Anki note types")
    
    for model in sheets2anki_models:
        try:
            model_name = model.get("name", "")
            is_cloze = model.get("type") == 1
            
            debug_messages.append(f"[UPDATE_TEMPLATES] Processing: {model_name} (cloze: {is_cloze})")
            
            # Check if IMAGE HTML field already exists
            existing_fields = []
            for field in model.get("flds", []):
                # Handle different field formats (dict or object)
                if hasattr(field, 'get'):
                    field_name = field.get("name", "")
                elif isinstance(field, dict):
                    field_name = field.get("name", "")
                else:
                    # Assume it's an object with name attribute
                    field_name = getattr(field, 'name', "")
                existing_fields.append(field_name)
            
            if multimedia_1 not in existing_fields:
                debug_messages.append(f"[UPDATE_TEMPLATES] Adding field {multimedia_1}")
                # Add IMAGE HTML field
                field_template = col.models.new_field(multimedia_1)
                col.models.add_field(model, field_template)
            else:
                debug_messages.append(f"[UPDATE_TEMPLATES] Field {multimedia_1} already exists")
            
            # Update card templates
            templates = model.get("tmpls", [])
            if templates:
                new_card_template = create_card_template(is_cloze)
                template_updated = False
                
                for i, template in enumerate(templates):
                    # Handle different template formats
                    if hasattr(template, 'get'):
                        old_qfmt = template.get("qfmt", "")
                        old_afmt = template.get("afmt", "")
                    elif isinstance(template, dict):
                        old_qfmt = template.get("qfmt", "")
                        old_afmt = template.get("afmt", "")
                    else:
                        old_qfmt = getattr(template, 'qfmt', "")
                        old_afmt = getattr(template, 'afmt', "")
                    
                    # Check if needs update (if doesn't have IMAGE HTML in template)
                    needs_update = multimedia_1 not in old_afmt
                    
                    if needs_update:
                        # Update template
                        if hasattr(template, '__setitem__'):
                            template["qfmt"] = new_card_template["qfmt"]
                            template["afmt"] = new_card_template["afmt"]
                        elif isinstance(template, dict):
                            template["qfmt"] = new_card_template["qfmt"]
                            template["afmt"] = new_card_template["afmt"]
                        else:
                            setattr(template, 'qfmt', new_card_template["qfmt"])
                            setattr(template, 'afmt', new_card_template["afmt"])
                        
                        template_updated = True
                        debug_messages.append(f"[UPDATE_TEMPLATES] Template {i+1} updated for {model_name}")
                    else:
                        debug_messages.append(f"[UPDATE_TEMPLATES] Template {i+1} already contains {multimedia_1}")
                
                if not template_updated:
                    debug_messages.append(f"[UPDATE_TEMPLATES] No template needed update for {model_name}")
            
            # Save updated model
            col.models.save(model)
            updated_count += 1
            debug_messages.append(f"[UPDATE_TEMPLATES] ✅ {model_name} processed successfully")
            
        except Exception as e:
            debug_messages.append(f"[UPDATE_TEMPLATES] ❌ Error updating {model.get('name', 'unknown')}: {e}")
    
    debug_messages.append(f"[UPDATE_TEMPLATES] 🎯 Total note types processed: {updated_count}")
    return updated_count
