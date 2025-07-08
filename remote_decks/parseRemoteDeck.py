
import csv
import requests
import re  # Import the 're' module for regular expressions
from . import column_definitions as cols  # Import centralized column definitions

# Custom exception for remote deck errors
class RemoteDeckError(Exception):
    pass

class RemoteDeck:
    """Class representing a deck loaded from a remote TSV source."""
    def __init__(self):
        self.deckName = ""
        self.questions = []  # Keep using 'questions' attribute
        self.media = []

    def getMedia(self):
        return self.media

def getRemoteDeck(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RemoteDeckError(f"Network error downloading TSV: {e}")
    try:
        tsv_data = response.content.decode('utf-8')
    except UnicodeDecodeError as e:
        raise RemoteDeckError(f"Error decoding TSV content: {e}")

    try:
        data = parse_tsv_data(tsv_data)
        remoteDeck = build_remote_deck_from_tsv(data)
        return remoteDeck
    except Exception as e:
        raise RemoteDeckError(f"Error parsing remote deck: {e}")

def validate_tsv_headers(headers):
    """Validate that the TSV has the required headers."""
    headers_upper = [h.strip().upper() for h in headers]
    missing_headers = [h for h in cols.REQUIRED_COLUMNS if h not in headers_upper]
    
    if missing_headers:
        raise ValueError(f"Missing required columns: {', '.join(missing_headers)}")
    
    return headers_upper

def parse_tsv_data(tsv_data):
    """Parse and validate TSV data."""
    try:
        reader = csv.reader(tsv_data.splitlines(), delimiter='\t')
        data = list(reader)
        
        if not data:
            raise ValueError("TSV file is empty")
            
        if len(data) < 2:  # At least headers and one row
            raise ValueError("TSV file must contain headers and at least one card")
            
        return data
    except csv.Error as e:
        raise ValueError(f"Invalid TSV format: {str(e)}")

def has_cloze_deletion(text):
    """Check if the text contains cloze deletions in the format {{c1::text}}."""
    return bool(re.search(r'\{\{c\d+::.+?\}\}', text))

def clean_tag_text(text):
    """Clean text for use in tags by removing special chars and converting spaces to underscores."""
    if not text or not text.strip():
        return ""
    return re.sub(r'[^\w\s]', '', text.strip()).replace(' ', '_')

def create_tags_from_fields(fields):
    """Create hierarchical tags from specific fields.
    
    Creates tags in the format:
    - topicos::topico1::subtopicos_do_topico1
    - bancas::banca1
    - provas::ano1
    - variado::tag_adicional1
    
    Args:
        fields (dict): Dictionary containing the card fields
        
    Returns:
        list: List of Anki-compatible hierarchical tags
    """
    tags = []
    
    # Process TOPICO and SUBTOPICO
    topico = clean_tag_text(fields.get(cols.TOPICO, ''))
    subtopicos_raw = fields.get(cols.SUBTOPICO, '')
    if topico:
        if subtopicos_raw:
            # Split subtopics by comma and process each one
            for subtopico in subtopicos_raw.split(','):
                subtopico_clean = clean_tag_text(subtopico)
                if subtopico_clean:
                    tags.append(f"topicos::{topico}::{subtopico_clean}")
        else:
            tags.append(f"topicos::{topico}")
            
    # Process BANCAS (can have multiple comma-separated values)
    bancas = fields.get(cols.BANCAS, '')
    if bancas:
        for banca in bancas.split(','):
            banca_clean = clean_tag_text(banca)
            if banca_clean:
                tags.append(f"bancas::{banca_clean}")
                
    # Process ANO
    ano = clean_tag_text(fields.get(cols.ANO, ''))
    if ano:
        tags.append(f"provas::{ano}")
        
    # Process MORE_TAGS (additional tags)
    more_tags = fields.get(cols.MORE_TAGS, '')
    if more_tags:
        for tag in more_tags.split(','):
            tag_clean = clean_tag_text(tag)
            if tag_clean:
                tags.append(f"variado::{tag_clean}")
    
    return tags

def build_remote_deck_from_tsv(data):
    # Process and validate headers
    headers = validate_tsv_headers(data[0])
    
    # Create header to index mapping
    header_indices = {header: idx for idx, header in enumerate(headers)}
    
    questions = []
    for row_num, row in enumerate(data[1:], start=2):
        # Skip empty rows
        if not any(cell.strip() for cell in row):
            continue

        # Validate row length matches headers
        if len(row) != len(headers):
            continue

        # Create fields dictionary
        fields = {}
        for header in headers:
            idx = header_indices[header]
            if idx < len(row):
                fields[header] = row[idx].strip()
            else:
                fields[header] = ""

        # Validate required fields
        if not fields[cols.ID] or not fields[cols.PERGUNTA]:
            continue

        # Generate tags from fields
        tags = create_tags_from_fields(fields)
        
        # Create and add question with tags
        question = {
            'fields': fields,
            'tags': tags
        }
        questions.append(question)

    # Create and return deck
    remoteDeck = RemoteDeck()
    remoteDeck.deckName = "Deck from CSV"
    remoteDeck.questions = questions

    return remoteDeck
