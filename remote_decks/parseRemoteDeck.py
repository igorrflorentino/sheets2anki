import csv
import requests
import re  # Import the 're' module for regular expressions

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
    required_headers = [
        'ID', 'PERGUNTA', 'RESPOSTA_PROVA', 'RESPOSTA_RESUMIDA',
        'RESPOSTA_COMPLETA', 'EXAMPLO1', 'EXAMPLO2', 'EXAMPLO3',
        'TOPICO', 'SUBTOPICO', 'BANCAS', 'IMPORTANCIA', 'TAGS'
    ]
    
    headers_upper = [h.strip().upper() for h in headers]
    missing_headers = [h for h in required_headers if h not in headers_upper]
    
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
        if not fields['ID'] or not fields['PERGUNTA']:
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
