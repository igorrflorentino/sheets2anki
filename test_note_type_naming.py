#!/usr/bin/env python3
"""
Teste para verificar o novo sistema de nomenclatura de note types.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_note_type_naming():
    """Testa a geração de nomes de note types no novo formato."""
    
    # Simular imports
    try:
        from utils import get_note_type_name
        
        # Dados de teste
        url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSsNCEFZvBR3UjBwTbyaPPz-B1SKw17I7Jb72XWweS1y75HmzXfgdFJ1TpZX6_S06m9_phJTy5XnCI6/pub?gid=36065074&single=true&output=tsv"
        remote_deck_name = "#0 Sheets2Anki Template"
        
        print("=== Teste do novo sistema de nomenclatura ===")
        print(f"Remote deck name: '{remote_deck_name}'")
        print()
        
        # Testar diferentes combinações
        test_cases = [
            {"student": None, "is_cloze": False, "expected": "Sheets2Anki - #0 Sheets2Anki Template - Basic"},
            {"student": None, "is_cloze": True, "expected": "Sheets2Anki - #0 Sheets2Anki Template - Cloze"},
            {"student": "Belle", "is_cloze": False, "expected": "Sheets2Anki - #0 Sheets2Anki Template - Belle - Basic"},
            {"student": "Belle", "is_cloze": True, "expected": "Sheets2Anki - #0 Sheets2Anki Template - Belle - Cloze"},
            {"student": "Igor", "is_cloze": False, "expected": "Sheets2Anki - #0 Sheets2Anki Template - Igor - Basic"},
            {"student": "Igor", "is_cloze": True, "expected": "Sheets2Anki - #0 Sheets2Anki Template - Igor - Cloze"},
        ]
        
        all_passed = True
        for i, test_case in enumerate(test_cases, 1):
            result = get_note_type_name(
                url, 
                remote_deck_name, 
                student=test_case["student"], 
                is_cloze=test_case["is_cloze"]
            )
            
            expected = test_case["expected"]
            passed = result == expected
            status = "✅ PASS" if passed else "❌ FAIL"
            
            print(f"Teste {i}: {status}")
            print(f"  Params: student='{test_case['student']}', is_cloze={test_case['is_cloze']}")
            print(f"  Resultado: '{result}'")
            print(f"  Esperado:  '{expected}'")
            print()
            
            if not passed:
                all_passed = False
        
        if all_passed:
            print("🎉 Todos os testes passaram!")
            print("✅ O novo formato preserva espaços corretamente")
            print("✅ Remove a dependência do hash da URL")
            print("✅ Usa o formato 'Sheets2Anki - {remote_deck_name} - {student} - {type}'")
        else:
            print("❌ Alguns testes falharam!")
            
        return all_passed
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_note_type_naming()
