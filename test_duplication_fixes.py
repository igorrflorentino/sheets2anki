#!/usr/bin/env python3
"""
Teste para verificar se as correções de duplicação funcionam.
"""

def test_duplication_fixes():
    """
    Testa as correções implementadas para evitar duplicação.
    """
    print("🧪 TESTE: Correções de Duplicação")
    print("=" * 50)
    
    print("\n📋 CENÁRIOS DE TESTE:")
    
    # Cenário 1: [MISSING A.] já está em disabled_students_set
    print("\n1️⃣ CENÁRIO: [MISSING A.] já detectado como aluno desabilitado")
    
    # Simular situação onde [MISSING A.] foi incorretamente detectado
    disabled_students_set = {"Aluno Teste 2", "Isabelle", "[MISSING A.]"}
    sync_missing_disabled = False  # [MISSING A.] foi desabilitado
    
    # Aplicar correção
    all_students_to_remove = list(disabled_students_set)
    
    if not sync_missing_disabled:
        # Verificar duplicação antes de adicionar (CORREÇÃO)
        if "[MISSING A.]" not in all_students_to_remove:
            all_students_to_remove.append("[MISSING A.]")
    
    # Remover duplicatas e ordenar (CORREÇÃO ADICIONAL)
    unique_students = sorted(list(set(all_students_to_remove)))
    
    print(f"   disabled_students_set: {sorted(disabled_students_set)}")
    print(f"   all_students_to_remove (antes): {sorted(all_students_to_remove)}")
    print(f"   unique_students (depois): {unique_students}")
    print(f"   ✅ [MISSING A.] aparece apenas 1 vez: {unique_students.count('[MISSING A.]') == 1}")
    
    # Cenário 2: [MISSING A.] NÃO está em disabled_students_set
    print("\n2️⃣ CENÁRIO: [MISSING A.] não detectado como aluno, mas foi desabilitado")
    
    disabled_students_set2 = {"Aluno Teste 2", "Isabelle"}  # Sem [MISSING A.]
    sync_missing_disabled2 = False  # [MISSING A.] foi desabilitado
    
    # Aplicar correção
    all_students_to_remove2 = list(disabled_students_set2)
    
    if not sync_missing_disabled2:
        # Verificar duplicação antes de adicionar (CORREÇÃO)
        if "[MISSING A.]" not in all_students_to_remove2:
            all_students_to_remove2.append("[MISSING A.]")
    
    # Remover duplicatas e ordenar (CORREÇÃO ADICIONAL)
    unique_students2 = sorted(list(set(all_students_to_remove2)))
    
    print(f"   disabled_students_set: {sorted(disabled_students_set2)}")
    print(f"   all_students_to_remove (antes): {sorted(all_students_to_remove2)}")
    print(f"   unique_students (depois): {unique_students2}")
    print(f"   ✅ [MISSING A.] aparece apenas 1 vez: {unique_students2.count('[MISSING A.]') == 1}")
    
    # Cenário 3: [MISSING A.] não foi desabilitado
    print("\n3️⃣ CENÁRIO: [MISSING A.] continua habilitado")
    
    disabled_students_set3 = {"Aluno Teste 2", "Isabelle"}
    sync_missing_disabled3 = True  # [MISSING A.] continua habilitado
    
    # Aplicar correção
    all_students_to_remove3 = list(disabled_students_set3)
    
    if not sync_missing_disabled3:
        # Esta condição não será executada
        if "[MISSING A.]" not in all_students_to_remove3:
            all_students_to_remove3.append("[MISSING A.]")
    
    # Remover duplicatas e ordenar (CORREÇÃO ADICIONAL)
    unique_students3 = sorted(list(set(all_students_to_remove3)))
    
    print(f"   disabled_students_set: {sorted(disabled_students_set3)}")
    print(f"   all_students_to_remove (antes): {sorted(all_students_to_remove3)}")
    print(f"   unique_students (depois): {unique_students3}")
    print(f"   ✅ [MISSING A.] não está na lista: {'[MISSING A.]' not in unique_students3}")

def test_anki_detection_fixes():
    """
    Testa as correções na detecção de alunos do Anki.
    """
    print("\n" + "=" * 50)
    print("🔧 TESTE: Correções na Detecção do Anki")
    print()
    
    # Simular dados do Anki
    available_students = ["Aluno Teste 2", "Isabelle", "Igor"]
    anki_students_raw = {"Aluno Teste 2", "Isabelle", "Igor", "[MISSING A.]", "João Antigo", "Maria Antiga"}
    
    print(f"📊 DADOS DE ENTRADA:")
    print(f"   available_students: {available_students}")
    print(f"   anki_students_raw: {sorted(anki_students_raw)}")
    print()
    
    # ANTES (lógica antiga - problemática)
    print("❌ LÓGICA ANTERIOR (PROBLEMÁTICA):")
    previous_enabled_old = set()
    previous_enabled_old.update(available_students)
    previous_enabled_old.update(anki_students_raw)  # Inclui tudo do Anki
    print(f"   previous_enabled: {sorted(previous_enabled_old)}")
    print("   Problema: Inclui alunos muito antigos e [MISSING A.]")
    print()
    
    # DEPOIS (lógica nova - corrigida)
    print("✅ LÓGICA ATUAL (CORRIGIDA):")
    previous_enabled_new = set()
    previous_enabled_new.update(available_students)
    
    # Filtrar apenas alunos do Anki que também estão em available_students
    anki_students_filtered = anki_students_raw - {"[MISSING A.]"}  # Remove [MISSING A.]
    relevant_anki_students = anki_students_filtered.intersection(set(available_students))
    previous_enabled_new.update(relevant_anki_students)
    
    print(f"   anki_students_filtered: {sorted(anki_students_filtered)}")
    print(f"   relevant_anki_students: {sorted(relevant_anki_students)}")
    print(f"   previous_enabled: {sorted(previous_enabled_new)}")
    print("   Benefícios: Remove alunos antigos e [MISSING A.]")
    print()
    
    print("🎯 RESULTADOS:")
    print(f"   Antes: {len(previous_enabled_old)} alunos detectados")
    print(f"   Depois: {len(previous_enabled_new)} alunos detectados")
    print(f"   Redução: {len(previous_enabled_old) - len(previous_enabled_new)} alunos filtrados")

if __name__ == "__main__":
    test_duplication_fixes()
    test_anki_detection_fixes()
