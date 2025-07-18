#!/usr/bin/env python3
"""
Script de Preparação para AnkiWeb

Este script prepara o add-on Sheets2Anki para publicação no AnkiWeb,
criando um pacote limpo e otimizado.
"""

import os
import shutil
import json
import zipfile
from pathlib import Path

def create_ankiweb_package():
    """Cria pacote otimizado para AnkiWeb"""
    
    print("📦 PREPARANDO PACOTE PARA ANKIWEB")
    print("=" * 50)
    
    # Diretórios
    script_dir = Path(__file__).parent
    source_dir = script_dir.parent  # Diretório raiz do projeto
    build_dir = source_dir / "build"
    package_dir = build_dir / "sheets2anki"
    
    # Limpar build anterior
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    # Criar diretórios
    build_dir.mkdir()
    package_dir.mkdir()
    
    print("1. Copiando arquivos essenciais...")
    
    # Arquivos obrigatórios
    essential_files = [
        "__init__.py",
        "manifest.json", 
        "config.json"
    ]
    
    for file in essential_files:
        source = source_dir / file
        dest = package_dir / file
        if source.exists():
            shutil.copy2(source, dest)
            print(f"   ✓ {file}")
        else:
            print(f"   ❌ {file} não encontrado")
    
    print("\n2. Copiando código fonte...")
    
    # Diretório src
    src_source = source_dir / "src"
    src_dest = package_dir / "src"
    if src_source.exists():
        shutil.copytree(src_source, src_dest, ignore=ignore_patterns)
        print("   ✓ src/")
    
    # Diretório libs
    libs_source = source_dir / "libs"
    libs_dest = package_dir / "libs"
    if libs_source.exists():
        shutil.copytree(libs_source, libs_dest, ignore=ignore_patterns)
        print("   ✓ libs/")
    
    print("\n3. Configurando modo de produção...")
    
    # Alterar a constante IS_DEVELOPMENT_MODE para False
    constants_path = package_dir / "src" / "constants.py"
    if constants_path.exists():
        with open(constants_path, 'r', encoding='utf-8') as f:
            constants_content = f.read()
        
        # Substituir IS_DEVELOPMENT_MODE = True por IS_DEVELOPMENT_MODE = False
        constants_content = constants_content.replace(
            "IS_DEVELOPMENT_MODE = True", 
            "IS_DEVELOPMENT_MODE = False"
        )
        
        with open(constants_path, 'w', encoding='utf-8') as f:
            f.write(constants_content)
        
        print("   ✅ Modo de desenvolvimento desativado")
    
    print("\n4. Limpando arquivos desnecessários...")
    
    # Remover meta.json se existir (gerado automaticamente pelo Anki)
    meta_json_path = package_dir / "meta.json"
    if meta_json_path.exists():
        meta_json_path.unlink()
        print("   🗑️  Removido: meta.json (gerado automaticamente pelo Anki)")
    
    # Remover arquivos de cache e desenvolvimento
    for root, dirs, files in os.walk(package_dir):
        # Remover __pycache__ - CRÍTICO para AnkiWeb
        dirs_to_remove = [d for d in dirs if d == "__pycache__"]
        for d in dirs_to_remove:
            shutil.rmtree(os.path.join(root, d))
            print(f"   🗑️  Removido: {os.path.relpath(os.path.join(root, d), package_dir)}/__pycache__")
            dirs.remove(d)  # Evita que os.walk entre no diretório removido
        
        # Remover arquivos .pyc, .pyo - CRÍTICO para AnkiWeb
        for file in files[:]:  # Criar cópia da lista para iteração segura
            if file.endswith(('.pyc', '.pyo')):
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f"   🗑️  Removido: {os.path.relpath(file_path, package_dir)}")
        
        # Remover outros arquivos desnecessários
        for file in files[:]:
            if file.startswith('.DS_Store') or file.endswith('.tmp'):
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f"   🗑️  Removido: {os.path.relpath(file_path, package_dir)}")
    
    # Verificação final: garantir que não há __pycache__ ou .pyc
    cache_found = False
    for root, dirs, files in os.walk(package_dir):
        if "__pycache__" in dirs:
            print(f"   ❌ ERRO: __pycache__ ainda presente em {root}")
            cache_found = True
        for file in files:
            if file.endswith(('.pyc', '.pyo')):
                print(f"   ❌ ERRO: arquivo .pyc/.pyo ainda presente: {file}")
                cache_found = True
    
    if cache_found:
        print("   ❌ ERRO CRÍTICO: AnkiWeb não aceita arquivos com __pycache__ ou .pyc!")
        return False
    else:
        print("   ✅ Verificação de limpeza: OK (sem __pycache__ ou .pyc)")
    
    print("\n5. Validando pacote...")
    
    # Verificar arquivos obrigatórios
    required = ["__init__.py", "manifest.json"]
    for req in required:
        if not (package_dir / req).exists():
            print(f"   ❌ ERRO: {req} não encontrado no pacote!")
            return False
        else:
            print(f"   ✓ {req}")
    
    # Verificar e validar manifest.json
    print("\n🔍 Validando manifest.json...")
    manifest_valid, manifest = validate_manifest(package_dir / "manifest.json")
    if not manifest_valid:
        print("   ❌ ERRO: manifest.json não está conforme as especificações do AnkiWeb!")
        return False
    else:
        print("   ✅ manifest.json validado com sucesso")
    
    print("\n6. Criando arquivo .ankiaddon...")
    
    # Criar arquivo .ankiaddon para AnkiWeb
    # IMPORTANTE: Seguir especificações do AnkiWeb - sem pasta raiz no ZIP
    ankiaddon_path = build_dir / "sheets2anki.ankiaddon"
    
    with zipfile.ZipFile(ankiaddon_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # CRÍTICO: Caminho relativo sem a pasta raiz (package_dir)
                # AnkiWeb requer que os arquivos estejam na raiz do ZIP
                arc_path = os.path.relpath(file_path, package_dir)
                zipf.write(file_path, arc_path)
                print(f"   📝 Adicionado ao ZIP: {arc_path}")
                
    print(f"   ✅ Criado: {ankiaddon_path}")
    
    # Verificar estrutura do ZIP criado
    print("\n7. Verificando estrutura do arquivo .ankiaddon...")
    with zipfile.ZipFile(ankiaddon_path, 'r') as zipf:
        zip_contents = zipf.namelist()
        
        # Verificar se há pasta raiz (não deve ter)
        has_root_folder = any('/' not in name and name.endswith('/') for name in zip_contents if name != '')
        if has_root_folder:
            print("   ❌ ERRO: ZIP contém pasta raiz - AnkiWeb não aceita!")
            return False
        
        # Verificar arquivos obrigatórios na raiz
        root_files = [name for name in zip_contents if '/' not in name and name != '']
        if '__init__.py' not in root_files:
            print("   ❌ ERRO: __init__.py não está na raiz do ZIP!")
            return False
        if 'manifest.json' not in root_files:
            print("   ❌ ERRO: manifest.json não está na raiz do ZIP!")
            return False
            
        print("   ✅ Estrutura do ZIP: OK")
        print(f"   📁 Arquivos na raiz: {', '.join(root_files)}")
        
        # Verificar se há __pycache__ ou .pyc no ZIP
        cache_in_zip = [name for name in zip_contents if '__pycache__' in name or name.endswith(('.pyc', '.pyo'))]
        if cache_in_zip:
            print(f"   ❌ ERRO CRÍTICO: Cache Python no ZIP: {cache_in_zip}")
            print("   ❌ AnkiWeb não aceita arquivos com __pycache__ ou .pyc!")
            return False
        else:
            print("   ✅ Verificação de cache no ZIP: OK")
    
    # Estatísticas finais
    file_count = sum(len(files) for _, _, files in os.walk(package_dir))
    ankiaddon_size = ankiaddon_path.stat().st_size / 1024  # KB
    
    print(f"\n📊 ESTATÍSTICAS DO PACOTE:")
    print(f"   📁 Arquivos incluídos: {file_count}")
    print(f"   📦 Tamanho .ankiaddon: {ankiaddon_size:.1f} KB")
    if manifest:
        print(f"   🎯 Compatibilidade: Anki {manifest.get('min_point_version', 'N/A')} - {manifest.get('max_point_version', 'N/A')}")
    else:
        print(f"   🎯 Compatibilidade: Anki N/A - N/A")
    
    print(f"\n✅ PACOTE CRIADO COM SUCESSO!")
    print(f"📍 Arquivo para AnkiWeb: {ankiaddon_path}")
    print(f"\n📋 PRÓXIMOS PASSOS PARA PUBLICAÇÃO:")
    print("   1. Acesse: https://ankiweb.net/shared/addons/")
    print("   2. Clique em 'Upload' ou 'Share a New Add-on'")
    print(f"   3. Faça upload do arquivo: {ankiaddon_path.name}")
    print("   4. Preencha as informações adicionais do add-on")
    print("   5. Publique!")
    print(f"\n⚠️  IMPORTANTE:")
    print("   - O arquivo está pronto para AnkiWeb (sem pasta raiz)")
    print("   - Todos os arquivos __pycache__ e .pyc foram removidos")
    print("   - A estrutura segue as especificações do AnkiWeb")
    
    return True

def ignore_patterns(dir, files):
    """Padrões de arquivos a ignorar"""
    ignore = []
    for file in files:
        if file.startswith('.'):
            ignore.append(file)
        elif file.endswith(('.pyc', '.pyo')):
            ignore.append(file)
        elif file == '__pycache__':
            ignore.append(file)
    return ignore

def validate_manifest(manifest_path):
    """
    Valida o manifest.json de acordo com as especificações do AnkiWeb.
    
    Para AnkiWeb, o manifest deve conter pelo menos:
    - package: especifica o nome da pasta onde o add-on será armazenado
    - name: especifica o nome que será mostrado ao usuário
    - conflicts (opcional): lista de outros pacotes que conflitam
    - mod (opcional): timestamp de quando o add-on foi atualizado
    """
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
    except Exception as e:
        print(f"   ❌ Erro ao ler manifest.json: {e}")
        return False, None
    
    # Campos obrigatórios para AnkiWeb
    required_fields = ['package', 'name']
    
    for field in required_fields:
        if field not in manifest:
            print(f"   ❌ Campo obrigatório ausente no manifest: {field}")
            return False, None
        if not manifest[field] or not isinstance(manifest[field], str):
            print(f"   ❌ Campo '{field}' deve ser uma string não vazia")
            return False, None
    
    # Validar campo 'conflicts' se presente
    if 'conflicts' in manifest:
        if not isinstance(manifest['conflicts'], list):
            print("   ❌ Campo 'conflicts' deve ser uma lista")
            return False, None
        print(f"   ✓ Conflitos declarados: {len(manifest['conflicts'])} pacotes")
    
    # Validar campo 'mod' se presente
    if 'mod' in manifest:
        if not isinstance(manifest['mod'], (int, float)):
            print("   ❌ Campo 'mod' deve ser um número (timestamp)")
            return False, None
    
    # Validar outros campos úteis
    optional_fields = ['version', 'author', 'description', 'homepage', 'min_point_version', 'max_point_version']
    for field in optional_fields:
        if field in manifest and manifest[field]:
            if field in ['min_point_version', 'max_point_version']:
                if not isinstance(manifest[field], int):
                    print(f"   ⚠️  Campo '{field}' deveria ser um inteiro")
            print(f"   ✓ {field}: {manifest[field]}")
    
    return True, manifest

if __name__ == "__main__":
    create_ankiweb_package()
