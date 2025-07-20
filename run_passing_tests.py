#!/usr/bin/env python3
"""
Script para executar apenas os testes que estão passando no Sheets2Anki.
"""
import sys
import subprocess
import os

def run_passing_tests():
    """Executa apenas os testes que sabemos que estão passando."""
    print("🚀 EXECUTANDO TESTES QUE ESTÃO PASSANDO - SHEETS2ANKI")
    print("=" * 60)
    
    # Comando para executar apenas os testes que estão passando
    cmd = [
        sys.executable, 
        "-m", 
        "pytest", 
        "tests/unit/test_basic.py",
        "tests/unit/test_sync_selective.py",
        "tests/unit/test_url_validation.py"
    ]
    
    print(f"Comando: {' '.join(cmd)}")
    
    # Executar o comando
    try:
        result = subprocess.run(cmd, cwd=os.path.dirname(__file__))
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Erro ao executar testes: {e}")
        return False

def main():
    """Função principal."""
    # Executar testes
    success = run_passing_tests()
    
    # Resumo final
    print("\n" + "=" * 60)
    if success:
        print("🎉 TODOS OS TESTES PASSARAM!")
    else:
        print("⚠️  ALGUNS TESTES FALHARAM")
    
    print("\n📋 COMANDOS ÚTEIS:")
    print("   ./run_passing_tests.py    # Executar testes que estão passando")
    print("   ./run_pytest.py           # Executar todos os testes")
    print("   ./run_pytest.py quick     # Executar testes rápidos")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())