#!/bin/bash

# 🚀 Script de Build para Sheets2Anki
# Autor: Igor Florentino
# Descrição: Cria o build do add-on Sheets2Anki para publicação no AnkiWeb

set -e  # Parar se houver erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Função para imprimir com cores
print_color() {
    echo -e "${1}${2}${NC}"
}

# Header
print_color $CYAN "🚀 SHEETS2ANKI BUILD SCRIPT"
print_color $CYAN "=============================="
echo

# Verificar se estamos no diretório correto
# Se estivermos na pasta scripts, vamos para o diretório pai
if [ -f "../manifest.json" ] && [ -f "../prepare_ankiweb.py" ]; then
    cd ..
    print_color $YELLOW "📁 Mudando para o diretório raiz do projeto"
fi

if [ ! -f "manifest.json" ] || [ ! -f "scripts/prepare_ankiweb.py" ]; then
    print_color $RED "❌ ERRO: Execute este script no diretório raiz do projeto Sheets2Anki"
    print_color $YELLOW "   Esperado: manifest.json no diretório atual e scripts/prepare_ankiweb.py"
    exit 1
fi

print_color $GREEN "✓ Diretório correto identificado"

# Verificar se Python está disponível
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        print_color $RED "❌ ERRO: Python não encontrado no sistema"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

print_color $GREEN "✓ Python encontrado: $PYTHON_CMD"

# Executar testes (opcional)
if [ "$1" = "--skip-tests" ]; then
    print_color $YELLOW "⚠️  Testes ignorados (--skip-tests)"
else
    print_color $BLUE "🧪 Executando testes..."
    if $PYTHON_CMD run_tests.py; then
        print_color $GREEN "✓ Todos os testes passaram"
    else
        print_color $YELLOW "⚠️  Alguns testes falharam, mas continuando..."
    fi
fi

echo

# Executar o build
print_color $BLUE "📦 Iniciando build..."
if $PYTHON_CMD scripts/prepare_ankiweb.py; then
    echo
    print_color $GREEN "🎉 BUILD CONCLUÍDO COM SUCESSO!"
    
    # Mostrar informações do arquivo gerado
    if [ -f "build/sheets2anki.ankiaddon" ]; then
        FILESIZE=$(du -h "build/sheets2anki.ankiaddon" | cut -f1)
        print_color $CYAN "📁 Arquivo: build/sheets2anki.ankiaddon"
        print_color $CYAN "📊 Tamanho: $FILESIZE"
        print_color $PURPLE "🚀 PRONTO PARA UPLOAD NO ANKIWEB!"
    fi
    
    # Instruções
    echo
    print_color $YELLOW "💡 PRÓXIMOS PASSOS:"
    print_color $NC "   1. Acesse: https://ankiweb.net/shared/addons/"
    print_color $NC "   2. Faça upload do arquivo: build/sheets2anki.ankiaddon"
    print_color $NC "   3. Preencha as informações do add-on"
    
else
    print_color $RED "❌ ERRO: Build falhou"
    exit 1
fi
