#!/usr/bin/env python3
"""
Script Unificado de Build

Este script permite criar pacotes para diferentes tipos de distribuição:
1. AnkiWeb (upload direto na plataforma)
2. Standalone (distribuição independente)
"""

import sys
import subprocess
from pathlib import Path

def main():
    print("🚀 SHEETS2ANKI - CRIADOR DE PACOTES")
    print("=" * 40)
    print()
    print("Escolha o tipo de pacote:")
    print("1. AnkiWeb (para upload no AnkiWeb)")
    print("2. Standalone (para distribuição independente)")
    print("3. Ambos")
    print()
    
    while True:
        choice = input("Digite sua escolha (1/2/3): ").strip()
        
        if choice in ['1', '2', '3']:
            break
        else:
            print("❌ Escolha inválida. Digite 1, 2 ou 3.")
    
    script_dir = Path(__file__).parent
    
    success = True
    
    if choice in ['1', '3']:
        print("\n" + "="*50)
        print("📦 CRIANDO PACOTE PARA ANKIWEB")
        print("="*50)
        
        try:
            result = subprocess.run([
                sys.executable, 
                script_dir / "prepare_ankiweb.py"
            ], check=True)
            print("✅ Pacote AnkiWeb criado com sucesso!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao criar pacote AnkiWeb: {e}")
            success = False
    
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
            
        print("\n📚 INSTRUÇÕES:")
        if choice in ['1', '3']:
            print("   AnkiWeb: https://ankiweb.net/shared/addons/")
        if choice in ['2', '3']:
            print("   Standalone: Distribua o arquivo .ankiaddon diretamente")
    else:
        print("❌ HOUVE ERROS NA CRIAÇÃO DOS PACOTES")
        print("   Verifique as mensagens acima para detalhes")

if __name__ == "__main__":
    main()
