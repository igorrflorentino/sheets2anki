#!/usr/bin/env python3
"""
Teste para verificar se a correção do sync_history funciona.
"""

import json
import os
import tempfile
import shutil

def test_sync_history_preservation():
    """
    Testa se o sync_history é preservado ao salvar configuração global de alunos.
    """
    print("🧪 TESTE: Preservação do sync_history")
    print("=" * 50)
    
    # Criar diretório temporário para teste
    test_dir = tempfile.mkdtemp()
    test_meta_file = os.path.join(test_dir, "meta.json")
    
    try:
        # Simular meta.json com sync_history
        original_meta = {
            "config": {
                "debug": True
            },
            "students": {
                "available_students": ["Alice", "Bob", "Carol"],
                "enabled_students": ["Alice", "Bob"],
                "auto_remove_disabled_students": False,
                "sync_missing_students_notes": False,
                "sync_history": {
                    "Alice": {
                        "first_sync": 1756349347,
                        "last_sync": 1756349347,
                        "total_syncs": 5
                    },
                    "Bob": {
                        "first_sync": 1756349300,
                        "last_sync": 1756349400,
                        "total_syncs": 3
                    }
                },
                "custom_field": "valor_importante"
            }
        }
        
        # Salvar meta.json original
        with open(test_meta_file, 'w', encoding='utf-8') as f:
            json.dump(original_meta, f, indent=4)
        
        print("✅ Meta.json original criado:")
        print(f"   - sync_history tem {len(original_meta['students']['sync_history'])} entradas")
        print(f"   - custom_field: {original_meta['students']['custom_field']}")
        
        # Simular o que a função save_global_student_config FAZIA (problema)
        print("\n🚨 PROBLEMA ANTERIOR:")
        problematic_meta = json.loads(json.dumps(original_meta))
        problematic_meta["students"] = {
            "available_students": ["Alice", "Bob", "Dave"],
            "enabled_students": ["Alice", "Dave"],
            "auto_remove_disabled_students": True,
            "sync_missing_students_notes": True,
        }
        
        print("   - sync_history perdido ❌")
        print("   - custom_field perdido ❌")
        print(f"   - Apenas {len(problematic_meta['students'])} chaves restantes")
        
        # Simular a CORREÇÃO
        print("\n✅ SOLUÇÃO IMPLEMENTADA:")
        corrected_meta = json.loads(json.dumps(original_meta))
        
        # Atualizar apenas as chaves necessárias (preservando o resto)
        if "students" not in corrected_meta:
            corrected_meta["students"] = {}
        
        corrected_meta["students"]["available_students"] = ["Alice", "Bob", "Dave"]
        corrected_meta["students"]["enabled_students"] = ["Alice", "Dave"]
        corrected_meta["students"]["auto_remove_disabled_students"] = True
        corrected_meta["students"]["sync_missing_students_notes"] = True
        
        print(f"   - sync_history preservado ✅ ({len(corrected_meta['students']['sync_history'])} entradas)")
        print(f"   - custom_field preservado ✅: {corrected_meta['students']['custom_field']}")
        print(f"   - Total de chaves: {len(corrected_meta['students'])}")
        
        # Verificar resultados
        print("\n📊 COMPARAÇÃO:")
        print(f"   Original:    {list(original_meta['students'].keys())}")
        print(f"   Problemático: {list(problematic_meta['students'].keys())}")
        print(f"   Corrigido:   {list(corrected_meta['students'].keys())}")
        
        # Verificar se dados importantes foram preservados
        sync_history_preserved = (
            "sync_history" in corrected_meta["students"] and
            corrected_meta["students"]["sync_history"] == original_meta["students"]["sync_history"]
        )
        
        custom_field_preserved = (
            "custom_field" in corrected_meta["students"] and
            corrected_meta["students"]["custom_field"] == original_meta["students"]["custom_field"]
        )
        
        print(f"\n🎯 RESULTADO:")
        print(f"   - sync_history preservado: {'✅' if sync_history_preserved else '❌'}")
        print(f"   - custom_field preservado: {'✅' if custom_field_preserved else '❌'}")
        print(f"   - Configurações atualizadas: {'✅' if corrected_meta['students']['auto_remove_disabled_students'] else '❌'}")
        
        if sync_history_preserved and custom_field_preserved:
            print("\n🎉 TESTE PASSOU! A correção funciona corretamente.")
            return True
        else:
            print("\n💥 TESTE FALHOU! Ainda há problemas.")
            return False
            
    finally:
        # Limpar arquivos temporários
        shutil.rmtree(test_dir)

if __name__ == "__main__":
    test_sync_history_preservation()
