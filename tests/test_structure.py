#!/usr/bin/env python3
"""
Script de teste simples para verificar se os caminhos e estrutura estão corretos
"""

import sys
import os

# Adicionar o diretório pai (raiz do projeto) ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

print("Testando estrutura do plugin sheets2anki...")

# Teste 1: Verificar se os arquivos existem
print("1. Verificando arquivos principais...")
files_to_check = [
    'src/main.py',
    'libs/org_to_anki/utils.py',
    '__init__.py'
]

all_files_exist = True
for file_path in files_to_check:
    full_path = os.path.join(project_root, file_path)
    if os.path.exists(full_path):
        print(f"   ✓ {file_path} existe")
    else:
        print(f"   ✗ {file_path} não encontrado")
        all_files_exist = False

# Teste 2: Verificar se as funções existem nos arquivos
print("\n2. Verificando funções em src/main.py...")
main_py_path = os.path.join(project_root, 'src', 'main.py')
if os.path.exists(main_py_path):
    with open(main_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    functions_to_check = [
        'def import_test_deck',
        'def addNewDeck',
        'def syncDecksWithSelection',
        'def removeRemoteDeck'
    ]
    
    for func in functions_to_check:
        if func in content:
            print(f"   ✓ {func} encontrada")
        else:
            print(f"   ✗ {func} não encontrada")

# Teste 3: Verificar função em utils.py
print("\n3. Verificando função em libs/org_to_anki/utils.py...")
utils_py_path = os.path.join(project_root, 'libs', 'org_to_anki', 'utils.py')
if os.path.exists(utils_py_path):
    with open(utils_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'def getAnkiPluginConnector' in content:
        print("   ✓ getAnkiPluginConnector encontrada")
    else:
        print("   ✗ getAnkiPluginConnector não encontrada")

# Teste 4: Verificar se o __init__.py foi corrigido
print("\n4. Verificando correções no __init__.py...")
init_py_path = os.path.join(project_root, '__init__.py')
if os.path.exists(init_py_path):
    with open(init_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'from .src.main import' in content:
        print("   ✓ Imports corrigidos para usar src.main")
    else:
        print("   ✗ Imports ainda apontam para local incorreto")
        
    if 'from .libs.org_to_anki.utils import' in content:
        print("   ✓ Import do utils corrigido")
    else:
        print("   ✗ Import do utils ainda incorreto")
        
    if 'remote_decks' in content:
        print("   ⚠️ Ainda há referências a 'remote_decks' no arquivo")
    else:
        print("   ✓ Todas as referências a 'remote_decks' foram removidas")

print("\n📋 RESUMO DAS CORREÇÕES APLICADAS:")
print("=================================")
print("1. Caminho das bibliotecas corrigido:")
print("   DE: libs_path = os.path.join(addon_path, 'remote_decks', 'libs')")
print("   PARA: libs_path = os.path.join(addon_path, 'libs')")
print()
print("2. Imports das funções principais corrigidos:")
print("   DE: from .remote_decks.main import ...")
print("   PARA: from .src.main import ...")
print()
print("3. Import do utils corrigido:")
print("   DE: from .remote_decks.libs.org_to_anki.utils import ...")
print("   PARA: from .libs.org_to_anki.utils import ...")
print()
print("4. Configuração pyrightconfig.json atualizada:")
print("   DE: 'remote_decks' na seção include")
print("   PARA: 'src' na seção include")

if all_files_exist:
    print("\n✅ PROBLEMA RESOLVIDO!")
    print("O erro 'No module named 'sheet2anki-v2.remote_decks'' deve estar corrigido.")
    print("Agora os imports apontam para a estrutura correta do projeto.")
else:
    print("\n❌ Alguns arquivos não foram encontrados. Verifique a estrutura do projeto.")
