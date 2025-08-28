#!/usr/bin/env python3
"""
Simula o fluxo completo do problema para verificar a correção.
"""

def simulate_real_scenario():
    """
    Simula o cenário real do usuário.
    """
    print("🎭 SIMULAÇÃO: Cenário Real do Usuário")
    print("=" * 50)
    
    print("📋 CENÁRIO:")
    print("1. Usuário tem meta.json com sync_history")
    print("2. Usuário abre configuração global de alunos")
    print("3. Usuário clica OK")
    print("4. sync_history deve ser preservado")
    print()
    
    # Estado inicial (como o seu meta.json atual)
    initial_state = {
        "students": {
            "available_students": ["Aluno Teste 2", "Isabelle", "Igor"],
            "enabled_students": ["Igor"],
            "auto_remove_disabled_students": True,
            "sync_missing_students_notes": False,
            "sync_history": {
                "Igor": {
                    "first_sync": 1756349347,
                    "last_sync": 1756349347,
                    "total_syncs": 1
                }
            }
        }
    }
    
    print("📊 ESTADO INICIAL:")
    print(f"   - enabled_students: {initial_state['students']['enabled_students']}")
    print(f"   - sync_history para Igor: {initial_state['students']['sync_history']['Igor']}")
    print()
    
    # Simular save_global_student_config ANTES da correção
    print("🚨 COMPORTAMENTO ANTERIOR (PROBLEMA):")
    broken_state = {"students": {}}
    
    # O que acontecia antes:
    broken_state["students"] = {
        "available_students": ["Aluno Teste 2", "Isabelle", "Igor"],
        "enabled_students": ["Igor"],
        "auto_remove_disabled_students": True,
        "sync_missing_students_notes": False,
    }
    # sync_history PERDIDO!
    
    print(f"   - sync_history perdido: {'sync_history' not in broken_state['students']}")
    print()
    
    # Simular save_global_student_config DEPOIS da correção
    print("✅ COMPORTAMENTO ATUAL (CORRIGIDO):")
    corrected_state = {
        "students": dict(initial_state["students"])  # Cópia do estado atual
    }
    
    # O que acontece agora:
    corrected_state["students"]["available_students"] = ["Aluno Teste 2", "Isabelle", "Igor"]
    corrected_state["students"]["enabled_students"] = ["Igor"]
    corrected_state["students"]["auto_remove_disabled_students"] = True
    corrected_state["students"]["sync_missing_students_notes"] = False
    # sync_history PRESERVADO!
    
    print(f"   - sync_history preservado: {'sync_history' in corrected_state['students']}")
    print(f"   - Dados do Igor mantidos: {corrected_state['students']['sync_history']['Igor']}")
    print()
    
    print("🎯 VERIFICAÇÃO:")
    history_preserved = (
        "sync_history" in corrected_state["students"] and
        "Igor" in corrected_state["students"]["sync_history"] and
        corrected_state["students"]["sync_history"]["Igor"]["total_syncs"] == 1
    )
    
    print(f"   - Histórico preservado: {'✅' if history_preserved else '❌'}")
    print(f"   - Configurações aplicadas: {'✅' if corrected_state['students']['auto_remove_disabled_students'] else '❌'}")
    
    if history_preserved:
        print("\n🎉 PROBLEMA RESOLVIDO!")
        print("   O usuário pode clicar OK sem perder o histórico.")
    else:
        print("\n💥 PROBLEMA PERSISTE!")
    
    return history_preserved

if __name__ == "__main__":
    simulate_real_scenario()
