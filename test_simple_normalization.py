#!/usr/bin/env python3
"""
Script de teste direto para verificar normalização de nomes.
"""

import re

def normalize_student_name(name: str) -> str:
    """Função de normalização copiada diretamente."""
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

def test_normalization():
    """Testa todas as funções de normalização."""
    
    print("🧪 TESTANDO NORMALIZAÇÃO DE NOMES DE ESTUDANTES")
    print("=" * 60)
    
    # Teste 1: Normalização básica
    print("\n1️⃣ TESTE: Normalização básica")
    test_cases = [
        "pedro", "PEDRO", "Pedro", "  pedro  ", "pEdRo",
        "maria silva", "MARIA SILVA", "Maria Silva", "  maria silva  ",
        "joão", "JOÃO", "João", "joão pedro", "JOÃO PEDRO",
        "igor", "iGRO", "IGOR"
    ]
    
    for name in test_cases:
        normalized = normalize_student_name(name)
        print(f"  '{name}' → '{normalized}'")
    
    # Teste 2: Caso específico do usuário
    print("\n2️⃣ TESTE: Caso específico Pedro vs pedro")
    config_students = ["Belle", "Pedro"]
    note_type_students = ["pedro", "belle"]
    
    print(f"  Config: {config_students}")
    print(f"  Note types (raw): {note_type_students}")
    
    config_normalized = [normalize_student_name(s) for s in config_students]
    note_types_normalized = [normalize_student_name(s) for s in note_type_students]
    
    print(f"  Config (norm): {config_normalized}")
    print(f"  Note types (norm): {note_types_normalized}")
    
    # Verificar se são iguais após normalização
    config_set = set(config_normalized)
    note_type_set = set(note_types_normalized)
    intersection = config_set.intersection(note_type_set)
    
    print(f"  Interseção: {sorted(intersection)}")
    print(f"  Alunos habilitados: {sorted(config_set)}")
    print(f"  Alunos nos note types: {sorted(note_type_set)}")
    
    # O problema original: Pedro (config) não era reconhecido como pedro (note types)
    pedro_config = normalize_student_name("Pedro")  # Do config
    pedro_note_type = normalize_student_name("pedro")  # Do note type
    
    print(f"\n  🎯 VERIFICAÇÃO PRINCIPAL:")
    print(f"  'Pedro' (config) → '{pedro_config}'")  
    print(f"  'pedro' (note type) → '{pedro_note_type}'")
    print(f"  São iguais após normalização? {pedro_config == pedro_note_type}")
    
    print("\n✅ TESTE CONCLUÍDO!")
    print("🎯 RESULTADO: Agora Pedro/pedro/PEDRO são sempre normalizados para 'Pedro'")

if __name__ == "__main__":
    test_normalization()
