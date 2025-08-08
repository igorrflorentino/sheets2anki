#!/usr/bin/env python3
"""
Teste específico para verificar filtro de questões com normalização.
"""

import re

def normalize_student_name(name: str) -> str:
    """Função de normalização copiada."""
    if not name or not isinstance(name, str):
        return ""
    
    cleaned = re.sub(r'\s+', ' ', name.strip())
    cleaned = re.sub(r'[^\w\s]', '', cleaned)
    
    if not cleaned:
        return ""
    
    return cleaned.title()

def test_question_filtering():
    """Simula o filtro de questões."""
    
    print("🧪 TESTE: FILTRO DE QUESTÕES COM NORMALIZAÇÃO")
    print("=" * 60)
    
    # Simular questões do deck remoto
    mock_questions = [
        {"fields": {"ALUNOS": "pedro"}},        # Minúsculo
        {"fields": {"ALUNOS": "PEDRO"}},        # Maiúsculo  
        {"fields": {"ALUNOS": "Pedro"}},        # Title Case
        {"fields": {"ALUNOS": "belle"}},        # Minúsculo
        {"fields": {"ALUNOS": "Belle"}},        # Title Case
        {"fields": {"ALUNOS": "igor"}},         # Não habilitado
        {"fields": {"ALUNOS": "pedro, belle"}}, # Múltiplos alunos
        {"fields": {"ALUNOS": ""}},             # Sem aluno
    ]
    
    # Simular alunos selecionados (já normalizados pelo sistema)
    selected_students = {"Pedro", "Belle"}
    
    print(f"📋 DADOS DE TESTE:")
    print(f"  • Questões no deck remoto: {len(mock_questions)}")
    print(f"  • Alunos selecionados: {sorted(selected_students)}")
    
    print(f"\n🔍 PROCESSAMENTO:")
    
    filtered_questions = []
    
    for i, question in enumerate(mock_questions):
        fields = question.get('fields', {})
        alunos_field = fields.get('ALUNOS', '').strip()
        
        if not alunos_field:
            print(f"  📝 Questão {i+1}: [SEM ALUNO] → IGNORADA")
            continue
        
        # Normalizar estudantes da questão
        question_students = set()
        alunos_list = re.split(r'[,;|]', alunos_field)
        for aluno in alunos_list:
            aluno = aluno.strip()
            if aluno:
                normalized_student = normalize_student_name(aluno)
                if normalized_student:
                    question_students.add(normalized_student)
        
        # Verificar interseção
        intersection = question_students.intersection(selected_students)
        
        if intersection:
            filtered_questions.append(question)
            print(f"  📝 Questão {i+1}: '{alunos_field}' → {sorted(question_students)} → ✅ INCLUÍDA (match: {sorted(intersection)})")
        else:
            print(f"  📝 Questão {i+1}: '{alunos_field}' → {sorted(question_students)} → ❌ IGNORADA")
    
    print(f"\n🎯 RESULTADO:")
    print(f"  • Questões filtradas: {len(filtered_questions)}/{len(mock_questions)}")
    print(f"  • Espera-se: 6 questões (todas com pedro/Pedro/PEDRO e belle/Belle + 1 mista)")
    print(f"  • Sucesso: {'✅' if len(filtered_questions) == 6 else '❌'}")

if __name__ == "__main__":
    test_question_filtering()
