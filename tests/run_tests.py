#!/usr/bin/env python3
"""
Script para executar todos os testes do Sheets2Anki

Uso:
    python run_tests.py              # Executar todos os testes
    python run_tests.py --unit       # Apenas testes unitários
    python run_tests.py --integration # Apenas testes de integração
    python run_tests.py --coverage   # Com relatório de cobertura
    python run_tests.py --verbose    # Saída detalhada
    python run_tests.py --fast       # Pular testes lentos
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Executar testes do Sheets2Anki")

    parser.add_argument(
        "--unit", action="store_true", help="Executar apenas testes unitários"
    )
    parser.add_argument(
        "--integration",
        action="store_true",
        help="Executar apenas testes de integração",
    )
    parser.add_argument(
        "--coverage", action="store_true", help="Gerar relatório de cobertura"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Saída verbose")
    parser.add_argument(
        "--fast", action="store_true", help="Pular testes marcados como lentos"
    )
    parser.add_argument(
        "--file", "-f", type=str, help="Executar arquivo de teste específico"
    )
    parser.add_argument(
        "--function", "-k", type=str, help="Executar função de teste específica"
    )

    args = parser.parse_args()

    # Garantir que estamos no diretório correto
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Construir comando pytest
    cmd = ["python", "-m", "pytest"]

    # Adicionar flags baseadas nos argumentos
    if args.verbose:
        cmd.extend(["-v", "-s"])

    if args.coverage:
        cmd.extend(["--cov=src", "--cov-report=html", "--cov-report=term"])

    if args.fast:
        cmd.extend(["-m", "not slow"])

    if args.unit:
        cmd.extend(["-m", "unit"])
    elif args.integration:
        cmd.extend(["-m", "integration"])

    if args.file:
        test_file = Path("tests") / args.file
        if not test_file.suffix:
            test_file = test_file.with_suffix(".py")
        if not str(test_file).startswith("test_"):
            test_file = test_file.parent / f"test_{test_file.name}"
        cmd.append(str(test_file))
    else:
        cmd.append("tests/")

    if args.function:
        cmd.extend(["-k", args.function])

    # Configurações padrão do pytest
    cmd.extend(
        [
            "--tb=short",  # Traceback curto
            "--strict-markers",  # Strict markers
            "--disable-warnings",  # Desabilitar warnings verbosos
        ]
    )

    print(f"🧪 Executando testes com comando: {' '.join(cmd)}")
    print("=" * 60)

    try:
        # Executar testes
        result = subprocess.run(cmd, check=False)

        # Relatório final
        print("\n" + "=" * 60)
        if result.returncode == 0:
            print("✅ Todos os testes passaram!")

            if args.coverage:
                print("📊 Relatório de cobertura gerado em htmlcov/index.html")
        else:
            print("❌ Alguns testes falharam!")

        return result.returncode

    except KeyboardInterrupt:
        print("\n🛑 Testes interrompidos pelo usuário")
        return 1
    except FileNotFoundError:
        print("❌ pytest não encontrado. Instale com: pip install pytest")
        return 1


def show_test_info():
    """Mostrar informações sobre os testes disponíveis."""
    print("📋 Testes Disponíveis:")
    print("-" * 40)

    test_files = [
        ("test_data_processor.py", "Processamento de dados TSV"),
        ("test_config_manager.py", "Gerenciamento de configurações"),
        ("test_utils.py", "Funções utilitárias"),
        ("test_student_manager.py", "Gestão de alunos"),
        ("test_integration.py", "Testes de integração"),
        ("test_new_tags.py", "Sistema de tags (existente)"),
    ]

    for filename, description in test_files:
        test_path = Path("tests") / filename
        status = "✅" if test_path.exists() else "❌"
        print(f"{status} {filename:25} - {description}")

    print("\n📊 Estatísticas:")
    print(f"Total de arquivos de teste: {len(test_files)}")

    existing_files = [f for f, _ in test_files if (Path("tests") / f).exists()]
    print(f"Arquivos existentes: {len(existing_files)}")

    print("\n🏃 Exemplos de uso:")
    print("  python run_tests.py --unit --verbose")
    print("  python run_tests.py --integration --coverage")
    print("  python run_tests.py --file data_processor --verbose")
    print("  python run_tests.py --function test_parse_students --verbose")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--info":
        show_test_info()
    else:
        sys.exit(main())
