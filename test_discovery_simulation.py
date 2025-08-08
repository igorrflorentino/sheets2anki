#!/usr/bin/env python3
"""
Simulação exata do processo de descoberta.
"""

def normalize_student_name(name):
    """Cópia da função do config_manager."""
    if not name or not isinstance(name, str):
        return ""
    return name.strip().capitalize()

def simulate_discovery():
    """Simula o processo completo de descoberta."""
    print("=== SIMULAÇÃO DO PROCESSO DE DESCOBERTA ===")
    
    # Dados atuais do meta.json
    current_available = {'Belle', 'Igor'}
    print(f"📋 Estudantes disponíveis atuais: {sorted(current_available)}")
    
    # Dados descobertos do TSV
    discovered_raw = ['Belle', 'Igor2', 'pedro']
    print(f"🔍 Estudantes brutos descobertos: {discovered_raw}")
    
    # Normalizar descobertos (como faz a função)
    discovered_normalized = set()
    for student in discovered_raw:
        normalized = normalize_student_name(student)
        if normalized:
            discovered_normalized.add(normalized)
            print(f"  '{student}' → '{normalized}'")
    
    print(f"🎯 Estudantes normalizados: {sorted(discovered_normalized)}")
    
    # Calcular novos (diferença)
    new_students = discovered_normalized - current_available
    print(f"✨ Novos estudantes: {sorted(new_students)}")
    print(f"📊 Quantidade de novos: {len(new_students)}")
    
    if len(new_students) == 0:
        print("❌ PROBLEMA: Sistema reportará 'nenhum novo estudante'")
        print("Mas isso está ERRADO porque há estudantes diferentes!")
        
        print("\n🔍 ANÁLISE DETALHADA:")
        print(f"'Belle' em current? {'Belle' in current_available}")
        print(f"'Igor2' em current? {'Igor2' in current_available}")  
        print(f"'Pedro' em current? {'Pedro' in current_available}")
        
        # Verificar se o problema é case-sensitive
        current_lower = {s.lower() for s in current_available}
        discovered_lower = {s.lower() for s in discovered_normalized}
        
        print(f"\nComparação case-insensitive:")
        print(f"Current (lower): {sorted(current_lower)}")
        print(f"Discovered (lower): {sorted(discovered_lower)}")
        
        new_case_insensitive = discovered_lower - current_lower
        print(f"Novos (case-insensitive): {sorted(new_case_insensitive)}")
        
        if len(new_case_insensitive) > 0:
            print("✅ HÁ NOVOS ESTUDANTES! O problema não é case-sensitivity.")
        else:
            print("❌ PROBLEMA: Mesmo case-insensitive, não há novos?")
    
    else:
        print("✅ Sistema funcionará corretamente!")
    
    return new_students

if __name__ == "__main__":
    new_students = simulate_discovery()
    
    if len(new_students) > 0:
        print(f"\n🎉 SIMULAÇÃO OK: {len(new_students)} novos estudantes serão encontrados")
    else:
        print(f"\n❌ SIMULAÇÃO FALHOU: Sistema reportará 0 novos estudantes incorretamente")
        print("\nPossíveis causas:")
        print("1. Problema na normalização")
        print("2. Problema na comparação de conjuntos")
        print("3. Dados inconsistentes no meta.json")
        print("4. Bug na lógica de descoberta")
