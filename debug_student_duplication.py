#!/usr/bin/env python3
"""
Debug para investigar problema de duplicação na detecção de alunos.
"""

def debug_student_detection_issue():
    """
    Simula o problema que o usuário está enfrentando.
    """
    print("🔍 DEBUG: Investigando problema de detecção de alunos")
    print("=" * 70)
    
    print("\n📋 CENÁRIO REPORTADO:")
    print("• Apenas [MISSING A.] foi removido da sincronização")
    print("• Mas a mensagem mostra: Aluno Teste 2, Isabelle, [MISSING A.], [MISSING A.]")
    print()
    
    print("🔍 POSSÍVEIS CAUSAS:")
    print()
    
    print("1️⃣ DUPLICAÇÃO DE [MISSING A.]:")
    print("   • [MISSING A.] detectado nos dados do Anki via _get_students_from_anki_data()")
    print("   • [MISSING A.] adicionado novamente pela condição is_sync_missing_students_notes()")
    print()
    
    print("2️⃣ DETECÇÃO INCORRETA DE ALUNOS:")
    print("   • Função _get_students_from_anki_data() pode estar detectando alunos que não deveriam")
    print("   • Lógica de available_students pode incluir alunos antigos")
    print()
    
    # Simular o problema
    print("🧪 SIMULAÇÃO DO PROBLEMA:")
    print()
    
    # Configuração atual (simulada)
    current_enabled = ["Igor"]  # Apenas Igor habilitado
    available_students = ["Aluno Teste 2", "Isabelle", "Igor"]  # Lista disponível
    
    # Dados do Anki (simulados)
    anki_students = {"Aluno Teste 2", "Isabelle", "Igor", "[MISSING A.]"}  # [MISSING A.] detectado no Anki
    
    # Lógica atual (PROBLEMÁTICA)
    current_enabled_set = set(current_enabled)
    previous_enabled_raw = set()
    previous_enabled_raw.update(available_students)
    previous_enabled_raw.update(anki_students)  # AQUI está o problema!
    
    previous_enabled_set = previous_enabled_raw
    disabled_students_set = previous_enabled_set - current_enabled_set
    
    all_students_to_remove = list(disabled_students_set)
    
    # Verificar se [MISSING A.] deve ser limpo (simulado como True)
    sync_missing_disabled = False  # [MISSING A.] foi desabilitado
    if not sync_missing_disabled:
        all_students_to_remove.append("[MISSING A.]")  # DUPLICAÇÃO aqui!
    
    print(f"📊 RESULTADOS DA SIMULAÇÃO:")
    print(f"   • current_enabled: {current_enabled}")
    print(f"   • available_students: {available_students}")
    print(f"   • anki_students: {sorted(anki_students)}")
    print(f"   • previous_enabled_raw: {sorted(previous_enabled_raw)}")
    print(f"   • disabled_students_set: {sorted(disabled_students_set)}")
    print(f"   • all_students_to_remove: {sorted(all_students_to_remove)}")
    print()
    
    print("❌ PROBLEMA IDENTIFICADO:")
    print("   1. [MISSING A.] é detectado no Anki via _get_students_from_anki_data()")
    print("   2. [MISSING A.] é adicionado a disabled_students_set")
    print("   3. [MISSING A.] é adicionado NOVAMENTE pela condição is_sync_missing_students_notes()")
    print("   4. Resultado: [MISSING A.] aparece DUAS vezes na lista!")
    print()
    
    print("   Além disso:")
    print("   5. Alunos antigos (Aluno Teste 2, Isabelle) são detectados no Anki")
    print("   6. Eles são considerados 'anteriormente habilitados' mesmo se não estão mais ativos")
    print()
    
    print("✅ SOLUÇÕES NECESSÁRIAS:")
    print()
    print("   1️⃣ FILTRAR [MISSING A.] na função _get_students_from_anki_data()")
    print("      • [MISSING A.] não deveria ser considerado um 'aluno' normal")
    print()
    print("   2️⃣ USAR APENAS available_students ao invés de dados do Anki")
    print("      • Os dados do Anki podem conter alunos muito antigos")
    print("      • available_students é a fonte confiável de alunos 'conhecidos'")
    print()
    print("   3️⃣ VERIFICAR DUPLICAÇÃO antes de adicionar [MISSING A.]")
    print("      • Só adicionar [MISSING A.] se não estiver já na lista")

def propose_fix():
    """
    Propõe a correção para o problema.
    """
    print("\n" + "=" * 70)
    print("🔧 CORREÇÃO PROPOSTA:")
    print()
    
    print("1️⃣ FILTRAR [MISSING A.] em _get_students_from_anki_data():")
    print("```python")
    print("# ANTES:")
    print("if potential_student and potential_student != \"[MISSING A.]\":")
    print("    students_found.add(potential_student)")
    print()
    print("# DEPOIS: Já está correto!")
    print("```")
    print()
    
    print("2️⃣ EVITAR DUPLICAÇÃO em _handle_consolidated_confirmation_cleanup():")
    print("```python")
    print("# ANTES:")
    print("all_students_to_remove = list(disabled_students_set)")
    print("if not is_sync_missing_students_notes():")
    print("    all_students_to_remove.append(\"[MISSING A.]\")")
    print()
    print("# DEPOIS:")
    print("all_students_to_remove = list(disabled_students_set)")
    print("if not is_sync_missing_students_notes():")
    print("    if \"[MISSING A.]\" not in all_students_to_remove:")
    print("        all_students_to_remove.append(\"[MISSING A.]\")")
    print("```")
    print()
    
    print("3️⃣ REVISAR LÓGICA DE DETECÇÃO (opcional):")
    print("```python")
    print("# Considerar usar apenas available_students em vez de escanear Anki")
    print("# previous_enabled_raw.update(available_students)  # Apenas isso")
    print("# # previous_enabled_raw.update(anki_students)     # Remover esta linha")
    print("```")

if __name__ == "__main__":
    debug_student_detection_issue()
    propose_fix()
