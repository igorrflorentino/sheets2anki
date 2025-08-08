#!/usr/bin/env python3
"""
Script de teste para verificar normalização consistente de nomes de estudantes.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.student_normalization import (
    normalize_student_name, 
    normalize_student_list,
    extract_student_from_note_type_name
)

def test_normalization():
    """Testa todas as funções de normalização."""
    
    print("🧪 TESTANDO NORMALIZAÇÃO DE NOMES DE ESTUDANTES")
    print("=" * 60)
    
    # Teste 1: Normalização básica
    print("\n1️⃣ TESTE: Normalização básica")
    test_cases = [
        "pedro", "PEDRO", "Pedro", "  pedro  ", "pEdRo",
        "maria silva", "MARIA SILVA", "Maria Silva", "  maria silva  ",
        "joão", "JOÃO", "João", "joão pedro", "JOÃO PEDRO"
    ]
    
    for name in test_cases:
        normalized = normalize_student_name(name)
        print(f"  '{name}' → '{normalized}'")
    
    # Teste 2: Lista de normalização
    print("\n2️⃣ TESTE: Normalização de listas")
    test_list = ["pedro", "PEDRO", "belle", "Belle", "igor", "IGOR", "pedro", "Belle"]
    normalized_list = normalize_student_list(test_list)
    print(f"  Original: {test_list}")
    print(f"  Normalizada: {normalized_list}")
    
    # Teste 3: Extração de note types
    print("\n3️⃣ TESTE: Extração de note types")
    note_type_names = [
        "Sheets2Anki - #0 Sheets2Anki Template 7 - pedro - Basic",
        "Sheets2Anki - #0 Sheets2Anki Template 7 - PEDRO - Cloze", 
        "Sheets2Anki - #0 Sheets2Anki Template 7 - Belle - Basic",
        "Sheets2Anki - #0 Sheets2Anki Template 7 - maria silva - Cloze",
        "Sheets2Anki - #0 Sheets2Anki Template 7 - [MISSING A.] - Basic"
    ]
    
    for note_type_name in note_type_names:
        extracted = extract_student_from_note_type_name(note_type_name)
        print(f"  '{note_type_name}' → '{extracted}'")
    
    # Teste 4: Caso específico do usuário (Pedro vs pedro)
    print("\n4️⃣ TESTE: Caso específico Pedro vs pedro")
    config_students = ["Belle", "Pedro"]
    note_type_students = ["pedro", "belle"]
    
    print(f"  Config: {config_students}")
    print(f"  Note types (raw): {note_type_students}")
    
    config_normalized = [normalize_student_name(s) for s in config_students]
    note_types_normalized = [normalize_student_name(s) for s in note_type_students]
    
    print(f"  Config (norm): {config_normalized}")
    print(f"  Note types (norm): {note_types_normalized}")
    
    # Verificar interseção
    config_set = set(config_normalized)
    note_type_set = set(note_types_normalized)
    intersection = config_set.intersection(note_type_set)
    
    print(f"  Interseção: {sorted(intersection)}")
    print(f"  Alunos desabilitados: {sorted(note_type_set - config_set)}")
    
    print("\n✅ TESTE CONCLUÍDO!")
    print("🎯 RESULTADO: A normalização deve garantir que 'Pedro' e 'pedro' sejam tratados como 'Pedro'")

if __name__ == "__main__":
    test_normalization()
