import csv
import requests
import re  # Import the 're' module for regular expressions
from . import column_definitions as cols  # Import centralized column definitions

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
        tsv_data = response.content.decode('utf-8')
    except Exception as e:
        raise Exception(f"Error downloading or reading the TSV: {e}")

    data = parse_tsv_data(tsv_data)
    remoteDeck = build_remote_deck_from_tsv(data)
    return remoteDeck

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

def parse_tags(tags_str):
    """Parse tags in the format 'tagtype1: tagname1, tagtype1: tagname2, tagtype2: tagname1, ...'
    
    Args:
        tags_str (str): String containing tags in the format 'tagtype1: tagname1, tagtype1: tagname2, ...'
        
    Returns:
        list: List of Anki-compatible tags in the format ['tagtype1::tagname1', 'tagtype1::tagname2', ...]
    """
    if not tags_str or not tags_str.strip():
        return []
        
    # Split by commas and clean up whitespace
    tag_pairs = [pair.strip() for pair in tags_str.split(',')]
    
    # Process each tag pair
    processed_tags = []
    for pair in tag_pairs:
        # Skip empty pairs
        if not pair:
            continue
            
        # Split by colon and clean up whitespace
        parts = [part.strip() for part in pair.split(':', 1)]
        if len(parts) != 2:
            continue
            
        tag_type, tag_name = parts
        # Skip if either part is empty
        if not tag_type or not tag_name:
            continue
            
        # Convert spaces to underscores and remove special characters
        tag_type = re.sub(r'[^\w\s]', '', tag_type).replace(' ', '_')
        tag_name = re.sub(r'[^\w\s]', '', tag_name).replace(' ', '_')
        
        # Combine with double colon for Anki hierarchical tags
        processed_tags.append(f"{tag_type}::{tag_name}")
    
    return processed_tags

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

        # Create and add question
        question = {
            'fields': fields
        }
        questions.append(question)

    # Create and return deck
    remoteDeck = RemoteDeck()
    remoteDeck.deckName = "Deck from CSV"
    remoteDeck.questions = questions

    return remoteDeck
