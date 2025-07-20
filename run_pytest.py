#!/usr/bin/env python3
"""
Script para executar os testes do Sheets2Anki usando pytest.
"""
import sys
import subprocess
import os

def run_tests(quick=False):
    """Executa os testes usando pytest."""
    print("🚀 EXECUTANDO TESTES COM PYTEST - SHEETS2ANKI")
    print("=" * 60)
    
    # Comando base do pytest
    cmd = ["pytest"]
    
    # Adicionar opções
    cmd.extend(["-v"])  # Modo verboso
    
    if quick:
        print("⚡ Modo rápido: executando apenas testes essenciais")
        cmd.extend(["-m", "not slow"])  # Pular testes lentos
    else:
        print("🔍 Modo completo: executando todos os testes")
    
    # Executar o comando
    try:
        result = subprocess.run(cmd, cwd=os.path.dirname(__file__))
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Erro ao executar testes: {e}")
        return False

def main():
    """Função principal."""
    # Verificar argumentos da linha de comando
    quick = len(sys.argv) > 1 and sys.argv[1] == 'quick'
    
    # Executar testes
    success = run_tests(quick)
    
    # Resumo final
    print("\n" + "=" * 60)
    if success:
        print("🎉 TODOS OS TESTES PASSARAM!")
    else:
        print("⚠️  ALGUNS TESTES FALHARAM")
    
    print("\n📋 COMANDOS ÚTEIS:")
    print("   python run_pytest.py        # Executar todos os testes")
    print("   python run_pytest.py quick  # Executar testes rápidos")
    print("   pytest tests/unit           # Executar apenas testes unitários")
    print("   pytest tests/integration    # Executar apenas testes de integração")
    print("   pytest -xvs tests/unit/test_sync_selective.py  # Executar um teste específico")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())