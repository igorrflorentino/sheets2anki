#!/usr/bin/env python3
"""
Script Unificado de Build

Este script permite criar pacotes para AnkiWeb e/ou distribuição standalone
"""

import subprocess
import sys
from pathlib import Path

def main():
    script_dir = Path(__file__).parent
    build_dir = script_dir.parent / "build"
    
    print("🚀 SHEETS2ANKI - CRIADOR DE PACOTES")
    print("="*40)
    print("Escolha o tipo de pacote:")
    print("1. AnkiWeb (para upload no AnkiWeb)")
    print("2. Standalone (para distribuição independente)")
    print("3. Ambos")
    
    choice = input("Digite sua escolha (1/2/3): ").strip()
    
    if choice not in ['1', '2', '3']:
        print("❌ Opção inválida!")
        return
    
    success = True
    
    # Criar pacote AnkiWeb
    if choice in ['1', '3']:
        print("\n" + "="*50)
        print("📦 CRIANDO PACOTE PARA ANKIWEB")
        print("="*50)
        
        try:
            result = subprocess.run([
                sys.executable, 
                script_dir / "create_ankiweb_package.py"
            ], check=True)
            print("✅ Pacote AnkiWeb criado com sucesso!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao criar pacote AnkiWeb: {e}")
            success = False
    
    # Criar pacote Standalone
    if choice in ['2', '3']:
        print("\n" + "="*50)
        print("📦 CRIANDO PACOTE STANDALONE")
        print("="*50)
        
        try:
            result = subprocess.run([
                sys.executable, 
                script_dir / "create_standalone_package.py"
            ], check=True)
            print("✅ Pacote Standalone criado com sucesso!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao criar pacote Standalone: {e}")
            success = False
    
    print("\n" + "="*50)
    if success:
        print("🎉 TODOS OS PACOTES FORAM CRIADOS COM SUCESSO!")
        print("\n📁 Verifique a pasta 'build/' para os arquivos:")
        
        if choice in ['1', '3']:
            print("   - sheets2anki.ankiaddon (para AnkiWeb)")
        if choice in ['2', '3']:
            print("   - sheets2anki-standalone.ankiaddon (para distribuição)")
        
        # Executar validação dos pacotes criados
        print("\n🔍 VALIDANDO PACOTES CRIADOS...")
        print("="*50)
        
        # Lista de arquivos para validar
        files_to_validate = []
        
        # Adiciona os arquivos baseado nas opções escolhidas
        if choice in ['1', '3']:  # AnkiWeb
            files_to_validate.append(build_dir / "sheets2anki.ankiaddon")
        if choice in ['2', '3']:  # Standalone
            files_to_validate.append(build_dir / "sheets2anki-standalone.ankiaddon")
        
        # Valida cada arquivo
        validation_success = True
        for file_path in files_to_validate:
            if file_path.exists():
                print(f"📋 Validando: {file_path.name}")
                try:
                    result = subprocess.run([
                        sys.executable, 
                        script_dir / "validate_packages.py",
                        str(file_path)
                    ], check=True, capture_output=True, text=True)
                    
                    if result.stdout:
                        print(result.stdout)
                    print(f"✅ {file_path.name} validado com sucesso!")
                    
                except subprocess.CalledProcessError as e:
                    print(f"❌ Erro na validação de {file_path.name}: {e}")
                    if e.stdout:
                        print("Saída:", e.stdout)
                    if e.stderr:
                        print("Erro:", e.stderr)
                    validation_success = False
                except Exception as e:
                    print(f"❌ Erro inesperado na validação de {file_path.name}: {e}")
                    validation_success = False
                print("-" * 30)
            else:
                print(f"⚠️  Arquivo não encontrado: {file_path.name}")
                validation_success = False
        
        if validation_success:
            print("\n🎯 VALIDAÇÃO CONCLUÍDA COM SUCESSO!")
            print("\n📚 INSTRUÇÕES:")
            if choice in ['1', '3']:
                print("   AnkiWeb: https://ankiweb.net/shared/addons/")
            if choice in ['2', '3']:
                print("   Standalone: Distribua o arquivo .ankiaddon diretamente")
        else:
            print("\n⚠️  PACOTES CRIADOS MAS COM PROBLEMAS DE VALIDAÇÃO")
            print("   Verifique as mensagens de validação acima")
            
    else:
        print("❌ HOUVE ERROS NA CRIAÇÃO DOS PACOTES")
        print("   Verifique as mensagens acima para detalhes")

if __name__ == "__main__":
    main()
