#!/usr/bin/env python3
"""
Script para Criação de Pacote Standalone

Este script cria um pacote .ankiaddon para distribuição FORA do AnkiWeb.
Para distribuição fora do AnkiWeb, o manifest.json deve incluir informações completas.
"""

import os
import shutil
import json
import zipfile
from pathlib import Path

def create_standalone_package():
    """
    Cria pacote .ankiaddon para distribuição fora do AnkiWeb.
    
    Para distribuição fora do AnkiWeb, o manifest.json deve conter:
    - package: nome da pasta onde será armazenado
    - name: nome mostrado ao usuário  
    - conflicts (opcional): lista de pacotes conflitantes
    - mod (opcional): timestamp de atualização
    """
    
    print("📦 CRIANDO PACOTE STANDALONE (.ankiaddon)")
    print("=" * 50)
    print("ℹ️  Para distribuição FORA do AnkiWeb")
    
    # Diretórios
    script_dir = Path(__file__).parent
    source_dir = script_dir.parent  # Diretório raiz do projeto
    build_dir = source_dir / "build"
    package_dir = build_dir / "sheets2anki-standalone"
    
    # Limpar build anterior
    if package_dir.exists():
        shutil.rmtree(package_dir)
    
    # Criar diretórios
    build_dir.mkdir(exist_ok=True)
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
    
    print("\n3. Validando manifest.json para distribuição standalone...")
    
    # Ler e validar manifest
    manifest_path = package_dir / "manifest.json"
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
    except Exception as e:
        print(f"   ❌ Erro ao ler manifest.json: {e}")
        return False
    
    # Verificar campos obrigatórios para distribuição externa
    required_fields = ['package', 'name']
    for field in required_fields:
        if field not in manifest or not manifest[field]:
            print(f"   ❌ Campo obrigatório ausente: {field}")
            return False
        print(f"   ✓ {field}: {manifest[field]}")
    
    # Adicionar timestamp se não existir
    if 'mod' not in manifest:
        import time
        manifest['mod'] = int(time.time())
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=4, ensure_ascii=False)
        print(f"   ✓ Campo 'mod' adicionado: {manifest['mod']}")
    
    # Verificar outros campos úteis
    if 'conflicts' not in manifest:
        manifest['conflicts'] = []
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=4, ensure_ascii=False)
        print("   ✓ Campo 'conflicts' adicionado (lista vazia)")
    
    print("\n4. Limpando arquivos desnecessários...")
    
    # Remover arquivos de cache
    for root, dirs, files in os.walk(package_dir):
        # Remover __pycache__
        dirs_to_remove = [d for d in dirs if d == "__pycache__"]
        for d in dirs_to_remove:
            shutil.rmtree(os.path.join(root, d))
            print(f"   🗑️  Removido: {os.path.relpath(os.path.join(root, d), package_dir)}")
            dirs.remove(d)
        
        # Remover arquivos .pyc, .pyo
        for file in files[:]:
            if file.endswith(('.pyc', '.pyo', '.DS_Store')) or file.startswith('.'):
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f"   🗑️  Removido: {os.path.relpath(file_path, package_dir)}")
    
    print("\n5. Criando arquivo .ankiaddon standalone...")
    
    # Criar arquivo .ankiaddon
    ankiaddon_path = build_dir / "sheets2anki-standalone.ankiaddon"
    
    with zipfile.ZipFile(ankiaddon_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Caminho relativo sem a pasta raiz
                arc_path = os.path.relpath(file_path, package_dir)
                zipf.write(file_path, arc_path)
                print(f"   📝 Adicionado: {arc_path}")
    
    # Estatísticas
    file_count = sum(len(files) for _, _, files in os.walk(package_dir))
    ankiaddon_size = ankiaddon_path.stat().st_size / 1024  # KB
    
    print(f"\n📊 ESTATÍSTICAS DO PACOTE STANDALONE:")
    print(f"   📁 Arquivos incluídos: {file_count}")
    print(f"   📦 Tamanho .ankiaddon: {ankiaddon_size:.1f} KB")
    print(f"   📋 Package ID: {manifest['package']}")
    print(f"   🏷️  Nome: {manifest['name']}")
    print(f"   🕒 Timestamp: {manifest.get('mod', 'N/A')}")
    
    print(f"\n✅ PACOTE STANDALONE CRIADO COM SUCESSO!")
    print(f"📍 Arquivo: {ankiaddon_path}")
    print(f"\n📤 DISTRIBUIÇÃO FORA DO ANKIWEB:")
    print("   - Este arquivo pode ser distribuído independentemente")
    print("   - Usuários podem instalar via 'Install from file...'")
    print("   - O manifest.json contém todas as informações necessárias")
    print("   - Compatível com instalação manual no Anki")
    
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

if __name__ == "__main__":
    create_standalone_package()
