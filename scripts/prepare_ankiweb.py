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
    
    print("\n3. Limpando arquivos desnecessários...")
    
    # Remover meta.json se existir (gerado automaticamente pelo Anki)
    meta_json_path = package_dir / "meta.json"
    if meta_json_path.exists():
        meta_json_path.unlink()
        print("   🗑️  Removido: meta.json (gerado automaticamente pelo Anki)")
    
    # Remover arquivos de cache e desenvolvimento
    for root, dirs, files in os.walk(package_dir):
        # Remover __pycache__
        if "__pycache__" in dirs:
            shutil.rmtree(os.path.join(root, "__pycache__"))
            print(f"   🗑️  Removido: {root}/__pycache__")
        
        # Remover arquivos .pyc
        for file in files:
            if file.endswith(('.pyc', '.pyo')):
                os.remove(os.path.join(root, file))
                print(f"   🗑️  Removido: {file}")
    
    print("\n4. Validando pacote...")
    
    # Verificar arquivos obrigatórios
    required = ["__init__.py", "manifest.json"]
    for req in required:
        if not (package_dir / req).exists():
            print(f"   ❌ ERRO: {req} não encontrado no pacote!")
            return False
        else:
            print(f"   ✓ {req}")
    
    # Verificar manifest.json
    try:
        with open(package_dir / "manifest.json", 'r') as f:
            manifest = json.load(f)
        
        print(f"   ✓ Nome: {manifest.get('name')}")
        print(f"   ✓ Versão: {manifest.get('version')}")
        print(f"   ✓ Anki min: {manifest.get('min_point_version')}")
        print(f"   ✓ Anki max: {manifest.get('max_point_version')}")
        
    except Exception as e:
        print(f"   ❌ Erro no manifest.json: {e}")
        return False
    
    print("\n5. Criando arquivo .ankiaddon...")
    
    # Criar arquivo .ankiaddon para AnkiWeb
    ankiaddon_path = build_dir / "sheets2anki.ankiaddon"
    with zipfile.ZipFile(ankiaddon_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, package_dir)
                zipf.write(file_path, arc_path)
                
    print(f"   ✅ Criado: {ankiaddon_path}")
    
    # Também criar ZIP para backup/desenvolvimento
    zip_path = build_dir / "sheets2anki-backup.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, package_dir)
                zipf.write(file_path, arc_path)
                
    print(f"   📦 Backup ZIP: {zip_path}")
    
    # Estatísticas
    file_count = sum(len(files) for _, _, files in os.walk(package_dir))
    ankiaddon_size = ankiaddon_path.stat().st_size / 1024  # KB
    
    print(f"\n📊 ESTATÍSTICAS DO PACOTE:")
    print(f"   📁 Arquivos: {file_count}")
    print(f"   📦 Tamanho .ankiaddon: {ankiaddon_size:.1f} KB")
    
    print(f"\n✅ PACOTE CRIADO COM SUCESSO!")
    print(f"📍 Arquivo principal: {ankiaddon_path}")
    print(f"📍 Backup ZIP: {zip_path}")
    print(f"\n🚀 PRONTO PARA UPLOAD NO ANKIWEB!")
    print("💡 Use o arquivo .ankiaddon para publicação no AnkiWeb")
    
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
    create_ankiweb_package()
