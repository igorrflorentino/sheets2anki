"""
Utilitários para normalização de nomes de estudantes.

Este módulo garante que todos os nomes de estudantes sejam tratados
de forma consistente em todo o sistema, independente de como foram
inseridos pelo usuário ou vindos do deck remoto.
"""

import re
from typing import Set, List, Dict, Any

def normalize_student_name(name: str) -> str:
    """
    Normaliza nome de estudante para formato consistente.
    
    Regras de normalização:
    1. Remove espaços extras no início e fim
    2. Primeira letra maiúscula, resto minúsculo (Title Case)
    3. Preserva espaços internos para nomes compostos
    4. Remove caracteres especiais inválidos
    
    Args:
        name (str): Nome original do estudante
        
    Returns:
        str: Nome normalizado no formato "Nome" ou "Nome Sobrenome"
        
    Examples:
        >>> normalize_student_name("igor")
        "Igor"
        >>> normalize_student_name("PEDRO")
        "Pedro" 
        >>> normalize_student_name("maria SILVA")
        "Maria Silva"
        >>> normalize_student_name("  joão  ")
        "João"
    """
    if not name or not isinstance(name, str):
        return ""
    
    # Remove espaços extras e caracteres de controle
    cleaned = re.sub(r'\s+', ' ', name.strip())
    
    # Remove caracteres especiais (mantém apenas letras, números e espaços)
    cleaned = re.sub(r'[^\w\s]', '', cleaned)
    
    if not cleaned:
        return ""
    
    # Aplica Title Case (primeira letra de cada palavra maiúscula)
    normalized = cleaned.title()
    
    return normalized


def normalize_student_list(students: List[str]) -> List[str]:
    """
    Normaliza uma lista de nomes de estudantes.
    
    Args:
        students (List[str]): Lista de nomes originais
        
    Returns:
        List[str]: Lista de nomes normalizados, sem duplicatas
    """
    if not students:
        return []
    
    normalized_set = set()
    for student in students:
        normalized = normalize_student_name(student)
        if normalized:  # Apenas adiciona nomes válidos
            normalized_set.add(normalized)
    
    return sorted(list(normalized_set))


def normalize_student_set(students: Set[str]) -> Set[str]:
    """
    Normaliza um conjunto de nomes de estudantes.
    
    Args:
        students (Set[str]): Conjunto de nomes originais
        
    Returns:
        Set[str]: Conjunto de nomes normalizados
    """
    if not students:
        return set()
    
    return {normalize_student_name(student) for student in students if normalize_student_name(student)}


def normalize_config_students(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normaliza todos os nomes de estudantes em uma configuração.
    
    Args:
        config (Dict): Configuração contendo listas de estudantes
        
    Returns:
        Dict: Configuração com nomes normalizados
    """
    if not config:
        return config
    
    # Copiar configuração para não modificar original
    normalized_config = config.copy()
    
    # Normalizar available_students
    if 'available_students' in normalized_config:
        normalized_config['available_students'] = normalize_student_list(
            normalized_config['available_students']
        )
    
    # Normalizar enabled_students
    if 'enabled_students' in normalized_config:
        normalized_config['enabled_students'] = normalize_student_list(
            normalized_config['enabled_students']
        )
    
    return normalized_config


def extract_student_from_note_type_name(note_type_name: str) -> str:
    """
    Extrai e normaliza nome de estudante de um note type.
    
    Padrão esperado: "Sheets2Anki - ... - StudentName - ..."
    
    Args:
        note_type_name (str): Nome do note type
        
    Returns:
        str: Nome normalizado do estudante ou string vazia se não encontrado
    """
    if not note_type_name or "Sheets2Anki -" not in note_type_name:
        return ""
    
    parts = note_type_name.split(" - ")
    if len(parts) >= 3:
        raw_student_name = parts[2].strip()
        if raw_student_name and raw_student_name != "[MISSING A.]":
            return normalize_student_name(raw_student_name)
    
    return ""


def extract_student_from_deck_name(deck_name: str) -> str:
    """
    Extrai e normaliza nome de estudante de um nome de deck.
    
    Padrão esperado: "DeckName::StudentName::..."
    
    Args:
        deck_name (str): Nome do deck
        
    Returns:
        str: Nome normalizado do estudante ou string vazia se não encontrado
    """
    if not deck_name:
        return ""
    
    parts = deck_name.split("::")
    if len(parts) >= 2 and "Sheets2Anki" in parts[0]:
        raw_student_name = parts[1].strip()
        if raw_student_name and raw_student_name != "[MISSING A.]":
            return normalize_student_name(raw_student_name)
    
    return ""
