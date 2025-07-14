#!/usr/bin/env python3
"""
Script de teste integrado para o projeto Sheets2Anki

Este script executa todos os testes disponíveis e fornece um relatório
completo sobre o status do projeto. 

Agora utiliza a nova estrutura organizada de testes na pasta tests/.
"""

import sys
import os
import subprocess
import glob

def run_organized_tests(test_type='all'):
    """Executa os testes organizados na pasta tests/"""
    tests_dir = os.path.join(os.path.dirname(__file__), 'tests')
    
    if test_type == 'quick':
        print("🚀 EXECUTANDO TESTES RÁPIDOS (NOVA ESTRUTURA)")
        cmd = [sys.executable, os.path.join(tests_dir, 'run_all_tests.py'), 'quick']
    else:
        print("🚀 EXECUTANDO SUITE COMPLETA DE TESTES (NOVA ESTRUTURA)")
        cmd = [sys.executable, os.path.join(tests_dir, 'run_all_tests.py')]
    
    try:
        result = subprocess.run(cmd, cwd=tests_dir, timeout=300)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("⏰ Timeout: Testes demoraram mais de 5 minutos")
        return False
    except Exception as e:
        print(f"❌ Erro ao executar testes: {e}")
        return False

def run_legacy_tests():
    """Executa testes antigos que ainda existem"""
    legacy_tests = []
    
    # Buscar por testes na raiz que ainda existem
    for pattern in ['test_*.py', 'debug_*.py']:
        legacy_tests.extend(glob.glob(pattern))
    
    if legacy_tests:
        print(f"⚠️  Encontrados {len(legacy_tests)} arquivos de teste antigos na raiz:")
        for test in legacy_tests:
            print(f"   - {test}")
        print("   Recomendação: mover para tests/ ou remover se obsoletos")
        return False
    else:
        print("✅ Nenhum arquivo de teste antigo encontrado na raiz")
        return True

def run_test(test_file, description):
    """Executa um teste e retorna o resultado"""
    print(f"\n{'='*60}")
    print(f"🧪 EXECUTANDO: {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print("✅ PASSOU")
            print(result.stdout)
            return True
        else:
            print("❌ FALHOU")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
    except Exception as e:
        print(f"❌ ERRO AO EXECUTAR: {e}")
        return False

def get_all_test_files():
    """Descobre automaticamente todos os arquivos de teste na pasta tests/"""
    test_pattern = "tests/test_*.py"
    test_files = glob.glob(test_pattern)
    
    # Ordenar para execução consistente
    test_files.sort()
    
    # Criar lista com descrições baseadas no nome do arquivo
    tests = []
    for test_file in test_files:
        # Extrair nome do teste do arquivo
        test_name = os.path.basename(test_file)
        test_name = test_name.replace("test_", "").replace(".py", "").replace("_", " ").title()
        description = f"Teste de {test_name}"
        tests.append((test_file, description))
    
    return tests

def main():
    """Função principal"""
    print("🚀 EXECUTANDO SUITE DE TESTES - SHEETS2ANKI")
    print("=" * 60)
    
    # Verificar argumentos da linha de comando
    test_type = 'all'
    if len(sys.argv) > 1 and sys.argv[1] == 'quick':
        test_type = 'quick'
    
    # Executar testes organizados
    print("📋 Usando nova estrutura organizada de testes")
    organized_success = run_organized_tests(test_type)
    
    # Verificar arquivos antigos
    print("\n" + "=" * 60)
    print("🔍 VERIFICANDO ESTRUTURA ANTIGA")
    legacy_clean = run_legacy_tests()
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO FINAL")
    print("=" * 60)
    
    if organized_success:
        print("✅ Testes organizados: SUCESSO")
    else:
        print("❌ Testes organizados: FALHOU")
    
    if legacy_clean:
        print("✅ Estrutura: LIMPA (sem arquivos antigos)")
    else:
        print("⚠️  Estrutura: ARQUIVOS ANTIGOS ENCONTRADOS")
    
    overall_success = organized_success and legacy_clean
    
    if overall_success:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("💡 Estrutura de testes organizada e funcionando perfeitamente")
    else:
        print("\n⚠️  ALGUNS PROBLEMAS ENCONTRADOS")
        if not organized_success:
            print("   - Testes organizados falharam")
        if not legacy_clean:
            print("   - Arquivos antigos precisam ser movidos/removidos")
    
    print("\n� COMANDOS ÚTEIS:")
    print("   python run_tests.py        # Executar todos os testes")
    print("   python run_tests.py quick  # Executar testes rápidos")
    print("   cd tests && python run_all_tests.py  # Executar da pasta tests")
    print("   cd tests && python integration/test_integration.py  # Teste específico")
    
    return 0 if overall_success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
