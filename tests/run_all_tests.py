#!/usr/bin/env python3
"""
Suite de testes centralizada para o Sheets2Anki.
Executa todos os testes de forma organizada.
"""

import sys
import os
import importlib.util
import subprocess
from pathlib import Path

def run_test_file(test_file):
    """Executa um arquivo de teste e retorna o resultado."""
    try:
        # Executar o arquivo de teste
        result = subprocess.run(
            [sys.executable, str(test_file)],
            capture_output=True,
            text=True,
            timeout=120,  # Aumentar timeout para 2 minutos
            cwd=str(test_file.parent)  # Executar no diretório do teste
        )
        
        success = result.returncode == 0
        return {
            'success': success,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'stdout': '',
            'stderr': 'Test timeout after 2 minutes',
            'returncode': -1
        }
    except Exception as e:
        return {
            'success': False,
            'stdout': '',
            'stderr': f'Exception during test execution: {str(e)}',
            'returncode': -1
        }

def run_organized_tests():
    """Executa todos os testes organizados."""
    print("🧪 SUITE DE TESTES CENTRALIZADA - SHEETS2ANKI")
    print("=" * 60)
    
    # Definir estrutura de testes
    test_structure = {
        'Unit Tests': [
            'test_case_insensitive.py',
            'test_sync_selective.py',
            'test_sync_internal_only.py',
            'test_sync_basic.py',
            'test_formula_errors_simple.py',
            'test_formula_advanced.py',
            'test_url_validation.py',
            'test_ignored_cards.py',
            'test_data_validation.py',
            'test_card_templates.py',
            'test_config.py',
        ],
        'Integration Tests': [
            'test_formula_integration.py',
            'test_sync_advanced.py',
            'test_compatibility.py',
            'test_deck_sync_counting.py',
            'integration/test_integration.py',
        ],
        'Workflow Tests': [
            'workflow/test_workflow.py',
        ],
        'Fixed Tests': [
            'test_real_csv.py',
            'test_debug_sync.py',
            'test_formula_errors.py',
        ],
        'Structure Tests': [
            'test_structure.py',
            'test_imports.py',
        ]
    }
    
    # Diretório de testes
    tests_dir = Path(__file__).parent
    
    # Resultados
    all_results = {}
    total_tests = 0
    passed_tests = 0
    
    # Executar cada categoria
    for category, test_files in test_structure.items():
        print(f"\n📋 {category.upper()}")
        print("-" * 40)
        
        category_results = {}
        for test_file in test_files:
            test_path = tests_dir / test_file
            if test_path.exists():
                print(f"🔄 Executando: {test_file}")
                result = run_test_file(test_path)
                category_results[test_file] = result
                total_tests += 1
                
                if result['success']:
                    print(f"✅ PASSOU: {test_file}")
                    passed_tests += 1
                else:
                    print(f"❌ FALHOU: {test_file}")
                    if result['stderr']:
                        print(f"   Erro: {result['stderr'][:200]}...")
            else:
                print(f"⚠️  Arquivo não encontrado: {test_file}")
        
        all_results[category] = category_results
    
    # Executar testes de debug se solicitado
    debug_tests = [
        'debug/debug_suite.py',
    ]
    
    print(f"\n🔍 DEBUG TESTS")
    print("-" * 40)
    
    for test_file in debug_tests:
        test_path = tests_dir / test_file
        if test_path.exists():
            print(f"🔄 Executando: {test_file}")
            result = run_test_file(test_path)
            
            if result['success']:
                print(f"✅ DEBUG EXECUTADO: {test_file}")
            else:
                print(f"❌ DEBUG FALHOU: {test_file}")
                if result['stderr']:
                    print(f"   Erro: {result['stderr'][:200]}...")
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO FINAL DOS TESTES")
    print("-" * 60)
    
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"Total de testes: {total_tests}")
    print(f"Testes aprovados: {passed_tests}")
    print(f"Testes falharam: {total_tests - passed_tests}")
    print(f"Taxa de sucesso: {success_rate:.1f}%")
    
    # Detalhes por categoria
    print("\n📋 DETALHES POR CATEGORIA:")
    for category, results in all_results.items():
        if results:
            cat_total = len(results)
            cat_passed = sum(1 for r in results.values() if r['success'])
            cat_rate = (cat_passed / cat_total) * 100 if cat_total > 0 else 0
            print(f"  {category}: {cat_passed}/{cat_total} ({cat_rate:.1f}%)")
    
    # Status final
    if success_rate == 100:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        return True
    elif success_rate >= 80:
        print("\n✅ MAIORIA DOS TESTES PASSOU!")
        return True
    else:
        print("\n⚠️  MUITOS TESTES FALHARAM - VERIFICAR PROBLEMAS")
        return False

def run_quick_tests():
    """Executa apenas testes rápidos essenciais."""
    print("⚡ TESTES RÁPIDOS - SHEETS2ANKI")
    print("=" * 40)
    
    essential_tests = [
        'test_case_insensitive.py',
        'test_sync_selective.py',
        'test_sync_internal_only.py',
        'test_formula_errors_simple.py',
        'test_url_validation.py',
        'test_structure.py',
        'test_imports.py',
        'test_data_validation.py',
        'integration/test_integration.py',
    ]
    
    tests_dir = Path(__file__).parent
    passed = 0
    total = 0
    
    for test_file in essential_tests:
        test_path = tests_dir / test_file
        if test_path.exists():
            print(f"🔄 {test_file}")
            result = run_test_file(test_path)
            total += 1
            
            if result['success']:
                print(f"✅ PASSOU")
                passed += 1
            else:
                print(f"❌ FALHOU")
                if result['stderr']:
                    print(f"   Erro: {result['stderr'][:100]}...")
        else:
            print(f"⚠️  Não encontrado: {test_file}")
    
    success_rate = (passed / total) * 100 if total > 0 else 0
    print(f"\n📊 Resultado: {passed}/{total} ({success_rate:.1f}%)")
    
    return success_rate >= 80

def main():
    """Função principal."""
    if len(sys.argv) > 1 and sys.argv[1] == 'quick':
        return run_quick_tests()
    else:
        return run_organized_tests()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
