@echo off
REM 🚀 Script de Build para Sheets2Anki - Windows
REM Autor: Igor Florentino
REM Descrição: Cria o build do add-on Sheets2Anki para publicação no AnkiWeb

setlocal enabledelayedexpansion

echo 🚀 SHEETS2ANKI BUILD SCRIPT
echo ==============================
echo.

REM Verificar se estamos no diretório correto
REM Se estivermos na pasta scripts, vamos para o diretório pai
if exist "..\manifest.json" if exist "..\scripts\prepare_ankiweb.py" (
    cd ..
    echo 📁 Mudando para o diretório raiz do projeto
)

if not exist "manifest.json" (
    echo ❌ ERRO: Execute este script no diretório raiz do projeto Sheets2Anki
    echo    Esperado: manifest.json no diretório atual
    pause
    exit /b 1
)

if not exist "scripts\prepare_ankiweb.py" (
    echo ❌ ERRO: scripts\prepare_ankiweb.py não encontrado
    pause
    exit /b 1
)

echo ✓ Diretório correto identificado

REM Verificar se Python está disponível
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERRO: Python não encontrado no sistema
    echo    Instale Python e adicione-o ao PATH
    pause
    exit /b 1
)

echo ✓ Python encontrado

REM Executar testes (opcional)
if "%1"=="--skip-tests" (
    echo ⚠️  Testes ignorados (--skip-tests)
) else (
    echo 🧪 Executando testes...
    python run_tests.py
    if %errorlevel% neq 0 (
        echo ⚠️  Alguns testes falharam, mas continuando...
    ) else (
        echo ✓ Todos os testes passaram
    )
)

echo.

REM Executar o build
echo 📦 Iniciando build...
python scripts\prepare_ankiweb.py

if %errorlevel% equ 0 (
    echo.
    echo 🎉 BUILD CONCLUÍDO COM SUCESSO!
    
    if exist "build\sheets2anki.ankiaddon" (
        for %%I in ("build\sheets2anki.ankiaddon") do set "filesize=%%~zI"
        echo 📁 Arquivo: build\sheets2anki.ankiaddon
        echo 📊 Tamanho: !filesize! bytes
        echo 🚀 PRONTO PARA UPLOAD NO ANKIWEB!
    )
    
    echo.
    echo 💡 PRÓXIMOS PASSOS:
    echo    1. Acesse: https://ankiweb.net/shared/addons/
    echo    2. Faça upload do arquivo: build\sheets2anki.ankiaddon
    echo    3. Preencha as informações do add-on
    
) else (
    echo ❌ ERRO: Build falhou
    pause
    exit /b 1
)

echo.
echo Pressione qualquer tecla para continuar...
pause >nul
